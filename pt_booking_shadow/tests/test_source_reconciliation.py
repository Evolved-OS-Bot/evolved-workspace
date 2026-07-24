from pt_booking_shadow.models import PTContact
from pt_booking_shadow.source_reconciliation import (
    CrossSystemSnapshot,
    StripeEntitlementReader,
    StripeOneOffPayment,
    WorkbookPTRecord,
    cross_system_findings,
    normalise_phone,
)


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
