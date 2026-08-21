from __future__ import annotations

from typing import Any

from reporting_control.current_people_client import (
    CurrentPeopleContract,
    ExactParity,
    exact_parity,
    fetch_cutover_authority,
    fetch_current_people,
    publish_parallel_result,
)

from .models import PTContact


METRIC_ID = "consumer_pt_booking_continuity_contract"
DEFINITION_VERSION = "pt-booking-hub-read-v1"


def _normal(value: Any) -> str:
    return str(value or "").strip().lower()


def _has_pt_service(row: dict[str, Any]) -> bool:
    return any(
        isinstance(item, dict)
        and _normal(item.get("status") or item.get("current_status"))
        in {"active", "current", "cancelling"}
        and _normal(item.get("service_type"))
        in {"personal_training", "fast_track"}
        for item in row.get("service_relationships") or []
    )


def _commercial_supported(row: dict[str, Any]) -> bool:
    return any(
        isinstance(item, dict)
        and _normal(item.get("status"))
        in {"confirmed", "current", "active", "paid_in_advance"}
        and item.get("current", True) is not False
        and _normal(item.get("service_type"))
        in {"personal_training", "fast_track"}
        for item in row.get("entitlements") or []
    )


def hub_pt_projection(row: dict[str, Any] | None) -> dict[str, Any]:
    if row is None:
        return {
            "current_pt": False,
            "suppression": "identity_unresolved",
            "commercial_supported": False,
        }
    lifecycle = row.get("lifecycle") or {}
    status = _normal(lifecycle.get("status"))
    current_lifecycle = status in {
        "active",
        "cancelling",
        "notice_active",
        "approved_hold",
        "on_hold",
    }
    if status in {"approved_hold", "on_hold"}:
        suppression = "pt_hold"
    elif status in {"cancelling", "notice_active"}:
        suppression = "pt_cancellation"
    elif status in {"inactive", "cancelled", "ended"}:
        suppression = "former_pt"
    elif status in {"", "review_required", "unresolved"} or lifecycle.get(
        "missing_reason"
    ):
        suppression = "identity_unresolved"
    else:
        suppression = "none"
    return {
        "current_pt": current_lifecycle and _has_pt_service(row),
        "suppression": suppression,
        "commercial_supported": _commercial_supported(row),
    }


def legacy_pt_projection(contact: PTContact) -> dict[str, Any]:
    return {
        "current_pt": contact.effective_status
        in {"active", "pt_cancellation", "pt_hold"},
        "suppression": {
            "pt_cancellation": "pt_cancellation",
            "pt_hold": "pt_hold",
            "former_pt": "former_pt",
        }.get(contact.effective_status, "none"),
        # Legacy contact resolution has no authoritative commercial status.
        "commercial_supported": None,
    }


def compare_pt_cohort(
    contacts: list[PTContact],
    contract: CurrentPeopleContract,
) -> ExactParity:
    by_contact = contract.by_source_identity("ghl")
    legacy_rows = [
        {
            "contact_id": contact.id,
            **legacy_pt_projection(contact),
        }
        for contact in contacts
    ]
    hub_rows = [
        {
            "contact_id": contact.id,
            **hub_pt_projection(by_contact.get(contact.id)),
        }
        for contact in contacts
    ]
    return exact_parity(
        legacy_rows,
        hub_rows,
        key=lambda row: row["contact_id"],
        projection=lambda row: {
            "current_pt": row["current_pt"],
            "suppression": row["suppression"],
        },
    )


def fetch_pt_contract(*, max_age_hours: int = 192) -> CurrentPeopleContract:
    return fetch_current_people(
        period="week",
        max_age_hours=max_age_hours,
        expected_contract_version="current-person-v1",
    )


def pt_cutover_authority():
    return fetch_cutover_authority(
        metric_id=METRIC_ID,
        definition_version=DEFINITION_VERSION,
    )


def apply_hub_authority(
    contacts: list[PTContact],
    contract: CurrentPeopleContract,
) -> None:
    by_contact = contract.by_source_identity("ghl")
    for contact in contacts:
        projection = hub_pt_projection(by_contact.get(contact.id))
        contact.effective_status = {
            "pt_hold": "pt_hold",
            "pt_cancellation": "pt_cancellation",
            "former_pt": "former_pt",
        }.get(projection["suppression"], "active")
        contact.status_reason = (
            "Canonical Hub lifecycle and current-service contract."
        )


def apply_hub_commercial_evidence(
    evidence: dict[str, Any],
    row: dict[str, Any],
) -> None:
    projection = hub_pt_projection(row)
    evidence["commercial"]["supported"] = projection[
        "commercial_supported"
    ]
    evidence["commercial"]["supporting_sources"] = ["canonical_hub"]
    evidence["stripe"]["entitled"] = projection["commercial_supported"]
    pack_entitlements = [
        item
        for item in row.get("entitlements") or []
        if isinstance(item, dict)
        and _normal(item.get("service_type"))
        in {"personal_training", "fast_track"}
        and "pack" in _normal(item.get("source"))
    ]
    evidence["stripe"]["verified_prepaid_pack"] = bool(pack_entitlements)
    evidence["stripe"]["verified_pack_payments"] = [
        {
            "entitlement_id": item.get("entitlement_id"),
            "source_record_id": item.get("source_record_id"),
            "source_snapshot_id": item.get("source_snapshot_id"),
        }
        for item in pack_entitlements
    ]
    identities = row.get("source_identities") or []
    if isinstance(identities, list):
        trainerize_active = any(
            isinstance(item, dict) and item.get("source") == "trainerize"
            for item in identities
        )
    else:
        trainerize_active = bool(identities.get("trainerize"))
    evidence["trainerize"]["active_access"] = trainerize_active
    evidence["hub_contract"] = {
        "person_id": row.get("person_id"),
        "contract_version": "current-person-v1",
        "suppression_reasons": row.get("suppression_reasons") or [],
    }


def publish_pt_parity(
    *,
    contract: CurrentPeopleContract,
    contacts: list[PTContact],
    comparison_cycle: str,
) -> tuple[ExactParity, dict[str, Any]]:
    parity = compare_pt_cohort(contacts, contract)
    period = contract.period
    published = publish_parallel_result(
        metric_id=METRIC_ID,
        definition_version=DEFINITION_VERSION,
        period_start=str(period.get("start") or ""),
        period_end=str(period.get("end") or ""),
        comparison_cycle=comparison_cycle,
        source_run_ids={
            "hub_current_people": contract.snapshot_id,
            "legacy_ghl_pt_cohort": comparison_cycle,
        },
        parity=parity,
        extra_evidence={
            "delivery_attributes_complete": False,
            "retained_sources": [
                "GHL PT calendars",
                "GHL PT frequency and hold delivery fields",
            ],
            "identified_differences_protected": True,
        },
    )
    return parity, published
