from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Any


ACTIVE = "Active"
ACTIVE_PIA = "Active - PIA"
ACTIVE_ARREARS = "Active - ARREARS"

CLEAN_COLLECTING = "CLEAN_COLLECTING"
CLASS_ACTIVE_PIA = "ACTIVE_PIA"
APPROVED_PAUSE = "APPROVED_PAUSE"
APPROVED_FUTURE_START = "APPROVED_FUTURE_START"
PIF_PACK_IN_DELIVERY = "PIF_PACK_IN_DELIVERY"
PACK_RENEWAL_DUE = "PACK_RENEWAL_DUE"
PAYMENT_CURRENT_NO_BOOKING = "PAYMENT_CURRENT_NO_BOOKING"
BOOKING_PAYMENT_UNRESOLVED = "BOOKING_PAYMENT_UNRESOLVED"
REFUND_REMOVE_FROM_ACTIVE = "REFUND_REMOVE_FROM_ACTIVE"
DOWNGRADE_RECONCILIATION_REQUIRED = "DOWNGRADE_RECONCILIATION_REQUIRED"
LIFECYCLE_EXCEPTION = "LIFECYCLE_EXCEPTION"
SOURCE_READ_FAILURE = "SOURCE_READ_FAILURE"
FAST_TRACK_PAIR_MISSING = "FAST_TRACK_PAIR_MISSING"
FAST_TRACK_ALLOCATION_MISMATCH = "FAST_TRACK_ALLOCATION_MISMATCH"


@dataclass(frozen=True)
class RosterRecord:
    service: str
    row_number: int
    first_name: str
    last_name: str
    email: str
    phone: str
    status: str
    weekly_allocation: Decimal | None
    payment_marker: str
    product: str = ""
    trainer: str = ""
    session_length: str = ""
    sessions_per_week: str = ""
    session_cost: Decimal | None = None
    notes: str = ""
    contract_length: str = ""
    renewal_date: str = ""

    @property
    def name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def is_fast_track_component(self) -> bool:
        return "fast track" in f"{self.product} {self.notes}".lower()


@dataclass
class SourceEvidence:
    email: str
    ghl_contact_ids: list[str] = field(default_factory=list)
    stripe_statuses: list[str] = field(default_factory=list)
    latest_invoice_status: str = ""
    latest_invoice_paid: bool = False
    latest_receipt_date: str = ""
    pause_collection: bool = False
    trainerize_active: bool = False
    membership_type: str = ""
    membership_stage: str = ""
    cancellation_status: str = ""
    final_access_date: str = ""
    hold_status: str = ""
    booking_category: str = ""
    booked_through: str = ""
    last_completed: str = ""
    last_future: str = ""
    has_future_booking: bool | None = None
    source_run_id: str = ""
    raw: dict[str, Any] = field(default_factory=dict)

    @property
    def has_current_subscription(self) -> bool:
        return any(
            value in {"active", "trialing"}
            for value in (item.lower() for item in self.stripe_statuses)
        )

    @property
    def has_payment_recovery_status(self) -> bool:
        statuses = {item.lower() for item in self.stripe_statuses}
        return bool(statuses & {"past_due", "unpaid", "incomplete"})

    @property
    def collecting_receipt_confirmed(self) -> bool:
        return (
            self.has_current_subscription
            and not self.pause_collection
            and self.latest_invoice_paid
            and self.latest_invoice_status.lower() == "paid"
        )


@dataclass(frozen=True)
class LegacyPaymentEvidence:
    email: str
    rail: str
    status: str
    weekly_amount: Decimal | None = None
    last_receipt_date: str = ""
    next_due_date: str = ""
    notes: str = ""

    @property
    def collecting(self) -> bool:
        return self.status.strip().lower() in {
            "collecting",
            "active",
            "paid",
            "paid_in_advance",
            "pif",
        }

    def collecting_as_of(self, as_of: date, max_age_days: int = 14) -> bool:
        status = self.status.strip().lower()
        if status in {"paid_in_advance", "pif"}:
            return True
        if status not in {"collecting", "active", "paid"}:
            return False
        try:
            receipt_date = date.fromisoformat(self.last_receipt_date[:10])
        except (TypeError, ValueError):
            return False
        age = (as_of - receipt_date).days
        return 0 <= age <= max_age_days


@dataclass(frozen=True)
class TimingItem:
    label: str
    amount: Decimal
    email: str = ""
    category: str = ""
    receipt_date: str = ""
    service_week: str = ""
    owner: str = ""
    next_action: str = ""
    due_date: str = ""


@dataclass
class AuditException:
    email: str
    client_name: str
    service: str
    classification: str
    summary: str
    financial_value: Decimal = Decimal("0")
    evidence_checked: list[str] = field(default_factory=list)
    owner: str = "Admin Eve"
    next_action: str = ""
    due_date: str = ""
    source_row: int | None = None


@dataclass
class ClientAssessment:
    roster: RosterRecord
    evidence: SourceEvidence
    classification: str
    reasons: list[str] = field(default_factory=list)
    included_in_confirmed_income: bool = False
    included_in_scheduled_run_rate: bool = False


@dataclass(frozen=True)
class AuditInputs:
    window_start: date
    window_end: date
    cleared_cash: Decimal
    roster: list[RosterRecord]
    evidence_by_email: dict[str, SourceEvidence]
    legacy_evidence_by_email: dict[str, LegacyPaymentEvidence] = field(
        default_factory=dict
    )
    timing_items: list[TimingItem] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)
    cash_label: str = ""


@dataclass
class CashBridge:
    sgpt_numeric_allocation: Decimal = Decimal("0")
    pt_numeric_allocation: Decimal = Decimal("0")
    combined_numeric_allocation: Decimal = Decimal("0")
    pif_rows: int = 0
    approved_pauses: Decimal = Decimal("0")
    arrears: Decimal = Decimal("0")
    future_starts: Decimal = Decimal("0")
    confirmed_current_income: Decimal = Decimal("0")
    scheduled_run_rate: Decimal = Decimal("0")
    cleared_cash: Decimal = Decimal("0")
    timing_items: Decimal = Decimal("0")
    unexplained_variance: Decimal = Decimal("0")


@dataclass
class AuditResult:
    run_id: str
    window_start: date
    window_end: date
    assessments: list[ClientAssessment]
    exceptions: list[AuditException]
    bridge: CashBridge
    limitations: list[str]
    status_counts: dict[str, int]
    duplicate_emails: list[str]
