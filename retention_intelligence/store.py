from __future__ import annotations

import json
import uuid
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    create_engine,
    delete,
    func,
    inspect,
    insert,
    select,
    text,
    update,
)
from sqlalchemy.engine import make_url

from .models import RetentionAssessment


metadata = MetaData()

runs = Table(
    "retention_runs",
    metadata,
    Column("run_id", String(64), primary_key=True),
    Column("started_at", DateTime(timezone=True), nullable=False),
    Column("completed_at", DateTime(timezone=True)),
    Column("status", String(20), nullable=False),
    Column("source_run_id", String(64)),
    Column("member_count", Integer, nullable=False, default=0),
    Column("included_count", Integer, nullable=False, default=0),
    Column("summary_json", Text),
    Column("error", Text),
)

snapshots = Table(
    "retention_member_snapshots",
    metadata,
    Column("run_id", String(64), primary_key=True),
    Column("trainerize_user_id", Integer, primary_key=True),
    Column("email", String(320), nullable=False),
    Column("first_name", String(160)),
    Column("last_name", String(160)),
    Column("service", String(200)),
    Column("trainer_name", String(200)),
    Column("status", String(60), nullable=False),
    Column("urgency", String(40), nullable=False),
    Column("data_confidence", String(40), nullable=False),
    Column("reason", Text, nullable=False),
    Column("action_owner", String(200)),
    Column("review_date", String(20)),
    Column("latest_signed_in", String(64)),
    Column("workouts_7d", Integer, nullable=False),
    Column("workouts_28d", Integer, nullable=False),
    Column("workouts_90d", Integer, nullable=False),
    Column("baseline_weekly_rate", Float, nullable=False),
    Column("recent_weekly_rate", Float, nullable=False),
    Column("change_percent", Float),
    Column("last_workout_date", String(20)),
    Column("days_since_last_workout", Integer),
    Column("engagement_source", String(40), nullable=False),
    Column("class_bookings_7d", Integer, nullable=False),
    Column("class_bookings_28d", Integer, nullable=False),
    Column("class_bookings_90d", Integer, nullable=False),
    Column("class_baseline_weekly_rate", Float, nullable=False),
    Column("class_recent_weekly_rate", Float, nullable=False),
    Column("class_change_percent", Float),
    Column("last_class_booking_date", String(20)),
    Column("days_since_last_class_booking", Integer),
    Column("classifier_version", String(40), nullable=False),
    Column("included_in_kpi", Boolean, nullable=False),
    Column("captured_at", DateTime(timezone=True), nullable=False),
)


class RetentionStore:
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
        connect_args = (
            {"check_same_thread": False}
            if database_url.startswith("sqlite")
            else {}
        )
        self.engine = create_engine(database_url, pool_pre_ping=True, connect_args=connect_args)
        metadata.create_all(self.engine)
        if hasattr(self.engine, "dialect"):
            self._migrate_snapshot_columns()

    def _migrate_snapshot_columns(self) -> None:
        existing = {
            item["name"]
            for item in inspect(self.engine).get_columns(
                "retention_member_snapshots"
            )
        }
        additions = {
            "engagement_source": (
                "VARCHAR(40) NOT NULL DEFAULT 'tracked_workout'"
            ),
            "class_bookings_7d": "INTEGER NOT NULL DEFAULT 0",
            "class_bookings_28d": "INTEGER NOT NULL DEFAULT 0",
            "class_bookings_90d": "INTEGER NOT NULL DEFAULT 0",
            "class_baseline_weekly_rate": "FLOAT NOT NULL DEFAULT 0",
            "class_recent_weekly_rate": "FLOAT NOT NULL DEFAULT 0",
            "class_change_percent": "FLOAT",
            "last_class_booking_date": "VARCHAR(20)",
            "days_since_last_class_booking": "INTEGER",
        }
        with self.engine.begin() as connection:
            for name, definition in additions.items():
                if name not in existing:
                    connection.execute(
                        text(
                            "ALTER TABLE retention_member_snapshots "
                            f"ADD COLUMN {name} {definition}"
                        )
                    )

    def start_run(self) -> str:
        run_id = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
        with self.engine.begin() as connection:
            connection.execute(
                insert(runs).values(
                    run_id=run_id,
                    started_at=datetime.now(UTC),
                    status="running",
                )
            )
        return run_id

    def complete_run(
        self,
        run_id: str,
        source_run_id: str,
        assessments: list[RetentionAssessment],
    ) -> dict[str, Any]:
        now = datetime.now(UTC)
        counts = Counter(
            item.status for item in assessments if item.included_in_kpi
        )
        summary = {
            "statuses": dict(sorted(counts.items())),
            "member_count": len(assessments),
            "included_count": sum(item.included_in_kpi for item in assessments),
        }
        with self.engine.begin() as connection:
            connection.execute(
                delete(snapshots).where(snapshots.c.run_id == run_id)
            )
            if assessments:
                connection.execute(
                    insert(snapshots),
                    [
                        {
                            **item.to_dict(),
                            "run_id": run_id,
                            "captured_at": now,
                        }
                        for item in assessments
                    ],
                )
            connection.execute(
                update(runs)
                .where(runs.c.run_id == run_id)
                .values(
                    completed_at=now,
                    status="complete",
                    source_run_id=source_run_id,
                    member_count=len(assessments),
                    included_count=summary["included_count"],
                    summary_json=json.dumps(summary, sort_keys=True),
                )
            )
        return summary

    def fail_run(self, run_id: str, error: str) -> None:
        with self.engine.begin() as connection:
            connection.execute(
                update(runs)
                .where(runs.c.run_id == run_id)
                .values(
                    completed_at=datetime.now(UTC),
                    status="failed",
                    error=error[:2000],
                )
            )

    def latest_successful_run_id(self) -> str | None:
        with self.engine.begin() as connection:
            value = connection.execute(
                select(runs.c.run_id)
                .where(runs.c.status == "complete")
                .order_by(runs.c.completed_at.desc())
                .limit(1)
            ).scalar()
        return str(value) if value else None

    def latest_summary(self) -> dict[str, Any] | None:
        with self.engine.begin() as connection:
            row = connection.execute(
                select(runs)
                .order_by(runs.c.started_at.desc())
                .limit(1)
            ).mappings().first()
        if not row:
            return None
        return {
            "runId": row["run_id"],
            "startedAt": row["started_at"].isoformat() if row["started_at"] else None,
            "completedAt": (
                row["completed_at"].isoformat() if row["completed_at"] else None
            ),
            "status": row["status"],
            "sourceRunId": row["source_run_id"],
            "memberCount": row["member_count"],
            "includedCount": row["included_count"],
            "summary": json.loads(row["summary_json"]) if row["summary_json"] else {},
            "error": row["error"],
        }

    def latest_radar(self, *, include_excluded: bool = False) -> list[dict[str, Any]]:
        run_id = self.latest_successful_run_id()
        if not run_id:
            return []
        query = select(snapshots).where(snapshots.c.run_id == run_id)
        if not include_excluded:
            query = query.where(snapshots.c.included_in_kpi.is_(True))
        query = query.order_by(
            snapshots.c.status,
            snapshots.c.days_since_last_workout.desc(),
            snapshots.c.last_name,
            snapshots.c.first_name,
        )
        with self.engine.begin() as connection:
            rows = connection.execute(query).mappings().all()
        return [
            {
                key: (
                    value.isoformat()
                    if isinstance(value, datetime)
                    else value
                )
                for key, value in dict(row).items()
            }
            for row in rows
        ]

    def consecutive_successes(self) -> int:
        with self.engine.begin() as connection:
            statuses = connection.execute(
                select(runs.c.status)
                .order_by(runs.c.started_at.desc())
                .limit(50)
            ).scalars().all()
        count = 0
        for status in statuses:
            if status != "complete":
                break
            count += 1
        return count
