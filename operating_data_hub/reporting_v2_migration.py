from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime
from typing import Any, Iterable

from .contracts import canonical_json, fingerprint


HISTORICAL_CONFIDENCE_LEVELS = (
    "verified",
    "high",
    "medium",
    "low",
    "legacy_aggregate",
    "unresolved",
)


def build_raw_workbook_record(
    *,
    workbook_id: str,
    tab_name: str,
    tab_id: int,
    row_number: int,
    values: list[Any],
    formulas: list[Any] | None,
    exported_at: datetime | str,
) -> dict[str, Any]:
    if not workbook_id.strip() or not tab_name.strip():
        raise ValueError("workbook_id and tab_name are required")
    if tab_id < 0 or row_number < 1:
        raise ValueError("tab_id and row_number are invalid")
    if isinstance(exported_at, str):
        exported_at = datetime.fromisoformat(
            exported_at.replace("Z", "+00:00")
        )
    if exported_at.tzinfo is None:
        raise ValueError("exported_at must include a timezone")
    material = {
        "workbook_id": workbook_id,
        "tab_name": tab_name,
        "tab_id": tab_id,
        "row_number": row_number,
        "values": values,
        "formulas": formulas or [],
    }
    return {
        **material,
        "exported_at": exported_at.astimezone(UTC).isoformat(),
        "row_hash": fingerprint(material),
        "raw_json": canonical_json(material),
    }


def classify_historical_confidence(
    evidence: dict[str, Any],
) -> dict[str, str]:
    if evidence.get("conflict") or evidence.get("ambiguous_duplicate"):
        return {
            "confidence": "unresolved",
            "reason": "conflicting or duplicated evidence requires review",
        }
    if evidence.get("legacy_aggregate_only"):
        return {
            "confidence": "legacy_aggregate",
            "reason": "only the historical aggregate survives",
        }
    if evidence.get("stable_source_event_id"):
        return {
            "confidence": "verified",
            "reason": "stable source event identity is preserved",
        }
    if evidence.get("exact_cross_source_match"):
        return {
            "confidence": "verified",
            "reason": "exact event match exists across authoritative sources",
        }
    if (
        evidence.get("exact_person_match")
        and evidence.get("compatible_timestamp")
        and evidence.get("compatible_product_or_amount")
    ):
        return {
            "confidence": "high",
            "reason": "person, time and commercial evidence align",
        }
    if (
        evidence.get("probable_identity_match")
        and evidence.get("compatible_date")
    ):
        return {
            "confidence": "medium",
            "reason": "probable identity and date match without stable event ID",
        }
    if evidence.get("workbook_row_only"):
        return {
            "confidence": "low",
            "reason": "workbook-only row lacks authoritative event identity",
        }
    return {
        "confidence": "unresolved",
        "reason": "insufficient evidence to classify the historical record",
    }


def summarise_backfill_confidence(
    records: Iterable[dict[str, Any]],
) -> dict[str, Any]:
    counts: Counter[str] = Counter()
    total = 0
    for record in records:
        confidence = str(record.get("confidence") or "")
        if confidence not in HISTORICAL_CONFIDENCE_LEVELS:
            raise ValueError("record has an invalid confidence")
        counts[confidence] += 1
        total += 1
    accepted_for_official_aggregate = (
        counts["verified"] + counts["high"]
    )
    return {
        "record_count": total,
        "counts": {
            level: counts[level]
            for level in HISTORICAL_CONFIDENCE_LEVELS
        },
        "accepted_for_official_aggregate": (
            accepted_for_official_aggregate
        ),
        "context_only": (
            counts["medium"]
            + counts["low"]
            + counts["legacy_aggregate"]
        ),
        "unresolved": counts["unresolved"],
    }
