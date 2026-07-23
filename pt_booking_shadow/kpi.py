from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

from .config import BRISBANE_TZ, CURRENT_TRAINERS
from .models import Appointment, CalendarRecord


EXCLUDED_STATUSES = {
    "cancelled",
    "canceled",
    "no_show",
    "noshow",
    "no-show",
}


@dataclass(frozen=True)
class TrainerKPI:
    bookings: int = 0
    booked_minutes: int = 0

    @property
    def booked_hours(self) -> float:
        return round(self.booked_minutes / 60, 2)


@dataclass(frozen=True)
class WeeklyPTKPI:
    week_start: date
    trainers: dict[str, TrainerKPI]

    @property
    def total_bookings(self) -> int:
        return sum(item.bookings for item in self.trainers.values())

    @property
    def total_booked_hours(self) -> float:
        return round(
            sum(item.booked_minutes for item in self.trainers.values()) / 60,
            2,
        )

    def to_dict(self) -> dict:
        return {
            "week_start": self.week_start.isoformat(),
            "trainers": {
                trainer: {
                    "bookings": item.bookings,
                    "booked_minutes": item.booked_minutes,
                    "booked_hours": item.booked_hours,
                }
                for trainer, item in self.trainers.items()
            },
            "total_bookings": self.total_bookings,
            "total_booked_hours": self.total_booked_hours,
        }


def monday_for(value: datetime | date) -> date:
    local_date = (
        value.astimezone(BRISBANE_TZ).date()
        if isinstance(value, datetime)
        else value
    )
    return local_date - timedelta(days=local_date.weekday())


def aggregate_weekly_pt_kpi(
    events: list[Appointment],
    calendars: dict[str, CalendarRecord],
    week_start: date,
) -> WeeklyPTKPI:
    start = datetime.combine(week_start, time.min, tzinfo=BRISBANE_TZ)
    end = start + timedelta(days=7)
    mutable = {
        trainer: {"bookings": 0, "booked_minutes": 0}
        for trainer in CURRENT_TRAINERS
    }
    seen_ids: set[str] = set()
    seen_slots: set[tuple[str, str]] = set()

    for event in events:
        calendar = calendars.get(event.calendar_id)
        if not calendar or calendar.trainer not in mutable:
            continue
        local_start = event.start.astimezone(BRISBANE_TZ)
        if not start <= local_start < end:
            continue
        normalised_status = event.status.strip().lower().replace(" ", "_")
        if event.deleted or normalised_status in EXCLUDED_STATUSES:
            continue
        if event.id and event.id in seen_ids:
            continue
        if event.id:
            seen_ids.add(event.id)
        slot_key = (event.contact_id, local_start.isoformat())
        if slot_key in seen_slots:
            continue
        seen_slots.add(slot_key)

        mutable[calendar.trainer]["bookings"] += 1
        mutable[calendar.trainer]["booked_minutes"] += event.duration_minutes

    return WeeklyPTKPI(
        week_start=week_start,
        trainers={
            trainer: TrainerKPI(
                bookings=values["bookings"],
                booked_minutes=values["booked_minutes"],
            )
            for trainer, values in mutable.items()
        },
    )
