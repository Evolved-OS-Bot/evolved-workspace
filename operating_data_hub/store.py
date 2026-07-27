from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    UniqueConstraint,
    create_engine,
    func,
    insert,
    select,
    update,
)
from sqlalchemy.engine import make_url

from .contracts import canonical_json, fingerprint


metadata = MetaData()

source_snapshots = Table(
    "hub_source_snapshots",
    metadata,
    Column("snapshot_id", String(64), primary_key=True),
    Column("source", String(80), nullable=False, index=True),
    Column("observed_at", DateTime(timezone=True), nullable=False),
    Column("accepted_at", DateTime(timezone=True), nullable=False),
    Column("status", String(24), nullable=False),
    Column("complete", Integer, nullable=False),
    Column("record_count", Integer, nullable=False),
    Column("schema_version", Integer, nullable=False),
    Column("fingerprint", String(64), nullable=False),
    Column("payload_json", Text, nullable=False),
    UniqueConstraint("source", "fingerprint", name="uq_hub_source_fingerprint"),
)

job_runs = Table(
    "hub_job_runs",
    metadata,
    Column("run_id", String(64), primary_key=True),
    Column("job_id", String(120), nullable=False, index=True),
    Column("started_at", DateTime(timezone=True), nullable=False),
    Column("completed_at", DateTime(timezone=True)),
    Column("status", String(24), nullable=False),
    Column("summary_json", Text),
    Column("error", Text),
)

exceptions = Table(
    "hub_exceptions",
    metadata,
    Column("exception_id", String(64), primary_key=True),
    Column("domain", String(80), nullable=False),
    Column("code", String(120), nullable=False),
    Column("severity", String(24), nullable=False),
    Column("owner", String(160)),
    Column("status", String(24), nullable=False),
    Column("evidence_json", Text, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)

metric_snapshots = Table(
    "hub_metric_snapshots",
    metadata,
    Column("metric_snapshot_id", String(64), primary_key=True),
    Column("period_start", String(10), nullable=False),
    Column("period_end", String(10), nullable=False),
    Column("generated_at", DateTime(timezone=True), nullable=False),
    Column("source_snapshot_ids_json", Text, nullable=False),
    Column("metrics_json", Text, nullable=False),
    Column("definition_version", String(40), nullable=False),
)


class HubStore:
    def __init__(self, database_url: str):
        if database_url.startswith("postgresql://"):
            database_url = database_url.replace(
                "postgresql://", "postgresql+psycopg://", 1
            )
        elif database_url.startswith("postgres://"):
            database_url = database_url.replace(
                "postgres://", "postgresql+psycopg://", 1
            )
        if database_url.startswith("sqlite"):
            sqlite_database = make_url(database_url).database
            if sqlite_database and sqlite_database != ":memory:":
                Path(sqlite_database).parent.mkdir(parents=True, exist_ok=True)
        self.engine = create_engine(
            database_url,
            pool_pre_ping=True,
            connect_args=(
                {"check_same_thread": False}
                if database_url.startswith("sqlite")
                else {}
            ),
        )
        metadata.create_all(self.engine)

    def accept_snapshot(self, source: str, payload: dict[str, Any]) -> dict[str, Any]:
        payload_fingerprint = fingerprint(payload)
        now = datetime.now(UTC)
        observed_at = datetime.fromisoformat(
            str(payload["observed_at"]).replace("Z", "+00:00")
        )
        record_count = len(payload.get("rows") or [])
        if not record_count:
            summary = payload.get("summary") or {}
            record_count = int(
                summary.get("record_count")
                or summary.get("memberCount")
                or summary.get("includedCount")
                or 0
            )
        with self.engine.begin() as connection:
            existing = connection.execute(
                select(source_snapshots.c.snapshot_id).where(
                    source_snapshots.c.source == source,
                    source_snapshots.c.fingerprint == payload_fingerprint,
                )
            ).scalar()
            if existing:
                return {
                    "status": "duplicate",
                    "snapshot_id": str(existing),
                    "fingerprint": payload_fingerprint,
                }
            snapshot_id = (
                now.strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
            )
            connection.execute(
                insert(source_snapshots).values(
                    snapshot_id=snapshot_id,
                    source=source,
                    observed_at=observed_at,
                    accepted_at=now,
                    status=str(payload.get("status") or "complete"),
                    complete=int(bool(payload.get("complete"))),
                    record_count=record_count,
                    schema_version=int(payload.get("schema_version") or 1),
                    fingerprint=payload_fingerprint,
                    payload_json=canonical_json(payload),
                )
            )
        return {
            "status": "accepted",
            "snapshot_id": snapshot_id,
            "record_count": record_count,
            "fingerprint": payload_fingerprint,
        }

    def latest_snapshot(self, source: str) -> dict[str, Any] | None:
        with self.engine.begin() as connection:
            row = connection.execute(
                select(source_snapshots)
                .where(
                    source_snapshots.c.source == source,
                    source_snapshots.c.complete == 1,
                )
                .order_by(source_snapshots.c.observed_at.desc())
                .limit(1)
            ).mappings().first()
        return self._snapshot(row) if row else None

    def latest_snapshots(self) -> list[dict[str, Any]]:
        latest = (
            select(
                source_snapshots.c.source,
                func.max(source_snapshots.c.observed_at).label("observed_at"),
            )
            .where(source_snapshots.c.complete == 1)
            .group_by(source_snapshots.c.source)
            .subquery()
        )
        with self.engine.begin() as connection:
            rows = connection.execute(
                select(source_snapshots).join(
                    latest,
                    (source_snapshots.c.source == latest.c.source)
                    & (source_snapshots.c.observed_at == latest.c.observed_at),
                )
            ).mappings().all()
        return [self._snapshot(row) for row in rows]

    @staticmethod
    def _snapshot(row: Any) -> dict[str, Any]:
        return {
            "snapshot_id": row["snapshot_id"],
            "source": row["source"],
            "observed_at": row["observed_at"].isoformat(),
            "accepted_at": row["accepted_at"].isoformat(),
            "status": row["status"],
            "complete": bool(row["complete"]),
            "record_count": row["record_count"],
            "schema_version": row["schema_version"],
            "fingerprint": row["fingerprint"],
            "payload": json.loads(row["payload_json"]),
        }

    def start_job(self, job_id: str) -> str:
        run_id = (
            datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
            + "-"
            + uuid.uuid4().hex[:8]
        )
        with self.engine.begin() as connection:
            connection.execute(
                insert(job_runs).values(
                    run_id=run_id,
                    job_id=job_id,
                    started_at=datetime.now(UTC),
                    status="running",
                )
            )
        return run_id

    def finish_job(
        self,
        run_id: str,
        *,
        status: str,
        summary: dict[str, Any] | None = None,
        error: str | None = None,
    ) -> None:
        with self.engine.begin() as connection:
            connection.execute(
                update(job_runs)
                .where(job_runs.c.run_id == run_id)
                .values(
                    completed_at=datetime.now(UTC),
                    status=status,
                    summary_json=(
                        canonical_json(summary) if summary is not None else None
                    ),
                    error=(error or "")[:2000] or None,
                )
            )

    def recent_jobs(self, limit: int = 25) -> list[dict[str, Any]]:
        with self.engine.begin() as connection:
            rows = connection.execute(
                select(job_runs)
                .order_by(job_runs.c.started_at.desc())
                .limit(limit)
            ).mappings().all()
        return [
            {
                "run_id": row["run_id"],
                "job_id": row["job_id"],
                "started_at": row["started_at"].isoformat(),
                "completed_at": (
                    row["completed_at"].isoformat()
                    if row["completed_at"]
                    else None
                ),
                "status": row["status"],
                "summary": (
                    json.loads(row["summary_json"])
                    if row["summary_json"]
                    else {}
                ),
                "error": row["error"],
            }
            for row in rows
        ]

    def open_exception_counts(self) -> dict[str, int]:
        with self.engine.begin() as connection:
            rows = connection.execute(
                select(exceptions.c.severity, func.count())
                .where(exceptions.c.status == "open")
                .group_by(exceptions.c.severity)
            ).all()
        return {str(severity): int(count) for severity, count in rows}

