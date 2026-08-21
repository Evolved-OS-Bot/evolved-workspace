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

from reporting_control.hub_membership_client import (
    publish_membership_snapshot,
)
from reporting_control.hub_client import publish_summary
from reporting_control.hub_roster_client import (
    build_roster_candidate_from_records,
    promote_roster_candidate_payload,
    publish_roster_candidate,
    publish_roster_candidate_payload,
)
from reporting_control.hub_revenue_commercial_client import (
    publish_revenue_commercial_evidence,
)
from reporting_control.hub_source_client import fetch_latest_source
from reporting_control.pt_roster_self_mending import (
    build_pt_roster_self_mending_shadow,
)

from .cli import parser as controller_parser
from .cli import run as run_controller
from .hub_contract import (
    fetch_revenue_contract,
    publish_revenue_parity,
    revenue_cutover_authority,
    revenue_roster_contract_complete,
)


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
PURCHASED_SERVICE_TERM_FIELDS = (
    "term_id",
    "stripe_invoice_id",
    "additional_stripe_invoice_ids",
    "purchaser_email",
    "beneficiary_email",
    "service_type",
    "quantity",
    "unit",
    "state",
    "effective_from",
    "effective_to",
    "approved_by",
    "approved_on",
    "note",
)
PURCHASED_SERVICE_TYPES = {"sgpt", "personal_training"}
PURCHASED_SERVICE_TERM_STATES = {"approved", "revoked"}
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
        self.purchased_service_terms_path = (
            self.base_dir / "purchased-service-terms.csv"
        )
        self.hub_pt_minder_state_path = (
            self.base_dir / "hub-pt-minder-parity.json"
        )
        self.pt_roster_self_mending_path = (
            self.base_dir / "pt-roster-self-mending.json"
        )
        self._lock = threading.Lock()
        self._roster_refresh_lock = threading.Lock()

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
        try:
            publish_membership_snapshot(
                self.membership_database,
                run_id=str(summary["run_id"]),
            )
        except Exception as exc:
            log.warning(
                "Canonical membership publish failed: %s",
                type(exc).__name__,
            )
        return str(summary["run_id"])

    def refresh_roster_candidate_shadow(self) -> dict[str, Any]:
        if not self._roster_refresh_lock.acquire(blocking=False):
            return {"status": "already_running"}
        try:
            scripts_dir = Path(__file__).resolve().parents[1] / "scripts"
            sys.path.insert(0, str(scripts_dir))
            try:
                from sheets_client import read_sheet

                from .sources import load_live_roster

                roster = load_live_roster(read_sheet)
            finally:
                sys.path.pop(0)
            observed_at = datetime.now(self.settings.timezone).isoformat(
                timespec="seconds"
            )
            payload = build_roster_candidate_from_records(
                roster,
                source_run_id=(
                    "google-roster-"
                    + datetime.now(self.settings.timezone).strftime(
                        "%Y%m%dT%H%M%S%z"
                    )
                ),
                observed_at=observed_at,
                identity_links_path=self.identity_links_path,
            )
            return self._publish_and_promote_roster_candidate(payload)
        finally:
            self._roster_refresh_lock.release()

    @staticmethod
    def _roster_signature(payload: dict[str, Any]) -> dict[str, tuple]:
        signature: dict[str, tuple] = {}
        for row in payload.get("rows") or []:
            services = tuple(
                sorted(
                    (
                        str(service.get("service_type") or ""),
                        str(service.get("status") or ""),
                        str(service.get("classification") or ""),
                        str(service.get("product") or ""),
                        str(service.get("assigned_trainer") or ""),
                        str(
                            service.get(
                                "contracted_weekly_frequency"
                            )
                            or ""
                        ),
                        str(service.get("service_duration") or ""),
                        str(service.get("weekly_allocation") or ""),
                        str(service.get("allocation_currency") or ""),
                        str(service.get("payment_marker") or ""),
                        str(service.get("allocation_basis") or ""),
                    )
                    for service in row.get("services") or []
                )
            )
            signature[str(row.get("canonical_key") or "").lower()] = services
        return signature

    @staticmethod
    def _governed_roster_signature(
        payload: dict[str, Any],
    ) -> dict[str, tuple[str, ...]]:
        signature: dict[str, tuple[str, ...]] = {}
        for row in payload.get("rows") or []:
            if not row.get("confirmed_active"):
                continue
            governed = (row.get("evidence") or {}).get(
                "governed_roster"
            ) or []
            signature[str(row.get("canonical_key") or "").lower()] = tuple(
                sorted(
                    str(service.get("service") or "")
                    for service in governed
                )
            )
        return signature

    @staticmethod
    def _latest_source_or_none(source: str) -> dict[str, Any] | None:
        try:
            return fetch_latest_source(source, max_age_hours=240)
        except Exception as exc:
            log.info(
                "No usable %s snapshot for roster acceptance: %s",
                source,
                type(exc).__name__,
            )
            return None

    def _publish_and_promote_roster_candidate(
        self,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        latest_candidate = self._latest_source_or_none(
            "active_roster_candidate"
        )
        unchanged = bool(
            latest_candidate
            and self._roster_signature(latest_candidate["payload"])
            == self._roster_signature(payload)
        )
        publish_result = publish_roster_candidate_payload(payload)

        snapshot_id = str(publish_result.get("snapshot_id") or "")
        result = {
            **publish_result,
            "contentUnchanged": unchanged,
            "candidateClients": len(payload["rows"]),
            "candidateServiceRelationships": sum(
                len(row["services"]) for row in payload["rows"]
            ),
        }
        if not snapshot_id:
            return result

        cohort = self._latest_source_or_none("active_client_cohort")
        if not cohort:
            return {
                **result,
                "acceptance": {
                    "status": "review_required",
                    "reason": "The governed client list is not available.",
                },
            }
        candidate_signature = self._roster_signature(payload)
        governed_signature = self._governed_roster_signature(
            cohort["payload"]
        )
        candidate_keys = set(candidate_signature)
        governed_keys = set(governed_signature)
        removed = sorted(governed_keys - candidate_keys)
        changed_services = sorted(
            key
            for key in candidate_keys & governed_keys
            if tuple(
                sorted(
                    service[0]
                    for service in candidate_signature[key]
                )
            )
            != governed_signature[key]
        )
        if removed or changed_services:
            return {
                **result,
                "acceptance": {
                    "status": "review_required",
                    "removedClients": len(removed),
                    "changedServices": len(changed_services),
                    "reason": (
                        "A removal or existing service change needs review."
                    ),
                },
            }

        source_refs = cohort["payload"].get("source_refs") or {}
        membership = self._latest_source_or_none(
            "membership_reconciliation"
        )
        commercial = self._latest_source_or_none(
            "commercial_evidence_stripe"
        )
        already_evaluated = bool(
            source_refs.get("roster_candidate_snapshot") == snapshot_id
            and (
                not membership
                or source_refs.get("membership_snapshot")
                == membership["snapshot_id"]
            )
            and (
                not commercial
                or source_refs.get("commercial_snapshot")
                == commercial["snapshot_id"]
            )
        )
        if already_evaluated:
            return {
                **result,
                "acceptance": {"status": "already_current"},
            }

        return {
            **result,
            "acceptance": promote_roster_candidate_payload(snapshot_id),
        }

    def refresh_commercial_evidence_shadow(self) -> dict[str, Any]:
        return publish_revenue_commercial_evidence(
            self.audit_database,
            identity_links_path=self.identity_links_path,
            legacy_evidence_path=self.legacy_evidence_path,
            account_classifications_path=self.account_classifications_path,
            purchased_service_terms_path=self.purchased_service_terms_path,
        )

    def refresh_pt_roster_self_mending_shadow(self) -> dict[str, Any]:
        scripts_dir = Path(__file__).resolve().parents[1] / "scripts"
        sys.path.insert(0, str(scripts_dir))
        try:
            from sheets_client import read_sheet

            sales_rows = read_sheet("Sales", "A1:T500")
            active_pt_rows = read_sheet("Active PT", "A1:K500")
        finally:
            sys.path.pop(0)

        membership = fetch_latest_source(
            "membership_reconciliation",
            max_age_hours=48,
        )
        commercial_snapshots = [
            fetch_latest_source(
                "commercial_evidence_stripe",
                max_age_hours=48,
            )
        ]
        try:
            commercial_snapshots.append(
                fetch_latest_source(
                    "commercial_evidence_stripe_pack",
                    max_age_hours=192,
                )
            )
        except Exception as exc:
            log.warning(
                "Stripe pack commercial evidence unavailable to PT "
                "roster shadow: %s",
                type(exc).__name__,
            )
        pt_minder = fetch_latest_source(
            "pt_minder",
            max_age_hours=192,
        )
        try:
            commercial_snapshots.append(
                fetch_latest_source(
                    "commercial_evidence_revenue_control",
                    max_age_hours=96,
                )
            )
        except Exception as exc:
            log.warning(
                "Revenue-control commercial evidence unavailable to PT "
                "roster shadow: %s",
                type(exc).__name__,
            )

        observed_at = datetime.now(self.settings.timezone).isoformat(
            timespec="seconds"
        )
        result = build_pt_roster_self_mending_shadow(
            sales_rows=sales_rows,
            active_pt_rows=active_pt_rows,
            membership_snapshot=membership,
            commercial_snapshots=commercial_snapshots,
            pt_minder_snapshot=pt_minder,
            observed_at=observed_at,
        )
        temporary = self.pt_roster_self_mending_path.with_suffix(".tmp")
        temporary.write_text(
            json.dumps(result, indent=2, default=str),
            encoding="utf-8",
        )
        temporary.replace(self.pt_roster_self_mending_path)
        hub_result = publish_summary(
            "pt_roster_self_mending",
            {
                **result["summary"],
                "mode": result["mode"],
                "sourceSnapshotIds": result["source_snapshot_ids"],
                "action_items": [
                    {
                        "client_name": case.get("client_name"),
                        "email": case["email"],
                        "state": case["state"],
                        "reason": case["reason"],
                    }
                    for case in result["cases"]
                    if case["state"]
                    in {"pending_terms", "pending_provisioning", "exception"}
                ],
            },
            observed_at=result["observed_at"],
        )
        return {
            **result["summary"],
            "status": result["status"],
            "mode": result["mode"],
            "observedAt": result["observed_at"],
            "hub": hub_result,
        }

    def pt_roster_self_mending_status(
        self,
        *,
        identified: bool = False,
    ) -> dict[str, Any]:
        if not self.pt_roster_self_mending_path.exists():
            return {"status": "not_found", "mode": "read_only_shadow"}
        state = json.loads(
            self.pt_roster_self_mending_path.read_text(encoding="utf-8")
        )
        if identified:
            return state
        return {
            "status": state["status"],
            "mode": state["mode"],
            "observedAt": state["observed_at"],
            **state["summary"],
        }

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
    def _weekly_amount_from_values(
        amount_value: Any,
        receipt_value: Any,
        due_value: Any,
    ) -> str:
        amount = Decimal(str(amount_value or "0"))
        receipt = date.fromisoformat(str(receipt_value))
        due = date.fromisoformat(str(due_value))
        interval_weeks = max(1, round((due - receipt).days / 7))
        return f"{amount / interval_weeks:.2f}"

    @classmethod
    def _weekly_amount(cls, row: dict[str, Any]) -> str:
        return cls._weekly_amount_from_values(
            row.get("amount"),
            row["last_successful_payment"],
            row["next_scheduled_payment"],
        )

    @classmethod
    def _recurring_transaction_evidence(
        cls,
        row: dict[str, Any],
    ) -> tuple[dict[str, str] | None, bool]:
        transactions = row.get("transactions")
        if not isinstance(transactions, list):
            return None, False
        recurring = [
            transaction
            for transaction in transactions
            if transaction.get("status") in {"completed", "pending"}
            and transaction.get("cadence") == "recurring"
            and transaction.get("occurred_on")
            and transaction.get("amount")
        ]
        completed = [
            transaction
            for transaction in recurring
            if transaction.get("status") == "completed"
        ]
        if not completed:
            return None, False
        latest_event_date = max(
            str(transaction["occurred_on"]) for transaction in recurring
        )
        current_types = {
            str(transaction.get("service_type") or "")
            for transaction in recurring
            if str(transaction["occurred_on"]) == latest_event_date
        }
        if len(current_types) > 1:
            return None, True
        latest = max(
            completed,
            key=lambda transaction: (
                str(transaction["occurred_on"]),
                str(transaction["source_transaction_id"]),
            ),
        )
        last_receipt = (
            str(row.get("last_successful_payment") or "").strip()
            or str(latest["occurred_on"])
        )
        next_due_candidates = {
            str(row.get("next_scheduled_payment") or "").strip(),
            *(
                str(transaction.get("next_scheduled_payment") or "").strip()
                for transaction in recurring
                if transaction.get("status") in {"completed", "pending"}
            ),
        }
        next_due = max(
            (candidate for candidate in next_due_candidates if candidate),
            default="",
        )
        weekly_amount = row.get("weekly_amount")
        if weekly_amount not in (None, ""):
            weekly_amount = f"{Decimal(str(weekly_amount)):.2f}"
        elif latest.get("next_scheduled_payment"):
            weekly_amount = cls._weekly_amount_from_values(
                latest["amount"],
                latest["occurred_on"],
                latest["next_scheduled_payment"],
            )
        else:
            return None, False
        if not next_due:
            return None, False
        return (
            {
                "status": "collecting",
                "weekly_amount": weekly_amount,
                "last_receipt_date": last_receipt,
                "next_due_date": next_due,
            },
            False,
        )

    @staticmethod
    def _pt_minder_row_is_collecting(row: dict[str, Any]) -> bool:
        product = str(row.get("product") or "").strip().lower()
        return row.get("state") == "collecting" and "paused" not in product

    def refresh_hub_pt_minder_shadow(self) -> dict[str, Any]:
        snapshot = fetch_latest_source("pt_minder", max_age_hours=192)
        payload = snapshot.get("payload", {})
        rows = payload.get("rows")
        if not isinstance(rows, list):
            raise ValueError("PT Minder hub snapshot rows are missing")
        transaction_detail_complete = (
            payload.get("transaction_detail_complete") is True
        )

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
        ambiguous_recurring: list[str] = []
        ad_hoc_pt_transactions = 0
        ad_hoc_pt_cash = Decimal("0")
        for row in rows:
            email = str(row.get("email") or "").strip().lower()
            email = aliases.get(email, email)
            for transaction in row.get("transactions") or []:
                if (
                    transaction.get("status") == "completed"
                    and transaction.get("service_type")
                    == "personal_training"
                    and transaction.get("cadence") == "ad_hoc"
                ):
                    ad_hoc_pt_transactions += 1
                    ad_hoc_pt_cash += Decimal(
                        str(transaction.get("amount") or "0")
                    )
            if transaction_detail_complete:
                evidence, ambiguous = self._recurring_transaction_evidence(row)
                if ambiguous and EMAIL_PATTERN.fullmatch(email):
                    ambiguous_recurring.append(email)
                if (
                    not EMAIL_PATTERN.fullmatch(email)
                    or not self._pt_minder_row_is_collecting(row)
                    or evidence is None
                ):
                    continue
                hub[email] = evidence
                continue
            if (
                not EMAIL_PATTERN.fullmatch(email)
                or not self._pt_minder_row_is_collecting(row)
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
        parity_equal = (
            not mismatched
            and set(hub) == set(legacy)
            and bool(hub)
        )
        if not transaction_detail_complete:
            status = "source_contract_incomplete"
        elif ambiguous_recurring:
            status = "ambiguous_recurring_streams"
        else:
            status = "parity" if parity_equal else "differences_found"
        state = {
            "status": status,
            "snapshotId": snapshot.get("snapshot_id"),
            "fingerprint": snapshot.get("fingerprint"),
            "observedAt": snapshot.get("observed_at"),
            "sourceContractVersion": payload.get("schema_version", 1),
            "transactionDetailComplete": transaction_detail_complete,
            "hubEligibleRows": len(hub),
            "legacyRows": len(legacy),
            "matchedRows": len(shared) - len(mismatched),
            "mismatchedRows": len(mismatched),
            "hubOnlyRows": len(set(hub) - set(legacy)),
            "legacyOnlyRows": len(set(legacy) - set(hub)),
            "mismatchFieldCounts": mismatch_field_counts,
            "ambiguousRecurringAccounts": len(ambiguous_recurring),
            "adHocPtTransactions": ad_hoc_pt_transactions,
            "adHocPtCash": f"{ad_hoc_pt_cash:.2f}",
            "cutoverEligible": (
                transaction_detail_complete
                and not ambiguous_recurring
                and parity_equal
            ),
            "privateDifferences": {
                "mismatched": mismatched,
                "hubOnly": sorted(set(hub) - set(legacy)),
                "legacyOnly": sorted(set(legacy) - set(hub)),
                "ambiguousRecurring": sorted(ambiguous_recurring),
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

    def replace_purchased_service_terms(
        self, rows: list[dict[str, Any]]
    ) -> dict[str, Any]:
        if not isinstance(rows, list) or len(rows) > 500:
            raise ValueError("rows must be a list with at most 500 entries")
        cleaned: list[dict[str, str]] = []
        seen_terms: set[str] = set()
        seen_invoice_beneficiaries: set[tuple[str, str, str]] = set()
        for position, row in enumerate(rows, start=1):
            if not isinstance(row, dict):
                raise ValueError(f"row {position} must be an object")
            term_id = str(row.get("term_id") or "").strip()
            if not term_id or len(term_id) > 120:
                raise ValueError(f"row {position} has an invalid term_id")
            if term_id in seen_terms:
                raise ValueError(f"duplicate term_id at row {position}")
            seen_terms.add(term_id)
            invoice_id = str(row.get("stripe_invoice_id") or "").strip()
            if not invoice_id.startswith("in_") or len(invoice_id) > 120:
                raise ValueError(
                    f"row {position} has an invalid Stripe invoice ID"
                )
            additional_value = row.get("additional_stripe_invoice_ids") or []
            if isinstance(additional_value, str):
                additional_invoice_ids = [
                    value.strip()
                    for value in re.split(r"[;,]", additional_value)
                    if value.strip()
                ]
            elif isinstance(additional_value, list):
                additional_invoice_ids = [
                    str(value).strip()
                    for value in additional_value
                    if str(value).strip()
                ]
            else:
                raise ValueError(
                    f"row {position} has invalid additional invoice IDs"
                )
            all_invoice_ids = [invoice_id, *additional_invoice_ids]
            if (
                len(set(all_invoice_ids)) != len(all_invoice_ids)
                or any(
                    not value.startswith("in_") or len(value) > 120
                    for value in all_invoice_ids
                )
            ):
                raise ValueError(
                    f"row {position} has invalid additional invoice IDs"
                )
            purchaser = str(
                row.get("purchaser_email") or ""
            ).strip().lower()
            beneficiary = str(
                row.get("beneficiary_email") or ""
            ).strip().lower()
            if not EMAIL_PATTERN.fullmatch(purchaser):
                raise ValueError(
                    f"row {position} has an invalid purchaser email"
                )
            if not EMAIL_PATTERN.fullmatch(beneficiary):
                raise ValueError(
                    f"row {position} has an invalid beneficiary email"
                )
            service_type = str(
                row.get("service_type") or ""
            ).strip().lower()
            if service_type not in PURCHASED_SERVICE_TYPES:
                raise ValueError(
                    f"row {position} has an invalid service type"
                )
            unique_binding = (invoice_id, beneficiary, service_type)
            if unique_binding in seen_invoice_beneficiaries:
                raise ValueError(
                    "duplicate invoice, beneficiary and service binding "
                    f"at row {position}"
                )
            seen_invoice_beneficiaries.add(unique_binding)
            state = str(row.get("state") or "").strip().lower()
            if state not in PURCHASED_SERVICE_TERM_STATES:
                raise ValueError(f"row {position} has an invalid state")
            effective_from = self._validate_iso_date(
                row.get("effective_from"), "effective_from"
            )
            effective_to = self._validate_iso_date(
                row.get("effective_to"), "effective_to"
            )
            if not effective_from or not effective_to:
                raise ValueError(
                    f"row {position} requires exact effective dates"
                )
            if effective_from > effective_to:
                raise ValueError(
                    f"row {position} effective_from follows effective_to"
                )
            approved_by = " ".join(
                str(row.get("approved_by") or "").split()
            )
            approved_on = self._validate_iso_date(
                row.get("approved_on"), "approved_on"
            )
            if not approved_by or not approved_on:
                raise ValueError(
                    f"row {position} requires approval provenance"
                )
            quantity = str(row.get("quantity") or "").strip()
            if quantity:
                try:
                    parsed_quantity = Decimal(quantity)
                except InvalidOperation as exc:
                    raise ValueError(
                        f"row {position} has an invalid quantity"
                    ) from exc
                if parsed_quantity <= 0 or parsed_quantity > Decimal("10000"):
                    raise ValueError(
                        f"row {position} quantity is out of range"
                    )
                quantity = str(parsed_quantity)
            unit = " ".join(str(row.get("unit") or "").split())[:80]
            if bool(quantity) != bool(unit):
                raise ValueError(
                    f"row {position} quantity and unit must be supplied together"
                )
            cleaned.append(
                {
                    "term_id": term_id,
                    "stripe_invoice_id": invoice_id,
                    "additional_stripe_invoice_ids": ";".join(
                        additional_invoice_ids
                    ),
                    "purchaser_email": purchaser,
                    "beneficiary_email": beneficiary,
                    "service_type": service_type,
                    "quantity": quantity,
                    "unit": unit,
                    "state": state,
                    "effective_from": effective_from,
                    "effective_to": effective_to,
                    "approved_by": approved_by,
                    "approved_on": approved_on,
                    "note": " ".join(
                        str(row.get("note") or "").split()
                    )[:500],
                }
            )
        return self._atomic_csv(
            self.purchased_service_terms_path,
            list(PURCHASED_SERVICE_TERM_FIELDS),
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
            "purchasedServiceTerms": status(
                self.purchased_service_terms_path
            ),
            "hubPtMinder": self.hub_pt_minder_status(),
        }

    def purchased_service_terms(self) -> dict[str, Any]:
        rows: list[dict[str, str]] = []
        if self.purchased_service_terms_path.exists():
            with self.purchased_service_terms_path.open(
                encoding="utf-8-sig", newline=""
            ) as handle:
                rows = list(csv.DictReader(handle))
        return {
            "status": "ready" if rows else "not_found",
            "rowCount": len(rows),
            "rows": rows,
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
            try:
                roster_candidate_hub = (
                    self.refresh_roster_candidate_shadow()
                )
            except Exception as exc:
                log.warning(
                    "Active roster candidate refresh failed: %s",
                    type(exc).__name__,
                )
                roster_candidate_hub = {
                    "status": "failed",
                    "error": type(exc).__name__,
                }
            source_run = self._membership_reconciliation()
            legacy_result, legacy_metadata = run_controller(
                self._controller_arguments(window_start, window_end)
            )
            result, metadata = legacy_result, legacy_metadata
            legacy_audit_run_id = str(legacy_metadata["run_id"])
            try:
                contract = fetch_revenue_contract()
                parity, parallel_result = publish_revenue_parity(
                    contract=contract,
                    database=self.audit_database,
                    run_id=legacy_audit_run_id,
                    legacy_source_run=source_run,
                )
                roster_complete = revenue_roster_contract_complete(contract)
                try:
                    authority = revenue_cutover_authority()
                    promotion_ready = bool(
                        authority.promotion_authorised
                        and parity.equivalent
                        and roster_complete
                    )
                    cutover_state = authority.effective_state
                except Exception as exc:
                    promotion_ready = False
                    cutover_state = (
                        f"unavailable:{type(exc).__name__}"
                    )
                person_contract = {
                    "status": "shadow_compared",
                    "contractVersion": contract.contract_version,
                    "snapshotId": contract.snapshot_id,
                    "equivalent": parity.equivalent,
                    "unexplainedEventCount": (
                        parity.unexplained_event_count
                    ),
                    "rosterAttributesComplete": roster_complete,
                    "parallelResult": parallel_result,
                    "authority": "legacy",
                    "promotionReady": promotion_ready,
                    "cutoverState": cutover_state,
                    "retainedReason": (
                        "A fresh schema-v2 governed roster cycle, two exact "
                        "scheduled comparisons and Hub publication approval "
                        "are required before the report input switches."
                    ),
                }
                if promotion_ready:
                    try:
                        result, metadata = run_controller(
                            self._controller_arguments(
                                window_start, window_end
                            ),
                            hub_contract=contract,
                        )
                        person_contract.update(
                            {
                                "status": "hub_authoritative",
                                "authority": "hub",
                                "retainedReason": None,
                                "hubAuditRunId": str(metadata["run_id"]),
                                "legacyComparisonRunId": (
                                    legacy_audit_run_id
                                ),
                            }
                        )
                    except Exception as exc:
                        result, metadata = legacy_result, legacy_metadata
                        person_contract.update(
                            {
                                "status": "legacy_fallback",
                                "authority": "legacy",
                                "failClosed": True,
                                "hubInputError": type(exc).__name__,
                                "retainedReason": (
                                    "The approved Hub input could not be "
                                    "projected into the existing report; the "
                                    "verified legacy run was restored."
                                ),
                            }
                        )
            except Exception as exc:
                log.warning(
                    "Hub revenue person-contract read failed closed to "
                    "legacy: %s",
                    type(exc).__name__,
                )
                person_contract = {
                    "status": "legacy_fallback",
                    "failClosed": True,
                    "error": type(exc).__name__,
                    "authority": "legacy",
                }
            try:
                completed_candidate = publish_roster_candidate(
                    self.audit_database,
                    run_id=legacy_audit_run_id,
                    identity_links_path=self.identity_links_path,
                )
                roster_candidate_hub["completedAuditPublish"] = (
                    completed_candidate
                )
            except Exception as exc:
                log.warning(
                    "Completed roster candidate publish failed: %s",
                    type(exc).__name__,
                )
                roster_candidate_hub["completedAuditPublish"] = {
                    "status": "failed",
                    "error": type(exc).__name__,
                }
            try:
                commercial_hub = publish_revenue_commercial_evidence(
                    self.audit_database,
                    run_id=legacy_audit_run_id,
                    identity_links_path=self.identity_links_path,
                    legacy_evidence_path=self.legacy_evidence_path,
                    account_classifications_path=(
                        self.account_classifications_path
                    ),
                    purchased_service_terms_path=(
                        self.purchased_service_terms_path
                    ),
                )
            except Exception as exc:
                log.warning(
                    "Revenue commercial-evidence publish failed: %s",
                    type(exc).__name__,
                )
                commercial_hub = {
                    "status": "failed",
                    "error": type(exc).__name__,
                }
            try:
                pt_roster_self_mending = (
                    self.refresh_pt_roster_self_mending_shadow()
                )
            except Exception as exc:
                log.warning(
                    "PT roster self-mending shadow failed: %s",
                    type(exc).__name__,
                )
                pt_roster_self_mending = {
                    "status": "failed",
                    "error": type(exc).__name__,
                    "mode": "read_only_shadow",
                }
            state = {
                "status": "complete",
                "kind": kind,
                "startedAt": started_at,
                "completedAt": datetime.now(self.settings.timezone).isoformat(),
                "windowStart": window_start,
                "windowEnd": window_end,
                "membershipSourceRun": source_run,
                "rosterCandidateHub": roster_candidate_hub,
                "commercialEvidenceHub": commercial_hub,
                "hubPersonContract": person_contract,
                "ptRosterSelfMending": pt_roster_self_mending,
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
