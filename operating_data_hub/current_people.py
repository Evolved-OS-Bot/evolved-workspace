from __future__ import annotations

import json
from datetime import UTC, date, datetime
from typing import Any

from sqlalchemy import select

from .membership_lifecycle import CURRENT_PERSON_CONTRACT_VERSION
from .store import (
    canonical_people,
    entitlements,
    governed_cohort_members,
    lifecycle_states,
    payment_accounts,
    payment_events,
    service_relationships,
    source_identities,
)


def _iso(value: Any) -> str | None:
    return value.isoformat() if value is not None else None


def _group(rows, field: str) -> dict[str, list[Any]]:
    result: dict[str, list[Any]] = {}
    for row in rows:
        value = row[field]
        if value is not None:
            result.setdefault(str(value), []).append(row)
    return result


def _roster_attributes(
    relationship: Any,
    *,
    confirmed_entitlement: bool,
) -> dict[str, Any]:
    metadata = json.loads(relationship["metadata_json"])
    allocation_basis = str(
        metadata.get("allocation_basis") or "unresolved"
    ).strip().lower()
    weekly_allocation = metadata.get("weekly_allocation")
    if weekly_allocation:
        allocation_evidence_status = "confirmed_weekly_amount"
    elif allocation_basis == "prepaid" and confirmed_entitlement:
        allocation_evidence_status = "confirmed_prepaid_entitlement"
    elif allocation_basis == "prepaid":
        allocation_evidence_status = (
            "prepaid_marker_without_confirmed_entitlement"
        )
    else:
        allocation_evidence_status = "unresolved"
    attributes = {
        "product": metadata.get("product")
        or relationship["service_name"],
        "assigned_trainer": metadata.get("assigned_trainer"),
        "contracted_weekly_frequency": metadata.get(
            "contracted_weekly_frequency"
        ),
        "service_duration": metadata.get("service_duration"),
        "weekly_allocation": weekly_allocation,
        "allocation_currency": metadata.get("allocation_currency"),
        "allocation_basis": allocation_basis,
        "allocation_evidence_status": allocation_evidence_status,
        "weekly_allocation_applicable": (
            allocation_basis == "weekly_recurring"
        ),
        "payment_marker": metadata.get("payment_marker"),
        "contract_length": metadata.get("contract_length"),
    }
    required = (
        [
            "product",
            "assigned_trainer",
            "contracted_weekly_frequency",
            "service_duration",
        ]
        if relationship["service_type"] == "personal_training"
        else ["product"]
    )
    missing = [name for name in required if not attributes.get(name)]
    if allocation_evidence_status not in {
        "confirmed_weekly_amount",
        "confirmed_prepaid_entitlement",
    }:
        missing.append("allocation_evidence")
    return {
        "complete": not missing,
        "attributes": attributes,
        "missing_attributes": missing,
        "effective_from": relationship["effective_from"],
        "effective_to": relationship["effective_to"],
        "source": relationship["source"],
        "source_record_id": relationship["source_record_id"],
        "source_snapshot_id": relationship["source_snapshot_id"],
    }


def build_current_people_contract(
    engine,
    *,
    period: dict[str, str],
    source_freshness: list[dict[str, Any]],
    as_of: datetime | None = None,
) -> dict[str, Any]:
    instant = as_of or datetime.now(UTC)
    if instant.tzinfo is None:
        raise ValueError("as_of must include a timezone")
    as_of_date = date.fromisoformat(period["end"])
    with engine.begin() as connection:
        people = connection.execute(
            select(canonical_people)
        ).mappings().all()
        identities = connection.execute(
            select(source_identities).where(
                source_identities.c.source.in_(("ghl", "trainerize"))
            )
        ).mappings().all()
        lifecycle_rows = connection.execute(
            select(lifecycle_states)
        ).mappings().all()
        relationship_rows = connection.execute(
            select(service_relationships).where(
                service_relationships.c.status.in_(
                    ("active", "paused", "cancelling")
                )
            )
        ).mappings().all()
        entitlement_rows = connection.execute(
            select(entitlements).where(
                entitlements.c.status != "superseded"
            )
        ).mappings().all()
        account_rows = connection.execute(
            select(payment_accounts)
        ).mappings().all()
        event_rows = connection.execute(
            select(payment_events).order_by(
                payment_events.c.occurred_on.desc(),
                payment_events.c.payment_event_id.desc(),
            )
        ).mappings().all()
        cohort_rows = connection.execute(
            select(governed_cohort_members).where(
                governed_cohort_members.c.current == 1
            )
        ).mappings().all()

    identities_by_person = _group(identities, "person_id")
    relationships_by_person = _group(relationship_rows, "person_id")
    entitlements_by_person = _group(entitlement_rows, "person_id")
    accounts_by_person = _group(account_rows, "person_id")
    lifecycle_by_person = {
        str(row["person_id"]): row for row in lifecycle_rows
    }
    cohort_by_person = {
        str(row["person_id"]): row for row in cohort_rows
    }
    latest_event_by_account_service: dict[tuple[str, str], Any] = {}
    for event in event_rows:
        if str(event["occurred_on"]) > as_of_date.isoformat():
            continue
        latest_event_by_account_service.setdefault(
            (
                str(event["payment_account_id"]),
                str(event["service_type"]),
            ),
            event,
        )
    rows = []
    for person in people:
        person_id = str(person["person_id"])
        lifecycle = lifecycle_by_person.get(person_id)
        relationships = relationships_by_person.get(person_id, [])
        current_entitlements = [
            row
            for row in entitlements_by_person.get(person_id, [])
            if (
                not row["effective_from"]
                or str(row["effective_from"]) <= as_of_date.isoformat()
            )
            and (
                not row["effective_to"]
                or str(row["effective_to"]) >= as_of_date.isoformat()
            )
        ]
        confirmed_entitlement_services = {
            str(row["service_type"])
            for row in current_entitlements
            if row["status"] == "confirmed"
        }
        roster_attributes = [
            _roster_attributes(
                relationship,
                confirmed_entitlement=(
                    str(relationship["service_type"])
                    in confirmed_entitlement_services
                ),
            )
            for relationship in relationships
            if relationship["source"] == "active_client_cohort"
        ]
        lifecycle_status = (
            str(lifecycle["status"]).strip().lower()
            if lifecycle is not None
            else "unresolved"
        )
        cancellation_status = (
            str(lifecycle["cancellation_status"] or "").strip().lower()
            if lifecycle is not None
            else ""
        )
        cancellation_type = (
            str(lifecycle["cancellation_type"] or "").strip().lower()
            if lifecycle is not None
            else ""
        )
        hold_status = (
            str(lifecycle["hold_status"] or "").strip().lower()
            if lifecycle is not None
            else ""
        )
        classification = (
            str(lifecycle["classification"] or "").strip().lower()
            if lifecycle is not None
            else ""
        )
        service_types = {
            str(row["service_type"]) for row in relationships
        }
        suppression_reasons = []
        if hold_status in {"on hold", "returning"}:
            suppression_reasons.append("approved_hold")
        if (
            lifecycle_status == "cancelling"
            or cancellation_status in {"notice active", "cancelling"}
        ):
            suppression_reasons.append("active_cancellation_notice")
        if (
            cancellation_type == "pt"
            and bool({"sgpt", "fast_track"} & service_types)
        ):
            suppression_reasons.append("downgrade_only_not_member_loss")
        if "staff" in classification or "complimentary" in classification:
            suppression_reasons.append("staff_or_complimentary")
        if lifecycle_status in {"inactive", "cancelled"}:
            suppression_reasons.append("resolved_or_inactive")
        if lifecycle is None or lifecycle_status == "review_required":
            suppression_reasons.append("lifecycle_unresolved")

        accounts = []
        for account in accounts_by_person.get(person_id, []):
            evidence = [
                event
                for (
                    account_id,
                    _service_type,
                ), event in latest_event_by_account_service.items()
                if account_id == str(account["payment_account_id"])
            ]
            accounts.append(
                {
                    "payment_account_id": account["payment_account_id"],
                    "source": account["source"],
                    "source_account_id": account["source_account_id"],
                    "agreement_id": account["agreement_id"],
                    "status": account["status"],
                    "weekly_amount": account["weekly_amount"],
                    "as_of": _iso(account["observed_at"]),
                    "source_snapshot_id": account["source_snapshot_id"],
                    "latest_event_evidence": [
                        {
                            "payment_event_id": event["payment_event_id"],
                            "source_event_id": event["source_event_id"],
                            "occurred_on": event["occurred_on"],
                            "status": event["status"],
                            "service_type": event["service_type"],
                            "cadence": event["cadence"],
                            "coverage_start": event["coverage_start"],
                            "coverage_end": event["coverage_end"],
                            "source_snapshot_id": event[
                                "source_snapshot_id"
                            ],
                        }
                        for event in evidence
                    ],
                    "missing_reason": (
                        None
                        if evidence
                        else "no_current_payment_event_evidence"
                    ),
                }
            )
        cohort = cohort_by_person.get(person_id)
        rows.append(
            {
                "person_id": person_id,
                "display": {
                    "email": person["email"],
                    "first_name": person["first_name"],
                    "last_name": person["last_name"],
                    "identity_authority": False,
                },
                "source_identities": [
                    {
                        "source": identity["source"],
                        "source_record_id": identity["source_record_id"],
                        "as_of": _iso(identity["observed_at"]),
                        "source_snapshot_id": identity[
                            "source_snapshot_id"
                        ],
                    }
                    for identity in identities_by_person.get(person_id, [])
                ],
                "lifecycle": {
                    "status": lifecycle_status,
                    "cancellation_status": (
                        lifecycle["cancellation_status"]
                        if lifecycle is not None
                        else None
                    ),
                    "cancellation_type": (
                        lifecycle["cancellation_type"]
                        if lifecycle is not None
                        else None
                    ),
                    "notice_end_date": (
                        lifecycle["notice_end_date"]
                        if lifecycle is not None
                        else None
                    ),
                    "final_access_date": (
                        lifecycle["final_access_date"]
                        if lifecycle is not None
                        else None
                    ),
                    "hold_status": (
                        lifecycle["hold_status"]
                        if lifecycle is not None
                        else None
                    ),
                    "hold_type": (
                        lifecycle["hold_type"]
                        if lifecycle is not None
                        else None
                    ),
                    "hold_start_date": (
                        lifecycle["hold_start_date"]
                        if lifecycle is not None
                        else None
                    ),
                    "hold_end_date": (
                        lifecycle["hold_end_date"]
                        if lifecycle is not None
                        else None
                    ),
                    "effective_date": (
                        lifecycle["final_access_date"]
                        or lifecycle["notice_end_date"]
                        if lifecycle is not None
                        else None
                    ),
                    "as_of": (
                        _iso(lifecycle["observed_at"])
                        if lifecycle is not None
                        else None
                    ),
                    "source": (
                        lifecycle["source"]
                        if lifecycle is not None
                        else None
                    ),
                    "source_snapshot_id": (
                        lifecycle["source_snapshot_id"]
                        if lifecycle is not None
                        else None
                    ),
                    "confidence": (
                        "verified"
                        if lifecycle is not None
                        and lifecycle_status != "review_required"
                        else "unresolved"
                    ),
                    "missing_reason": (
                        None
                        if lifecycle is not None
                        else "no_authoritative_lifecycle_state"
                    ),
                },
                "service_relationships": [
                    {
                        "relationship_id": relationship["relationship_id"],
                        "service_type": relationship["service_type"],
                        "service_name": relationship["service_name"],
                        "status": relationship["status"],
                        "effective_from": relationship["effective_from"],
                        "effective_to": relationship["effective_to"],
                        "source": relationship["source"],
                        "source_snapshot_id": relationship[
                            "source_snapshot_id"
                        ],
                        "metadata": json.loads(
                            relationship["metadata_json"]
                        ),
                        "governed_roster_attributes": (
                            _roster_attributes(
                                relationship,
                                confirmed_entitlement=(
                                    str(relationship["service_type"])
                                    in confirmed_entitlement_services
                                ),
                            )
                            if relationship["source"]
                            == "active_client_cohort"
                            else {
                                "complete": False,
                                "attributes": {},
                                "missing_attributes": [
                                    "governed_active_roster_relationship"
                                ],
                                "effective_from": relationship[
                                    "effective_from"
                                ],
                                "effective_to": relationship["effective_to"],
                                "source": relationship["source"],
                                "source_record_id": relationship[
                                    "source_record_id"
                                ],
                                "source_snapshot_id": relationship[
                                    "source_snapshot_id"
                                ],
                            }
                        ),
                    }
                    for relationship in relationships
                ],
                "service_missing_reason": (
                    None
                    if relationships
                    else "no_current_service_relationship"
                ),
                "delivery_attributes": {
                    "complete": bool(roster_attributes)
                    and all(
                        item["complete"] for item in roster_attributes
                    ),
                    "authority": "governed_active_roster",
                    "relationships": roster_attributes,
                    "missing_reason": (
                        None
                        if roster_attributes
                        and all(
                            item["complete"] for item in roster_attributes
                        )
                        else (
                            "governed_roster_attributes_incomplete"
                            if roster_attributes
                            else "no_governed_active_roster_relationship"
                        )
                    ),
                },
                "entitlements": [
                    {
                        "entitlement_id": entitlement["entitlement_id"],
                        "service_type": entitlement["service_type"],
                        "status": entitlement["status"],
                        "effective_from": entitlement["effective_from"],
                        "effective_to": entitlement["effective_to"],
                        "source": entitlement["source"],
                        "source_record_id": entitlement[
                            "source_record_id"
                        ],
                        "source_snapshot_id": entitlement[
                            "source_snapshot_id"
                        ],
                        "metadata": json.loads(
                            entitlement["metadata_json"]
                        ),
                    }
                    for entitlement in current_entitlements
                ],
                "entitlement_missing_reason": (
                    None
                    if current_entitlements
                    else "no_current_entitlement_evidence"
                ),
                "payment_accounts": accounts,
                "payment_missing_reason": (
                    None if accounts else "no_current_payment_account"
                ),
                "governed_cohort": {
                    "confirmed_active": (
                        bool(cohort["confirmed_active"])
                        if cohort is not None
                        else False
                    ),
                    "decision_required": (
                        bool(cohort["decision_required"])
                        if cohort is not None
                        else True
                    ),
                    "classification": (
                        cohort["primary_reason"]
                        if cohort is not None
                        else "not_in_current_governed_cohort"
                    ),
                    "as_of_date": (
                        cohort["as_of_date"] if cohort is not None else None
                    ),
                    "source_snapshot_id": (
                        cohort["source_snapshot_id"]
                        if cohort is not None
                        else None
                    ),
                },
                "suppression_reasons": sorted(set(suppression_reasons)),
            }
        )
    stale = [
        row["source"]
        for row in source_freshness
        if row.get("freshness") != "fresh"
    ]
    blocked = []
    if stale:
        blocked.append("stale required sources: " + ", ".join(sorted(stale)))
    return {
        "schema_version": 1,
        "contract_version": CURRENT_PERSON_CONTRACT_VERSION,
        "mode": "shadow",
        "publication_impact": "none",
        "protected": True,
        "generated_at": instant.astimezone(UTC).isoformat(),
        "period": period,
        "source_freshness": source_freshness,
        "complete": not blocked,
        "blocked_reasons": blocked,
        "row_count": len(rows),
        "rows": rows,
    }
