from datetime import date

from retention_intelligence.classification import classify_member
from retention_intelligence.models import MemberInput, UsageMetrics


TODAY = date(2026, 7, 26)


def member(**changes):
    values = {
        "trainerize_user_id": 1,
        "email": "member@example.com",
        "first_name": "Test",
        "last_name": "Member",
        "service": "Strong, Fit & Flexible Membership",
        "trainer_name": "Piper",
        "created_date": "2025-01-01",
        "latest_signed_in": "2026-07-25",
        "ghl_active": True,
        "stripe_entitled": True,
        "trainerize_active": True,
        "cancellation_status": None,
        "final_access_date": None,
        "account_classification": None,
        "has_operational_exception": False,
        "usage": UsageMetrics(
            workouts_7d=0,
            workouts_28d=1,
            workouts_90d=10,
            baseline_workouts=24,
            last_workout_date="2026-06-20",
            days_since_last_workout=36,
        ),
    }
    values.update(changes)
    return MemberInput(**values)


def test_large_decline_and_long_inactivity_is_at_risk():
    result = classify_member(member(), today=TODAY)
    assert result.status == "At risk"
    assert result.urgency == "High"
    assert result.included_in_kpi is True


def test_moderate_decline_is_drifting():
    result = classify_member(
        member(
            usage=UsageMetrics(
                workouts_7d=1,
                workouts_28d=5,
                workouts_90d=19,
                baseline_workouts=24,
                last_workout_date="2026-07-22",
                days_since_last_workout=4,
            )
        ),
        today=TODAY,
    )
    assert result.status == "Drifting"
    assert "below the personal baseline" in result.reason


def test_fit_and_flexible_is_not_falsely_labelled_at_risk():
    result = classify_member(
        member(service="Fit & Flexible"),
        today=TODAY,
    )
    assert result.status == "Insufficient data"
    assert result.data_confidence == "Low"


def test_staff_is_excluded():
    result = classify_member(
        member(account_classification="staff"),
        today=TODAY,
    )
    assert result.status == "Excluded"
    assert result.included_in_kpi is False


def test_operational_exception_takes_priority():
    result = classify_member(
        member(has_operational_exception=True),
        today=TODAY,
    )
    assert result.status == "Operational exception"
    assert result.action_owner == "Admin Eve"


def test_sparse_baseline_is_insufficient_data():
    result = classify_member(
        member(
            usage=UsageMetrics(
                workouts_28d=0,
                baseline_workouts=3,
                days_since_last_workout=60,
            )
        ),
        today=TODAY,
    )
    assert result.status == "Insufficient data"
