from __future__ import annotations

import json
import os
import threading
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from reporting_control.hub_client import publish_summary
from scripts.trainerize_performance_reporting import (
    run_performance_reporting,
)

from .config import Settings
from .refresh import refresh_sources


class PerformanceService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.settings.data_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._refresh_lock = threading.Lock()

    @property
    def state_path(self) -> Path:
        return self.settings.data_dir / "latest-run.json"

    @property
    def refresh_state_path(self) -> Path:
        return self.settings.data_dir / "latest-refresh.json"

    def sources_ready(self) -> bool:
        return all(
            path.exists()
            for path in (
                self.settings.reconciliation_database,
                self.settings.longitudinal_database,
                self.settings.assessment_database,
            )
        )

    def latest(self) -> dict[str, Any]:
        if not self.state_path.exists():
            return {"status": "not_found"}
        return json.loads(self.state_path.read_text(encoding="utf-8"))

    def latest_refresh(self) -> dict[str, Any]:
        if not self.refresh_state_path.exists():
            return {"status": "not_found"}
        return json.loads(
            self.refresh_state_path.read_text(encoding="utf-8")
        )

    @staticmethod
    def _write_json(path: Path, state: dict[str, Any]) -> None:
        temporary = path.with_suffix(
            f".{uuid.uuid4().hex}.tmp"
        )
        temporary.write_text(
            json.dumps(state, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        temporary.chmod(0o600)
        os.replace(temporary, path)

    def _write_state(self, state: dict[str, Any]) -> None:
        self._write_json(self.state_path, state)

    def run(self) -> dict[str, Any]:
        if not self._lock.acquire(blocking=False):
            raise RuntimeError("a performance report is already running")
        started_at = datetime.now(UTC).isoformat()
        try:
            if not self.sources_ready():
                raise RuntimeError("performance source bundle is not installed")
            summary = run_performance_reporting(
                reconciliation_database=(
                    self.settings.reconciliation_database
                ),
                longitudinal_database=self.settings.longitudinal_database,
                assessment_database=self.settings.assessment_database,
                private_dir=self.settings.data_dir / "private",
                public_dir=self.settings.data_dir / "public",
                max_reconciliation_age_days=(
                    self.settings.max_reconciliation_age_days
                ),
                max_workout_age_days=self.settings.max_workout_age_days,
            )
            state = {
                "status": "complete",
                "mode": "read_only_shadow",
                "startedAt": started_at,
                "completedAt": datetime.now(UTC).isoformat(),
                **summary,
            }
            try:
                state["hub"] = publish_summary(
                    "trainerize_performance",
                    {
                        "runId": summary["run_id"],
                        "activeRoster": summary["active_roster"],
                        "membersWithDetailedWorkouts": summary[
                            "members_with_detailed_workouts"
                        ],
                        "remarkableCandidates": summary[
                            "remarkable_candidates"
                        ],
                        "reassessmentDue": summary["reassessment_due"],
                        "detailedWorkoutSourceThrough": summary[
                            "detailed_workout_source_through"
                        ],
                        "strengthImprovement": summary[
                            "strength_improvement"
                        ],
                        "topPerformers": summary["top_performers"],
                        "workoutMilestones": summary[
                            "workout_milestones"
                        ],
                        "standardsEvidenceSchemaVersion": summary[
                            "standards_evidence_schema_version"
                        ],
                        "standardsEvidence": summary[
                            "standards_evidence"
                        ],
                        "standardsEvidenceCoverage": summary[
                            "standards_evidence_coverage"
                        ],
                        "sgptBookingEvents": summary[
                            "sgpt_booking_events"
                        ],
                    },
                )
            except Exception as exc:
                state["hub"] = {
                    "status": "failed",
                    "error": type(exc).__name__,
                }
            self._write_state(state)
            return state
        except Exception as exc:
            state = {
                "status": "failed",
                "mode": "read_only_shadow",
                "startedAt": started_at,
                "completedAt": datetime.now(UTC).isoformat(),
                "error": f"{type(exc).__name__}: {exc}",
            }
            self._write_state(state)
            raise
        finally:
            self._lock.release()

    def refresh_and_run(self) -> dict[str, Any]:
        if not self._refresh_lock.acquire(blocking=False):
            raise RuntimeError("a Trainerize source refresh is already running")
        started_at = datetime.now(UTC).isoformat()
        try:
            if not self.sources_ready():
                raise RuntimeError("performance source bundle is not installed")
            refresh = refresh_sources(
                reconciliation_database=(
                    self.settings.reconciliation_database
                ),
                longitudinal_database=self.settings.longitudinal_database,
                assessment_database=self.settings.assessment_database,
                lookback_days=self.settings.refresh_lookback_days,
            )
            refresh_state = {
                **refresh,
                "startedAt": started_at,
                "completedAt": datetime.now(UTC).isoformat(),
            }
            self._write_json(self.refresh_state_path, refresh_state)
            report = self.run()
            return {"refresh": refresh_state, "report": report}
        except Exception as exc:
            self._write_json(
                self.refresh_state_path,
                {
                    "status": "failed",
                    "startedAt": started_at,
                    "completedAt": datetime.now(UTC).isoformat(),
                    "error": f"{type(exc).__name__}: {exc}",
                },
            )
            raise
        finally:
            self._refresh_lock.release()
