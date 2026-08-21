from __future__ import annotations

import logging
from collections import Counter
from datetime import date, datetime, timedelta
from typing import Any

from .classification import classify_member
from .config import BRISBANE_TZ, Settings
from .models import RetentionAssessment
from .sheets import RetentionSheetsWriter
from .source import (
    active_user_ids,
    load_active_members,
    run_source_reconciliation,
)
from .store import RetentionStore
from .trainerize_usage import TrainerizeUsageReader
from reporting_control.hub_client import publish_summary
from reporting_control.hub_commercial_client import (
    publish_stripe_commercial_evidence,
)
from reporting_control.hub_membership_client import (
    publish_membership_snapshot,
)
from .hub_contract import (
    apply_hub_authority,
    fetch_retention_contract,
    publish_retention_parity,
    retention_cutover_authority,
)


log = logging.getLogger(__name__)


class RetentionService:
    def __init__(
        self,
        settings: Settings,
        *,
        store: RetentionStore | None = None,
        usage_reader: TrainerizeUsageReader | None = None,
        sheets_writer: RetentionSheetsWriter | None = None,
    ):
        self.settings = settings
        self.store = store or RetentionStore(settings.database_url)
        self.usage_reader = usage_reader
        self.sheets_writer = sheets_writer

    @staticmethod
    def _week_start(today: date) -> date:
        return today - timedelta(days=today.weekday())

    def _writer(self) -> RetentionSheetsWriter:
        if self.sheets_writer is None:
            self.sheets_writer = RetentionSheetsWriter(self.settings)
        return self.sheets_writer

    def run(self, *, write_sheets: bool = False) -> dict[str, Any]:
        run_id = self.store.start_run()
        today = datetime.now(BRISBANE_TZ).date()
        try:
            source = run_source_reconciliation(self.settings)
            try:
                membership_hub = publish_membership_snapshot(
                    self.settings.reconciliation_database,
                    run_id=str(source["run_id"]),
                )
            except Exception as exc:
                log.warning(
                    "Canonical membership publish failed: %s",
                    type(exc).__name__,
                )
                membership_hub = {"status": "failed"}
            try:
                commercial_hub = publish_stripe_commercial_evidence(
                    self.settings.reconciliation_database,
                    run_id=str(source["run_id"]),
                )
            except Exception as exc:
                log.warning(
                    "Stripe commercial evidence publish failed: %s",
                    type(exc).__name__,
                )
                commercial_hub = {"status": "failed"}
            user_ids = active_user_ids(self.settings)
            reader = self.usage_reader or TrainerizeUsageReader()
            usage = reader.read_many(user_ids, today=today)
            source_run_id, members = load_active_members(
                self.settings,
                usage,
                source["account_classifications"],
            )
            person_contract = {"status": "unavailable"}
            try:
                contract = fetch_retention_contract()
                hub_members = apply_hub_authority(members, contract)
                parity, published = publish_retention_parity(
                    contract=contract,
                    legacy_members=members,
                    hub_members=hub_members,
                    comparison_cycle=run_id,
                    legacy_source_run=source_run_id,
                )
                try:
                    authority = retention_cutover_authority()
                    promoted = bool(
                        authority.promotion_authorised
                        and parity.equivalent
                    )
                    authority_state = authority.effective_state
                except Exception as exc:
                    promoted = False
                    authority_state = (
                        f"unavailable:{type(exc).__name__}"
                    )
                if promoted:
                    members = hub_members
                person_contract = {
                    "status": "shadow_compared",
                    "contractVersion": contract.contract_version,
                    "snapshotId": contract.snapshot_id,
                    "equivalent": parity.equivalent,
                    "unexplainedEventCount": (
                        parity.unexplained_event_count
                    ),
                    "parallelResult": published,
                    "authority": "hub" if promoted else "legacy",
                    "cutoverState": authority_state,
                }
            except Exception as exc:
                log.warning(
                    "Hub current-person shadow comparison unavailable: %s",
                    type(exc).__name__,
                )
                person_contract = {
                    "status": "legacy_fallback",
                    "failClosed": True,
                    "error": type(exc).__name__,
                    "authority": "legacy",
                }
            assessments = [
                classify_member(member, today=today) for member in members
            ]
            summary = self.store.complete_run(
                run_id, source_run_id, assessments
            )
            snapshot = datetime.now(BRISBANE_TZ).isoformat(timespec="seconds")
            sheet_result = {"status": "not_requested"}
            if write_sheets:
                sheet_result = self._writer().write(
                    assessments,
                    snapshot=snapshot,
                    week_start=self._week_start(today),
                    run_id=run_id,
                )
            result = {
                "status": "complete",
                "mode": "read_only_shadow",
                "runId": run_id,
                "sourceRunId": source_run_id,
                "memberCount": len(assessments),
                "includedCount": summary["included_count"],
                "statuses": summary["statuses"],
                "consecutiveSuccessfulRuns": self.store.consecutive_successes(),
                "sheets": sheet_result,
                "canonicalHub": membership_hub,
                "commercialHub": commercial_hub,
                "hubPersonContract": person_contract,
            }
            try:
                result["hub"] = publish_summary(
                    "retention_intelligence",
                    {
                        "runId": run_id,
                        "sourceRunId": source_run_id,
                        "memberCount": len(assessments),
                        "includedCount": summary["included_count"],
                        "statuses": summary["statuses"],
                        "consecutiveSuccessfulRuns": (
                            self.store.consecutive_successes()
                        ),
                    },
                )
            except Exception as exc:
                log.warning(
                    "Hub compatibility publish failed: %s",
                    type(exc).__name__,
                )
                result["hub"] = {"status": "failed"}
            log.info(
                "Retention run complete run=%s members=%s statuses=%s",
                run_id,
                len(assessments),
                dict(Counter(item.status for item in assessments)),
            )
            return result
        except Exception as exc:
            self.store.fail_run(run_id, str(exc))
            raise

    def preview(self) -> dict[str, Any]:
        radar = self.store.latest_radar()
        counts = Counter(row["status"] for row in radar)
        return {
            "latestRun": self.store.latest_summary(),
            "memberCount": len(radar),
            "statuses": dict(sorted(counts.items())),
            "members": radar,
        }
