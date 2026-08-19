from datetime import UTC, datetime

from pt_booking_shadow.models import PTContact
from pt_booking_shadow.source_reconciliation import StripeOneOffPayment
from reporting_control.hub_pack_commercial_client import (
    build_stripe_pack_commercial_evidence,
)


def test_only_explicit_beneficiary_pack_payments_are_published():
    contact = PTContact(
        id="ghl-vavaa",
        name="Vavaa Mawuli",
        email="vavaa@example.com",
        tags={"pt only"},
        custom_fields={},
    )
    payment = StripeOneOffPayment(
        payment_intent_id="pi_pack",
        customer_id="cus_payer",
        payer_email="payer@example.com",
        amount_received=120000,
        currency="aud",
        created=int(
            datetime(2026, 6, 13, tzinfo=UTC).timestamp()
        ),
        beneficiary_contact_id=contact.id,
    )

    payload = build_stripe_pack_commercial_evidence(
        [contact],
        {contact.id: [payment]},
        source_run_id="pt-run-1",
        observed_at="2026-07-28T10:00:00+00:00",
    )

    assert payload["source_system"] == "stripe_pack"
    assert len(payload["rows"]) == 1
    row = payload["rows"][0]
    assert row["canonical_key"] == "vavaa@example.com"
    assert row["entitlements"][0]["status"] == "confirmed"
    assert row["entitlements"][0]["service_type"] == "personal_training"
    assert row["payment_accounts"][0]["status"] == "paid_in_advance"
    assert row["payment_events"][0]["amount"] == "1200.00"


def test_unmapped_or_unidentifiable_payments_publish_empty_snapshot():
    payload = build_stripe_pack_commercial_evidence(
        [],
        {},
        source_run_id="pt-run-empty",
    )

    assert payload["rows"] == []


def test_mapped_beneficiary_can_be_loaded_from_raw_ghl_contact():
    payment = StripeOneOffPayment(
        payment_intent_id="pi_pack",
        customer_id="cus_payer",
        payer_email="payer@example.com",
        amount_received=120000,
        currency="aud",
        created=int(
            datetime(2026, 6, 13, tzinfo=UTC).timestamp()
        ),
        beneficiary_contact_id="ghl-vavaa",
    )

    payload = build_stripe_pack_commercial_evidence(
        [{"id": "ghl-vavaa", "email": "vavaa@example.com"}],
        {"ghl-vavaa": [payment]},
        source_run_id="pt-run-raw-contact",
    )

    assert payload["rows"][0]["canonical_key"] == "vavaa@example.com"
