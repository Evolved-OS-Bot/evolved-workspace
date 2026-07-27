from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from .models import Appointment, Finding, PTContact


SESSION_NUMBER = re.compile(
    r"\b(?:session\s*)?(?P<number>\d{1,3})\s*/\s*(?P<total>\d{1,3})\b",
    re.IGNORECASE,
)
NON_ACTIVE_STATUSES = {"cancelled", "canceled", "no_show", "noshow"}


@dataclass(frozen=True)
class PackMarker:
    appointment_id: str
    start: datetime
    number: int
    total: int
    status: str
    source: str

    def to_evidence(self) -> dict[str, Any]:
        return {
            "appointment_id": self.appointment_id,
            "start": self.start.isoformat(),
            "session_number": self.number,
            "pack_total": self.total,
            "status": self.status,
            "source": self.source,
        }


def marker_for(appointment: Appointment) -> PackMarker | None:
    for source, value in (
        ("description", appointment.description),
        ("notes", appointment.notes),
    ):
        match = SESSION_NUMBER.search(value or "")
        if not match:
            continue
        number = int(match.group("number"))
        total = int(match.group("total"))
        if total <= 0 or number <= 0 or number > total:
            return None
        return PackMarker(
            appointment_id=appointment.id,
            start=appointment.start,
            number=number,
            total=total,
            status=appointment.status,
            source=source,
        )
    return None


def prepaid_pack_findings(
    contact: PTContact,
    appointments: list[Appointment],
    cross_system_evidence: dict[str, Any],
    now: datetime,
    renewal_window_days: int = 21,
) -> list[Finding]:
    stripe = cross_system_evidence.get("stripe") or {}
    if contact.effective_status != "active" or not stripe.get("verified_prepaid_pack"):
        return []

    live_appointments = sorted(
        (
            appointment
            for appointment in appointments
            if not appointment.deleted
            and appointment.status not in NON_ACTIVE_STATUSES
        ),
        key=lambda appointment: appointment.start,
    )
    markers = [
        marker
        for appointment in live_appointments
        if (marker := marker_for(appointment)) is not None
    ]
    if not markers:
        return [
            Finding(
                contact_id=contact.id,
                contact_name=contact.name,
                category="PREPAID_PACK_SESSION_LEDGER_MISSING",
                reason=(
                    "A verified prepaid PT pack exists, but no valid Session X/Y "
                    "counter was found in the active appointment descriptions."
                ),
                effective_status=contact.effective_status,
                evidence={"verified_pack_payments": stripe.get("verified_pack_payments", [])},
            )
        ]

    totals = sorted({marker.total for marker in markers})
    regressions = [
        (previous, current)
        for previous, current in zip(markers, markers[1:])
        if current.total != previous.total or current.number < previous.number
    ]
    duplicate_numbers = sorted(
        {
            marker.number
            for marker in markers
            if sum(
                other.number == marker.number and other.total == marker.total
                for other in markers
            )
            > 1
        }
    )
    terminal_markers = [marker for marker in markers if marker.number == marker.total]
    first_terminal = terminal_markers[0] if terminal_markers else None
    appointments_after_terminal = (
        [
            appointment
            for appointment in live_appointments
            if first_terminal and appointment.start > first_terminal.start
        ]
        if first_terminal
        else []
    )

    common_evidence = {
        "verified_pack_payments": stripe.get("verified_pack_payments", []),
        "session_markers": [marker.to_evidence() for marker in markers],
        "pack_totals_seen": totals,
        "duplicate_session_numbers": duplicate_numbers,
        "appointments_after_first_terminal": [
            {
                "appointment_id": appointment.id,
                "start": appointment.start.isoformat(),
                "description": appointment.description,
                "status": appointment.status,
            }
            for appointment in appointments_after_terminal
        ],
    }

    if len(totals) > 1 or regressions or duplicate_numbers:
        return [
            Finding(
                contact_id=contact.id,
                contact_name=contact.name,
                category="PREPAID_PACK_SEQUENCE_REVIEW_REQUIRED",
                reason=(
                    "The verified prepaid pack has conflicting appointment counters. "
                    "Do not infer remaining entitlement until Admin corrects or "
                    "confirms the Session X/Y sequence."
                ),
                effective_status=contact.effective_status,
                evidence={
                    **common_evidence,
                    "regressions": [
                        {
                            "from": previous.to_evidence(),
                            "to": current.to_evidence(),
                        }
                        for previous, current in regressions
                    ],
                },
            )
        ]

    if first_terminal and appointments_after_terminal:
        return [
            Finding(
                contact_id=contact.id,
                contact_name=contact.name,
                category="PREPAID_PACK_BOOKINGS_AFTER_END",
                reason=(
                    f"The appointment ledger reaches Session {first_terminal.number}/"
                    f"{first_terminal.total} on {first_terminal.start.date().isoformat()}, "
                    "but later PT bookings remain. Confirm a renewal/payment or remove "
                    "the unsupported bookings."
                ),
                effective_status=contact.effective_status,
                booked_through=first_terminal.start.isoformat(),
                evidence=common_evidence,
            )
        ]

    latest = markers[-1]
    if latest.number == latest.total and latest.start <= now + timedelta(
        days=renewal_window_days
    ):
        return [
            Finding(
                contact_id=contact.id,
                contact_name=contact.name,
                category="PREPAID_PACK_RENEWAL_DUE",
                reason=(
                    f"The verified prepaid pack reaches Session {latest.number}/"
                    f"{latest.total} on {latest.start.date().isoformat()}. Confirm "
                    "renewal or restart regular debits before the final session."
                ),
                effective_status=contact.effective_status,
                booked_through=latest.start.isoformat(),
                evidence=common_evidence,
            )
        ]
    return []
