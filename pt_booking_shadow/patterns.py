from __future__ import annotations

from collections import Counter
from datetime import datetime

from .models import Appointment, CalendarRecord, PatternResult, PatternSlot, PTContact


VALID_FUTURE = {"confirmed", "new", "active"}
VALID_HISTORY = VALID_FUTURE | {"showed", "completed"}


def infer_pattern(
    contact: PTContact,
    appointments: list[Appointment],
    calendars: dict[str, CalendarRecord],
    now: datetime,
    minimum_confidence: float = 0.80,
) -> PatternResult:
    usable = [
        event
        for event in appointments
        if not event.deleted
        and event.calendar_id in calendars
        and event.status in (VALID_FUTURE if event.start >= now else VALID_HISTORY)
    ]
    if not usable:
        return PatternResult(
            confidence=0.0,
            reason="No usable PT appointments were found.",
            expected_frequency=contact.expected_frequency,
            inferred_frequency=0,
        )

    future_counts: Counter[tuple[str, int, str]] = Counter()
    history_counts: Counter[tuple[str, int, str]] = Counter()
    for event in usable:
        local = event.start
        key = (event.calendar_id, local.weekday(), local.strftime("%H:%M"))
        if event.start >= now:
            future_counts[key] += 1
        else:
            history_counts[key] += 1

    all_keys = set(future_counts) | set(history_counts)
    ranked: list[tuple[float, tuple[str, int, str], int, int]] = []
    for key in all_keys:
        future = future_counts[key]
        history = history_counts[key]
        score = future * 2.0 + history
        ranked.append((score, key, future, history))
    ranked.sort(reverse=True)

    expected = contact.expected_frequency
    if expected is None:
        stable = [item for item in ranked if item[2] >= 3 or (item[2] >= 2 and item[3] >= 2)]
        inferred_frequency = min(3, len(stable))
    else:
        inferred_frequency = expected

    if inferred_frequency == 0:
        return PatternResult(
            confidence=0.45,
            reason="Appointments exist, but no repeating weekly slot is stable enough to infer.",
            expected_frequency=expected,
            inferred_frequency=0,
        )

    chosen = ranked[:inferred_frequency]
    slots: list[PatternSlot] = []
    slot_confidences: list[float] = []
    for _, key, future, history in chosen:
        calendar = calendars[key[0]]
        confidence = min(1.0, 0.55 + min(future, 8) * 0.045 + min(history, 6) * 0.025)
        slot_confidences.append(confidence)
        hour, minute = (int(part) for part in key[2].split(":"))
        slots.append(
            PatternSlot(
                weekday=key[1],
                local_time=datetime(2000, 1, 1, hour, minute).time(),
                calendar_id=calendar.id,
                trainer=calendar.trainer,
                duration_minutes=calendar.duration_minutes,
                confidence=round(confidence, 3),
                evidence_count=future + history,
            )
        )

    overall = min(slot_confidences) if slot_confidences else 0.0
    stable_text = ", ".join(slot.label for slot in sorted(slots, key=lambda item: item.weekday))
    reason = (
        f"Inferred {len(slots)} repeating weekly slot(s) from future and recent PT events: "
        f"{stable_text}."
    )
    if expected is not None and len(slots) != expected:
        overall = min(overall, 0.5)
        reason += f" Expected frequency is {expected}, but {len(slots)} slots were inferred."
    if overall < minimum_confidence:
        reason += " Confidence is below the automatic-recommendation threshold."

    return PatternResult(
        slots=sorted(slots, key=lambda item: (item.weekday, item.local_time)),
        confidence=round(overall, 3),
        reason=reason,
        expected_frequency=expected,
        inferred_frequency=len(slots),
    )
