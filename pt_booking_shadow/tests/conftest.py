from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from pt_booking_shadow.config import BRISBANE_TZ
from pt_booking_shadow.models import Appointment, CalendarRecord, PTContact


@pytest.fixture
def now():
    return datetime(2026, 7, 23, 12, 0, tzinfo=BRISBANE_TZ)


@pytest.fixture
def calendar():
    return CalendarRecord(
        id="cal-megan-30",
        name="30 Min 1:1 PT - Megan",
        trainer="Megan",
        duration_minutes=30,
        user_id="user-megan",
    )


@pytest.fixture
def contact():
    return PTContact(
        id="contact-1",
        name="Test Member",
        tags={"personal training", "1 p.wk"},
        custom_fields={},
        expected_frequency=1,
    )


def make_event(
    event_id,
    contact_id,
    calendar_id,
    start,
    duration=30,
    status="confirmed",
):
    return Appointment(
        id=event_id,
        contact_id=contact_id,
        calendar_id=calendar_id,
        start=start,
        end=start + timedelta(minutes=duration),
        status=status,
    )
