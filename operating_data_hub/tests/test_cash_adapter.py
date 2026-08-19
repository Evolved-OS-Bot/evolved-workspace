from datetime import UTC, datetime

from operating_data_hub.cash_adapter import (
    build_pt_minder_cash_batch,
    build_stripe_cash_batch,
    gst_from_taxable_gross,
)


def test_gst_from_fully_taxable_inclusive_amount():
    assert gst_from_taxable_gross(11000) == 1000
    assert gst_from_taxable_gross(9900) == 900
    assert gst_from_taxable_gross(6900) == 627


def test_stripe_cash_batch_uses_invoice_tax_and_refund_date():
    observed_at = datetime(2026, 8, 1, 1, 0, tzinfo=UTC)
    payload = build_stripe_cash_batch(
        observed_at=observed_at,
        payment_intents=[
            {
                "id": "pi_paid",
                "status": "succeeded",
                "currency": "aud",
                "amount_received": 11000,
                "invoice": {
                    "id": "in_paid",
                    "total": 11000,
                    "total_excluding_tax": 10000,
                },
                "latest_charge": {
                    "id": "ch_paid",
                    "created": 1785542400,
                    "refunds": {
                        "has_more": False,
                        "data": [
                            {
                                "id": "re_partial",
                                "created": 1785546000,
                                "amount": 2200,
                                "status": "succeeded",
                            }
                        ],
                    },
                },
            },
            {
                "id": "pi_pending",
                "status": "processing",
                "currency": "aud",
            },
        ],
    )

    assert payload["complete"] is True
    assert payload["adapter_summary"]["source_records"] == 2
    assert payload["adapter_summary"]["accepted_events"] == 2
    settled, refund = payload["events"]
    assert settled["source_event_id"] == "pi_paid:settled"
    assert settled["gross_amount_cents"] == 11000
    assert settled["gst_amount_cents"] == 1000
    assert refund["source_event_id"] == "re_partial"
    assert refund["event_type"] == "refund"
    assert refund["gross_amount_cents"] == 2200
    assert refund["gst_amount_cents"] == 200
    assert refund["occurred_at"] != settled["occurred_at"]


def test_stripe_cash_batch_uses_approved_tax_rule_for_direct_payment():
    payload = build_stripe_cash_batch(
        observed_at=datetime(2026, 8, 1, 1, 0, tzinfo=UTC),
        payment_intents=[
            {
                "id": "pi_missing_tax",
                "status": "succeeded",
                "currency": "aud",
                "amount_received": 9900,
                "invoice": None,
                "latest_charge": {
                    "id": "ch_missing_tax",
                    "created": 1785542400,
                    "refunds": {"has_more": False, "data": []},
                },
            }
        ],
    )

    assert payload["complete"] is True
    assert payload["adapter_summary"]["error_count"] == 0
    assert payload["events"][0]["gst_amount_cents"] == 900
    assert payload["events"][0]["evidence"]["gst_basis"] == (
        "approved_fully_taxable_gst_inclusive_supply"
    )


def test_stripe_cash_batch_fails_closed_when_invoice_tax_is_missing():
    payload = build_stripe_cash_batch(
        observed_at=datetime(2026, 8, 1, 1, 0, tzinfo=UTC),
        payment_intents=[
            {
                "id": "pi_missing_tax",
                "status": "succeeded",
                "currency": "aud",
                "amount_received": 9900,
                "invoice": {
                    "id": "in_missing_tax",
                    "total": 9900,
                    "total_excluding_tax": None,
                },
                "latest_charge": {
                    "id": "ch_missing_tax",
                    "created": 1785542400,
                    "refunds": {"has_more": False, "data": []},
                },
            }
        ],
    )

    assert payload["complete"] is False
    assert payload["events"] == []
    assert payload["adapter_summary"]["error_count"] == 1


def test_stripe_cash_batch_allocates_invoice_tax_to_partial_settlement():
    payload = build_stripe_cash_batch(
        observed_at=datetime(2026, 8, 1, 1, 0, tzinfo=UTC),
        payment_intents=[
            {
                "id": "pi_partial",
                "status": "succeeded",
                "currency": "aud",
                "amount_received": 5500,
                "invoice": {
                    "id": "in_partial",
                    "total": 11000,
                    "total_excluding_tax": 10000,
                },
                "latest_charge": {
                    "id": "ch_partial",
                    "created": 1785542400,
                    "refunds": {"has_more": False, "data": []},
                },
            }
        ],
    )

    assert payload["complete"] is True
    assert payload["events"][0]["gst_amount_cents"] == 500
    assert payload["events"][0]["evidence"]["gst_basis"] == (
        "proportional_from_stripe_invoice_tax"
    )


def test_pt_minder_cash_batch_uses_only_completed_and_refunded_debits():
    snapshot = {
        "snapshot_id": "ptm-snapshot-1",
        "observed_at": "2026-08-01T01:00:00+00:00",
        "payload": {
            "transaction_detail_complete": True,
            "rows": [
                {
                    "source_account_id": "account-1",
                    "transactions": [
                        {
                            "source_transaction_id": "debit-complete",
                            "occurred_on": "2026-07-31",
                            "amount": "99.00",
                            "status": "completed",
                        },
                        {
                            "source_transaction_id": "debit-pending",
                            "occurred_on": "2026-08-01",
                            "amount": "99.00",
                            "status": "pending",
                        },
                        {
                            "source_transaction_id": "debit-failed",
                            "occurred_on": "2026-07-24",
                            "amount": "99.00",
                            "status": "failed",
                        },
                        {
                            "source_transaction_id": "debit-refund",
                            "occurred_on": "2026-07-30",
                            "amount": "69.00",
                            "status": "refunded",
                        },
                    ],
                }
            ],
        },
    }

    payload = build_pt_minder_cash_batch(
        snapshot,
        as_of=datetime(2026, 8, 1, 1, 0, tzinfo=UTC),
    )

    assert payload["complete"] is True
    assert [row["source_event_id"] for row in payload["events"]] == [
        "debit-complete",
        "debit-refund",
    ]
    assert payload["events"][0]["gst_amount_cents"] == 900
    assert payload["events"][1]["gst_amount_cents"] == 627
    assert payload["events"][1]["event_type"] == "refund"


def test_pt_minder_cash_batch_blocks_incomplete_transaction_capture():
    payload = build_pt_minder_cash_batch(
        {
            "snapshot_id": "ptm-snapshot-2",
            "observed_at": "2026-08-01T01:00:00+00:00",
            "payload": {
                "transaction_detail_complete": False,
                "rows": [{"source_account_id": "account-1"}],
            },
        }
    )

    assert payload["complete"] is False
    assert payload["adapter_summary"]["error_count"] == 1
