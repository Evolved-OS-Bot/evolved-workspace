from datetime import UTC, datetime

import pytest

from operating_data_hub.conversation_clearance import (
    aggregate_cases,
    build_case,
    case_cycle_key,
    deterministic_category,
    resolution_from_observation,
    staffed_deadline,
)


def observation(**overrides):
    row = {
        "conversation_id": "conversation-1",
        "contact_id": "contact-1",
        "channel": "SMS",
        "latest_inbound_message_id": "message-in-1",
        "latest_inbound_at": "2026-08-10T00:00:00Z",
        "latest_inbound_excerpt": "Can you help with my booking?",
        "latest_outbound_message_id": None,
        "latest_outbound_at": None,
        "latest_outbound_is_automated": None,
        "message_history_complete": True,
        "classification": {
            "category": "member_administration",
            "action": "Review booking request",
            "version": "conversation-service-risk-v1",
        },
    }
    row.update(overrides)
    return row


def test_cycle_key_changes_only_for_new_inbound_cycle():
    first = observation()
    repeat = observation(latest_inbound_excerpt="Updated excerpt")
    new = observation(latest_inbound_message_id="message-in-2")
    assert case_cycle_key(first) == case_cycle_key(repeat)
    assert case_cycle_key(first) != case_cycle_key(new)


def test_deterministic_guards_fail_closed_and_protect_risk():
    assert (
        deterministic_category(
            "hello", message_history_complete=False
        )
        == "manual_review"
    )
    assert (
        deterministic_category("I was charged twice")
        == "immediate_service_risk"
    )
    assert (
        deterministic_category(
            "READY", is_sa_prequalification=True
        )
        == "revenue_sensitive"
    )


def test_staffed_deadline_rolls_after_hours_to_next_weekday():
    opened = datetime(2026, 8, 7, 8, 30, tzinfo=UTC)  # Friday 18:30 Brisbane
    due = staffed_deadline(opened, "immediate_service_risk")
    assert due == datetime(2026, 8, 9, 23, 0, tzinfo=UTC)  # Monday 09:00


def test_read_state_is_not_resolution_and_human_outbound_is():
    assert resolution_from_observation(observation(unread=False)) is None
    automated = observation(
        latest_outbound_message_id="out-1",
        latest_outbound_at="2026-08-10T00:01:00Z",
        latest_outbound_is_automated=True,
    )
    assert resolution_from_observation(automated) is None
    human = dict(automated, latest_outbound_is_automated=False)
    assert resolution_from_observation(human)["code"] == "responded"


def test_approved_dispositions_require_evidence():
    with pytest.raises(ValueError, match="approved_by"):
        resolution_from_observation(
            observation(),
            disposition={
                "code": "spam_or_solicitation",
                "approved_at": "2026-08-10T00:10:00Z",
            },
        )
    with pytest.raises(ValueError, match="task_id"):
        resolution_from_observation(
            observation(),
            disposition={
                "code": "delegated_to_owned_task",
                "approved_by": "Peter",
                "reason": "Needs billing reconciliation",
                "approved_at": "2026-08-10T00:10:00Z",
            },
        )


def test_build_and_aggregate_cases_keep_identified_content_out_of_summary():
    now = datetime(2026, 8, 10, 10, 0, tzinfo=UTC)
    case = build_case(observation(), observed_at=now)
    assert case["state"] == "overdue"
    summary = aggregate_cases([case], now=now)
    assert summary["opening_backlog"] == 1
    assert summary["overdue"] == 1
    assert "contact_id" not in summary
    assert "excerpt" not in summary
