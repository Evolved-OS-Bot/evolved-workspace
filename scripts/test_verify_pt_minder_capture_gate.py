import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from verify_pt_minder_capture_gate import verify_capture


def payload(*, observed_at="2026-08-03T09:00:00+10:00", rows=27):
    return {
        "observed_at": observed_at,
        "transaction_detail_complete": True,
        "rows": [
            {
                "source_account_id": f"account-{index}",
                "email": f"member{index}@example.com",
                "state": "active",
                "weekly_amount": "99",
                "transactions": [
                    {
                        "source_transaction_id": f"{index}-{transaction}",
                        "entry_type": "debit",
                        "occurred_on": "2026-08-03",
                        "description": "Silver Package Weekly",
                        "amount": "99",
                        "status": "completed",
                    }
                    for transaction in range(20)
                ],
            }
            for index in range(rows)
        ],
    }


def test_second_capture_preflight_accepts_new_complete_snapshot():
    result = verify_capture(
        payload(),
        prior_observed_at="2026-07-27T08:21:05+00:00",
    )

    assert result["status"] == "ready_for_upload"
    assert result["account_count"] == 27
    assert result["transaction_count"] == 540


def test_second_capture_preflight_rejects_reused_observation():
    result = verify_capture(
        payload(observed_at="2026-07-27T08:21:05+00:00"),
        prior_observed_at="2026-07-27T08:21:05+00:00",
    )

    assert result["status"] == "blocked"
    assert any("not newer" in row for row in result["failures"])


def test_second_capture_preflight_rejects_partial_history():
    incomplete = payload(rows=1)
    result = verify_capture(
        incomplete,
        prior_observed_at="2026-07-27T08:21:05+00:00",
    )

    assert result["status"] == "blocked"
    assert len(result["failures"]) == 2
