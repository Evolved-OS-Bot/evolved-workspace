import pytest

from operating_data_hub.sa_attendance_sheet import (
    SA_ATTENDANCE_HEADERS,
    build_upsert_plan,
    validate_layout,
)


def attendance_row(appointment_id="appointment-1", status="confirmed"):
    return {
        "appointment_id": appointment_id,
        "contact_id": "contact-1",
        "start_at": "2026-07-29T08:00:00+00:00",
        "end_at": "2026-07-29T09:00:00+00:00",
        "assigned_user_id": "coach-1",
        "delivered_by": "",
        "canonical_status": status,
        "observed_at": "2026-07-29T10:00:00+00:00",
        "reconciliation_state": "elapsed_confirmed",
        "exception_code": "elapsed_confirmed",
        "rule_version": "sa-attendance-v1",
    }


def test_layout_must_match_exactly():
    validate_layout(SA_ATTENDANCE_HEADERS)
    with pytest.raises(ValueError, match="layout mismatch"):
        validate_layout((*SA_ATTENDANCE_HEADERS[:-1], "Wrong"))


def test_upsert_plan_appends_new_event():
    plan = build_upsert_plan(
        [list(SA_ATTENDANCE_HEADERS)],
        [attendance_row()],
    )
    assert plan["updates"] == []
    assert plan["appends"][0][0] == "appointment-1"


def test_upsert_plan_is_idempotent():
    first = build_upsert_plan(
        [list(SA_ATTENDANCE_HEADERS)],
        [attendance_row()],
    )
    existing = [list(SA_ATTENDANCE_HEADERS), first["appends"][0]]
    second = build_upsert_plan(existing, [attendance_row()])
    assert second == {"updates": [], "appends": []}


def test_upsert_plan_uses_configured_sheet_name():
    first = build_upsert_plan(
        [list(SA_ATTENDANCE_HEADERS)],
        [attendance_row()],
    )
    existing = [list(SA_ATTENDANCE_HEADERS), first["appends"][0]]
    changed = attendance_row(status="showed")
    plan = build_upsert_plan(
        existing,
        [changed],
        sheet_name="Governed SA",
    )
    assert plan["updates"][0]["range"] == "'Governed SA'!A2:O2"


def test_upsert_plan_rejects_duplicate_existing_event_ids():
    row = ["appointment-1"] + [""] * (len(SA_ATTENDANCE_HEADERS) - 1)
    with pytest.raises(ValueError, match="duplicate Appointment ID"):
        build_upsert_plan(
            [list(SA_ATTENDANCE_HEADERS), row, row],
            [attendance_row()],
        )
