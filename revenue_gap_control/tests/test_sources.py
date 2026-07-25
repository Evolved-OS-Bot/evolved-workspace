from __future__ import annotations

import sqlite3
from datetime import UTC, date, datetime
from pathlib import Path

import pytest

from revenue_gap_control.sources import (
    SourceError,
    apply_verified_phone_fallback,
    load_approved_account_classifications,
    load_booking_evidence,
    parse_active_pt,
    parse_active_sgpt,
    read_kpi_cash,
)
from revenue_gap_control.models import RosterRecord, SourceEvidence


def test_parse_active_sgpt_trims_status_header_and_preserves_pia():
    rows = [
        [
            "Date",
            "First Name",
            "Last Name",
            "Phone",
            "Email",
            "Salesperson",
            "Membership Tier",
            "Status ",
            "Weekly Debit",
        ],
        ["", "Laura", "Wong", "0400", "Laura@example.com", "", "Bronze", "Active - PIA", "PIF"],
    ]
    parsed = parse_active_sgpt(rows)
    assert parsed[0].email == "laura@example.com"
    assert parsed[0].status == "Active - PIA"
    assert parsed[0].weekly_allocation is None


def test_parse_active_pt_uses_current_headers_and_amounts():
    rows = [
        [
            "1:1",
            "First Name",
            "Last Name",
            "Phone",
            "Email",
            "Personal Trainer",
            "Session Length",
            "Sessions p/wk",
            "$$$",
            "Weekly Debit",
            "Rebook",
        ],
        ["", "Anne", "Leditschke", "0400", "anne@example.com", "Megan Brown", "30 mins", "2", "$60", "$120", "PT Minder active"],
    ]
    parsed = parse_active_pt(rows)
    assert parsed[0].weekly_allocation is not None
    assert str(parsed[0].weekly_allocation) == "120.00"
    assert str(parsed[0].session_cost) == "60.00"


def test_missing_required_header_fails_closed():
    with pytest.raises(SourceError):
        parse_active_sgpt([["First Name", "Email"]])


def test_kpi_cash_uses_the_monday_after_the_entitlement_window():
    rows = [[] for _ in range(106)]
    rows[0] = ["", 46230]
    rows[105] = ["", 10927.24]

    def read_sheet(_name, _range):
        return rows

    cash, label = read_kpi_cash(read_sheet, date(2026, 7, 27))
    assert str(cash) == "10927.24"
    assert label == "KPI B106 dated 2026-07-27"


def test_booking_snapshot_maps_contact_id_to_canonical_email(tmp_path: Path):
    database = tmp_path / "booking.sqlite"
    connection = sqlite3.connect(database)
    with connection:
        connection.executescript(
            """
            CREATE TABLE audit_runs (
              id TEXT, run_type TEXT, started_at TEXT, completed_at TEXT,
              status TEXT, cohort_count INTEGER, finding_count INTEGER, error TEXT
            );
            CREATE TABLE findings (
              id INTEGER PRIMARY KEY, run_id TEXT, contact_id TEXT,
              category TEXT, payload_json TEXT, created_at TEXT
            );
            """
        )
        now = datetime.now(UTC).isoformat()
        connection.execute(
            "INSERT INTO audit_runs VALUES ('run-1','full',?,?, 'completed',1,1,NULL)",
            (now, now),
        )
        connection.execute(
            """
            INSERT INTO findings(run_id,contact_id,category,payload_json,created_at)
            VALUES ('run-1','contact-1','NO_FUTURE_BOOKINGS',
                    '{"last_completed":"2026-07-01T10:00:00+10:00"}',?)
            """,
            (now,),
        )
    evidence = {"member@example.com": SourceEvidence(email="member@example.com")}
    limitations, run_id = load_booking_evidence(
        database,
        evidence,
        {"contact-1": "member@example.com"},
    )
    assert limitations == []
    assert run_id == "run-1"
    assert evidence["member@example.com"].has_future_booking is False


def test_verified_unique_phone_can_link_a_stale_roster_email():
    roster = [
        RosterRecord(
            service="PT",
            row_number=2,
            first_name="Member",
            last_name="Example",
            email="legacy@example.com",
            phone="61400111222",
            status="Active",
            weekly_allocation=None,
            payment_marker="",
        )
    ]
    source = SourceEvidence(
        email="current@example.com",
        raw={"verified_phones": ["0400 111 222"]},
    )
    evidence = {"current@example.com": source}
    apply_verified_phone_fallback(roster, evidence)
    assert evidence["legacy@example.com"] is source


def test_ambiguous_phone_does_not_link():
    roster = [
        RosterRecord(
            service="PT",
            row_number=2,
            first_name="Member",
            last_name="Example",
            email="legacy@example.com",
            phone="0400111222",
            status="Active",
            weekly_allocation=None,
            payment_marker="",
        )
    ]
    evidence = {
        "one@example.com": SourceEvidence(
            email="one@example.com", raw={"verified_phones": ["0400111222"]}
        ),
        "two@example.com": SourceEvidence(
            email="two@example.com", raw={"verified_phones": ["0400111222"]}
        ),
    }
    apply_verified_phone_fallback(roster, evidence)
    assert "legacy@example.com" not in evidence


def test_account_classification_does_not_treat_current_pt_as_receipt(tmp_path: Path):
    path = tmp_path / "classifications.csv"
    path.write_text(
        "email,classification,approved_active_without_local_entitlement,note\n"
        "current@example.com,current_pt_client,true,Current PT\n"
        "prepaid@example.com,prepaid_credit_client,true,Approved PIF\n",
        encoding="utf-8",
    )
    loaded = load_approved_account_classifications(path)
    assert "current@example.com" not in loaded
    assert loaded["prepaid@example.com"].status == "paid_in_advance"
