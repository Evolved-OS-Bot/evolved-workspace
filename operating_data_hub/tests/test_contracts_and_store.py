from datetime import UTC, datetime

import pytest

from operating_data_hub.contracts import validate_pt_minder
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

