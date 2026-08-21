from __future__ import annotations

from collections import defaultdict
from datetime import UTC, date, datetime, timedelta
from typing import Any, Iterable


DEFINITION_VERSION = "sgpt-delivery-v1"
TIMETABLE_VERSION = "sgpt-timetable-2026-07-24"
CAPACITY_VERSION = "sgpt-sop-capacity-2026-08-02"
CLASS_CAPACITY = 15
KNOWN_CLASS_NAMES = {
    "Build & Balance",
    "HybridFit",
    "Metabolic Burn",
    "Pilates",
    "Sculpt & Strength",
}


def _date(value: Any) -> date:
    return date.fromisoformat(str(value)[:10])


def _percent(numerator: int, denominator: int) -> float | None:
    if denominator <= 0:
        return None
    return round(numerator * 100 / denominator, 1)


def _outcome(row: dict[str, Any]) -> str:
    explicit = str(
        row.get("delivery_outcome")
        or row.get("attendance_outcome")
        or row.get("outcome")
        or row.get("booking_status")
        or ""
    ).strip().lower()
    aliases = {
        "attended": "attended",
        "checked_in": "attended",
        "checkedin": "attended",
        "completed": "attended",
        "complete": "attended",
        "tracked": "attended",
        "cancelled": "cancelled",
        "canceled": "cancelled",
        "no_show": "no_show",
        "no-show": "no_show",
        "noshow": "no_show",
        "missed": "no_show",
        "booked": "booked",
        "scheduled": "booked",
        "confirmed": "booked",
    }
    return aliases.get(explicit, "unknown")


def _slot_key(row: dict[str, Any]) -> str | None:
    scheduled_date = str(row.get("scheduled_date") or "")[:10]
    local_time = str(row.get("scheduled_local_time") or "").strip()
    scheduled_start = str(row.get("scheduled_start") or "")
    if not scheduled_date or (not local_time and not scheduled_start):
        return None
    try:
        day = _date(scheduled_date).strftime("%A").lower()
        time_text = local_time or datetime.fromisoformat(
            scheduled_start.replace("Z", "+00:00")
        ).strftime("%H:%M")
    except ValueError:
        return None
    return f"{day}-{time_text}"


def _breakdown(
    rows: list[dict[str, Any]],
    *,
    key_name: str,
    key_value: Any,
    class_sessions: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    outcomes = [_outcome(row) for row in rows]
    booked_rows = [
        row
        for row in rows
        if _outcome(row) in {"booked", "attended", "no_show"}
    ]
    attended = outcomes.count("attended")
    sessions = {
        str(row.get("class_session_id") or "")
        for row in rows
        if row.get("class_session_id")
    }
    capacity = sum(
        int(class_sessions[session_id]["capacity"])
        for session_id in sessions
        if session_id in class_sessions
    )
    return {
        key_name: key_value,
        "class_sessions": len(sessions),
        "capacity_places": capacity,
        "booked": len(booked_rows),
        "attended": attended,
        "cancelled": outcomes.count("cancelled"),
        "no_show": outcomes.count("no_show"),
        "booked_fill_rate": _percent(len(booked_rows), capacity),
        "attended_fill_rate": _percent(attended, capacity),
    }


def summarise_sgpt_delivery(
    events: Iterable[dict[str, Any]],
    *,
    start_date: date,
    end_date: date,
    active_sgpt_person_keys: Iterable[str] | None = None,
    identity_unmatched_events: int = 0,
) -> dict[str, Any]:
    raw_selected = [
        dict(row)
        for row in events
        if row.get("scheduled_date")
        and start_date <= _date(row["scheduled_date"]) <= end_date
    ]
    deduplicated: dict[tuple[str, str], dict[str, Any]] = {}
    for row in raw_selected:
        session_id = str(row.get("class_session_id") or "").strip()
        person_key = str(
            row.get("person_id")
            or row.get("person_key")
            or row.get("trainerize_user_id")
            or ""
        ).strip()
        if not session_id or not person_key:
            continue
        key = (session_id, person_key)
        previous = deduplicated.get(key)
        if previous is None or (
            _outcome(previous) in {"booked", "unknown"}
            and _outcome(row) not in {"booked", "unknown"}
        ):
            deduplicated[key] = row
    selected = list(deduplicated.values())
    sessions: dict[str, dict[str, Any]] = {}
    for row in selected:
        session_id = str(row.get("class_session_id") or "")
        if not session_id:
            continue
        sessions.setdefault(
            session_id,
            {
                "class_session_id": session_id,
                "class_name": str(row.get("class_name") or "Unclassified"),
                "slot_key": _slot_key(row),
                "trainer": str(
                    row.get("trainer_name") or "Unassigned"
                ).strip(),
                "duration_minutes": int(row.get("duration_minutes") or 0),
                "capacity": CLASS_CAPACITY,
            },
        )

    outcomes = [_outcome(row) for row in selected]
    booked_rows = [
        row
        for row in selected
        if _outcome(row) in {"booked", "attended", "no_show"}
    ]
    attended_rows = [
        row for row in selected if _outcome(row) == "attended"
    ]
    cancelled_rows = [
        row for row in selected if _outcome(row) == "cancelled"
    ]
    no_show_rows = [
        row for row in selected if _outcome(row) == "no_show"
    ]
    unknown_rows = [
        row for row in selected if _outcome(row) == "unknown"
    ]
    explicit_outcome_rows = attended_rows + cancelled_rows + no_show_rows
    capacity_places = sum(
        int(session["capacity"]) for session in sessions.values()
    )
    coaching_minutes = sum(
        int(session["duration_minutes"]) for session in sessions.values()
    )
    booked_members = {
        str(row.get("person_id") or row.get("person_key"))
        for row in booked_rows
        if row.get("person_id") or row.get("person_key")
    }
    served_members = {
        str(row.get("person_id") or row.get("person_key"))
        for row in attended_rows
        if row.get("person_id") or row.get("person_key")
    }
    attendance_available = bool(explicit_outcome_rows)
    roster_keys = (
        {
            str(person_key)
            for person_key in active_sgpt_person_keys
            if person_key
        }
        if active_sgpt_person_keys is not None
        else None
    )
    no_booked_or_attended = (
        len(roster_keys - booked_members - served_members)
        if roster_keys is not None
        else None
    )
    members_with_no_booking = (
        sorted(roster_keys - booked_members)
        if roster_keys is not None
        else None
    )
    members_with_no_attendance = (
        sorted(roster_keys - served_members)
        if roster_keys is not None and attendance_available
        else None
    )

    by_class: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_slot: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_trainer: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in selected:
        by_class[str(row.get("class_name") or "Unclassified")].append(row)
        by_slot[_slot_key(row) or "unmatched"].append(row)
        by_trainer[
            str(row.get("trainer_name") or "Unassigned").strip()
        ].append(row)

    timetable_matched_sessions = sum(
        bool(session["slot_key"])
        and session["class_name"] in KNOWN_CLASS_NAMES
        and session["trainer"] != "Unassigned"
        for session in sessions.values()
    )
    return {
        "definition_version": DEFINITION_VERSION,
        "period_start": start_date.isoformat(),
        "period_end": end_date.isoformat(),
        "booking_records": len(selected),
        "raw_booking_records": len(raw_selected),
        "duplicate_records_removed": len(raw_selected) - len(selected),
        "booked": len(booked_rows),
        "attended": len(attended_rows) if attendance_available else None,
        "cancelled": len(cancelled_rows) if attendance_available else None,
        "no_show": len(no_show_rows) if attendance_available else None,
        "unknown_outcomes": len(unknown_rows),
        "unique_members_booked": len(booked_members),
        "unique_members_served": (
            len(served_members) if attendance_available else None
        ),
        # Backward-compatible name used by the first Reporting V2 preview.
        "member_bookings": len(booked_rows),
        "unique_members": len(booked_members),
        "class_sessions": len(sessions),
        "coaching_hours": coaching_minutes / 60,
        "capacity_places": capacity_places,
        "booked_fill_rate": _percent(len(booked_rows), capacity_places),
        "attended_fill_rate": (
            _percent(len(attended_rows), capacity_places)
            if attendance_available
            else None
        ),
        "active_sgpt_members": (
            len(roster_keys) if roster_keys is not None else None
        ),
        "active_sgpt_members_no_booked_or_attended_delivery": (
            no_booked_or_attended
        ),
        "active_members_with_no_booking": members_with_no_booking,
        "active_members_with_no_booking_count": (
            len(members_with_no_booking)
            if members_with_no_booking is not None
            else None
        ),
        "active_members_with_no_attendance": members_with_no_attendance,
        "active_members_with_no_attendance_count": (
            len(members_with_no_attendance)
            if members_with_no_attendance is not None
            else None
        ),
        "class_breakdown": [
            _breakdown(
                rows,
                key_name="class_name",
                key_value=class_name,
                class_sessions=sessions,
            )
            for class_name, rows in sorted(by_class.items())
        ],
        "slot_breakdown": [
            _breakdown(
                rows,
                key_name="slot_key",
                key_value=slot_key,
                class_sessions=sessions,
            )
            for slot_key, rows in sorted(by_slot.items())
        ],
        "trainer_breakdown": [
            {
                **_breakdown(
                    rows,
                    key_name="trainer",
                    key_value=trainer,
                    class_sessions=sessions,
                ),
                "booked_utilisation": _percent(
                    sum(
                        _outcome(row)
                        in {"booked", "attended", "no_show"}
                        for row in rows
                    ),
                    sum(
                        int(sessions[session_id]["capacity"])
                        for session_id in {
                            str(row.get("class_session_id") or "")
                            for row in rows
                        }
                        if session_id in sessions
                    ),
                ),
                "attended_utilisation": (
                    _percent(
                        sum(_outcome(row) == "attended" for row in rows),
                        sum(
                            int(sessions[session_id]["capacity"])
                            for session_id in {
                                str(row.get("class_session_id") or "")
                                for row in rows
                            }
                            if session_id in sessions
                        ),
                    )
                    if attendance_available
                    else None
                ),
            }
            for trainer, rows in sorted(by_trainer.items())
        ],
        "attendance_available": attendance_available,
        "attendance_note": (
            "Explicit Trainerize outcomes are available. Booked, attended, "
            "cancelled and no-show remain separate."
            if attendance_available
            else (
                "Trainerize proves bookings and scheduled delivery in this "
                "period, but supplies no explicit attended, cancelled or "
                "no-show outcome. No outcome is inferred from a booking or "
                "an elapsed session."
            )
        ),
        "capacity_contract": {
            "version": CAPACITY_VERSION,
            "places_per_class": CLASS_CAPACITY,
            "basis": (
                "Current delivery SOPs specify 15 members for governed SGPT "
                "class types. The Trainerize booking ceiling of 18 is a "
                "separate configuration exception, not the safe fill-rate "
                "denominator."
            ),
        },
        "timetable_reconciliation": {
            "version": TIMETABLE_VERSION,
            "observed_sessions": len(sessions),
            "matched_sessions": timetable_matched_sessions,
            "unmatched_sessions": len(sessions) - timetable_matched_sessions,
            "coverage_percent": _percent(
                timetable_matched_sessions, len(sessions)
            ),
        },
        "identity_reconciliation": {
            "active_sgpt_members": (
                len(roster_keys) if roster_keys is not None else None
            ),
            "matched_event_records": (
                len(selected) - identity_unmatched_events
            ),
            "unmatched_event_records": identity_unmatched_events,
            "coverage_percent": _percent(
                len(selected) - identity_unmatched_events,
                len(selected),
            ),
        },
        "outcome_evidence": {
            "explicit_outcome_records": len(explicit_outcome_rows),
            "scheduled_only_records": outcomes.count("booked"),
            "unknown_records": len(unknown_rows),
            "inferred_outcome_records": 0,
        },
    }


def sgpt_delivery_preview(
    events: Iterable[dict[str, Any]],
    *,
    period_start: str,
    period_end: str,
    today: date,
    active_sgpt_person_keys: Iterable[str] | None = None,
    active_sgpt_member_ids: Iterable[str] | None = None,
    identity_unmatched_events: int = 0,
    source: dict[str, Any] | None = None,
) -> dict[str, Any]:
    rows = list(events)
    current_week_start = today - timedelta(days=today.weekday())
    current_week_end = current_week_start + timedelta(days=6)
    active_keys = (
        active_sgpt_member_ids
        if active_sgpt_member_ids is not None
        else active_sgpt_person_keys
    )
    observed_at = str((source or {}).get("observed_at") or "")
    source_age_hours = None
    try:
        observed = datetime.fromisoformat(observed_at.replace("Z", "+00:00"))
        if observed.tzinfo is None:
            observed = observed.replace(tzinfo=UTC)
        source_age_hours = round(
            (datetime.now(UTC) - observed.astimezone(UTC)).total_seconds()
            / 3600,
            1,
        )
    except ValueError:
        pass
    return {
        "available": bool(rows),
        "definition_version": DEFINITION_VERSION,
        "publication_impact": "none",
        "source": {
            "snapshot_id": (source or {}).get("snapshot_id"),
            "run_id": (source or {}).get("run_id"),
            "observed_at": observed_at or None,
            "complete": bool((source or {}).get("complete", bool(rows))),
            "status": (source or {}).get("status"),
            "age_hours": source_age_hours,
            "freshness": (
                "fresh"
                if source_age_hours is not None and source_age_hours <= 26
                else ("stale" if source_age_hours is not None else "unknown")
            ),
            "sample_count": len(rows),
        },
        "selected_period": summarise_sgpt_delivery(
            rows,
            start_date=date.fromisoformat(period_start),
            end_date=date.fromisoformat(period_end),
            active_sgpt_person_keys=active_keys,
            identity_unmatched_events=identity_unmatched_events,
        ),
        "current_week": summarise_sgpt_delivery(
            rows,
            start_date=current_week_start,
            end_date=current_week_end,
            active_sgpt_person_keys=active_keys,
            identity_unmatched_events=identity_unmatched_events,
        ),
        "acceptance": {
            "publication_state": "shadow",
            "unexplained_event_count": (
                sum(_outcome(row) == "unknown" for row in rows)
                + identity_unmatched_events
            ),
            "accepted_dashboard_unchanged": True,
            "kpi_workbook_unchanged": True,
        },
    }


# Compatibility alias retained for existing imports.
summarise_sgpt_bookings = summarise_sgpt_delivery
