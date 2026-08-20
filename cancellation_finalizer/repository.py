from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Integer, String, Text, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker


class Base(DeclarativeBase):
    pass


class FinalizationCase(Base):
    __tablename__ = "cancellation_finalization_cases"

    idempotency_key: Mapped[str] = mapped_column(String(160), primary_key=True)
    contact_id: Mapped[str] = mapped_column(String(80), index=True)
    cancellation_type: Mapped[str] = mapped_column(String(32))
    final_access_date: Mapped[str] = mapped_column(String(10))
    payload: Mapped[dict[str, Any]] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(40), index=True, default="queued")
    current_step: Mapped[str] = mapped_column(String(60), default="queued")
    receipts: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    next_attempt_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    def public(self) -> dict[str, Any]:
        return {
            "idempotency_key": self.idempotency_key,
            "contact_id": self.contact_id,
            "cancellation_type": self.cancellation_type,
            "final_access_date": self.final_access_date,
            "status": self.status,
            "current_step": self.current_step,
            "attempts": self.attempts,
            "last_error": self.last_error,
            "receipts": self.receipts or {},
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class Repository:
    def __init__(self, database_url: str):
        if database_url.startswith("postgres://"):
            database_url = "postgresql+psycopg://" + database_url[len("postgres://") :]
        elif database_url.startswith("postgresql://"):
            database_url = "postgresql+psycopg://" + database_url[len("postgresql://") :]
        self.engine = create_engine(database_url, pool_pre_ping=True)
        self.sessions = sessionmaker(self.engine, expire_on_commit=False)

    def create_schema(self) -> None:
        Base.metadata.create_all(self.engine)

    def upsert(self, payload: dict[str, Any], *, now: datetime) -> FinalizationCase:
        key = payload["idempotency_key"]
        with self.sessions.begin() as db:
            case = db.get(FinalizationCase, key)
            if case:
                if case.payload != payload:
                    raise ValueError("idempotency key already exists with a different payload")
                return case
            case = FinalizationCase(
                idempotency_key=key,
                contact_id=payload["contact_id"],
                cancellation_type=payload["cancellation_type"],
                final_access_date=payload["final_access_date"],
                payload=payload,
                status="queued",
                current_step="queued",
                receipts={},
                attempts=0,
                created_at=now,
                updated_at=now,
            )
            db.add(case)
        return case

    def get(self, key: str) -> FinalizationCase | None:
        with self.sessions() as db:
            return db.get(FinalizationCase, key)

    def due(self, now: datetime, limit: int = 25) -> list[str]:
        with self.sessions() as db:
            return list(
                db.scalars(
                    select(FinalizationCase.idempotency_key)
                    .where(FinalizationCase.status.in_(("queued", "retry_scheduled")))
                    .where(
                        (FinalizationCase.next_attempt_at.is_(None))
                        | (FinalizationCase.next_attempt_at <= now)
                    )
                    .order_by(FinalizationCase.created_at)
                    .limit(limit)
                ).all()
            )

    def update(self, key: str, **values: Any) -> FinalizationCase:
        values["updated_at"] = values.get("updated_at") or datetime.now(UTC)
        with self.sessions.begin() as db:
            case = db.get(FinalizationCase, key)
            if case is None:
                raise KeyError(key)
            for name, value in values.items():
                setattr(case, name, value)
        return case

