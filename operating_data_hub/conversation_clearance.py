from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime, time, timedelta
from typing import Any, Iterable

from .config import BRISBANE_TZ


RULE_VERSION = "conversation-clearance-v1-shadow"
CLASSIFICATION_VERSION = "conversation-service-risk-v1"

CATEGORIES = {
    "immediate_service_risk",
    "revenue_sensitive",
    "member_administration",
    "routine_response",
    "no_response_required",
    "manual_review",
}

DISPOSITIONS = {
    "responded",
    "spam_or_solicitation",
    "duplicate_or_system_message",
    "no_response_required_approved",
    "delegated_to_owned_task",
    "blocked_and_escalated",
}

OPEN_STATES = {"open", "due_soon", "overdue", "blocked"}
TERMINAL_STATES = {"resolved", "disposed", "delegated", "reopened"}

DEFAULT_SERVICE_MINUTES = {
    "immediate_service_risk": 60,
    "revenue_sensitive": 240,
    "member_administration": 240,
    "routine_response": 480,
    "no_response_required": 480,
    "manual_review": 120,
}

PROTECTED_PATTERNS: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "immediate_service_risk",
        (
            "complaint",
            "cancel my membership",
            "cancel membership",
            "cancel my pt",
            "refund",
            "charged twice",
            "double charged",
            "can't access",
            "cannot access",
            "locked out",
            "injured",
            "injury",
            "unsafe",
            "emergency",
        ),
    ),
    (
        "member_administration",
        (
            "hold my membership",
            "pause my membership",
            "reschedule",
            "change my booking",
            "cancel my session",
            "payment failed",
        ),
    ),
)


def parse_datetime(value: Any, field: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be an ISO datetime") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"{field} must include a timezone")
    return parsed.astimezone(UTC)


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        default=str,
    )


def stable_id(prefix: str, *values: Any) -> str:
    digest = hashlib.sha256(
        "|".join(str(value or "") for value in values).encode("utf-8")
    ).hexdigest()
    return f"{prefix}_{digest[:40]}"


def case_cycle_key(observation: dict[str, Any]) -> str:
    conversation_id = str(observation.get("conversation_id") or "").strip()
    inbound_id = str(
        observation.get("latest_inbound_message_id") or ""
    ).strip()
    inbound_at = str(observation.get("latest_inbound_at") or "").strip()
    if not conversation_id:
        raise ValueError("conversation_id is required")
    if not inbound_id and not inbound_at:
        raise ValueError(
            "latest inbound message id or timestamp is required"
        )
    return stable_id(
        "conversation_cycle",
        conversation_id,
        inbound_id or f"unresolved:{inbound_at}",
    )


def deterministic_category(
    text: Any,
    *,
    is_sa_prequalification: bool = False,
    identity_review_required: bool = False,
    message_history_complete: bool = True,
) -> str | None:
    if identity_review_required or not message_history_complete:
        return "manual_review"
    if is_sa_prequalification:
        return "revenue_sensitive"
    normal = " ".join(str(text or "").lower().split())
    for category, phrases in PROTECTED_PATTERNS:
        if any(phrase in normal for phrase in phrases):
            return category
    return None


def normalise_category(value: Any) -> str:
    category = str(value or "manual_review").strip().lower()
    if category not in CATEGORIES:
        return "manual_review"
    return category


def _next_staffed_start(
    value: datetime,
    *,
    start_hour: int,
    end_hour: int,
    staffed_weekdays: tuple[int, ...],
) -> datetime:
    local = value.astimezone(BRISBANE_TZ)
    while True:
        if local.weekday() not in staffed_weekdays:
            local = datetime.combine(
                local.date() + timedelta(days=1),
                time(hour=start_hour),
                BRISBANE_TZ,
            )
            continue
        day_start = datetime.combine(
            local.date(), time(hour=start_hour), BRISBANE_TZ
        )
        day_end = datetime.combine(
            local.date(), time(hour=end_hour), BRISBANE_TZ
        )
        if local < day_start:
            return day_start
        if local >= day_end:
            local = datetime.combine(
                local.date() + timedelta(days=1),
                time(hour=start_hour),
                BRISBANE_TZ,
            )
            continue
        return local


def staffed_deadline(
    opened_at: datetime,
    category: str,
    *,
    service_minutes: dict[str, int] | None = None,
    start_hour: int = 8,
    end_hour: int = 17,
    staffed_weekdays: tuple[int, ...] = (0, 1, 2, 3, 4),
) -> datetime:
    minutes = int(
        (service_minutes or DEFAULT_SERVICE_MINUTES).get(category, 120)
    )
    cursor = _next_staffed_start(
        opened_at,
        start_hour=start_hour,
        end_hour=end_hour,
        staffed_weekdays=staffed_weekdays,
    )
    remaining = timedelta(minutes=max(1, minutes))
    while remaining.total_seconds() > 0:
        local = cursor.astimezone(BRISBANE_TZ)
        day_end = datetime.combine(
            local.date(), time(hour=end_hour), BRISBANE_TZ
        )
        available = day_end - local
        if remaining <= available:
            return (local + remaining).astimezone(UTC)
        remaining -= max(available, timedelta())
        cursor = _next_staffed_start(
            day_end + timedelta(seconds=1),
            start_hour=start_hour,
            end_hour=end_hour,
            staffed_weekdays=staffed_weekdays,
        )
    return cursor.astimezone(UTC)


def resolution_from_observation(
    observation: dict[str, Any],
    *,
    disposition: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    inbound_at = parse_datetime(
        observation["latest_inbound_at"], "latest_inbound_at"
    )
    outbound_value = observation.get("latest_outbound_at")
    if outbound_value:
        outbound_at = parse_datetime(outbound_value, "latest_outbound_at")
        is_automated = observation.get("latest_outbound_is_automated")
        if outbound_at > inbound_at and is_automated is False:
            return {
                "code": "responded",
                "resolved_at": outbound_at.isoformat(),
                "evidence": {
                    "message_id": observation.get(
                        "latest_outbound_message_id"
                    ),
                    "source": "ghl_message",
                },
            }
    if not disposition:
        return None
    code = str(disposition.get("code") or "").strip()
    if code not in DISPOSITIONS or code == "responded":
        raise ValueError("disposition code is not approved")
    approved_by = str(disposition.get("approved_by") or "").strip()
    reason = str(disposition.get("reason") or "").strip()
    if not approved_by or not reason:
        raise ValueError("disposition requires approved_by and reason")
    if code == "delegated_to_owned_task":
        if not str(disposition.get("task_id") or "").strip():
            raise ValueError("delegated disposition requires task_id")
        if not str(disposition.get("task_owner_id") or "").strip():
            raise ValueError("delegated disposition requires task_owner_id")
    resolved_at = parse_datetime(
        disposition.get("approved_at"), "disposition approved_at"
    )
    return {
        "code": code,
        "resolved_at": resolved_at.isoformat(),
        "evidence": dict(disposition),
    }


def build_case(
    observation: dict[str, Any],
    *,
    observed_at: datetime,
    owner_role: str = "Admin Eve",
    owner_user_id: str | None = None,
    person_id: str | None = None,
    disposition: dict[str, Any] | None = None,
) -> dict[str, Any]:
    inbound_at = parse_datetime(
        observation["latest_inbound_at"], "latest_inbound_at"
    )
    classification = observation.get("classification") or {}
    category = normalise_category(classification.get("category"))
    resolution = resolution_from_observation(
        observation,
        disposition=disposition,
    )
    due_at = staffed_deadline(inbound_at, category)
    state = "resolved" if resolution else "open"
    if not resolution and observed_at > due_at:
        state = "overdue"
    cycle_key = case_cycle_key(observation)
    return {
        "case_id": stable_id("conversation_case", cycle_key),
        "cycle_key": cycle_key,
        "conversation_id": str(observation["conversation_id"]),
        "contact_id": str(observation.get("contact_id") or "") or None,
        "person_id": person_id,
        "latest_inbound_message_id": str(
            observation.get("latest_inbound_message_id") or ""
        )
        or None,
        "opened_at": inbound_at,
        "latest_inbound_at": inbound_at,
        "latest_outbound_at": (
            parse_datetime(
                observation["latest_outbound_at"], "latest_outbound_at"
            )
            if observation.get("latest_outbound_at")
            else None
        ),
        "category": category,
        "recommendation": str(
            classification.get("action") or "Review in GHL"
        ).strip(),
        "owner_role": owner_role,
        "owner_user_id": owner_user_id,
        "due_at": due_at,
        "state": state,
        "breached": state == "overdue",
        "classification_version": str(
            classification.get("version") or CLASSIFICATION_VERSION
        ),
        "channel": str(observation.get("channel") or "unknown"),
        "current_assignment": str(
            observation.get("current_assignment") or ""
        )
        or None,
        "excerpt": str(observation.get("latest_inbound_excerpt") or "")[:500]
        or None,
        "resolution_code": resolution["code"] if resolution else None,
        "resolution_at": (
            parse_datetime(resolution["resolved_at"], "resolved_at")
            if resolution
            else None
        ),
        "disposition": resolution["evidence"] if resolution else {},
        "rule_version": RULE_VERSION,
    }


def aggregate_cases(
    cases: Iterable[dict[str, Any]],
    *,
    now: datetime | None = None,
) -> dict[str, Any]:
    rows = [dict(row) for row in cases]
    observed_at = (now or datetime.now(UTC)).astimezone(UTC)
    open_rows = [row for row in rows if row.get("state") in OPEN_STATES]
    resolved_rows = [
        row for row in rows if row.get("state") in TERMINAL_STATES
    ]
    ages = []
    for row in open_rows:
        opened = row.get("opened_at")
        if isinstance(opened, str):
            opened = parse_datetime(opened, "opened_at")
        if isinstance(opened, datetime):
            ages.append(max(0.0, (observed_at - opened).total_seconds() / 3600))
    category_counts = {
        category: sum(row.get("category") == category for row in open_rows)
        for category in sorted(CATEGORIES)
    }
    return {
        "schema_version": 1,
        "definition_version": RULE_VERSION,
        "observed_at": observed_at.isoformat(),
        "opening_backlog": len(open_rows),
        "resolved_total": len(resolved_rows),
        "overdue": sum(row.get("state") == "overdue" for row in open_rows),
        "blocked": sum(row.get("state") == "blocked" for row in open_rows),
        "oldest_unresolved_hours": round(max(ages), 1) if ages else 0.0,
        "categories": category_counts,
    }


__all__ = [
    "CATEGORIES",
    "CLASSIFICATION_VERSION",
    "DEFAULT_SERVICE_MINUTES",
    "DISPOSITIONS",
    "OPEN_STATES",
    "RULE_VERSION",
    "aggregate_cases",
    "build_case",
    "case_cycle_key",
    "deterministic_category",
    "normalise_category",
    "resolution_from_observation",
    "staffed_deadline",
]
