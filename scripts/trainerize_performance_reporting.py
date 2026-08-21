#!/usr/bin/env python3
"""Build current active-member performance reporting from private Trainerize data.

The identified member and candidate files stay under data/private/. Only aggregate
statistics without names, emails or Trainerize user IDs are written to outputs/.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import sqlite3
import statistics
from collections import defaultdict
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
RECON_DB = ROOT / "data" / "private" / "integration-reporting" / "reconciliation.sqlite"
LONGITUDINAL_DB = (
    ROOT
    / "data"
    / "private"
    / "trainerize-longitudinal-audit"
    / "trainerize_longitudinal.sqlite"
)
ASSESSMENT_DB = (
    ROOT
    / "data"
    / "private"
    / "strength-assessments"
    / "strength_assessments.sqlite"
)
BRISBANE_TZ = ZoneInfo("Australia/Brisbane")


def _trainerize_local_datetime(value: Any) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(BRISBANE_TZ)


def _explicit_class_outcome(
    status: Any,
    detail: dict[str, Any],
) -> tuple[str | None, str | None, bool | None]:
    checked_in_value = detail.get("isCheckedIn")
    if checked_in_value is None:
        checked_in_value = detail.get("checkedIn")
    checked_in = checked_in_value is True
    if checked_in:
        return "attended", "trainerize_check_in", True
    raw = " ".join(
        str(
            detail.get("attendanceStatus")
            or detail.get("attendance")
            or status
            or ""
        )
        .strip()
        .lower()
        .replace("-", " ")
        .replace("_", " ")
        .split()
    )
    if raw in {"attended", "checked in", "complete", "completed"}:
        return "attended", "trainerize_terminal_status", checked_in_value
    if raw in {"cancelled", "canceled"}:
        return "cancelled", "trainerize_terminal_status", checked_in_value
    if raw in {"no show", "noshow", "missed"}:
        return "no_show", "trainerize_terminal_status", checked_in_value
    return None, None, checked_in_value


def sgpt_booking_events(
    connection: sqlite3.Connection,
    active_ids: set[int],
    *,
    today: date,
    lookback_days: int = 120,
    future_days: int = 7,
    booking_capacity: int = 18,
) -> list[dict[str, Any]]:
    table_exists = connection.execute(
        """
        SELECT 1 FROM sqlite_master
        WHERE type='table' AND name='calendar_items'
        """
    ).fetchone()
    if not table_exists or not active_ids:
        return []
    placeholders = ",".join("?" for _ in active_ids)
    start_date = today - timedelta(days=lookback_days)
    end_date = today + timedelta(days=future_days)
    rows = connection.execute(
        f"""
        SELECT trainerize_user_id, calendar_date, item_id, status, title,
               trainer_id, trainer_name, raw_json
        FROM calendar_items
        WHERE trainerize_user_id IN ({placeholders})
          AND item_type='appointmentV2'
          AND event_category='class'
          AND calendar_date BETWEEN ? AND ?
        ORDER BY calendar_date, item_id, trainerize_user_id
        """,
        (*sorted(active_ids), start_date.isoformat(), end_date.isoformat()),
    ).fetchall()
    events = []
    for row in rows:
        raw = json.loads(row["raw_json"] or "{}")
        detail = raw.get("detail") or {}
        start_at = str(detail.get("startDate") or "").strip() or None
        end_at = str(detail.get("endDate") or "").strip() or None
        local_start = _trainerize_local_datetime(start_at)
        local_end = _trainerize_local_datetime(end_at)
        duration_minutes = None
        try:
            if local_start and local_end:
                duration_minutes = int(
                    (local_end - local_start).total_seconds()
                    / 60
                )
        except (TypeError, ValueError):
            duration_minutes = None
        outcome, outcome_evidence, checked_in = _explicit_class_outcome(
            row["status"],
            {
                **detail,
                "checkedIn": (
                    detail.get("checkedIn")
                    if "checkedIn" in detail
                    else raw.get("checkedIn")
                ),
                "isCheckedIn": (
                    detail.get("isCheckedIn")
                    if "isCheckedIn" in detail
                    else raw.get("isCheckedIn")
                ),
            },
        )
        person_key = hashlib.sha256(
            f"trainerize:{int(row['trainerize_user_id'])}".encode()
        ).hexdigest()[:20]
        scheduled_date = (
            local_start.date().isoformat()
            if local_start
            else row["calendar_date"]
        )
        scheduled_local_time = (
            local_start.strftime("%H:%M") if local_start else None
        )
        slot_label = (
            f"{local_start.strftime('%A')} {scheduled_local_time}"
            if local_start
            else None
        )
        events.append(
            {
                "source_event_id": (
                    f"trainerize-class-booking:{row['item_id']}:"
                    f"{person_key}"
                ),
                "class_session_id": str(row["item_id"]),
                "person_key": person_key,
                "trainerize_user_id": str(row["trainerize_user_id"]),
                "scheduled_date": scheduled_date,
                "scheduled_start": start_at,
                "scheduled_end": end_at,
                "scheduled_local_time": scheduled_local_time,
                "slot_label": slot_label,
                "duration_minutes": duration_minutes,
                "class_name": row["title"],
                "trainer_id": (
                    str(row["trainer_id"])
                    if row["trainer_id"] is not None
                    else None
                ),
                "trainer_name": row["trainer_name"],
                "booking_status": row["status"],
                "attendance_outcome": outcome,
                "outcome_evidence": outcome_evidence,
                "checked_in": checked_in,
                "booking_capacity": booking_capacity,
                "capacity_basis": "trainerize_configured_booking_limit",
            }
        )
    return events


PRIVATE_DIR = ROOT / "data" / "private" / "integration-reporting"
PUBLIC_DIR = ROOT / "outputs" / "trainerize-reporting-reconciliation"

MOVEMENT_ALIASES = {
    "Bench Press": {"Barbell Bench Press"},
    "Deadlift": {"Barbell Deadlift"},
    "Nexus Point Squat": {
        "Nexus Point Squat",
        "Barbell Front Squat",
        "Barbell Back Squat",
    },
}
INTERNAL_TEAM_NAMES = {
    "Megan Brown",
    "Piper Mae",
    "Nora Silva",
    "Katrina Parsons",
    "Leisa Smith",
}


def iso_date(value: Any) -> date | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text[:10]).date()
    except ValueError:
        return None


def median(values: list[float]) -> float | None:
    return round(statistics.median(values), 2) if values else None


def percentile(values: list[float], p: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    position = (len(ordered) - 1) * p
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return round(ordered[lower], 2)
    value = ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)
    return round(value, 2)


def estimated_one_rep_max(weight: Any, reps: Any) -> float | None:
    try:
        load = float(weight)
        repetitions = float(reps)
    except (TypeError, ValueError):
        return None
    if load <= 0 or repetitions <= 0 or repetitions > 20:
        return None
    return load if repetitions <= 1 else load * (1 + repetitions / 30)


def canonical_movement(exercise_name: Any) -> str | None:
    name = str(exercise_name or "").strip()
    for movement, aliases in MOVEMENT_ALIASES.items():
        if name in aliases:
            return movement
    return None


def latest_complete_run(connection: sqlite3.Connection) -> str:
    row = connection.execute(
        "SELECT run_id FROM runs WHERE status='complete' ORDER BY started_at DESC LIMIT 1"
    ).fetchone()
    if not row:
        raise RuntimeError("No completed reconciliation run exists")
    return str(row[0])


def active_roster(
    connection: sqlite3.Connection, run_id: str
) -> dict[int, dict[str, Any]]:
    rows = connection.execute(
        """
        SELECT trainerize_user_id, email, first_name, last_name, client_type,
               trainer_id, latest_signed_in
        FROM trainerize_clients
        WHERE run_id=? AND roster_view='active'
        """,
        (run_id,),
    ).fetchall()
    return {int(row["trainerize_user_id"]): dict(row) for row in rows}


def workout_metrics(
    connection: sqlite3.Connection,
    active_ids: set[int],
    *,
    today: date,
) -> dict[int, dict[str, Any]]:
    if not active_ids:
        return {}
    placeholders = ",".join("?" for _ in active_ids)
    rows = connection.execute(
        f"""
        SELECT trainerize_user_id, workout_date
        FROM daily_workouts
        WHERE trainerize_user_id IN ({placeholders})
          AND lower(COALESCE(status, '')) IN ('tracked', 'completed', 'complete')
        ORDER BY trainerize_user_id, workout_date
        """,
        tuple(sorted(active_ids)),
    ).fetchall()
    dates_by_user: dict[int, list[date]] = defaultdict(list)
    for row in rows:
        observed = iso_date(row["workout_date"])
        if observed:
            dates_by_user[int(row["trainerize_user_id"])].append(observed)

    metrics: dict[int, dict[str, Any]] = {}
    for user_id in active_ids:
        dates = dates_by_user.get(user_id, [])
        first = min(dates) if dates else None
        last = max(dates) if dates else None
        metrics[user_id] = {
            "workouts_total": len(dates),
            "workout_days_total": len(set(dates)),
            "workouts_30d": sum(day >= today - timedelta(days=29) for day in dates),
            "workouts_90d": sum(day >= today - timedelta(days=89) for day in dates),
            "workouts_365d": sum(day >= today - timedelta(days=364) for day in dates),
            "first_workout_date": first.isoformat() if first else None,
            "last_workout_date": last.isoformat() if last else None,
            "days_since_last_workout": (today - last).days if last else None,
            "observed_training_span_days": (last - first).days if first and last else 0,
        }
    return metrics


def strength_metrics(
    connection: sqlite3.Connection,
    active_ids: set[int],
    *,
    today: date,
) -> dict[int, dict[str, dict[str, Any]]]:
    if not active_ids:
        return {}
    placeholders = ",".join("?" for _ in active_ids)
    rows = connection.execute(
        f"""
        SELECT trainerize_user_id, workout_date, exercise_name, weight, reps
        FROM exercise_results
        WHERE trainerize_user_id IN ({placeholders})
          AND weight > 0 AND reps > 0 AND reps <= 20
        ORDER BY trainerize_user_id, workout_date
        """,
        tuple(sorted(active_ids)),
    ).fetchall()
    observations: dict[
        tuple[int, str], dict[date, list[float]]
    ] = defaultdict(lambda: defaultdict(list))
    for row in rows:
        movement = canonical_movement(row["exercise_name"])
        observed = iso_date(row["workout_date"])
        estimate = estimated_one_rep_max(row["weight"], row["reps"])
        if movement and observed and estimate:
            observations[(int(row["trainerize_user_id"]), movement)][observed].append(
                estimate
            )

    result: dict[int, dict[str, dict[str, Any]]] = defaultdict(dict)
    for (user_id, movement), by_date in observations.items():
        all_dates = sorted(by_date)
        first_date = all_dates[0]
        baseline_end = first_date + timedelta(days=14)
        governed_baseline = max(
            value
            for observed, values in by_date.items()
            if observed <= baseline_end
            for value in values
        )
        baseline_window_end = first_date + timedelta(days=60)
        baseline = max(
            value
            for observed, values in by_date.items()
            if observed <= baseline_window_end
            for value in values
        )
        recent_start = today - timedelta(days=180)
        recent_values = [
            value
            for observed, values in by_date.items()
            if observed >= recent_start
            for value in values
        ]
        latest = max(recent_values) if recent_values else max(
            value for values in by_date.values() for value in values
        )
        last_date = all_dates[-1]
        span_days = (last_date - first_date).days
        improvement = (
            round((latest - baseline) / baseline * 100, 1)
            if baseline > 0 and span_days >= 90
            else None
        )
        horizon_improvements = {}
        for key, (minimum_day, maximum_day) in {
            "fourWeeks": (21, 42),
            "twelveWeeks": (70, 98),
            "sixMonths": (154, 210),
        }.items():
            values = [
                value
                for observed, observed_values in by_date.items()
                if (
                    first_date + timedelta(days=minimum_day)
                    <= observed
                    <= first_date + timedelta(days=maximum_day)
                )
                for value in observed_values
            ]
            horizon_improvements[key] = (
                round(
                    (max(values) - governed_baseline)
                    / governed_baseline
                    * 100,
                    1,
                )
                if governed_baseline > 0 and values
                else None
            )
        horizon_improvements["overall"] = (
            round(
                (latest - governed_baseline)
                / governed_baseline
                * 100,
                1,
            )
            if governed_baseline > 0 and span_days >= 28
            else None
        )
        result[user_id][movement] = {
            "baseline_e1rm": round(baseline, 2),
            "current_e1rm": round(latest, 2),
            "improvement_percent": improvement,
            "first_recorded_date": first_date.isoformat(),
            "last_recorded_date": last_date.isoformat(),
            "span_days": span_days,
            "horizon_improvement_percent": horizon_improvements,
        }
    return dict(result)


def aggregate_strength_improvement(
    strengths: dict[int, dict[str, dict[str, Any]]],
) -> dict[str, dict[str, Any]]:
    results: dict[str, dict[str, Any]] = {}
    for horizon in ("fourWeeks", "twelveWeeks", "sixMonths", "overall"):
        member_values = []
        for member_strength in strengths.values():
            movement_values = [
                data.get("horizon_improvement_percent", {}).get(horizon)
                for data in member_strength.values()
            ]
            comparable = [
                float(value)
                for value in movement_values
                if value is not None
            ]
            if comparable:
                member_values.append(statistics.median(comparable))
        results[horizon] = {
            "medianPercent": (
                round(statistics.median(member_values), 1)
                if member_values
                else None
            ),
            "women": len(member_values),
            "definition": (
                "Median woman-level change in estimated one-repetition "
                "maximum from the first 14 recorded days."
            ),
        }
    return results


def member_achievement_summaries(
    member_rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    def member_name(row: dict[str, Any]) -> str:
        parts = []
        for value in (
            str(row.get("first_name") or "").strip(),
            str(row.get("last_name") or "").strip(),
        ):
            cleaned = value.strip(" .,-")
            if cleaned:
                parts.append(cleaned)
        return " ".join(parts)

    eligible_rows = [
        row
        for row in member_rows
        if member_name(row) not in INTERNAL_TEAM_NAMES
    ]
    improvements = [
        float(row["best_improvement_percent"])
        for row in eligible_rows
        if row.get("best_improvement_percent") is not None
        and float(row["best_improvement_percent"]) >= 0
    ]
    p25 = percentile(improvements, 0.25)
    p75 = percentile(improvements, 0.75)
    upper_fence = (
        min(200.0, p75 + 1.5 * (p75 - p25))
        if p25 is not None and p75 is not None
        else 200.0
    )
    top_performers = []
    ranked = sorted(
        (
            row
            for row in eligible_rows
            if row.get("best_improvement_percent") is not None
            and 15
            <= float(row["best_improvement_percent"])
            <= upper_fence
            and int(row.get("workouts_total") or 0) >= 20
        ),
        key=lambda row: float(row["best_improvement_percent"]),
        reverse=True,
    )
    for row in ranked[:5]:
        top_performers.append(
            {
                "name": member_name(row),
                "result": (
                    f"{row['best_improvement_percent']:.1f}% "
                    f"{row.get('best_improving_movement') or 'strength'}"
                ),
            }
        )

    workout_milestones = []
    thresholds = (50, 100, 150, 200, 250, 300, 400, 500)
    for row in eligible_rows:
        workouts = int(row.get("workouts_total") or 0)
        completed = [
            threshold
            for threshold in thresholds
            if 0 <= workouts - threshold <= 5
        ]
        approaching = [
            threshold
            for threshold in thresholds
            if 0 < threshold - workouts <= 10
        ]
        if not completed and not approaching:
            continue
        threshold = max(completed) if completed else min(approaching)
        status = "completed" if completed else "approaching"
        workout_milestones.append(
            {
                "name": member_name(row),
                "milestone": (
                    f"{workouts} workouts, {status} {threshold}"
                ),
                "workouts": workouts,
                "threshold": threshold,
                "status": status,
            }
        )
    workout_milestones.sort(
        key=lambda row: (
            row["status"] != "completed",
            -row["threshold"],
            row["name"],
        )
    )
    return top_performers, workout_milestones[:12]


def last_assessment_dates(
    database: Path, active_ids: set[int]
) -> dict[int, date]:
    if not database.exists() or not active_ids:
        return {}
    connection = sqlite3.connect(database)
    placeholders = ",".join("?" for _ in active_ids)
    rows = connection.execute(
        f"""
        SELECT trainerize_user_id, MAX(assessment_date)
        FROM assessments
        WHERE trainerize_user_id IN ({placeholders})
        GROUP BY trainerize_user_id
        """,
        tuple(sorted(active_ids)),
    ).fetchall()
    connection.close()
    return {
        int(user_id): observed
        for user_id, value in rows
        if (observed := iso_date(value)) is not None
    }


def standards_evidence(
    database: Path,
    active_ids: set[int],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Return raw assessment observations for Hub-owned classification.

    This deliberately does not alias, score or classify an exercise. Trainerize
    owns the observation; the Operating Data Hub owns every Evolved rule.
    """
    unavailable = {
        "status": "unavailable",
        "activeMembersRequested": len(active_ids),
        "membersWithAssessmentEvidence": 0,
        "assessments": 0,
        "exerciseObservations": 0,
        "reason": "assessment evidence tables are unavailable",
    }
    if not database.exists() or not active_ids:
        return [], unavailable
    connection = sqlite3.connect(database)
    connection.row_factory = sqlite3.Row
    tables = {
        str(row[0])
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
    }
    if not {"assessments", "assessment_exercises"}.issubset(tables):
        connection.close()
        return [], unavailable

    assessment_columns = {
        str(row[1])
        for row in connection.execute("PRAGMA table_info(assessments)")
    }
    exercise_columns = {
        str(row[1])
        for row in connection.execute(
            "PRAGMA table_info(assessment_exercises)"
        )
    }
    body_columns = (
        {
            str(row[1])
            for row in connection.execute(
                "PRAGMA table_info(assessment_body_weights)"
            )
        }
        if "assessment_body_weights" in tables
        else set()
    )
    required_assessment = {
        "daily_workout_id",
        "trainerize_user_id",
        "assessment_date",
    }
    required_exercise = {
        "daily_workout_id",
        "exercise_position",
        "stat_position",
        "exercise_name",
    }
    if not (
        required_assessment <= assessment_columns
        and required_exercise <= exercise_columns
    ):
        connection.close()
        return [], {
            **unavailable,
            "reason": "assessment evidence schema is incomplete",
        }

    placeholders = ",".join("?" for _ in active_ids)
    optional_assessment = {
        "status": "NULL",
        "schema_version": "NULL",
        "workout_id": "NULL",
    }
    assessment_select = [
        column if column in assessment_columns else expression
        for column, expression in (
            ("daily_workout_id", "NULL"),
            ("trainerize_user_id", "NULL"),
            ("assessment_date", "NULL"),
            *optional_assessment.items(),
        )
    ]
    assessment_rows = connection.execute(
        f"""
        SELECT {", ".join(assessment_select)}
        FROM assessments
        WHERE trainerize_user_id IN ({placeholders})
          AND lower(COALESCE(status, 'tracked')) IN (
              'tracked', 'completed', 'complete'
          )
        ORDER BY trainerize_user_id, assessment_date, daily_workout_id
        """,
        tuple(sorted(active_ids)),
    ).fetchall()
    assessment_ids = [int(row["daily_workout_id"]) for row in assessment_rows]
    if not assessment_ids:
        connection.close()
        return [], {
            **unavailable,
            "status": "complete",
            "reason": None,
        }

    evidence_placeholders = ",".join("?" for _ in assessment_ids)
    optional_exercise = (
        "side",
        "target",
        "record_type",
        "reps",
        "weight",
        "distance",
        "time_seconds",
        "level",
    )
    exercise_select = [
        "daily_workout_id",
        "exercise_position",
        "stat_position",
        "exercise_name",
        *[
            column if column in exercise_columns else f"NULL AS {column}"
            for column in optional_exercise
        ],
    ]
    exercise_rows = connection.execute(
        f"""
        SELECT {", ".join(exercise_select)}
        FROM assessment_exercises
        WHERE daily_workout_id IN ({evidence_placeholders})
        ORDER BY daily_workout_id, exercise_position, stat_position
        """,
        tuple(assessment_ids),
    ).fetchall()
    exercises_by_assessment: dict[int, list[dict[str, Any]]] = defaultdict(
        list
    )
    for row in exercise_rows:
        assessment_id = int(row["daily_workout_id"])
        exercises_by_assessment[assessment_id].append(
            {
                "sourceObservationId": (
                    f"trainerize-assessment:{assessment_id}:"
                    f"{int(row['exercise_position'])}:"
                    f"{int(row['stat_position'])}"
                ),
                "exerciseName": row["exercise_name"],
                "side": row["side"],
                "target": row["target"],
                "recordType": row["record_type"],
                "reps": row["reps"],
                "weightKg": row["weight"],
                "distance": row["distance"],
                "timeSeconds": row["time_seconds"],
                "level": row["level"],
            }
        )

    weights: dict[int, dict[str, Any]] = {}
    required_body = {
        "daily_workout_id",
        "body_weight_kg",
    }
    if required_body <= body_columns:
        body_select = [
            "daily_workout_id",
            "body_weight_kg",
            *[
                column if column in body_columns else f"NULL AS {column}"
                for column in (
                    "measurement_date",
                    "day_offset",
                    "timing_quality",
                    "selection_method",
                )
            ],
        ]
        for row in connection.execute(
            f"""
            SELECT {", ".join(body_select)}
            FROM assessment_body_weights
            WHERE daily_workout_id IN ({evidence_placeholders})
            """,
            tuple(assessment_ids),
        ):
            weights[int(row["daily_workout_id"])] = {
                "kg": row["body_weight_kg"],
                "measurementDate": row["measurement_date"],
                "dayOffset": row["day_offset"],
                "timingQuality": row["timing_quality"],
                "selectionMethod": row["selection_method"],
            }
    connection.close()

    evidence = []
    for row in assessment_rows:
        assessment_id = int(row["daily_workout_id"])
        evidence.append(
            {
                "sourceAssessmentId": (
                    f"trainerize-assessment:{assessment_id}"
                ),
                "trainerizeUserId": int(row["trainerize_user_id"]),
                "assessmentDate": str(row["assessment_date"])[:10],
                "assessmentStatus": row["status"],
                "sourceSchemaVersion": row["schema_version"],
                "sourceWorkoutId": row["workout_id"],
                "bodyWeight": weights.get(assessment_id),
                "observations": exercises_by_assessment.get(
                    assessment_id, []
                ),
            }
        )
    members = {
        int(row["trainerizeUserId"])
        for row in evidence
        if row["observations"]
    }
    return evidence, {
        "status": "complete",
        "activeMembersRequested": len(active_ids),
        "membersWithAssessmentEvidence": len(members),
        "assessments": len(evidence),
        "exerciseObservations": sum(
            len(row["observations"]) for row in evidence
        ),
        "reason": None,
    }


def build_member_rows(
    roster: dict[int, dict[str, Any]],
    workouts: dict[int, dict[str, Any]],
    strengths: dict[int, dict[str, dict[str, Any]]],
    assessments: dict[int, date],
    *,
    today: date,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for user_id, client in sorted(
        roster.items(),
        key=lambda item: (
            str(item[1].get("last_name") or ""),
            str(item[1].get("first_name") or ""),
            item[0],
        ),
    ):
        workout = workouts.get(user_id, {})
        movement_data = strengths.get(user_id, {})
        improvements = [
            data["improvement_percent"]
            for data in movement_data.values()
            if data.get("improvement_percent") is not None
        ]
        best_movement = None
        best_improvement = None
        if improvements:
            best_movement, best_data = max(
                (
                    (movement, data)
                    for movement, data in movement_data.items()
                    if data.get("improvement_percent") is not None
                ),
                key=lambda item: item[1]["improvement_percent"],
            )
            best_improvement = best_data["improvement_percent"]

        last_assessment = assessments.get(user_id)
        assessment_age = (
            (today - last_assessment).days if last_assessment else None
        )
        due_reason = (
            "No recorded Strength Assessment"
            if last_assessment is None
            else "Assessment 180+ days old"
            if assessment_age is not None and assessment_age >= 180
            else ""
        )
        total_workouts = int(workout.get("workouts_total") or 0)
        remarkable = bool(
            total_workouts >= 50
            and (
                (best_improvement is not None and best_improvement >= 15)
                or int(workout.get("workouts_365d") or 0) >= 75
            )
        )
        rows.append(
            {
                "trainerize_user_id": user_id,
                "first_name": client.get("first_name"),
                "last_name": client.get("last_name"),
                "email": client.get("email"),
                "client_type": client.get("client_type"),
                **workout,
                "last_assessment_date": (
                    last_assessment.isoformat() if last_assessment else None
                ),
                "days_since_assessment": assessment_age,
                "reassessment_due": bool(due_reason),
                "reassessment_reason": due_reason,
                "best_improving_movement": best_movement,
                "best_improvement_percent": best_improvement,
                "remarkable_candidate": remarkable,
                "strength_json": json.dumps(movement_data, sort_keys=True),
            }
        )
    return rows


def write_private_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    os.chmod(path.parent, 0o700)
    fields = list(rows[0]) if rows else []
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    os.chmod(path, 0o600)


def build_public_summary(
    run_id: str,
    member_rows: list[dict[str, Any]],
    strengths: dict[int, dict[str, dict[str, Any]]],
    *,
    source_latest_workout: str | None,
) -> str:
    inactivity = {
        "14+ days": sum(
            row.get("days_since_last_workout") is None
            or int(row["days_since_last_workout"]) >= 14
            for row in member_rows
        ),
        "30+ days": sum(
            row.get("days_since_last_workout") is None
            or int(row["days_since_last_workout"]) >= 30
            for row in member_rows
        ),
        "60+ days": sum(
            row.get("days_since_last_workout") is None
            or int(row["days_since_last_workout"]) >= 60
            for row in member_rows
        ),
    }
    workouts_30 = [int(row.get("workouts_30d") or 0) for row in member_rows]
    workouts_90 = [int(row.get("workouts_90d") or 0) for row in member_rows]
    movement_improvements: dict[str, list[float]] = defaultdict(list)
    for member_strength in strengths.values():
        for movement, data in member_strength.items():
            if data.get("improvement_percent") is not None:
                movement_improvements[movement].append(data["improvement_percent"])

    lines = [
        "# Active-Member Performance Summary",
        "",
        f"**Reconciliation run:** {run_id}  ",
        f"**Generated:** {datetime.now(UTC).isoformat(timespec='seconds')}  ",
        f"**Detailed workout source through:** {source_latest_workout or 'Unavailable'}",
        "",
        "## Coverage",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Current Trainerize active roster | {len(member_rows):,} |",
        f"| Active clients with any recovered detailed workout | {sum(int(row.get('workouts_total') or 0) > 0 for row in member_rows):,} |",
        f"| Median completed workouts in last 30 days | {median(workouts_30) or 0:,.1f} |",
        f"| Median completed workouts in last 90 days | {median(workouts_90) or 0:,.1f} |",
        f"| Reassessment due or missing | {sum(bool(row.get('reassessment_due')) for row in member_rows):,} |",
        f"| Remarkable-results candidates | {sum(bool(row.get('remarkable_candidate')) for row in member_rows):,} |",
        "",
        "## Inactivity Signals",
        "",
        "| Signal | Active clients |",
        "|---|---:|",
    ]
    for label, count in inactivity.items():
        lines.append(f"| {label} since last recovered workout | {count:,} |")
    lines += [
        "",
        "## Observed Strength Improvement",
        "",
        "| Canonical movement | Women with 90+ day comparison | Median improvement | 25th to 75th percentile |",
        "|---|---:|---:|---:|",
    ]
    for movement in MOVEMENT_ALIASES:
        values = movement_improvements.get(movement, [])
        med = median(values)
        p25 = percentile(values, 0.25)
        p75 = percentile(values, 0.75)
        interval = (
            f"{p25:.1f}% to {p75:.1f}%" if p25 is not None and p75 is not None else "Unavailable"
        )
        lines.append(
            f"| {movement} | {len(values):,} | "
            f"{f'{med:.1f}%' if med is not None else 'Unavailable'} | {interval} |"
        )
    lines += [
        "",
        "## Interpretation",
        "",
        "Workout recency reflects the latest recovered detailed Trainerize data, not a real-time attendance guarantee. Newly active clients may not yet appear in the historical detailed-workout database.",
        "",
        "Strength change is observational. It compares the best estimated one-repetition maximum in the first 60 recorded days with the best value in the latest 180 days, requiring at least 90 days of observed history.",
        "",
        "Remarkable-results candidates require coach validation, identity verification and consent before any marketing use.",
        "",
    ]
    return "\n".join(lines)


def run_performance_reporting(
    *,
    reconciliation_database: Path = RECON_DB,
    longitudinal_database: Path = LONGITUDINAL_DB,
    assessment_database: Path = ASSESSMENT_DB,
    private_dir: Path = PRIVATE_DIR,
    public_dir: Path = PUBLIC_DIR,
    today: date | None = None,
    max_reconciliation_age_days: int = 8,
    max_workout_age_days: int = 14,
) -> dict[str, Any]:
    today = today or date.today()
    if not reconciliation_database.exists():
        raise RuntimeError("Reconciliation database does not exist")
    if not longitudinal_database.exists():
        raise RuntimeError("Longitudinal Trainerize database does not exist")

    recon = sqlite3.connect(reconciliation_database)
    recon.row_factory = sqlite3.Row
    run_id = latest_complete_run(recon)
    run_row = recon.execute(
        "SELECT started_at FROM runs WHERE run_id=?",
        (run_id,),
    ).fetchone()
    reconciliation_date = (
        iso_date(run_row["started_at"]) if run_row else None
    )
    if reconciliation_date is None:
        recon.close()
        raise RuntimeError("Completed reconciliation has no valid started_at")
    reconciliation_age_days = (today - reconciliation_date).days
    if reconciliation_age_days > max_reconciliation_age_days:
        recon.close()
        raise RuntimeError(
            "Latest completed reconciliation is stale: "
            f"{reconciliation_age_days} days old"
        )
    roster = active_roster(recon, run_id)
    recon.close()

    longitudinal = sqlite3.connect(longitudinal_database)
    longitudinal.row_factory = sqlite3.Row
    active_ids = set(roster)
    workouts = workout_metrics(longitudinal, active_ids, today=today)
    strengths = strength_metrics(longitudinal, active_ids, today=today)
    sgpt_events = sgpt_booking_events(
        longitudinal,
        active_ids,
        today=today,
    )
    source_row = longitudinal.execute(
        "SELECT MAX(workout_date) FROM daily_workouts"
    ).fetchone()
    source_latest_workout = source_row[0] if source_row else None
    observation_table = longitudinal.execute(
        """
        SELECT 1 FROM sqlite_master
        WHERE type='table' AND name='source_observations'
        """
    ).fetchone()
    source_observed_at = None
    if observation_table:
        observation_row = longitudinal.execute(
            """
            SELECT MAX(observed_at) FROM source_observations
            WHERE status='complete'
            """
        ).fetchone()
        source_observed_at = observation_row[0] if observation_row else None
    longitudinal.close()
    workout_source_date = iso_date(source_latest_workout)
    if workout_source_date is None:
        raise RuntimeError("Longitudinal workout store has no valid source date")
    observation_date = iso_date(source_observed_at) or workout_source_date
    workout_source_age_days = (today - observation_date).days
    if workout_source_age_days > max_workout_age_days:
        raise RuntimeError(
            "Detailed workout source is stale: "
            f"{workout_source_age_days} days old"
        )

    assessments = last_assessment_dates(assessment_database, active_ids)
    standard_observations, standard_coverage = standards_evidence(
        assessment_database,
        active_ids,
    )
    member_rows = build_member_rows(
        roster, workouts, strengths, assessments, today=today
    )
    run_dir = private_dir / "runs" / run_id
    write_private_csv(run_dir / "active_member_performance.csv", member_rows)
    candidates = [row for row in member_rows if row["remarkable_candidate"]]
    write_private_csv(run_dir / "remarkable_results_candidates.csv", candidates)
    reassessments = [row for row in member_rows if row["reassessment_due"]]
    write_private_csv(run_dir / "reassessment_due.csv", reassessments)

    public_dir.mkdir(parents=True, exist_ok=True)
    public_summary = build_public_summary(
        run_id,
        member_rows,
        strengths,
        source_latest_workout=source_latest_workout,
    )
    (public_dir / "latest-performance-summary.md").write_text(
        public_summary, encoding="utf-8"
    )
    summary = {
        "run_id": run_id,
        "active_roster": len(roster),
        "members_with_detailed_workouts": sum(
            int(row.get("workouts_total") or 0) > 0 for row in member_rows
        ),
        "remarkable_candidates": len(candidates),
        "reassessment_due": len(reassessments),
        "detailed_workout_source_through": source_latest_workout,
        "workout_source_observed_at": source_observed_at,
        "reconciliation_source_age_days": reconciliation_age_days,
        "workout_source_age_days": workout_source_age_days,
        "strength_improvement": aggregate_strength_improvement(strengths),
        "sgpt_booking_events": sgpt_events,
        "standards_evidence_schema_version": 1,
        "standards_evidence": standard_observations,
        "standards_evidence_coverage": standard_coverage,
    }
    top_performers, workout_milestones = member_achievement_summaries(
        member_rows
    )
    summary["top_performers"] = top_performers
    summary["workout_milestones"] = workout_milestones
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reconciliation-database", type=Path, default=RECON_DB)
    parser.add_argument("--longitudinal-database", type=Path, default=LONGITUDINAL_DB)
    parser.add_argument("--assessment-database", type=Path, default=ASSESSMENT_DB)
    parser.add_argument("--max-reconciliation-age-days", type=int, default=8)
    parser.add_argument("--max-workout-age-days", type=int, default=14)
    args = parser.parse_args()
    summary = run_performance_reporting(
        reconciliation_database=args.reconciliation_database,
        longitudinal_database=args.longitudinal_database,
        assessment_database=args.assessment_database,
        max_reconciliation_age_days=args.max_reconciliation_age_days,
        max_workout_age_days=args.max_workout_age_days,
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
