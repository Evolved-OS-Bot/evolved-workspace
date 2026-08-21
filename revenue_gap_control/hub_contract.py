from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from reporting_control.current_people_client import (
    CurrentPeopleContract,
    ExactParity,
    exact_parity,
    fetch_cutover_authority,
    fetch_current_people,
    publish_parallel_result,
)

from .models import RosterRecord, SourceEvidence


METRIC_ID = "consumer_revenue_control_contract"
DEFINITION_VERSION = "revenue-control-hub-read-v1"
PREPAID_COMMERCIAL_CLASSIFICATIONS = {
    "ACTIVE_PIA",
    "PIF_PACK_IN_DELIVERY",
    "PACK_RENEWAL_DUE",
}


def _normal(value: Any) -> str:
    return str(value or "").strip().lower()


def _text(value: Any) -> str:
    return " ".join(str(value or "").split())


def _decimal(value: Any, field: str) -> Decimal | None:
    if value in (None, ""):
        return None
    try:
        return Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError(f"{field} is not a decimal") from exc


def _legacy_allocation_state(
    *,
    service: str,
    status: Any,
    payment_marker: Any,
    weekly_allocation: Any,
    renewal_date: Any,
    commercial_classification: Any,
) -> tuple[str, str, bool]:
    allocation = _text(weekly_allocation)
    marker = _text(payment_marker).upper()
    classification = _text(commercial_classification).upper()
    prepaid = marker in {"PIF", "PIA"} or _normal(status) == "active - pia"
    confirmed_prepaid = prepaid and (
        (
            service == "sgpt"
            and bool(_text(renewal_date))
        )
        or (
            service == "personal_training"
            and classification in PREPAID_COMMERCIAL_CLASSIFICATIONS
        )
    )
    if confirmed_prepaid:
        return "prepaid", "confirmed_prepaid_entitlement", False
    if prepaid:
        return (
            "prepaid",
            "prepaid_marker_without_confirmed_entitlement",
            False,
        )
    if allocation:
        return "weekly_recurring", "confirmed_weekly_amount", True
    return "unresolved", "unresolved", False


def _governed_roster_relationships(
    row: dict[str, Any],
) -> list[dict[str, Any]]:
    relationships = []
    for relationship in row.get("service_relationships") or []:
        if not isinstance(relationship, dict):
            continue
        if _normal(
            relationship.get("status")
            or relationship.get("current_status")
        ) not in {"active", "current", "cancelling"}:
            continue
        governed = relationship.get("governed_roster_attributes")
        if (
            relationship.get("source") != "active_client_cohort"
            or not isinstance(governed, dict)
        ):
            continue
        attributes = governed.get("attributes") or {}
        if not isinstance(attributes, dict):
            attributes = {}
        weekly_allocation = _text(attributes.get("weekly_allocation"))
        allocation_basis = _normal(
            attributes.get("allocation_basis")
            or ("weekly_recurring" if weekly_allocation else "unresolved")
        )
        allocation_evidence_status = _normal(
            attributes.get("allocation_evidence_status")
            or (
                "confirmed_weekly_amount"
                if weekly_allocation
                else "unresolved"
            )
        )
        weekly_allocation_applicable = attributes.get(
            "weekly_allocation_applicable"
        )
        if weekly_allocation_applicable is None:
            weekly_allocation_applicable = (
                allocation_basis == "weekly_recurring"
            )
        allocation_complete = (
            allocation_evidence_status == "confirmed_weekly_amount"
            and bool(weekly_allocation)
        ) or (
            allocation_basis == "prepaid"
            and allocation_evidence_status
            == "confirmed_prepaid_entitlement"
            and weekly_allocation_applicable is False
        )
        relationships.append(
            {
                "service_type": _normal(
                    relationship.get("service_type")
                ),
                "complete": (
                    governed.get("complete") is True
                    and allocation_complete
                ),
                "product": _text(attributes.get("product")),
                "assigned_trainer": _text(
                    attributes.get("assigned_trainer")
                ),
                "contracted_weekly_frequency": _text(
                    attributes.get("contracted_weekly_frequency")
                ),
                "service_duration": _text(
                    attributes.get("service_duration")
                ),
                "weekly_allocation": weekly_allocation,
                "allocation_currency": _text(
                    attributes.get("allocation_currency")
                ),
                "allocation_basis": allocation_basis,
                "allocation_evidence_status": (
                    allocation_evidence_status
                ),
                "weekly_allocation_applicable": bool(
                    weekly_allocation_applicable
                ),
                "payment_marker": _text(
                    attributes.get("payment_marker")
                ),
                "contract_length": _text(
                    attributes.get("contract_length")
                ),
                "effective_from": _text(governed.get("effective_from")),
                "effective_to": _text(governed.get("effective_to")),
                "source_snapshot_id": _text(
                    governed.get("source_snapshot_id")
                ),
                "missing_attributes": sorted(
                    _text(value)
                    for value in governed.get("missing_attributes") or []
                    if _text(value)
                ),
            }
        )
    return sorted(
        relationships,
        key=lambda item: (
            item["service_type"],
            item["product"],
            item["source_snapshot_id"],
        ),
    )


def hub_revenue_projection(row: dict[str, Any]) -> dict[str, Any]:
    lifecycle = row.get("lifecycle") or {}
    service_types = sorted(
        {
            _normal(item.get("service_type"))
            for item in row.get("service_relationships") or []
            if isinstance(item, dict)
            and _normal(item.get("status") or item.get("current_status"))
            in {"active", "current", "cancelling"}
            and _normal(item.get("service_type"))
        }
    )
    entitlement_services = sorted(
        {
            _normal(item.get("service_type"))
            for item in row.get("entitlements") or []
            if isinstance(item, dict)
            and _normal(item.get("status"))
            in {"confirmed", "current", "active", "paid_in_advance"}
            and item.get("current", True) is not False
            and _normal(item.get("service_type"))
        }
    )
    payment_states = sorted(
        {
            _normal(
                item.get("current_evidence_state")
                or item.get("status")
                or item.get("state")
            )
            for item in row.get("payment_accounts") or []
            if isinstance(item, dict)
            and _normal(
                item.get("current_evidence_state")
                or item.get("status")
                or item.get("state")
            )
        }
    )
    roster_relationships = _governed_roster_relationships(row)
    return {
        "lifecycle_status": _normal(lifecycle.get("status"))
        or "unresolved",
        "service_types": service_types,
        "entitlement_services": entitlement_services,
        "payment_states": payment_states,
        "roster_relationships": roster_relationships,
        "roster_attributes_complete": bool(roster_relationships)
        and all(item["complete"] for item in roster_relationships),
        "decision_required": (
            _normal(lifecycle.get("status"))
            in {"", "review_required", "unresolved"}
            or bool(lifecycle.get("missing_reason"))
        ),
    }


def _legacy_rows(
    database: Path,
    *,
    run_id: str,
    contract: CurrentPeopleContract,
) -> list[dict[str, Any]]:
    by_contact = contract.by_source_identity("ghl")
    connection = sqlite3.connect(database)
    connection.row_factory = sqlite3.Row
    identities = connection.execute(
        "SELECT * FROM client_identity WHERE run_id=?",
        (run_id,),
    ).fetchall()
    lifecycle = {
        str(row["email"]): row
        for row in connection.execute(
            "SELECT * FROM lifecycle_evidence WHERE run_id=?",
            (run_id,),
        ).fetchall()
    }
    payment = {
        str(row["email"]): row
        for row in connection.execute(
            "SELECT * FROM payment_evidence WHERE run_id=?",
            (run_id,),
        ).fetchall()
    }
    services: dict[str, set[str]] = {}
    roster_relationships: dict[str, list[dict[str, Any]]] = {}
    for row in connection.execute(
        """
        SELECT email, service, product, status, payment_marker,
               classification, trainer,
               sessions_per_week, session_length, weekly_allocation,
               contract_length, renewal_date
        FROM roster_snapshot
        WHERE run_id=?
        """,
        (run_id,),
    ).fetchall():
        email = str(row["email"])
        service = (
            "personal_training"
            if str(row["service"]) == "PT"
            else "sgpt"
        )
        services.setdefault(email, set()).add(service)
        weekly_allocation = _text(row["weekly_allocation"])
        payment_marker = _text(row["payment_marker"]).upper()
        (
            allocation_basis,
            allocation_evidence_status,
            weekly_allocation_applicable,
        ) = _legacy_allocation_state(
            service=service,
            status=row["status"],
            payment_marker=payment_marker,
            weekly_allocation=weekly_allocation,
            renewal_date=row["renewal_date"],
            commercial_classification=row["classification"],
        )
        required = (
            (
                "product",
                "assigned_trainer",
                "contracted_weekly_frequency",
                "service_duration",
            )
            if service == "personal_training"
            else ("product",)
        )
        values = {
            "product": _text(row["product"]),
            "assigned_trainer": _text(row["trainer"]),
            "contracted_weekly_frequency": _text(
                row["sessions_per_week"]
            ),
            "service_duration": _text(row["session_length"]),
            "weekly_allocation": weekly_allocation,
            "allocation_currency": (
                "AUD" if weekly_allocation else ""
            ),
            "allocation_basis": allocation_basis,
            "allocation_evidence_status": allocation_evidence_status,
            "weekly_allocation_applicable": weekly_allocation_applicable,
            "payment_marker": payment_marker,
            "contract_length": _text(row["contract_length"]),
            "effective_from": "",
            "effective_to": _text(row["renewal_date"]),
        }
        missing = [name for name in required if not values[name]]
        if allocation_evidence_status not in {
            "confirmed_weekly_amount",
            "confirmed_prepaid_entitlement",
        }:
            missing.append("allocation_evidence")
        roster_relationships.setdefault(email, []).append(
            {
                "service_type": service,
                "complete": not missing,
                **values,
                "source_snapshot_id": "",
                "missing_attributes": missing,
            }
        )
    connection.close()

    result_by_person: dict[str, dict[str, Any]] = {}
    for identity in identities:
        email = str(identity["email"] or "")
        # The audit database retains source evidence for the broader GHL
        # population. Revenue Control's legacy authority is the governed
        # active roster, so unrelated source identities must not enter the
        # consumer parity set.
        if email not in roster_relationships:
            continue
        contact_ids = json.loads(
            str(identity["ghl_contact_ids_json"] or "[]")
        )
        matched_people = {
            str(by_contact[str(contact_id)]["person_id"])
            for contact_id in contact_ids
            if str(contact_id) in by_contact
        }
        person_id = (
            next(iter(matched_people))
            if len(matched_people) == 1
            else f"unresolved:{email}"
        )
        lifecycle_row = lifecycle.get(email)
        payment_row = payment.get(email)
        cancellation = (
            str(lifecycle_row["cancellation_status"] or "").strip()
            if lifecycle_row
            else ""
        )
        final_access = (
            str(lifecycle_row["final_access_date"] or "").strip()
            if lifecycle_row
            else ""
        )
        if cancellation and final_access:
            lifecycle_status = "cancelling"
        elif lifecycle_row:
            lifecycle_status = "active"
        else:
            lifecycle_status = "unresolved"
        stripe_statuses = (
            json.loads(str(payment_row["stripe_statuses_json"] or "[]"))
            if payment_row
            else []
        )
        payment_states = sorted(
            {
                _normal(value)
                for value in stripe_statuses
                if _normal(value)
            }
        )
        if (
            payment_row
            and payment_row["latest_invoice_paid"]
            and not payment_states
        ):
            payment_states = ["paid"]
        current_payment = bool(
            payment_row
            and (
                payment_row["latest_invoice_paid"]
                or {
                    _normal(value) for value in stripe_statuses
                }
                & {"active", "trialing", "past_due", "unpaid"}
            )
        )
        projected = {
            "person_id": person_id,
            "lifecycle_status": lifecycle_status,
            "service_types": sorted(services.get(email, set())),
            "entitlement_services": (
                sorted(services.get(email, set()))
                if current_payment
                else []
            ),
            "payment_states": payment_states,
            "roster_relationships": sorted(
                roster_relationships.get(email, []),
                key=lambda item: (
                    item["service_type"],
                    item["product"],
                ),
            ),
            "roster_attributes_complete": bool(
                roster_relationships.get(email)
            )
            and all(
                item["complete"]
                for item in roster_relationships.get(email, [])
            ),
            "decision_required": person_id.startswith("unresolved:"),
        }
        existing = result_by_person.get(person_id)
        if existing is None:
            result_by_person[person_id] = projected
            continue
        lifecycle_values = {
            existing["lifecycle_status"],
            projected["lifecycle_status"],
        }
        lifecycle_conflict = len(lifecycle_values) > 1
        existing["lifecycle_status"] = (
            next(iter(lifecycle_values))
            if not lifecycle_conflict
            else "review_required"
        )
        for field in (
            "service_types",
            "entitlement_services",
            "payment_states",
        ):
            existing[field] = sorted(
                set(existing[field]) | set(projected[field])
            )
        relationships = {
            json.dumps(item, sort_keys=True): item
            for item in (
                existing["roster_relationships"]
                + projected["roster_relationships"]
            )
        }
        existing["roster_relationships"] = sorted(
            relationships.values(),
            key=lambda item: (
                item["service_type"],
                item["product"],
            ),
        )
        existing["roster_attributes_complete"] = bool(
            existing["roster_relationships"]
        ) and all(
            item["complete"]
            for item in existing["roster_relationships"]
        )
        existing["decision_required"] = bool(
            existing["decision_required"]
            or projected["decision_required"]
            or lifecycle_conflict
        )
    return list(result_by_person.values())


def compare_revenue_run(
    database: Path,
    *,
    run_id: str,
    contract: CurrentPeopleContract,
) -> ExactParity:
    legacy = _legacy_rows(database, run_id=run_id, contract=contract)
    person_ids = {row["person_id"] for row in legacy}
    hub = [
        {
            "person_id": str(row["person_id"]),
            **hub_revenue_projection(row),
        }
        for row in contract.rows
        if str(row["person_id"]) in person_ids
    ]
    return exact_parity(
        legacy,
        hub,
        key=lambda row: row["person_id"],
        projection=lambda row: {
            "lifecycle_status": row["lifecycle_status"],
            "service_types": row["service_types"],
            "entitlement_services": row["entitlement_services"],
            "payment_states": row["payment_states"],
            "roster_relationships": [
                {
                    key: value
                    for key, value in relationship.items()
                    if key != "source_snapshot_id"
                }
                for relationship in row["roster_relationships"]
            ],
            "roster_attributes_complete": row[
                "roster_attributes_complete"
            ],
            "decision_required": row["decision_required"],
        },
    )


def revenue_roster_contract_complete(
    contract: CurrentPeopleContract,
) -> bool:
    active_rows = [
        row
        for row in contract.rows
        if (row.get("governed_cohort") or {}).get("confirmed_active") is True
    ]
    return bool(active_rows) and all(
        hub_revenue_projection(row)["roster_attributes_complete"]
        for row in active_rows
    )


@dataclass(frozen=True)
class HubAuditSources:
    roster: tuple[RosterRecord, ...]
    evidence_by_email: dict[str, SourceEvidence]
    contact_to_email: dict[str, str]
    source_run_id: str
    limitations: tuple[str, ...]


def build_hub_audit_sources(
    contract: CurrentPeopleContract,
) -> HubAuditSources:
    if not revenue_roster_contract_complete(contract):
        raise ValueError(
            "Hub governed roster attributes are incomplete for an active person"
        )
    roster: list[RosterRecord] = []
    evidence_by_email: dict[str, SourceEvidence] = {}
    contact_to_email: dict[str, str] = {}
    seen_emails: set[str] = set()
    row_number = 1
    for row in contract.rows:
        cohort = row.get("governed_cohort") or {}
        if cohort.get("confirmed_active") is not True:
            continue
        person_id = _text(row.get("person_id"))
        display = row.get("display") or {}
        email = _normal(display.get("email"))
        if not person_id or not email or email in seen_emails:
            raise ValueError(
                "Hub active roster requires one protected presentation email "
                "per person"
            )
        seen_emails.add(email)
        first_name = _text(display.get("first_name"))
        last_name = _text(display.get("last_name"))
        relationships = _governed_roster_relationships(row)
        for relationship in relationships:
            allocation = _decimal(
                relationship["weekly_allocation"],
                "weekly_allocation",
            )
            frequency = _decimal(
                relationship["contracted_weekly_frequency"],
                "contracted_weekly_frequency",
            )
            session_cost = (
                allocation / frequency
                if allocation is not None
                and frequency is not None
                and frequency > 0
                else None
            )
            service = (
                "PT"
                if relationship["service_type"] == "personal_training"
                else "SGPT"
            )
            status = "Active"
            roster.append(
                RosterRecord(
                    service=service,
                    row_number=row_number,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    phone="",
                    status=status,
                    weekly_allocation=allocation,
                    payment_marker=(
                        relationship["payment_marker"]
                        or (
                            "PIF"
                            if relationship["allocation_evidence_status"]
                            == "confirmed_prepaid_entitlement"
                            else (
                                str(allocation)
                                if allocation is not None
                                else ""
                            )
                        )
                    ),
                    product=relationship["product"],
                    trainer=relationship["assigned_trainer"],
                    session_length=relationship["service_duration"],
                    sessions_per_week=relationship[
                        "contracted_weekly_frequency"
                    ],
                    session_cost=session_cost,
                    contract_length=relationship["contract_length"],
                    renewal_date=relationship["effective_to"],
                    notes=f"Hub person_id {person_id}",
                )
            )
            row_number += 1
        identities = row.get("source_identities") or []
        ghl_ids = [
            _text(identity.get("source_record_id"))
            for identity in identities
            if isinstance(identity, dict)
            and identity.get("source") == "ghl"
            and _text(identity.get("source_record_id"))
        ]
        trainerize_active = any(
            isinstance(identity, dict)
            and identity.get("source") == "trainerize"
            for identity in identities
        )
        for contact_id in ghl_ids:
            if (
                contact_id in contact_to_email
                and contact_to_email[contact_id] != email
            ):
                raise ValueError("Hub GHL identity maps to multiple people")
            contact_to_email[contact_id] = email
        lifecycle = row.get("lifecycle") or {}
        accounts = [
            account
            for account in row.get("payment_accounts") or []
            if isinstance(account, dict)
        ]
        statuses = sorted(
            {
                _normal(account.get("status"))
                for account in accounts
                if _normal(account.get("status"))
            }
        )
        events = [
            event
            for account in accounts
            for event in account.get("latest_event_evidence") or []
            if isinstance(event, dict)
        ]
        paid_events = [
            event
            for event in events
            if _normal(event.get("status"))
            in {"completed", "paid", "succeeded"}
        ]
        evidence_by_email[email] = SourceEvidence(
            email=email,
            ghl_contact_ids=ghl_ids,
            stripe_statuses=statuses,
            latest_invoice_status="paid" if paid_events else "",
            latest_invoice_paid=bool(paid_events),
            latest_receipt_date=max(
                (
                    _text(event.get("occurred_on"))
                    for event in paid_events
                ),
                default="",
            ),
            pause_collection=bool(
                set(statuses) & {"paused", "on_hold"}
            ),
            trainerize_active=trainerize_active,
            membership_type=", ".join(
                sorted(
                    {
                        relationship["service_type"]
                        for relationship in relationships
                    }
                )
            ),
            membership_stage=_text(lifecycle.get("status")),
            cancellation_status=_text(
                lifecycle.get("cancellation_status")
            ),
            final_access_date=_text(lifecycle.get("final_access_date")),
            hold_status=_text(lifecycle.get("hold_status")),
            source_run_id=contract.snapshot_id,
            raw={
                "hub_person_id": person_id,
                "contract_version": contract.contract_version,
                "source_snapshot_ids": sorted(
                    {
                        relationship["source_snapshot_id"]
                        for relationship in relationships
                    }
                ),
            },
        )
    if not roster:
        raise ValueError("Hub governed roster contains no active services")
    return HubAuditSources(
        roster=tuple(roster),
        evidence_by_email=evidence_by_email,
        contact_to_email=contact_to_email,
        source_run_id=contract.snapshot_id,
        limitations=(
            "Hub current-person-v1 is authoritative for person, lifecycle, "
            "service, entitlement, payment and governed roster attributes.",
        ),
    )


def fetch_revenue_contract(
    *, max_age_hours: int = 96
) -> CurrentPeopleContract:
    return fetch_current_people(
        period="week",
        max_age_hours=max_age_hours,
        expected_contract_version="current-person-v1",
    )


def revenue_cutover_authority():
    return fetch_cutover_authority(
        metric_id=METRIC_ID,
        definition_version=DEFINITION_VERSION,
    )


def publish_revenue_parity(
    *,
    contract: CurrentPeopleContract,
    database: Path,
    run_id: str,
    legacy_source_run: str,
) -> tuple[ExactParity, dict[str, Any]]:
    parity = compare_revenue_run(
        database,
        run_id=run_id,
        contract=contract,
    )
    period = contract.period
    roster_complete = revenue_roster_contract_complete(contract)
    published = publish_parallel_result(
        metric_id=METRIC_ID,
        definition_version=DEFINITION_VERSION,
        period_start=str(period.get("start") or ""),
        period_end=str(period.get("end") or ""),
        comparison_cycle=run_id,
        source_run_ids={
            "hub_current_people": contract.snapshot_id,
            "legacy_membership_reconciliation": legacy_source_run,
            "legacy_revenue_control": run_id,
        },
        parity=parity,
        hub_source_complete=roster_complete,
        extra_evidence={
            "delivery_attributes_complete": roster_complete,
            "retained_sources": [
                "approved manual timing controls",
                "PT booking continuity evidence",
                "cash bridge presentation inputs",
            ],
            "identified_differences_protected": True,
        },
    )
    return parity, published
