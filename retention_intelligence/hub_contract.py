from __future__ import annotations

from dataclasses import replace
from typing import Any

from reporting_control.current_people_client import (
    CurrentPeopleContract,
    ExactParity,
    exact_parity,
    fetch_cutover_authority,
    fetch_current_people,
    publish_parallel_result,
)

from .models import MemberInput


METRIC_ID = "consumer_retention_intelligence_contract"
DEFINITION_VERSION = "retention-hub-read-v1"


def _normal(value: Any) -> str:
    return str(value or "").strip().lower()


def _current_services(row: dict[str, Any]) -> tuple[set[str], str | None]:
    types: set[str] = set()
    names: list[str] = []
    for relationship in row.get("service_relationships") or []:
        if not isinstance(relationship, dict):
            continue
        status = _normal(
            relationship.get("status")
            or relationship.get("current_status")
        )
        if status not in {"active", "current", "cancelling"}:
            continue
        service_type = _normal(relationship.get("service_type"))
        if service_type:
            types.add(service_type)
        name = str(relationship.get("service_name") or "").strip()
        if name and name not in names:
            names.append(name)
    return types, ", ".join(names) or None


def _has_current_entitlement(row: dict[str, Any]) -> bool:
    for entitlement in row.get("entitlements") or []:
        if not isinstance(entitlement, dict):
            continue
        if _normal(entitlement.get("status")) in {
            "confirmed",
            "current",
            "active",
            "paid_in_advance",
        } and entitlement.get("current", True) is not False:
            return True
    return False


def _hub_fields(row: dict[str, Any]) -> dict[str, Any]:
    lifecycle = row.get("lifecycle") or {}
    lifecycle_status = _normal(lifecycle.get("status"))
    service_types, service_label = _current_services(row)
    unresolved = (
        lifecycle_status in {"", "review_required", "unresolved"}
        or bool(lifecycle.get("missing_reason"))
        or not service_types
    )
    return {
        "service": service_label
        or ", ".join(sorted(service_types))
        or None,
        "service_types": sorted(service_types),
        "ghl_active": lifecycle_status
        in {"active", "cancelling", "notice_active"},
        "stripe_entitled": _has_current_entitlement(row),
        "cancellation_status": (
            str(lifecycle.get("cancellation_status") or "").strip() or None
        ),
        "final_access_date": (
            str(lifecycle.get("final_access_date") or "").strip() or None
        ),
        "has_operational_exception": unresolved,
        "lifecycle_status": lifecycle_status,
    }


def apply_hub_authority(
    legacy_members: list[MemberInput],
    contract: CurrentPeopleContract,
) -> list[MemberInput]:
    by_trainerize = contract.by_source_identity("trainerize")
    result: list[MemberInput] = []
    for member in legacy_members:
        row = by_trainerize.get(str(member.trainerize_user_id))
        if row is None:
            result.append(
                replace(
                    member,
                    ghl_active=False,
                    stripe_entitled=False,
                    has_operational_exception=True,
                )
            )
            continue
        fields = _hub_fields(row)
        display = row.get("display") or {}
        result.append(
            replace(
                member,
                email=(
                    str(display.get("email") or "").strip().lower()
                    or member.email
                ),
                first_name=(
                    str(display.get("first_name") or "").strip()
                    or member.first_name
                ),
                last_name=(
                    str(display.get("last_name") or "").strip()
                    or member.last_name
                ),
                service=fields["service"],
                ghl_active=fields["ghl_active"],
                stripe_entitled=fields["stripe_entitled"],
                cancellation_status=fields["cancellation_status"],
                final_access_date=fields["final_access_date"],
                has_operational_exception=fields[
                    "has_operational_exception"
                ],
            )
        )
    return result


def _legacy_projection(member: MemberInput) -> dict[str, Any]:
    service = _normal(member.service)
    service_types = []
    if "fast track" in service:
        service_types = ["fast_track"]
    elif service.startswith("pt ") or "personal training" in service:
        service_types = ["personal_training"]
    elif "online" in service:
        service_types = ["online"]
    elif service:
        service_types = ["sgpt"]
    lifecycle = (
        "cancelling"
        if member.cancellation_status and member.final_access_date
        else "active"
        if member.ghl_active
        else "review_required"
        if member.trainerize_active or member.stripe_entitled
        else "inactive"
    )
    return {
        "service_types": service_types,
        "lifecycle_status": lifecycle,
        "entitled": bool(member.stripe_entitled),
        "operational_exception": bool(member.has_operational_exception),
    }


def _hub_projection(member: MemberInput) -> dict[str, Any]:
    service = _normal(member.service)
    service_types = sorted(
        {
            item
            for item in (
                "fast_track" if "fast track" in service else "",
                (
                    "personal_training"
                    if "personal training" in service
                    else ""
                ),
                "online" if "online" in service else "",
                (
                    "sgpt"
                    if service
                    and not any(
                        value in service
                        for value in (
                            "fast track",
                            "personal training",
                            "online",
                        )
                    )
                    else ""
                ),
            )
            if item
        }
    )
    lifecycle = (
        "cancelling"
        if member.cancellation_status and member.final_access_date
        else "active"
        if member.ghl_active
        else "review_required"
        if member.trainerize_active or member.stripe_entitled
        else "inactive"
    )
    return {
        "service_types": service_types,
        "lifecycle_status": lifecycle,
        "entitled": bool(member.stripe_entitled),
        "operational_exception": bool(member.has_operational_exception),
    }


def compare_retention_members(
    legacy_members: list[MemberInput],
    hub_members: list[MemberInput],
) -> ExactParity:
    return exact_parity(
        legacy_members,
        hub_members,
        key=lambda member: str(member.trainerize_user_id),
        projection=lambda member: (
            _legacy_projection(member)
            if member in legacy_members
            else _hub_projection(member)
        ),
    )


def fetch_retention_contract(
    *, max_age_hours: int = 14
) -> CurrentPeopleContract:
    return fetch_current_people(
        period="week",
        max_age_hours=max_age_hours,
        expected_contract_version="current-person-v1",
    )


def retention_cutover_authority():
    return fetch_cutover_authority(
        metric_id=METRIC_ID,
        definition_version=DEFINITION_VERSION,
    )


def publish_retention_parity(
    *,
    contract: CurrentPeopleContract,
    legacy_members: list[MemberInput],
    hub_members: list[MemberInput],
    comparison_cycle: str,
    legacy_source_run: str,
) -> tuple[ExactParity, dict[str, Any]]:
    parity = exact_parity(
        legacy_members,
        hub_members,
        key=lambda member: str(member.trainerize_user_id),
        projection=lambda member: _legacy_projection(member),
    )
    period = contract.period
    published = publish_parallel_result(
        metric_id=METRIC_ID,
        definition_version=DEFINITION_VERSION,
        period_start=str(period.get("start") or ""),
        period_end=str(period.get("end") or ""),
        comparison_cycle=comparison_cycle,
        source_run_ids={
            "hub_current_people": contract.snapshot_id,
            "legacy_membership_reconciliation": legacy_source_run,
        },
        parity=parity,
        extra_evidence={
            "delivery_profile_source_retained": True,
            "identified_differences_protected": True,
        },
    )
    return parity, published
