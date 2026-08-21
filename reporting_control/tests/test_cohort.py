from datetime import date

from reporting_control.cohort import (
    authoritative_lifecycle_status,
    normalise_control_text,
    summarise_cohort_rows,
)


def test_literal_none_is_not_a_cancellation_status():
    assert normalise_control_text("None") is None
    assert (
        authoritative_lifecycle_status(
            ghl_active=False,
            stripe_entitled=False,
            trainerize_active=False,
            cancellation_status="None",
            final_access_date=None,
            as_of=date(2026, 7, 27),
        )
        == "inactive"
    )


def test_payment_or_access_alone_requires_review_not_active_lifecycle():
    for stripe, trainerize in ((True, False), (False, True)):
        assert (
            authoritative_lifecycle_status(
                ghl_active=False,
                stripe_entitled=stripe,
                trainerize_active=trainerize,
                cancellation_status=None,
                final_access_date=None,
                as_of=date(2026, 7, 27),
            )
            == "review_required"
        )


def test_cancellation_counts_only_inside_final_access_window():
    assert (
        authoritative_lifecycle_status(
            ghl_active=False,
            stripe_entitled=True,
            trainerize_active=True,
            cancellation_status="Notice Active",
            final_access_date="2026-07-27",
            as_of=date(2026, 7, 27),
        )
        == "cancelling"
    )
    assert (
        authoritative_lifecycle_status(
            ghl_active=False,
            stripe_entitled=True,
            trainerize_active=True,
            cancellation_status="Notice Active",
            final_access_date="2026-07-26",
            as_of=date(2026, 7, 27),
        )
        == "review_required"
    )


def test_cohort_summary_keeps_signal_confirmed_and_exception_separate():
    rows = [
        {
            "in_legacy_cohort": True,
            "active_signal": True,
            "confirmed_active": True,
            "paid_or_entitled": True,
            "disposition": "confirmed_active",
            "decision_required": False,
        },
        {
            "in_legacy_cohort": True,
            "active_signal": True,
            "confirmed_active": False,
            "paid_or_entitled": None,
            "disposition": "decision_required",
            "decision_required": True,
        },
        {
            "in_legacy_cohort": False,
            "active_signal": False,
            "confirmed_active": True,
            "paid_or_entitled": None,
            "disposition": "confirmed_active",
            "decision_required": False,
        },
    ]

    summary = summarise_cohort_rows(rows)

    assert summary["active_source_signal_people"] == 2
    assert summary["confirmed_active_clients"] == 2
    assert summary["identity_difference"] == 2
    assert summary["decision_required"] == 1
