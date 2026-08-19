from __future__ import annotations

import json
import sqlite3

from reporting_control.hub_commercial_client import (
    build_stripe_commercial_evidence,
)


def build_database(tmp_path, *, with_invoice: bool):
    database = tmp_path / "reconciliation.sqlite"
    connection = sqlite3.connect(database)
    connection.executescript(
        """
        CREATE TABLE runs (
            run_id TEXT PRIMARY KEY,
            started_at TEXT,
            finished_at TEXT,
            status TEXT
        );
        CREATE TABLE identity_register (
            run_id TEXT,
            identity_key TEXT,
            email TEXT,
            stripe_customer_ids_json TEXT,
            membership_type TEXT,
            membership_stage TEXT
        );
        CREATE TABLE stripe_subscriptions (
            run_id TEXT,
            subscription_id TEXT,
            customer_id TEXT,
            status TEXT,
            current_period_start TEXT,
            current_period_end TEXT,
            cancel_at TEXT,
            cancel_at_period_end INTEGER,
            canceled_at TEXT,
            pause_collection_json TEXT,
            product_ids_json TEXT,
            price_ids_json TEXT,
            raw_json TEXT
        );
        CREATE TABLE stripe_invoices (
            run_id TEXT,
            invoice_id TEXT,
            customer_id TEXT,
            subscription_id TEXT,
            status TEXT,
            paid INTEGER,
            amount_due INTEGER,
            amount_paid INTEGER,
            period_end TEXT,
            created_at TEXT,
            raw_json TEXT
        );
        INSERT INTO runs VALUES (
            'run-1',
            '2026-07-28T00:00:00+00:00',
            '2026-07-28T00:01:00+00:00',
            'complete'
        );
        INSERT INTO identity_register VALUES (
            'run-1',
            'member@example.com',
            'member@example.com',
            '["cus-1"]',
            'Fast Track Package',
            'PT 2 p.wk'
        );
        """
    )
    raw_subscription = {
        "items": {
            "data": [
                {
                    "quantity": 1,
                    "price": {
                        "unit_amount": 19900,
                        "recurring": {
                            "interval": "week",
                            "interval_count": 1,
                        },
                    },
                }
            ]
        }
    }
    connection.execute(
        """
        INSERT INTO stripe_subscriptions VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
        """,
        (
            "run-1",
            "sub-1",
            "cus-1",
            "active",
            "2026-07-27T00:00:00+00:00",
            "2026-08-03T00:00:00+00:00",
            None,
            0,
            None,
            "null",
            "[]",
            "[]",
            json.dumps(raw_subscription),
        ),
    )
    if with_invoice:
        connection.execute(
            """
            INSERT INTO stripe_invoices VALUES (
                'run-1', 'in-1', 'cus-1', 'sub-1', 'paid', 1,
                19900, 19900, '2026-07-27T00:00:00+00:00',
                '2026-07-27T00:01:00+00:00', '{}'
            )
            """
        )
    connection.commit()
    connection.close()
    return database


def test_paid_invoice_confirms_current_subscription_entitlements(tmp_path):
    payload = build_stripe_commercial_evidence(
        build_database(tmp_path, with_invoice=True)
    )

    row = payload["rows"][0]
    assert row["payment_accounts"][0]["weekly_amount"] == "199.00"
    assert {
        entitlement["service_type"]
        for entitlement in row["entitlements"]
    } == {"fast_track", "personal_training"}
    assert {
        entitlement["status"] for entitlement in row["entitlements"]
    } == {"confirmed"}
    assert row["payment_events"][0]["status"] == "completed"
    assert row["payment_events"][0]["amount"] == "199.00"


def test_contract_without_paid_invoice_remains_pending(tmp_path):
    payload = build_stripe_commercial_evidence(
        build_database(tmp_path, with_invoice=False)
    )

    assert {
        entitlement["status"]
        for entitlement in payload["rows"][0]["entitlements"]
    } == {"pending"}
    assert payload["rows"][0]["payment_events"] == []


def test_paid_cancelled_invoice_confirms_only_exact_line_coverage(
    tmp_path,
):
    database = build_database(tmp_path, with_invoice=True)
    connection = sqlite3.connect(database)
    line = {
        "amount": 39900,
        "proration": False,
        "period": {
            "start": 1784505600,
            "end": 1787184000,
        },
    }
    connection.execute(
        """
        UPDATE stripe_subscriptions
        SET status='cancelled',
            current_period_start=NULL,
            current_period_end=NULL
        WHERE subscription_id='sub-1'
        """
    )
    connection.execute(
        """
        UPDATE stripe_invoices
        SET amount_due=39900,
            amount_paid=39900,
            raw_json=?
        WHERE invoice_id='in-1'
        """,
        (json.dumps({"lines": {"data": [line]}}),),
    )
    connection.commit()
    connection.close()

    payload = build_stripe_commercial_evidence(database)
    row = payload["rows"][0]
    event = row["payment_events"][0]
    coverage = [
        item
        for item in row["entitlements"]
        if item["basis"]
        == "paid_stripe_invoice_line_coverage_period"
    ]

    assert payload["schema_version"] == 2
    assert event["coverage_start"] == "2026-07-20"
    assert event["coverage_end"] == "2026-08-20"
    assert coverage == [
        {
            "source_record_id": "in-1:coverage:sgpt",
            "service_type": "sgpt",
            "status": "confirmed",
            "effective_from": "2026-07-20",
            "effective_to": "2026-08-20",
            "basis": "paid_stripe_invoice_line_coverage_period",
        }
    ]


def test_one_time_invoice_does_not_create_ongoing_entitlement(
    tmp_path,
):
    database = build_database(tmp_path, with_invoice=True)
    connection = sqlite3.connect(database)
    line = {
        "amount": 39900,
        "proration": False,
        "period": {
            "start": 1784505600,
            "end": 1784505600,
        },
    }
    connection.execute(
        "UPDATE stripe_subscriptions SET status='cancelled'"
    )
    connection.execute(
        "UPDATE stripe_invoices SET raw_json=?",
        (json.dumps({"lines": {"data": [line]}}),),
    )
    connection.commit()
    connection.close()

    payload = build_stripe_commercial_evidence(database)

    assert not [
        item
        for item in payload["rows"][0]["entitlements"]
        if item["basis"]
        == "paid_stripe_invoice_line_coverage_period"
    ]
