from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, datetime, time
from typing import Any


@dataclass(frozen=True)
class CalendarRecord:
    id: str
    name: str
    trainer: str
    duration_minutes: int
    user_id: str | None
    active: bool = True


@dataclass(frozen=True)
class Appointment:
    id: str
    contact_id: str
    calendar_id: str
    start: datetime
    end: datetime
    status: str
    assigned_user_id: str | None = None
    deleted: bool = False

    @property
    def duration_minutes(self) -> int:
        return max(0, round((self.end - self.start).total_seconds() / 60))


@dataclass
class PTContact:
    id: str
    name: str
    tags: set[str]
    custom_fields: dict[str, Any]
    stage_id: str | None = None
    expected_frequency: int | None = None
    effective_status: str = "active"
    status_reason: str = ""
    hold_start: date | None = None
    hold_end: date | None = None
    final_access: date | None = None


@dataclass(frozen=True)
class PatternSlot:
    weekday: int
    local_time: time
    calendar_id: str
    trainer: str
    duration_minutes: int
    confidence: float
    evidence_count: int

    @property
    def label(self) -> str:
        return (
            f"{['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][self.weekday]} "
            f"{self.local_time.strftime('%-I:%M %p')} · {self.trainer} · "
            f"{self.duration_minutes} min"
        )


@dataclass
class PatternResult:
    slots: list[PatternSlot] = field(default_factory=list)
    confidence: float = 0.0
    reason: str = ""
    expected_frequency: int | None = None
    inferred_frequency: int | None = None


@dataclass
class Finding:
    contact_id: str
    contact_name: str
    category: str
    reason: str
    effective_status: str
    expected_frequency: int | None = None
    inferred_frequency: int | None = None
    confidence: float = 0.0
    patterns: list[str] = field(default_factory=list)
    last_completed: str | None = None
    last_future: str | None = None
    booked_through: str | None = None
    coverage_weeks: int = 0
    proposed_dates: list[str] = field(default_factory=list)
    evidence: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
