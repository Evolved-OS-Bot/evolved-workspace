from __future__ import annotations

import json
import sqlite3

from reporting_control.hub_membership_client import (
    _lifecycle_status,
    _services,
    build_membership_snapshot,
)


def test_build_membership_snapshot_uses_completed_identity_register(tmp_path):
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
            ghl_contact_ids_json TEXT,
            stripe_customer_ids_json TEXT,
            trainerize_active_ids_json TEXT,
            trainerize_deactivated_ids_json TEXT,
            ghl_active_signal INTEGER,
            stripe_entitled_signal INTEGER,
            trainerize_active_signal INTEGER,
            membership_type TEXT,
            membership_stage TEXT,
            cancellation_status TEXT,
            cancellation_type TEXT,
            notice_end_date TEXT,
            final_access_date TEXT,
            evidence_json TEXT
        );
        CREATE TABLE ghl_contacts (
            run_id TEXT,
            contact_id TEXT,
            first_name TEXT,
            last_name TEXT,
            date_updated TEXT
        );
        """
    )
    connection.execute(
        "INSERT INTO runs VALUES (?, ?, ?, ?)",
        (
            "run-1",
            "2026-07-27T09:55:00+00:00",
            "2026-07-27T10:00:00+00:00",
            "complete",
        ),
    )
    connection.execute(
        "INSERT INTO ghl_contacts VALUES (?, ?, ?, ?, ?)",
        (
            "run-1",
            "ghl-1",
            "Miriam",
            "Wellauer",
            "2026-07-27T09:59:00+00:00",
        ),
    )
    connection.execute(
        """
        INSERT INTO identity_register VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
        """,
        (
            "run-1",
            "member@example.com",
            "member@example.com",
            json.dumps(["ghl-1"]),
            json.dumps(["cus-1"]),
            json.dumps([123]),
            json.dumps([]),
            1,
            1,
            1,
            "Fast Track Package",
            "Fast Track",
            "Notice Active",
            "PT",
            "2026-08-01",
            "2026-08-03",
            json.dumps({"pt_block_trainer": "Piper Mae"}),
        ),
    )
    connection.commit()
    connection.close()

    snapshot = build_membership_snapshot(database)

    assert snapshot["source_run_id"] == "run-1"
    assert snapshot["rows"][0]["service_type"] == "fast_track"
    assert snapshot["rows"][0]["source_ids"] == {
        "ghl": ["ghl-1"],
        "stripe": ["cus-1"],
        "trainerize": ["123"],
    }
    assert snapshot["rows"][0]["pt_block_trainer"] == "Piper Mae"
    assert snapshot["rows"][0]["first_name"] == "Miriam"
    assert snapshot["rows"][0]["last_name"] == "Wellauer"
    assert snapshot["rows"][0]["cancellation_type"] == "PT"
    assert snapshot["rows"][0]["notice_end_date"] == "2026-08-01"


def test_services_preserve_fast_track_and_pt_add_on():
    class Row(dict):
        __getattr__ = dict.__getitem__

    services = _services(
        Row(
            membership_type="Fast Track Package",
            membership_stage="PT 2 p.wk",
        )
    )

    assert services == [
        {
            "service_type": "fast_track",
            "service_name": "Fast Track Package",
        },
        {
            "service_type": "personal_training",
            "service_name": "PT 2 p.wk",
        },
    ]


def test_build_membership_snapshot_normalises_timestamp_date(tmp_path):
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
            ghl_contact_ids_json TEXT,
            stripe_customer_ids_json TEXT,
            trainerize_active_ids_json TEXT,
            trainerize_deactivated_ids_json TEXT,
            ghl_active_signal INTEGER,
            stripe_entitled_signal INTEGER,
            trainerize_active_signal INTEGER,
            membership_type TEXT,
            membership_stage TEXT,
            cancellation_status TEXT,
            cancellation_type TEXT,
            notice_end_date TEXT,
            final_access_date TEXT
        );
        INSERT INTO runs VALUES (
            'run-1',
            '2026-07-27T09:55:00+00:00',
            '2026-07-27T10:00:00+00:00',
            'complete'
        );
        INSERT INTO identity_register VALUES (
            'run-1',
            'member@example.com',
            'member@example.com',
            '[]',
            '[]',
            '[]',
            '[]',
            1,
            1,
            1,
            'Fast Track',
            NULL,
            NULL,
            NULL,
            NULL,
            '2026-07-07T00:00:00.000Z'
        );
        """
    )
    connection.close()

    snapshot = build_membership_snapshot(database)

    assert snapshot["rows"][0]["final_access_date"] == "2026-07-07"


def test_lifecycle_does_not_promote_trainerize_or_stripe_to_active():
    class Row(dict):
        __getattr__ = dict.__getitem__

    row = Row(
        ghl_active_signal=0,
        stripe_entitled_signal=1,
        trainerize_active_signal=1,
        cancellation_status=None,
        final_access_date=None,
    )

    assert _lifecycle_status(row) == "review_required"


def test_literal_none_cancellation_does_not_inflate_lifecycle():
    class Row(dict):
        __getattr__ = dict.__getitem__

    row = Row(
        ghl_active_signal=0,
        stripe_entitled_signal=0,
        trainerize_active_signal=0,
        cancellation_status="None",
        final_access_date=None,
    )

    assert _lifecycle_status(row) == "inactive"
