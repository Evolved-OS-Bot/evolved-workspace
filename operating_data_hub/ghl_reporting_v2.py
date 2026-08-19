from __future__ import annotations

import statistics
import time
from hashlib import sha256
from datetime import UTC, datetime, timedelta
from typing import Any

import requests

from .config import BRISBANE_TZ
from .reporting_v2 import attribute_sales_to_assessments


WARM_PIPELINE_ID = "JBVLybtIPZRIfjhzl5KV"
WARM_STAGE_ASSESSMENT_BOOKED = "c419912e-6e51-4e83-8820-6700d12ae971"
WARM_STAGE_PREQUALIFIED = "f0db07c9-247f-41d5-ab68-8040f25e566d"
WARM_LATER_STAGES = {
    "e66774c3-5ee8-4924-8802-33a1fd6d6216",
    "d31d88cb-fd7d-48c5-ad79-68faf382c897",
    "0aba395d-2ac7-45bc-96e1-410fbeb114c2",
    "53f391b8-0173-4bd3-ad77-a9ced2c0b58a",
    "3bb4fe17-c26c-4a48-8d2b-33aab3d7ab5d",
}
MEMBERSHIP_TYPE_FIELD_ID = "1SgYibtlIuophn9FYAh8"
MEMBERSHIP_AGREEMENT_DATE_FIELD_ID = "1WWilN82DxffsOdgKV2Y"
PT_AGREEMENT_DATE_FIELD_ID = "m7XNn6iutAoI4br2QUXu"
PREQUAL_SUMMARY_FIELD_ID = "j5eRYc16qSm49xE8VOx3"
PREQUAL_COMPLETED_BY_FIELD_ID = "tbXFuxkHNESOzh56qLM6"
PREQUAL_COMPLETED_AT_FIELD_ID = "YdWdWipFNHsfhGEMVLHW"
PREQUAL_WAIVED_BY_FIELD_ID = "D6mkBR5FCIfpndCzzqtQ"
PREQUAL_WAIVED_AT_FIELD_ID = "c1h7UzZK51KvHfH76LKx"
PREQUAL_WAIVER_REASON_FIELD_ID = "arwbqUrUeEGSekEUKrNZ"
PREQUAL_SHARED_ROLE_IDENTITIES = {
    "admin eve",
    "eve",
    "automation",
    "integration",
}
PREQUAL_HUMAN_NAMES = {
    "peter brown": "Peter Brown",
    "megan brown": "Megan Brown",
    "nora silva": "Nora Silva",
    "piper mae": "Piper Mae",
}
ONBOARDING_CALENDARS = {
    "s0C4iENvRiaYyREvTGJD": "onboarding",
    "tc9BC56PdRNQGQmY0CgN": "intro",
    "UTOhZ4UA8XDPYEZend4p": "intro",
    "pPu3BfzgdKgKYGlYGeAX": "intro",
    "Nbzw8JiElSyeXdDqBLnQ": "intro",
    "jY8Fm4d2jkUoDW6hFNiZ": "intro",
    "5lHjOoGaVFdJPNReVDeg": "pt_session",
    "9QkeVcyoclQuWOmNlUup": "pt_session",
    "EjHsuZD0s0vJUqPUXOMb": "pt_session",
    "HgRT8Vd7bsH2LZDeOzZz": "pt_session",
    "JFVV14qlUY1QeLO62SMc": "pt_session",
    "U1RSfH7BhPSSXdsBl61N": "pt_session",
    "UIdP5AYIwUW00hC7e5mN": "pt_session",
    "YT1U8WtmgGb5SO3BWE5n": "pt_session",
    "eoL2TrbLGb8D5BA98Z7I": "pt_session",
    "oSrXQVZhtv1tyL0bMFHe": "pt_session",
    "pLtfbopAKPgSGqDnwndF": "pt_session",
    "pOia47f6u6bDNvVMGWPo": "pt_session",
    "skZi4KFJdJdoG2QqANoS": "pt_session",
    "xTF4OeRHi8vM8w7dcKuC": "pt_session",
    "zB8vInq5Hs44IrRKHkmx": "pt_session",
    # Retain the former Jo calendars for confidence-labelled history.
    "7zHRHEDuYAq7ONpWzZZo": "pt_session",
    "vwAIk7FBKfw1mWTvoTbm": "pt_session",
    "z5tYgPhKcN0fzpb6pEkn": "pt_session",
}
TERMINAL_NON_DELIVERY_STATUSES = {"cancelled", "invalid", "no_show"}


def _iso_datetime(value: Any, field: str) -> datetime:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{field} is required")
    parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=BRISBANE_TZ)
    return parsed.astimezone(UTC)


def _agreement_datetime(value: Any) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        if len(text) == 10:
            local = datetime.fromisoformat(f"{text}T12:00:00").replace(
                tzinfo=BRISBANE_TZ
            )
            return local.astimezone(UTC)
        return _iso_datetime(text, "agreement date")
    except ValueError:
        return None


def contact_fields(contact: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for item in contact.get("customFields") or []:
        if not isinstance(item, dict):
            continue
        field_id = str(item.get("id") or item.get("fieldId") or "").strip()
        if field_id:
            result[field_id] = item.get("value")
    return result


def _prequalification_completed_at(value: Any) -> datetime | None:
    """Accept only an explicitly Brisbane-offset completion timestamp."""
    text = str(value or "").strip()
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None or parsed.utcoffset() != BRISBANE_TZ.utcoffset(parsed):
        return None
    return parsed.astimezone(UTC)


def _prequalification_control_state(
    *,
    contact_id: str,
    contact_name: str,
    fields: dict[str, Any],
    warm: list[dict[str, Any]],
    observed_at: datetime,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    """Build an immutable human-completion event or fail closed."""
    eligible_opportunities = [
        item
        for item in warm
        if str(item.get("pipelineStageId") or "").strip()
        in {WARM_STAGE_PREQUALIFIED, *WARM_LATER_STAGES}
    ]
    eligible_opportunity_ids = sorted(
        str(item.get("id") or "").strip()
        for item in eligible_opportunities
        if str(item.get("id") or "").strip()
    )
    summary = str(fields.get(PREQUAL_SUMMARY_FIELD_ID) or "").strip()
    completer = " ".join(
        str(fields.get(PREQUAL_COMPLETED_BY_FIELD_ID) or "").split()
    )
    completed_at_raw = fields.get(PREQUAL_COMPLETED_AT_FIELD_ID)
    completed_at = _prequalification_completed_at(completed_at_raw)
    waived_by = " ".join(
        str(fields.get(PREQUAL_WAIVED_BY_FIELD_ID) or "").split()
    )
    waived_at_raw = fields.get(PREQUAL_WAIVED_AT_FIELD_ID)
    waived_at = _prequalification_completed_at(waived_at_raw)
    waiver_reason = str(
        fields.get(PREQUAL_WAIVER_REASON_FIELD_ID) or ""
    ).strip()
    waiver_signal = bool(
        waived_by or str(waived_at_raw or "").strip() or waiver_reason
    )
    completion_signal = bool(
        summary or completer or str(completed_at_raw or "").strip()
    )
    issues: list[str] = []
    if waiver_signal:
        if completion_signal:
            issues.append("completion_and_waiver_contradictory")
        if not waived_by:
            issues.append("waiver_human_missing")
        elif waived_by.lower() in PREQUAL_SHARED_ROLE_IDENTITIES:
            issues.append("waiver_shared_role")
        elif waived_by.lower() not in PREQUAL_HUMAN_NAMES:
            issues.append("waiver_human_unrecognised")
        if waived_at is None:
            issues.append("waiver_timestamp_invalid")
        if not waiver_reason:
            issues.append("waiver_reason_missing")
    else:
        if not eligible_opportunities:
            issues.append("eligible_warm_stage_missing")
        elif (
            len(eligible_opportunities) > 1
            or len(eligible_opportunity_ids) != 1
        ):
            issues.append("eligible_warm_opportunity_ambiguous")
        if not summary:
            issues.append("prequal_summary_missing")
        if not completer:
            issues.append("human_completer_missing")
        elif completer.lower() in PREQUAL_SHARED_ROLE_IDENTITIES:
            issues.append("shared_role_completer")
        elif completer.lower() not in PREQUAL_HUMAN_NAMES:
            issues.append("human_completer_unrecognised")
        if completed_at is None:
            issues.append("brisbane_completion_timestamp_invalid")

    # Historical stage state predates these controls and must not create a
    # review queue by itself. A review begins only when at least one governed
    # completion field has actually been populated.
    any_completion_signal = completion_signal or waiver_signal
    if issues:
        if not any_completion_signal:
            return None, None
        return None, {
            "source_event_id": (
                "prequalification-exception:"
                + (
                    eligible_opportunity_ids[0]
                    if len(eligible_opportunity_ids) == 1
                    else contact_id
                )
            ),
            "source_object_id": (
                eligible_opportunity_ids[0]
                if len(eligible_opportunity_ids) == 1
                else contact_id
            ),
            "contact_id": contact_id,
            "contact_name": contact_name,
            "state": "exception",
            "issue_codes": issues,
            "eligible_opportunity_ids": eligible_opportunity_ids,
            "completed_by_raw": completer or None,
            "completed_at_raw": str(completed_at_raw or "").strip() or None,
            "waived_by_raw": waived_by or None,
            "waived_at_raw": str(waived_at_raw or "").strip() or None,
            "occurred_at": observed_at.isoformat(),
        }
    if waiver_signal:
        assert waived_at is not None
        return {
            "source_event_id": f"prequalification-waived:{contact_id}",
            "source_object_id": contact_id,
            "contact_id": contact_id,
            "contact_name": contact_name,
            "occurred_at": waived_at.isoformat(),
            "state": "waived",
            "waived_by": PREQUAL_HUMAN_NAMES[waived_by.lower()],
            "waiver_timestamp_field": PREQUAL_WAIVED_AT_FIELD_ID,
            "waiver_by_field": PREQUAL_WAIVED_BY_FIELD_ID,
            "waiver_reason_field": PREQUAL_WAIVER_REASON_FIELD_ID,
            "confidence": "verified",
        }, None
    assert completed_at is not None
    opportunity = eligible_opportunities[0]
    opportunity_id = eligible_opportunity_ids[0]
    return {
        "source_event_id": f"prequalification-completed:{opportunity_id}",
        "source_object_id": opportunity_id,
        "contact_id": contact_id,
        "contact_name": contact_name,
        "opportunity_id": opportunity_id,
        "occurred_at": completed_at.isoformat(),
        "state": "completed",
        "stage_id": str(opportunity.get("pipelineStageId") or "").strip(),
        "completed_by": PREQUAL_HUMAN_NAMES[completer.lower()],
        "completion_timestamp_field": PREQUAL_COMPLETED_AT_FIELD_ID,
        "completer_field": PREQUAL_COMPLETED_BY_FIELD_ID,
        "summary_field": PREQUAL_SUMMARY_FIELD_ID,
        "confidence": "verified",
    }, None


def build_prequalification_parity_sample(
    *,
    contacts: list[dict[str, Any]],
    opportunities: list[dict[str, Any]],
    persisted_event_refs: list[dict[str, Any]],
    persisted_review_queue: list[dict[str, Any]],
    observed_at: datetime | str,
    sample_size: int = 30,
) -> dict[str, Any]:
    """Compare a deterministic, aggregate-only GHL control sample to Hub state.

    This is a read-only check. It intentionally exposes neither contact IDs nor
    names: those remain in the protected source snapshots used for the check.
    """
    observed = _iso_datetime(observed_at, "observed_at")
    opportunities_by_contact: dict[str, list[dict[str, Any]]] = {}
    for opportunity in opportunities:
        if str(opportunity.get("pipelineId") or "") != WARM_PIPELINE_ID:
            continue
        contact_id = str(opportunity.get("contactId") or "").strip()
        if contact_id:
            opportunities_by_contact.setdefault(contact_id, []).append(
                opportunity
            )

    expected: dict[str, dict[str, Any]] = {}
    for contact in contacts:
        contact_id = str(contact.get("id") or "").strip()
        if not contact_id:
            continue
        completion, exception = _prequalification_control_state(
            contact_id=contact_id,
            contact_name="protected",
            fields=contact_fields(contact),
            warm=opportunities_by_contact.get(contact_id, []),
            observed_at=observed,
        )
        if completion:
            expected[contact_id] = {
                "state": "completed",
                "source_event_id": completion["source_event_id"],
                "issue_codes": [],
            }
        elif exception:
            expected[contact_id] = {
                "state": "exception",
                "source_event_id": exception["source_event_id"],
                "issue_codes": sorted(exception["issue_codes"]),
            }

    persisted: dict[str, dict[str, Any]] = {}
    for row in persisted_event_refs:
        contact_id = str(row.get("contact_id") or "").strip()
        if contact_id:
            persisted[contact_id] = {
                "state": "completed",
                "source_event_id": str(row.get("source_event_id") or ""),
                "issue_codes": [],
            }
    for row in persisted_review_queue:
        contact_id = str(row.get("contact_id") or "").strip()
        if contact_id:
            persisted[contact_id] = {
                "state": "exception",
                "source_event_id": str(row.get("source_event_id") or ""),
                "issue_codes": sorted(row.get("issue_codes") or []),
            }

    candidate_ids = sorted(set(expected) | set(persisted))
    selected = sorted(
        candidate_ids,
        key=lambda value: sha256(value.encode("utf-8")).hexdigest(),
    )[:sample_size]
    exact = 0
    mismatches = 0
    fingerprints: list[str] = []
    state_counts = {
        "expected_completed": 0,
        "expected_exception": 0,
        "persisted_completed": 0,
        "persisted_exception": 0,
    }
    for contact_id in selected:
        expected_row = expected.get(contact_id)
        persisted_row = persisted.get(contact_id)
        if expected_row:
            state_counts[f"expected_{expected_row['state']}"] += 1
        if persisted_row:
            state_counts[f"persisted_{persisted_row['state']}"] += 1
        is_exact = expected_row == persisted_row
        exact += int(is_exact)
        mismatches += int(not is_exact)
        fingerprints.append(
            sha256(
                "|".join(
                    (
                        contact_id,
                        str(expected_row),
                        str(persisted_row),
                    )
                ).encode("utf-8")
            ).hexdigest()
        )
    return {
        "definition_version": "ghl-prequalification-parity-v1",
        "observed_at": observed.isoformat(),
        "sample_size": len(selected),
        "requested_sample_size": sample_size,
        "candidate_count": len(candidate_ids),
        "exact": exact,
        "mismatches": mismatches,
        "state_counts": state_counts,
        "sample_fingerprint": sha256(
            "|".join(fingerprints).encode("utf-8")
        ).hexdigest(),
        "complete": len(selected) == min(sample_size, len(candidate_ids)),
    }


def _membership_components(label: str) -> list[dict[str, str]]:
    normalised = " ".join(label.lower().split())
    if "fast track" in normalised or "silver" in normalised:
        return [
            {"service_type": "sgpt", "service_name": "Strength & Sculpt"},
            {"service_type": "pt", "service_name": "Fast Track PT"},
        ]
    return [{"service_type": "sgpt", "service_name": label or "Membership"}]


def _onboarding_entitlement(label: str, *, pt_only: bool = False) -> dict[str, Any]:
    normalised = " ".join(label.lower().split())
    if pt_only:
        return {"required": True, "sessions": 1, "type": "pt_intro"}
    if "fast track" in normalised or "silver" in normalised:
        return {"required": True, "sessions": 4, "type": "fast_track"}
    if "strong" in normalised or "bronze" in normalised:
        return {"required": True, "sessions": 1, "type": "kickstart"}
    return {"required": False, "sessions": 0, "type": "none"}


def normalise_onboarding_event(raw: dict[str, Any]) -> dict[str, Any]:
    event_id = str(raw.get("id") or "").strip()
    contact_id = str(raw.get("contactId") or "").strip()
    calendar_id = str(raw.get("calendarId") or "").strip()
    if not event_id or not contact_id or calendar_id not in ONBOARDING_CALENDARS:
        raise ValueError("onboarding event identity is incomplete")
    status = " ".join(
        str(
            raw.get("appointmentStatus")
            or raw.get("status")
            or "unknown"
        )
        .strip()
        .lower()
        .replace("-", " ")
        .split()
    )
    status = {
        "show": "showed",
        "attended": "showed",
        "no show": "no_show",
        "noshow": "no_show",
        "canceled": "cancelled",
        "cancel": "cancelled",
    }.get(status, status)
    return {
        "source_event_id": f"onboarding-appointment:{event_id}",
        "source_object_id": event_id,
        "appointment_id": event_id,
        "contact_id": contact_id,
        "calendar_id": calendar_id,
        "appointment_type": ONBOARDING_CALENDARS[calendar_id],
        "scheduled_start": _iso_datetime(
            raw.get("startTime"), "onboarding start"
        ).isoformat(),
        "scheduled_end": _iso_datetime(
            raw.get("endTime"), "onboarding end"
        ).isoformat(),
        "booked_at": (
            _iso_datetime(raw.get("dateAdded"), "onboarding booked time")
            .isoformat()
            if raw.get("dateAdded")
            else None
        ),
        "status": status or "unknown",
        "assigned_user_id": str(raw.get("assignedUserId") or "").strip()
        or None,
    }


def link_sales_to_onboarding(
    sales: list[dict[str, Any]],
    onboarding_events: list[dict[str, Any]],
    *,
    observed_at: datetime,
    link_days: int = 60,
) -> list[dict[str, Any]]:
    events_by_contact: dict[str, list[dict[str, Any]]] = {}
    for event in onboarding_events:
        events_by_contact.setdefault(event["contact_id"], []).append(event)
    cases = []
    for sale in sales:
        if not sale.get("qualifying_new_membership"):
            continue
        evidence = sale.get("evidence") or {}
        membership_type = str(evidence.get("membership_type") or "").strip()
        entitlement = _onboarding_entitlement(
            membership_type,
            pt_only=sale.get("sale_type") == "pt_membership",
        )
        if not entitlement["required"]:
            continue
        sold_at = _iso_datetime(sale["sold_at"], "sold_at")
        sold_day = sold_at.astimezone(BRISBANE_TZ).date()
        candidates = []
        for event in events_by_contact.get(sale["contact_id"], []):
            allowed_types = {
                "kickstart": {"onboarding", "intro"},
                "fast_track": {"onboarding", "intro", "pt_session"},
                "pt_intro": {"intro", "pt_session"},
            }.get(entitlement["type"], set())
            if event["appointment_type"] not in allowed_types:
                continue
            start = _iso_datetime(event["scheduled_start"], "scheduled_start")
            local_day = start.astimezone(BRISBANE_TZ).date()
            if sold_day <= local_day <= sold_day + timedelta(days=link_days):
                candidates.append(event)
        candidates.sort(
            key=lambda row: (
                row["scheduled_start"],
                row.get("booked_at") or "",
                row["appointment_id"],
            )
        )
        deduplicated = []
        seen_slots: set[tuple[str, str, str]] = set()
        for event in candidates:
            slot_key = (
                event["contact_id"],
                event["scheduled_start"],
                str(event.get("assigned_user_id") or ""),
            )
            if slot_key in seen_slots:
                continue
            seen_slots.add(slot_key)
            deduplicated.append(event)
        candidates = deduplicated
        valid = [
            row
            for row in candidates
            if row["status"] not in TERMINAL_NON_DELIVERY_STATUSES
        ]
        first_booked = valid[0] if valid else None
        completed = [row for row in valid if row["status"] == "showed"]
        first_completed = completed[0] if completed else None
        elapsed_unverified = [
            row
            for row in valid
            if row["status"] == "confirmed"
            and _iso_datetime(row["scheduled_end"], "scheduled_end")
            < observed_at
        ]
        cases.append(
            {
                "sale_id": sale["sale_id"],
                "contact_id": sale["contact_id"],
                "sold_at": sale["sold_at"],
                "entitlement_type": entitlement["type"],
                "entitled_sessions": entitlement["sessions"],
                "first_onboarding_appointment_id": (
                    first_booked["appointment_id"] if first_booked else None
                ),
                "first_onboarding_scheduled_at": (
                    first_booked["scheduled_start"] if first_booked else None
                ),
                "first_onboarding_booked_at": (
                    first_booked.get("booked_at") if first_booked else None
                ),
                "first_onboarding_completed_at": (
                    first_completed["scheduled_end"]
                    if first_completed
                    else None
                ),
                "booking_days": (
                    (
                        _iso_datetime(
                            first_booked["scheduled_start"],
                            "scheduled_start",
                        ).astimezone(BRISBANE_TZ).date()
                        - sold_day
                    ).days
                    if first_booked
                    else None
                ),
                "completion_days": (
                    (
                        _iso_datetime(
                            first_completed["scheduled_end"],
                            "scheduled_end",
                        ).astimezone(BRISBANE_TZ).date()
                        - sold_day
                    ).days
                    if first_completed
                    else None
                ),
                "elapsed_confirmed_appointments": len(elapsed_unverified),
                "completion_state": (
                    "completed"
                    if first_completed
                    else "elapsed_unverified"
                    if elapsed_unverified
                    else "booked"
                    if first_booked
                    else "unbooked"
                ),
            }
        )
    return cases


def summarise_onboarding_cases(cases: list[dict[str, Any]]) -> dict[str, Any]:
    booking_days = [
        int(row["booking_days"])
        for row in cases
        if row.get("booking_days") is not None
    ]
    completion_days = [
        int(row["completion_days"])
        for row in cases
        if row.get("completion_days") is not None
    ]
    return {
        "eligible_sales": len(cases),
        "booked_sales": len(booking_days),
        "unbooked_sales": sum(
            row["completion_state"] == "unbooked" for row in cases
        ),
        "completed_sales": len(completion_days),
        "elapsed_unverified_sales": sum(
            row["completion_state"] == "elapsed_unverified"
            for row in cases
        ),
        "average_sale_to_booking_days": (
            sum(booking_days) / len(booking_days) if booking_days else None
        ),
        "median_sale_to_booking_days": (
            statistics.median(booking_days) if booking_days else None
        ),
        "average_sale_to_completion_days": (
            sum(completion_days) / len(completion_days)
            if completion_days
            else None
        ),
        "median_sale_to_completion_days": (
            statistics.median(completion_days) if completion_days else None
        ),
        "completed_within_three_days": (
            sum(days <= 3 for days in completion_days)
            / len(completion_days)
            if completion_days
            else None
        ),
        "completion_tracking_available": bool(completion_days),
    }


def upcoming_assessment_readiness(
    *,
    contacts: list[dict[str, Any]],
    attendance_rows: list[dict[str, Any]],
    prequalification_events: list[dict[str, Any]],
    observed_at: datetime,
    window_days: int = 7,
) -> dict[str, Any]:
    window_end = observed_at + timedelta(days=window_days)
    contact_names = {
        str(row.get("id") or "").strip(): (
            str(
                row.get("name")
                or " ".join(
                    part
                    for part in (
                        str(row.get("firstName") or "").strip(),
                        str(row.get("lastName") or "").strip(),
                    )
                    if part
                )
                or "Unnamed contact"
            ).strip()
        )
        for row in contacts
        if str(row.get("id") or "").strip()
    }
    prequalified_contact_ids = {
        str(row.get("contact_id") or "").strip()
        for row in prequalification_events
        if row.get("contact_id")
    }
    appointments = []
    for row in attendance_rows:
        appointment_id = str(row.get("appointment_id") or "").strip()
        contact_id = str(row.get("contact_id") or "").strip()
        status = str(
            row.get("canonical_status") or row.get("status") or ""
        ).strip().lower()
        if (
            not appointment_id
            or not contact_id
            or status not in {"confirmed", "showed"}
            or bool(row.get("deleted"))
        ):
            continue
        scheduled_at = _iso_datetime(row.get("start_at"), "start_at")
        if not observed_at <= scheduled_at < window_end:
            continue
        scheduled_local = scheduled_at.astimezone(BRISBANE_TZ)
        appointments.append(
            {
                "appointment_id": appointment_id,
                "contact_id": contact_id,
                "client_name": contact_names.get(
                    contact_id, "Unnamed contact"
                ),
                "scheduled_start": scheduled_at.isoformat(),
                "scheduled_local": scheduled_local.isoformat(),
                "scheduled_label": scheduled_local.strftime(
                    "%a %d %b, %I:%M %p"
                )
                .replace(" 0", " ")
                .replace("AM", "am")
                .replace("PM", "pm"),
                "assigned_user_id": row.get("assigned_user_id"),
                "prequalified": contact_id in prequalified_contact_ids,
            }
        )
    appointments.sort(
        key=lambda row: (
            row["scheduled_start"],
            row["client_name"].lower(),
            row["appointment_id"],
        )
    )
    prequalified = sum(
        bool(row["prequalified"]) for row in appointments
    )
    total = len(appointments)
    return {
        "definition_version": "upcoming-sa-readiness-v1",
        "observed_at": observed_at.isoformat(),
        "window_start": observed_at.isoformat(),
        "window_end": window_end.isoformat(),
        "timezone": "Australia/Brisbane",
        "booked": total,
        "prequalified": prequalified,
        "awaiting_prequalification": total - prequalified,
        "prequalification_rate": (
            prequalified / total if total else None
        ),
        "appointments": appointments,
    }


def build_ghl_acquisition_snapshot(
    *,
    contacts: list[dict[str, Any]],
    opportunities: list[dict[str, Any]],
    attendance_rows: list[dict[str, Any]],
    observed_at: datetime | str,
    onboarding_events: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    observed = _iso_datetime(observed_at, "observed_at")
    opportunities_by_contact: dict[str, list[dict[str, Any]]] = {}
    for opportunity in opportunities:
        if str(opportunity.get("pipelineId") or "") != WARM_PIPELINE_ID:
            continue
        contact_id = str(opportunity.get("contactId") or "").strip()
        if contact_id:
            opportunities_by_contact.setdefault(contact_id, []).append(
                opportunity
            )

    lead_events = []
    prequalification_events = []
    prequalification_waiver_events = []
    prequalification_eligible_events = []
    sales = []
    for contact in contacts:
        contact_id = str(contact.get("id") or "").strip()
        if not contact_id:
            continue
        date_added = contact.get("dateAdded") or contact.get("createdAt")
        if date_added:
            try:
                lead_at = _iso_datetime(date_added, "lead date")
                lead_events.append(
                    {
                        "source_event_id": f"lead:{contact_id}",
                        "contact_id": contact_id,
                        "occurred_at": lead_at.isoformat(),
                        "observed_at": observed.isoformat(),
                        "event_type": "lead_created",
                        "lead_source": contact.get("source"),
                    }
                )
            except ValueError:
                pass

        warm = opportunities_by_contact.get(contact_id, [])

        fields = contact_fields(contact)
        tags = {
            str(tag).strip().lower()
            for tag in contact.get("tags") or []
            if str(tag).strip()
        }
        returning = "old member" in tags
        membership_date = _agreement_datetime(
            fields.get(MEMBERSHIP_AGREEMENT_DATE_FIELD_ID)
        )
        membership_type = str(
            fields.get(MEMBERSHIP_TYPE_FIELD_ID) or ""
        ).strip()
        if membership_date:
            sales.append(
                {
                    "sale_id": (
                        f"ghl-membership:{contact_id}:"
                        f"{membership_date.date().isoformat()}"
                    ),
                    "source_system": "ghl",
                    "source_sale_id": (
                        f"membership-agreement:{contact_id}:"
                        f"{membership_date.date().isoformat()}"
                    ),
                    "contact_id": contact_id,
                    "sold_at": membership_date.isoformat(),
                    "sale_type": (
                        "reactivation" if returning else "membership"
                    ),
                    "returning_former_member": returning,
                    "qualifying_new_membership": not returning,
                    "confidence": "high",
                    "service_components": _membership_components(
                        membership_type
                    ),
                    "evidence": {
                        "agreement_date_field": (
                            MEMBERSHIP_AGREEMENT_DATE_FIELD_ID
                        ),
                        "membership_type_field": MEMBERSHIP_TYPE_FIELD_ID,
                        "membership_type": membership_type,
                        "won_warm_opportunity": any(
                            str(item.get("status") or "").lower() == "won"
                            for item in warm
                        ),
                        "date_precision": "date_only",
                    },
                }
            )
        pt_date = _agreement_datetime(
            fields.get(PT_AGREEMENT_DATE_FIELD_ID)
        )
        if pt_date and not membership_date:
            sales.append(
                {
                    "sale_id": (
                        f"ghl-pt:{contact_id}:"
                        f"{pt_date.date().isoformat()}"
                    ),
                    "source_system": "ghl",
                    "source_sale_id": (
                        f"pt-agreement:{contact_id}:"
                        f"{pt_date.date().isoformat()}"
                    ),
                    "contact_id": contact_id,
                    "sold_at": pt_date.isoformat(),
                    "sale_type": (
                        "reactivation" if returning else "pt_membership"
                    ),
                    "returning_former_member": returning,
                    "qualifying_new_membership": not returning,
                    "confidence": "high",
                    "service_components": [
                        {"service_type": "pt", "service_name": "PT"}
                    ],
                    "evidence": {
                        "agreement_date_field": PT_AGREEMENT_DATE_FIELD_ID,
                        "membership_type": "PT only",
                        "won_warm_opportunity": any(
                            str(item.get("status") or "").lower() == "won"
                            for item in warm
                        ),
                        "date_precision": "date_only",
                    },
                }
            )

    prequalification_events = []
    prequalification_exceptions = []
    for contact in contacts:
        contact_id = str(contact.get("id") or "").strip()
        if not contact_id:
            continue
        fields = contact_fields(contact)
        warm = opportunities_by_contact.get(contact_id, [])
        completion_event, exception = _prequalification_control_state(
            contact_id=contact_id,
            contact_name=str(
                contact.get("name")
                or " ".join(
                    part
                    for part in (
                        str(contact.get("firstName") or "").strip(),
                        str(contact.get("lastName") or "").strip(),
                    )
                    if part
                )
                or "Unnamed contact"
            ).strip(),
            fields=fields,
            warm=warm,
            observed_at=observed,
        )
        if completion_event:
            if completion_event["state"] == "completed":
                prequalification_events.append(completion_event)
            else:
                prequalification_waiver_events.append(completion_event)
        if exception:
            prequalification_exceptions.append(exception)
    for row in attendance_rows:
        appointment_id = str(row.get("appointment_id") or "").strip()
        contact_id = str(row.get("contact_id") or "").strip()
        status = str(row.get("canonical_status") or row.get("status") or "")
        if not appointment_id or not contact_id or status in {"cancelled", "invalid"}:
            continue
        eligible = {
            "source_event_id": f"prequalification-eligible:{appointment_id}",
            "source_object_id": appointment_id,
            "appointment_id": appointment_id,
            "contact_id": contact_id,
            "occurred_at": row["start_at"],
            "observed_at": observed.isoformat(),
            "state": "eligible",
        }
        prequalification_eligible_events.append(eligible)

    attributed = attribute_sales_to_assessments(
        attendance_rows,
        sales,
    )
    normalised_onboarding = [
        normalise_onboarding_event(row)
        for row in (onboarding_events or [])
    ]
    onboarding_cases = link_sales_to_onboarding(
        attributed["sales"],
        normalised_onboarding,
        observed_at=observed,
    )
    onboarding_summary = summarise_onboarding_cases(onboarding_cases)
    week_ahead = upcoming_assessment_readiness(
        contacts=contacts,
        attendance_rows=attendance_rows,
        prequalification_events=prequalification_events,
        observed_at=observed,
    )
    return {
        "schema_version": 2,
        "source": "ghl_acquisition_v2",
        "observed_at": observed.isoformat(),
        "complete": True,
        "lead_events": lead_events,
        "prequalification_eligible_events": prequalification_eligible_events,
        "prequalification_events": prequalification_events,
        "prequalification_waiver_events": prequalification_waiver_events,
        "prequalification_exceptions": prequalification_exceptions,
        "sales": attributed["sales"],
        "onboarding_events": normalised_onboarding,
        "onboarding_cases": onboarding_cases,
        "week_ahead": week_ahead,
        "attribution_exceptions": attributed["exceptions"],
        "summary": {
            "contacts": len(contacts),
            "warm_opportunities": sum(
                len(rows) for rows in opportunities_by_contact.values()
            ),
            "leads": len(lead_events),
            "prequalified": len(prequalification_events),
            "prequalification_exceptions": len(prequalification_exceptions),
            "prequalification_waived": len(prequalification_waiver_events),
            "prequalification_waiver_state": "explicit_governed_event",
            "prequalification_eligible": len(
                prequalification_eligible_events
            ),
            "prequalification_completion_rate": None,
            "sales": len(sales),
            "attributed_sales": sum(
                row.get("attribution_state") == "attributed"
                for row in attributed["sales"]
            ),
            "reactivations": sum(
                row.get("attribution_state") == "reactivation_excluded"
                for row in attributed["sales"]
            ),
            "attribution_exceptions": len(
                attributed["exceptions"]
            ),
            "onboarding": onboarding_summary,
        },
    }


class GHLAcquisitionReader:
    base_url = "https://services.leadconnectorhq.com"

    def __init__(self, api_key: str, location_id: str, timeout: int = 60):
        self.location_id = location_id
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {api_key}",
                "Version": "2021-07-28",
                "Accept": "application/json",
            }
        )

    def _request(self, method: str, path: str, **kwargs) -> dict[str, Any]:
        last_error = None
        for attempt in range(5):
            try:
                response = self.session.request(
                    method,
                    f"{self.base_url}{path}",
                    timeout=self.timeout,
                    **kwargs,
                )
                if response.status_code == 429 or response.status_code >= 500:
                    time.sleep(min(8, 2**attempt))
                    continue
                response.raise_for_status()
                return response.json()
            except requests.RequestException as exc:
                last_error = exc
                if attempt < 4:
                    time.sleep(min(8, 2**attempt))
        raise RuntimeError(f"GHL acquisition read failed: {last_error}")

    def contacts(self) -> list[dict[str, Any]]:
        rows = []
        page = 1
        expected = None
        while True:
            payload = self._request(
                "POST",
                "/contacts/search",
                json={
                    "locationId": self.location_id,
                    "page": page,
                    "pageLimit": 100,
                },
            )
            batch = payload.get("contacts") or []
            expected = int(payload.get("total") or 0)
            rows.extend(batch)
            if len(rows) == expected:
                return rows
            if not batch or len(rows) > expected:
                raise RuntimeError("GHL contact snapshot is incomplete")
            page += 1

    def opportunities(self) -> list[dict[str, Any]]:
        rows = []
        params: dict[str, Any] | None = {
            "location_id": self.location_id,
            "pipeline_id": WARM_PIPELINE_ID,
            "limit": 100,
        }
        url = "/opportunities/search"
        while url:
            payload = self._request("GET", url, params=params)
            rows.extend(payload.get("opportunities") or [])
            next_url = (payload.get("meta") or {}).get("nextPageUrl")
            if not next_url:
                break
            url = next_url.replace(self.base_url, "")
            params = None
        return rows

    def form_submissions(
        self,
        form_id: str,
        start: datetime,
        end: datetime,
    ) -> list[dict[str, Any]]:
        if not form_id.strip():
            raise RuntimeError("GHL subscriber form ID is required")
        rows: list[dict[str, Any]] = []
        page = 1
        while True:
            payload = self._request(
                "GET",
                "/forms/submissions",
                params={
                    "locationId": self.location_id,
                    "formId": form_id,
                    "startAt": start.date().isoformat(),
                    "endAt": end.date().isoformat(),
                    "page": page,
                    "limit": 100,
                },
            )
            rows.extend(payload.get("submissions") or [])
            next_page = (payload.get("meta") or {}).get("nextPage")
            if not next_page:
                return rows
            page = int(next_page)

    def onboarding_events(
        self,
        start: datetime,
        end: datetime,
    ) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for calendar_id in ONBOARDING_CALENDARS:
            payload = self._request(
                "GET",
                "/calendars/events",
                params={
                    "locationId": self.location_id,
                    "calendarId": calendar_id,
                    "startTime": int(start.timestamp() * 1000),
                    "endTime": int(end.timestamp() * 1000),
                },
            )
            for item in payload.get("events") or []:
                if not item.get("id") or not item.get("contactId"):
                    continue
                row = dict(item)
                row.setdefault("calendarId", calendar_id)
                rows.append(row)
        return rows
