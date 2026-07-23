from datetime import date, datetime, timedelta

from pt_booking_shadow.config import BRISBANE_TZ, CURRENT_TRAINERS
from pt_booking_shadow.kpi import aggregate_weekly_pt_kpi
from pt_booking_shadow.models import Appointment, CalendarRecord


def event(
    event_id: str,
    contact_id: str,
    calendar_id: str,
    start: datetime,
    minutes: int,
    status: str = "confirmed",
    deleted: bool = False,
) -> Appointment:
    return Appointment(
        id=event_id,
        contact_id=contact_id,
        calendar_id=calendar_id,
        start=start,
        end=start + timedelta(minutes=minutes),
        status=status,
        deleted=deleted,
    )


def test_weekly_kpi_counts_bookings_and_hours_by_calendar_trainer():
    week = date(2026, 7, 20)
    calendars = {
        "megan-30": CalendarRecord(
            "megan-30", "30 Min 1:1 PT - Megan", "Megan", 30, "megan"
        ),
        "piper-45": CalendarRecord(
            "piper-45", "45 Min 1:1 PT - Piper", "Piper", 45, "piper"
        ),
        "leisa-60": CalendarRecord(
            "leisa-60", "60 Min 1:1 PT - Leisa", "Leisa", 60, "leisa"
        ),
    }
    start = datetime(2026, 7, 20, 8, 0, tzinfo=BRISBANE_TZ)
    events = [
        event("1", "a", "megan-30", start, 30),
        event("2", "b", "piper-45", start + timedelta(days=1), 45),
        event("3", "c", "leisa-60", start + timedelta(days=2), 60),
    ]

    result = aggregate_weekly_pt_kpi(events, calendars, week)

    assert result.total_bookings == 3
    assert result.total_booked_hours == 2.25
    assert result.trainers["Megan"].bookings == 1
    assert result.trainers["Megan"].booked_hours == 0.5
    assert result.trainers["Piper"].booked_hours == 0.75
    assert result.trainers["Leisa"].booked_hours == 1.0
    assert set(result.trainers) == set(CURRENT_TRAINERS)


def test_weekly_kpi_excludes_cancelled_deleted_outside_and_duplicates():
    week = date(2026, 7, 20)
    calendar = CalendarRecord(
        "nora-30", "30 Min 1:1 PT - Nora", "Nora", 30, "nora"
    )
    calendars = {calendar.id: calendar}
    start = datetime(2026, 7, 20, 9, 0, tzinfo=BRISBANE_TZ)
    events = [
        event("kept", "a", calendar.id, start, 30),
        event("kept", "a", calendar.id, start, 30),
        event("different-id", "a", calendar.id, start, 30),
        event("cancelled", "b", calendar.id, start + timedelta(hours=1), 30, "cancelled"),
        event("no-show", "c", calendar.id, start + timedelta(hours=2), 30, "no show"),
        event("deleted", "d", calendar.id, start + timedelta(hours=3), 30, deleted=True),
        event("next-week", "e", calendar.id, start + timedelta(days=7), 30),
    ]

    result = aggregate_weekly_pt_kpi(events, calendars, week)

    assert result.total_bookings == 1
    assert result.total_booked_hours == 0.5
