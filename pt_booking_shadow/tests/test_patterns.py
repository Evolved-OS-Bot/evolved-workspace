from datetime import timedelta

from pt_booking_shadow.models import PTContact
from pt_booking_shadow.patterns import infer_pattern
from pt_booking_shadow.tests.conftest import make_event


def test_stable_future_series_produces_high_confidence(now, calendar, contact):
    events = []
    first = now + timedelta(days=(1 - now.weekday()) % 7)
    first = first.replace(hour=17, minute=15)
    for index in range(8):
        events.append(
            make_event(
                f"e{index}", contact.id, calendar.id, first + timedelta(weeks=index)
            )
        )
    result = infer_pattern(contact, events, {calendar.id: calendar}, now)
    assert result.confidence >= 0.80
    assert len(result.slots) == 1
    assert result.slots[0].weekday == 1


def test_one_off_reschedule_does_not_redefine_pattern(now, calendar, contact):
    events = []
    first = (now + timedelta(days=(1 - now.weekday()) % 7)).replace(
        hour=17, minute=15
    )
    for index in range(7):
        events.append(
            make_event(
                f"e{index}", contact.id, calendar.id, first + timedelta(weeks=index)
            )
        )
    events.append(
        make_event("moved", contact.id, calendar.id, first + timedelta(days=2, weeks=3))
    )
    result = infer_pattern(contact, events, {calendar.id: calendar}, now)
    assert len(result.slots) == 1
    assert result.slots[0].weekday == 1
    assert result.slots[0].local_time.hour == 17


def test_unknown_frequency_with_no_stable_slot_is_ambiguous(now, calendar):
    contact = PTContact(
        id="c1",
        name="Unknown Frequency",
        tags={"personal training"},
        custom_fields={},
    )
    events = [
        make_event("e1", contact.id, calendar.id, now + timedelta(days=1)),
        make_event("e2", contact.id, calendar.id, now + timedelta(days=4, hours=2)),
    ]
    result = infer_pattern(contact, events, {calendar.id: calendar}, now)
    assert result.confidence < 0.80
    assert result.inferred_frequency == 0
