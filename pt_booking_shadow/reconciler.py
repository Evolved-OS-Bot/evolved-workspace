from __future__ import annotations

from collections import Counter
from datetime import date, datetime, timedelta

from .models import Appointment, CalendarRecord, Finding, PTContact
from .patterns import VALID_FUTURE, infer_pattern


def _iso(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


def _next_occurrence(now: datetime, weekday: int, local_time) -> datetime:
    days = (weekday - now.weekday()) % 7
    candidate = now.replace(
        hour=local_time.hour, minute=local_time.minute, second=0, microsecond=0
    ) + timedelta(days=days)
    if candidate < now:
        candidate += timedelta(days=7)
    return candidate


def _week_start(value: datetime) -> date:
    """Return the Monday date for the appointment's local ISO week."""
    return value.date() - timedelta(days=value.weekday())


def _base_finding(contact: PTContact, category: str, reason: str) -> Finding:
    return Finding(
        contact_id=contact.id,
        contact_name=contact.name,
        category=category,
        reason=reason,
        effective_status=contact.effective_status,
        expected_frequency=contact.expected_frequency,
    )


def reconcile_contact(
    contact: PTContact,
    appointments: list[Appointment],
    calendars: dict[str, CalendarRecord],
    now: datetime,
    horizon_weeks: int = 13,
    minimum_confidence: float = 0.80,
) -> Finding:
    valid = [
        event
        for event in appointments
        if event.calendar_id in calendars and not event.deleted
    ]
    future = sorted(
        [event for event in valid if event.start >= now and event.status in VALID_FUTURE],
        key=lambda event: event.start,
    )
    completed = sorted(
        [
            event
            for event in valid
            if event.start < now and event.status in {"showed", "completed", "confirmed", "active"}
        ],
        key=lambda event: event.start,
    )

    duplicate_starts = [
        start for start, count in Counter(event.start for event in future).items() if count > 1
    ]
    if duplicate_starts:
        finding = _base_finding(
            contact,
            "DUPLICATE_APPOINTMENT",
            f"{len(duplicate_starts)} future PT time(s) contain duplicate active appointments.",
        )
        finding.last_future = _iso(future[-1].start) if future else None
        finding.evidence["duplicate_starts"] = [item.isoformat() for item in duplicate_starts]
        return finding

    if contact.effective_status == "pt_cancellation":
        if contact.final_access is None:
            finding = _base_finding(
                contact,
                "CANCELLATION_DATE_MISSING",
                "PT cancellation is active but CS: Final Access Date is blank.",
            )
            finding.last_future = _iso(future[-1].start) if future else None
            return finding
        after = [event for event in future if event.start.date() > contact.final_access]
        category = "WOULD_REMOVE_AFTER_CANCELLATION" if after else "PT_NOTICE_ACTIVE"
        reason = (
            f"{len(after)} future PT appointment(s) fall after Final Access Date "
            f"{contact.final_access.isoformat()}."
            if after
            else f"No future PT appointments fall after Final Access Date {contact.final_access.isoformat()}."
        )
        finding = _base_finding(contact, category, reason)
        finding.proposed_dates = [event.start.isoformat() for event in after]
        finding.last_future = _iso(future[-1].start) if future else None
        finding.evidence["final_access_date"] = contact.final_access.isoformat()
        return finding

    if contact.effective_status == "former_pt":
        finding = _base_finding(
            contact,
            "FORMER_PT_WITH_FUTURE_BOOKINGS" if future else "FORMER_PT",
            (
                f"Former PT contact still has {len(future)} future PT appointment(s)."
                if future
                else "Former PT contact has no future PT bookings."
            ),
        )
        finding.last_future = _iso(future[-1].start) if future else None
        return finding

    if contact.effective_status == "pt_hold":
        finding = _base_finding(
            contact,
            "PT_HOLD_ACTIVE",
            "PT-specific hold is active or pending. Top-up recommendations are paused and no removal is proposed.",
        )
        finding.last_future = _iso(future[-1].start) if future else None
        finding.evidence.update(
            {
                "hold_start": contact.hold_start.isoformat() if contact.hold_start else None,
                "hold_end": contact.hold_end.isoformat() if contact.hold_end else None,
                "future_appointments_retained": len(future),
            }
        )
        return finding

    if not future:
        finding = _base_finding(
            contact,
            "NO_FUTURE_BOOKINGS",
            "Active PT contact has no valid future PT appointment.",
        )
        finding.last_completed = _iso(completed[-1].start) if completed else None
        return finding

    pattern = infer_pattern(contact, valid, calendars, now, minimum_confidence)
    if not pattern.slots or pattern.confidence < minimum_confidence:
        finding = _base_finding(
            contact,
            "PATTERN_CONFIRMATION_REQUIRED",
            pattern.reason,
        )
        finding.confidence = pattern.confidence
        finding.inferred_frequency = pattern.inferred_frequency
        finding.last_completed = _iso(completed[-1].start) if completed else None
        finding.last_future = _iso(future[-1].start)
        return finding

    if contact.expected_frequency is not None and len(pattern.slots) != contact.expected_frequency:
        finding = _base_finding(
            contact,
            "FREQUENCY_MISMATCH",
            (
                f"Expected {contact.expected_frequency} PT session(s) per week but inferred "
                f"{len(pattern.slots)} stable slot(s)."
            ),
        )
        finding.confidence = pattern.confidence
        finding.inferred_frequency = len(pattern.slots)
        finding.patterns = [slot.label for slot in pattern.slots]
        return finding

    expected: list[tuple[datetime, int, str]] = []
    for slot in pattern.slots:
        start = _next_occurrence(now, slot.weekday, slot.local_time)
        for week in range(horizon_weeks):
            expected.append(
                (start + timedelta(weeks=week), slot.duration_minutes, slot.calendar_id)
            )
    expected.sort()

    unmatched = future.copy()
    missing: list[datetime] = []
    matched_dates: list[datetime] = []
    expected_duration_by_start: dict[datetime, int] = {}
    for expected_start, expected_duration, expected_calendar in expected:
        expected_duration_by_start[expected_start] = expected_duration
        exact = next(
            (
                event
                for event in unmatched
                if event.calendar_id == expected_calendar
                and abs((event.start - expected_start).total_seconds()) <= 60
                and abs(event.duration_minutes - expected_duration) <= 1
            ),
            None,
        )
        if exact:
            unmatched.remove(exact)
            matched_dates.append(expected_start)
            continue

        same_week = next(
            (
                event
                for event in unmatched
                if event.start.isocalendar()[:2] == expected_start.isocalendar()[:2]
                and abs(event.duration_minutes - expected_duration) <= 1
            ),
            None,
        )
        if same_week:
            unmatched.remove(same_week)
            matched_dates.append(expected_start)
            continue
        missing.append(expected_start)

    # A client may intentionally make up a missed session in the immediately
    # following week. Only unmatched surplus appointments can cover the prior
    # week's deficit, so the next week's own expected sessions remain protected.
    carry_over_matches: list[dict[str, str]] = []
    still_missing: list[datetime] = []
    for expected_start in missing:
        expected_duration = expected_duration_by_start[expected_start]
        make_up_week = _week_start(expected_start) + timedelta(days=7)
        make_up = next(
            (
                event
                for event in unmatched
                if _week_start(event.start) == make_up_week
                and abs(event.duration_minutes - expected_duration) <= 1
            ),
            None,
        )
        if make_up is None:
            still_missing.append(expected_start)
            continue
        unmatched.remove(make_up)
        matched_dates.append(expected_start)
        carry_over_matches.append(
            {
                "missed_expected": expected_start.isoformat(),
                "make_up_appointment": make_up.start.isoformat(),
            }
        )
    missing = still_missing

    first_missing = min(missing) if missing else None
    booked_through = max(matched_dates) if matched_dates else None
    last_future = future[-1].start
    coverage_weeks = 0
    for week in range(horizon_weeks):
        week_expected = expected[
            week * len(pattern.slots) : (week + 1) * len(pattern.slots)
        ]
        if all(item[0] in matched_dates for item in week_expected):
            coverage_weeks += 1
        else:
            break

    if not missing:
        category = "HEALTHY"
        reason = (
            f"All {len(expected)} expected PT occurrence(s) are covered for "
            f"{horizon_weeks} weeks."
        )
        if carry_over_matches:
            reason += (
                f" {len(carry_over_matches)} session(s) are covered by an "
                "adjacent-week make-up."
            )
    elif first_missing and first_missing < last_future:
        category = "GAP_INSIDE_SERIES"
        reason = (
            f"{len(missing)} expected occurrence(s) are missing, including a gap before later bookings."
        )
    else:
        category = "WOULD_TOP_UP"
        reason = (
            f"{len(missing)} occurrence(s) would be added to restore the rolling 13-week horizon."
        )

    finding = _base_finding(contact, category, reason)
    finding.confidence = pattern.confidence
    finding.inferred_frequency = pattern.inferred_frequency
    finding.patterns = [slot.label for slot in pattern.slots]
    finding.last_completed = _iso(completed[-1].start) if completed else None
    finding.last_future = _iso(last_future)
    finding.booked_through = _iso(booked_through)
    finding.coverage_weeks = coverage_weeks
    finding.proposed_dates = [item.isoformat() for item in missing]
    finding.evidence.update(
        {
            "matched_occurrences": len(matched_dates),
            "expected_occurrences": len(expected),
            "unmatched_future_events": len(unmatched),
            "adjacent_week_make_ups": carry_over_matches,
        }
    )
    return finding
