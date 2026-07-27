from __future__ import annotations

import hashlib
import json
import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any


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
    "other",
}
PT_MINDER_CADENCES = {
    "recurring",
    "ad_hoc",
    "other",
}
PT_TRANSACTION_PATTERN = re.compile(
    r"(?:(?:\d+\s*x\s*)?pt\b|personal training|"
    r"one[\s-]*on[\s-]*one|1\s*:\s*1|"
    r"\d+\s*x\s*\d+\s*min)",
    re.IGNORECASE,
)
MEMBERSHIP_TRANSACTION_PATTERN = re.compile(
    r"(?:membership|program|\bsgpt\b|gypsy|strong membership|"
    r"fit\s*(?:&|and)\s*flexible|fast track)",
    re.IGNORECASE,
)
RECURRING_TRANSACTION_PATTERN = re.compile(
    r"(?:weekly|fortnightly|recurring|membership|subscription|"
    r"program\s*-\s*from)",
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


def classify_pt_minder_transaction(description: Any) -> dict[str, str]:
    text = " ".join(str(description or "").split())
    if PT_TRANSACTION_PATTERN.search(text):
        service_type = "personal_training"
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
        cleaned.append(
            {
                "source_transaction_id": source_transaction_id,
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
