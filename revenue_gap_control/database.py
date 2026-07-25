from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from .models import AuditInputs, AuditResult


SCHEMA = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS runs (
    run_id TEXT PRIMARY KEY,
    window_start TEXT NOT NULL,
    window_end TEXT NOT NULL,
    cash_label TEXT,
    cleared_cash TEXT NOT NULL,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    status TEXT NOT NULL,
    limitations_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS client_identity (
    run_id TEXT NOT NULL,
    identity_key TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    ghl_contact_ids_json TEXT NOT NULL,
    PRIMARY KEY (run_id, identity_key)
);

CREATE TABLE IF NOT EXISTS roster_snapshot (
    run_id TEXT NOT NULL,
    service TEXT NOT NULL,
    source_row INTEGER NOT NULL,
    email TEXT,
    phone TEXT,
    name TEXT NOT NULL,
    product TEXT,
    status TEXT,
    weekly_allocation TEXT,
    payment_marker TEXT,
    trainer TEXT,
    session_length TEXT,
    sessions_per_week TEXT,
    session_cost TEXT,
    notes TEXT,
    classification TEXT NOT NULL,
    PRIMARY KEY (run_id, service, source_row)
);

CREATE TABLE IF NOT EXISTS payment_evidence (
    run_id TEXT NOT NULL,
    email TEXT NOT NULL,
    stripe_statuses_json TEXT NOT NULL,
    latest_invoice_status TEXT,
    latest_invoice_paid INTEGER NOT NULL,
    latest_receipt_date TEXT,
    pause_collection INTEGER NOT NULL,
    source_run_id TEXT,
    raw_json TEXT NOT NULL,
    PRIMARY KEY (run_id, email)
);

CREATE TABLE IF NOT EXISTS booking_evidence (
    run_id TEXT NOT NULL,
    email TEXT NOT NULL,
    category TEXT,
    has_future_booking INTEGER,
    booked_through TEXT,
    last_completed TEXT,
    last_future TEXT,
    raw_json TEXT NOT NULL,
    PRIMARY KEY (run_id, email)
);

CREATE TABLE IF NOT EXISTS lifecycle_evidence (
    run_id TEXT NOT NULL,
    email TEXT NOT NULL,
    membership_type TEXT,
    membership_stage TEXT,
    cancellation_status TEXT,
    final_access_date TEXT,
    hold_status TEXT,
    trainerize_active INTEGER NOT NULL,
    PRIMARY KEY (run_id, email)
);

CREATE TABLE IF NOT EXISTS cash_bridge (
    run_id TEXT PRIMARY KEY,
    sgpt_numeric_allocation TEXT NOT NULL,
    pt_numeric_allocation TEXT NOT NULL,
    combined_numeric_allocation TEXT NOT NULL,
    pif_rows INTEGER NOT NULL,
    approved_pauses TEXT NOT NULL,
    arrears TEXT NOT NULL,
    future_starts TEXT NOT NULL,
    confirmed_current_income TEXT NOT NULL,
    scheduled_run_rate TEXT NOT NULL,
    cleared_cash TEXT NOT NULL,
    timing_items TEXT NOT NULL,
    unexplained_variance TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS exceptions (
    run_id TEXT NOT NULL,
    exception_number INTEGER NOT NULL,
    email TEXT,
    client_name TEXT NOT NULL,
    service TEXT NOT NULL,
    classification TEXT NOT NULL,
    summary TEXT NOT NULL,
    financial_value TEXT NOT NULL,
    evidence_checked_json TEXT NOT NULL,
    owner TEXT NOT NULL,
    next_action TEXT NOT NULL,
    due_date TEXT,
    source_row INTEGER,
    PRIMARY KEY (run_id, exception_number)
);

CREATE TABLE IF NOT EXISTS decisions (
    decision_id INTEGER PRIMARY KEY AUTOINCREMENT,
    exception_run_id TEXT NOT NULL,
    exception_number INTEGER NOT NULL,
    decision TEXT NOT NULL,
    decided_by TEXT NOT NULL,
    decided_at TEXT NOT NULL,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS write_evidence (
    write_id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    target TEXT NOT NULL,
    requested_json TEXT NOT NULL,
    applied_json TEXT,
    verified_json TEXT,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL
);
"""


class AuditStore:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as connection:
            connection.executescript(SCHEMA)

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def save(self, inputs: AuditInputs, result: AuditResult) -> None:
        now = datetime.now(UTC).isoformat(timespec="seconds")
        with self.connect() as connection:
            connection.execute(
                """
                INSERT INTO runs VALUES (?, ?, ?, ?, ?, ?, ?, 'complete', ?)
                """,
                (
                    result.run_id,
                    inputs.window_start.isoformat(),
                    inputs.window_end.isoformat(),
                    inputs.cash_label,
                    str(inputs.cleared_cash),
                    now,
                    now,
                    json.dumps(inputs.limitations),
                ),
            )
            assessment_by_key = {
                (item.roster.service, item.roster.row_number): item
                for item in result.assessments
            }
            connection.executemany(
                """
                INSERT INTO roster_snapshot VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
                """,
                [
                    (
                        result.run_id,
                        row.service,
                        row.row_number,
                        row.email,
                        row.phone,
                        row.name,
                        row.product,
                        row.status,
                        str(row.weekly_allocation) if row.weekly_allocation is not None else None,
                        row.payment_marker,
                        row.trainer,
                        row.session_length,
                        row.sessions_per_week,
                        str(row.session_cost) if row.session_cost is not None else None,
                        row.notes,
                        assessment_by_key[(row.service, row.row_number)].classification,
                    )
                    for row in inputs.roster
                ],
            )
            for email, evidence in inputs.evidence_by_email.items():
                identity_key = email or f"unmatched:{','.join(evidence.ghl_contact_ids)}"
                connection.execute(
                    "INSERT INTO client_identity VALUES (?, ?, ?, ?, ?)",
                    (
                        result.run_id,
                        identity_key,
                        email,
                        "",
                        json.dumps(evidence.ghl_contact_ids),
                    ),
                )
                connection.execute(
                    "INSERT INTO payment_evidence VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        result.run_id,
                        email,
                        json.dumps(evidence.stripe_statuses),
                        evidence.latest_invoice_status,
                        int(evidence.latest_invoice_paid),
                        evidence.latest_receipt_date,
                        int(evidence.pause_collection),
                        evidence.source_run_id,
                        json.dumps(evidence.raw, default=str),
                    ),
                )
                connection.execute(
                    "INSERT INTO booking_evidence VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        result.run_id,
                        email,
                        evidence.booking_category,
                        (
                            None
                            if evidence.has_future_booking is None
                            else int(evidence.has_future_booking)
                        ),
                        evidence.booked_through,
                        evidence.last_completed,
                        evidence.last_future,
                        json.dumps(evidence.raw.get("booking", {}), default=str),
                    ),
                )
                connection.execute(
                    "INSERT INTO lifecycle_evidence VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        result.run_id,
                        email,
                        evidence.membership_type,
                        evidence.membership_stage,
                        evidence.cancellation_status,
                        evidence.final_access_date,
                        evidence.hold_status,
                        int(evidence.trainerize_active),
                    ),
                )

            bridge = result.bridge
            connection.execute(
                "INSERT INTO cash_bridge VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    result.run_id,
                    str(bridge.sgpt_numeric_allocation),
                    str(bridge.pt_numeric_allocation),
                    str(bridge.combined_numeric_allocation),
                    bridge.pif_rows,
                    str(bridge.approved_pauses),
                    str(bridge.arrears),
                    str(bridge.future_starts),
                    str(bridge.confirmed_current_income),
                    str(bridge.scheduled_run_rate),
                    str(bridge.cleared_cash),
                    str(bridge.timing_items),
                    str(bridge.unexplained_variance),
                ),
            )
            connection.executemany(
                """
                INSERT INTO exceptions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        result.run_id,
                        index,
                        item.email,
                        item.client_name,
                        item.service,
                        item.classification,
                        item.summary,
                        str(item.financial_value),
                        json.dumps(item.evidence_checked),
                        item.owner,
                        item.next_action,
                        item.due_date,
                        item.source_row,
                    )
                    for index, item in enumerate(result.exceptions, start=1)
                ],
            )

    def latest_run(self) -> sqlite3.Row | None:
        with self.connect() as connection:
            return connection.execute(
                "SELECT * FROM runs WHERE status='complete' ORDER BY completed_at DESC LIMIT 1"
            ).fetchone()
