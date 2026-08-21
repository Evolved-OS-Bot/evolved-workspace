from datetime import date

from pt_booking_shadow.models import PTContact
from pt_booking_shadow.source_reconciliation import (
    ApprovedAccountRecord,
    ControllerPTRecord,
    CrossSystemSnapshot,
    StripeEntitlementReader,
    StripeOneOffPayment,
    WorkbookPTRecord,
    cross_system_findings,
    normalise_phone,
    reconcile_primary_with_cross_system_evidence,
)
from pt_booking_shadow.models import Finding
from revenue_gap_control.models import LegacyPaymentEvidence


def active_contact(**overrides):
    values = {
        "id": "contact-1",
        "name": "Test Client",
        "email": "test@example.com",
        "phone": "0412 345 678",
        "tags": {"personal training"},
        "custom_fields": {},
        "effective_status": "active",
        "expected_frequency": 2,
    }
    values.update(overrides)
    return PTContact(**values)


def workbook_record():
    return WorkbookPTRecord(
        name="Test Client",
        email="test@example.com",
        phone="0412345678",
        trainer="Piper Mae",
        session_length="30 mins",
        sessions_per_week="2",
        weekly_debit="$120.00",
        row_number=12,
    )


def test_phone_normalisation_handles_australian_country_code():
    assert normalise_phone("+61 412 345 678") == "0412345678"


def test_snapshot_matches_workbook_by_email_and_exposes_all_sources():
    snapshot = CrossSystemSnapshot(
        stripe_statuses_by_email={"test@example.com": ["active"]},
        stripe_entitled_emails={"test@example.com"},
        trainerize_active_emails={"test@example.com"},
        workbook_by_email={"test@example.com": workbook_record()},
    )

    evidence = snapshot.evidence_for(active_contact())

    assert evidence["stripe"]["entitled"] is True
    assert evidence["trainerize"]["active_access"] is True
    assert evidence["brown_casserly"]["active_pt_record"] is True
    assert evidence["identity_match"]["workbook_match_method"] == "email"


def test_missing_commercial_and_access_evidence_creates_review_findings():
    snapshot = CrossSystemSnapshot(
        workbook_by_email={"test@example.com": workbook_record()}
    )
    contact = active_contact()
    evidence = snapshot.evidence_for(contact)

    findings = cross_system_findings(contact, evidence, has_future_booking=True)
    categories = {item.category for item in findings}

    assert "COMMERCIAL_EVIDENCE_REVIEW_REQUIRED" in categories
    assert "TRAINERIZE_ACCESS_REVIEW_REQUIRED" in categories
    assert "WORKBOOK_PT_RECORD_MISSING" not in categories


def test_future_booking_without_workbook_row_is_visible():
    contact = active_contact()
    evidence = CrossSystemSnapshot(
        stripe_entitled_emails={contact.email},
        trainerize_active_emails={contact.email},
    ).evidence_for(contact)

    findings = cross_system_findings(contact, evidence, has_future_booking=True)

    assert [item.category for item in findings] == ["WORKBOOK_PT_RECORD_MISSING"]


def test_verified_third_party_pack_payment_entitles_the_beneficiary():
    contact = active_contact(id="shaanta-contact")
    payment = StripeOneOffPayment(
        payment_intent_id="pi_pack",
        customer_id="cus_archer",
        payer_email="archer@example.com",
        amount_received=240000,
        currency="aud",
        created=1783746837,
        beneficiary_contact_id=contact.id,
    )
    snapshot = CrossSystemSnapshot(
        stripe_pack_payments_by_contact_id={contact.id: [payment]},
        workbook_by_email={contact.email: workbook_record()},
    )

    evidence = snapshot.evidence_for(contact)
    findings = cross_system_findings(contact, evidence, has_future_booking=True)

    assert evidence["stripe"]["entitled"] is True
    assert evidence["stripe"]["recurring_entitled"] is False
    assert evidence["stripe"]["verified_prepaid_pack"] is True
    assert not any(
        item.category
        in {
            "COMMERCIAL_EVIDENCE_REVIEW_REQUIRED",
            "STRIPE_PREPAID_PAYMENT_REVIEW_REQUIRED",
        }
        for item in findings
    )


def test_unverified_same_email_one_off_payment_creates_pack_review():
    contact = active_contact()
    payment = StripeOneOffPayment(
        payment_intent_id="pi_unverified",
        customer_id="cus_client",
        payer_email=contact.email,
        amount_received=120000,
        currency="aud",
        created=1783746837,
    )
    snapshot = CrossSystemSnapshot(
        stripe_one_off_payments_by_email={contact.email: [payment]},
        workbook_by_email={contact.email: workbook_record()},
    )

    findings = cross_system_findings(
        contact, snapshot.evidence_for(contact), has_future_booking=False
    )

    assert [item.category for item in findings] == [
        "STRIPE_PREPAID_PAYMENT_REVIEW_REQUIRED"
    ]


def test_current_legacy_receipt_satisfies_commercial_evidence():
    contact = active_contact()
    snapshot = CrossSystemSnapshot(
        workbook_by_email={contact.email: workbook_record()},
        legacy_payment_by_email={
            contact.email: LegacyPaymentEvidence(
                email=contact.email,
                rail="PTMinder/EziDebit",
                status="collecting",
                weekly_amount=None,
                last_receipt_date="2026-07-22",
                next_due_date="2026-07-29",
            )
        },
        as_of=date(2026, 7, 27),
    )

    evidence = snapshot.evidence_for(contact)
    findings = cross_system_findings(contact, evidence, has_future_booking=True)

    assert evidence["commercial"]["supported"] is True
    assert evidence["commercial"]["supporting_sources"] == ["ptminder_ezidebit"]
    assert "COMMERCIAL_EVIDENCE_REVIEW_REQUIRED" not in {
        item.category for item in findings
    }


def test_identity_alias_reuses_stripe_entitlement():
    contact = active_contact(email="canonical@example.com")
    snapshot = CrossSystemSnapshot(
        stripe_statuses_by_email={"stripe@example.com": ["active"]},
        stripe_entitled_emails={"stripe@example.com"},
        workbook_by_email={"canonical@example.com": workbook_record()},
        identity_aliases_by_email={
            "canonical@example.com": {"stripe@example.com"},
            "stripe@example.com": {"canonical@example.com"},
        },
    )

    evidence = snapshot.evidence_for(contact)

    assert evidence["stripe"]["entitled"] is True
    assert evidence["identity_match"]["approved_alias_used"] is True
    assert evidence["commercial"]["supported"] is True


def test_resolved_revenue_controller_state_prevents_duplicate_generic_review():
    contact = active_contact()
    snapshot = CrossSystemSnapshot(
        workbook_by_email={contact.email: workbook_record()},
        controller_pt_by_email={
            contact.email: ControllerPTRecord(
                classification="APPROVED_FUTURE_START",
                status="Active",
                payment_marker="$50.00",
                notes="First recurring debit starts in week four.",
                source_run_id="run-1",
            )
        },
    )

    evidence = snapshot.evidence_for(contact)
    findings = cross_system_findings(contact, evidence, has_future_booking=True)

    assert evidence["commercial"]["supported"] is True
    assert "COMMERCIAL_EVIDENCE_REVIEW_REQUIRED" not in {
        item.category for item in findings
    }


def test_unresolved_controller_state_does_not_hide_real_commercial_gap():
    contact = active_contact()
    snapshot = CrossSystemSnapshot(
        workbook_by_email={contact.email: workbook_record()},
        controller_pt_by_email={
            contact.email: ControllerPTRecord(
                classification="BOOKING_PAYMENT_UNRESOLVED",
                status="Active",
                payment_marker="$120.00",
                notes="No current evidence.",
                source_run_id="run-1",
            )
        },
    )

    findings = cross_system_findings(
        contact, snapshot.evidence_for(contact), has_future_booking=True
    )

    assert "COMMERCIAL_EVIDENCE_REVIEW_REQUIRED" in {
        item.category for item in findings
    }


def test_owner_approved_external_payment_prevents_duplicate_review():
    contact = active_contact()
    snapshot = CrossSystemSnapshot(
        workbook_by_email={contact.email: workbook_record()},
        approved_account_by_email={
            contact.email: ApprovedAccountRecord(
                classification="external_payment_client",
                confirmed_by="Peter Brown",
                confirmed_date="2026-07-27",
                note="Pays through owner-approved external Stripe account.",
            )
        },
        as_of=date(2026, 7, 27),
    )

    evidence = snapshot.evidence_for(contact)
    findings = cross_system_findings(contact, evidence, has_future_booking=True)

    assert evidence["commercial"]["supported"] is True
    assert "COMMERCIAL_EVIDENCE_REVIEW_REQUIRED" not in {
        item.category for item in findings
    }


def test_stripe_reader_maps_successful_non_invoice_payment_to_beneficiary():
    reader = StripeEntitlementReader("test-key")
    collections = {
        "customers": [
            {"id": "cus_archer", "email": "archer@example.com"},
        ],
        "subscriptions": [],
        "payment_intents": [
            {
                "id": "pi_pack",
                "customer": "cus_archer",
                "amount_received": 240000,
                "currency": "aud",
                "created": 1783746837,
                "status": "succeeded",
                "invoice": None,
            },
            {
                "id": "pi_failed",
                "customer": "cus_archer",
                "amount_received": 0,
                "currency": "aud",
                "created": 1783746837,
                "status": "requires_payment_method",
                "invoice": None,
            },
        ],
    }
    reader._collection = lambda resource, params=None: collections[resource]

    _, recurring, one_off, packs = reader.snapshot(
        {"pi_pack": "shaanta-contact"}
    )

    assert recurring == set()
    assert [item.payment_intent_id for item in one_off["archer@example.com"]] == [
        "pi_pack"
    ]
    assert [item.payment_intent_id for item in packs["shaanta-contact"]] == [
        "pi_pack"
    ]


def test_ghl_only_record_is_not_reported_as_missing_bookings():
    contact = active_contact()
    evidence = CrossSystemSnapshot().evidence_for(contact)
    primary = Finding(
        contact_id=contact.id,
        contact_name=contact.name,
        category="NO_FUTURE_BOOKINGS",
        reason="Active PT contact has no valid future PT appointment.",
        effective_status="active",
    )

    reconcile_primary_with_cross_system_evidence(
        primary, contact, evidence, has_future_booking=False
    )

    assert primary.category == "GHL_ONLY_PT_RECORD_REVIEW"
    assert not primary.proposed_dates


def test_approved_pause_suppresses_booking_gap():
    contact = active_contact()
    snapshot = CrossSystemSnapshot(
        controller_pt_by_email={
            contact.email: ControllerPTRecord(
                classification="APPROVED_PAUSE",
                status="Active",
                payment_marker="paused",
                notes="Processed surgical hold.",
                source_run_id="run-1",
            )
        }
    )
    primary = Finding(
        contact_id=contact.id,
        contact_name=contact.name,
        category="GAP_INSIDE_SERIES",
        reason="Missing booking.",
        effective_status="active",
        proposed_dates=["2026-08-01T09:00:00+10:00"],
    )

    reconcile_primary_with_cross_system_evidence(
        primary,
        contact,
        snapshot.evidence_for(contact),
        has_future_booking=True,
    )

    assert primary.category == "PT_HOLD_ACTIVE"
    assert not primary.proposed_dates
