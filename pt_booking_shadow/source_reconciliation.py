from __future__ import annotations

import json
import re
import sqlite3
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any

import requests

from .config import Settings
from .google_sheets import SheetsKPIWriter
from .models import Finding, PTContact
from revenue_gap_control.sources import load_legacy_payment_csv


STRIPE_ENTITLED_STATUSES = {"active", "trialing", "past_due", "unpaid"}
CONTROLLER_RESOLVED_COMMERCIAL_STATES = {
    "CLEAN_COLLECTING",
    "ACTIVE_PIA",
    "APPROVED_PAUSE",
    "APPROVED_FUTURE_START",
    "PIF_PACK_IN_DELIVERY",
    "PACK_RENEWAL_DUE",
    "PAYMENT_CURRENT_NO_BOOKING",
    "Active - ARREARS",
}
OWNER_APPROVED_COMMERCIAL_CLASSES = {
    "external_payment_client",
    "prepaid_credit_client",
    "inactive_pt_credit",
}


def normalise_email(value: Any) -> str:
    return str(value or "").strip().lower()


def normalise_phone(value: Any) -> str:
    digits = re.sub(r"\D", "", str(value or ""))
    if digits.startswith("61") and len(digits) >= 11:
        digits = "0" + digits[2:]
    return digits


@dataclass(frozen=True)
class WorkbookPTRecord:
    name: str
    email: str
    phone: str
    trainer: str
    session_length: str
    sessions_per_week: str
    weekly_debit: str
    row_number: int

    def to_evidence(self) -> dict[str, Any]:
        return {
            "source_tab": "Active PT",
            "source_row": self.row_number,
            "trainer": self.trainer,
            "session_length": self.session_length,
            "sessions_per_week": self.sessions_per_week,
            "weekly_debit": self.weekly_debit,
        }


@dataclass(frozen=True)
class ControllerPTRecord:
    classification: str
    status: str
    payment_marker: str
    notes: str
    source_run_id: str

    def to_evidence(self) -> dict[str, Any]:
        return {
            "classification": self.classification,
            "status": self.status,
            "payment_marker": self.payment_marker,
            "notes": self.notes,
            "source_run_id": self.source_run_id,
            "commercial_state_resolved": (
                self.classification in CONTROLLER_RESOLVED_COMMERCIAL_STATES
            ),
        }


@dataclass(frozen=True)
class ApprovedAccountRecord:
    classification: str
    confirmed_by: str
    confirmed_date: str
    note: str

    @property
    def supports_commercial_status(self) -> bool:
        return self.classification in OWNER_APPROVED_COMMERCIAL_CLASSES

    def supports_commercial_status_as_of(
        self, as_of: date, max_age_days: int = 14
    ) -> bool:
        if not self.supports_commercial_status:
            return False
        if self.classification != "external_payment_client":
            return True
        try:
            confirmed = date.fromisoformat(self.confirmed_date[:10])
        except (TypeError, ValueError):
            return False
        age = (as_of - confirmed).days
        return 0 <= age <= max_age_days

    def to_evidence(self, as_of: date) -> dict[str, Any]:
        return {
            "classification": self.classification,
            "confirmed_by": self.confirmed_by,
            "confirmed_date": self.confirmed_date,
            "note": self.note,
            "commercial_status_supported": (
                self.supports_commercial_status_as_of(as_of)
            ),
        }


@dataclass(frozen=True)
class StripeOneOffPayment:
    payment_intent_id: str
    customer_id: str
    payer_email: str
    amount_received: int
    currency: str
    created: int
    beneficiary_contact_id: str | None = None

    def to_evidence(self) -> dict[str, Any]:
        return {
            "payment_intent_id": self.payment_intent_id,
            "payer_customer_id": self.customer_id,
            "amount_received": self.amount_received,
            "currency": self.currency,
            "created": self.created,
            "beneficiary_match_method": (
                "approved_payment_to_contact_map"
                if self.beneficiary_contact_id
                else "payer_email"
            ),
        }


@dataclass
class CrossSystemSnapshot:
    stripe_statuses_by_email: dict[str, list[str]] = field(default_factory=dict)
    stripe_entitled_emails: set[str] = field(default_factory=set)
    stripe_one_off_payments_by_email: dict[str, list[StripeOneOffPayment]] = field(
        default_factory=dict
    )
    stripe_pack_payments_by_contact_id: dict[
        str, list[StripeOneOffPayment]
    ] = field(default_factory=dict)
    trainerize_active_emails: set[str] = field(default_factory=set)
    workbook_by_email: dict[str, WorkbookPTRecord] = field(default_factory=dict)
    workbook_by_phone: dict[str, WorkbookPTRecord] = field(default_factory=dict)
    identity_aliases_by_email: dict[str, set[str]] = field(default_factory=dict)
    legacy_payment_by_email: dict[str, Any] = field(default_factory=dict)
    controller_pt_by_email: dict[str, ControllerPTRecord] = field(default_factory=dict)
    approved_account_by_email: dict[str, ApprovedAccountRecord] = field(
        default_factory=dict
    )
    as_of: date = field(default_factory=date.today)

    def evidence_for(self, contact: PTContact) -> dict[str, Any]:
        email = normalise_email(contact.email)
        matched_emails = sorted(
            {email, *self.identity_aliases_by_email.get(email, set())} - {""}
        )
        phone = normalise_phone(contact.phone)
        workbook = next(
            (
                self.workbook_by_email[candidate]
                for candidate in matched_emails
                if candidate in self.workbook_by_email
            ),
            None,
        )
        if workbook is None and phone:
            workbook = self.workbook_by_phone.get(phone)
        payer_matched_payments = [
            payment
            for candidate in matched_emails
            for payment in self.stripe_one_off_payments_by_email.get(candidate, [])
        ]
        verified_pack_payments = self.stripe_pack_payments_by_contact_id.get(
            contact.id, []
        )
        recurring_entitled = any(
            candidate in self.stripe_entitled_emails for candidate in matched_emails
        )
        legacy = next(
            (
                self.legacy_payment_by_email[candidate]
                for candidate in matched_emails
                if candidate in self.legacy_payment_by_email
            ),
            None,
        )
        legacy_collecting = bool(legacy and legacy.collecting_as_of(self.as_of))
        controller = next(
            (
                self.controller_pt_by_email[candidate]
                for candidate in matched_emails
                if candidate in self.controller_pt_by_email
            ),
            None,
        )
        approved_account = next(
            (
                self.approved_account_by_email[candidate]
                for candidate in matched_emails
                if candidate in self.approved_account_by_email
            ),
            None,
        )
        controller_resolved = bool(
            controller
            and controller.classification in CONTROLLER_RESOLVED_COMMERCIAL_STATES
        )
        owner_approved = bool(
            approved_account
            and approved_account.supports_commercial_status_as_of(self.as_of)
        )
        commercial_supported = (
            recurring_entitled
            or bool(verified_pack_payments)
            or legacy_collecting
            or controller_resolved
            or owner_approved
        )
        return {
            "identity_match": {
                "email_available": bool(email),
                "matched_emails": matched_emails,
                "approved_alias_used": any(
                    candidate != email for candidate in matched_emails
                ),
                "phone_available": bool(phone),
                "workbook_match_method": (
                    "email"
                    if workbook
                    and any(
                        self.workbook_by_email.get(candidate) is workbook
                        for candidate in matched_emails
                    )
                    else "phone" if workbook else None
                ),
            },
            "stripe": {
                "entitled": recurring_entitled or bool(verified_pack_payments),
                "recurring_entitled": recurring_entitled,
                "verified_prepaid_pack": bool(verified_pack_payments),
                "statuses": sorted(
                    {
                        status
                        for candidate in matched_emails
                        for status in self.stripe_statuses_by_email.get(candidate, [])
                    }
                ),
                "one_off_payments": [
                    payment.to_evidence() for payment in payer_matched_payments
                ],
                "verified_pack_payments": [
                    payment.to_evidence() for payment in verified_pack_payments
                ],
            },
            "trainerize": {
                "active_access": any(
                    candidate in self.trainerize_active_emails
                    for candidate in matched_emails
                )
            },
            "brown_casserly": {
                "active_pt_record": bool(workbook),
                "record": workbook.to_evidence() if workbook else None,
            },
            "legacy_payment": {
                "current_collecting_evidence": legacy_collecting,
                "record": (
                    {
                        "rail": legacy.rail,
                        "status": legacy.status,
                        "weekly_amount": (
                            str(legacy.weekly_amount)
                            if legacy.weekly_amount is not None
                            else None
                        ),
                        "last_receipt_date": legacy.last_receipt_date,
                        "next_due_date": legacy.next_due_date,
                        "notes": legacy.notes,
                    }
                    if legacy
                    else None
                ),
            },
            "revenue_controller": {
                "record": controller.to_evidence() if controller else None,
            },
            "approved_account": {
                "record": (
                    approved_account.to_evidence(self.as_of)
                    if approved_account
                    else None
                ),
            },
            "commercial": {
                "supported": commercial_supported,
                "supporting_sources": [
                    source
                    for source, present in (
                        ("stripe", recurring_entitled or bool(verified_pack_payments)),
                        ("ptminder_ezidebit", legacy_collecting),
                        ("revenue_controller", controller_resolved),
                        ("owner_approved_account", owner_approved),
                    )
                    if present
                ],
            },
        }


def load_identity_aliases(path: Path) -> dict[str, set[str]]:
    if not path.exists():
        return {}
    import csv

    groups: dict[str, set[str]] = {}
    with path.open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            canonical = normalise_email(row.get("canonical_email"))
            linked = normalise_email(row.get("linked_email"))
            if not canonical or not linked:
                continue
            combined = {canonical, linked}
            combined.update(groups.get(canonical, set()))
            combined.update(groups.get(linked, set()))
            for item in combined:
                groups[item] = set(combined - {item})
    return groups


def load_approved_accounts(path: Path) -> dict[str, ApprovedAccountRecord]:
    if not path.exists():
        return {}
    import csv

    result: dict[str, ApprovedAccountRecord] = {}
    with path.open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            email = normalise_email(row.get("email"))
            approved = str(
                row.get("approved_active_without_local_entitlement") or ""
            ).strip().lower() in {"1", "true", "yes"}
            if not email or not approved:
                continue
            result[email] = ApprovedAccountRecord(
                classification=str(row.get("classification") or "").strip().lower(),
                confirmed_by=str(row.get("confirmed_by") or "").strip(),
                confirmed_date=str(row.get("confirmed_date") or "").strip(),
                note=str(row.get("note") or "").strip(),
            )
    return result


def load_controller_pt_records(path: Path) -> dict[str, ControllerPTRecord]:
    if not path.exists():
        return {}
    try:
        connection = sqlite3.connect(path)
        connection.row_factory = sqlite3.Row
        run = connection.execute(
            """
            SELECT run_id
            FROM runs
            WHERE status='complete'
            ORDER BY completed_at DESC
            LIMIT 1
            """
        ).fetchone()
        if run is None:
            return {}
        rows = connection.execute(
            """
            SELECT email, classification, status, payment_marker, notes
            FROM roster_snapshot
            WHERE run_id=? AND service='PT' AND email != ''
            """,
            (run["run_id"],),
        ).fetchall()
        return {
            normalise_email(row["email"]): ControllerPTRecord(
                classification=str(row["classification"] or ""),
                status=str(row["status"] or ""),
                payment_marker=str(row["payment_marker"] or ""),
                notes=str(row["notes"] or ""),
                source_run_id=str(run["run_id"]),
            )
            for row in rows
            if normalise_email(row["email"])
        }
    except sqlite3.Error:
        return {}
    finally:
        if "connection" in locals():
            connection.close()


class StripeEntitlementReader:
    base_url = "https://api.stripe.com/v1"

    def __init__(self, key: str, timeout: int = 30):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.auth = (key, "")

    def _collection(self, resource: str, params=None) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        query = {"limit": 100, **(params or {})}
        while True:
            response = self.session.get(
                f"{self.base_url}/{resource}", params=query, timeout=self.timeout
            )
            response.raise_for_status()
            payload = response.json()
            batch = [item for item in payload.get("data") or [] if isinstance(item, dict)]
            rows.extend(batch)
            if not payload.get("has_more") or not batch:
                return rows
            query["starting_after"] = batch[-1]["id"]

    def snapshot(
        self,
        beneficiary_map: dict[str, str] | None = None,
        lookback_days: int = 365,
    ) -> tuple[
        dict[str, list[str]],
        set[str],
        dict[str, list[StripeOneOffPayment]],
        dict[str, list[StripeOneOffPayment]],
    ]:
        customers = self._collection("customers")
        subscriptions = self._collection("subscriptions", {"status": "all"})
        payment_intents = self._collection(
            "payment_intents",
            {"created[gte]": int(time.time()) - (lookback_days * 86400)},
        )
        beneficiary_map = beneficiary_map or {}
        email_by_customer = {
            str(item.get("id")): normalise_email(item.get("email"))
            for item in customers
            if item.get("id") and normalise_email(item.get("email"))
        }
        statuses: dict[str, set[str]] = defaultdict(set)
        entitled: set[str] = set()
        for subscription in subscriptions:
            email = email_by_customer.get(str(subscription.get("customer") or ""))
            status = str(subscription.get("status") or "").strip().lower()
            if not email or not status:
                continue
            statuses[email].add(status)
            if status in STRIPE_ENTITLED_STATUSES:
                entitled.add(email)
        one_off_by_email: dict[str, list[StripeOneOffPayment]] = defaultdict(list)
        pack_by_contact_id: dict[str, list[StripeOneOffPayment]] = defaultdict(list)
        for payment_intent in payment_intents:
            if str(payment_intent.get("status") or "").lower() != "succeeded":
                continue
            if int(payment_intent.get("amount_received") or 0) <= 0:
                continue
            if payment_intent.get("invoice"):
                continue
            payment_id = str(payment_intent.get("id") or "")
            customer_id = str(payment_intent.get("customer") or "")
            payer_email = email_by_customer.get(customer_id, "")
            beneficiary_contact_id = beneficiary_map.get(payment_id)
            if not payment_id or (not payer_email and not beneficiary_contact_id):
                continue
            payment = StripeOneOffPayment(
                payment_intent_id=payment_id,
                customer_id=customer_id,
                payer_email=payer_email,
                amount_received=int(payment_intent.get("amount_received") or 0),
                currency=str(payment_intent.get("currency") or "").lower(),
                created=int(payment_intent.get("created") or 0),
                beneficiary_contact_id=beneficiary_contact_id,
            )
            if payer_email:
                one_off_by_email[payer_email].append(payment)
            if beneficiary_contact_id:
                pack_by_contact_id[beneficiary_contact_id].append(payment)
        return (
            {email: sorted(values) for email, values in statuses.items()},
            entitled,
            dict(one_off_by_email),
            dict(pack_by_contact_id),
        )


class TrainerizeAccessReader:
    def __init__(
        self,
        group_id: str,
        api_token: str,
        base_url: str,
        location_id: int,
        timeout: int = 30,
    ):
        self.base_url = base_url.rstrip("/")
        self.location_id = location_id
        self.timeout = timeout
        self.session = requests.Session()
        self.session.auth = (group_id, api_token)
        self.session.headers.update(
            {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "The-Evolved-PT-Booking-Shadow/1.0",
            }
        )

    def active_emails(self) -> set[str]:
        emails: set[str] = set()
        start = 0
        while True:
            response = self.session.post(
                f"{self.base_url}/user/getClientList",
                json={
                    "view": "activeClient",
                    "sort": "name",
                    "start": start,
                    "count": 100,
                    "verbose": True,
                    "locationID": self.location_id,
                },
                timeout=self.timeout,
            )
            response.raise_for_status()
            payload = response.json()
            batch = [item for item in payload.get("users") or [] if isinstance(item, dict)]
            emails.update(
                normalise_email(item.get("email"))
                for item in batch
                if normalise_email(item.get("email"))
            )
            total = int(payload.get("total") or 0)
            if not batch or start + len(batch) >= total:
                return emails
            start += len(batch)


class BrownCasserlyReader:
    def __init__(self, settings: Settings):
        self.sheets = SheetsKPIWriter(settings)

    def active_pt(self) -> tuple[dict[str, WorkbookPTRecord], dict[str, WorkbookPTRecord]]:
        rows = self.sheets.read_values("Active PT", "A1:K500")
        if not rows:
            raise RuntimeError("Brown & Casserly Active PT tab is empty")
        header = [str(value).strip() for value in rows[0]]
        expected = {
            "First Name",
            "Last Name",
            "Phone",
            "Email",
            "Personal Trainer",
            "Session Length",
            "Sessions p/wk",
            "Weekly Debit",
        }
        missing = expected - set(header)
        if missing:
            raise RuntimeError(f"Active PT tab is missing columns: {sorted(missing)}")
        index = {name: header.index(name) for name in expected}
        by_email: dict[str, WorkbookPTRecord] = {}
        by_phone: dict[str, WorkbookPTRecord] = {}
        for row_number, row in enumerate(rows[1:], start=2):
            def cell(name: str) -> str:
                position = index[name]
                return str(row[position]).strip() if position < len(row) else ""

            email = normalise_email(cell("Email"))
            phone = normalise_phone(cell("Phone"))
            if not email and not phone:
                continue
            record = WorkbookPTRecord(
                name=f"{cell('First Name')} {cell('Last Name')}".strip(),
                email=email,
                phone=phone,
                trainer=cell("Personal Trainer"),
                session_length=cell("Session Length"),
                sessions_per_week=cell("Sessions p/wk"),
                weekly_debit=cell("Weekly Debit"),
                row_number=row_number,
            )
            if email:
                by_email[email] = record
            if phone:
                by_phone[phone] = record
        return by_email, by_phone


def build_cross_system_snapshot(settings: Settings) -> CrossSystemSnapshot:
    if not settings.stripe_restricted_key:
        raise RuntimeError("STRIPE_RESTRICTED_KEY is required")
    if not settings.trainerize_group_id or not settings.trainerize_api_token:
        raise RuntimeError("Trainerize credentials are required")
    if settings.trainerize_location_id is None:
        raise RuntimeError("TRAINERIZE_LOCATION_ID is required")

    try:
        beneficiary_map = json.loads(
            settings.stripe_pt_pack_beneficiary_map_json or "{}"
        )
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "STRIPE_PT_PACK_BENEFICIARY_MAP_JSON must be valid JSON"
        ) from exc
    if not isinstance(beneficiary_map, dict) or not all(
        isinstance(payment_id, str) and isinstance(contact_id, str)
        for payment_id, contact_id in beneficiary_map.items()
    ):
        raise RuntimeError(
            "STRIPE_PT_PACK_BENEFICIARY_MAP_JSON must map payment IDs to contact IDs"
        )
    (
        statuses,
        entitled,
        one_off_by_email,
        pack_by_contact_id,
    ) = StripeEntitlementReader(settings.stripe_restricted_key).snapshot(
        beneficiary_map,
        settings.stripe_pt_pack_lookback_days,
    )
    trainerize_active = TrainerizeAccessReader(
        settings.trainerize_group_id,
        settings.trainerize_api_token,
        settings.trainerize_api_base_url,
        settings.trainerize_location_id,
    ).active_emails()
    workbook_email, workbook_phone = BrownCasserlyReader(settings).active_pt()
    revenue_dir = Path(settings.revenue_gap_data_dir)
    identity_aliases = load_identity_aliases(revenue_dir / "identity-links.csv")
    legacy_payments = load_legacy_payment_csv(
        revenue_dir / "legacy-payment-evidence.csv"
    )
    controller_pt = load_controller_pt_records(revenue_dir / "revenue_gap.sqlite")
    approved_accounts = load_approved_accounts(
        revenue_dir / "account-classifications.csv"
    )
    return CrossSystemSnapshot(
        stripe_statuses_by_email=statuses,
        stripe_entitled_emails=entitled,
        stripe_one_off_payments_by_email=one_off_by_email,
        stripe_pack_payments_by_contact_id=pack_by_contact_id,
        trainerize_active_emails=trainerize_active,
        workbook_by_email=workbook_email,
        workbook_by_phone=workbook_phone,
        identity_aliases_by_email=identity_aliases,
        legacy_payment_by_email=legacy_payments,
        controller_pt_by_email=controller_pt,
        approved_account_by_email=approved_accounts,
        as_of=datetime.now(settings.timezone).date(),
    )


def cross_system_findings(
    contact: PTContact,
    evidence: dict[str, Any],
    has_future_booking: bool,
) -> list[Finding]:
    if contact.effective_status != "active":
        return []
    stripe = evidence["stripe"]
    trainerize = evidence["trainerize"]
    workbook = evidence["brown_casserly"]
    identity = evidence["identity_match"]
    commercial = evidence["commercial"]
    findings: list[Finding] = []

    if not identity["email_available"]:
        findings.append(
            Finding(
                contact_id=contact.id,
                contact_name=contact.name,
                category="CROSS_SYSTEM_IDENTITY_REVIEW",
                reason=(
                    "Active PT contact has no email, so Stripe and Trainerize cannot "
                    "be reconciled deterministically."
                ),
                effective_status=contact.effective_status,
                expected_frequency=contact.expected_frequency,
                evidence=evidence,
            )
        )
        return findings

    if (
        workbook["active_pt_record"]
        and not commercial["supported"]
        and stripe["one_off_payments"]
    ):
        findings.append(
            Finding(
                contact_id=contact.id,
                contact_name=contact.name,
                category="STRIPE_PREPAID_PAYMENT_REVIEW_REQUIRED",
                reason=(
                    "Brown & Casserly lists active PT and Stripe has a successful "
                    "one-off payment for the same payer email, but the payment has "
                    "not been verified as this client's PT pack."
                ),
                effective_status=contact.effective_status,
                expected_frequency=contact.expected_frequency,
                evidence=evidence,
            )
        )
    elif workbook["active_pt_record"] and not commercial["supported"]:
        findings.append(
            Finding(
                contact_id=contact.id,
                contact_name=contact.name,
                category="COMMERCIAL_EVIDENCE_REVIEW_REQUIRED",
                reason=(
                    "Brown & Casserly lists active PT, but no entitled Stripe "
                    "subscription or verified prepaid-pack payment was found. Check "
                    "the payer, pack beneficiary or workbook record."
                ),
                effective_status=contact.effective_status,
                expected_frequency=contact.expected_frequency,
                evidence=evidence,
            )
        )
    if has_future_booking and not trainerize["active_access"]:
        findings.append(
            Finding(
                contact_id=contact.id,
                contact_name=contact.name,
                category="TRAINERIZE_ACCESS_REVIEW_REQUIRED",
                reason=(
                    "The client has future GHL PT bookings but no matching active "
                    "Trainerize account."
                ),
                effective_status=contact.effective_status,
                expected_frequency=contact.expected_frequency,
                evidence=evidence,
            )
        )
    if has_future_booking and not workbook["active_pt_record"]:
        findings.append(
            Finding(
                contact_id=contact.id,
                contact_name=contact.name,
                category="WORKBOOK_PT_RECORD_MISSING",
                reason=(
                    "The client has future GHL PT bookings but no matching Active PT "
                    "row in Brown & Casserly."
                ),
                effective_status=contact.effective_status,
                expected_frequency=contact.expected_frequency,
                evidence=evidence,
            )
        )
    return findings


BOOKING_GAP_CATEGORIES = {
    "NO_FUTURE_BOOKINGS",
    "GAP_INSIDE_SERIES",
    "WOULD_TOP_UP",
}


def reconcile_primary_with_cross_system_evidence(
    primary: Finding,
    contact: PTContact,
    evidence: dict[str, Any],
    has_future_booking: bool,
) -> Finding:
    """Prevent booking actions when lifecycle evidence owns the exception."""
    if contact.effective_status != "active" or primary.category not in BOOKING_GAP_CATEGORIES:
        return primary

    controller = evidence.get("revenue_controller", {}).get("record") or {}
    if controller.get("classification") == "APPROVED_PAUSE":
        primary.category = "PT_HOLD_ACTIVE"
        primary.reason = (
            "The shared revenue controller confirms an approved payment or "
            "lifecycle pause. Booking top-ups are suppressed until the pause is resolved."
        )
        primary.proposed_dates = []
        primary.evidence["cross_system_state_override"] = "APPROVED_PAUSE"
        return primary

    workbook_active = bool(
        evidence.get("brown_casserly", {}).get("active_pt_record")
    )
    commercial_supported = bool(
        evidence.get("commercial", {}).get("supported")
    )
    trainerize_active = bool(
        evidence.get("trainerize", {}).get("active_access")
    )
    if (
        not has_future_booking
        and not workbook_active
        and not commercial_supported
        and not trainerize_active
    ):
        primary.category = "GHL_ONLY_PT_RECORD_REVIEW"
        primary.reason = (
            "GHL is the only source indicating this is a current PT client. "
            "There is no future PT booking, Active PT workbook row, supported "
            "payment evidence or active Trainerize access. Confirm stale/test "
            "status instead of rebooking."
        )
        primary.proposed_dates = []
        primary.evidence["cross_system_state_override"] = "GHL_ONLY_PT_RECORD"
    return primary
