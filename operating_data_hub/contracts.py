from __future__ import annotations

import hashlib
import json
import re
from datetime import date, datetime
from zoneinfo import ZoneInfo
from decimal import Decimal, InvalidOperation
from typing import Any

from .conversation_clearance import (
    CATEGORIES as CONVERSATION_CATEGORIES,
    CLASSIFICATION_VERSION as CONVERSATION_CLASSIFICATION_VERSION,
)


EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PT_MINDER_STATES = {
    "active",
    "collecting",
    "paused",
    "cancelled",
    "arrears",
    "failed",
    "paid_in_advance",
    "review_required",
}
PT_MINDER_TRANSACTION_STATUSES = {
    "completed",
    "failed",
    "pending",
    "refunded",
}
PT_MINDER_SERVICE_TYPES = {
    "sgpt",
    "personal_training",
    "fast_track",
    "other",
}
PT_MINDER_CADENCES = {
    "recurring",
    "ad_hoc",
    "other",
}
PAYMENT_SERVICE_OVERRIDE_SOURCES = {
    "pt_minder",
}
MEMBERSHIP_SERVICE_TYPES = {
    "sgpt",
    "personal_training",
    "fast_track",
    "online",
    "hybrid",
    "other",
}
SERVICE_CHANGE_EVENT_TYPES = {
    "requested",
    "accepted",
    "exception",
}
SERVICE_CHANGE_SURFACES = {
    "billing",
    "ghl",
    "trainerize",
    "appointments",
    "workbook",
    "reporting",
}
SERVICE_CHANGE_SURFACE_STATUSES = {
    "pending",
    "succeeded",
    "not_applicable",
    "exception",
}
COHORT_DISPOSITIONS = {
    "confirmed_active",
    "excluded",
    "revenue_review_only",
    "timing_difference",
    "decision_required",
}
COMMERCIAL_SOURCES = {
    "stripe",
    "stripe_pack",
    "pt_minder",
    "governed_manual",
    "revenue_control",
}
ROSTER_ALLOCATION_BASES = {
    "weekly_recurring",
    "prepaid",
    "unresolved",
}
ENTITLEMENT_STATUSES = {
    "confirmed",
    "pending",
    "paused",
    "expired",
    "not_entitled",
}
PAYMENT_ACCOUNT_STATUSES = {
    "active",
    "collecting",
    "paused",
    "cancelled",
    "paid_in_advance",
    "review_required",
}
SA_ATTENDANCE_STATUSES = {
    "confirmed",
    "showed",
    "no_show",
    "cancelled",
    "invalid",
    "unknown",
}
SA_DELIVERED_BY = {
    "Megan",
    "Piper",
    "Nora",
    "Katrina",
    "Leisa",
    "Approved cover / other",
    "Unrecorded - legacy form",
}
PT_TRANSACTION_PATTERN = re.compile(
    r"(?:\d+\s*x\s*pt\b|\bpt\b|personal training|"
    r"one[\s-]*on[\s-]*one|1\s*:\s*1|"
    r"\d+\s*x\s*\d+\s*min)",
    re.IGNORECASE,
)
MEMBERSHIP_TRANSACTION_PATTERN = re.compile(
    r"(?:membership|program|\bsgpt\b|evolved-anywhere|strong membership|"
    r"fit\s*(?:&|and)\s*flexible|fast track|"
    r"(?:bronze|silver|gold)\s+package)",
    re.IGNORECASE,
)
FAST_TRACK_TRANSACTION_PATTERN = re.compile(
    r"\bsilver\s+package\b",
    re.IGNORECASE,
)
RECURRING_TRANSACTION_PATTERN = re.compile(
    r"(?:weekly|fortnightly|recurring|membership|subscription|"
    r"program\s*-\s*from)",
    re.IGNORECASE,
)
PT_MINDER_PERIOD_PATTERN = re.compile(
    r"\bfrom\s+(\d{2}/\d{2}/\d{4})\s+to\s+"
    r"(\d{2}/\d{2}/\d{4})\b",
    re.IGNORECASE,
)


def canonical_json(payload: Any) -> str:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )


def fingerprint(payload: Any) -> str:
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def iso_datetime(value: Any, field: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{field} is required")
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).isoformat()
    except ValueError as exc:
        raise ValueError(f"{field} must be an ISO datetime") from exc


def optional_iso_date(value: Any, field: str) -> str | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return date.fromisoformat(text).isoformat()
    except ValueError as exc:
        raise ValueError(f"{field} must be an ISO date") from exc


def _optional_nonnegative_decimal(
    value: Any,
    field: str,
) -> str | None:
    if value in (None, ""):
        return None
    try:
        parsed = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError(f"{field} must be a decimal") from exc
    if parsed < 0 or parsed > Decimal("10000"):
        raise ValueError(f"{field} is out of range")
    return format(parsed, "f")


def classify_pt_minder_transaction(description: Any) -> dict[str, str]:
    text = " ".join(str(description or "").split())
    if PT_TRANSACTION_PATTERN.search(text):
        service_type = "personal_training"
    elif FAST_TRACK_TRANSACTION_PATTERN.search(text):
        service_type = "fast_track"
    elif MEMBERSHIP_TRANSACTION_PATTERN.search(text):
        service_type = "sgpt"
    else:
        service_type = "other"
    if RECURRING_TRANSACTION_PATTERN.search(text):
        cadence = "recurring"
    elif service_type == "personal_training":
        cadence = "ad_hoc"
    else:
        cadence = "other"
    return {
        "service_type": service_type,
        "cadence": cadence,
    }


def _validate_pt_minder_transactions(
    value: Any,
    *,
    row_position: int,
) -> list[dict[str, Any]]:
    if not isinstance(value, list) or len(value) > 500:
        raise ValueError(
            f"row {row_position} transactions must be a list "
            "with at most 500 entries"
        )
    cleaned: list[dict[str, Any]] = []
    seen: set[str] = set()
    for transaction_position, transaction in enumerate(value, start=1):
        label = f"row {row_position} transaction {transaction_position}"
        if not isinstance(transaction, dict):
            raise ValueError(f"{label} must be an object")
        source_transaction_id = str(
            transaction.get("source_transaction_id") or ""
        ).strip()
        if not source_transaction_id:
            raise ValueError(f"{label} requires source_transaction_id")
        if source_transaction_id in seen:
            raise ValueError(f"{label} duplicates source_transaction_id")
        seen.add(source_transaction_id)
        entry_type = str(
            transaction.get("entry_type") or "payment"
        ).strip().lower()
        if entry_type == "charge":
            continue
        if entry_type not in {"payment", "debit"}:
            raise ValueError(f"{label} has an invalid entry_type")
        description = " ".join(
            str(transaction.get("description") or "").split()
        )
        if not description:
            raise ValueError(f"{label} requires description")
        try:
            amount = Decimal(str(transaction.get("amount") or ""))
        except InvalidOperation as exc:
            raise ValueError(f"{label} has an invalid amount") from exc
        if amount <= 0 or amount > Decimal("10000"):
            raise ValueError(f"{label} amount is out of range")
        status = str(transaction.get("status") or "").strip().lower()
        if status not in PT_MINDER_TRANSACTION_STATUSES:
            raise ValueError(f"{label} has an invalid status")
        inferred = classify_pt_minder_transaction(description)
        source_classification = str(
            transaction.get("classification") or ""
        ).strip().lower()
        if source_classification == "inferred":
            supplied_service_type = inferred["service_type"]
            supplied_cadence = inferred["cadence"]
        else:
            supplied_service_type = str(
                transaction.get("service_type") or inferred["service_type"]
            ).strip().lower()
            supplied_cadence = str(
                transaction.get("cadence") or inferred["cadence"]
            ).strip().lower()
        if supplied_service_type not in PT_MINDER_SERVICE_TYPES:
            raise ValueError(f"{label} has an invalid service_type")
        if supplied_cadence not in PT_MINDER_CADENCES:
            raise ValueError(f"{label} has an invalid cadence")
        overridden = (
            supplied_service_type != inferred["service_type"]
            or supplied_cadence != inferred["cadence"]
        )
        if overridden and not str(
            transaction.get("classification_note") or ""
        ).strip():
            raise ValueError(
                f"{label} classification override requires classification_note"
            )
        occurred_on = optional_iso_date(
            transaction.get("occurred_on"),
            f"{label} occurred_on",
        )
        if not occurred_on:
            raise ValueError(f"{label} requires occurred_on")
        coverage_start = optional_iso_date(
            transaction.get("coverage_start"),
            f"{label} coverage_start",
        )
        coverage_end = optional_iso_date(
            transaction.get("coverage_end"),
            f"{label} coverage_end",
        )
        if not coverage_start and not coverage_end:
            period_match = PT_MINDER_PERIOD_PATTERN.search(description)
            if period_match:
                coverage_start = datetime.strptime(
                    period_match.group(1), "%d/%m/%Y"
                ).date().isoformat()
                coverage_end = datetime.strptime(
                    period_match.group(2), "%d/%m/%Y"
                ).date().isoformat()
        if bool(coverage_start) != bool(coverage_end):
            raise ValueError(
                f"{label} requires both coverage dates or neither"
            )
        if (
            coverage_start
            and coverage_end
            and coverage_start > coverage_end
        ):
            raise ValueError(
                f"{label} coverage_start cannot follow coverage_end"
            )
        cleaned.append(
            {
                "source_transaction_id": source_transaction_id,
                "entry_type": entry_type,
                "occurred_on": occurred_on,
                "description": description,
                "amount": f"{amount:.2f}",
                "status": status,
                "service_type": supplied_service_type,
                "cadence": supplied_cadence,
                "next_scheduled_payment": optional_iso_date(
                    transaction.get("next_scheduled_payment"),
                    f"{label} next_scheduled_payment",
                ),
                "coverage_start": coverage_start,
                "coverage_end": coverage_end,
                "classification": "explicit" if overridden else "inferred",
                "classification_note": " ".join(
                    str(transaction.get("classification_note") or "").split()
                )
                or None,
            }
        )
    return cleaned


def validate_pt_minder(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("payload must be an object")
    observed_at = iso_datetime(payload.get("observed_at"), "observed_at")
    rows = payload.get("rows")
    if not isinstance(rows, list) or len(rows) > 1000:
        raise ValueError("rows must be a list with at most 1000 entries")
    if not rows:
        raise ValueError("a complete PT Minder snapshot cannot be empty")
    transaction_detail_complete = (
        payload.get("transaction_detail_complete") is True
    )

    cleaned: list[dict[str, Any]] = []
    source_ids: set[str] = set()
    for position, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            raise ValueError(f"row {position} must be an object")
        source_id = str(row.get("source_account_id") or "").strip()
        if not source_id:
            raise ValueError(f"row {position} requires source_account_id")
        if source_id in source_ids:
            raise ValueError(f"duplicate source_account_id at row {position}")
        source_ids.add(source_id)
        email = str(row.get("email") or "").strip().lower()
        if email and not EMAIL.fullmatch(email):
            raise ValueError(f"row {position} has an invalid email")
        state = str(row.get("state") or "").strip().lower()
        if state not in PT_MINDER_STATES:
            raise ValueError(f"row {position} has an invalid state")
        amount = row.get("amount")
        if amount not in (None, ""):
            try:
                amount = Decimal(str(amount))
            except InvalidOperation as exc:
                raise ValueError(
                    f"row {position} has an invalid amount"
                ) from exc
            if amount < 0 or amount > Decimal("10000"):
                raise ValueError(f"row {position} amount is out of range")
            amount = f"{amount:.2f}"
        else:
            amount = None
        weekly_amount = row.get("weekly_amount")
        if weekly_amount not in (None, ""):
            try:
                weekly_amount = Decimal(str(weekly_amount))
            except InvalidOperation as exc:
                raise ValueError(
                    f"row {position} has an invalid weekly_amount"
                ) from exc
            if weekly_amount < 0 or weekly_amount > Decimal("10000"):
                raise ValueError(
                    f"row {position} weekly_amount is out of range"
                )
            weekly_amount = f"{weekly_amount:.2f}"
        else:
            weekly_amount = None
        transactions: list[dict[str, Any]] = []
        if transaction_detail_complete:
            if "transactions" not in row:
                raise ValueError(
                    f"row {position} requires transactions when "
                    "transaction_detail_complete is true"
                )
            transactions = _validate_pt_minder_transactions(
                row.get("transactions"),
                row_position=position,
            )
        cleaned.append(
            {
                "source_account_id": source_id,
                "email": email or None,
                "agreement_id": (
                    str(row.get("agreement_id") or "").strip() or None
                ),
                "product": str(row.get("product") or "").strip() or None,
                "state": state,
                "amount": amount,
                "weekly_amount": weekly_amount,
                "last_successful_payment": optional_iso_date(
                    row.get("last_successful_payment"),
                    "last_successful_payment",
                ),
                "next_scheduled_payment": optional_iso_date(
                    row.get("next_scheduled_payment"),
                    "next_scheduled_payment",
                ),
                "failed_payment_date": optional_iso_date(
                    row.get("failed_payment_date"),
                    "failed_payment_date",
                ),
                "transactions": transactions,
            }
        )
    return {
        "schema_version": 2 if transaction_detail_complete else 1,
        "source": "pt_minder",
        "observed_at": observed_at,
        "complete": True,
        "transaction_detail_complete": transaction_detail_complete,
        "rows": cleaned,
    }


def validate_payment_service_overrides(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("payload must be an object")
    observed_at = iso_datetime(payload.get("observed_at"), "observed_at")
    rows = payload.get("rows")
    if not isinstance(rows, list) or not rows or len(rows) > 1000:
        raise ValueError(
            "payment service override rows must contain 1 to 1000 entries"
        )

    cleaned: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for position, row in enumerate(rows, start=1):
        label = f"row {position}"
        if not isinstance(row, dict):
            raise ValueError(f"{label} must be an object")
        source = str(row.get("source") or "").strip().lower()
        if source not in PAYMENT_SERVICE_OVERRIDE_SOURCES:
            raise ValueError(f"{label} has an invalid source")
        source_account_id = str(
            row.get("source_account_id") or ""
        ).strip()
        agreement_id = str(row.get("agreement_id") or "").strip()
        if not source_account_id and not agreement_id:
            raise ValueError(
                f"{label} requires source_account_id or agreement_id"
            )
        key = (source, source_account_id, agreement_id)
        if key in seen:
            raise ValueError(f"{label} duplicates an override target")
        seen.add(key)
        service_type = str(
            row.get("service_type") or ""
        ).strip().lower()
        if service_type not in PT_MINDER_SERVICE_TYPES:
            raise ValueError(f"{label} has an invalid service_type")
        cadence = str(row.get("cadence") or "").strip().lower()
        if cadence not in PT_MINDER_CADENCES:
            raise ValueError(f"{label} has an invalid cadence")
        approved_by = " ".join(
            str(row.get("approved_by") or "").split()
        )
        reason = " ".join(str(row.get("reason") or "").split())
        if not approved_by:
            raise ValueError(f"{label} requires approved_by")
        if len(reason) < 20:
            raise ValueError(
                f"{label} requires a specific governance reason"
            )
        effective_from = optional_iso_date(
            row.get("effective_from"),
            f"{label} effective_from",
        )
        effective_to = optional_iso_date(
            row.get("effective_to"),
            f"{label} effective_to",
        )
        if (
            effective_from
            and effective_to
            and effective_from > effective_to
        ):
            raise ValueError(
                f"{label} effective_from cannot follow effective_to"
            )
        expected_weekly_amount = row.get("expected_weekly_amount")
        if expected_weekly_amount not in (None, ""):
            try:
                expected_weekly_amount = Decimal(
                    str(expected_weekly_amount)
                )
            except InvalidOperation as exc:
                raise ValueError(
                    f"{label} has an invalid expected_weekly_amount"
                ) from exc
            if (
                expected_weekly_amount <= 0
                or expected_weekly_amount > Decimal("10000")
            ):
                raise ValueError(
                    f"{label} expected_weekly_amount is out of range"
                )
            expected_weekly_amount = f"{expected_weekly_amount:.2f}"
        else:
            expected_weekly_amount = None
        cleaned.append(
            {
                "source": source,
                "source_account_id": source_account_id or None,
                "agreement_id": agreement_id or None,
                "service_type": service_type,
                "cadence": cadence,
                "expected_weekly_amount": expected_weekly_amount,
                "effective_from": effective_from,
                "effective_to": effective_to,
                "approved_by": approved_by,
                "reason": reason,
                "active": row.get("active") is not False,
            }
        )
    return {
        "schema_version": 1,
        "source": "payment_service_overrides",
        "observed_at": observed_at,
        "status": "complete",
        "complete": True,
        "rows": cleaned,
    }


def validate_summary(source: str, payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("payload must be an object")
    observed_at = iso_datetime(payload.get("observed_at"), "observed_at")
    status = str(payload.get("status") or "").strip().lower()
    if status not in {"complete", "healthy", "failed", "partial"}:
        raise ValueError("status must be complete, healthy, partial or failed")
    summary = payload.get("summary")
    if not isinstance(summary, dict):
        raise ValueError("summary must be an object")
    return {
        "schema_version": int(payload.get("schema_version") or 1),
        "source": source,
        "observed_at": observed_at,
        "status": status,
        "complete": status in {"complete", "healthy"},
        "summary": summary,
    }


def validate_conversation_clearance(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("payload must be an object")
    observed_at = iso_datetime(payload.get("observed_at"), "observed_at")
    source_run_id = str(payload.get("source_run_id") or "").strip()
    if not source_run_id:
        raise ValueError("source_run_id is required")
    status = str(payload.get("status") or "").strip().lower()
    if status not in {"complete", "partial", "failed"}:
        raise ValueError("status must be complete, partial or failed")
    complete = bool(payload.get("complete"))
    if complete != (status == "complete"):
        raise ValueError("complete must match status")
    pages = int(payload.get("pages") or 0)
    if status != "failed" and pages < 1:
        raise ValueError("successful extraction requires at least one page")
    rows = payload.get("rows") or []
    if not isinstance(rows, list):
        raise ValueError("rows must be an array")
    if status == "failed" and rows:
        raise ValueError("failed extraction cannot contain rows")
    cleaned: list[dict[str, Any]] = []
    seen_conversations: set[str] = set()
    for index, source in enumerate(rows):
        if not isinstance(source, dict):
            raise ValueError(f"rows[{index}] must be an object")
        conversation_id = str(source.get("conversation_id") or "").strip()
        if not conversation_id:
            raise ValueError(f"rows[{index}] requires conversation_id")
        if conversation_id in seen_conversations:
            raise ValueError("conversation_id must be unique within a run")
        seen_conversations.add(conversation_id)
        latest_inbound_at = iso_datetime(
            source.get("latest_inbound_at"),
            f"rows[{index}].latest_inbound_at",
        )
        latest_outbound_at = None
        if source.get("latest_outbound_at"):
            latest_outbound_at = iso_datetime(
                source.get("latest_outbound_at"),
                f"rows[{index}].latest_outbound_at",
            )
        classification = source.get("classification") or {}
        if not isinstance(classification, dict):
            raise ValueError(f"rows[{index}].classification must be an object")
        category = str(
            classification.get("category") or "manual_review"
        ).strip().lower()
        if category not in CONVERSATION_CATEGORIES:
            category = "manual_review"
        action = str(
            classification.get("action") or "Review in GHL"
        ).strip()
        cleaned.append(
            {
                "conversation_id": conversation_id,
                "contact_id": str(source.get("contact_id") or "").strip()
                or None,
                "channel": str(source.get("channel") or "unknown").strip(),
                "current_assignment": str(
                    source.get("current_assignment") or ""
                ).strip()
                or None,
                "unread": bool(source.get("unread", True)),
                "contact_name": str(source.get("contact_name") or "").strip()
                or None,
                "latest_inbound_message_id": str(
                    source.get("latest_inbound_message_id") or ""
                ).strip()
                or None,
                "latest_inbound_at": latest_inbound_at,
                "latest_inbound_excerpt": str(
                    source.get("latest_inbound_excerpt") or ""
                )[:500],
                "latest_outbound_message_id": str(
                    source.get("latest_outbound_message_id") or ""
                ).strip()
                or None,
                "latest_outbound_at": latest_outbound_at,
                "latest_outbound_is_automated": (
                    bool(source.get("latest_outbound_is_automated"))
                    if source.get("latest_outbound_is_automated") is not None
                    else None
                ),
                "message_history_complete": bool(
                    source.get("message_history_complete")
                ),
                "classification": {
                    "category": category,
                    "action": action,
                    "source": str(
                        classification.get("source") or "fallback"
                    ).strip(),
                    "version": str(
                        classification.get("version")
                        or CONVERSATION_CLASSIFICATION_VERSION
                    ).strip(),
                },
                "identity": {
                    "is_sa_prequalification": bool(
                        (source.get("identity") or {}).get(
                            "is_sa_prequalification"
                        )
                    ),
                    "identity_review_required": bool(
                        (source.get("identity") or {}).get(
                            "identity_review_required"
                        )
                    ),
                },
            }
        )
    return {
        "schema_version": int(payload.get("schema_version") or 1),
        "source": "conversation_clearance",
        "source_run_id": source_run_id,
        "observed_at": observed_at,
        "status": status,
        "complete": complete,
        "pages": pages,
        "expected_total": (
            int(payload["expected_total"])
            if payload.get("expected_total") is not None
            else None
        ),
        "error_code": str(payload.get("error_code") or "").strip() or None,
        "rows": cleaned,
    }


def validate_sa_attendance(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("payload must be an object")
    observed_at = iso_datetime(payload.get("observed_at"), "observed_at")
    source_run_id = str(payload.get("source_run_id") or "").strip()
    if not source_run_id:
        raise ValueError("source_run_id is required")
    requested = [
        str(item).strip()
        for item in (payload.get("calendar_ids_requested") or [])
        if str(item).strip()
    ]
    completed = [
        str(item).strip()
        for item in (payload.get("calendar_ids_completed") or [])
        if str(item).strip()
    ]
    complete = bool(payload.get("complete"))
    if not requested:
        raise ValueError("calendar_ids_requested cannot be empty")
    if complete and set(requested) != set(completed):
        raise ValueError("complete source run must cover every requested calendar")
    rows = payload.get("rows")
    if not isinstance(rows, list) or len(rows) > 10000:
        raise ValueError("rows must be a list with at most 10000 entries")
    cleaned: list[dict[str, Any]] = []
    seen: set[str] = set()
    for position, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            raise ValueError(f"row {position} must be an object")
        appointment_id = str(row.get("appointment_id") or "").strip()
        contact_id = str(row.get("contact_id") or "").strip()
        calendar_id = str(row.get("calendar_id") or "").strip()
        if not appointment_id or not contact_id or not calendar_id:
            raise ValueError(
                f"row {position} requires appointment, contact and calendar IDs"
            )
        if appointment_id in seen:
            raise ValueError(f"row {position} duplicates appointment_id")
        seen.add(appointment_id)
        if calendar_id not in requested:
            raise ValueError(f"row {position} uses an unapproved calendar")
        status = str(row.get("status") or "").strip().lower()
        if status not in SA_ATTENDANCE_STATUSES:
            raise ValueError(f"row {position} has an invalid status")
        start_at = iso_datetime(row.get("start_at"), f"row {position} start_at")
        end_at = iso_datetime(row.get("end_at"), f"row {position} end_at")
        if datetime.fromisoformat(end_at) <= datetime.fromisoformat(start_at):
            raise ValueError(f"row {position} end_at must follow start_at")
        cleaned.append(
            {
                "appointment_id": appointment_id,
                "contact_id": contact_id,
                "calendar_id": calendar_id,
                "booked_at": (
                    iso_datetime(
                        row.get("booked_at"),
                        f"row {position} booked_at",
                    )
                    if row.get("booked_at")
                    else None
                ),
                "start_at": start_at,
                "end_at": end_at,
                "status": status,
                "assigned_user_id": str(
                    row.get("assigned_user_id") or ""
                ).strip()
                or None,
                "updated_at": (
                    iso_datetime(
                        row.get("updated_at"),
                        f"row {position} updated_at",
                    )
                    if row.get("updated_at")
                    else None
                ),
                "deleted": bool(row.get("deleted", False)),
                "observed_at": iso_datetime(
                    row.get("observed_at") or observed_at,
                    f"row {position} observed_at",
                ),
            }
        )
    return {
        "schema_version": int(payload.get("schema_version") or 1),
        "source": "strength_assessment_attendance",
        "source_run_id": source_run_id,
        "observed_at": observed_at,
        "status": "complete" if complete else "partial",
        "complete": complete,
        "calendar_ids_requested": requested,
        "calendar_ids_completed": completed,
        "coverage_start": (
            iso_datetime(payload.get("coverage_start"), "coverage_start")
            if payload.get("coverage_start")
            else None
        ),
        "coverage_end": (
            iso_datetime(payload.get("coverage_end"), "coverage_end")
            if payload.get("coverage_end")
            else None
        ),
        "rows": cleaned,
    }


def validate_sa_feedback(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("payload must be an object")
    contact_id = str(payload.get("contact_id") or "").strip()
    submission_id = str(payload.get("form_submission_id") or "").strip()
    delivered_by = str(payload.get("delivered_by") or "").strip()
    if not contact_id:
        raise ValueError("contact_id is required")
    if not submission_id:
        raise ValueError("form_submission_id is required")
    if delivered_by not in SA_DELIVERED_BY:
        raise ValueError("delivered_by is not in the canonical roster")
    submitted_at = iso_datetime(payload.get("submitted_at"), "submitted_at")
    delivery_key = str(payload.get("delivery_key") or "").strip()
    if not delivery_key:
        raise ValueError("delivery_key is required")
    if len(delivery_key) > 160:
        raise ValueError("delivery_key is too long")
    sales_outcome = str(payload.get("sales_outcome") or "").strip()
    if sales_outcome and sales_outcome not in {"Sale", "No Sale"}:
        raise ValueError("sales_outcome must be Sale or No Sale")
    return {
        "schema_version": 1,
        "contact_id": contact_id,
        "form_submission_id": submission_id,
        "submitted_at": submitted_at,
        "sales_outcome": sales_outcome or None,
        "delivered_by": delivered_by,
        "workflow_execution_id": str(
            payload.get("workflow_execution_id") or ""
        ).strip()
        or None,
        "delivery_key": delivery_key,
    }


def validate_membership_reconciliation(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("payload must be an object")
    observed_at = iso_datetime(payload.get("observed_at"), "observed_at")
    source_run_id = str(payload.get("source_run_id") or "").strip()
    if not source_run_id:
        raise ValueError("source_run_id is required")
    rows = payload.get("rows")
    if not isinstance(rows, list) or len(rows) > 5000:
        raise ValueError("rows must be a list with at most 5000 entries")
    if not rows:
        raise ValueError("membership reconciliation rows cannot be empty")

    cleaned: list[dict[str, Any]] = []
    seen: set[str] = set()
    for position, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            raise ValueError(f"row {position} must be an object")
        canonical_key = str(row.get("canonical_key") or "").strip().lower()
        email = str(row.get("email") or "").strip().lower()
        if not canonical_key:
            raise ValueError(f"row {position} requires canonical_key")
        if canonical_key in seen:
            raise ValueError(f"row {position} duplicates canonical_key")
        seen.add(canonical_key)
        if email and not EMAIL.fullmatch(email):
            raise ValueError(f"row {position} has an invalid email")

        source_ids = row.get("source_ids") or {}
        if not isinstance(source_ids, dict):
            raise ValueError(f"row {position} source_ids must be an object")
        cleaned_source_ids: dict[str, list[str]] = {}
        for source in ("ghl", "stripe", "trainerize"):
            raw_ids = source_ids.get(source) or []
            if not isinstance(raw_ids, list) or len(raw_ids) > 100:
                raise ValueError(
                    f"row {position} {source} source IDs must be a list"
                )
            cleaned_source_ids[source] = sorted(
                {
                    str(item).strip()
                    for item in raw_ids
                    if str(item).strip()
                }
            )

        raw_services = row.get("services")
        if raw_services is None:
            raw_services = [
                {
                    "service_type": row.get("service_type") or "other",
                    "service_name": row.get("service_name"),
                }
            ]
        if not isinstance(raw_services, list) or not raw_services:
            raise ValueError(f"row {position} services must be a non-empty list")
        if len(raw_services) > 10:
            raise ValueError(f"row {position} has too many services")
        services: list[dict[str, str | None]] = []
        seen_services: set[tuple[str, str]] = set()
        for service in raw_services:
            if not isinstance(service, dict):
                raise ValueError(
                    f"row {position} service must be an object"
                )
            service_type = str(
                service.get("service_type") or "other"
            ).strip().lower()
            if service_type not in MEMBERSHIP_SERVICE_TYPES:
                raise ValueError(
                    f"row {position} has an invalid service_type"
                )
            service_name = (
                str(service.get("service_name") or "").strip() or None
            )
            key = (service_type, (service_name or "").lower())
            if key in seen_services:
                continue
            seen_services.add(key)
            services.append(
                {
                    "service_type": service_type,
                    "service_name": service_name,
                }
            )
        lifecycle_status = str(
            row.get("lifecycle_status") or "review_required"
        ).strip().lower()
        if lifecycle_status not in {
            "active",
            "paused",
            "cancelling",
            "cancelled",
            "inactive",
            "review_required",
        }:
            raise ValueError(
                f"row {position} has an invalid lifecycle_status"
            )

        active_signal = bool(
            row.get("ghl_active")
            or row.get("stripe_entitled")
            or row.get("trainerize_active")
        )
        if (
            "active_signal" in row
            and bool(row.get("active_signal")) != active_signal
        ):
            raise ValueError(
                f"row {position} active_signal conflicts with source evidence"
            )
        cleaned.append(
            {
                "canonical_key": canonical_key,
                "email": email or None,
                "first_name": (
                    str(row.get("first_name") or "").strip() or None
                ),
                "last_name": (
                    str(row.get("last_name") or "").strip() or None
                ),
                "source_ids": cleaned_source_ids,
                "service_type": services[0]["service_type"],
                "service_name": services[0]["service_name"],
                "services": services,
                "lifecycle_status": lifecycle_status,
                "active_signal": active_signal,
                "ghl_active": bool(row.get("ghl_active")),
                "stripe_entitled": bool(row.get("stripe_entitled")),
                "trainerize_active": bool(row.get("trainerize_active")),
                "pt_block_trainer": (
                    str(row.get("pt_block_trainer") or "").strip()
                    or None
                ),
                "cancellation_status": (
                    str(row.get("cancellation_status") or "").strip()
                    or None
                ),
                "cancellation_type": (
                    str(row.get("cancellation_type") or "").strip()
                    or None
                ),
                "notice_end_date": optional_iso_date(
                    row.get("notice_end_date"),
                    f"row {position} notice_end_date",
                ),
                "final_access_date": optional_iso_date(
                    row.get("final_access_date"),
                    f"row {position} final_access_date",
                ),
                "hold_status": (
                    str(row.get("hold_status") or "").strip() or None
                ),
                "hold_type": (
                    str(row.get("hold_type") or "").strip() or None
                ),
                "hold_start_date": optional_iso_date(
                    row.get("hold_start_date"),
                    f"row {position} hold_start_date",
                ),
                "hold_end_date": optional_iso_date(
                    row.get("hold_end_date"),
                    f"row {position} hold_end_date",
                ),
                "classification": (
                    str(row.get("classification") or "").strip() or None
                ),
            }
        )
    return {
        "schema_version": int(payload.get("schema_version") or 1),
        "source": "membership_reconciliation",
        "source_run_id": source_run_id,
        "observed_at": observed_at,
        "status": "complete",
        "complete": True,
        "rows": cleaned,
    }


def _validate_service_change_services(
    value: Any,
    *,
    field: str,
) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value or len(value) > 10:
        raise ValueError(f"{field} must contain 1 to 10 services")
    cleaned: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for position, item in enumerate(value, start=1):
        label = f"{field} item {position}"
        if not isinstance(item, dict):
            raise ValueError(f"{label} must be an object")
        service_type = str(item.get("service_type") or "").strip().lower()
        if service_type not in MEMBERSHIP_SERVICE_TYPES:
            raise ValueError(f"{label} has an invalid service_type")
        service_name = " ".join(
            str(item.get("service_name") or "").split()
        )
        if not service_name:
            raise ValueError(f"{label} requires service_name")
        key = (service_type, service_name.lower())
        if key in seen:
            raise ValueError(f"{field} contains a duplicate service")
        seen.add(key)
        weekly_price_cents = item.get("weekly_price_cents")
        if weekly_price_cents not in (None, ""):
            try:
                weekly_price_cents = int(weekly_price_cents)
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"{label} weekly_price_cents must be an integer"
                ) from exc
            if weekly_price_cents < 0 or weekly_price_cents > 1_000_000:
                raise ValueError(
                    f"{label} weekly_price_cents is out of range"
                )
        else:
            weekly_price_cents = None
        cleaned.append(
            {
                "service_type": service_type,
                "service_name": service_name,
                "weekly_price_cents": weekly_price_cents,
                "quantity": (
                    " ".join(str(item.get("quantity") or "").split())
                    or None
                ),
                "unit": (
                    " ".join(str(item.get("unit") or "").split())
                    or None
                ),
            }
        )
    return cleaned


def validate_service_change_event(payload: Any) -> dict[str, Any]:
    """Validate one immutable membership service-change event.

    A requested event records the signed decision without changing current
    service. An accepted event is allowed only after every required surface
    has either succeeded or is explicitly not applicable.
    """
    if not isinstance(payload, dict):
        raise ValueError("payload must be an object")
    event_type = str(payload.get("event_type") or "").strip().lower()
    if event_type not in SERVICE_CHANGE_EVENT_TYPES:
        raise ValueError("event_type must be requested, accepted or exception")
    request_id = str(payload.get("request_id") or "").strip()
    if not request_id or len(request_id) > 160:
        raise ValueError("request_id is required and must be at most 160 characters")
    event_version = payload.get("event_version")
    try:
        event_version = int(event_version)
    except (TypeError, ValueError) as exc:
        raise ValueError("event_version must be an integer") from exc
    if event_version < 1:
        raise ValueError("event_version must be positive")
    if event_type == "requested" and event_version != 1:
        raise ValueError("requested events require event_version 1")
    if event_type in {"accepted", "exception"} and event_version < 2:
        raise ValueError(
            f"{event_type} events require event_version 2 or greater"
        )
    canonical_key = str(payload.get("canonical_key") or "").strip().lower()
    if not canonical_key:
        raise ValueError("canonical_key is required")
    email = str(payload.get("email") or "").strip().lower()
    if email and not EMAIL.fullmatch(email):
        raise ValueError("email is invalid")
    contact_id = str(payload.get("contact_id") or "").strip()
    if not contact_id:
        raise ValueError("contact_id is required")
    occurred_at = iso_datetime(payload.get("occurred_at"), "occurred_at")
    request_date = optional_iso_date(payload.get("request_date"), "request_date")
    effective_date = optional_iso_date(
        payload.get("effective_date"),
        "effective_date",
    )
    if not request_date or not effective_date:
        raise ValueError("request_date and effective_date are required")
    if effective_date < request_date:
        raise ValueError("effective_date cannot precede request_date")
    effective_at = (
        iso_datetime(payload.get("effective_at"), "effective_at")
        if payload.get("effective_at")
        else f"{effective_date}T00:00:00+10:00"
    )
    effective_at_date = datetime.fromisoformat(
        effective_at.replace("Z", "+00:00")
    ).astimezone(ZoneInfo("Australia/Brisbane")).date().isoformat()
    if effective_at_date != effective_date:
        raise ValueError(
            "effective_at must fall on effective_date in Australia/Brisbane"
        )
    offer_version = str(payload.get("offer_version") or "").strip()
    agreement_version = str(payload.get("agreement_version") or "").strip()
    if not offer_version or not agreement_version:
        raise ValueError("offer_version and agreement_version are required")
    signed_at = iso_datetime(payload.get("signed_at"), "signed_at")
    signature_document = str(
        payload.get("signature_document") or ""
    ).strip()
    if not signature_document:
        raise ValueError("signature_document is required")
    prior_services = _validate_service_change_services(
        payload.get("prior_services"),
        field="prior_services",
    )
    requested_services = _validate_service_change_services(
        payload.get("requested_services"),
        field="requested_services",
    )
    if prior_services == requested_services:
        raise ValueError("requested_services must differ from prior_services")

    raw_surfaces = payload.get("surface_statuses") or {}
    if not isinstance(raw_surfaces, dict):
        raise ValueError("surface_statuses must be an object")
    unknown_surfaces = set(raw_surfaces) - SERVICE_CHANGE_SURFACES
    if unknown_surfaces:
        raise ValueError(
            "surface_statuses contains unknown surfaces: "
            + ", ".join(sorted(unknown_surfaces))
        )
    surface_statuses = {
        surface: str(raw_surfaces.get(surface) or "pending").strip().lower()
        for surface in sorted(SERVICE_CHANGE_SURFACES)
    }
    invalid = {
        surface: status
        for surface, status in surface_statuses.items()
        if status not in SERVICE_CHANGE_SURFACE_STATUSES
    }
    if invalid:
        raise ValueError("surface_statuses contains an invalid status")
    if event_type == "requested" and any(
        status not in {"pending", "not_applicable"}
        for status in surface_statuses.values()
    ):
        raise ValueError(
            "requested events may only use pending or not_applicable surfaces"
        )
    if event_type == "accepted" and any(
        status not in {"succeeded", "not_applicable"}
        for status in surface_statuses.values()
    ):
        raise ValueError(
            "accepted events require every surface to succeed or be not_applicable"
        )
    last_error = " ".join(str(payload.get("last_error") or "").split())
    if event_type == "exception" and not last_error:
        raise ValueError("exception events require last_error")
    if event_type != "exception" and last_error:
        raise ValueError("last_error is only valid for exception events")

    return {
        "schema_version": 1,
        "event_type": event_type,
        "event_version": event_version,
        "request_id": request_id,
        "canonical_key": canonical_key,
        "email": email or None,
        "contact_id": contact_id,
        "occurred_at": occurred_at,
        "request_date": request_date,
        "effective_date": effective_date,
        "effective_at": effective_at,
        "offer_version": offer_version,
        "agreement_version": agreement_version,
        "signed_at": signed_at,
        "signature_document": signature_document,
        "prior_services": prior_services,
        "requested_services": requested_services,
        "surface_statuses": surface_statuses,
        "source_workflow_id": (
            str(payload.get("source_workflow_id") or "").strip() or None
        ),
        "source_submission_id": (
            str(payload.get("source_submission_id") or "").strip() or None
        ),
        "approved_by": (
            " ".join(str(payload.get("approved_by") or "").split()) or None
        ),
        "last_error": last_error or None,
    }


def validate_active_client_cohort(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("payload must be an object")
    observed_at = iso_datetime(payload.get("observed_at"), "observed_at")
    as_of_date = optional_iso_date(payload.get("as_of_date"), "as_of_date")
    if not as_of_date:
        raise ValueError("as_of_date is required")
    rule_version = str(payload.get("rule_version") or "").strip()
    if not rule_version:
        raise ValueError("rule_version is required")
    source_refs = payload.get("source_refs")
    if not isinstance(source_refs, dict) or not source_refs:
        raise ValueError("source_refs must identify the compared snapshots")
    rows = payload.get("rows")
    if not isinstance(rows, list) or not rows or len(rows) > 5000:
        raise ValueError("rows must be a non-empty list with at most 5000 entries")

    cleaned = []
    seen: set[str] = set()
    for position, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            raise ValueError(f"row {position} must be an object")
        canonical_key = str(row.get("canonical_key") or "").strip().lower()
        if not canonical_key or canonical_key in seen:
            raise ValueError(
                f"row {position} requires a unique canonical_key"
            )
        seen.add(canonical_key)
        disposition = str(row.get("disposition") or "").strip().lower()
        if disposition not in COHORT_DISPOSITIONS:
            raise ValueError(f"row {position} has an invalid disposition")
        in_legacy = bool(row.get("in_legacy_cohort"))
        confirmed = bool(row.get("confirmed_active"))
        decision_required = bool(row.get("decision_required"))
        if confirmed != (disposition == "confirmed_active"):
            raise ValueError(
                f"row {position} confirmed_active conflicts with disposition"
            )
        if decision_required != (disposition == "decision_required"):
            raise ValueError(
                f"row {position} decision_required conflicts with disposition"
            )
        if not in_legacy and not confirmed:
            raise ValueError(
                f"row {position} is outside both compared cohorts"
            )
        paid = row.get("paid_or_entitled")
        if paid not in (True, False, None):
            raise ValueError(
                f"row {position} paid_or_entitled must be true, false or null"
            )
        reason = str(row.get("primary_reason") or "").strip()
        if not reason:
            raise ValueError(f"row {position} requires primary_reason")
        evidence = row.get("evidence")
        if not isinstance(evidence, dict) or not evidence:
            raise ValueError(f"row {position} requires evidence")
        evidence = dict(evidence)
        governed_roster = evidence.get("governed_roster")
        if governed_roster is not None:
            if not isinstance(governed_roster, list) or len(
                governed_roster
            ) > 10:
                raise ValueError(
                    f"row {position} governed_roster must be a list"
                )
            cleaned_roster = []
            for service_position, service in enumerate(
                governed_roster,
                start=1,
            ):
                label = (
                    f"row {position} governed service {service_position}"
                )
                if not isinstance(service, dict):
                    raise ValueError(f"{label} must be an object")
                service_type = str(
                    service.get("service") or ""
                ).strip().upper()
                if service_type not in {"SGPT", "PT"}:
                    raise ValueError(f"{label} has an invalid service")
                status = " ".join(
                    str(service.get("status") or "").split()
                )
                if status.lower() not in {"active", "active - pia"}:
                    raise ValueError(f"{label} has an invalid status")
                cleaned_roster.append(
                    {
                        "service": service_type,
                        "status": status,
                        "classification": " ".join(
                            str(
                                service.get("classification") or ""
                            ).split()
                        )
                        or None,
                        "product": " ".join(
                            str(service.get("product") or "").split()
                        )
                        or None,
                        "assigned_trainer": (
                            " ".join(
                                str(
                                    service.get("assigned_trainer") or ""
                                ).split()
                            )
                            or None
                        ),
                        "contracted_weekly_frequency": (
                            " ".join(
                                str(
                                    service.get(
                                        "contracted_weekly_frequency"
                                    )
                                    or ""
                                ).split()
                            )
                            or None
                        ),
                        "service_duration": (
                            " ".join(
                                str(
                                    service.get("service_duration") or ""
                                ).split()
                            )
                            or None
                        ),
                        "weekly_allocation": _optional_nonnegative_decimal(
                            service.get("weekly_allocation"),
                            f"{label} weekly_allocation",
                        ),
                        "allocation_currency": (
                            str(
                                service.get("allocation_currency") or ""
                            ).strip().upper()
                            or None
                        ),
                        "contract_length": (
                            " ".join(
                                str(
                                    service.get("contract_length") or ""
                                ).split()
                            )
                            or None
                        ),
                        "effective_to": optional_iso_date(
                            service.get("effective_to"),
                            f"{label} effective_to",
                        ),
                        "payment_marker": (
                            " ".join(
                                str(
                                    service.get("payment_marker") or ""
                                ).split()
                            )
                            or None
                        ),
                        "allocation_basis": (
                            str(
                                service.get("allocation_basis")
                                or "unresolved"
                            ).strip().lower()
                        ),
                    }
                )
                cleaned_service = cleaned_roster[-1]
                currency = cleaned_service["allocation_currency"]
                allocation = cleaned_service["weekly_allocation"]
                if currency not in {None, "AUD"}:
                    raise ValueError(
                        f"{label} allocation_currency must be AUD"
                    )
                if allocation is not None and currency != "AUD":
                    raise ValueError(
                        f"{label} requires AUD allocation_currency"
                    )
                allocation_basis = cleaned_service["allocation_basis"]
                if allocation_basis not in ROSTER_ALLOCATION_BASES:
                    raise ValueError(
                        f"{label} has an invalid allocation_basis"
                    )
                if (
                    allocation_basis == "weekly_recurring"
                    and allocation is None
                ):
                    raise ValueError(
                        f"{label} weekly_recurring requires "
                        "weekly_allocation"
                    )
            evidence["governed_roster"] = cleaned_roster
        cleaned.append(
            {
                "canonical_key": canonical_key,
                "in_legacy_cohort": in_legacy,
                "active_signal": bool(row.get("active_signal")),
                "confirmed_active": confirmed,
                "paid_or_entitled": paid,
                "disposition": disposition,
                "primary_reason": reason,
                "decision_required": decision_required,
                "owner": str(row.get("owner") or "").strip() or None,
                "owner_question": (
                    str(row.get("owner_question") or "").strip() or None
                ),
                "evidence": evidence,
            }
        )
    return {
        "schema_version": 1,
        "source": "active_client_cohort",
        "observed_at": observed_at,
        "as_of_date": as_of_date,
        "rule_version": rule_version,
        "status": "complete",
        "complete": True,
        "source_refs": source_refs,
        "rows": cleaned,
    }


def validate_active_roster_candidate(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("payload must be an object")
    observed_at = iso_datetime(payload.get("observed_at"), "observed_at")
    as_of_date = optional_iso_date(payload.get("as_of_date"), "as_of_date")
    if not as_of_date:
        raise ValueError("as_of_date is required")
    if str(payload.get("source_system") or "").strip() != "google_sheet":
        raise ValueError("source_system must be google_sheet")
    source_run_id = str(payload.get("source_run_id") or "").strip()
    if not source_run_id:
        raise ValueError("source_run_id is required")
    rows = payload.get("rows")
    if not isinstance(rows, list) or not rows or len(rows) > 1000:
        raise ValueError("rows must be a non-empty list with at most 1000 entries")

    cleaned = []
    seen: set[str] = set()
    for position, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            raise ValueError(f"row {position} must be an object")
        canonical_key = str(row.get("canonical_key") or "").strip().lower()
        if not canonical_key or canonical_key in seen:
            raise ValueError(
                f"row {position} requires a unique canonical_key"
            )
        seen.add(canonical_key)
        services = row.get("services")
        if not isinstance(services, list) or not services or len(services) > 2:
            raise ValueError(f"row {position} requires one or two services")
        cleaned_services = []
        service_types: set[str] = set()
        for service_position, service in enumerate(services, start=1):
            label = f"row {position} service {service_position}"
            if not isinstance(service, dict):
                raise ValueError(f"{label} must be an object")
            service_type = str(
                service.get("service_type") or ""
            ).strip().upper()
            if service_type not in {"SGPT", "PT"}:
                raise ValueError(f"{label} has an invalid service_type")
            if service_type in service_types:
                raise ValueError(f"row {position} duplicates a service_type")
            service_types.add(service_type)
            status = " ".join(str(service.get("status") or "").split())
            if (
                service_type == "SGPT"
                and status.lower() not in {"active", "active - pia"}
            ):
                raise ValueError(f"{label} has an invalid active status")
            cleaned_services.append(
                {
                    "service_type": service_type,
                    "status": status or "Active",
                    "classification": (
                        " ".join(
                            str(service.get("classification") or "").split()
                        )
                        or None
                    ),
                    "product": (
                        " ".join(str(service.get("product") or "").split())
                        or None
                    ),
                    "source_row": int(service.get("source_row") or 0),
                    "assigned_trainer": (
                        " ".join(
                            str(service.get("assigned_trainer") or "").split()
                        )
                        or None
                    ),
                    "contracted_weekly_frequency": (
                        " ".join(
                            str(
                                service.get(
                                    "contracted_weekly_frequency"
                                )
                                or ""
                            ).split()
                        )
                        or None
                    ),
                    "service_duration": (
                        " ".join(
                            str(service.get("service_duration") or "").split()
                        )
                        or None
                    ),
                    "weekly_allocation": _optional_nonnegative_decimal(
                        service.get("weekly_allocation"),
                        f"{label} weekly_allocation",
                    ),
                    "allocation_currency": (
                        str(
                            service.get("allocation_currency") or ""
                        ).strip().upper()
                        or None
                    ),
                    "contract_length": (
                        " ".join(
                            str(service.get("contract_length") or "").split()
                        )
                        or None
                    ),
                    "effective_to": optional_iso_date(
                        service.get("effective_to"),
                        f"{label} effective_to",
                    ),
                    "payment_marker": (
                        " ".join(
                            str(
                                service.get("payment_marker") or ""
                            ).split()
                        )
                        or None
                    ),
                    "allocation_basis": (
                        str(
                            service.get("allocation_basis")
                            or "unresolved"
                        ).strip().lower()
                    ),
                }
            )
            cleaned_service = cleaned_services[-1]
            currency = cleaned_service["allocation_currency"]
            allocation = cleaned_service["weekly_allocation"]
            if currency not in {None, "AUD"}:
                raise ValueError(
                    f"{label} allocation_currency must be AUD"
                )
            if allocation is not None and currency != "AUD":
                raise ValueError(
                    f"{label} requires AUD allocation_currency"
                )
            allocation_basis = cleaned_service["allocation_basis"]
            if allocation_basis not in ROSTER_ALLOCATION_BASES:
                raise ValueError(
                    f"{label} has an invalid allocation_basis"
                )
            if (
                allocation_basis == "weekly_recurring"
                and allocation is None
            ):
                raise ValueError(
                    f"{label} weekly_recurring requires weekly_allocation"
                )
        cleaned.append(
            {
                "canonical_key": canonical_key,
                "services": cleaned_services,
            }
        )
    return {
        "schema_version": 2,
        "source": "active_roster_candidate",
        "source_system": "google_sheet",
        "source_run_id": source_run_id,
        "observed_at": observed_at,
        "as_of_date": as_of_date,
        "status": "complete",
        "complete": True,
        "rows": cleaned,
    }


def validate_commercial_evidence(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("payload must be an object")
    observed_at = iso_datetime(payload.get("observed_at"), "observed_at")
    source_system = str(
        payload.get("source_system") or ""
    ).strip().lower()
    if source_system not in COMMERCIAL_SOURCES:
        raise ValueError("source_system is not registered")
    source_run_id = str(payload.get("source_run_id") or "").strip()
    if not source_run_id:
        raise ValueError("source_run_id is required")
    rows = payload.get("rows")
    if not isinstance(rows, list) or len(rows) > 5000:
        raise ValueError(
            "rows must be a list with at most 5000 entries"
        )
    cleaned_rows = []
    seen_people: set[str] = set()
    seen_accounts: set[str] = set()
    seen_events: set[str] = set()
    seen_entitlements: set[str] = set()
    for position, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            raise ValueError(f"row {position} must be an object")
        canonical_key = str(
            row.get("canonical_key") or ""
        ).strip().lower()
        if not canonical_key or canonical_key in seen_people:
            raise ValueError(
                f"row {position} requires a unique canonical_key"
            )
        seen_people.add(canonical_key)
        email = str(row.get("email") or "").strip().lower()
        if email and not EMAIL.fullmatch(email):
            raise ValueError(f"row {position} has an invalid email")
        source_identity_ids = sorted(
            {
                str(value).strip()
                for value in row.get("source_identity_ids") or []
                if str(value).strip()
            }
        )
        entitlements_clean = []
        for item_position, item in enumerate(
            row.get("entitlements") or [],
            start=1,
        ):
            label = f"row {position} entitlement {item_position}"
            if not isinstance(item, dict):
                raise ValueError(f"{label} must be an object")
            source_record_id = str(
                item.get("source_record_id") or ""
            ).strip()
            if not source_record_id or source_record_id in seen_entitlements:
                raise ValueError(
                    f"{label} requires a globally unique source_record_id"
                )
            seen_entitlements.add(source_record_id)
            service_type = str(
                item.get("service_type") or ""
            ).strip().lower()
            if service_type not in MEMBERSHIP_SERVICE_TYPES:
                raise ValueError(f"{label} has an invalid service_type")
            status = str(item.get("status") or "").strip().lower()
            if status not in ENTITLEMENT_STATUSES:
                raise ValueError(f"{label} has an invalid status")
            quantity = item.get("quantity")
            if quantity not in (None, ""):
                try:
                    quantity = Decimal(str(quantity))
                except InvalidOperation as exc:
                    raise ValueError(
                        f"{label} has an invalid quantity"
                    ) from exc
                if quantity < 0 or quantity > Decimal("10000"):
                    raise ValueError(f"{label} quantity is out of range")
                quantity = str(quantity)
            else:
                quantity = None
            effective_from = optional_iso_date(
                item.get("effective_from"),
                f"{label} effective_from",
            )
            effective_to = optional_iso_date(
                item.get("effective_to"),
                f"{label} effective_to",
            )
            if (
                effective_from
                and effective_to
                and effective_from > effective_to
            ):
                raise ValueError(
                    f"{label} effective_from cannot follow effective_to"
                )
            entitlements_clean.append(
                {
                    "source_record_id": source_record_id,
                    "service_type": service_type,
                    "quantity": quantity,
                    "unit": (
                        " ".join(str(item.get("unit") or "").split())
                        or None
                    ),
                    "status": status,
                    "effective_from": effective_from,
                    "effective_to": effective_to,
                    "basis": " ".join(
                        str(item.get("basis") or "").split()
                    )
                    or None,
                    "payment_reference": (
                        " ".join(
                            str(
                                item.get("payment_reference") or ""
                            ).split()
                        )
                        or None
                    ),
                }
            )
        accounts_clean = []
        account_ids_for_person: set[str] = set()
        for item_position, item in enumerate(
            row.get("payment_accounts") or [],
            start=1,
        ):
            label = f"row {position} payment account {item_position}"
            if not isinstance(item, dict):
                raise ValueError(f"{label} must be an object")
            source_account_id = str(
                item.get("source_account_id") or ""
            ).strip()
            if not source_account_id or source_account_id in seen_accounts:
                raise ValueError(
                    f"{label} requires a globally unique source_account_id"
                )
            seen_accounts.add(source_account_id)
            account_ids_for_person.add(source_account_id)
            status = str(item.get("status") or "").strip().lower()
            if status not in PAYMENT_ACCOUNT_STATUSES:
                raise ValueError(f"{label} has an invalid status")
            weekly_amount = item.get("weekly_amount")
            if weekly_amount not in (None, ""):
                try:
                    weekly_amount = Decimal(str(weekly_amount))
                except InvalidOperation as exc:
                    raise ValueError(
                        f"{label} has an invalid weekly_amount"
                    ) from exc
                if weekly_amount < 0 or weekly_amount > Decimal("10000"):
                    raise ValueError(
                        f"{label} weekly_amount is out of range"
                    )
                weekly_amount = f"{weekly_amount:.2f}"
            else:
                weekly_amount = None
            accounts_clean.append(
                {
                    "source_account_id": source_account_id,
                    "agreement_id": (
                        str(item.get("agreement_id") or "").strip()
                        or None
                    ),
                    "status": status,
                    "weekly_amount": weekly_amount,
                }
            )
        events_clean = []
        for item_position, item in enumerate(
            row.get("payment_events") or [],
            start=1,
        ):
            label = f"row {position} payment event {item_position}"
            if not isinstance(item, dict):
                raise ValueError(f"{label} must be an object")
            source_event_id = str(
                item.get("source_event_id") or ""
            ).strip()
            if not source_event_id or source_event_id in seen_events:
                raise ValueError(
                    f"{label} requires a globally unique source_event_id"
                )
            seen_events.add(source_event_id)
            source_account_id = str(
                item.get("source_account_id") or ""
            ).strip()
            if source_account_id not in account_ids_for_person:
                raise ValueError(
                    f"{label} references an undeclared payment account"
                )
            try:
                amount = Decimal(str(item.get("amount") or ""))
            except InvalidOperation as exc:
                raise ValueError(f"{label} has an invalid amount") from exc
            if amount <= 0 or amount > Decimal("100000"):
                raise ValueError(f"{label} amount is out of range")
            status = str(item.get("status") or "").strip().lower()
            if status not in PT_MINDER_TRANSACTION_STATUSES:
                raise ValueError(f"{label} has an invalid status")
            service_type = str(
                item.get("service_type") or ""
            ).strip().lower()
            if service_type not in PT_MINDER_SERVICE_TYPES:
                raise ValueError(f"{label} has an invalid service_type")
            cadence = str(item.get("cadence") or "").strip().lower()
            if cadence not in PT_MINDER_CADENCES:
                raise ValueError(f"{label} has an invalid cadence")
            description = " ".join(
                str(item.get("description") or "").split()
            )
            if not description:
                raise ValueError(f"{label} requires description")
            occurred_on = optional_iso_date(
                item.get("occurred_on"),
                f"{label} occurred_on",
            )
            if not occurred_on:
                raise ValueError(f"{label} requires occurred_on")
            events_clean.append(
                {
                    "source_event_id": source_event_id,
                    "source_account_id": source_account_id,
                    "occurred_on": occurred_on,
                    "amount": f"{amount:.2f}",
                    "status": status,
                    "service_type": service_type,
                    "cadence": cadence,
                    "description": description,
                    "coverage_start": optional_iso_date(
                        item.get("coverage_start"),
                        f"{label} coverage_start",
                    ),
                    "coverage_end": optional_iso_date(
                        item.get("coverage_end"),
                        f"{label} coverage_end",
                    ),
                }
            )
        cleaned_rows.append(
            {
                "canonical_key": canonical_key,
                "email": email or None,
                "source_identity_ids": source_identity_ids,
                "entitlements": entitlements_clean,
                "payment_accounts": accounts_clean,
                "payment_events": events_clean,
            }
        )
    return {
        "schema_version": int(payload.get("schema_version") or 1),
        "source": "commercial_evidence",
        "source_system": source_system,
        "source_run_id": source_run_id,
        "observed_at": observed_at,
        "status": "complete",
        "complete": True,
        "rows": cleaned_rows,
    }
