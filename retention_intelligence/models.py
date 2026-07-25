from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class UsageMetrics:
    workouts_7d: int = 0
    workouts_28d: int = 0
    workouts_90d: int = 0
    baseline_workouts: int = 0
    baseline_weeks: float = 12.0
    last_workout_date: str | None = None
    days_since_last_workout: int | None = None

    @property
    def recent_weekly_rate(self) -> float:
        return round(self.workouts_28d / 4.0, 2)

    @property
    def baseline_weekly_rate(self) -> float:
        if self.baseline_weeks <= 0:
            return 0.0
        return round(self.baseline_workouts / self.baseline_weeks, 2)

    @property
    def change_percent(self) -> float | None:
        baseline = self.baseline_weekly_rate
        if baseline < 0.25:
            return None
        return round((self.recent_weekly_rate - baseline) / baseline * 100, 1)


@dataclass(frozen=True)
class MemberInput:
    trainerize_user_id: int
    email: str
    first_name: str
    last_name: str
    service: str | None
    trainer_name: str | None
    created_date: str | None
    latest_signed_in: str | None
    ghl_active: bool
    stripe_entitled: bool
    trainerize_active: bool
    cancellation_status: str | None
    final_access_date: str | None
    account_classification: str | None
    has_operational_exception: bool
    usage: UsageMetrics


@dataclass(frozen=True)
class RetentionAssessment:
    trainerize_user_id: int
    email: str
    first_name: str
    last_name: str
    service: str | None
    trainer_name: str | None
    status: str
    urgency: str
    data_confidence: str
    reason: str
    action_owner: str
    review_date: str | None
    latest_signed_in: str | None
    workouts_7d: int
    workouts_28d: int
    workouts_90d: int
    baseline_weekly_rate: float
    recent_weekly_rate: float
    change_percent: float | None
    last_workout_date: str | None
    days_since_last_workout: int | None
    classifier_version: str
    included_in_kpi: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
