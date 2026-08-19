from __future__ import annotations

from datetime import date
from typing import Any


NULL_TEXT = {"", "none", "null", "n/a", "na", "-"}
COHORT_DISPOSITIONS = {
    "confirmed_active",
    "excluded",
    "revenue_review_only",
    "timing_difference",
    "decision_required",
}


def normalise_control_text(value: Any) -> str | None:
    text = " ".join(str(value or "").strip().split())
    if text.lower() in NULL_TEXT:
        return None
    return text


def optional_date(value: Any) -> date | None:
    text = normalise_control_text(value)
    if not text:
        return None
    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        return None


def authoritative_lifecycle_status(
    *,
    ghl_active: bool,
    stripe_entitled: bool,
    trainerize_active: bool,
    cancellation_status: Any,
    final_access_date: Any,
    as_of: date,
) -> str:
    """Resolve lifecycle without promoting payment or access into GHL state."""
    cancellation = normalise_control_text(cancellation_status)
    final_access = optional_date(final_access_date)
    if cancellation:
        if final_access and final_access >= as_of:
            return "cancelling"
        return "review_required"
    if ghl_active:
        return "active"
    if stripe_entitled or trainerize_active:
        return "review_required"
    return "inactive"


def active_signal(
    *,
    ghl_active: bool,
    stripe_entitled: bool,
    trainerize_active: bool,
) -> bool:
    return bool(ghl_active or stripe_entitled or trainerize_active)


def summarise_cohort_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    dispositions = {value: 0 for value in sorted(COHORT_DISPOSITIONS)}
    paid_known = 0
    paid_unknown = 0
    for row in rows:
        dispositions[row["disposition"]] += 1
        if row.get("paid_or_entitled") is None:
            paid_unknown += 1
        elif row["paid_or_entitled"]:
            paid_known += 1
    return {
        "union_people": len(rows),
        "legacy_inflated_cohort": sum(
            bool(row["in_legacy_cohort"]) for row in rows
        ),
        "active_source_signal_people": sum(
            bool(row["active_signal"]) for row in rows
        ),
        "confirmed_active_clients": sum(
            bool(row["confirmed_active"]) for row in rows
        ),
        "paid_or_entitled_confirmed": paid_known,
        "paid_or_entitled_unknown": paid_unknown,
        "identity_difference": sum(
            bool(row["in_legacy_cohort"])
            != bool(row["confirmed_active"])
            for row in rows
        ),
        "decision_required": sum(
            bool(row["decision_required"]) for row in rows
        ),
        "dispositions": dispositions,
    }
