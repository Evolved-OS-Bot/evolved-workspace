from datetime import datetime, timedelta

from pt_booking_shadow.config import BRISBANE_TZ
from pt_booking_shadow.models import Appointment, PTContact
from pt_booking_shadow.pack_ledger import marker_for, prepaid_pack_findings


NOW = datetime(2026, 7, 27, 9, 0, tzinfo=BRISBANE_TZ)


def appointment(
    appointment_id: str,
    days: int,
    description: str,
    status: str = "confirmed",
) -> Appointment:
    start = NOW + timedelta(days=days)
    return Appointment(
        id=appointment_id,
        contact_id="contact-1",
        calendar_id="calendar-1",
        start=start,
        end=start + timedelta(minutes=45),
        status=status,
        description=description,
        notes=description,
    )


def contact() -> PTContact:
    return PTContact(id="contact-1", name="Pack Client", tags=set(), custom_fields={})


def evidence(verified: bool = True):
    return {
        "stripe": {
            "verified_prepaid_pack": verified,
            "verified_pack_payments": [{"payment_intent_id": "pi_pack"}],
        }
    }


def test_marker_reads_description_and_short_format():
    marker = marker_for(appointment("a", 0, "10/20"))
    assert marker is not None
    assert (marker.number, marker.total, marker.source) == (10, 20, "description")


def test_sequence_regression_fails_closed():
    findings = prepaid_pack_findings(
        contact(),
        [
            appointment("a", 0, "Session 19/20"),
            appointment("b", 1, "Session 20/20"),
            appointment("c", 2, "Session 14/20"),
        ],
        evidence(),
        NOW,
    )
    assert [finding.category for finding in findings] == [
        "PREPAID_PACK_SEQUENCE_REVIEW_REQUIRED"
    ]
    assert findings[0].evidence["regressions"][0]["from"]["session_number"] == 20
    assert findings[0].evidence["regressions"][0]["to"]["session_number"] == 14


def test_booking_after_clean_terminal_is_flagged():
    findings = prepaid_pack_findings(
        contact(),
        [
            appointment("a", 0, "Session 19/20"),
            appointment("b", 1, "Session 20/20"),
            appointment("c", 8, ""),
        ],
        evidence(),
        NOW,
    )
    assert [finding.category for finding in findings] == [
        "PREPAID_PACK_BOOKINGS_AFTER_END"
    ]


def test_terminal_inside_window_prompts_renewal():
    findings = prepaid_pack_findings(
        contact(),
        [
            appointment("a", 1, "Session 19/20"),
            appointment("b", 8, "Session 20/20"),
        ],
        evidence(),
        NOW,
    )
    assert [finding.category for finding in findings] == [
        "PREPAID_PACK_RENEWAL_DUE"
    ]


def test_unverified_payment_does_not_create_pack_ledger_finding():
    findings = prepaid_pack_findings(
        contact(),
        [appointment("a", 1, "Session 20/20")],
        evidence(False),
        NOW,
    )
    assert findings == []


def test_cancelled_duplicate_is_not_treated_as_active_sequence_conflict():
    findings = prepaid_pack_findings(
        contact(),
        [
            appointment("a", 0, "Session 5/20", status="cancelled"),
            appointment("b", 1, "Session 5/20"),
        ],
        evidence(),
        NOW,
    )
    assert findings == []
