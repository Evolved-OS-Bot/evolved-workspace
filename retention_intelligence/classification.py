from __future__ import annotations

from datetime import date, datetime, timedelta

from .models import MemberInput, RetentionAssessment


CLASSIFIER_VERSION = "retention-v1.0"
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
    elif _service_is_fit_flexible(member.service):
        status = "Insufficient data"
        urgency = "Routine"
        confidence = "Low"
        reason = (
            "Fit & Flexible attendance is not reliably represented by strength-workout "
            "tracking; connect verified class attendance before applying a usage-risk label."
        )
    elif _new_member(member, today):
        status = "Insufficient data"
        urgency = "Routine"
        confidence = "Medium"
        reason = "The member has fewer than six weeks of observed tenure."
    elif usage.baseline_workouts < 4:
        status = "Insufficient data"
        urgency = "Routine"
        confidence = "Low"
        reason = "Fewer than four tracked workouts exist in the personal baseline window."
    else:
        decline = usage.change_percent
        days_since = usage.days_since_last_workout
        confidence = "High" if usage.baseline_workouts >= 8 else "Medium"
        if (
            (days_since is not None and days_since >= 28)
            or (
                decline is not None
                and decline <= -65
                and usage.recent_weekly_rate <= 0.5
            )
        ):
            status = "At risk"
            urgency = "High"
            review_date = today.isoformat()
            if days_since is not None and days_since >= 28:
                reason = f"No tracked workout for {days_since} days."
            else:
                reason = (
                    f"Recent usage is {abs(decline or 0):.0f}% below the personal baseline "
                    f"({usage.recent_weekly_rate:.2f} vs "
                    f"{usage.baseline_weekly_rate:.2f} workouts/week)."
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
                    f"Recent usage is {abs(decline):.0f}% below the personal baseline "
                    f"({usage.recent_weekly_rate:.2f} vs "
                    f"{usage.baseline_weekly_rate:.2f} workouts/week)."
                )
            else:
                reason = f"No tracked workout for {days_since} days."
        elif (
            usage.recent_weekly_rate >= 1.0
            and decline is not None
            and decline >= 10
        ):
            status = "Thriving"
            urgency = "None"
            reason = (
                f"Recent usage is {decline:.0f}% above the personal baseline "
                f"({usage.recent_weekly_rate:.2f} vs "
                f"{usage.baseline_weekly_rate:.2f} workouts/week)."
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
        classifier_version=CLASSIFIER_VERSION,
        included_in_kpi=included,
    )
