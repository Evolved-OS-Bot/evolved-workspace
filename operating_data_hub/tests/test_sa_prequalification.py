from operating_data_hub.sa_prequalification import (
    STAGE_KEYS,
    validate_observation_run,
    validate_review,
)
from operating_data_hub.store import HubStore


def observation_payload():
    stages = {
        key: {
            "state": "complete" if key == "exercise_history" else "not_asked",
            "value": (
                "no prior strength-training history"
                if key == "exercise_history"
                else None
            ),
            "evidence_message_ids": ["m1"] if key == "exercise_history" else [],
        }
        for key in STAGE_KEYS
    }
    return {
        "source_run_id": "run-1",
        "observed_at": "2026-08-17T01:00:00Z",
        "status": "complete",
        "complete": True,
        "cohort_fingerprint": "cohort-1",
        "rows": [
            {
                "appointment_id": "appointment-1",
                "contact_id": "contact-1",
                "conversation_id": "conversation-1",
                "contact_name": "Penn",
                "scheduled_at": "2026-08-20T01:00:00Z",
                "appointment_status": "confirmed",
                "case_state": "draft_ready",
                "first_incomplete_stage": "support_preference",
                "next_action": "review draft",
                "blocked_reasons": [],
                "conversation_complete": True,
                "conversation_fingerprint": "conversation-fingerprint",
                "latest_message_id": "m1",
                "latest_message_at": "2026-08-17T00:59:00Z",
                "stages": stages,
                "facts": {
                    "exercise_history": "no prior strength-training history"
                },
                "draft": {
                    "draft_id": "draft-1",
                    "stage": "support_preference",
                    "wording": "What support would help you feel most confident?",
                    "send_authorised": False,
                },
                "rule_version": "sa-prequalification-state-v1-observer",
            }
        ],
    }


def test_observation_and_review_contracts_force_no_send_authority():
    payload = validate_observation_run(observation_payload())
    assert payload["rows"][0]["first_incomplete_stage"] == "support_preference"
    review = validate_review(
        {
            "appointment_id": "appointment-1",
            "draft_id": "draft-1",
            "reviewer": "Peter",
            "action": "approved_unchanged",
            "reviewed_at": "2026-08-17T01:05:00Z",
        }
    )
    assert review["send_authorised"] is False


def test_store_persists_deduplicates_and_attributes_human_review():
    store = HubStore("sqlite+pysqlite:///:memory:")
    first = store.accept_sa_prequalification_observation(
        validate_observation_run(observation_payload())
    )
    repeat = store.accept_sa_prequalification_observation(
        validate_observation_run(observation_payload())
    )
    assert first["cases_created"] == 1
    assert repeat["status"] == "duplicate"
    rows = store.sa_prequalification_case_rows()
    assert rows[0]["facts"]["exercise_history"] == (
        "no prior strength-training history"
    )

    review = validate_review(
        {
            "appointment_id": "appointment-1",
            "draft_id": "draft-1",
            "reviewer": "Peter",
            "action": "rejected",
            "reason_codes": ["too_many_questions"],
            "reviewed_at": "2026-08-17T01:05:00Z",
        }
    )
    accepted = store.accept_sa_prequalification_review(review)
    duplicate = store.accept_sa_prequalification_review(review)
    assert accepted["status"] == "accepted"
    assert duplicate["status"] == "duplicate"
    events = store.sa_prequalification_events_for_case("appointment-1")
    review_event = [row for row in events if row["event_type"] == "draft_reviewed"]
    assert review_event[0]["actor"] == "Peter"
    assert review_event[0]["payload"]["send_authorised"] is False


def test_delivery_fingerprint_state_is_governed():
    store = HubStore("sqlite+pysqlite:///:memory:")
    preview = store.sa_prequalification_delivery_preview(
        delivery_key="hourly_actionable",
        queue_fingerprint="first",
    )
    assert preview["changed_since_delivery"] is True
    store.acknowledge_sa_prequalification_delivery(
        delivery_key="hourly_actionable",
        queue_fingerprint="first",
        payload={"destination": "discord"},
    )
    same = store.sa_prequalification_delivery_preview(
        delivery_key="hourly_actionable",
        queue_fingerprint="first",
    )
    changed = store.sa_prequalification_delivery_preview(
        delivery_key="hourly_actionable",
        queue_fingerprint="second",
    )
    assert same["changed_since_delivery"] is False
    assert changed["changed_since_delivery"] is True
