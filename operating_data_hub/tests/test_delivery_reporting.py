from datetime import date

from operating_data_hub.delivery_reporting import sgpt_delivery_preview


def event(
    *,
    session="class-1",
    person="member-1",
    day="2026-07-21",
    local_time="17:00",
    trainer="Piper",
    class_name="Sculpt & Strength",
    outcome=None,
    booking_status="scheduled",
):
    return {
        "class_session_id": session,
        "person_key": person,
        "scheduled_date": day,
        "scheduled_start": f"{day}T07:00:00+00:00",
        "scheduled_local_time": local_time,
        "duration_minutes": 60,
        "class_name": class_name,
        "trainer_name": trainer,
        "booking_status": booking_status,
        "attendance_outcome": outcome,
    }


def test_sgpt_delivery_counts_member_bookings_and_class_sessions_separately():
    events = [
        event(person="member-1"),
        event(person="member-2"),
        event(
            session="class-2",
            person="member-1",
            day="2026-07-23",
            local_time="09:00",
            trainer="Nora",
        ),
    ]

    result = sgpt_delivery_preview(
        events,
        period_start="2026-07-20",
        period_end="2026-07-26",
        today=date(2026, 7, 29),
    )

    period = result["selected_period"]
    assert period["member_bookings"] == 3
    assert period["unique_members"] == 2
    assert period["class_sessions"] == 2
    assert period["coaching_hours"] == 2
    assert period["capacity_places"] == 30
    assert period["booked_fill_rate"] == 10
    assert period["attendance_available"] is False
    assert period["attended"] is None
    assert period["cancelled"] is None
    assert period["no_show"] is None
    assert period["outcome_evidence"]["inferred_outcome_records"] == 0


def test_explicit_outcomes_are_separate_and_cancellation_exits_fill_rate():
    events = [
        event(person="member-1", outcome="attended"),
        event(person="member-2", outcome="no_show"),
        event(person="member-3", outcome="cancelled"),
        event(person="member-4"),
    ]

    period = sgpt_delivery_preview(
        events,
        period_start="2026-07-20",
        period_end="2026-07-26",
        today=date(2026, 7, 29),
    )["selected_period"]

    assert period["booking_records"] == 4
    assert period["booked"] == 3
    assert period["attended"] == 1
    assert period["cancelled"] == 1
    assert period["no_show"] == 1
    assert period["unique_members_booked"] == 3
    assert period["unique_members_served"] == 1
    assert period["booked_fill_rate"] == 20
    assert period["attended_fill_rate"] == 6.7


def test_checked_in_false_or_elapsed_booking_never_becomes_no_show():
    row = event()
    row["checked_in"] = False

    period = sgpt_delivery_preview(
        [row],
        period_start="2026-07-20",
        period_end="2026-07-26",
        today=date(2026, 8, 2),
    )["selected_period"]

    assert period["booked"] == 1
    assert period["attendance_available"] is False
    assert period["no_show"] is None
    assert period["outcome_evidence"]["inferred_outcome_records"] == 0


def test_class_slot_and_trainer_breakdowns_use_brisbane_slot():
    events = [
        event(person="member-1", outcome="attended"),
        event(person="member-2"),
    ]

    period = sgpt_delivery_preview(
        events,
        period_start="2026-07-20",
        period_end="2026-07-26",
        today=date(2026, 7, 29),
    )["selected_period"]

    assert period["class_breakdown"][0]["class_name"] == "Sculpt & Strength"
    assert period["slot_breakdown"][0]["slot_key"] == "tuesday-17:00"
    assert period["trainer_breakdown"][0]["trainer"] == "Piper"
    assert period["trainer_breakdown"][0]["booked_utilisation"] == 13.3
    assert period["trainer_breakdown"][0]["attended_utilisation"] == 6.7
    assert period["timetable_reconciliation"]["coverage_percent"] == 100


def test_active_sgpt_no_delivery_uses_exact_governed_identity_set():
    events = [
        event(person="member-1"),
        event(person="member-2", outcome="cancelled"),
    ]

    period = sgpt_delivery_preview(
        events,
        period_start="2026-07-20",
        period_end="2026-07-26",
        today=date(2026, 7, 29),
        active_sgpt_person_keys={"member-1", "member-2", "member-3"},
    )["selected_period"]

    assert period["active_sgpt_members"] == 3
    assert period[
        "active_sgpt_members_no_booked_or_attended_delivery"
    ] == 2


def test_acceptance_metadata_is_aggregate_and_shadow_only():
    result = sgpt_delivery_preview(
        [event()],
        period_start="2026-07-20",
        period_end="2026-07-26",
        today=date(2026, 7, 29),
        source={
            "snapshot_id": "snapshot-1",
            "run_id": "run-1",
            "observed_at": "2026-07-29T01:00:00+00:00",
            "complete": True,
            "status": "complete",
        },
    )

    assert result["definition_version"] == "sgpt-delivery-v1"
    assert result["source"]["snapshot_id"] == "snapshot-1"
    assert result["source"]["run_id"] == "run-1"
    assert result["source"]["sample_count"] == 1
    assert result["acceptance"]["publication_state"] == "shadow"
    assert result["acceptance"]["accepted_dashboard_unchanged"] is True
    assert result["acceptance"]["kpi_workbook_unchanged"] is True


def test_duplicate_member_session_prefers_explicit_terminal_outcome():
    events = [
        event(person="member-1"),
        event(person="member-1", outcome="attended"),
    ]

    period = sgpt_delivery_preview(
        events,
        period_start="2026-07-20",
        period_end="2026-07-26",
        today=date(2026, 7, 29),
    )["selected_period"]

    assert period["raw_booking_records"] == 2
    assert period["booking_records"] == 1
    assert period["duplicate_records_removed"] == 1
    assert period["attended"] == 1
