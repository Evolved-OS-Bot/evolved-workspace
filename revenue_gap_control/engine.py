from __future__ import annotations

import uuid
from collections import Counter, defaultdict
from decimal import Decimal

from .models import (
    ACTIVE_ARREARS,
    ACTIVE_PIA,
    APPROVED_FUTURE_START,
    APPROVED_PAUSE,
    BOOKING_PAYMENT_UNRESOLVED,
    CLASS_ACTIVE_PIA,
    CLEAN_COLLECTING,
    DOWNGRADE_RECONCILIATION_REQUIRED,
    FAST_TRACK_ALLOCATION_MISMATCH,
    FAST_TRACK_PAIR_MISSING,
    LIFECYCLE_EXCEPTION,
    PACK_RENEWAL_DUE,
    PAYMENT_CURRENT_NO_BOOKING,
    PIF_PACK_IN_DELIVERY,
    REFUND_REMOVE_FROM_ACTIVE,
    SOURCE_READ_FAILURE,
    AuditException,
    AuditInputs,
    AuditResult,
    CashBridge,
    ClientAssessment,
    RosterRecord,
    SourceEvidence,
)


ZERO = Decimal("0")


def _contains(value: str, *needles: str) -> bool:
    lowered = value.lower()
    return any(item.lower() in lowered for item in needles)


def _future_start(record: RosterRecord) -> bool:
    return _contains(
        record.notes,
        "future start",
        "first debit is due",
        "first $",
        "payments start",
    )


def _renewal_due(record: RosterRecord) -> bool:
    return _contains(
        record.notes,
        "renewal decision",
        "renewal due",
        "20/20",
        "final session",
        "pack end",
    )


def _refunded(record: RosterRecord, evidence: SourceEvidence) -> bool:
    return _contains(
        f"{record.notes} {evidence.cancellation_status}",
        "refund",
        "cooling off",
        "cooling-off",
    )


def _approved_hold(evidence: SourceEvidence) -> bool:
    return bool(evidence.hold_status.strip())


def _source_names(record: RosterRecord, evidence: SourceEvidence) -> list[str]:
    sources = ["Brown & Casserly workbook"]
    if evidence.source_run_id:
        sources.extend(["GHL", "Stripe", "Trainerize"])
    if record.service == "PT" and evidence.booking_category:
        sources.append("GHL expanded PT calendars")
    return sources


class AuditEngine:
    def assess_record(
        self,
        record: RosterRecord,
        evidence: SourceEvidence,
        legacy_collecting: bool,
    ) -> ClientAssessment:
        reasons: list[str] = []

        if _refunded(record, evidence):
            return ClientAssessment(
                record,
                evidence,
                REFUND_REMOVE_FROM_ACTIVE,
                ["Refund or cooling-off evidence conflicts with an active roster row."],
            )

        if record.status.strip() == ACTIVE_ARREARS:
            return ClientAssessment(
                record,
                evidence,
                ACTIVE_ARREARS,
                ["Workbook explicitly classifies the client as payment in arrears."],
            )

        if evidence.pause_collection:
            if _approved_hold(evidence):
                return ClientAssessment(
                    record,
                    evidence,
                    APPROVED_PAUSE,
                    ["Stripe pause_collection aligns with GHL hold evidence."],
                    included_in_scheduled_run_rate=True,
                )
            return ClientAssessment(
                record,
                evidence,
                LIFECYCLE_EXCEPTION,
                ["Stripe is paused but no approved GHL hold evidence was found."],
            )

        if _future_start(record):
            return ClientAssessment(
                record,
                evidence,
                APPROVED_FUTURE_START,
                ["The workbook records an evidenced future recurring start."],
                included_in_scheduled_run_rate=True,
            )

        is_pif = (
            record.payment_marker in {"PIF", "PIA"}
            or record.status.strip() == ACTIVE_PIA
        )
        if is_pif:
            if record.service == "SGPT" and record.status.strip() == ACTIVE_PIA:
                return ClientAssessment(
                    record,
                    evidence,
                    CLASS_ACTIVE_PIA,
                    ["Paid-in-advance membership remains active and is excluded from recurring income."],
                )
            if record.service == "PT" and evidence.has_future_booking is False:
                return ClientAssessment(
                    record,
                    evidence,
                    PAYMENT_CURRENT_NO_BOOKING,
                    ["Paid pack evidence exists but no future PT booking was found."],
                )
            classification = PACK_RENEWAL_DUE if _renewal_due(record) else PIF_PACK_IN_DELIVERY
            return ClientAssessment(
                record,
                evidence,
                classification,
                ["Paid-in-advance or PIF treatment is recorded separately from recurring income."],
            )

        if evidence.has_payment_recovery_status or evidence.latest_invoice_status.lower() in {
            "open",
            "uncollectible",
            "void",
            "incomplete",
            "past_due",
        }:
            return ClientAssessment(
                record,
                evidence,
                ACTIVE_ARREARS,
                ["Stripe invoice or subscription evidence requires payment recovery."],
            )

        collecting = evidence.collecting_receipt_confirmed or legacy_collecting
        if collecting:
            if record.service == "PT" and evidence.has_future_booking is False:
                return ClientAssessment(
                    record,
                    evidence,
                    PAYMENT_CURRENT_NO_BOOKING,
                    ["Current payment evidence exists but no future PT booking was found."],
                    included_in_confirmed_income=True,
                    included_in_scheduled_run_rate=True,
                )
            return ClientAssessment(
                record,
                evidence,
                CLEAN_COLLECTING,
                ["Current unpaused payment and successful-receipt evidence agree."],
                included_in_confirmed_income=True,
                included_in_scheduled_run_rate=True,
            )

        if record.service == "PT" and evidence.has_future_booking:
            reasons.append("Future PT booking exists but current payment evidence is unresolved.")
        else:
            reasons.append("No current successful recurring or approved legacy receipt was found.")
        return ClientAssessment(
            record,
            evidence,
            BOOKING_PAYMENT_UNRESOLVED,
            reasons,
        )

    def _exception_for(self, assessment: ClientAssessment) -> AuditException | None:
        classification = assessment.classification
        if classification in {
            CLEAN_COLLECTING,
            CLASS_ACTIVE_PIA,
            PIF_PACK_IN_DELIVERY,
            APPROVED_PAUSE,
            APPROVED_FUTURE_START,
        }:
            return None
        actions = {
            ACTIVE_ARREARS: "Recover payment or document the approved treatment.",
            PACK_RENEWAL_DUE: "Confirm renewal before the final entitled session.",
            PAYMENT_CURRENT_NO_BOOKING: "Rebook delivery or document the approved service end.",
            BOOKING_PAYMENT_UNRESOLVED: "Verify Stripe and approved legacy receipt evidence before further delivery.",
            REFUND_REMOVE_FROM_ACTIVE: "Remove the refunded service from active systems using the approved boundary.",
            DOWNGRADE_RECONCILIATION_REQUIRED: "Align the current service across workbook, GHL, payment rail and Trainerize.",
            LIFECYCLE_EXCEPTION: "Resolve the hold, cancellation or payment-state contradiction.",
        }
        record = assessment.roster
        return AuditException(
            email=record.email,
            client_name=record.name,
            service=record.service,
            classification=classification,
            summary=" ".join(assessment.reasons),
            financial_value=record.weekly_allocation or ZERO,
            evidence_checked=_source_names(record, assessment.evidence),
            next_action=actions.get(classification, "Review and resolve the exception."),
            source_row=record.row_number,
        )

    def _fast_track_exceptions(
        self, assessments: list[ClientAssessment]
    ) -> list[AuditException]:
        by_email: dict[str, list[ClientAssessment]] = defaultdict(list)
        for item in assessments:
            if item.roster.email:
                by_email[item.roster.email].append(item)
        exceptions: list[AuditException] = []
        for email, items in by_email.items():
            if not any(item.roster.is_fast_track_component for item in items):
                continue
            sgpt = [item for item in items if item.roster.service == "SGPT"]
            pt = [item for item in items if item.roster.service == "PT"]
            name = items[0].roster.name
            if not sgpt or not pt:
                exceptions.append(
                    AuditException(
                        email=email,
                        client_name=name,
                        service="Fast Track",
                        classification=FAST_TRACK_PAIR_MISSING,
                        summary="Current Fast Track requires one Active SGPT row and one Active PT row.",
                        financial_value=ZERO,
                        evidence_checked=["Active SGPT", "Active PT"],
                        next_action="Create or restore the missing allocation row after payment evidence is verified.",
                    )
                )
                continue
            sgpt_amount = sum(
                (item.roster.weekly_allocation or ZERO for item in sgpt), ZERO
            )
            pt_amount = sum(
                (item.roster.weekly_allocation or ZERO for item in pt), ZERO
            )
            if sgpt_amount != Decimal("99.00") or pt_amount != Decimal("50.00"):
                exceptions.append(
                    AuditException(
                        email=email,
                        client_name=name,
                        service="Fast Track",
                        classification=FAST_TRACK_ALLOCATION_MISMATCH,
                        summary=(
                            f"Fast Track allocation is SGPT ${sgpt_amount:.2f} and "
                            f"PT ${pt_amount:.2f}; expected $99.00 and $50.00."
                        ),
                        financial_value=abs(sgpt_amount - Decimal("99.00"))
                        + abs(pt_amount - Decimal("50.00")),
                        evidence_checked=["Active SGPT", "Active PT"],
                        next_action="Correct the allocation rows without counting the $149 receipt twice.",
                    )
                )
        return exceptions

    def _duplicates(self, roster: list[RosterRecord]) -> list[str]:
        keys = [
            f"{item.service}:{item.email}"
            for item in roster
            if item.email
        ]
        return sorted(key for key, count in Counter(keys).items() if count > 1)

    def run(self, inputs: AuditInputs, run_id: str | None = None) -> AuditResult:
        run_id = run_id or str(uuid.uuid4())
        assessments: list[ClientAssessment] = []
        exceptions: list[AuditException] = []
        for record in inputs.roster:
            evidence = inputs.evidence_by_email.get(
                record.email, SourceEvidence(email=record.email)
            )
            legacy = inputs.legacy_evidence_by_email.get(record.email)
            assessment = self.assess_record(
                record,
                evidence,
                bool(legacy and legacy.collecting),
            )
            assessments.append(assessment)
            exception = self._exception_for(assessment)
            if exception:
                exceptions.append(exception)

        exceptions.extend(self._fast_track_exceptions(assessments))
        for limitation in inputs.limitations:
            if not limitation.startswith("SOURCE:"):
                continue
            exceptions.append(
                AuditException(
                    email="",
                    client_name="System",
                    service="All",
                    classification=SOURCE_READ_FAILURE,
                    summary=limitation,
                    evidence_checked=[],
                    owner="Peter Brown",
                    next_action="Restore the source and rerun before authorising changes.",
                )
            )

        bridge = CashBridge(cleared_cash=inputs.cleared_cash)
        for item in assessments:
            value = item.roster.weekly_allocation or ZERO
            if item.roster.service == "SGPT":
                bridge.sgpt_numeric_allocation += value
            else:
                bridge.pt_numeric_allocation += value
            if item.roster.payment_marker in {"PIF", "PIA"}:
                bridge.pif_rows += 1
            if item.classification == ACTIVE_ARREARS:
                bridge.arrears += value
            elif item.classification in {APPROVED_PAUSE, LIFECYCLE_EXCEPTION} and item.evidence.pause_collection:
                bridge.approved_pauses += value
            elif item.classification == APPROVED_FUTURE_START:
                bridge.future_starts += value
            if item.included_in_confirmed_income:
                bridge.confirmed_current_income += value
            if item.included_in_scheduled_run_rate:
                bridge.scheduled_run_rate += value

        bridge.combined_numeric_allocation = (
            bridge.sgpt_numeric_allocation + bridge.pt_numeric_allocation
        )
        bridge.timing_items = sum((item.amount for item in inputs.timing_items), ZERO)
        bridge.unexplained_variance = (
            bridge.confirmed_current_income
            - bridge.cleared_cash
            - bridge.timing_items
        )
        return AuditResult(
            run_id=run_id,
            window_start=inputs.window_start,
            window_end=inputs.window_end,
            assessments=assessments,
            exceptions=exceptions,
            bridge=bridge,
            limitations=list(inputs.limitations),
            status_counts=dict(Counter(item.classification for item in assessments)),
            duplicate_emails=self._duplicates(inputs.roster),
        )
