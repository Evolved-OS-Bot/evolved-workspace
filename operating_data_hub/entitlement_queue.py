from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from datetime import date
from typing import Any

from .contracts import classify_pt_minder_transaction


BUCKETS = {
    "lifecycle_mismatch": {
        "label": "Lifecycle correction required",
        "severity": "high",
        "owner": "Admin Eve",
        "next_action": (
            "Resolve the GHL lifecycle conflict before relying on payment "
            "or access evidence."
        ),
    },
    "approved_hold": {
        "label": "Approved hold evidence",
        "severity": "low",
        "owner": "Admin Eve",
        "next_action": (
            "Confirm the hold window and resume date; do not create debt "
            "or collecting revenue while the hold is open."
        ),
    },
    "future_start": {
        "label": "Approved future start",
        "severity": "low",
        "owner": "Admin Eve",
        "next_action": (
            "Verify the start date and first scheduled collection when the "
            "service becomes current."
        ),
    },
    "prepaid_or_pack": {
        "label": "PIA or prepaid pack evidence",
        "severity": "medium",
        "owner": "Admin Eve",
        "next_action": (
            "Attach the approved payment or pack beneficiary evidence to "
            "the shared commercial contract."
        ),
    },
    "arrears_retry": {
        "label": "Payment retry in progress",
        "severity": "high",
        "owner": "Admin Eve",
        "next_action": (
            "Track the specific failed scheduled debit and retry outcome; "
            "ignore PT Minder displayed balances and Charge entries."
        ),
    },
    "active_contract_receipt_unresolved": {
        "label": "Active contract, receipt unresolved",
        "severity": "high",
        "owner": "Admin Eve",
        "next_action": (
            "Verify the current paid receipt or payment-rail handoff; "
            "do not infer payment from contract status alone."
        ),
    },
    "payment_unresolved_with_future_booking": {
        "label": "PT booked, payment unresolved",
        "severity": "high",
        "owner": "Admin Eve",
        "next_action": (
            "Resolve the PT payment purpose and entitlement before "
            "treating future bookings as commercially covered."
        ),
    },
    "no_current_payment_evidence": {
        "label": "No current payment evidence",
        "severity": "high",
        "owner": "Admin Eve",
        "next_action": (
            "Locate the current authoritative payment rail or approved "
            "non-recurring entitlement; access and roster state are not "
            "payment proof."
        ),
    },
    "pt_minder_shadow_collecting": {
        "label": "PT Minder collecting, parity pending",
        "severity": "medium",
        "owner": "Admin Eve",
        "next_action": (
            "Retain the current PT Minder payment evidence in shadow until "
            "the second independent capture passes exact parity."
        ),
    },
    "paid_period_end_unresolved": {
        "label": "Recent receipt, paid-through date unresolved",
        "severity": "high",
        "owner": "Admin Eve",
        "next_action": (
            "Confirm the service period or final-access end date covered by "
            "the recent receipt before promoting entitlement."
        ),
    },
    "paid_period_expired_roster_active": {
        "label": "Paid period ended, roster active",
        "severity": "high",
        "owner": "Admin Eve",
        "next_action": (
            "Confirm a renewal or correct the active roster and lifecycle "
            "state; the last paid service period has ended."
        ),
    },
    "one_time_invoice_entitlement_term_missing": {
        "label": "One-time invoice, entitlement term missing",
        "severity": "high",
        "owner": "Admin Eve",
        "next_action": (
            "Attach the purchased service term or approved access end date; "
            "the one-time Stripe receipt does not define ongoing access."
        ),
    },
    "purchased_service_term_future": {
        "label": "Purchased service term starts later",
        "severity": "low",
        "owner": "Admin Eve",
        "next_action": (
            "Retain the approved future service term and verify the roster "
            "becomes current on its effective start date."
        ),
    },
    "confirmed_entitlement_starts_later": {
        "label": "Confirmed entitlement starts after dashboard date",
        "severity": "low",
        "owner": "Admin Eve",
        "next_action": (
            "No payment-purpose decision is required. Verify the next "
            "governed cohort includes the confirmed service period."
        ),
    },
    "purchased_service_term_expired": {
        "label": "Purchased service term ended, roster active",
        "severity": "high",
        "owner": "Admin Eve",
        "next_action": (
            "Confirm a new purchase or correct the active roster; the "
            "approved one-time service term has ended."
        ),
    },
    "payment_account_paused_roster_active": {
        "label": "Payment paused, roster active",
        "severity": "high",
        "owner": "Admin Eve",
        "next_action": (
            "Confirm the approved hold window or payment resumption before "
            "treating the active roster service as commercially covered."
        ),
    },
    "payment_service_mismatch": {
        "label": "Payment purpose does not match roster service",
        "severity": "high",
        "owner": "Admin Eve",
        "next_action": (
            "Resolve whether the payment purpose or governed roster service "
            "is incorrect; do not transfer evidence across service types."
        ),
    },
    "payment_current_booking_gap": {
        "label": "Payment current, booking gap",
        "severity": "medium",
        "owner": "Admin Eve",
        "next_action": (
            "Confirm the current payment evidence and resolve the PT "
            "booking-continuity exception separately."
        ),
    },
    "collecting_not_shared": {
        "label": "Collecting evidence not yet shared",
        "severity": "medium",
        "owner": "Admin Eve",
        "next_action": (
            "Publish the verified recurring payment evidence from its "
            "authoritative source into the hub contract."
        ),
    },
    "payment_booking_unresolved": {
        "label": "Payment and booking unresolved",
        "severity": "high",
        "owner": "Admin Eve",
        "next_action": (
            "Reconcile payment purpose, current entitlement and booking "
            "continuity before marking the service commercially verified."
        ),
    },
    "unclassified": {
        "label": "Owner classification required",
        "severity": "high",
        "owner": "Peter Brown",
        "next_action": (
            "Choose the authoritative evidence path or remove the service "
            "from the governed roster."
        ),
    },
}

BUCKET_ORDER = (
    "lifecycle_mismatch",
    "arrears_retry",
    "active_contract_receipt_unresolved",
    "payment_unresolved_with_future_booking",
    "payment_service_mismatch",
    "payment_account_paused_roster_active",
    "one_time_invoice_entitlement_term_missing",
    "purchased_service_term_expired",
    "paid_period_expired_roster_active",
    "paid_period_end_unresolved",
    "no_current_payment_evidence",
    "payment_booking_unresolved",
    "prepaid_or_pack",
    "collecting_not_shared",
    "pt_minder_shadow_collecting",
    "payment_current_booking_gap",
    "approved_hold",
    "purchased_service_term_future",
    "confirmed_entitlement_starts_later",
    "future_start",
    "unclassified",
)


def service_is_covered(
    service_type: str,
    confirmed_entitlement_types: set[str],
) -> bool:
    required = {
        "sgpt": {"sgpt", "fast_track"},
        "personal_training": {"personal_training", "fast_track"},
    }.get(service_type, {service_type})
    return bool(required & confirmed_entitlement_types)


def classify_gap(
    *,
    classification: str | None,
    roster_status: str | None,
    lifecycle_status: str | None,
    ghl_active: bool,
) -> str:
    value = str(classification or "").strip().upper()
    status = str(roster_status or "").strip().upper()
    if not ghl_active or lifecycle_status != "active":
        return "lifecycle_mismatch"
    if value in {"APPROVED_PAUSE", "LIFECYCLE_EXCEPTION"}:
        return "approved_hold"
    if value == "APPROVED_FUTURE_START":
        return "future_start"
    if value in {"ACTIVE_PIA", "PIF_PACK_IN_DELIVERY", "PACK_RENEWAL_DUE"}:
        return "prepaid_or_pack"
    if status == "ACTIVE - PIA":
        return "prepaid_or_pack"
    if value in {"ACTIVE - ARREARS", "ARREARS"}:
        return "arrears_retry"
    if value == "PAYMENT_CURRENT_NO_BOOKING":
        return "payment_current_booking_gap"
    if value == "ACTIVE_CONTRACT_RECEIPT_UNRESOLVED":
        return "active_contract_receipt_unresolved"
    if value == "PAYMENT_UNRESOLVED_WITH_FUTURE_BOOKING":
        return "payment_unresolved_with_future_booking"
    if value == "NO_CURRENT_PAYMENT_EVIDENCE":
        return "no_current_payment_evidence"
    if value == "CLEAN_COLLECTING":
        return "collecting_not_shared"
    if value == "BOOKING_PAYMENT_UNRESOLVED":
        return "payment_booking_unresolved"
    return "unclassified"


def _json_object(value: Any) -> dict[str, Any]:
    try:
        parsed = json.loads(str(value or "{}"))
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _compatible_event_service(
    event: dict[str, Any],
) -> str:
    if str(event.get("source") or "") == "pt_minder":
        if event.get("service_override_id"):
            return str(event.get("service_type") or "")
        return classify_pt_minder_transaction(
            event.get("description")
        )["service_type"]
    return str(event.get("service_type") or "")


def _route_payment_evidence_gap(
    *,
    person_id: str,
    service_type: str,
    as_of_date: str,
    payment_accounts_by_person: dict[str, list[dict[str, Any]]],
    payment_events_by_person: dict[str, list[dict[str, Any]]],
) -> str:
    accounts = payment_accounts_by_person.get(person_id, [])
    events = payment_events_by_person.get(person_id, [])
    try:
        as_of = date.fromisoformat(as_of_date)
    except ValueError:
        return "no_current_payment_evidence"

    recent = []
    for event in events:
        try:
            age = (as_of - date.fromisoformat(
                str(event.get("occurred_on") or "")
            )).days
        except ValueError:
            continue
        if 0 <= age <= 35:
            recent.append(event)

    compatible = [
        event
        for event in recent
        if service_is_covered(
            service_type,
            {_compatible_event_service(event)},
        )
    ]
    pt_minder_accounts = [
        account
        for account in accounts
        if account.get("source") == "pt_minder"
        and account.get("status") == "collecting"
    ]
    pt_minder_compatible = [
        event
        for event in compatible
        if event.get("source") == "pt_minder"
        and event.get("cadence") == "recurring"
    ]
    if pt_minder_accounts and pt_minder_compatible:
        current_period_events = [
            event
            for event in pt_minder_compatible
            if (
                not event.get("coverage_start")
                or str(event["coverage_start"]) <= as_of_date
            )
            and (
                not event.get("coverage_end")
                or str(event["coverage_end"]) >= as_of_date
            )
        ]
        latest = max(
            current_period_events or pt_minder_compatible,
            key=lambda event: (
                str(event.get("coverage_end") or ""),
                str(event.get("occurred_on") or ""),
                str(event.get("source_event_id") or ""),
            ),
        )
        if latest.get("status") == "failed":
            return "arrears_retry"
        if latest.get("status") in {"completed", "pending"}:
            return "pt_minder_shadow_collecting"

    current_accounts = [
        account
        for account in accounts
        if account.get("status") in {"active", "collecting"}
    ]
    if current_accounts and recent and not compatible:
        return "payment_service_mismatch"
    if any(account.get("status") == "paused" for account in accounts):
        if any(event.get("status") == "completed" for event in compatible):
            return "payment_account_paused_roster_active"
    if any(account.get("status") == "cancelled" for account in accounts):
        completed_stripe = [
            event
            for event in compatible
            if event.get("source") == "stripe"
            and event.get("status") == "completed"
        ]
        if any(
            event.get("coverage_start")
            and event.get("coverage_start") == event.get("coverage_end")
            for event in completed_stripe
        ):
            return "one_time_invoice_entitlement_term_missing"
        if any(
            event.get("coverage_end")
            and str(event["coverage_end"]) < as_of_date
            for event in completed_stripe
        ):
            return "paid_period_expired_roster_active"
        if any(
            event.get("source") == "stripe"
            and event.get("status") == "completed"
            for event in compatible
        ):
            return "paid_period_end_unresolved"
    return "no_current_payment_evidence"


def build_entitlement_exception_queue(
    *,
    governed_rows: list[dict[str, Any]],
    relationships: list[dict[str, Any]],
    entitlement_rows: list[dict[str, Any]],
    lifecycle_rows: list[dict[str, Any]],
    people_rows: list[dict[str, Any]],
    payment_account_rows: list[dict[str, Any]] | None = None,
    payment_event_rows: list[dict[str, Any]] | None = None,
    identified: bool = False,
) -> dict[str, Any]:
    governed_people = {
        str(row["person_id"])
        for row in governed_rows
        if row.get("confirmed_active")
    }
    as_of_date = max(
        (
            str(row.get("as_of_date") or "")
            for row in governed_rows
        ),
        default="",
    )
    confirmed_by_person: dict[str, set[str]] = defaultdict(set)
    current_revenue_classification: dict[tuple[str, str], str] = {}
    future_confirmed_services: dict[str, set[str]] = defaultdict(set)
    purchased_term_windows: dict[
        tuple[str, str], list[tuple[str, str]]
    ] = defaultdict(list)
    for row in entitlement_rows:
        if (
            row.get("source") != "active_client_cohort"
            and row.get("status") == "confirmed"
            and (
                not row.get("effective_from")
                or str(row["effective_from"]) <= as_of_date
            )
            and (
                not row.get("effective_to")
                or str(row["effective_to"]) >= as_of_date
            )
        ):
            confirmed_by_person[str(row["person_id"])].add(
                str(row["service_type"])
            )
        if (
            row.get("source") != "active_client_cohort"
            and row.get("status") == "confirmed"
            and row.get("effective_from")
            and str(row["effective_from"]) > as_of_date
        ):
            future_confirmed_services[str(row["person_id"])].add(
                str(row["service_type"])
            )
        if (
            row.get("source") == "revenue_control"
            and row.get("status") != "superseded"
        ):
            metadata = _json_object(row.get("metadata_json"))
            basis = str(metadata.get("basis") or "")
            prefix = "revenue_control_assessment:"
            if basis.startswith(prefix):
                current_revenue_classification[
                    (
                        str(row["person_id"]),
                        str(row["service_type"]),
                    )
                ] = basis.removeprefix(prefix)
            if (
                basis
                == "revenue_control_governed_purchased_service_term"
                and row.get("status") == "confirmed"
                and row.get("effective_from")
                and row.get("effective_to")
            ):
                purchased_term_windows[
                    (
                        str(row["person_id"]),
                        str(row["service_type"]),
                    )
                ].append(
                    (
                        str(row["effective_from"]),
                        str(row["effective_to"]),
                    )
                )
    lifecycle_by_person = {
        str(row["person_id"]): row for row in lifecycle_rows
    }
    people_by_person = {
        str(row["person_id"]): row for row in people_rows
    }
    payment_accounts_by_person: dict[
        str, list[dict[str, Any]]
    ] = defaultdict(list)
    for row in payment_account_rows or []:
        payment_accounts_by_person[str(row.get("person_id") or "")].append(
            row
        )
    payment_events_by_person: dict[
        str, list[dict[str, Any]]
    ] = defaultdict(list)
    for row in payment_event_rows or []:
        payment_events_by_person[str(row.get("person_id") or "")].append(
            row
        )

    cases = []
    for relationship in relationships:
        person_id = str(relationship["person_id"])
        if person_id not in governed_people:
            continue
        service_type = str(relationship["service_type"])
        if service_is_covered(
            service_type,
            confirmed_by_person.get(person_id, set()),
        ):
            continue
        metadata = _json_object(relationship.get("metadata_json"))
        lifecycle = lifecycle_by_person.get(person_id) or {}
        lifecycle_evidence = _json_object(
            lifecycle.get("evidence_json")
        )
        classification = current_revenue_classification.get(
            (person_id, service_type),
            metadata.get("classification"),
        )
        roster_status = metadata.get("status")
        bucket = classify_gap(
            classification=classification,
            roster_status=roster_status,
            lifecycle_status=str(lifecycle.get("status") or ""),
            ghl_active=bool(
                lifecycle_evidence.get("ghl_active", False)
            ),
        )
        if bucket in {
            "no_current_payment_evidence",
            "payment_unresolved_with_future_booking",
        }:
            routed_bucket = _route_payment_evidence_gap(
                person_id=person_id,
                service_type=service_type,
                as_of_date=as_of_date,
                payment_accounts_by_person=payment_accounts_by_person,
                payment_events_by_person=payment_events_by_person,
            )
            if (
                routed_bucket != "no_current_payment_evidence"
                or bucket == "no_current_payment_evidence"
            ):
                bucket = routed_bucket
        if bucket in {
            "one_time_invoice_entitlement_term_missing",
            "paid_period_expired_roster_active",
            "paid_period_end_unresolved",
            "no_current_payment_evidence",
        }:
            term_windows = purchased_term_windows.get(
                (person_id, service_type),
                [],
            )
            if any(start > as_of_date for start, _ in term_windows):
                bucket = "purchased_service_term_future"
            elif any(end < as_of_date for _, end in term_windows):
                bucket = "purchased_service_term_expired"
        if (
            BUCKETS[bucket]["severity"] == "high"
            and service_is_covered(
                service_type,
                future_confirmed_services.get(person_id, set()),
            )
        ):
            bucket = "confirmed_entitlement_starts_later"
        person = people_by_person.get(person_id) or {}
        case = {
            "_person_id": person_id,
            "case_id": hashlib.sha256(
                f"{person_id}:{service_type}".encode("utf-8")
            ).hexdigest()[:16],
            "bucket": bucket,
            "service_type": service_type,
            "service_name": relationship.get("service_name"),
            "classification": classification,
            "roster_status": roster_status,
            "lifecycle_status": lifecycle.get("status"),
            "owner": BUCKETS[bucket]["owner"],
            "next_action": BUCKETS[bucket]["next_action"],
        }
        if identified:
            case["canonical_key"] = person.get("canonical_key")
            case["email"] = person.get("email")
        cases.append(case)

    grouped = []
    for code in BUCKET_ORDER:
        bucket_cases = [
            case for case in cases if case["bucket"] == code
        ]
        if not bucket_cases:
            continue
        definition = BUCKETS[code]
        grouped.append(
            {
                "code": code,
                **definition,
                "client_count": len(
                    {
                        case["_person_id"]
                        for case in bucket_cases
                    }
                ),
                "service_gap_count": len(bucket_cases),
                **(
                    {
                        "cases": [
                            {
                                key: value
                                for key, value in case.items()
                                if key != "_person_id"
                            }
                            for case in bucket_cases
                        ]
                    }
                    if identified
                    else {}
                ),
            }
        )
    pending_people = {case["_person_id"] for case in cases}
    return {
        "status": "ready",
        "identified": identified,
        "summary": {
            "clients_pending": len(pending_people),
            "service_gaps": len(cases),
            "bucket_count": len(grouped),
            "high_priority_service_gaps": sum(
                bucket["service_gap_count"]
                for bucket in grouped
                if bucket["severity"] == "high"
            ),
        },
        "buckets": grouped,
    }
