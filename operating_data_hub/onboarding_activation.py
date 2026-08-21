from __future__ import annotations

import re
from datetime import UTC, date, datetime, timedelta
from typing import Any, Iterable

from .config import BRISBANE_TZ
from .trainerize_attendance import (
    SESSION_NAMES,
    TRACKED_STATUSES,
    TrainerizeAttendanceClient,
    _identity_candidates,
    normalise_text,
)


TRAINING_RECORD_TYPES = {
    "workoutregular",
    "workoutcircuit",
    "workoutinterval",
}
POSITIVE_REPLY_TASK = re.compile(
    r"^day\s+(?:7|8|9)\s+positive\s+reply:\s+respond\s+and\s+verify$",
    re.IGNORECASE,
)
CONFIRMED_CALL_TASK = re.compile(
    r"^first\s+week\s+confirmed(?:\s+by\s+call)?$",
    re.IGNORECASE,
)


def _datetime(value: Any) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=BRISBANE_TZ)
    return parsed.astimezone(UTC)


def _training_records(
    calendar: Iterable[dict[str, Any]],
    *,
    not_before: date,
) -> list[dict[str, str]]:
    records: dict[str, dict[str, str]] = {}
    for day in calendar:
        training_date = str(day.get("date") or "")[:10]
        if not training_date or date.fromisoformat(training_date) < not_before:
            continue
        for item in day.get("items") or []:
            item_type = re.sub(
                r"[^a-z]", "", str(item.get("type") or "").lower()
            )
            status = re.sub(
                r"[^a-z]", "", str(item.get("status") or "").lower()
            )
            if (
                item_type not in TRAINING_RECORD_TYPES
                or status not in {
                    re.sub(r"[^a-z]", "", value)
                    for value in TRACKED_STATUSES
                }
            ):
                continue
            record_id = str(item.get("id") or "").strip()
            if not record_id:
                continue
            records.setdefault(
                record_id,
                {
                    "record_id": record_id,
                    "training_date": training_date,
                    "record_type": str(item.get("type") or "").strip(),
                },
            )
    return sorted(
        records.values(),
        key=lambda row: (row["training_date"], row["record_id"]),
    )


def _first_week_confirmation(
    tasks: Iterable[dict[str, Any]],
) -> dict[str, Any] | None:
    evidence = []
    for task in tasks:
        if not bool(task.get("completed")):
            continue
        title = " ".join(str(task.get("title") or "").split())
        if POSITIVE_REPLY_TASK.match(title):
            kind = "positive_reply_verified"
        elif CONFIRMED_CALL_TASK.match(title):
            kind = "staff_call_confirmed"
        else:
            continue
        occurred_at = _datetime(
            task.get("completedAt")
            or task.get("updatedAt")
            or task.get("dueDate")
        )
        if occurred_at is None:
            continue
        evidence.append(
            {
                "kind": kind,
                "occurred_at": occurred_at.isoformat(),
                "task_id": str(task.get("id") or "").strip() or None,
            }
        )
    return (
        min(evidence, key=lambda row: row["occurred_at"])
        if evidence
        else None
    )


def _trainerize_onboarding_attended(
    calendar: Iterable[dict[str, Any]],
    *,
    target_date: str | None,
) -> bool:
    if not target_date:
        return False
    for day in calendar:
        if str(day.get("date") or "")[:10] != target_date:
            continue
        for item in day.get("items") or []:
            status = normalise_text(item.get("status")).replace(" ", "_")
            name = normalise_text(
                item.get("name")
                or item.get("title")
                or item.get("workoutName")
                or item.get("description")
            )
            if (
                status in TRACKED_STATUSES
                and name in SESSION_NAMES["onboarding"]
            ):
                return True
    return False


def build_onboarding_activation_evidence(
    *,
    trainerize_client: TrainerizeAttendanceClient,
    ghl_client: Any,
    onboarding_cases: list[dict[str, Any]],
    identities: dict[str, dict[str, Any]],
    observed_at: datetime,
    lookback_days: int = 120,
    activation_window_days: int = 60,
) -> dict[str, Any]:
    earliest_sale = (
        observed_at.astimezone(BRISBANE_TZ).date()
        - timedelta(days=lookback_days)
    )
    selected = [
        dict(row)
        for row in onboarding_cases
        if (
            _datetime(row.get("sold_at")) is not None
            and _datetime(row["sold_at"]).astimezone(BRISBANE_TZ).date()
            >= earliest_sale
        )
    ]
    clients = trainerize_client.attendance_clients()
    cases: list[dict[str, Any]] = []
    for source in selected:
        contact_id = str(source.get("contact_id") or "")
        sold_at = _datetime(source.get("sold_at"))
        if sold_at is None:
            continue
        sold_date = sold_at.astimezone(BRISBANE_TZ).date()
        end_date = min(
            sold_date + timedelta(days=activation_window_days),
            observed_at.astimezone(BRISBANE_TZ).date(),
        )
        matches, identity_basis = _identity_candidates(
            identities.get(contact_id) or {},
            clients,
        )
        identity_state = (
            "matched"
            if len(matches) == 1
            else "missing"
            if not matches
            else "ambiguous"
        )
        records: list[dict[str, str]] = []
        calendar: list[dict[str, Any]] = []
        if len(matches) == 1 and end_date >= sold_date:
            calendar = trainerize_client.calendar(
                int(matches[0]["id"]),
                sold_date,
                end_date,
            )
            records = _training_records(
                calendar,
                not_before=sold_date,
            )
        confirmation = _first_week_confirmation(
            ghl_client.list_contact_tasks(contact_id)
        )
        onboarding_at = _datetime(
            source.get("first_onboarding_completed_at")
        )
        onboarding_source = "ghl_showed" if onboarding_at else None
        scheduled_onboarding = _datetime(
            source.get("first_onboarding_scheduled_at")
        )
        if (
            onboarding_at is None
            and scheduled_onboarding is not None
            and _trainerize_onboarding_attended(
                calendar,
                target_date=(
                    scheduled_onboarding.astimezone(BRISBANE_TZ)
                    .date()
                    .isoformat()
                ),
            )
        ):
            onboarding_at = scheduled_onboarding
            onboarding_source = "trainerize_exact_date_tracked_session"
        third_training_at = (
            datetime.combine(
                date.fromisoformat(records[2]["training_date"]),
                datetime.min.time(),
                tzinfo=BRISBANE_TZ,
            ).astimezone(UTC)
            if len(records) >= 3
            else None
        )
        requirements = {
            "onboarding_attended": onboarding_at is not None,
            "three_training_records": third_training_at is not None,
            "first_week_confirmed": confirmation is not None,
        }
        activation_at = (
            max(
                [
                    onboarding_at,
                    third_training_at,
                    _datetime(
                        confirmation.get("occurred_at")
                        if confirmation
                        else None
                    ),
                ]
            )
            if all(requirements.values())
            else None
        )
        cases.append(
            {
                "sale_id": source.get("sale_id"),
                "contact_id": contact_id,
                "sold_at": sold_at.isoformat(),
                "service": source.get("entitlement_type"),
                "identity_state": identity_state,
                "identity_basis": identity_basis,
                "onboarding_attended_at": (
                    onboarding_at.isoformat() if onboarding_at else None
                ),
                "onboarding_attendance_source": onboarding_source,
                "training_record_count": len(records),
                "third_training_at": (
                    third_training_at.isoformat()
                    if third_training_at
                    else None
                ),
                "first_week_confirmation": confirmation,
                "requirements": requirements,
                "activation_at": (
                    activation_at.isoformat() if activation_at else None
                ),
                "activation_days": (
                    (
                        activation_at.astimezone(BRISBANE_TZ).date()
                        - sold_date
                    ).days
                    if activation_at
                    else None
                ),
            }
        )
    return {
        "definition_version": "successful-first-week-v1",
        "observed_at": observed_at.isoformat(),
        "complete": True,
        "cases": cases,
        "summary": {
            "eligible_sales": len(cases),
            "activated": sum(
                row["activation_at"] is not None for row in cases
            ),
            "onboarding_attended": sum(
                row["requirements"]["onboarding_attended"] for row in cases
            ),
            "three_training_records": sum(
                row["requirements"]["three_training_records"]
                for row in cases
            ),
            "first_week_confirmed": sum(
                row["requirements"]["first_week_confirmed"] for row in cases
            ),
            "trainerize_identity_unresolved": sum(
                row["identity_state"] != "matched" for row in cases
            ),
        },
    }
