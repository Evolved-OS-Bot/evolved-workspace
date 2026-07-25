from __future__ import annotations

import base64
import html
import json
import logging
import os
import sys
import threading
from datetime import datetime
from pathlib import Path
from typing import Any

import requests

from .cli import parser as controller_parser
from .cli import run as run_controller


log = logging.getLogger(__name__)


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
