from __future__ import annotations

import base64
import csv
import hashlib
import html
import io
import json
import logging
import os
import re
import sys
import threading
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

import requests

from reporting_control.hub_source_client import fetch_latest_source

from .cli import parser as controller_parser
from .cli import run as run_controller


log = logging.getLogger(__name__)

LEGACY_EVIDENCE_FIELDS = (
    "email",
    "payment_rail",
    "status",
    "weekly_amount",
    "last_receipt_date",
    "next_due_date",
    "notes",
)
LEGACY_EVIDENCE_STATUSES = {
    "collecting",
    "review_required",
    "paused",
    "inactive",
    "paid_in_advance",
    "pif",
}
ACCOUNT_CLASSIFICATIONS = {
    "approved_internal_access",
    "current_pt_client",
    "external_payment_client",
    "inactive_pt_credit",
    "online_client",
    "owner_admin",
    "prepaid_credit_client",
    "staff",
}
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class RailwayRevenueRuntime:
    def __init__(self, settings: Any) -> None:
        self.settings = settings
        self.base_dir = Path(
            os.getenv("REVENUE_GAP_DATA_DIR", "/data/revenue-gap-control")
        )
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.membership_database = self.base_dir / "reconciliation.sqlite"
        self.audit_database = self.base_dir / "revenue_gap.sqlite"
        self.latest_state_path = self.base_dir / "latest-run.json"
        self.legacy_evidence_path = self.base_dir / "legacy-payment-evidence.csv"
        self.timing_items_path = self.base_dir / "timing-items.csv"
        self.identity_links_path = self.base_dir / "identity-links.csv"
        self.account_classifications_path = (
            self.base_dir / "account-classifications.csv"
        )
        self.hub_pt_minder_state_path = (
            self.base_dir / "hub-pt-minder-parity.json"
        )
        self._lock = threading.Lock()

    def _membership_reconciliation(self) -> str:
        scripts_dir = Path(__file__).resolve().parents[1] / "scripts"
        sys.path.insert(0, str(scripts_dir))
        try:
            from membership_reconciliation import run_reconciliation

            summary = run_reconciliation(
                database=self.membership_database,
                fetch_invoices=True,
            )
        finally:
            sys.path.pop(0)
        return str(summary["run_id"])

    def _controller_arguments(
        self, window_start: str, window_end: str
    ):
        arguments = [
            "--window-start",
            window_start,
            "--window-end",
            window_end,
            "--membership-db",
            str(self.membership_database),
            "--booking-db",
            str(self.settings.database_path),
            "--audit-db",
            str(self.audit_database),
            "--private-output-dir",
            str(self.base_dir),
            "--public-output-dir",
            str(self.base_dir),
            "--identity-links-csv",
            str(self.identity_links_path),
            "--account-classifications-csv",
            str(self.account_classifications_path),
            "--legacy-evidence-csv",
            str(self.legacy_evidence_path),
            "--timing-items-csv",
            str(self.timing_items_path),
        ]
        return controller_parser().parse_args(arguments)

    def _write_state(self, state: dict[str, Any]) -> None:
        temporary = self.latest_state_path.with_suffix(".tmp")
        temporary.write_text(
            json.dumps(state, indent=2, default=str),
            encoding="utf-8",
        )
        temporary.replace(self.latest_state_path)

    def latest_state(self) -> dict[str, Any] | None:
        if not self.latest_state_path.exists():
            return None
        return json.loads(self.latest_state_path.read_text(encoding="utf-8"))

    @staticmethod
    def _validate_iso_date(value: Any, field: str) -> str:
        text = str(value or "").strip()
        if not text:
            return ""
        try:
            date.fromisoformat(text)
        except ValueError as exc:
            raise ValueError(f"{field} must be an ISO date") from exc
        return text

    def replace_legacy_evidence(self, rows: list[dict[str, Any]]) -> dict[str, Any]:
        if not isinstance(rows, list):
            raise ValueError("rows must be a list")
        if len(rows) > 500:
            raise ValueError("rows cannot exceed 500 entries")

        cleaned: list[dict[str, str]] = []
        seen: set[str] = set()
        for position, row in enumerate(rows, start=1):
            if not isinstance(row, dict):
                raise ValueError(f"row {position} must be an object")
            email = str(row.get("email") or "").strip().lower()
            if not EMAIL_PATTERN.fullmatch(email):
                raise ValueError(f"row {position} has an invalid email")
            if email in seen:
                raise ValueError(f"duplicate email at row {position}")
            seen.add(email)

            rail = str(row.get("payment_rail") or "").strip()
            if rail.lower() not in {
                "ptminder",
                "ezidebit",
                "ptminder/ezidebit",
            }:
                raise ValueError(f"row {position} has an unapproved payment rail")

            status = str(row.get("status") or "").strip().lower()
            if status not in LEGACY_EVIDENCE_STATUSES:
                raise ValueError(f"row {position} has an invalid status")

            amount_text = str(row.get("weekly_amount") or "").strip()
            try:
                amount = Decimal(amount_text)
            except InvalidOperation as exc:
                raise ValueError(f"row {position} has an invalid weekly amount") from exc
            if amount <= 0 or amount > Decimal("5000"):
                raise ValueError(f"row {position} has an invalid weekly amount")

            notes = " ".join(str(row.get("notes") or "").split())
            if len(notes) > 500:
                raise ValueError(f"row {position} notes exceed 500 characters")

            cleaned.append(
                {
                    "email": email,
                    "payment_rail": "PTMinder/EziDebit",
                    "status": status,
                    "weekly_amount": f"{amount:.2f}",
                    "last_receipt_date": self._validate_iso_date(
                        row.get("last_receipt_date"), "last_receipt_date"
                    ),
                    "next_due_date": self._validate_iso_date(
                        row.get("next_due_date"), "next_due_date"
                    ),
                    "notes": notes,
                }
            )

        output = io.StringIO(newline="")
        writer = csv.DictWriter(output, fieldnames=LEGACY_EVIDENCE_FIELDS)
        writer.writeheader()
        writer.writerows(cleaned)
        payload = output.getvalue().encode("utf-8")
        temporary = self.legacy_evidence_path.with_suffix(".tmp")
        temporary.write_bytes(payload)
        temporary.replace(self.legacy_evidence_path)
        return {
            "status": "replaced",
            "rowCount": len(cleaned),
            "sha256": hashlib.sha256(payload).hexdigest(),
        }

    def legacy_evidence_status(self) -> dict[str, Any]:
        if not self.legacy_evidence_path.exists():
            return {"status": "not_found", "rowCount": 0}
        payload = self.legacy_evidence_path.read_bytes()
        with io.StringIO(payload.decode("utf-8-sig")) as handle:
            row_count = sum(1 for _ in csv.DictReader(handle))
        return {
            "status": "ready",
            "rowCount": row_count,
            "sha256": hashlib.sha256(payload).hexdigest(),
            "updatedAt": datetime.fromtimestamp(
                self.legacy_evidence_path.stat().st_mtime,
                tz=self.settings.timezone,
            ).isoformat(),
        }

    @staticmethod
    def _weekly_amount(row: dict[str, Any]) -> str:
        amount = Decimal(str(row.get("amount") or "0"))
        receipt = date.fromisoformat(str(row["last_successful_payment"]))
        due = date.fromisoformat(str(row["next_scheduled_payment"]))
        interval_weeks = max(1, round((due - receipt).days / 7))
        return f"{amount / interval_weeks:.2f}"

    def refresh_hub_pt_minder_shadow(self) -> dict[str, Any]:
        snapshot = fetch_latest_source("pt_minder", max_age_hours=192)
        rows = snapshot.get("payload", {}).get("rows")
        if not isinstance(rows, list):
            raise ValueError("PT Minder hub snapshot rows are missing")

        aliases: dict[str, str] = {}
        if self.identity_links_path.exists():
            with self.identity_links_path.open(
                newline="", encoding="utf-8-sig"
            ) as handle:
                for row in csv.DictReader(handle):
                    canonical = str(
                        row.get("canonical_email") or ""
                    ).strip().lower()
                    linked = str(
                        row.get("linked_email") or ""
                    ).strip().lower()
                    if canonical and linked:
                        aliases[linked] = canonical

        hub: dict[str, dict[str, str]] = {}
        for row in rows:
            email = str(row.get("email") or "").strip().lower()
            email = aliases.get(email, email)
            if (
                not EMAIL_PATTERN.fullmatch(email)
                or row.get("state") != "collecting"
                or not row.get("amount")
                or not row.get("last_successful_payment")
                or not row.get("next_scheduled_payment")
            ):
                continue
            hub[email] = {
                "status": "collecting",
                "weekly_amount": self._weekly_amount(row),
                "last_receipt_date": str(row["last_successful_payment"]),
                "next_due_date": str(row["next_scheduled_payment"]),
            }

        legacy: dict[str, dict[str, str]] = {}
        if self.legacy_evidence_path.exists():
            with self.legacy_evidence_path.open(
                newline="", encoding="utf-8-sig"
            ) as handle:
                for row in csv.DictReader(handle):
                    email = str(row.get("email") or "").strip().lower()
                    if email:
                        legacy[email] = {
                            "status": str(row.get("status") or "").strip().lower(),
                            "weekly_amount": (
                                f"{Decimal(str(row.get('weekly_amount'))):.2f}"
                            ),
                            "last_receipt_date": str(
                                row.get("last_receipt_date") or ""
                            ).strip(),
                            "next_due_date": str(
                                row.get("next_due_date") or ""
                            ).strip(),
                        }

        shared = sorted(set(hub) & set(legacy))
        mismatched = [
            email for email in shared if hub[email] != legacy[email]
        ]
        mismatch_field_counts = {
            field: sum(
                1
                for email in mismatched
                if hub[email].get(field) != legacy[email].get(field)
            )
            for field in (
                "status",
                "weekly_amount",
                "last_receipt_date",
                "next_due_date",
            )
        }
        state = {
            "status": "parity" if not mismatched else "differences_found",
            "snapshotId": snapshot.get("snapshot_id"),
            "fingerprint": snapshot.get("fingerprint"),
            "observedAt": snapshot.get("observed_at"),
            "hubEligibleRows": len(hub),
            "legacyRows": len(legacy),
            "matchedRows": len(shared) - len(mismatched),
            "mismatchedRows": len(mismatched),
            "hubOnlyRows": len(set(hub) - set(legacy)),
            "legacyOnlyRows": len(set(legacy) - set(hub)),
            "mismatchFieldCounts": mismatch_field_counts,
            "cutoverEligible": (
                not mismatched and set(hub) == set(legacy) and bool(hub)
            ),
            "privateDifferences": {
                "mismatched": mismatched,
                "hubOnly": sorted(set(hub) - set(legacy)),
                "legacyOnly": sorted(set(legacy) - set(hub)),
            },
            "checkedAt": datetime.now(self.settings.timezone).isoformat(),
        }
        temporary = self.hub_pt_minder_state_path.with_suffix(".tmp")
        temporary.write_text(
            json.dumps(state, indent=2),
            encoding="utf-8",
        )
        temporary.replace(self.hub_pt_minder_state_path)
        return {
            key: value
            for key, value in state.items()
            if key != "privateDifferences"
        }

    def hub_pt_minder_status(self) -> dict[str, Any]:
        if not self.hub_pt_minder_state_path.exists():
            return {"status": "not_checked"}
        state = json.loads(
            self.hub_pt_minder_state_path.read_text(encoding="utf-8")
        )
        return {
            key: value
            for key, value in state.items()
            if key != "privateDifferences"
        }

    @staticmethod
    def _atomic_csv(
        path: Path,
        fieldnames: list[str],
        rows: list[dict[str, str]],
    ) -> dict[str, Any]:
        output = io.StringIO(newline="")
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
        payload = output.getvalue().encode("utf-8")
        temporary = path.with_suffix(".tmp")
        temporary.write_bytes(payload)
        temporary.replace(path)
        return {
            "status": "replaced",
            "rowCount": len(rows),
            "sha256": hashlib.sha256(payload).hexdigest(),
        }

    def replace_identity_links(self, rows: list[dict[str, Any]]) -> dict[str, Any]:
        if not isinstance(rows, list) or len(rows) > 500:
            raise ValueError("rows must be a list with at most 500 entries")
        cleaned: list[dict[str, str]] = []
        seen: set[tuple[str, str]] = set()
        for position, row in enumerate(rows, start=1):
            canonical = str(row.get("canonical_email") or "").strip().lower()
            linked = str(row.get("linked_email") or "").strip().lower()
            if not EMAIL_PATTERN.fullmatch(canonical) or not EMAIL_PATTERN.fullmatch(linked):
                raise ValueError(f"row {position} has an invalid email")
            if canonical == linked:
                raise ValueError(f"row {position} links an email to itself")
            pair = (canonical, linked)
            if pair in seen:
                raise ValueError(f"duplicate identity link at row {position}")
            seen.add(pair)
            cleaned.append(
                {
                    "canonical_email": canonical,
                    "linked_email": linked,
                    "confirmed_name": " ".join(
                        str(row.get("confirmed_name") or "").split()
                    ),
                    "confirmed_by": " ".join(
                        str(row.get("confirmed_by") or "").split()
                    ),
                    "confirmed_date": self._validate_iso_date(
                        row.get("confirmed_date"), "confirmed_date"
                    ),
                    "note": " ".join(str(row.get("note") or "").split())[:500],
                }
            )
        return self._atomic_csv(
            self.identity_links_path,
            [
                "canonical_email",
                "linked_email",
                "confirmed_name",
                "confirmed_by",
                "confirmed_date",
                "note",
            ],
            cleaned,
        )

    def replace_account_classifications(
        self, rows: list[dict[str, Any]]
    ) -> dict[str, Any]:
        if not isinstance(rows, list) or len(rows) > 500:
            raise ValueError("rows must be a list with at most 500 entries")
        cleaned: list[dict[str, str]] = []
        seen: set[str] = set()
        for position, row in enumerate(rows, start=1):
            email = str(row.get("email") or "").strip().lower()
            if not EMAIL_PATTERN.fullmatch(email):
                raise ValueError(f"row {position} has an invalid email")
            if email in seen:
                raise ValueError(f"duplicate account email at row {position}")
            seen.add(email)
            classification = str(row.get("classification") or "").strip().lower()
            if classification not in ACCOUNT_CLASSIFICATIONS:
                raise ValueError(f"row {position} has an invalid classification")
            approved = str(
                row.get("approved_active_without_local_entitlement") or ""
            ).strip().lower() in {"1", "true", "yes"}
            cleaned.append(
                {
                    "email": email,
                    "name": " ".join(str(row.get("name") or "").split()),
                    "classification": classification,
                    "approved_active_without_local_entitlement": (
                        "true" if approved else "false"
                    ),
                    "confirmed_by": " ".join(
                        str(row.get("confirmed_by") or "").split()
                    ),
                    "confirmed_date": self._validate_iso_date(
                        row.get("confirmed_date"), "confirmed_date"
                    ),
                    "note": " ".join(str(row.get("note") or "").split())[:500],
                }
            )
        return self._atomic_csv(
            self.account_classifications_path,
            [
                "email",
                "name",
                "classification",
                "approved_active_without_local_entitlement",
                "confirmed_by",
                "confirmed_date",
                "note",
            ],
            cleaned,
        )

    def shared_evidence_status(self) -> dict[str, Any]:
        def status(path: Path) -> dict[str, Any]:
            if not path.exists():
                return {"status": "not_found", "rowCount": 0}
            payload = path.read_bytes()
            with io.StringIO(payload.decode("utf-8-sig")) as handle:
                count = sum(1 for _ in csv.DictReader(handle))
            return {
                "status": "ready",
                "rowCount": count,
                "sha256": hashlib.sha256(payload).hexdigest(),
            }

        return {
            "legacyPayments": status(self.legacy_evidence_path),
            "identityLinks": status(self.identity_links_path),
            "accountClassifications": status(self.account_classifications_path),
            "hubPtMinder": self.hub_pt_minder_status(),
        }

    def _send_report(self, metadata: dict[str, Any], kind: str) -> dict[str, Any]:
        if not self.settings.resend_api_key:
            raise RuntimeError("RESEND_API_KEY is required to email the revenue report")
        summary_path = Path(metadata["reports"]["public_summary"])
        exceptions_path = Path(metadata["reports"]["exceptions"])
        summary = summary_path.read_text(encoding="utf-8")
        recipient = os.getenv(
            "REVENUE_REPORT_TO", "peter@theevolvedgym.com.au"
        ).strip()
        subject_label = (
            "Monday Active Client Revenue Audit"
            if kind == "monday"
            else "Friday KPI Cash Close"
        )
        response = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {self.settings.resend_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "from": self.settings.email_from,
                "to": [recipient],
                "subject": (
                    f"{subject_label} · "
                    f"{datetime.now(self.settings.timezone).strftime('%-d %b %Y')}"
                ),
                "html": (
                    "<html><body style='font-family:Arial,sans-serif;"
                    "max-width:760px;margin:0 auto;color:#222'>"
                    "<div style='background:#fff3cd;border:1px solid #e4c55b;"
                    "padding:12px;border-radius:6px'><strong>READ-ONLY CONTROL:"
                    " NO CLIENT RECORDS OR PAYMENTS WERE CHANGED</strong></div>"
                    f"<pre style='white-space:pre-wrap'>{html.escape(summary)}</pre>"
                    "</body></html>"
                ),
                "attachments": [
                    {
                        "filename": f"revenue-gap-exceptions-{metadata['run_id']}.csv",
                        "content": base64.b64encode(
                            exceptions_path.read_bytes()
                        ).decode("ascii"),
                    }
                ],
            },
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def run(
        self,
        *,
        kind: str,
        window_start: str,
        window_end: str,
        send_email: bool,
    ) -> dict[str, Any]:
        if kind not in {"monday", "friday"}:
            raise ValueError("kind must be monday or friday")
        if not self._lock.acquire(blocking=False):
            raise RuntimeError("A revenue-gap run is already in progress")
        started_at = datetime.now(self.settings.timezone).isoformat()
        try:
            source_run = self._membership_reconciliation()
            result, metadata = run_controller(
                self._controller_arguments(window_start, window_end)
            )
            state = {
                "status": "complete",
                "kind": kind,
                "startedAt": started_at,
                "completedAt": datetime.now(self.settings.timezone).isoformat(),
                "windowStart": window_start,
                "windowEnd": window_end,
                "membershipSourceRun": source_run,
                **metadata,
                "cashBridge": {
                    key: str(value)
                    for key, value in result.bridge.__dict__.items()
                },
                "emailStatus": "not_requested",
            }
            if send_email:
                try:
                    self._send_report(metadata, kind)
                    state["emailStatus"] = "sent"
                except Exception as exc:
                    state["emailStatus"] = f"failed: {type(exc).__name__}: {exc}"
                    log.exception("Revenue-gap report email failed")
            self._write_state(state)
            return state
        except Exception as exc:
            state = {
                "status": "failed",
                "kind": kind,
                "startedAt": started_at,
                "completedAt": datetime.now(self.settings.timezone).isoformat(),
                "windowStart": window_start,
                "windowEnd": window_end,
                "error": f"{type(exc).__name__}: {exc}",
            }
            self._write_state(state)
            log.exception("Revenue-gap run failed")
            raise
        finally:
            self._lock.release()
