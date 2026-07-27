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


def validate_pt_minder(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("payload must be an object")
    observed_at = iso_datetime(payload.get("observed_at"), "observed_at")
    rows = payload.get("rows")
    if not isinstance(rows, list) or len(rows) > 1000:
        raise ValueError("rows must be a list with at most 1000 entries")
    if not rows:
        raise ValueError("a complete PT Minder snapshot cannot be empty")

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
            }
        )
    return {
        "schema_version": 1,
        "source": "pt_minder",
        "observed_at": observed_at,
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

