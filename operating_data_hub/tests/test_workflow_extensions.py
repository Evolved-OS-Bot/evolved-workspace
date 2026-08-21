from datetime import UTC, datetime

import pytest

from operating_data_hub.workflow_extensions import (
    CONTRACT_VERSION,
    DecisionContractError,
    plan_workflow_extension,
    workflow_policy_registry,
)
from operating_data_hub.store import HubStore
from operating_data_hub.service import HubService


NOW = datetime(2026, 8, 2, 1, 0, tzinfo=UTC)


def decision(
    workflow_key: str = "onboarding_outcome_followup",
    *,
    acceptance_state: str = "accepted",
    action_type: str = "internal_task",
    owner_user_id: str = "ghl-user-1",
    suppression_reasons=None,
):
    return {
        "contract_version": CONTRACT_VERSION,
        "workflow_key": workflow_key,
        "decision_id": "decision-123",
        "decision_version": 1,
        "subject": {
            "person_id": "person-123",
            "contact_id": "contact-123",
        },
        "source": {
            "system": "ghl",
            "snapshot_id": "snapshot-123",
            "observed_at": "2026-08-02T00:30:00Z",
            "complete": True,
            "fresh": True,
        },
        "exception": {
            "code": "outcome_missing",
            "severity": "medium",
            "status": "open",
        },
        "acceptance": {
            "state": acceptance_state,
            "definition_id": "definition-1",
            "accepted_by": "Peter Brown",
            "technical_ready": True,
            "publication_authorised": False,
            "decision_authorised": acceptance_state == "accepted",
            "cutover": {
                "consumer": "",
                "authorised": False,
                "promotion_authorised": False,
                "status_record_id": "",
                "status_fingerprint": "",
                "distinct_parity_cycles": 0,
                "fresh_exact_parity": False,
                "contract_schema_version": 0,
            },
        },
        "action": {
            "type": action_type,
            "title": "Record the outcome",
            "body": "Use observed evidence only.",
            "owner": {
                "role": "Assigned Trainer",
                "user_id": owner_user_id,
            },
            "due_at": "2026-08-03T00:00:00Z",
        },
        "controls": {
            "dedupe_scope": "appointment-123:coach",
            "suppression_reasons": suppression_reasons or [],
            "consent": {"state": "not_required"},
        },
        "evidence": [
            {
                "authority": "ghl",
                "record_id": "appointment-123",
                "fingerprint": "evidence-fingerprint",
            }
        ],
    }


def test_accepted_internal_task_is_queued_with_stable_idempotency_key():
    first = plan_workflow_extension(decision(), now=NOW)
    second = plan_workflow_extension(decision(), now=NOW)
    assert first["outbox"]["state"] == "queued"
    assert (
        first["outbox"]["idempotency_key"]
        == second["outbox"]["idempotency_key"]
    )


def test_unaccepted_decision_is_preview_only():
    result = plan_workflow_extension(
        decision(acceptance_state="shadow"), now=NOW
    )
    assert result["outbox"]["state"] == "preview"
    assert "decision_not_accepted" in result["audit"]["result_reasons"]


def test_technical_readiness_without_decision_authority_is_preview_only():
    payload = decision()
    payload["acceptance"]["decision_authorised"] = False
    result = plan_workflow_extension(payload, now=NOW)
    assert result["outbox"]["state"] == "preview"
    assert "workflow_decision_not_authorised" in result["audit"][
        "result_reasons"
    ]


def test_unaccepted_workflow_policy_stays_preview_even_with_accepted_decision():
    result = plan_workflow_extension(
        decision("retention_intervention_review"), now=NOW
    )
    assert result["outbox"]["state"] == "preview"
    assert "workflow_policy_not_accepted" in result["audit"][
        "result_reasons"
    ]
    assert "consumer_cutover_not_authorised" in result["audit"][
        "result_reasons"
    ]
    assert "policy_owner_mismatch" in result["audit"]["result_reasons"]
    assert "oversight_owner_missing" in result["audit"]["result_reasons"]
    assert "primary_owner_unavailable" in result["audit"][
        "result_reasons"
    ]


def test_retention_owner_and_oversight_are_exact_and_absence_fails_closed():
    payload = decision("retention_intervention_review")
    payload["action"]["owner"] = {
        "role": "Member Experience",
        "user_id": "WOBADTaoxWfMqNRqHmX0",
    }
    payload["action"]["escalation_owner"] = {
        "name": "Megan Brown",
        "user_id": "adexBwouW9iBHpmiXrnN",
    }
    payload["controls"]["owner_availability"] = "available"
    result = plan_workflow_extension(payload, now=NOW)
    assert "policy_owner_mismatch" not in result["audit"]["result_reasons"]
    assert "oversight_owner_missing" not in result["audit"][
        "result_reasons"
    ]
    assert "primary_owner_unavailable" not in result["audit"][
        "result_reasons"
    ]

    payload["controls"]["owner_availability"] = "unavailable"
    absent = plan_workflow_extension(payload, now=NOW)
    assert absent["outbox"]["state"] == "preview"
    assert "primary_owner_unavailable" in absent["audit"][
        "result_reasons"
    ]


def test_build6_policy_requires_matching_authorised_cutover_record():
    payload = decision("pt_booking_continuity")
    payload["acceptance"]["cutover"] = {
        "consumer": "pt_booking_continuity",
        "authorised": True,
        "promotion_authorised": True,
        "status_record_id": "cutover-1",
        "status_fingerprint": "cutover-fingerprint-1",
        "distinct_parity_cycles": 2,
        "fresh_exact_parity": True,
        "contract_schema_version": 1,
    }
    result = plan_workflow_extension(payload, now=NOW)
    assert result["outbox"]["state"] == "preview"
    assert "consumer_cutover_not_authorised" not in result["audit"][
        "result_reasons"
    ]
    assert "consumer_cutover_parity_not_met" not in result["audit"][
        "result_reasons"
    ]
    assert "workflow_policy_not_accepted" in result["audit"][
        "result_reasons"
    ]


def test_exact_conversation_controlled_test_can_cross_policy_gate_only():
    payload = decision("conversation_support_routing")
    payload["subject"].update(
        {
            "test_contact": True,
            "email": "workflow-test@example.invalid",
        }
    )
    payload["action"]["owner"] = {
        "role": "Admin Eve",
        "user_id": "EtONSa9U2pTpyOpX1hX8",
    }
    payload["controls"].update(
        {
            "controlled_test": True,
            "owner_availability": "available",
        }
    )
    payload["acceptance"]["test_authority"] = {
        "approval_ref": "build7-conversation-controlled-test-2026-08-03",
        "approved_by": "Peter Brown",
        "reversible": True,
    }
    payload["acceptance"]["cutover"] = {
        "consumer": "conversation_triage",
        "authorised": True,
        "promotion_authorised": True,
        "status_record_id": "conversation-cutover-1",
        "status_fingerprint": "conversation-cutover-fingerprint-1",
        "distinct_parity_cycles": 2,
        "fresh_exact_parity": True,
        "contract_schema_version": 1,
    }
    result = plan_workflow_extension(payload, now=NOW)
    assert result["outbox"]["state"] == "queued"
    assert result["audit"]["controlled_test_authorised"] is True

    payload["subject"]["email"] = "real-client@example.com"
    unsafe = plan_workflow_extension(payload, now=NOW)
    assert unsafe["outbox"]["state"] == "preview"
    assert "workflow_policy_not_accepted" in unsafe["audit"][
        "result_reasons"
    ]


def test_build6_cutover_requires_exact_consumer_and_evidence_reference():
    payload = decision("revenue_exception_review")
    payload["acceptance"]["cutover"] = {
        "consumer": "pt_booking_continuity",
        "authorised": True,
        "promotion_authorised": True,
        "status_record_id": "cutover-1",
        "status_fingerprint": "",
        "distinct_parity_cycles": 1,
        "fresh_exact_parity": True,
        "contract_schema_version": 2,
    }
    result = plan_workflow_extension(payload, now=NOW)
    assert result["outbox"]["state"] == "preview"
    assert "consumer_cutover_not_authorised" in result["audit"][
        "result_reasons"
    ]


def test_revenue_requires_fresh_exact_current_person_schema_v2_parity():
    payload = decision("revenue_exception_review")
    payload["acceptance"]["cutover"] = {
        "consumer": "revenue_control",
        "authorised": True,
        "promotion_authorised": True,
        "status_record_id": "cutover-revenue-1",
        "status_fingerprint": "cutover-revenue-fingerprint-1",
        "distinct_parity_cycles": 1,
        "fresh_exact_parity": True,
        "contract_schema_version": 1,
    }
    wrong_schema = plan_workflow_extension(payload, now=NOW)
    assert "consumer_cutover_schema_mismatch" in wrong_schema["audit"][
        "result_reasons"
    ]

    payload["acceptance"]["cutover"]["contract_schema_version"] = 2
    payload["acceptance"]["cutover"]["fresh_exact_parity"] = False
    stale_parity = plan_workflow_extension(payload, now=NOW)
    assert "consumer_cutover_parity_not_met" in stale_parity["audit"][
        "result_reasons"
    ]


def test_revenue_generic_authority_cannot_replace_promotion_authority():
    payload = decision("revenue_exception_review")
    payload["acceptance"]["cutover"] = {
        "consumer": "revenue_control",
        "authorised": True,
        "promotion_authorised": False,
        "status_record_id": "cutover-revenue-2",
        "status_fingerprint": "cutover-revenue-fingerprint-2",
        "distinct_parity_cycles": 1,
        "fresh_exact_parity": True,
        "contract_schema_version": 2,
    }
    result = plan_workflow_extension(payload, now=NOW)
    assert result["outbox"]["state"] == "preview"
    assert "consumer_cutover_not_authorised" in result["audit"][
        "result_reasons"
    ]


def test_client_or_source_side_effect_is_rejected():
    result = plan_workflow_extension(
        decision(action_type="client_message"), now=NOW
    )
    assert result["outbox"]["state"] == "rejected"
    assert "client_or_source_side_effect_forbidden" in result["audit"][
        "result_reasons"
    ]


def test_forbidden_side_effect_remains_rejected_when_owner_is_missing():
    result = plan_workflow_extension(
        decision(action_type="client_message", owner_user_id=""), now=NOW
    )
    assert result["outbox"]["state"] == "rejected"


def test_missing_exact_owner_cannot_queue():
    result = plan_workflow_extension(
        decision(owner_user_id=""), now=NOW
    )
    assert result["outbox"]["state"] == "preview"
    assert "exact_owner_missing" in result["audit"]["result_reasons"]


def test_suppression_overrides_accepted_task():
    result = plan_workflow_extension(
        decision(suppression_reasons=["approved_hold"]), now=NOW
    )
    assert result["outbox"]["state"] == "suppressed"
    assert "approved_hold" in result["audit"]["result_reasons"]


def test_unaccepted_metric_with_suppression_remains_preview_only():
    result = plan_workflow_extension(
        decision(
            acceptance_state="shadow",
            suppression_reasons=["approved_hold"],
        ),
        now=NOW,
    )
    assert result["outbox"]["state"] == "preview"


def test_string_true_cannot_bypass_source_or_decision_authority():
    payload = decision()
    payload["source"]["fresh"] = "true"
    payload["acceptance"]["decision_authorised"] = "true"
    result = plan_workflow_extension(payload, now=NOW)
    assert result["outbox"]["state"] == "preview"
    assert "source_stale" in result["audit"]["result_reasons"]
    assert "workflow_decision_not_authorised" in result["audit"][
        "result_reasons"
    ]


def test_closed_exception_is_suppressed():
    payload = decision()
    payload["exception"]["status"] = "resolved"
    result = plan_workflow_extension(payload, now=NOW)
    assert result["outbox"]["state"] == "suppressed"
    assert "exception_not_open" in result["audit"]["result_reasons"]


def test_duplicate_and_cooldown_are_deterministic():
    first = plan_workflow_extension(decision(), now=NOW)
    duplicate = plan_workflow_extension(
        decision(), prior_records=[first["outbox"]], now=NOW
    )
    assert duplicate["outbox"]["state"] == "duplicate"

    changed = decision()
    changed["decision_id"] = "decision-456"
    changed["controls"]["dedupe_scope"] = "appointment-123:coach"
    cooldown = plan_workflow_extension(
        changed, prior_records=[first["outbox"]], now=NOW
    )
    assert cooldown["outbox"]["state"] == "cooldown"


def test_contract_requires_authoritative_evidence():
    payload = decision()
    payload["evidence"] = []
    with pytest.raises(DecisionContractError):
        plan_workflow_extension(payload, now=NOW)


def test_registry_exposes_all_six_guarded_workflows():
    registry = workflow_policy_registry()
    assert len(registry["policies"]) == 6
    assert registry["side_effect_boundary"] == ["internal_task"]


def test_store_persists_one_outbox_record_and_audit_event(tmp_path):
    store = HubStore(f"sqlite:///{tmp_path / 'hub.db'}")
    plan = plan_workflow_extension(decision(), now=NOW)
    first = store.record_workflow_extension(plan)
    second = store.record_workflow_extension(plan)
    records = store.workflow_extension_records(
        workflow_key="onboarding_outcome_followup",
        person_id="person-123",
    )
    assert first["status"] == "recorded"
    assert second["status"] == "duplicate"
    assert len(records) == 1
    assert records[0]["state"] == "queued"
    assert records[0]["audit"]["source_snapshot_id"] == "snapshot-123"


def test_service_preview_persistence_and_sqlite_cooldown(tmp_path):
    service = object.__new__(HubService)
    service.store = HubStore(f"sqlite:///{tmp_path / 'hub.db'}")
    preview = service.accept_workflow_extension_decision(
        decision(), persist=False
    )
    assert preview["mode"] == "preview"
    assert service.store.workflow_extension_records() == []

    accepted = service.accept_workflow_extension_decision(
        decision(), persist=True
    )
    assert accepted["persistence"]["status"] == "recorded"

    changed = decision()
    changed["decision_id"] = "decision-456"
    cooldown = service.accept_workflow_extension_decision(
        changed, persist=False
    )
    assert cooldown["plan"]["outbox"]["state"] == "cooldown"


def test_dispatch_evidence_is_idempotent_and_cannot_mutate_preview(tmp_path):
    store = HubStore(f"sqlite:///{tmp_path / 'hub.db'}")
    queued = plan_workflow_extension(decision(), now=NOW)
    store.record_workflow_extension(queued)
    first = store.mark_workflow_extension_dispatched(
        queued["outbox"]["idempotency_key"],
        external_action_id="ghl-task-1",
        evidence={"response_fingerprint": "response-1"},
        occurred_at=NOW,
    )
    duplicate = store.mark_workflow_extension_dispatched(
        queued["outbox"]["idempotency_key"],
        external_action_id="ghl-task-1",
        evidence={"response_fingerprint": "response-1"},
        occurred_at=NOW,
    )
    assert first["status"] == "dispatched"
    assert duplicate["status"] == "duplicate"
    assert store.workflow_extension_records()[0]["state"] == "dispatched"

    preview = plan_workflow_extension(
        decision("retention_intervention_review"), now=NOW
    )
    store.record_workflow_extension(preview)
    with pytest.raises(RuntimeError):
        store.mark_workflow_extension_dispatched(
            preview["outbox"]["idempotency_key"],
            external_action_id="ghl-task-2",
            evidence={},
            occurred_at=NOW,
        )
