from __future__ import annotations

import json
import re
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

import requests

from .config import Settings
from .google_sheets import SheetsKPIWriter
from .models import Finding, PTContact


STRIPE_ENTITLED_STATUSES = {"active", "trialing", "past_due", "unpaid"}


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

    def evidence_for(self, contact: PTContact) -> dict[str, Any]:
        email = normalise_email(contact.email)
        phone = normalise_phone(contact.phone)
        workbook = self.workbook_by_email.get(email) if email else None
        if workbook is None and phone:
            workbook = self.workbook_by_phone.get(phone)
        payer_matched_payments = (
            self.stripe_one_off_payments_by_email.get(email, []) if email else []
        )
        verified_pack_payments = self.stripe_pack_payments_by_contact_id.get(
            contact.id, []
        )
        recurring_entitled = (
            email in self.stripe_entitled_emails if email else False
        )
        return {
            "identity_match": {
                "email_available": bool(email),
                "phone_available": bool(phone),
                "workbook_match_method": (
                    "email"
                    if workbook and email and self.workbook_by_email.get(email) is workbook
                    else "phone" if workbook else None
                ),
            },
            "stripe": {
                "entitled": recurring_entitled or bool(verified_pack_payments),
                "recurring_entitled": recurring_entitled,
                "verified_prepaid_pack": bool(verified_pack_payments),
                "statuses": self.stripe_statuses_by_email.get(email, []) if email else [],
                "one_off_payments": [
                    payment.to_evidence() for payment in payer_matched_payments
                ],
                "verified_pack_payments": [
                    payment.to_evidence() for payment in verified_pack_payments
                ],
            },
            "trainerize": {
                "active_access": email in self.trainerize_active_emails if email else False
            },
            "brown_casserly": {
                "active_pt_record": bool(workbook),
                "record": workbook.to_evidence() if workbook else None,
            },
        }


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
    return CrossSystemSnapshot(
        stripe_statuses_by_email=statuses,
        stripe_entitled_emails=entitled,
        stripe_one_off_payments_by_email=one_off_by_email,
        stripe_pack_payments_by_contact_id=pack_by_contact_id,
        trainerize_active_emails=trainerize_active,
        workbook_by_email=workbook_email,
        workbook_by_phone=workbook_phone,
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
        and not stripe["entitled"]
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
    elif workbook["active_pt_record"] and not stripe["entitled"]:
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
