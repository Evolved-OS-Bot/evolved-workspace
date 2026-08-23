"""Side-effect-free PT hold entitlement reconciliation.

The module deliberately knows nothing about Stripe or GHL.  It validates supplied
evidence, classifies appointments around an inclusive hold window, and produces a
proposal for a human to approve in an *existing* GHL Conversation.
"""

from __future__ import annotations

import hashlib
import json
from datetime import date, datetime, timedelta
from typing import Any


SAFE_APPOINTMENT_STATUSES = {"scheduled", "completed", "attended"}
PAYMENT_STATUSES = {"paid", "skipped"}
ALLOWED_EVIDENCE_SOURCES = {"operating_data_hub", "validated_operator_bundle"}
POLICY_SENSITIVE_TERMS = {
    "billing_exception",
    "cancellation",
    "cancelled",
    "canceled",
    "complaint",
    "forfeited",
    "makeup",
    "medical",
    "no_show",
    "policy_ambiguity",
    "rescheduled",
    "safety",
}


class EvidenceError(ValueError):
    """Raised when an evidence field cannot be parsed safely."""


def _date(value: Any, field: str) -> date:
    if isinstance(value, date):
        return value
    if not isinstance(value, str):
        raise EvidenceError(f"{field} must be an ISO date")
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise EvidenceError(f"{field} must use YYYY-MM-DD") from exc


def _positive_int(value: Any, field: str) -> int:
    if isinstance(value, bool):
        raise EvidenceError(f"{field} must be a positive integer")
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise EvidenceError(f"{field} must be a positive integer") from exc
    if parsed <= 0:
        raise EvidenceError(f"{field} must be a positive integer")
    return parsed


def _nonnegative_int(value: Any, field: str) -> int:
    if isinstance(value, bool):
        raise EvidenceError(f"{field} must be a non-negative integer")
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise EvidenceError(f"{field} must be a non-negative integer") from exc
    if parsed < 0:
        raise EvidenceError(f"{field} must be a non-negative integer")
    return parsed


def _review_result(
    *,
    reasons: list[str],
    conversation_id: str,
    classifications: dict[str, list[dict[str, Any]]] | None = None,
    funding: dict[str, Any] | None = None,
) -> dict[str, Any]:
    result = {
        "status": "review_required",
        "safe_to_approve": False,
        "reasons": sorted(set(reasons)),
        "classifications": classifications or {"pre_hold": [], "in_hold": [], "post_hold": []},
        "funding": funding or {},
        "proposed_transfers": [],
        "cash_adjustment": None,
        "mutations_performed": [],
    }
    result["work_item"] = _work_item(conversation_id, result)
    return result


def _work_item(conversation_id: str, result: dict[str, Any]) -> dict[str, Any]:
    status = result["status"]
    transfers = result.get("proposed_transfers", [])
    if transfers:
        transfer_text = "; ".join(
            f"{item['source_appointment_date']} → {item['target_appointment_date']}"
            for item in transfers
        )
        summary = f"Proposed PT entitlement transfer: {transfer_text}. No cash adjustment."
    elif status == "no_transfer_needed":
        summary = "PT boundary reconciliation found no entitlement transfer or cash adjustment needed."
    else:
        summary = "PT hold requires human review: " + "; ".join(result.get("reasons", []))
    return {
        "type": "ghl_conversation_internal_note",
        "conversation_id": conversation_id or None,
        "proposal_id": result.get("proposal_id"),
        "use_existing_conversation": True,
        "create_task": False,
        "create_tracker": False,
        "requires_human_approval": True,
        "message": summary,
    }


def _public_appointment(appointment: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": appointment["id"],
        "date": appointment["date"].isoformat(),
        "status": appointment["status"],
    }


def _proposal_id(
    conversation_id: str,
    hold_start: date,
    hold_end: date,
    provenance: dict[str, Any],
    transfers: list[dict[str, Any]],
) -> str:
    identity = json.dumps(
        {
            "conversation_id": conversation_id,
            "hold_start": hold_start.isoformat(),
            "hold_end": hold_end.isoformat(),
            "snapshot_id": str(provenance.get("snapshot_id") or ""),
            "fingerprint": str(provenance.get("fingerprint") or ""),
            "transfers": transfers,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return "pt-hold-" + hashlib.sha256(identity.encode()).hexdigest()[:32]


def reconcile_pt_hold(payload: dict[str, Any]) -> dict[str, Any]:
    """Return a PT hold reconciliation proposal without performing any mutation."""

    reasons: list[str] = []
    conversation_id = str(payload.get("conversation_id") or "").strip()
    if not conversation_id:
        reasons.append("missing existing GHL Conversation ID")

    required_collections = ("appointments", "payments", "existing_adjustments", "risk_flags")
    for field in required_collections:
        if field not in payload or not isinstance(payload[field], list):
            reasons.append(f"missing {field} evidence")

    try:
        hold_start = _date(payload.get("hold_start_date"), "hold_start_date")
        hold_end = _date(payload.get("hold_end_date"), "hold_end_date")
        evidence_window_start = _date(
            payload.get("evidence_window_start_date"),
            "evidence_window_start_date",
        )
        evidence_window_end = _date(
            payload.get("evidence_window_end_date"),
            "evidence_window_end_date",
        )
        cadence_days = _positive_int(payload.get("payment_cadence_days"), "payment_cadence_days")
        sessions_per_payment = _positive_int(payload.get("sessions_per_payment"), "sessions_per_payment")
        service_offset_days = _nonnegative_int(
            payload.get("billing_to_service_offset_days"), "billing_to_service_offset_days"
        )
    except EvidenceError as exc:
        reasons.append(str(exc))
        return _review_result(reasons=reasons, conversation_id=conversation_id)

    if hold_end < hold_start:
        reasons.append("hold_end_date precedes hold_start_date")
    if evidence_window_end < evidence_window_start:
        reasons.append("evidence window end precedes its start")
    if evidence_window_start > hold_start - timedelta(days=cadence_days):
        reasons.append("appointment evidence does not cover the pre-hold boundary")
    if evidence_window_end < hold_end + timedelta(days=cadence_days):
        reasons.append("appointment evidence does not cover the post-hold boundary")
    if payload.get("evidence_complete") is not True:
        reasons.append("payment, appointment, adjustment, and risk evidence is not marked complete")
    provenance = payload.get("evidence_provenance")
    if not isinstance(provenance, dict):
        reasons.append("missing evidence provenance")
    else:
        source = str(provenance.get("source") or "").strip()
        snapshot_id = str(provenance.get("snapshot_id") or "").strip()
        fingerprint = str(provenance.get("fingerprint") or "").strip()
        if source not in ALLOWED_EVIDENCE_SOURCES:
            reasons.append("evidence source is not governed")
        if not snapshot_id or not fingerprint:
            reasons.append("evidence provenance lacks snapshot ID or fingerprint")
    if payload.get("offset_validated") is not True:
        reasons.append("billing-to-service offset is not validated")

    raw_risk_flags = payload.get("risk_flags", []) if isinstance(payload.get("risk_flags"), list) else []
    if raw_risk_flags:
        reasons.extend(f"policy-sensitive risk flag: {flag}" for flag in raw_risk_flags)

    appointments: list[dict[str, Any]] = []
    appointment_ids: set[str] = set()
    for index, raw in enumerate(payload.get("appointments", [])):
        try:
            appointment_id = str(raw.get("id") or "").strip()
            if not appointment_id:
                raise EvidenceError(f"appointments[{index}].id is required")
            if appointment_id in appointment_ids:
                raise EvidenceError(f"duplicate appointment id: {appointment_id}")
            appointment_ids.add(appointment_id)
            appointment_date = _date(raw.get("date"), f"appointments[{index}].date")
            if not evidence_window_start <= appointment_date <= evidence_window_end:
                reasons.append(
                    f"appointment {appointment_id} falls outside the declared evidence window"
                )
            status = str(raw.get("status") or "").strip().lower()
            if status not in SAFE_APPOINTMENT_STATUSES:
                reasons.append(
                    f"appointment {appointment_id} has policy-sensitive or unsupported status: {status or 'missing'}"
                )
            if any(term in status for term in POLICY_SENSITIVE_TERMS):
                reasons.append(f"appointment {appointment_id} requires policy review")
            appointments.append({"id": appointment_id, "date": appointment_date, "status": status})
        except (AttributeError, EvidenceError) as exc:
            reasons.append(str(exc))

    appointments.sort(key=lambda item: (item["date"], item["id"]))
    classifications = {
        "pre_hold": [_public_appointment(item) for item in appointments if item["date"] < hold_start],
        "in_hold": [
            _public_appointment(item) for item in appointments if hold_start <= item["date"] <= hold_end
        ],
        "post_hold": [_public_appointment(item) for item in appointments if item["date"] > hold_end],
    }

    payments: list[dict[str, Any]] = []
    payment_ids: set[str] = set()
    for index, raw in enumerate(payload.get("payments", [])):
        try:
            payment_id = str(raw.get("id") or "").strip()
            if not payment_id:
                raise EvidenceError(f"payments[{index}].id is required")
            if payment_id in payment_ids:
                raise EvidenceError(f"duplicate payment id: {payment_id}")
            payment_ids.add(payment_id)
            payment_date = _date(raw.get("date"), f"payments[{index}].date")
            status = str(raw.get("status") or "").strip().lower()
            if status not in PAYMENT_STATUSES:
                raise EvidenceError(f"payment {payment_id} has unsupported status: {status or 'missing'}")
            skip_reason = str(raw.get("skip_reason") or "").strip().lower()
            if status == "skipped" and skip_reason != "hold":
                reasons.append(
                    f"payment {payment_id} skip reason is not validated as hold: {skip_reason or 'missing'}"
                )
            payments.append(
                {
                    "id": payment_id,
                    "date": payment_date,
                    "status": status,
                    "skip_reason": skip_reason,
                    "cadence_relevant": raw.get("cadence_relevant", True) is True,
                    "funded_appointment_ids": list(raw.get("funded_appointment_ids") or []),
                }
            )
        except (AttributeError, EvidenceError) as exc:
            reasons.append(str(exc))

    cadence_payments = sorted(
        (payment for payment in payments if payment["cadence_relevant"]),
        key=lambda item: (item["date"], item["id"]),
    )
    if len(cadence_payments) < 2:
        reasons.append("insufficient payment schedule evidence to validate cadence")
    for previous, current in zip(cadence_payments, cadence_payments[1:]):
        gap = (current["date"] - previous["date"]).days
        if gap != cadence_days:
            reasons.append(
                f"irregular payment cadence between {previous['date']} and {current['date']}: {gap} days"
            )

    if cadence_payments:
        first_service_start = cadence_payments[0]["date"] + timedelta(
            days=service_offset_days
        )
        last_service_end = cadence_payments[-1]["date"] + timedelta(
            days=service_offset_days + cadence_days - 1
        )
        if first_service_start > evidence_window_start:
            reasons.append("payment evidence does not cover the start of the evidence window")
        if last_service_end < evidence_window_end:
            reasons.append("payment evidence does not cover the end of the evidence window")

    paid_by_appointment: dict[str, str] = {}
    skipped_by_appointment: dict[str, str] = {}
    payment_windows: list[dict[str, Any]] = []

    for payment in payments:
        if payment["cadence_relevant"]:
            service_start = payment["date"] + timedelta(days=service_offset_days)
            service_end = service_start + timedelta(days=cadence_days - 1)
            covered = [item for item in appointments if service_start <= item["date"] <= service_end]
            if len(covered) != sessions_per_payment:
                reasons.append(
                    f"payment {payment['id']} service window has {len(covered)} appointments; "
                    f"expected {sessions_per_payment}"
                )
        else:
            explicit_ids = payment["funded_appointment_ids"]
            covered = [item for item in appointments if item["id"] in explicit_ids]
            service_start = None
            service_end = None
            if payment["status"] == "paid" and len(covered) != len(explicit_ids):
                reasons.append(f"manual payment {payment['id']} references a missing appointment")
            if payment["status"] == "paid" and not explicit_ids:
                reasons.append(f"manual payment {payment['id']} lacks explicit appointment mapping")

        public_window = {
            "payment_id": payment["id"],
            "payment_date": payment["date"].isoformat(),
            "payment_status": payment["status"],
            "service_start": service_start.isoformat() if service_start else None,
            "service_end": service_end.isoformat() if service_end else None,
            "appointment_ids": [item["id"] for item in covered],
        }
        payment_windows.append(public_window)

        target_map = paid_by_appointment if payment["status"] == "paid" else skipped_by_appointment
        for appointment in covered:
            if appointment["id"] in paid_by_appointment or appointment["id"] in skipped_by_appointment:
                reasons.append(f"appointment {appointment['id']} maps to more than one payment window")
            target_map[appointment["id"]] = payment["id"]

    in_hold_by_id = {item["id"]: item for item in appointments if hold_start <= item["date"] <= hold_end}
    post_hold_by_id = {item["id"]: item for item in appointments if item["date"] > hold_end}
    paid_in_hold = sorted(
        (item for item_id, item in in_hold_by_id.items() if item_id in paid_by_appointment),
        key=lambda item: (item["date"], item["id"]),
    )
    unfunded_post = sorted(
        (
            item
            for item_id, item in post_hold_by_id.items()
            if item_id in skipped_by_appointment and item_id not in paid_by_appointment
        ),
        key=lambda item: (item["date"], item["id"]),
    )

    for item in paid_in_hold:
        if item["status"] != "scheduled":
            reasons.append(
                f"paid in-hold appointment {item['id']} is marked delivered; "
                "unused entitlement is ambiguous"
            )
    for item in unfunded_post:
        if item["status"] != "scheduled":
            reasons.append(
                f"post-hold target appointment {item['id']} is not scheduled"
            )

    funding = {
        "payment_windows": payment_windows,
        "paid_in_hold_appointment_ids": [item["id"] for item in paid_in_hold],
        "unfunded_post_hold_appointment_ids": [item["id"] for item in unfunded_post],
        "skipped_payment_dates": [
            item["date"].isoformat() for item in cadence_payments if item["status"] == "skipped"
        ],
    }

    if len(paid_in_hold) != len(unfunded_post):
        reasons.append(
            "boundary entitlement counts mismatch: "
            f"{len(paid_in_hold)} paid in-hold vs {len(unfunded_post)} unfunded post-hold"
        )

    existing_adjustments = (
        payload.get("existing_adjustments", [])
        if isinstance(payload.get("existing_adjustments"), list)
        else []
    )
    if existing_adjustments:
        reasons.append("existing cash/session adjustment evidence requires duplicate-credit review")

    if reasons:
        return _review_result(
            reasons=reasons,
            conversation_id=conversation_id,
            classifications=classifications,
            funding=funding,
        )

    proposed_transfers = [
        {
            "type": "pt_session_entitlement_transfer",
            "source_appointment_id": source["id"],
            "source_appointment_date": source["date"].isoformat(),
            "source_payment_id": paid_by_appointment[source["id"]],
            "target_appointment_id": target["id"],
            "target_appointment_date": target["date"].isoformat(),
            "skipped_payment_id": skipped_by_appointment[target["id"]],
            "cash_adjustment": None,
        }
        for source, target in zip(paid_in_hold, unfunded_post)
    ]

    status = "proposal_ready" if proposed_transfers else "no_transfer_needed"
    proposal_id = _proposal_id(
        conversation_id,
        hold_start,
        hold_end,
        provenance,
        proposed_transfers,
    )
    result = {
        "status": status,
        "proposal_id": proposal_id,
        "safe_to_approve": True,
        "reasons": [],
        "hold": {
            "start": hold_start.isoformat(),
            "end": hold_end.isoformat(),
            "pre_hold_billing_control_date": (
                hold_start - timedelta(days=service_offset_days)
            ).isoformat(),
            "pre_return_billing_control_date": (
                hold_end - timedelta(days=service_offset_days)
            ).isoformat(),
        },
        "evidence": {
            "window_start": evidence_window_start.isoformat(),
            "window_end": evidence_window_end.isoformat(),
            "provenance": provenance,
        },
        "classifications": classifications,
        "funding": funding,
        "proposed_transfers": proposed_transfers,
        "cash_adjustment": None,
        "mutations_performed": [],
        "approval_boundary": "human approval in existing GHL Conversation",
    }
    result["work_item"] = _work_item(conversation_id, result)
    return result
