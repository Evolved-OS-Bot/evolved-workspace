from datetime import UTC, datetime, timedelta

import pytest

from operating_data_hub.contracts import (
    validate_sa_attendance,
    validate_sa_feedback,
)
from operating_data_hub.sa_attendance import (
    LEGACY_UNRECORDED_COACH,
    normalise_event,
    normalise_feedback_submission,
    reconcile_attendance,
    summarise_attendance,
    validate_confirmed_to_showed,
)
from operating_data_hub.store import HubStore


NOW = datetime(2026, 7, 29, 10, 0, tzinfo=UTC)


def event(
    appointment_id: str,
    *,
    contact_id: str = "contact-1",
    status: str = "confirmed",
    end_at: datetime | None = None,
):
    end = end_at or NOW - timedelta(hours=2)
    return {
        "appointment_id": appointment_id,
        "contact_id": contact_id,
        "calendar_id": "calendar-1",
        "start_at": (end - timedelta(hours=1)).isoformat(),
        "end_at": end.isoformat(),
        "status": status,
        "assigned_user_id": "coach-1",
        "updated_at": None,
        "deleted": False,
        "observed_at": NOW.isoformat(),
    }


def feedback(
    submission_id: str,
    *,
    contact_id: str = "contact-1",
    submitted_at: datetime | None = None,
    delivered_by: str = "Megan",
):
    return {
        "contact_id": contact_id,
        "form_submission_id": submission_id,
        "submitted_at": (
            submitted_at or NOW - timedelta(minutes=30)
        ).isoformat(),
        "sales_outcome": "No Sale",
        "delivered_by": delivered_by,
        "delivery_key": f"delivery-{submission_id}",
    }


def snapshot(rows):
    return validate_sa_attendance(
        {
            "observed_at": NOW.isoformat(),
            "source_run_id": "run-1",
            "complete": True,
            "calendar_ids_requested": ["calendar-1"],
            "calendar_ids_completed": ["calendar-1"],
            "rows": rows,
        }
    )


def test_attendance_contract_rejects_partial_calendar_coverage():
    with pytest.raises(ValueError, match="cover every requested calendar"):
        validate_sa_attendance(
            {
                "observed_at": NOW.isoformat(),
                "source_run_id": "run-1",
                "complete": True,
                "calendar_ids_requested": ["calendar-1", "calendar-2"],
                "calendar_ids_completed": ["calendar-1"],
                "rows": [],
            }
        )


def test_appointment_booking_timestamp_is_preserved():
    row = normalise_event(
        {
            "id": "appointment-1",
            "contactId": "contact-1",
            "calendarId": "calendar-1",
            "dateAdded": "2026-07-20T00:00:00Z",
            "dateUpdated": "2026-07-21T00:00:00Z",
            "startTime": "2026-07-29T08:00:00Z",
            "endTime": "2026-07-29T09:00:00Z",
            "appointmentStatus": "confirmed",
        },
        observed_at=NOW,
    )

    assert row["booked_at"] == "2026-07-20T00:00:00+00:00"
    assert row["updated_at"] == "2026-07-21T00:00:00+00:00"
    assert snapshot([row])["rows"][0]["booked_at"] == row["booked_at"]


def test_feedback_contract_requires_roster_and_delivery_key():
    with pytest.raises(ValueError, match="canonical roster"):
        validate_sa_feedback(
            feedback("submission-1", delivered_by="Former coach")
        )
    invalid = feedback("submission-1")
    invalid["delivery_key"] = ""
    with pytest.raises(ValueError, match="delivery_key"):
        validate_sa_feedback(invalid)


def test_form_submission_is_minimised_and_uses_calendar_attribution():
    row = normalise_feedback_submission(
        {
            "id": "form-1",
            "contactId": "contact-1",
            "createdAt": NOW.isoformat(),
            "others": {
                "sales-field": "Sale ",
                "private_notes": "not retained",
            },
        },
        sales_outcome_field_id="sales-field",
    )
    assert row["sales_outcome"] == "Sale"
    assert row["delivered_by"] == LEGACY_UNRECORDED_COACH
    assert row["attribution_confidence"] == "assigned_calendar_trainer"
    assert "private_notes" not in row
    assert validate_sa_feedback(row)["delivered_by"] == (
        LEGACY_UNRECORDED_COACH
    )


def test_confirmed_with_one_feedback_proposes_showed():
    result = reconcile_attendance(
        [event("appointment-1")],
        [feedback("submission-1")],
        now=NOW,
    )
    row = result["rows"][0]
    assert row["reconciliation_state"] == "feedback_closes_confirmed"
    assert row["proposed_status"] == "showed"
    assert row["delivered_by"] == "coach-1"
    assert row["trainer_attribution_source"] == "assigned_calendar_trainer"
    assert result["summary"]["no_show"] == 0
    validate_confirmed_to_showed(event("appointment-1"), row)


def test_missing_feedback_never_creates_no_show():
    result = reconcile_attendance(
        [event("appointment-1")],
        [],
        now=NOW,
    )
    row = result["rows"][0]
    assert row["canonical_status"] == "confirmed"
    assert row["reconciliation_state"] == "elapsed_confirmed"
    assert row["proposed_status"] is None
    assert result["summary"]["no_show"] == 0


def test_pre_tracking_elapsed_confirmed_is_legacy_attended_not_rate_eligible():
    cutoff = datetime(2026, 7, 30, 0, 0, tzinfo=UTC)
    result = reconcile_attendance(
        [event("appointment-1")],
        [],
        now=NOW,
        legacy_showed_before=cutoff,
    )
    row = result["rows"][0]
    assert row["canonical_status"] == "showed"
    assert row["reconciliation_state"] == "legacy_attended"
    assert row["attendance_confidence"] == "legacy_aggregate"
    assert row["show_rate_eligible"] is False
    assert row["cancellation_rate_eligible"] is False
    assert row["conversion_eligible"] is True
    assert row["proposed_status"] is None
    assert result["summary"]["legacy_showed"] == 1
    assert result["summary"]["unresolved"] == 0
    assert result["summary"]["show_rate"] is None
    assert result["summary"]["cancellation_rate"] is None


def test_feedback_against_no_show_is_terminal_conflict():
    result = reconcile_attendance(
        [event("appointment-1", status="no_show")],
        [feedback("submission-1")],
        now=NOW,
    )
    assert result["rows"][0]["reconciliation_state"] == "terminal_conflict"
    assert result["rows"][0]["proposed_status"] is None
    assert result["exceptions"][0]["severity"] == "critical"


def test_cancelled_and_invalid_are_excluded_from_show_rate():
    rows = [
        {
            **event("showed", status="showed"),
            "canonical_status": "showed",
            "reconciliation_state": "terminal_consistent",
        },
        {
            **event("no-show", status="no_show"),
            "canonical_status": "no_show",
            "reconciliation_state": "terminal_consistent",
        },
        {
            **event("cancelled", status="cancelled"),
            "canonical_status": "cancelled",
            "reconciliation_state": "terminal_consistent",
        },
        {
            **event("invalid", status="invalid"),
            "canonical_status": "invalid",
            "reconciliation_state": "terminal_consistent",
        },
    ]
    summary = summarise_attendance(rows, now=NOW)
    assert summary["show_rate"] == 0.5
    assert summary["cancellation_rate"] == pytest.approx(1 / 3)
    assert summary["cancelled"] == 1
    assert summary["invalid"] == 1


def test_ambiguous_feedback_does_not_propose_a_write():
    result = reconcile_attendance(
        [
            event("appointment-1"),
            event(
                "appointment-2",
                end_at=NOW - timedelta(hours=3),
            ),
        ],
        [feedback("submission-1")],
        now=NOW,
    )
    assert all(row["proposed_status"] is None for row in result["rows"])
    assert result["exceptions"][0]["code"] == "ambiguous_feedback_match"


def test_same_day_feedback_disambiguates_repeat_appointments():
    earlier = event(
        "appointment-earlier",
        end_at=NOW - timedelta(days=5),
    )
    same_day = event(
        "appointment-same-day",
        end_at=NOW - timedelta(hours=2),
    )
    result = reconcile_attendance(
        [earlier, same_day],
        [feedback("submission-1")],
        now=NOW,
    )
    decisions = {
        item["appointment_id"]: item["reconciliation_state"]
        for item in result["rows"]
    }
    assert decisions["appointment-same-day"] == "feedback_closes_confirmed"
    assert decisions["appointment-earlier"] == "elapsed_confirmed"


def test_store_is_append_only_and_webhook_is_idempotent(tmp_path):
    store = HubStore(f"sqlite:///{tmp_path / 'hub.db'}")
    payload = snapshot([event("appointment-1")])
    first = store.accept_sa_attendance_snapshot(payload)
    second = store.accept_sa_attendance_snapshot(payload)
    assert first["observations_inserted"] == 1
    assert second["observations_inserted"] == 0

    valid_feedback = validate_sa_feedback(feedback("submission-1"))
    assert store.accept_sa_feedback(valid_feedback)["status"] == "accepted"
    assert store.accept_sa_feedback(valid_feedback)["status"] == "duplicate"

    result = reconcile_attendance(
        store.latest_sa_events(),
        store.sa_feedback_rows(),
        now=NOW,
    )
    persisted = store.record_sa_reconciliation(
        result["rows"],
        result["exceptions"],
    )
    repeated = store.record_sa_reconciliation(
        result["rows"],
        result["exceptions"],
    )
    assert persisted["decisions_inserted"] == 1
    assert repeated["decisions_inserted"] == 0


def test_reconciliation_decision_primary_key_race_is_idempotent(tmp_path):
    store = HubStore(f"sqlite:///{tmp_path / 'hub.db'}")
    store._stable_id = lambda *parts: "concurrent-decision"
    showed = {
        "appointment_id": "appointment-1",
        "contact_id": "contact-1",
        "canonical_status": "showed",
        "reconciliation_state": "terminal_consistent",
        "proposed_status": None,
        "feedback_submission_ids": [],
        "rule_version": "sa-attendance-v2",
    }
    cancelled = {
        **showed,
        "canonical_status": "cancelled",
    }

    first = store.record_sa_reconciliation([showed], [])
    collided = store.record_sa_reconciliation([cancelled], [])

    assert first["decisions_inserted"] == 1
    assert collided["decisions_inserted"] == 0
    assert len(store.sa_attendance_decisions()) == 1
