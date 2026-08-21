from datetime import date, timedelta

from pt_booking_shadow.models import CalendarRecord, PTContact
from pt_booking_shadow.reconciler import reconcile_contact
from pt_booking_shadow.tests.conftest import make_event


def weekly_events(now, contact, calendar, count=13, skip=None):
    first = (now + timedelta(days=(1 - now.weekday()) % 7)).replace(
        hour=17, minute=15
    )
    return [
        make_event(f"e{index}", contact.id, calendar.id, first + timedelta(weeks=index))
        for index in range(count)
        if index != skip
    ]


def test_complete_13_week_series_is_healthy(now, calendar, contact):
    finding = reconcile_contact(
        contact, weekly_events(now, contact, calendar), {calendar.id: calendar}, now
    )
    assert finding.category == "HEALTHY"
    assert finding.coverage_weeks == 13
    assert not finding.proposed_dates


def test_missing_middle_week_is_gap(now, calendar, contact):
    finding = reconcile_contact(
        contact,
        weekly_events(now, contact, calendar, skip=5),
        {calendar.id: calendar},
        now,
    )
    assert finding.category == "GAP_INSIDE_SERIES"
    assert len(finding.proposed_dates) == 1


def test_same_week_reschedule_covers_expected_session(now, calendar, contact):
    events = weekly_events(now, contact, calendar)
    moved = events[4]
    events[4] = make_event(
        "same-week-reschedule",
        contact.id,
        calendar.id,
        moved.start + timedelta(days=2, hours=1),
    )

    finding = reconcile_contact(contact, events, {calendar.id: calendar}, now)

    assert finding.category == "HEALTHY"
    assert not finding.proposed_dates
    assert not finding.evidence["adjacent_week_make_ups"]


def test_exact_trainer_cover_in_another_pt_calendar_is_not_a_gap(
    now, calendar, contact
):
    cover_calendar = CalendarRecord(
        id="cal-katrina-30",
        name="30 Min 1:1 PT - Katrina",
        trainer="Katrina",
        duration_minutes=30,
        user_id="user-katrina",
    )
    events = weekly_events(now, contact, calendar)
    covered = events[4]
    events[4] = make_event(
        "trainer-cover",
        contact.id,
        cover_calendar.id,
        covered.start,
    )

    finding = reconcile_contact(
        contact,
        events,
        {calendar.id: calendar, cover_calendar.id: cover_calendar},
        now,
    )

    assert finding.category == "HEALTHY"
    assert finding.coverage_weeks == 13
    assert not finding.proposed_dates
    assert finding.evidence["cross_calendar_exact_matches"] == [
        {
            "expected_start": covered.start.isoformat(),
            "actual_appointment_id": "trainer-cover",
            "expected_calendar_id": calendar.id,
            "actual_calendar_id": cover_calendar.id,
            "expected_trainer": "Megan",
            "actual_trainer": "Katrina",
        }
    ]


def test_exact_later_slot_is_not_consumed_by_an_earlier_gap(
    now, calendar, contact
):
    contact.expected_frequency = 2
    tuesday = (now + timedelta(days=(1 - now.weekday()) % 7)).replace(
        hour=17, minute=15
    )
    saturday = (now + timedelta(days=(5 - now.weekday()) % 7)).replace(
        hour=9, minute=0
    )
    events = []
    for week in range(13):
        if week != 4:
            events.append(
                make_event(
                    f"tue-{week}",
                    contact.id,
                    calendar.id,
                    tuesday + timedelta(weeks=week),
                )
            )
        events.append(
            make_event(
                f"sat-{week}",
                contact.id,
                calendar.id,
                saturday + timedelta(weeks=week),
            )
        )

    finding = reconcile_contact(contact, events, {calendar.id: calendar}, now)

    assert finding.category == "GAP_INSIDE_SERIES"
    assert finding.proposed_dates == [
        (tuesday + timedelta(weeks=4)).isoformat()
    ]


def test_expected_occurrences_inside_recorded_hold_window_are_excluded(
    now, calendar, contact
):
    events = weekly_events(now, contact, calendar)
    held = events.pop(4)
    contact.hold_start = held.start.date()
    contact.hold_end = held.start.date()

    finding = reconcile_contact(contact, events, {calendar.id: calendar}, now)

    assert finding.category == "HEALTHY"
    assert not finding.proposed_dates
    assert finding.evidence["hold_excluded_occurrences"] == [
        held.start.isoformat()
    ]


def test_next_week_surplus_covers_one_make_up(now, calendar, contact):
    events = weekly_events(now, contact, calendar)
    missed = events.pop(4)
    next_week = events[4]
    events.append(
        make_event(
            "next-week-make-up",
            contact.id,
            calendar.id,
            next_week.start + timedelta(days=2, hours=1),
        )
    )

    finding = reconcile_contact(contact, events, {calendar.id: calendar}, now)

    assert finding.category == "HEALTHY"
    assert not finding.proposed_dates
    assert finding.evidence["adjacent_week_make_ups"] == [
        {
            "missed_expected": missed.start.isoformat(),
            "make_up_appointment": (next_week.start + timedelta(days=2, hours=1)).isoformat(),
        }
    ]


def test_make_up_more_than_one_week_later_does_not_hide_gap(
    now, calendar, contact
):
    events = weekly_events(now, contact, calendar)
    events.pop(4)
    two_weeks_later = events[5]
    events.append(
        make_event(
            "late-extra",
            contact.id,
            calendar.id,
            two_weeks_later.start + timedelta(days=2, hours=1),
        )
    )

    finding = reconcile_contact(contact, events, {calendar.id: calendar}, now)

    assert finding.category == "GAP_INSIDE_SERIES"
    assert len(finding.proposed_dates) == 1
    assert not finding.evidence["adjacent_week_make_ups"]


def test_unexplained_extra_is_retained_as_evidence(now, calendar, contact):
    events = weekly_events(now, contact, calendar)
    events.append(
        make_event(
            "unexplained-extra",
            contact.id,
            calendar.id,
            events[4].start + timedelta(days=2, hours=1),
        )
    )

    finding = reconcile_contact(contact, events, {calendar.id: calendar}, now)

    assert finding.category == "HEALTHY"
    assert finding.evidence["unmatched_future_events"] == 1
    assert not finding.evidence["adjacent_week_make_ups"]


def test_short_series_would_top_up(now, calendar, contact):
    finding = reconcile_contact(
        contact,
        weekly_events(now, contact, calendar, count=8),
        {calendar.id: calendar},
        now,
    )
    assert finding.category == "WOULD_TOP_UP"
    assert len(finding.proposed_dates) == 5


def test_hold_never_recommends_removal(now, calendar, contact):
    contact.effective_status = "pt_hold"
    contact.hold_start = now.date()
    contact.hold_end = now.date() + timedelta(weeks=4)
    finding = reconcile_contact(
        contact, weekly_events(now, contact, calendar), {calendar.id: calendar}, now
    )
    assert finding.category == "PT_HOLD_ACTIVE"
    assert not finding.proposed_dates


def test_cancellation_requires_final_access_date(now, calendar, contact):
    contact.effective_status = "pt_cancellation"
    contact.final_access = None
    finding = reconcile_contact(
        contact, weekly_events(now, contact, calendar), {calendar.id: calendar}, now
    )
    assert finding.category == "CANCELLATION_DATE_MISSING"
    assert not finding.proposed_dates


def test_only_post_final_access_is_hypothetical_removal(now, calendar, contact):
    contact.effective_status = "pt_cancellation"
    contact.final_access = now.date() + timedelta(weeks=4)
    finding = reconcile_contact(
        contact, weekly_events(now, contact, calendar), {calendar.id: calendar}, now
    )
    assert finding.category == "WOULD_REMOVE_AFTER_CANCELLATION"
    assert all(
        __import__("datetime").datetime.fromisoformat(item).date() > contact.final_access
        for item in finding.proposed_dates
    )


def test_duplicate_future_time_is_flagged(now, calendar, contact):
    events = weekly_events(now, contact, calendar)
    events.append(
        make_event("duplicate", contact.id, calendar.id, events[0].start)
    )
    finding = reconcile_contact(contact, events, {calendar.id: calendar}, now)
    assert finding.category == "DUPLICATE_APPOINTMENT"
