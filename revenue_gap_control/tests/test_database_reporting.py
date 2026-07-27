from __future__ import annotations

import sqlite3
from datetime import date
from decimal import Decimal

from revenue_gap_control.database import AuditStore
from revenue_gap_control.engine import AuditEngine
from revenue_gap_control.models import AuditInputs, RosterRecord, SourceEvidence
from revenue_gap_control.reporting import write_reports


def test_store_and_reports_are_created(tmp_path):
    record = RosterRecord(
        service="SGPT",
        row_number=2,
        first_name="Test",
        last_name="Member",
        email="member@example.com",
        phone="0400000000",
        status="Active",
        weekly_allocation=Decimal("99"),
        payment_marker="$99",
        product="Bronze",
    )
    source = SourceEvidence(
        email=record.email,
        stripe_statuses=["active"],
        latest_invoice_status="paid",
        latest_invoice_paid=True,
        trainerize_active=True,
        source_run_id="source-1",
    )
    inputs = AuditInputs(
        window_start=date(2026, 7, 20),
        window_end=date(2026, 7, 26),
        cleared_cash=Decimal("99"),
        roster=[record],
        evidence_by_email={record.email: source},
    )
    result = AuditEngine().run(inputs, run_id="audit-1")
    database = tmp_path / "audit.sqlite"
    AuditStore(database).save(inputs, result)
    paths = write_reports(inputs, result, tmp_path / "public", tmp_path / "private")

    connection = sqlite3.connect(database)
    assert connection.execute("SELECT COUNT(*) FROM runs").fetchone()[0] == 1
    assert connection.execute("SELECT COUNT(*) FROM roster_snapshot").fetchone()[0] == 1
    assert paths["public_summary"].exists()
    assert paths["client_audit"].exists()
