from __future__ import annotations

from datetime import date, datetime, timedelta

from .models import MemberInput, RetentionAssessment


CLASSIFIER_VERSION = "retention-v1.1"
EXCLUDED_CLASSIFICATIONS = {
    "staff",
    "owner_admin",
    "approved_internal_access",
    "test",
    "demo",
}


def _date(value: str | None) -> date | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text[:10]).date()
    except ValueError:
        return None


def _service_is_fit_flexible(service: str | None) -> bool:
    value = str(service or "").lower()
    return value.startswith("fit & flexible") or value.startswith("limited")


def _new_member(member: MemberInput, today: date) -> bool:
    created = _date(member.created_date)
    return created is not None and (today - created).days < 42


def _engagement_signal(member: MemberInput) -> dict[str, object]:
    usage = member.usage
    use_classes = _service_is_fit_flexible(
        member.service
    ) or (
        usage.baseline_workouts < 4
        and usage.baseline_class_bookings >= 4
    )
    if use_classes:
        return {
            "source": "retained_class_booking",
            "label": "retained class attendance",
            "baseline_count": usage.baseline_class_bookings,
            "baseline_rate": usage.class_baseline_weekly_rate,
            "recent_rate": usage.class_recent_weekly_rate,
            "change": usage.class_change_percent,
            "days_since": usage.days_since_last_class_booking,
        }
    return {
        "source": "tracked_workout",
        "label": "tracked workout usage",
        "baseline_count": usage.baseline_workouts,
        "baseline_rate": usage.baseline_weekly_rate,
        "recent_rate": usage.recent_weekly_rate,
        "change": usage.change_percent,
        "days_since": usage.days_since_last_workout,
    }


def classify_member(
    member: MemberInput,
    *,
    today: date | None = None,
) -> RetentionAssessment:
    today = today or date.today()
    usage = member.usage
    account_classification = str(member.account_classification or "").lower()
    status = "Stable"
    urgency = "Routine"
    confidence = "High"
    reason = "Usage remains within the member's established range."
    owner = member.trainer_name or "Admin Eve"
    review_date: str | None = None
    included = True
    signal = _engagement_signal(member)
    engagement_source = str(signal["source"])

    if account_classification in EXCLUDED_CLASSIFICATIONS:
        status = "Excluded"
        urgency = "None"
        confidence = "High"
        reason = f"Excluded from member-retention KPIs: {account_classification} account."
        included = False
    elif member.has_operational_exception:
        status = "Operational exception"
        urgency = "Immediate"
        confidence = "High"
        reason = "A medium-or-higher cross-system entitlement or access exception requires review."
        owner = "Admin Eve"
        review_date = today.isoformat()
    elif not member.trainerize_active:
        status = "On hold"
        urgency = "None"
        confidence = "High"
        reason = "Trainerize access is not active; do not interpret missing workouts as disengagement."
        included = False
    elif _new_member(member, today):
        status = "Insufficient data"
        urgency = "Routine"
        confidence = "Medium"
        reason = "The member has fewer than six weeks of observed tenure."
    elif int(signal["baseline_count"]) < 4:
        status = "Insufficient data"
        urgency = "Routine"
        confidence = "Low"
        if engagement_source == "retained_class_booking":
            reason = (
                "Fewer than four retained past class bookings exist in the "
                "personal baseline window."
            )
        else:
            reason = (
                "Fewer than four tracked workouts exist in the personal baseline window."
            )
    else:
        decline = signal["change"]
        days_since = signal["days_since"]
        recent_rate = float(signal["recent_rate"])
        baseline_rate = float(signal["baseline_rate"])
        label = str(signal["label"])
        confidence = (
            "High" if int(signal["baseline_count"]) >= 8 else "Medium"
        )
        if (
            (days_since is not None and days_since >= 28)
            or (
                decline is not None
                and decline <= -65
                and recent_rate <= 0.5
            )
        ):
            status = "At risk"
            urgency = "High"
            review_date = today.isoformat()
            if days_since is not None and days_since >= 28:
                reason = f"No {label} for {days_since} days."
            else:
                reason = (
                    f"Recent {label} is {abs(decline or 0):.0f}% below the "
                    f"personal baseline ({recent_rate:.2f} vs "
                    f"{baseline_rate:.2f} per week)."
                )
        elif (
            (days_since is not None and days_since >= 14)
            or (decline is not None and decline <= -35)
        ):
            status = "Drifting"
            urgency = "Review"
            review_date = (today + timedelta(days=2)).isoformat()
            if decline is not None and decline <= -35:
                reason = (
                    f"Recent {label} is {abs(decline):.0f}% below the personal "
                    f"baseline ({recent_rate:.2f} vs {baseline_rate:.2f} per week)."
                )
            else:
                reason = f"No {label} for {days_since} days."
        elif (
            recent_rate >= 1.0
            and decline is not None
            and decline >= 10
        ):
            status = "Thriving"
            urgency = "None"
            reason = (
                f"Recent {label} is {decline:.0f}% above the personal baseline "
                f"({recent_rate:.2f} vs {baseline_rate:.2f} per week)."
            )

    return RetentionAssessment(
        trainerize_user_id=member.trainerize_user_id,
        email=member.email,
        first_name=member.first_name,
        last_name=member.last_name,
        service=member.service,
        trainer_name=member.trainer_name,
        status=status,
        urgency=urgency,
        data_confidence=confidence,
        reason=reason,
        action_owner=owner,
        review_date=review_date,
        latest_signed_in=member.latest_signed_in,
        workouts_7d=usage.workouts_7d,
        workouts_28d=usage.workouts_28d,
        workouts_90d=usage.workouts_90d,
        baseline_weekly_rate=usage.baseline_weekly_rate,
        recent_weekly_rate=usage.recent_weekly_rate,
        change_percent=usage.change_percent,
        last_workout_date=usage.last_workout_date,
        days_since_last_workout=usage.days_since_last_workout,
        engagement_source=engagement_source,
        class_bookings_7d=usage.class_bookings_7d,
        class_bookings_28d=usage.class_bookings_28d,
        class_bookings_90d=usage.class_bookings_90d,
        class_baseline_weekly_rate=usage.class_baseline_weekly_rate,
        class_recent_weekly_rate=usage.class_recent_weekly_rate,
        class_change_percent=usage.class_change_percent,
        last_class_booking_date=usage.last_class_booking_date,
        days_since_last_class_booking=usage.days_since_last_class_booking,
        classifier_version=CLASSIFIER_VERSION,
        included_in_kpi=included,
    )
