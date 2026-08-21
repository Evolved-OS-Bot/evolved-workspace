from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    data_dir: Path
    webhook_secret: str
    max_reconciliation_age_days: int
    max_workout_age_days: int
    refresh_lookback_days: int

    @classmethod
    def from_env(cls) -> "Settings":
        data_dir = Path(
            os.getenv(
                "TRAINERIZE_PERFORMANCE_DATA_DIR",
                "/data/trainerize-performance",
            )
        )
        secret = os.getenv("WEBHOOK_SHARED_SECRET", "").strip()
        if not secret:
            raise RuntimeError("WEBHOOK_SHARED_SECRET is required")
        return cls(
            data_dir=data_dir,
            webhook_secret=secret,
            max_reconciliation_age_days=int(
                os.getenv("MAX_RECONCILIATION_AGE_DAYS", "8")
            ),
            max_workout_age_days=int(
                os.getenv("MAX_WORKOUT_AGE_DAYS", "14")
            ),
            refresh_lookback_days=int(
                os.getenv("TRAINERIZE_REFRESH_LOOKBACK_DAYS", "21")
            ),
        )

    @property
    def reconciliation_database(self) -> Path:
        return self.data_dir / "reconciliation.sqlite"

    @property
    def longitudinal_database(self) -> Path:
        return self.data_dir / "longitudinal.sqlite"

    @property
    def assessment_database(self) -> Path:
        return self.data_dir / "assessments.sqlite"
