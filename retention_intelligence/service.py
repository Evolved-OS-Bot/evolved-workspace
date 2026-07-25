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
            user_ids = active_user_ids(self.settings)
            reader = self.usage_reader or TrainerizeUsageReader()
            usage = reader.read_many(user_ids, today=today)
            source_run_id, members = load_active_members(
                self.settings,
                usage,
                source["account_classifications"],
            )
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
            }
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
