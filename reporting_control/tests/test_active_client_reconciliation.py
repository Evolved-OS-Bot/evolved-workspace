import sqlite3
from pathlib import Path

from scripts.reconcile_active_client_cohort import (
    decision_for,
    load_current_identity_rows,
)


def test_latest_current_state_is_separate_from_historical_baseline(
    tmp_path: Path,
):
    database = tmp_path / "reconciliation.sqlite"
    connection = sqlite3.connect(database)
    connection.executescript(
        """
        CREATE TABLE runs (
            run_id TEXT PRIMARY KEY,
            started_at TEXT NOT NULL,
            finished_at TEXT,
            status TEXT NOT NULL
        );
        CREATE TABLE identity_register (
            run_id TEXT NOT NULL,
            email TEXT,
            ghl_active_signal INTEGER NOT NULL,
            stripe_entitled_signal INTEGER NOT NULL,
            trainerize_active_signal INTEGER NOT NULL,
            membership_type TEXT,
            membership_stage TEXT,
            cancellation_status TEXT,
            final_access_date TEXT
        );
        INSERT INTO runs VALUES
            ('older', '2026-07-27T00:00:00Z',
             '2026-07-27T00:01:00Z', 'complete'),
            ('latest', '2026-07-28T00:00:00Z',
             '2026-07-28T00:01:00Z', 'complete');
        INSERT INTO identity_register VALUES
            ('older', 'member@example.com', 1, 0, 1, '', '', '', ''),
            ('latest', 'member@example.com', 0, 0, 0, '', '',
             'Cancelled', '2026-03-04');
        """
    )
    connection.commit()
    connection.close()

    run_id, identities = load_current_identity_rows(database, {})

    assert run_id == "latest"
    assert identities["member@example.com"]["ghl_active_signal"] == "False"
    assert identities["member@example.com"]["trainerize_active_signal"] == (
        "False"
    )
    assert identities["member@example.com"]["cancellation_status"] == (
        "Cancelled"
    )


def test_resolved_cancellation_remains_in_history_but_leaves_owner_queue():
    historical = {
        "ghl_active_signal": "True",
        "stripe_entitled_signal": "False",
        "trainerize_active_signal": "True",
        "cancellation_status": "",
    }
    current = {
        "ghl_active_signal": "False",
        "stripe_entitled_signal": "False",
        "trainerize_active_signal": "False",
        "membership_type": "",
        "membership_stage": "",
        "cancellation_status": "Cancelled",
        "final_access_date": "2026-03-04",
    }

    row = decision_for(
        email="member@example.com",
        baseline_identity=historical,
        current_identity=current,
        roster=[],
        audit_roster=[],
        classification="",
        timing_additions=set(),
        known_internal=set(),
    )

    assert row["in_legacy_cohort"] is True
    assert row["active_signal"] is False
    assert row["decision_required"] is False
    assert row["primary_reason"] == "historical_signal_now_retired"


def test_owner_approved_roster_restoration_leaves_owner_queue():
    identity = {
        "ghl_active_signal": "True",
        "stripe_entitled_signal": "True",
        "trainerize_active_signal": "True",
        "membership_type": "Strong, Fit & Flexible",
        "membership_stage": "Strong, Fit & Flexible Membership",
        "cancellation_status": "",
        "final_access_date": "",
    }

    row = decision_for(
        email="member@example.com",
        baseline_identity=identity,
        current_identity=identity,
        roster=[],
        audit_roster=[],
        classification="current_sgpt_client",
        timing_additions=set(),
        known_internal=set(),
    )

    assert row["active_signal"] is True
    assert row["decision_required"] is False
    assert row["disposition"] == "timing_difference"
    assert row["primary_reason"] == (
        "active_roster_row_added_after_governed_snapshot"
    )


def test_owner_approved_complimentary_member_is_a_governed_exclusion():
    identity = {
        "ghl_active_signal": "True",
        "stripe_entitled_signal": "False",
        "trainerize_active_signal": "True",
        "membership_type": "",
        "membership_stage": "",
        "cancellation_status": "",
        "final_access_date": "",
    }

    row = decision_for(
        email="friend@example.com",
        baseline_identity=identity,
        current_identity=identity,
        roster=[],
        audit_roster=[],
        classification="complimentary_member",
        timing_additions=set(),
        known_internal=set(),
    )

    assert row["active_signal"] is True
    assert row["confirmed_active"] is False
    assert row["decision_required"] is False
    assert row["disposition"] == "excluded"
    assert row["primary_reason"] == "complimentary_membership_outside_kpi"
