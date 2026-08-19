from __future__ import annotations

from collections.abc import Iterable


REBOOK_GUARD_VERSION = "sa-rebook-guard-v1"
NO_SHOW_WORKFLOW_ID = "c531cc51-65cf-4a75-b4bf-ada7358a515a"
CANCELLED_WORKFLOW_ID = "d6259817-fa44-43d1-bcbe-5f74e78f409f"
MEMBER_TAG = "member"
COMPLETED_ASSESSMENT_TAG = "strength assessment showed"


def normalise_tags(tags: Iterable[object]) -> set[str]:
    return {
        " ".join(str(tag or "").strip().lower().split())
        for tag in tags
        if str(tag or "").strip()
    }


def classify_rebook_guard(
    tags: Iterable[object],
    *,
    contact_type: object = "",
) -> str:
    """Mirror the ordered first-step branches in both live GHL workflows."""
    normalised = normalise_tags(tags)
    if str(contact_type or "").strip().lower() == "customer":
        return "existing_customer_stop"
    if COMPLETED_ASSESSMENT_TAG in normalised:
        return "assessment_completed_stop"
    return "eligible_for_rebooking"
