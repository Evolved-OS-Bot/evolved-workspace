from __future__ import annotations

from datetime import UTC, datetime

import pytest

from reporting_control.current_people_client import (
    HubContractError,
    exact_parity,
    fetch_cutover_authority,
    publish_parallel_result,
    validate_current_people_contract,
)


def _payload():
    return {
        "schema_version": 1,
        "contract_version": "current-person-v1",
        "mode": "shadow",
        "generated_at": datetime.now(UTC).isoformat(),
        "period": {
            "period_id": "week",
            "timezone": "Australia/Brisbane",
            "start": "2026-07-20",
            "end": "2026-07-26",
        },
        "source_freshness": {"membership_reconciliation": {"status": "fresh"}},
        "complete": True,
        "blocked_reasons": [],
        "rows": [
            {
                "person_id": "person-1",
                "source_identities": {
                    "ghl": [{"source_id": "contact-1"}],
                    "trainerize": [{"source_id": "101"}],
                },
                "lifecycle": {"status": "active"},
                "service_relationships": [],
                "entitlements": [],
                "payment_accounts": [],
            }
        ],
    }


def test_validates_protected_current_people_contract():
    contract = validate_current_people_contract(
        _payload(),
        max_age_hours=1,
        expected_contract_version="current-person-v1",
    )
    assert contract.by_source_identity("ghl")["contact-1"]["person_id"] == (
        "person-1"
    )


def test_incomplete_contract_fails_closed():
    payload = _payload()
    payload["complete"] = False
    payload["blocked_reasons"] = ["membership source stale"]
    with pytest.raises(HubContractError, match="blocked or incomplete"):
        validate_current_people_contract(payload, max_age_hours=1)


def test_unapproved_identified_source_is_rejected():
    payload = _payload()
    payload["rows"][0]["source_identities"]["stripe"] = ["cus_1"]
    with pytest.raises(HubContractError, match="unapproved identity source"):
        validate_current_people_contract(payload, max_age_hours=1)


def test_exact_parity_requires_identity_and_projection_equality():
    legacy = [
        {"id": "101", "state": "active"},
        {"id": "102", "state": "hold"},
    ]
    hub = [
        {"id": "101", "state": "active"},
        {"id": "102", "state": "hold"},
    ]
    result = exact_parity(
        legacy,
        hub,
        key=lambda row: row["id"],
        projection=lambda row: {"state": row["state"]},
    )
    assert result.equivalent is True
    assert result.unexplained_event_count == 0
    assert (
        result.legacy_identity_fingerprint
        == result.hub_identity_fingerprint
    )
    assert (
        result.legacy_classification_fingerprint
        == result.hub_classification_fingerprint
    )


def test_exact_parity_reports_changed_and_missing_people():
    legacy = [
        {"id": "101", "state": "active"},
        {"id": "102", "state": "hold"},
    ]
    hub = [
        {"id": "101", "state": "cancelled"},
        {"id": "103", "state": "active"},
    ]
    result = exact_parity(
        legacy,
        hub,
        key=lambda row: row["id"],
        projection=lambda row: {"state": row["state"]},
    )
    assert result.equivalent is False
    assert result.changed == ("101",)
    assert result.missing_from_hub == ("102",)
    assert result.missing_from_legacy == ("103",)


class _Response:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


class _Session:
    def __init__(self, payload):
        self.payload = payload

    def get(self, *_args, **_kwargs):
        return _Response(self.payload)

    def post(self, *_args, **kwargs):
        self.posted = kwargs["json"]
        return _Response({"status": "passed"})


def test_cutover_authority_requires_exact_registered_approved_metric(
    monkeypatch,
):
    monkeypatch.setenv("HUB_REPORTING_BASE_URL", "https://hub.example")
    monkeypatch.setenv("HUB_WEBHOOK_SECRET", "secret")
    authority = fetch_cutover_authority(
        metric_id="consumer_test",
        definition_version="test-v1",
        session=_Session(
            {
                "metrics": [
                    {
                        "metric_id": "consumer_test",
                        "definition_version": "test-v1",
                        "cutover": {
                            "effective_state": "v2_accepted",
                            "promotion_authorised": True,
                            "blocked_reasons": [],
                        },
                    }
                ]
            }
        ),
    )
    assert authority.promotion_authorised is True


def test_cutover_rollback_disables_hub_authority(monkeypatch):
    monkeypatch.setenv("HUB_REPORTING_BASE_URL", "https://hub.example")
    monkeypatch.setenv("HUB_WEBHOOK_SECRET", "secret")
    authority = fetch_cutover_authority(
        metric_id="consumer_test",
        definition_version="test-v1",
        session=_Session(
            {
                "metrics": [
                    {
                        "metric_id": "consumer_test",
                        "definition_version": "test-v1",
                        "cutover": {
                            "effective_state": "rolled_back",
                            "promotion_authorised": False,
                            "latest_decision": {"action": "rollback"},
                            "blocked_reasons": [],
                        },
                    }
                ]
            }
        ),
    )
    assert authority.promotion_authorised is False
    assert authority.rollback_active is True


def test_parallel_result_uses_acceptance_controller_evidence_names(
    monkeypatch,
):
    monkeypatch.setenv("HUB_REPORTING_BASE_URL", "https://hub.example")
    monkeypatch.setenv("HUB_WEBHOOK_SECRET", "secret")
    parity = exact_parity(
        [{"id": "101", "state": "active"}],
        [{"id": "101", "state": "active"}],
        key=lambda row: row["id"],
        projection=lambda row: {"state": row["state"]},
    )
    session = _Session({})
    publish_parallel_result(
        metric_id="consumer_test",
        definition_version="test-v1",
        period_start="2026-07-20",
        period_end="2026-07-26",
        comparison_cycle="cycle-1",
        source_run_ids={"hub_current_people": "snapshot-1"},
        parity=parity,
        session=session,
    )
    evidence = session.posted["evidence"]
    assert evidence["period_id"] == "contract"
    assert evidence["comparison_cycle_id"] == "cycle-1"
    assert evidence["source_run_id"] == "snapshot-1"
    assert evidence["legacy_only_count"] == 0
    assert evidence["hub_only_count"] == 0
    assert evidence["hub_source_complete"] is True
    assert evidence["hub_source_fresh"] is True
