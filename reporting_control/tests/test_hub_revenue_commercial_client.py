from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from reporting_control.hub_revenue_commercial_client import (
    build_revenue_commercial_evidence,
)
from revenue_gap_control.database import AuditStore
from revenue_gap_control.engine import AuditEngine
from revenue_gap_control.models import (
    AuditInputs,
    LegacyPaymentEvidence,
    RosterRecord,
    SourceEvidence,
)


def _record(service: str, row_number: int) -> RosterRecord:
    return RosterRecord(
        service=service,
        row_number=row_number,
        first_name="Test",
        last_name="Member",
        email="member@example.com",
        phone="0400000000",
        status="Active",
        weekly_allocation=Decimal("99"),
        payment_marker="$99",
        product="Bronze" if service == "SGPT" else "PT",
    )


def _save(
    tmp_path,
    *,
    evidence: SourceEvidence,
    legacy: LegacyPaymentEvidence | None = None,
    limitations: list[str] | None = None,
):
    records = [_record("SGPT", 2), _record("PT", 3)]
    inputs = AuditInputs(
        window_start=date(2026, 7, 20),
        window_end=date(2026, 7, 26),
        cleared_cash=Decimal("198"),
        roster=records,
        evidence_by_email={evidence.email: evidence},
        legacy_evidence_by_email=(
            {legacy.email: legacy} if legacy else {}
        ),
        limitations=limitations or [],
    )
    result = AuditEngine().run(inputs, run_id="audit-1")
    database = tmp_path / "audit.sqlite"
    AuditStore(database).save(inputs, result)
    return database


def test_builds_exact_service_entitlements_from_current_stripe_receipt(
    tmp_path,
):
    database = _save(
        tmp_path,
        evidence=SourceEvidence(
            email="member@example.com",
            stripe_statuses=["active"],
            latest_invoice_status="paid",
            latest_invoice_paid=True,
            latest_receipt_date="2026-07-24",
            source_run_id="membership-1",
        ),
    )

    payload = build_revenue_commercial_evidence(database)

    assert payload["source_system"] == "revenue_control"
    assert len(payload["rows"]) == 1
    assert {
        item["service_type"]
        for item in payload["rows"][0]["entitlements"]
    } == {"sgpt", "personal_training"}
    assert {
        item["basis"]
        for item in payload["rows"][0]["entitlements"]
    } == {"revenue_control_current_stripe_receipt"}


def test_builds_only_when_legacy_receipt_is_current(tmp_path):
    legacy = LegacyPaymentEvidence(
        email="member@example.com",
        rail="PTMinder/EziDebit",
        status="collecting",
        last_receipt_date="2026-07-22",
    )
    database = _save(
        tmp_path,
        evidence=SourceEvidence(email="member@example.com"),
        legacy=legacy,
    )
    evidence_path = tmp_path / "legacy.csv"
    evidence_path.write_text(
        "email,status,last_receipt_date\n"
        "member@example.com,collecting,2026-07-22\n",
        encoding="utf-8",
    )

    payload = build_revenue_commercial_evidence(
        database,
        legacy_evidence_path=evidence_path,
    )

    assert len(payload["rows"][0]["entitlements"]) == 2
    assert {
        item["basis"]
        for item in payload["rows"][0]["entitlements"]
    } == {"revenue_control_current_approved_legacy_receipt"}


def test_governed_purchased_service_term_binds_invoice_and_dates(
    tmp_path,
):
    database = _save(
        tmp_path,
        evidence=SourceEvidence(email="member@example.com"),
    )
    terms = tmp_path / "purchased-service-terms.csv"
    terms.write_text(
        "term_id,stripe_invoice_id,additional_stripe_invoice_ids,"
        "purchaser_email,beneficiary_email,"
        "service_type,quantity,unit,state,effective_from,effective_to,"
        "approved_by,approved_on\n"
        "term-1,in_123,in_456,buyer@example.com,member@example.com,sgpt,"
        "12,sessions,approved,2026-07-20,2026-10-20,"
        "Peter Brown,2026-07-28\n",
        encoding="utf-8",
    )

    payload = build_revenue_commercial_evidence(
        database,
        purchased_service_terms_path=terms,
    )
    entitlement = next(
        item
        for item in payload["rows"][0]["entitlements"]
        if item["source_record_id"] == "purchased-service-term:term-1"
    )

    assert entitlement == {
        "source_record_id": "purchased-service-term:term-1",
        "service_type": "sgpt",
        "quantity": "12",
        "unit": "sessions",
        "status": "confirmed",
        "effective_from": "2026-07-20",
        "effective_to": "2026-10-20",
        "basis": (
            "revenue_control_governed_purchased_service_term"
        ),
        "payment_reference": "in_123;in_456",
    }


def test_revoked_purchased_service_term_cannot_confirm_entitlement(
    tmp_path,
):
    database = _save(
        tmp_path,
        evidence=SourceEvidence(email="member@example.com"),
    )
    terms = tmp_path / "purchased-service-terms.csv"
    terms.write_text(
        "term_id,stripe_invoice_id,purchaser_email,beneficiary_email,"
        "service_type,state,effective_from,effective_to,approved_by,"
        "approved_on\n"
        "term-1,in_123,buyer@example.com,member@example.com,sgpt,"
        "revoked,2026-07-20,2026-10-20,Peter Brown,2026-07-28\n",
        encoding="utf-8",
    )

    payload = build_revenue_commercial_evidence(
        database,
        purchased_service_terms_path=terms,
    )
    entitlement = next(
        item
        for item in payload["rows"][0]["entitlements"]
        if item["source_record_id"] == "purchased-service-term:term-1"
    )

    assert entitlement["status"] == "not_entitled"


def test_rejects_audit_with_source_limitations(tmp_path):
    database = _save(
        tmp_path,
        evidence=SourceEvidence(
            email="member@example.com",
            stripe_statuses=["active"],
            latest_invoice_status="paid",
            latest_invoice_paid=True,
            latest_receipt_date="2026-07-24",
        ),
        limitations=["SOURCE: Stripe snapshot is stale"],
    )

    with pytest.raises(RuntimeError, match="source limitations"):
        build_revenue_commercial_evidence(database)


def test_rejects_clean_classification_without_underlying_receipt(tmp_path):
    database = _save(
        tmp_path,
        evidence=SourceEvidence(email="member@example.com"),
        legacy=LegacyPaymentEvidence(
            email="member@example.com",
            rail="PTMinder/EziDebit",
            status="paid_in_advance",
        ),
    )

    with pytest.raises(RuntimeError, match="underlying receipt"):
        build_revenue_commercial_evidence(database)


def test_publishes_non_clean_assessment_as_pending_context(tmp_path):
    records = [_record("SGPT", 2)]
    inputs = AuditInputs(
        window_start=date(2026, 7, 20),
        window_end=date(2026, 7, 26),
        cleared_cash=Decimal("0"),
        roster=records,
        evidence_by_email={
            "member@example.com": SourceEvidence(
                email="member@example.com"
            )
        },
    )
    result = AuditEngine().run(inputs, run_id="audit-pending")
    database = tmp_path / "pending.sqlite"
    AuditStore(database).save(inputs, result)

    payload = build_revenue_commercial_evidence(database)
    entitlement = payload["rows"][0]["entitlements"][0]

    assert entitlement["status"] == "pending"
    assert entitlement["basis"] == (
        "revenue_control_assessment:NO_CURRENT_PAYMENT_EVIDENCE"
    )


def test_duplicate_service_is_isolated_as_pending_owner_review(
    tmp_path,
):
    records = [_record("SGPT", 2), _record("SGPT", 3)]
    evidence = SourceEvidence(
        email="member@example.com",
        stripe_statuses=["active"],
        latest_invoice_status="paid",
        latest_invoice_paid=True,
        latest_receipt_date="2026-07-24",
    )
    inputs = AuditInputs(
        window_start=date(2026, 7, 20),
        window_end=date(2026, 7, 26),
        cleared_cash=Decimal("198"),
        roster=records,
        evidence_by_email={evidence.email: evidence},
    )
    result = AuditEngine().run(inputs, run_id="audit-duplicate")
    database = tmp_path / "duplicate.sqlite"
    AuditStore(database).save(inputs, result)

    payload = build_revenue_commercial_evidence(database)
    entitlements = payload["rows"][0]["entitlements"]

    assert len(entitlements) == 1
    assert entitlements[0]["status"] == "pending"
    assert entitlements[0]["basis"] == (
        "revenue_control_assessment:DUPLICATE_ROSTER_SERVICE"
    )


def test_unresolved_payment_is_split_by_current_evidence(tmp_path):
    records = [
        _record("SGPT", 2),
        RosterRecord(
            **{
                **_record("PT", 3).__dict__,
                "email": "pt@example.com",
            }
        ),
    ]
    inputs = AuditInputs(
        window_start=date(2026, 7, 20),
        window_end=date(2026, 7, 26),
        cleared_cash=Decimal("0"),
        roster=records,
        evidence_by_email={
            "member@example.com": SourceEvidence(
                email="member@example.com",
                stripe_statuses=["active"],
                latest_invoice_status="",
                latest_invoice_paid=False,
            ),
            "pt@example.com": SourceEvidence(
                email="pt@example.com",
                has_future_booking=True,
            ),
        },
    )
    result = AuditEngine().run(inputs, run_id="audit-purpose")
    database = tmp_path / "purpose.sqlite"
    AuditStore(database).save(inputs, result)

    payload = build_revenue_commercial_evidence(database)
    bases = {
        row["canonical_key"]: row["entitlements"][0]["basis"]
        for row in payload["rows"]
    }

    assert bases == {
        "member@example.com": (
            "revenue_control_assessment:"
            "ACTIVE_CONTRACT_RECEIPT_UNRESOLVED"
        ),
        "pt@example.com": (
            "revenue_control_assessment:"
            "PAYMENT_UNRESOLVED_WITH_FUTURE_BOOKING"
        ),
    }


def test_owner_approved_prepaid_credit_covers_exact_service_window(
    tmp_path,
):
    record = RosterRecord(
        **{
            **_record("SGPT", 2).__dict__,
            "payment_marker": "PIA",
            "status": "Active - PIA",
        }
    )
    inputs = AuditInputs(
        window_start=date(2026, 7, 20),
        window_end=date(2026, 7, 26),
        cleared_cash=Decimal("0"),
        roster=[record],
        evidence_by_email={
            "member@example.com": SourceEvidence(
                email="member@example.com"
            )
        },
    )
    result = AuditEngine().run(inputs, run_id="audit-prepaid")
    database = tmp_path / "prepaid.sqlite"
    AuditStore(database).save(inputs, result)
    classifications = tmp_path / "classifications.csv"
    classifications.write_text(
        "email,classification,"
        "approved_active_without_local_entitlement\n"
        "member@example.com,prepaid_credit_client,true\n",
        encoding="utf-8",
    )

    payload = build_revenue_commercial_evidence(
        database,
        account_classifications_path=classifications,
    )
    entitlement = payload["rows"][0]["entitlements"][0]

    assert entitlement == {
        "source_record_id": "audit-prepaid:SGPT:2",
        "service_type": "sgpt",
        "status": "confirmed",
        "effective_from": "2026-07-20",
        "effective_to": "2026-07-26",
        "basis": (
            "revenue_control_owner_approved_prepaid_credit"
        ),
    }


def test_prepaid_marker_without_approved_evidence_stays_pending(
    tmp_path,
):
    record = RosterRecord(
        **{
            **_record("SGPT", 2).__dict__,
            "payment_marker": "PIF",
        }
    )
    inputs = AuditInputs(
        window_start=date(2026, 7, 20),
        window_end=date(2026, 7, 26),
        cleared_cash=Decimal("0"),
        roster=[record],
        evidence_by_email={
            "member@example.com": SourceEvidence(
                email="member@example.com"
            )
        },
    )
    result = AuditEngine().run(inputs, run_id="audit-unapproved-prepaid")
    database = tmp_path / "unapproved-prepaid.sqlite"
    AuditStore(database).save(inputs, result)

    payload = build_revenue_commercial_evidence(database)
    entitlement = payload["rows"][0]["entitlements"][0]

    assert entitlement["status"] == "pending"
    assert entitlement["basis"] == (
        "revenue_control_assessment:PIF_PACK_IN_DELIVERY"
    )


def test_governed_pif_with_future_renewal_covers_current_window(
    tmp_path,
):
    record = RosterRecord(
        **{
            **_record("SGPT", 2).__dict__,
            "payment_marker": "PIF",
            "contract_length": "12 Months",
            "renewal_date": "18/11/26",
        }
    )
    inputs = AuditInputs(
        window_start=date(2026, 7, 20),
        window_end=date(2026, 7, 26),
        cleared_cash=Decimal("0"),
        roster=[record],
        evidence_by_email={
            "member@example.com": SourceEvidence(
                email="member@example.com"
            )
        },
    )
    result = AuditEngine().run(inputs, run_id="audit-roster-pif")
    database = tmp_path / "roster-pif.sqlite"
    AuditStore(database).save(inputs, result)

    payload = build_revenue_commercial_evidence(database)
    entitlement = payload["rows"][0]["entitlements"][0]

    assert entitlement["status"] == "confirmed"
    assert entitlement["effective_from"] == "2026-07-20"
    assert entitlement["effective_to"] == "2026-11-18"
    assert entitlement["basis"] == (
        "revenue_control_governed_pif_roster_through_renewal"
    )


def test_governed_pif_accepts_google_sheet_serial_renewal_date(
    tmp_path,
):
    record = RosterRecord(
        **{
            **_record("SGPT", 2).__dict__,
            "payment_marker": "PIF",
            "contract_length": "12 Months",
            "renewal_date": "46399",
        }
    )
    inputs = AuditInputs(
        window_start=date(2026, 7, 27),
        window_end=date(2026, 8, 2),
        cleared_cash=Decimal("0"),
        roster=[record],
        evidence_by_email={
            "member@example.com": SourceEvidence(
                email="member@example.com"
            )
        },
    )
    result = AuditEngine().run(inputs, run_id="audit-roster-serial-pif")
    database = tmp_path / "roster-serial-pif.sqlite"
    AuditStore(database).save(inputs, result)

    payload = build_revenue_commercial_evidence(database)
    entitlement = payload["rows"][0]["entitlements"][0]

    assert entitlement["status"] == "confirmed"
    assert entitlement["effective_from"] == "2026-07-27"
    assert entitlement["effective_to"] == "2027-01-12"
    assert entitlement["basis"] == (
        "revenue_control_governed_pif_roster_through_renewal"
    )
