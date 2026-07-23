from __future__ import annotations

import json
import sqlite3
import threading
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable

from .models import Finding


class StateStore:
    def __init__(self, path: str):
        self.path = path
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._init()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=30)
        connection.row_factory = sqlite3.Row
        return connection

    def _init(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                PRAGMA journal_mode=WAL;
                CREATE TABLE IF NOT EXISTS audit_runs (
                    id TEXT PRIMARY KEY,
                    run_type TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    completed_at TEXT,
                    status TEXT NOT NULL,
                    cohort_count INTEGER DEFAULT 0,
                    finding_count INTEGER DEFAULT 0,
                    error TEXT
                );
                CREATE TABLE IF NOT EXISTS findings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    contact_id TEXT NOT NULL,
                    category TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_findings_contact
                    ON findings(contact_id, created_at);
                CREATE TABLE IF NOT EXISTS event_queue (
                    event_id TEXT PRIMARY KEY,
                    contact_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    received_at TEXT NOT NULL,
                    due_at TEXT NOT NULL,
                    processed_at TEXT
                );
                CREATE INDEX IF NOT EXISTS idx_event_queue_due
                    ON event_queue(due_at, processed_at);
                CREATE TABLE IF NOT EXISTS app_state (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                """
            )

    def start_run(self, run_type: str) -> str:
        run_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        with self._lock, self._connect() as connection:
            connection.execute(
                """
                INSERT INTO audit_runs(id, run_type, started_at, status)
                VALUES (?, ?, ?, 'running')
                """,
                (run_id, run_type, now),
            )
        return run_id

    def complete_run(
        self, run_id: str, findings: Iterable[Finding], cohort_count: int
    ) -> None:
        items = list(findings)
        now = datetime.now(timezone.utc).isoformat()
        with self._lock, self._connect() as connection:
            connection.executemany(
                """
                INSERT INTO findings(run_id, contact_id, category, payload_json, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                [
                    (
                        run_id,
                        item.contact_id,
                        item.category,
                        json.dumps(item.to_dict(), default=str),
                        now,
                    )
                    for item in items
                ],
            )
            connection.execute(
                """
                UPDATE audit_runs
                SET completed_at=?, status='completed', cohort_count=?, finding_count=?
                WHERE id=?
                """,
                (now, cohort_count, len(items), run_id),
            )
            connection.execute(
                """
                INSERT INTO app_state(key, value, updated_at)
                VALUES ('last_successful_run', ?, ?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at
                """,
                (now, now),
            )

    def fail_run(self, run_id: str, error: str) -> None:
        now = datetime.now(timezone.utc).isoformat()
        with self._lock, self._connect() as connection:
            connection.execute(
                """
                UPDATE audit_runs SET completed_at=?, status='failed', error=? WHERE id=?
                """,
                (now, error[:1000], run_id),
            )

    def enqueue_event(
        self, event_id: str, contact_id: str, event_type: str, delay_minutes: int = 10
    ) -> bool:
        now = datetime.now(timezone.utc)
        due = now + timedelta(minutes=delay_minutes)
        with self._lock, self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT OR IGNORE INTO event_queue(
                    event_id, contact_id, event_type, received_at, due_at
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (event_id, contact_id, event_type, now.isoformat(), due.isoformat()),
            )
            return cursor.rowcount > 0

    def due_contacts(self, limit: int = 20) -> list[str]:
        now = datetime.now(timezone.utc).isoformat()
        with self._lock, self._connect() as connection:
            rows = connection.execute(
                """
                SELECT contact_id, MIN(due_at) AS due_at
                FROM event_queue
                WHERE processed_at IS NULL AND due_at <= ?
                GROUP BY contact_id
                ORDER BY due_at
                LIMIT ?
                """,
                (now, limit),
            ).fetchall()
        return [str(row["contact_id"]) for row in rows]

    def mark_contact_events_processed(self, contact_id: str) -> None:
        now = datetime.now(timezone.utc).isoformat()
        with self._lock, self._connect() as connection:
            connection.execute(
                """
                UPDATE event_queue SET processed_at=?
                WHERE contact_id=? AND processed_at IS NULL
                """,
                (now, contact_id),
            )

    def last_successful_run(self) -> str | None:
        with self._lock, self._connect() as connection:
            row = connection.execute(
                "SELECT value FROM app_state WHERE key='last_successful_run'"
            ).fetchone()
        return str(row["value"]) if row else None

    def record_kpi_write(self, week_start: str, payload: dict) -> None:
        now = datetime.now(timezone.utc).isoformat()
        with self._lock, self._connect() as connection:
            connection.execute(
                """
                INSERT INTO app_state(key, value, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    value=excluded.value,
                    updated_at=excluded.updated_at
                """,
                (
                    f"kpi_write:{week_start}",
                    json.dumps(payload, sort_keys=True, default=str),
                    now,
                ),
            )
