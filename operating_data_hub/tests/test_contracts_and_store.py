from datetime import UTC, datetime

import pytest

from operating_data_hub.contracts import (
    classify_pt_minder_transaction,
    validate_pt_minder,
)
from operating_data_hub.store import HubStore


def pt_minder_payload():
    return {
        "observed_at": datetime.now(UTC).isoformat(),
        "rows": [
            {
                "source_account_id": "ptm-1",
                "email": "member@example.com",
                "agreement_id": "agreement-1",
                "product": "PT weekly",
                "state": "active",
                "amount": "120",
                "last_successful_payment": "2026-07-24",
                "next_scheduled_payment": "2026-07-31",
            }
        ],
    }


def test_pt_minder_contract_accepts_minimum_complete_snapshot():
    payload = validate_pt_minder(pt_minder_payload())
    assert payload["complete"] is True
    assert payload["transaction_detail_complete"] is False
    assert payload["rows"][0]["amount"] == "120.00"


def test_pt_minder_contract_rejects_empty_or_duplicate_snapshot():
    with pytest.raises(ValueError, match="cannot be empty"):
        validate_pt_minder(
            {
                "observed_at": datetime.now(UTC).isoformat(),
                "rows": [],
            }
        )
    raw = pt_minder_payload()
    raw["rows"].append(dict(raw["rows"][0]))
    with pytest.raises(ValueError, match="duplicate"):
        validate_pt_minder(raw)


def test_store_is_idempotent_and_preserves_latest_complete(tmp_path):
    store = HubStore(f"sqlite:///{tmp_path / 'hub.db'}")
    payload = validate_pt_minder(pt_minder_payload())
    first = store.accept_snapshot("pt_minder", payload)
    second = store.accept_snapshot("pt_minder", payload)

    assert first["status"] == "accepted"
    assert second["status"] == "duplicate"
    assert store.latest_snapshot("pt_minder")["record_count"] == 1


def test_pt_minder_contract_classifies_recurring_membership_and_ad_hoc_pt():
    raw = pt_minder_payload()
    raw["transaction_detail_complete"] = True
    raw["rows"][0]["transactions"] = [
        {
            "source_transaction_id": "txn-gypsy",
            "occurred_on": "2026-07-23",
            "description": "Gypsy Program - from 23/07/2026 to 29/07/2026",
            "amount": "69",
            "status": "completed",
            "next_scheduled_payment": "2026-07-30",
        },
        {
            "source_transaction_id": "txn-pt",
            "occurred_on": "2026-07-22",
            "description": "1xPT 24/7",
            "amount": "60",
            "status": "completed",
        },
    ]

    payload = validate_pt_minder(raw)

    assert payload["schema_version"] == 2
    membership, pt = payload["rows"][0]["transactions"]
    assert membership["service_type"] == "sgpt"
    assert membership["cadence"] == "recurring"
    assert pt["service_type"] == "personal_training"
    assert pt["cadence"] == "ad_hoc"


def test_pt_minder_transaction_override_requires_explanation():
    raw = pt_minder_payload()
    raw["transaction_detail_complete"] = True
    raw["rows"][0]["transactions"] = [
        {
            "source_transaction_id": "txn-1",
            "occurred_on": "2026-07-23",
            "description": "Manual adjustment",
            "amount": "69",
            "status": "completed",
            "service_type": "sgpt",
            "cadence": "recurring",
        }
    ]

    with pytest.raises(ValueError, match="classification override"):
        validate_pt_minder(raw)


def test_pt_minder_classifier_keeps_service_and_cadence_separate():
    assert classify_pt_minder_transaction("PT weekly") == {
        "service_type": "personal_training",
        "cadence": "recurring",
    }
    assert classify_pt_minder_transaction("2x30 min PT with Megan") == {
        "service_type": "personal_training",
        "cadence": "ad_hoc",
    }
