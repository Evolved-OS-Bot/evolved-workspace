from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from reporting_control.current_people_client import (
    CurrentPeopleContract,
    ExactParity,
    HubContractError,
    exact_parity,
    fetch_cutover_authority,
    fetch_current_people,
    publish_parallel_result,
)


METRIC_ID = "consumer_conversation_triage_contract"
DEFINITION_VERSION = "conversation-triage-hub-read-v1"


def _normal(value: Any) -> str:
    return str(value or "").strip().lower()


def _active_services(row: dict[str, Any]) -> set[str]:
    result: set[str] = set()
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
            result.add(service_type)
    return result


def hub_member_flags(row: dict[str, Any] | None) -> dict[str, Any]:
    if row is None:
        return {
            "is_sgpt_member": False,
            "is_pt_client": False,
            "identity_review_required": True,
        }
    lifecycle = row.get("lifecycle") or {}
    lifecycle_status = _normal(lifecycle.get("status"))
    current = lifecycle_status in {"active", "cancelling", "notice_active"}
    services = _active_services(row)
    return {
        "is_sgpt_member": current
        and bool({"sgpt", "fast_track"} & services),
        "is_pt_client": current
        and bool({"personal_training", "fast_track"} & services),
        "identity_review_required": lifecycle_status
        in {"", "review_required", "unresolved"}
        or bool(lifecycle.get("missing_reason")),
    }


@dataclass(frozen=True)
class TriageHubContext:
    contract: CurrentPeopleContract
    by_contact_id: dict[str, dict[str, Any]]

    @classmethod
    def fetch(cls, *, max_age_hours: int = 14) -> "TriageHubContext":
        contract = fetch_current_people(
            period="week",
            max_age_hours=max_age_hours,
            expected_contract_version="current-person-v1",
        )
        return cls(
            contract=contract,
            by_contact_id=contract.by_source_identity("ghl"),
        )

    def flags(self, contact_id: str) -> dict[str, Any]:
        return hub_member_flags(self.by_contact_id.get(str(contact_id)))


def compare_conversation_contacts(
    conversations: list[dict[str, Any]],
) -> ExactParity:
    legacy_rows = [
        {
            "contact_id": str(row.get("contact_id") or ""),
            "is_sgpt_member": bool(row.get("legacy_is_sgpt_member")),
            "is_pt_client": bool(row.get("legacy_is_pt_client")),
        }
        for row in conversations
    ]
    hub_rows = [
        {
            "contact_id": str(row.get("contact_id") or ""),
            "is_sgpt_member": bool(row.get("hub_is_sgpt_member")),
            "is_pt_client": bool(row.get("hub_is_pt_client")),
        }
        for row in conversations
    ]
    return exact_parity(
        legacy_rows,
        hub_rows,
        key=lambda row: row["contact_id"],
        projection=lambda row: {
            "is_sgpt_member": row["is_sgpt_member"],
            "is_pt_client": row["is_pt_client"],
        },
    )


def publish_conversation_parity(
    *,
    context: TriageHubContext,
    conversations: list[dict[str, Any]],
    comparison_cycle: str,
) -> dict[str, Any]:
    if not conversations:
        return {
            "status": "not_run",
            "reason": "No unread contact supplied classification evidence.",
        }
    parity = compare_conversation_contacts(conversations)
    period = context.contract.period
    return publish_parallel_result(
        metric_id=METRIC_ID,
        definition_version=DEFINITION_VERSION,
        period_start=str(period.get("start") or ""),
        period_end=str(period.get("end") or ""),
        comparison_cycle=comparison_cycle,
        source_run_ids={
            "hub_current_people": context.contract.snapshot_id,
            "legacy_ghl_contacts": comparison_cycle,
        },
        parity=parity,
        extra_evidence={
            "sample_contact_count": len(conversations),
            "identified_differences_protected": True,
        },
    )


def triage_cutover_authority():
    return fetch_cutover_authority(
        metric_id=METRIC_ID,
        definition_version=DEFINITION_VERSION,
    )


__all__ = [
    "HubContractError",
    "TriageHubContext",
    "compare_conversation_contacts",
    "hub_member_flags",
    "publish_conversation_parity",
    "triage_cutover_authority",
]
