from __future__ import annotations

from datetime import date
from decimal import Decimal

from revenue_gap_control.engine import AuditEngine
from revenue_gap_control.models import (
    ACTIVE_ARREARS,
    APPROVED_FUTURE_START,
    APPROVED_PAUSE,
    BOOKING_PAYMENT_UNRESOLVED,
    CLASS_ACTIVE_PIA,
    CLEAN_COLLECTING,
    FAST_TRACK_ALLOCATION_MISMATCH,
    FAST_TRACK_PAIR_MISSING,
    PAYMENT_CURRENT_NO_BOOKING,
    PIF_PACK_IN_DELIVERY,
    AuditInputs,
    LegacyPaymentEvidence,
    RosterRecord,
    SourceEvidence,
    TimingItem,
)


def roster(
    email="member@example.com",
    *,
    service="SGPT",
    status="Active",
    amount=Decimal("99.00"),
    marker="$99.00",
    product="Bronze",
    notes="",
    row=2,
):
    return RosterRecord(
        service=service,
        row_number=row,
        first_name="Test",
        last_name="Member",
        email=email,
        phone="0400000000",
        status=status,
        weekly_allocation=amount,
        payment_marker=marker,
        product=product,
        trainer="Piper Mae" if service == "PT" else "",
        session_length="30 mins" if service == "PT" else "",
        sessions_per_week="1" if service == "PT" else "",
        session_cost=Decimal("50.00") if service == "PT" else None,
        notes=notes,
    )


def evidence(email="member@example.com", **overrides):
    values = dict(
        email=email,
        stripe_statuses=["active"],
        latest_invoice_status="paid",
        latest_invoice_paid=True,
        pause_collection=False,
        trainerize_active=True,
        has_future_booking=True,
        source_run_id="membership-run",
    )
    values.update(overrides)
    return SourceEvidence(**values)


def inputs(records, evidence_rows, cash=Decimal("0"), timing=None, legacy=None):
    return AuditInputs(
        window_start=date(2026, 7, 20),
        window_end=date(2026, 7, 26),
        cleared_cash=cash,
        roster=records,
        evidence_by_email={item.email: item for item in evidence_rows},
        timing_items=timing or [],
        legacy_evidence_by_email=legacy or {},
    )


def test_clean_collecting_requires_paid_invoice_and_unpaused_subscription():
    item = roster()
    result = AuditEngine().run(inputs([item], [evidence()], cash=Decimal("99")))
    assert result.assessments[0].classification == CLEAN_COLLECTING
    assert result.bridge.confirmed_current_income == Decimal("99.00")
    assert result.bridge.unexplained_variance == Decimal("0.00")


def test_active_subscription_without_successful_invoice_is_unresolved():
    item = roster()
    source = evidence(latest_invoice_status="", latest_invoice_paid=False)
    result = AuditEngine().run(inputs([item], [source]))
    assert result.assessments[0].classification == BOOKING_PAYMENT_UNRESOLVED
    assert result.bridge.confirmed_current_income == Decimal("0")


def test_pause_with_hold_is_excluded_from_current_and_kept_in_scheduled():
    item = roster()
    source = evidence(pause_collection=True, hold_status="On Hold")
    result = AuditEngine().run(inputs([item], [source]))
    assert result.assessments[0].classification == APPROVED_PAUSE
    assert result.bridge.approved_pauses == Decimal("99.00")
    assert result.bridge.confirmed_current_income == Decimal("0")
    assert result.bridge.scheduled_run_rate == Decimal("99.00")


def test_arrears_status_excludes_allocation_from_confirmed_income():
    item = roster(status="Active - ARREARS")
    result = AuditEngine().run(inputs([item], [evidence()]))
    assert result.assessments[0].classification == ACTIVE_ARREARS
    assert result.bridge.arrears == Decimal("99.00")
    assert result.bridge.confirmed_current_income == Decimal("0")


def test_paid_in_advance_is_active_but_not_recurring_income():
    item = roster(status="Active - PIA", amount=None, marker="PIF")
    result = AuditEngine().run(inputs([item], [evidence()]))
    assert result.assessments[0].classification == CLASS_ACTIVE_PIA
    assert result.bridge.pif_rows == 1
    assert result.bridge.confirmed_current_income == Decimal("0")


def test_future_start_is_scheduled_but_not_current():
    item = roster(notes="First debit is due 3/8 to fund week 5")
    result = AuditEngine().run(inputs([item], [evidence()]))
    assert result.assessments[0].classification == APPROVED_FUTURE_START
    assert result.bridge.future_starts == Decimal("99.00")
    assert result.bridge.scheduled_run_rate == Decimal("99.00")


def test_pif_pt_pack_is_separate_from_recurring_income():
    item = roster(
        service="PT",
        amount=None,
        marker="PIF",
        product="PT",
    )
    result = AuditEngine().run(inputs([item], [evidence()]))
    assert result.assessments[0].classification == PIF_PACK_IN_DELIVERY
    assert result.bridge.pt_numeric_allocation == Decimal("0")


def test_current_payment_without_future_pt_booking_is_exception():
    item = roster(service="PT", amount=Decimal("120"), marker="$120", product="PT")
    source = evidence(has_future_booking=False)
    result = AuditEngine().run(inputs([item], [source]))
    assert result.assessments[0].classification == PAYMENT_CURRENT_NO_BOOKING
    assert result.bridge.confirmed_current_income == Decimal("120.00")


def test_approved_legacy_payment_can_prove_collecting():
    item = roster(service="PT", amount=Decimal("120"), marker="$120", product="PT")
    source = SourceEvidence(email=item.email, has_future_booking=True)
    legacy = {
        item.email: LegacyPaymentEvidence(
            email=item.email,
            rail="PTMinder",
            status="collecting",
            weekly_amount=Decimal("120"),
        )
    }
    result = AuditEngine().run(inputs([item], [source], legacy=legacy))
    assert result.assessments[0].classification == CLEAN_COLLECTING


def test_fast_track_requires_both_allocation_rows():
    sgpt = roster(product="Fast Track", amount=Decimal("99"))
    result = AuditEngine().run(inputs([sgpt], [evidence()]))
    assert any(
        item.classification == FAST_TRACK_PAIR_MISSING
        for item in result.exceptions
    )


def test_fast_track_allocation_mismatch_is_reported_without_double_counting():
    sgpt = roster(product="Fast Track", amount=Decimal("99"), row=2)
    pt = roster(
        service="PT",
        amount=Decimal("60"),
        marker="$60",
        product="Fast Track",
        notes="Fast Track",
        row=3,
    )
    result = AuditEngine().run(inputs([sgpt, pt], [evidence()]))
    assert result.bridge.combined_numeric_allocation == Decimal("159.00")
    assert any(
        item.classification == FAST_TRACK_ALLOCATION_MISMATCH
        for item in result.exceptions
    )


def test_named_timing_items_reduce_the_unexplained_variance():
    item = roster()
    result = AuditEngine().run(
        inputs(
            [item],
            [evidence()],
            cash=Decimal("60"),
            timing=[TimingItem(label="Processor timing", amount=Decimal("39"))],
        )
    )
    assert result.bridge.unexplained_variance == Decimal("0.00")


def test_duplicate_email_is_service_specific_and_cross_service_pair_is_allowed():
    first = roster(row=2)
    duplicate = roster(row=3)
    pt = roster(service="PT", amount=Decimal("50"), marker="$50", row=4)
    result = AuditEngine().run(inputs([first, duplicate, pt], [evidence()]))
    assert result.duplicate_emails == ["SGPT:member@example.com"]
