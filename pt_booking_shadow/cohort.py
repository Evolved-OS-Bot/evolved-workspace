from __future__ import annotations

from datetime import date, datetime
from typing import Any

from .config import FIELD_IDS, PT_PIPELINE_ID, PT_STAGE_FREQUENCY
from .models import PTContact


def _normal(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, dict):
        value = value.get("value") or value.get("label") or ""
    if isinstance(value, list):
        value = ", ".join(str(item) for item in value)
    return str(value).strip()


def custom_field_map(raw: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for item in raw.get("customFields") or []:
        field_id = item.get("id") or item.get("fieldId")
        if not field_id:
            continue
        result[str(field_id)] = item.get("value", item.get("fieldValue"))
    return result


def parse_date(value: Any) -> date | None:
    text = _normal(value)
    if not text:
        return None
    for parser in (
        lambda: datetime.fromisoformat(text.replace("Z", "+00:00")).date(),
        lambda: datetime.strptime(text, "%Y-%m-%d").date(),
        lambda: datetime.strptime(text, "%d/%m/%Y").date(),
        lambda: datetime.strptime(text, "%m/%d/%Y").date(),
    ):
        try:
            return parser()
        except ValueError:
            continue
    return None


def _frequency_from_tags(tags: set[str]) -> int | None:
    for frequency in (1, 2, 3):
        candidates = {
            f"{frequency} p.wk",
            f"{frequency} pw",
            f"{frequency}x week",
            f"{frequency}x per week",
        }
        if tags & candidates:
            return frequency
    return None


def _choose_pt_stage(opportunities: list[dict[str, Any]]) -> str | None:
    eligible = [
        item
        for item in opportunities
        if item.get("pipelineId") == PT_PIPELINE_ID
        and item.get("pipelineStageId") in PT_STAGE_FREQUENCY
        and str(item.get("status", "open")).lower() not in {"lost", "abandoned"}
    ]
    if not eligible:
        return None
    eligible.sort(key=lambda item: item.get("updatedAt") or item.get("createdAt") or "", reverse=True)
    return str(eligible[0]["pipelineStageId"])


def resolve_contact(
    raw: dict[str, Any], opportunities: list[dict[str, Any]]
) -> PTContact | None:
    tags = {str(tag).strip().lower() for tag in raw.get("tags") or []}
    stage_id = _choose_pt_stage(opportunities)
    has_pt_tag = "personal training" in tags
    if not has_pt_tag and stage_id is None and "old pt client" not in tags:
        return None

    fields = custom_field_map(raw)
    stage_frequency = PT_STAGE_FREQUENCY.get(stage_id) if stage_id else None
    expected_frequency = stage_frequency or _frequency_from_tags(tags)
    name = (
        f"{raw.get('firstName', '')} {raw.get('lastName', '')}".strip()
        or raw.get("contactName")
        or "Unnamed contact"
    )

    cancellation_status = _normal(fields.get(FIELD_IDS["cancellation_status"])).lower()
    cancellation_type = _normal(fields.get(FIELD_IDS["cancellation_type"])).lower()
    hold_status = _normal(fields.get(FIELD_IDS["hold_status"])).lower()
    hold_type = _normal(fields.get(FIELD_IDS["hold_type"])).lower()

    effective_status = "active"
    status_reason = "Current PT tag or PT pipeline stage."
    if cancellation_type == "pt" and cancellation_status in {"notice active", "cancelled"}:
        effective_status = "pt_cancellation"
        status_reason = f"PT cancellation status is {cancellation_status.title()}."
    elif hold_type == "pt" and hold_status in {"pending hold", "escalated hold", "on hold"}:
        effective_status = "pt_hold"
        status_reason = f"PT hold status is {hold_status.title()}."
    elif "old pt client" in tags:
        effective_status = "former_pt"
        status_reason = "Contact has the old pt client tag."

    return PTContact(
        id=str(raw["id"]),
        name=str(name),
        tags=tags,
        custom_fields=fields,
        email=str(raw.get("email") or "").strip().lower(),
        phone=str(raw.get("phone") or "").strip(),
        stage_id=stage_id,
        expected_frequency=expected_frequency,
        effective_status=effective_status,
        status_reason=status_reason,
        hold_start=parse_date(fields.get(FIELD_IDS["hold_start"])),
        hold_end=parse_date(fields.get(FIELD_IDS["hold_end"])),
        final_access=parse_date(fields.get(FIELD_IDS["final_access"])),
    )


def resolve_cohort(
    contacts: list[dict[str, Any]], opportunities: list[dict[str, Any]]
) -> list[PTContact]:
    by_contact: dict[str, list[dict[str, Any]]] = {}
    for opportunity in opportunities:
        contact_id = opportunity.get("contactId") or (opportunity.get("contact") or {}).get("id")
        if contact_id:
            by_contact.setdefault(str(contact_id), []).append(opportunity)

    cohort: list[PTContact] = []
    for raw in contacts:
        resolved = resolve_contact(raw, by_contact.get(str(raw.get("id")), []))
        if resolved:
            cohort.append(resolved)
    return sorted(cohort, key=lambda item: item.name.lower())
