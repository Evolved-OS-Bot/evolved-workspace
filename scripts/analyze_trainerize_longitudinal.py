#!/usr/bin/env python3
"""Build de-identified longitudinal strength audit tables from Trainerize SQLite."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import sqlite3
import statistics
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data/private/trainerize-longitudinal-audit/trainerize_longitudinal.sqlite"
PRIVATE_OUT = ROOT / "data/private/trainerize-longitudinal-audit/analysis"
PUBLIC_OUT = ROOT / "outputs/trainerize-longitudinal-audit-2026-07-21"

HORIZONS = {
    "Baseline (0-60d)": (0, 60),
    "6 months (120-240d)": (120, 240),
    "12 months (300-450d)": (300, 450),
    "24 months (600-900d)": (600, 900),
    "Beyond 24 months (901d+)": (901, 10000),
}

EXERCISE_ALIASES = {
    "Bench Press": ("Barbell Bench Press",),
    "Deadlift": ("Barbell Deadlift",),
    "Romanian Deadlift": ("Barbell Romanian Deadlift",),
    "Nexus Point Squat": (
        "Nexus Point Squat",
        "Barbell Front Squat",
        "Barbell Back Squat",
    ),
    "Overhead Press": ("Barbell Overhead Press",),
    "Lat Pulldown": ("Underhand Grip Lat Pulldown",),
    "Split Squat": ("Barbell Split Squat",),
    "Farmer Walk 60s": ("Farmer Walk",),
}

STANDARD_THRESHOLDS = {
    "Bench Press": (0.25, 0.75, 1.50),
    "Deadlift": (0.50, 1.25, 2.50),
    "Romanian Deadlift": (0.60, 1.20, 1.80),
    "Nexus Point Squat": (0.50, 1.25, 2.00),
    "Overhead Press": (0.20, 0.50, 1.00),
    "Lat Pulldown": (0.30, 0.70, 1.30),
    "Farmer Walk 60s": (0.75, 1.00, 1.50),
}

# Cross-exercise families are deliberately separated from the canonical strength
# analysis above. Only the bilateral squat family currently has an ordered coaching
# progression confirmed by The Evolved: goblet squat -> Nexus Point squat. The
# Barbell Front Squat and Barbell Back Squat names were unintended Trainerize labels
# for the same Nexus squat exercise, so all three names share one canonical stage.
MOVEMENT_FAMILY_MAP = [
    # Bilateral squat progression
    ("Kettlebell Goblet Squat", "Bilateral Squat", 1, "Goblet Squat", "confirmed"),
    ("Dumbbell Goblet Squat", "Bilateral Squat", 1, "Goblet Squat", "confirmed"),
    ("Goblet Box Squat", "Bilateral Squat", 1, "Goblet Squat", "provisional variant"),
    ("Banded Goblet Squat", "Bilateral Squat", 1, "Goblet Squat", "provisional variant"),
    ("Dumbbell Heel Elevated Goblet Squat", "Bilateral Squat", 1, "Goblet Squat", "provisional variant"),
    ("Nexus Point Squat", "Bilateral Squat", 2, "Nexus Point Squat", "confirmed canonical name"),
    ("Barbell Front Squat", "Bilateral Squat", 2, "Nexus Point Squat", "confirmed unintended alias"),
    ("Barbell Back Squat", "Bilateral Squat", 2, "Nexus Point Squat", "confirmed unintended alias"),
    # Exposure families below are not assigned an ordered progression.
    ("Dumbbell Bench Press", "Horizontal Press", None, "Dumbbell Bench Press", "exposure only"),
    ("Single Arm Bench Press", "Horizontal Press", None, "Single Arm Bench Press", "exposure only"),
    ("Barbell Bench Press", "Horizontal Press", None, "Barbell Bench Press", "exposure only"),
    ("Barbell Close Grip Bench Press", "Horizontal Press", None, "Close Grip Bench Press", "exposure only"),
    ("Dumbbell Incline Bench Press", "Horizontal Press", None, "Incline Bench Press", "exposure only"),
    ("Dumbbell Romanian Deadlift", "Hinge / Deadlift", None, "Dumbbell Romanian Deadlift", "exposure only"),
    ("Staggered Stance Romanian Deadlift", "Hinge / Deadlift", None, "Staggered RDL", "exposure only"),
    ("Front Anchored Banded Barbell Romanian Deadlift", "Hinge / Deadlift", None, "Anchored Barbell RDL", "exposure only"),
    ("Barbell Romanian Deadlift", "Hinge / Deadlift", None, "Barbell Romanian Deadlift", "exposure only"),
    ("Dumbbell Deadlift", "Hinge / Deadlift", None, "Dumbbell Deadlift", "exposure only"),
    ("Trap Bar Deadlift", "Hinge / Deadlift", None, "Trap Bar Deadlift", "exposure only"),
    ("Barbell Deadlift", "Hinge / Deadlift", None, "Barbell Deadlift", "exposure only"),
    ("Underhand Grip Lat Pulldown", "Vertical Pull", None, "Lat Pulldown", "exposure only"),
    ("Close Grip Strict Lat Pulldown", "Vertical Pull", None, "Lat Pulldown", "exposure only"),
    ("Single Arm Neutral Grip Lat Pulldown", "Vertical Pull", None, "Lat Pulldown", "exposure only"),
    ("Lat Pulldown Machine Wide Grip", "Vertical Pull", None, "Lat Pulldown", "exposure only"),
    ("Band Assisted Chin Up", "Vertical Pull", None, "Assisted Chin Up", "exposure only"),
    ("Band Assisted Mid Grip Pull Up", "Vertical Pull", None, "Assisted Pull Up", "exposure only"),
    ("Chin Up", "Vertical Pull", None, "Bodyweight Chin Up", "exposure only"),
    ("Pull Up", "Vertical Pull", None, "Bodyweight Pull Up", "exposure only"),
    ("Weighted Chin Up", "Vertical Pull", None, "Weighted Chin Up", "exposure only"),
    ("ATG Split Squat", "Split Squat", None, "ATG Split Squat", "exposure only"),
    ("Barbell Split Squat", "Split Squat", None, "Barbell Split Squat", "exposure only"),
    ("Dumbbell Bulgarian Split Squat", "Split Squat", None, "Bulgarian Split Squat", "exposure only"),
    ("Front Foot Elevated Split Squat", "Split Squat", None, "Front Foot Elevated Split Squat", "exposure only"),
    ("Farmer Walk", "Loaded Carry", None, "Farmer Walk", "exposure only"),
]


def iso_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value[:10]).date()
    except ValueError:
        return None


def pseudonym(user_id: int) -> str:
    digest = hashlib.sha256(f"wsp-2026-07-21:{user_id}".encode()).hexdigest()[:10].upper()
    return f"WSP-{digest}"


def median(values: list[float]) -> float | None:
    return round(statistics.median(values), 3) if values else None


def percentile(values: list[float], p: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    position = (len(ordered) - 1) * p
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return round(ordered[lower], 3)
    result = ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)
    return round(result, 3)


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fields is None:
        fields = list(rows[0]) if rows else []
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def nearest_weight(weights: dict[int, list[tuple[date, float]]], user_id: int, on_date: date) -> float | None:
    candidates = [
        (abs((weight_date - on_date).days), value)
        for weight_date, value in weights.get(user_id, [])
        if abs((weight_date - on_date).days) <= 45
    ]
    return min(candidates)[1] if candidates else None


def standard_level(movement: str, ratio: float | None) -> tuple[int | None, str]:
    if ratio is None or movement not in STANDARD_THRESHOLDS:
        return None, "Unavailable"
    live, long, perform = STANDARD_THRESHOLDS[movement]
    if ratio >= perform:
        return 3, "Perform"
    if ratio >= long:
        return 2, "Long"
    if ratio >= live:
        return 1, "Live"
    return 0, "Below Live"


def main() -> None:
    PUBLIC_OUT.mkdir(parents=True, exist_ok=True)
    PRIVATE_OUT.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB)
    connection.row_factory = sqlite3.Row

    clients_all = {
        int(row["trainerize_user_id"]): dict(row)
        for row in connection.execute(
            """
            SELECT trainerize_user_id, first_name, last_name, email, status,
                   birth_date, sex, created_at
            FROM clients WHERE is_test_client=0
            """
        )
    }
    clients = {
        user_id: client
        for user_id, client in clients_all.items()
        if (client.get("sex") or "").lower() == "female"
    }
    workout_summary = {
        int(row["trainerize_user_id"]): dict(row)
        for row in connection.execute(
            """
            SELECT trainerize_user_id, COUNT(*) workout_count,
                   COUNT(DISTINCT workout_date) workout_days,
                   MIN(workout_date) first_workout_date,
                   MAX(workout_date) last_workout_date
            FROM daily_workouts GROUP BY trainerize_user_id
            """
        )
    }
    calendar_summary = {
        int(row["trainerize_user_id"]): dict(row)
        for row in connection.execute(
            """
            SELECT trainerize_user_id,
                   COUNT(*) completed_calendar_workouts,
                   COUNT(DISTINCT calendar_date) completed_calendar_days,
                   MIN(calendar_date) calendar_first_workout,
                   MAX(calendar_date) calendar_last_workout
            FROM calendar_items
            WHERE item_type='workoutRegular' AND status='tracked'
            GROUP BY trainerize_user_id
            """
        )
    }
    weights: dict[int, list[tuple[date, float]]] = defaultdict(list)
    for row in connection.execute(
        """
        SELECT trainerize_user_id, calendar_date, body_weight_kg
        FROM calendar_items
        WHERE item_type='bodyStat' AND body_weight_kg BETWEEN 35 AND 250
        """
    ):
        observed = iso_date(row["calendar_date"])
        if observed:
            weights[int(row["trainerize_user_id"])].append((observed, float(row["body_weight_kg"])))

    coverage_rows: list[dict[str, Any]] = []
    for user_id, client in clients.items():
        calendar = calendar_summary.get(user_id, {})
        detailed = workout_summary.get(user_id, {})
        first = iso_date(calendar.get("calendar_first_workout"))
        last = iso_date(calendar.get("calendar_last_workout"))
        span = (last - first).days if first and last else None
        expected = int(calendar.get("completed_calendar_workouts") or 0)
        saved = int(detailed.get("workout_count") or 0)
        coverage_rows.append(
            {
                "participant_id": pseudonym(user_id),
                "account_status": client["status"],
                "completed_workouts_calendar": expected,
                "detailed_workouts_saved": saved,
                "detail_coverage_pct": round(saved / expected * 100, 1) if expected else None,
                "first_workout_date": calendar.get("calendar_first_workout"),
                "last_workout_date": calendar.get("calendar_last_workout"),
                "history_span_days": span,
                "eligible_6m": bool(span is not None and span >= 120),
                "eligible_12m": bool(span is not None and span >= 300),
                "eligible_24m": bool(span is not None and span >= 600),
                "bodyweight_available": user_id in weights,
            }
        )

    exercise_rows = [
        dict(row)
        for row in connection.execute(
            """
            SELECT er.exercise_name, er.record_type, er.exercise_type,
                   COUNT(*) result_rows,
                   COUNT(DISTINCT er.trainerize_user_id) participants,
                   COUNT(DISTINCT er.daily_workout_id) workouts,
                   MIN(er.workout_date) first_seen,
                   MAX(er.workout_date) last_seen
            FROM exercise_results er
            JOIN clients c ON c.trainerize_user_id=er.trainerize_user_id
            WHERE c.is_test_client=0 AND lower(c.sex)='female'
            GROUP BY er.exercise_name, er.record_type, er.exercise_type
            ORDER BY participants DESC, result_rows DESC
            """
        )
    ]

    family_lookup = {
        exercise: {
            "family": family,
            "stage": stage,
            "stage_label": stage_label,
            "mapping_status": mapping_status,
        }
        for exercise, family, stage, stage_label, mapping_status in MOVEMENT_FAMILY_MAP
    }
    mapped_names = list(family_lookup)
    family_observations = [
        dict(row)
        for row in connection.execute(
            """
            SELECT trainerize_user_id, workout_date, daily_workout_id, exercise_name,
                   COUNT(*) result_rows
            FROM exercise_results
            WHERE exercise_name IN ({})
            GROUP BY trainerize_user_id, workout_date, daily_workout_id, exercise_name
            """.format(",".join("?" for _ in mapped_names)),
            mapped_names,
        )
    ]
    exercise_family_counts: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "participants": set(), "workouts": set(), "result_rows": 0,
            "first_seen": None, "last_seen": None,
        }
    )
    family_counts: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "participants": set(), "workouts": set(), "result_rows": 0,
            "first_seen": None, "last_seen": None, "exercises": set(),
        }
    )
    for row in family_observations:
        if int(row["trainerize_user_id"]) not in clients:
            continue
        exercise = row["exercise_name"]
        family = family_lookup[exercise]["family"]
        for target in (exercise_family_counts[exercise], family_counts[family]):
            target["participants"].add(int(row["trainerize_user_id"]))
            target["workouts"].add(int(row["daily_workout_id"]))
            target["result_rows"] += int(row["result_rows"])
            target["first_seen"] = min(filter(None, [target["first_seen"], row["workout_date"]]))
            target["last_seen"] = max(filter(None, [target["last_seen"], row["workout_date"]]))
        family_counts[family]["exercises"].add(exercise)

    movement_family_map_rows: list[dict[str, Any]] = []
    for exercise, family, stage, stage_label, mapping_status in MOVEMENT_FAMILY_MAP:
        counts = exercise_family_counts[exercise]
        movement_family_map_rows.append(
            {
                "movement_family": family,
                "stage_number": stage,
                "stage_label": stage_label,
                "source_exercise_name": exercise,
                "mapping_status": mapping_status,
                "participants": len(counts["participants"]),
                "workouts": len(counts["workouts"]),
                "result_rows": counts["result_rows"],
                "first_seen": counts["first_seen"],
                "last_seen": counts["last_seen"],
                "comparison_rule": "Canonical Nexus alias; combine loads across the three confirmed source names"
                if family == "Bilateral Squat" and stage == 2
                else "Goblet stage; do not compare load numerically with canonical Nexus Squat"
                if family == "Bilateral Squat"
                else "Exposure grouping only; exact-exercise outcome analysis remains authoritative",
            }
        )

    movement_family_exposure_rows: list[dict[str, Any]] = []
    for family, counts in sorted(family_counts.items()):
        movement_family_exposure_rows.append(
            {
                "movement_family": family,
                "participants": len(counts["participants"]),
                "workouts": len(counts["workouts"]),
                "result_rows": counts["result_rows"],
                "mapped_exercises": len(counts["exercises"]),
                "first_seen": counts["first_seen"],
                "last_seen": counts["last_seen"],
                "analysis_use": "Ordered stage transitions"
                if family == "Bilateral Squat"
                else "Exposure and future mapping review only",
            }
        )

    squat_daily_stage: dict[tuple[int, date], dict[str, Any]] = {}
    for row in family_observations:
        if int(row["trainerize_user_id"]) not in clients:
            continue
        mapping = family_lookup[row["exercise_name"]]
        if mapping["family"] != "Bilateral Squat" or mapping["stage"] is None:
            continue
        observed_date = iso_date(row["workout_date"])
        if not observed_date:
            continue
        key = (int(row["trainerize_user_id"]), observed_date)
        candidate = {
            "stage": int(mapping["stage"]),
            "stage_label": mapping["stage_label"],
            "exercise": row["exercise_name"],
            "mapping_status": mapping["mapping_status"],
            "date": observed_date,
        }
        if candidate["stage"] > squat_daily_stage.get(key, {}).get("stage", -1):
            squat_daily_stage[key] = candidate

    squat_observations_by_user: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for (user_id, _), observation in squat_daily_stage.items():
        squat_observations_by_user[user_id].append(observation)
    squat_lifetime_progression_rows: list[dict[str, Any]] = []
    private_squat_lifetime_progression_rows: list[dict[str, Any]] = []
    for user_id, observations in squat_observations_by_user.items():
        observations.sort(key=lambda item: item["date"])
        first_goblet = next((item for item in observations if item["stage"] == 1), None)
        first_nexus_after = next(
            (
                item for item in observations
                if first_goblet and item["stage"] == 2 and item["date"] > first_goblet["date"]
            ),
            None,
        )
        first_mapped_stage = observations[0]["stage"]
        prior_higher_stage_before_goblet = bool(
            first_goblet
            and any(item["stage"] > 1 and item["date"] < first_goblet["date"] for item in observations)
        )
        clean_goblet_to_nexus = bool(
            first_goblet
            and first_nexus_after
            and first_mapped_stage == 1
            and not prior_higher_stage_before_goblet
        )
        common = {
            "participant_id": pseudonym(user_id),
            "account_status": clients[user_id]["status"],
            "first_mapped_squat_date": observations[0]["date"].isoformat(),
            "first_mapped_stage": first_mapped_stage,
            "first_mapped_stage_label": observations[0]["stage_label"],
            "last_mapped_squat_date": observations[-1]["date"].isoformat(),
            "first_goblet_date": first_goblet["date"].isoformat() if first_goblet else None,
            "first_nexus_after_goblet_date": first_nexus_after["date"].isoformat() if first_nexus_after else None,
            "days_goblet_to_nexus": (first_nexus_after["date"] - first_goblet["date"]).days
            if first_goblet and first_nexus_after else None,
            "observed_goblet_then_nexus_sequence": bool(first_nexus_after),
            "prior_higher_stage_before_goblet": prior_higher_stage_before_goblet,
            "clean_goblet_to_nexus_progression": clean_goblet_to_nexus,
            "highest_stage_observed": max(item["stage"] for item in observations),
            "highest_stage_label": max(observations, key=lambda item: item["stage"])["stage_label"],
            "interpretation": "Chronological Goblet-to-Nexus stage evidence; Goblet and Nexus loads are not compared",
        }
        squat_lifetime_progression_rows.append(common)
        private_squat_lifetime_progression_rows.append(
            {
                **common,
                "trainerize_user_id": user_id,
                "first_name": clients[user_id]["first_name"],
                "last_name": clients[user_id]["last_name"],
                "email": clients[user_id]["email"],
            }
        )

    names_to_movement = {
        exercise: movement
        for movement, exercises in EXERCISE_ALIASES.items()
        for exercise in exercises
    }
    daily_best: dict[tuple[int, str, date], float] = {}
    daily_reps: dict[tuple[int, str, date], float | None] = {}
    daily_weight: dict[tuple[int, str, date], float] = {}
    daily_source_exercise: dict[tuple[int, str, date], str] = {}
    for row in connection.execute(
        """
        SELECT trainerize_user_id, workout_date, exercise_name, record_type,
               reps, weight, target, target_detail
        FROM exercise_results
        WHERE exercise_name IN ({}) AND weight IS NOT NULL AND weight >= 0
        """.format(",".join("?" for _ in names_to_movement)),
        list(names_to_movement),
    ):
        if int(row["trainerize_user_id"]) not in clients:
            continue
        movement = names_to_movement[row["exercise_name"]]
        workout_date = iso_date(row["workout_date"])
        if not workout_date:
            continue
        weight = float(row["weight"])
        reps = float(row["reps"]) if row["reps"] is not None else None
        if movement == "Farmer Walk 60s":
            protocol = f"{row['target'] or ''} {row['target_detail'] or ''}".lower()
            if not any(token in protocol for token in ('60 sec', '60 seconds', '1 minute', '"time":60')):
                continue
            score = weight
        else:
            if reps is None or not 1 <= reps <= 12:
                continue
            score = weight * (1 + reps / 30.0)
        key = (int(row["trainerize_user_id"]), movement, workout_date)
        if score > daily_best.get(key, -1):
            daily_best[key] = score
            daily_reps[key] = reps
            daily_weight[key] = weight
            daily_source_exercise[key] = row["exercise_name"]

    first_workout = {
        user_id: iso_date(row.get("first_workout_date"))
        for user_id, row in workout_summary.items()
    }
    horizon_best: dict[tuple[int, str, str], dict[str, Any]] = {}
    for (user_id, movement, observed_date), score in daily_best.items():
        origin = first_workout.get(user_id)
        if not origin:
            continue
        day = (observed_date - origin).days
        for horizon, (start, end) in HORIZONS.items():
            if start <= day <= end:
                key = (user_id, movement, horizon)
                if score > horizon_best.get(key, {}).get("score", -1):
                    bodyweight = nearest_weight(weights, user_id, observed_date)
                    ratio = score / bodyweight if bodyweight else None
                    level_num, level_name = standard_level(movement, ratio)
                    horizon_best[key] = {
                        "score": score,
                        "observed_weight": daily_weight[(user_id, movement, observed_date)],
                        "reps": daily_reps[(user_id, movement, observed_date)],
                        "source_exercise_name": daily_source_exercise[(user_id, movement, observed_date)],
                        "date": observed_date.isoformat(),
                        "day": day,
                        "bodyweight": bodyweight,
                        "ratio": ratio,
                        "standard_level_num": level_num,
                        "standard_level": level_name,
                    }

    squat_horizon_stage: dict[tuple[int, str], dict[str, Any]] = {}
    for (user_id, observed_date), result in squat_daily_stage.items():
        origin = first_workout.get(user_id)
        if not origin:
            continue
        day = (observed_date - origin).days
        for horizon, (start, end) in HORIZONS.items():
            if not start <= day <= end:
                continue
            key = (user_id, horizon)
            current = squat_horizon_stage.get(key)
            if (
                current is None
                or result["stage"] > current["stage"]
                or (result["stage"] == current["stage"] and observed_date < current["date"])
            ):
                squat_horizon_stage[key] = {**result, "day": day}

    squat_progression_rows: list[dict[str, Any]] = []
    private_squat_progression_rows: list[dict[str, Any]] = []
    for user_id, client in clients.items():
        baseline = squat_horizon_stage.get((user_id, "Baseline (0-60d)"))
        if not baseline:
            continue
        for horizon in list(HORIZONS)[1:]:
            followup = squat_horizon_stage.get((user_id, horizon))
            if not followup:
                continue
            stage_change = followup["stage"] - baseline["stage"]
            confirmed_advance = baseline["stage"] == 1 and followup["stage"] == 2
            progression_classification = (
                "Advanced: confirmed Goblet to Nexus"
                if confirmed_advance
                else "Same highest stage observed"
                if stage_change == 0
                else "Only a lower stage was observed in this window; not evidence of regression"
            )
            common = {
                "participant_id": pseudonym(user_id),
                "account_status": client["status"],
                "horizon": horizon,
                "baseline_stage": baseline["stage"],
                "baseline_stage_label": baseline["stage_label"],
                "baseline_exercise": baseline["exercise"],
                "baseline_date": baseline["date"].isoformat(),
                "followup_stage": followup["stage"],
                "followup_stage_label": followup["stage_label"],
                "followup_exercise": followup["exercise"],
                "followup_date": followup["date"].isoformat(),
                "stages_gained": stage_change,
                "confirmed_goblet_to_nexus": confirmed_advance,
                "progression_classification": progression_classification,
            }
            squat_progression_rows.append(common)
            private_squat_progression_rows.append(
                {
                    **common,
                    "trainerize_user_id": user_id,
                    "first_name": client["first_name"],
                    "last_name": client["last_name"],
                    "email": client["email"],
                }
            )

    squat_progression_outcomes: list[dict[str, Any]] = []
    for horizon in list(HORIZONS)[1:]:
        rows = [row for row in squat_progression_rows if row["horizon"] == horizon]
        advanced = [row for row in rows if row["stages_gained"] > 0]
        confirmed = [row for row in rows if row["confirmed_goblet_to_nexus"]]
        maintained = [row for row in rows if row["stages_gained"] == 0]
        lower_only = [row for row in rows if row["stages_gained"] < 0]
        squat_progression_outcomes.append(
            {
                "horizon": horizon,
                "paired_participants": len(rows),
                "advanced_stage_n": len(advanced),
                "advanced_stage_pct": round(len(advanced) / len(rows) * 100, 1) if rows else None,
                "confirmed_goblet_to_nexus_n": len(confirmed),
                "confirmed_goblet_to_nexus_pct": round(len(confirmed) / len(rows) * 100, 1) if rows else None,
                "same_highest_stage_n": len(maintained),
                "lower_stage_only_n": len(lower_only),
                "median_stage_change": median([row["stages_gained"] for row in rows]),
                "interpretation": "Exercise-stage transition, not a cross-exercise load comparison",
            }
        )

    private_trajectories: list[dict[str, Any]] = []
    deidentified_trajectories: list[dict[str, Any]] = []
    for (user_id, movement, horizon), result in sorted(horizon_best.items()):
        baseline = horizon_best.get((user_id, movement, "Baseline (0-60d)"))
        pct = (
            (result["score"] / baseline["score"] - 1) * 100
            if baseline and baseline["score"] > 0 and horizon != "Baseline (0-60d)"
            else None
        )
        level_gain = (
            result["standard_level_num"] - baseline["standard_level_num"]
            if baseline
            and result["standard_level_num"] is not None
            and baseline["standard_level_num"] is not None
            else None
        )
        common = {
            "participant_id": pseudonym(user_id),
            "account_status": clients[user_id]["status"],
            "movement": movement,
            "source_exercise_name": result["source_exercise_name"],
            "horizon": horizon,
            "best_score_kg": round(result["score"], 2),
            "recorded_weight_kg": round(result["observed_weight"], 2),
            "recorded_reps": result["reps"],
            "result_date": result["date"],
            "days_from_first_workout": result["day"],
            "bodyweight_kg_near_result": round(result["bodyweight"], 2) if result["bodyweight"] else None,
            "score_to_bodyweight_ratio": round(result["ratio"], 3) if result["ratio"] else None,
            "standard_level": result["standard_level"],
            "change_from_baseline_pct": round(pct, 1) if pct is not None else None,
            "standard_levels_gained": level_gain,
        }
        deidentified_trajectories.append(common)
        private_trajectories.append(
            {
                **common,
                "trainerize_user_id": user_id,
                "first_name": clients[user_id]["first_name"],
                "last_name": clients[user_id]["last_name"],
                "email": clients[user_id]["email"],
            }
        )

    movement_rows: list[dict[str, Any]] = []
    for movement in EXERCISE_ALIASES:
        for horizon in list(HORIZONS)[1:]:
            pairs: list[tuple[dict[str, Any], dict[str, Any]]] = []
            statuses = Counter()
            for user_id in clients:
                baseline = horizon_best.get((user_id, movement, "Baseline (0-60d)"))
                followup = horizon_best.get((user_id, movement, horizon))
                if baseline and followup and baseline["score"] > 0:
                    pairs.append((baseline, followup))
                    statuses[clients[user_id]["status"]] += 1
            changes = [(follow["score"] / base["score"] - 1) * 100 for base, follow in pairs]
            absolute = [follow["score"] - base["score"] for base, follow in pairs]
            movement_rows.append(
                {
                    "movement": movement,
                    "horizon": horizon,
                    "paired_participants": len(pairs),
                    "active_accounts": statuses["active"],
                    "deactivated_accounts": statuses["deactivated"],
                    "median_baseline_score_kg": median([b["score"] for b, _ in pairs]),
                    "median_followup_score_kg": median([f["score"] for _, f in pairs]),
                    "median_absolute_gain_kg": median(absolute),
                    "median_change_pct": median(changes),
                    "p25_change_pct": percentile(changes, 0.25),
                    "p75_change_pct": percentile(changes, 0.75),
                    "material_improvement_n": sum(
                        change >= 20 and gain >= 5
                        for change, gain in zip(changes, absolute)
                    ),
                    "material_improvement_pct": round(
                        sum(change >= 20 and gain >= 5 for change, gain in zip(changes, absolute))
                        / len(pairs)
                        * 100,
                        1,
                    ) if pairs else None,
                }
            )

    transition_rows: list[dict[str, Any]] = []
    for row in deidentified_trajectories:
        if row["horizon"] == "Baseline (0-60d)" or row["standard_levels_gained"] is None:
            continue
        baseline = horizon_best[
            (
                next(uid for uid in clients if pseudonym(uid) == row["participant_id"]),
                row["movement"],
                "Baseline (0-60d)",
            )
        ]
        transition_rows.append(
            {
                "participant_id": row["participant_id"],
                "account_status": row["account_status"],
                "movement": row["movement"],
                "baseline_source_exercise": baseline["source_exercise_name"],
                "followup_source_exercise": row["source_exercise_name"],
                "horizon": row["horizon"],
                "baseline_level": baseline["standard_level"],
                "followup_level": row["standard_level"],
                "levels_gained": row["standard_levels_gained"],
                "baseline_ratio": round(baseline["ratio"], 3) if baseline["ratio"] else None,
                "followup_ratio": row["score_to_bodyweight_ratio"],
            }
        )

    remarkable: list[dict[str, Any]] = []
    by_person_horizon: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in deidentified_trajectories:
        if row["horizon"] != "Baseline (0-60d)" and row["change_from_baseline_pct"] is not None:
            by_person_horizon[(row["participant_id"], row["horizon"])].append(row)
    for (participant_id, horizon), rows in by_person_horizon.items():
        material = [r for r in rows if r["change_from_baseline_pct"] >= 20 and r["best_score_kg"] - next(
            b["best_score_kg"] for b in deidentified_trajectories
            if b["participant_id"] == participant_id and b["movement"] == r["movement"] and b["horizon"] == "Baseline (0-60d)"
        ) >= 5]
        large = [r for r in rows if r["change_from_baseline_pct"] >= 50]
        standards = [r for r in rows if (r["standard_levels_gained"] or 0) >= 1]
        if len(material) >= 3 or large or len(standards) >= 2:
            remarkable.append(
                {
                    "participant_id": participant_id,
                    "account_status": rows[0]["account_status"],
                    "horizon": horizon,
                    "movements_with_material_improvement": len(material),
                    "largest_change_pct": round(max(r["change_from_baseline_pct"] for r in rows), 1),
                    "movements_advancing_standard": len(standards),
                    "candidate_reason": "; ".join(
                        filter(None, [
                            f"{len(material)} movements improved >=20% and >=5kg" if len(material) >= 3 else None,
                            "at least one movement improved >=50%" if large else None,
                            f"{len(standards)} movements advanced a standard" if len(standards) >= 2 else None,
                        ])
                    ),
                    "review_required": "Yes: validate exercise conventions and member consent before use",
                }
            )

    tracked_counts = [
        int(calendar_summary[user_id]["completed_calendar_workouts"])
        for user_id in clients
        if user_id in calendar_summary
    ]
    tracked_spans = [
        row["history_span_days"]
        for row in coverage_rows
        if row["history_span_days"] is not None
    ]
    total_tracked_workouts = sum(tracked_counts)
    total_tracked_days = sum(
        int(calendar_summary[user_id]["completed_calendar_days"])
        for user_id in clients
        if user_id in calendar_summary
    )
    all_account_tracked_workouts = sum(
        int(row["completed_calendar_workouts"])
        for row in calendar_summary.values()
    )
    recorded_sex_counts = Counter()
    recorded_sex_workout_counts = Counter()
    for user_id, client in clients_all.items():
        recorded_sex = (client.get("sex") or "").strip().lower() or "missing"
        recorded_sex_counts[recorded_sex] += 1
        recorded_sex_workout_counts[recorded_sex] += int(
            calendar_summary.get(user_id, {}).get("completed_calendar_workouts") or 0
        )
    unique_candidate_ids = {row["participant_id"] for row in remarkable}
    multi_material_ids = {
        row["participant_id"]
        for row in remarkable
        if row["movements_with_material_improvement"] >= 3
    }
    multi_standard_ids = {
        row["participant_id"]
        for row in remarkable
        if row["movements_advancing_standard"] >= 2
    }
    strict_horizon_confirmed_squat_progression_ids = {
        row["participant_id"]
        for row in squat_progression_rows
        if row["confirmed_goblet_to_nexus"]
    }
    observed_goblet_nexus_sequence_ids = {
        row["participant_id"]
        for row in squat_lifetime_progression_rows
        if row["observed_goblet_then_nexus_sequence"]
    }
    confirmed_squat_progression_ids = {
        row["participant_id"]
        for row in squat_lifetime_progression_rows
        if row["clean_goblet_to_nexus_progression"]
    }
    marketing_milestone_rows: list[dict[str, Any]] = []
    tracked_participants = len(tracked_counts)
    for threshold in (1, 25, 50, 100, 250, 500):
        count = sum(value >= threshold for value in tracked_counts)
        marketing_milestone_rows.append(
            {
                "completed_workout_threshold": threshold,
                "confirmed_female_participants": count,
                "pct_of_confirmed_female_participants_with_workouts": round(count / tracked_participants * 100, 1)
                if tracked_participants else None,
                "claim_status": "Descriptive operational metric; not a health outcome",
            }
        )

    first_tracked_date = min(
        row["calendar_first_workout"] for user_id, row in calendar_summary.items()
        if user_id in clients and row.get("calendar_first_workout")
    )
    last_tracked_date = max(
        row["calendar_last_workout"] for user_id, row in calendar_summary.items()
        if user_id in clients and row.get("calendar_last_workout")
    )
    detailed_ids_female = set(workout_summary) & set(clients)
    female_exercise_result_rows = connection.execute(
        """
        SELECT COUNT(*) FROM exercise_results er
        JOIN clients c ON c.trainerize_user_id=er.trainerize_user_id
        WHERE c.is_test_client=0 AND lower(c.sex)='female'
        """
    ).fetchone()[0]
    marketing_evidence_rows = [
        {
            "category": "Cohort scope",
            "metric": "Confirmed-female accounts",
            "value": len(clients),
            "unit": "accounts",
            "recommended_wording": f"The accessible Trainerize account contains {len(clients):,} accounts explicitly recorded as female.",
            "claim_status": "Marketing-ready with scope stated",
            "caveat": f"Another {len(clients_all) - len(clients):,} non-test accounts are male, other or have no sex recorded and are excluded from women's outcome analysis.",
        },
        {
            "category": "Training activity",
            "metric": "Tracked completed workouts",
            "value": total_tracked_workouts,
            "unit": "workouts",
            "recommended_wording": f"Women have completed more than {total_tracked_workouts // 1000 * 1000:,} tracked workouts in the accessible Trainerize history.",
            "claim_status": "Marketing-ready with date range",
            "caveat": f"Confirmed-female accounts only; accessible history runs from {first_tracked_date} to {last_tracked_date}. All-account operational total is {all_account_tracked_workouts:,}.",
        },
        {
            "category": "Training activity",
            "metric": "All-account tracked programmed workouts",
            "value": all_account_tracked_workouts,
            "unit": "workouts",
            "recommended_wording": f"The accessible Trainerize account contains {all_account_tracked_workouts:,} tracked programmed workouts across all non-test client profiles.",
            "claim_status": "Internal evidence pending demographic verification",
            "caveat": "Includes 44 profiles not currently recorded as female: 34 have no sex value, 7 are recorded male and 3 are recorded other. The business owner reports these are onboarding classifications requiring review; do not describe the total as women's data until verified.",
        },
        {
            "category": "Training activity",
            "metric": "Distinct participant workout days",
            "value": total_tracked_days,
            "unit": "participant-days",
            "recommended_wording": f"The dataset contains {total_tracked_days:,} distinct days on which a woman completed at least one tracked workout.",
            "claim_status": "Internal evidence",
            "caveat": "Two workouts completed by one participant on the same date count as one participant-day.",
        },
        {
            "category": "Training activity",
            "metric": "Women with at least one tracked workout",
            "value": tracked_participants,
            "unit": "participants",
            "recommended_wording": f"The accessible history includes completed training for {tracked_participants:,} women.",
            "claim_status": "Marketing-ready with scope stated",
            "caveat": "Counts accounts explicitly recorded as female and excludes test accounts.",
        },
        {
            "category": "Training records",
            "metric": "Detailed workouts recovered",
            "value": sum(int(workout_summary[user_id]["workout_count"]) for user_id in detailed_ids_female),
            "unit": "detailed workouts",
            "recommended_wording": "The audit recovered more than 22,000 detailed workout records for women.",
            "claim_status": "Marketing-ready as a dataset-scale claim",
            "caveat": "Detailed API coverage is incomplete for former members; do not call this the total number of workouts completed.",
        },
        {
            "category": "Training records",
            "metric": "Exercise-result records",
            "value": female_exercise_result_rows,
            "unit": "result rows",
            "recommended_wording": f"The women's audit contains more than {female_exercise_result_rows // 100000 * 100000:,} recorded exercise results.",
            "claim_status": "Marketing-ready as a dataset-scale claim",
            "caveat": "A result row is not always equivalent to one completed set; use 'recorded exercise results', not 'sets'.",
        },
        {
            "category": "Training consistency",
            "metric": "Median tracked workouts per woman",
            "value": median(tracked_counts),
            "unit": "workouts",
            "recommended_wording": "Use internally to describe the distribution; milestone counts are clearer for public marketing.",
            "claim_status": "Internal evidence",
            "caveat": "Median is among women with at least one tracked workout, not every account or member ever sold.",
        },
        {
            "category": "Training tenure",
            "metric": "Women with at least 6 months between first and last tracked workout",
            "value": sum(span >= 180 for span in tracked_spans),
            "unit": "participants",
            "recommended_wording": "Use as evidence of longitudinal depth, not as a retention rate.",
            "claim_status": "Internal evidence",
            "caveat": "A calendar span does not prove uninterrupted membership or regular weekly attendance.",
        },
        {
            "category": "Training tenure",
            "metric": "Women with at least 12 months between first and last tracked workout",
            "value": sum(span >= 365 for span in tracked_spans),
            "unit": "participants",
            "recommended_wording": "Use as evidence of longitudinal depth, not as a retention rate.",
            "claim_status": "Internal evidence",
            "caveat": "A calendar span does not prove uninterrupted membership or regular weekly attendance.",
        },
        {
            "category": "Training tenure",
            "metric": "Women with at least 24 months between first and last tracked workout",
            "value": sum(span >= 730 for span in tracked_spans),
            "unit": "participants",
            "recommended_wording": "Use as evidence that the database contains multi-year histories.",
            "claim_status": "Internal evidence",
            "caveat": "A calendar span does not prove uninterrupted membership or regular weekly attendance.",
        },
        {
            "category": "Outcome screening",
            "metric": "Unique remarkable-result screening candidates",
            "value": len(unique_candidate_ids),
            "unit": "participants",
            "recommended_wording": "Internal story-development pipeline only.",
            "claim_status": "Requires coach validation and member consent",
            "caveat": "Candidates are algorithmic screening flags, not verified transformations or causal claims.",
        },
        {
            "category": "Outcome screening",
            "metric": "Women with material improvement in at least 3 canonical movements",
            "value": len(multi_material_ids),
            "unit": "participants",
            "recommended_wording": "Internal evidence for case review; validate each exercise history before publishing.",
            "claim_status": "Requires validation and consent",
            "caveat": "Material means at least 20% and 5 kg improvement in comparable estimated strength scores.",
        },
        {
            "category": "Standards screening",
            "metric": "Women advancing at least 2 mapped relative-strength standards",
            "value": len(multi_standard_ids),
            "unit": "participants",
            "recommended_wording": "Internal candidate list for standards-based success stories.",
            "claim_status": "Requires validation and consent",
            "caveat": "Requires nearby bodyweight and is unavailable for many follow-up results.",
        },
        {
            "category": "Movement progression",
            "metric": "Women with clean observed Goblet-to-Nexus progression",
            "value": len(confirmed_squat_progression_ids),
            "unit": "participants",
            "recommended_wording": "Internal evidence that the observed squat history began with Goblet Squat and later reached Nexus Point Squat.",
            "claim_status": "Requires coach validation before public use",
            "caveat": "Counts an exercise-stage transition, not a directly comparable kilogram improvement; accessible history may still omit older training.",
        },
        {
            "category": "Movement progression",
            "metric": "Women with any observed Goblet-then-Nexus sequence",
            "value": len(observed_goblet_nexus_sequence_ids),
            "unit": "participants",
            "recommended_wording": "Use as a programming-pattern signal, not as a progression result.",
            "claim_status": "Internal evidence",
            "caveat": "Some women had a higher-stage squat recorded before Goblet because accessible history begins mid-journey or programming cycles revisit earlier movements.",
        },
    ]

    state_counts = Counter(row["account_status"] for row in coverage_rows)
    detailed_ids = detailed_ids_female
    completed_changes = connection.execute(
        "SELECT COUNT(*) FROM account_state_changes WHERE restored_at IS NOT NULL"
    ).fetchone()[0]
    open_changes = connection.execute(
        "SELECT COUNT(*) FROM account_state_changes WHERE restored_at IS NULL"
    ).fetchone()[0]
    error_counts = Counter(
        row["stage"] for row in connection.execute("SELECT stage FROM extraction_errors")
    )
    summary = {
        "audit_date": "2026-07-22",
        "non_test_accounts": len(clients_all),
        "confirmed_female_analysis_accounts": len(clients),
        "accounts_excluded_from_womens_analysis": len(clients_all) - len(clients),
        "recorded_sex_counts": dict(recorded_sex_counts),
        "recorded_sex_workout_counts": dict(recorded_sex_workout_counts),
        "account_status_counts": dict(state_counts),
        "accounts_with_completed_calendar_workouts": len(set(calendar_summary) & set(clients)),
        "accounts_with_detailed_workouts": len(detailed_ids),
        "active_accounts_with_detail": sum(clients[uid]["status"] == "active" for uid in detailed_ids),
        "deactivated_accounts_with_detail": sum(clients[uid]["status"] == "deactivated" for uid in detailed_ids),
        "detailed_workouts": sum(int(workout_summary[uid]["workout_count"]) for uid in detailed_ids),
        "exercise_result_rows": female_exercise_result_rows,
        "bodyweight_participants": len(set(weights) & set(clients)),
        "paired_outcome_rows": sum(row["paired_participants"] for row in movement_rows),
        "remarkable_candidate_rows": len(remarkable),
        "remarkable_candidate_participants": len(unique_candidate_ids),
        "confirmed_goblet_to_nexus_participants": len(confirmed_squat_progression_ids),
        "observed_goblet_then_nexus_sequence_participants": len(observed_goblet_nexus_sequence_ids),
        "strict_horizon_goblet_to_nexus_participants": len(strict_horizon_confirmed_squat_progression_ids),
        "tracked_completed_workouts": total_tracked_workouts,
        "all_account_tracked_workouts": all_account_tracked_workouts,
        "tracked_participants": tracked_participants,
        "temporary_change_log_rows": completed_changes,
        "unrestored_temporary_changes": open_changes,
        "extraction_error_rows": sum(error_counts.values()),
        "extraction_errors_by_stage": dict(error_counts),
        "methodological_status": "Retrospective observational training-log audit; not a controlled scientific study",
    }

    quality_rows = [
        {"issue": "Women's cohort definition", "impact": "Trainerize records 34 non-test profiles with sex missing, 7 as male and 3 as other; these 44 profiles contain 1,118 tracked programmed workouts", "treatment": "The owner reports that non-female labels reflect onboarding errors, but the audit does not infer or overwrite sex. Outcomes remain restricted to 529 profiles explicitly recorded as female until each exception is business-verified; the 26,304-workout all-account total is labelled operational only"},
        {"issue": "Incomplete former-member detail", "impact": "Workout summaries exist for more former members than detailed set-level results", "treatment": "Report coverage by status; do not generalise detailed outcomes to all former members"},
        {"issue": "Survivor and engagement bias", "impact": "Members who train and log more are more likely to appear at later horizons", "treatment": "Use paired samples and show n for every horizon and movement"},
        {"issue": "Non-standardised testing", "impact": "Most outcomes are best training performances, not scheduled reassessments", "treatment": "Label all results as training-log proxies; V2 must standardise tests"},
        {"issue": "Estimated 1RM", "impact": "Loaded lifts use Epley estimates from 1-12 rep sets", "treatment": "Retain raw weight and reps; do not present estimates as measured 1RM"},
        {"issue": "Farmer Walk load convention", "impact": "Historical entries may mean total load or per-hand load", "treatment": "Include only explicit 60-second targets and treat load interpretation as provisional"},
        {"issue": "Bodyweight timing", "impact": "Relative standards require bodyweight within 45 days", "treatment": "Leave ratios and standards unavailable when no nearby bodyweight exists"},
        {"issue": "Exercise variants", "impact": "Different exercise names and equipment are not normally interchangeable", "treatment": "Keep exact names separate except for the coach-confirmed Nexus, Barbell Front Squat and Barbell Back Squat aliases"},
        {"issue": "Squat recording aliases", "impact": "The same Nexus squat was unintentionally recorded under three Trainerize exercise names", "treatment": "Combine all three names into one canonical Nexus Point Squat outcome and one progression stage"},
        {"issue": "Movement-family stages", "impact": "Goblet and Nexus squat loads are not directly comparable", "treatment": "Measure Goblet-to-Nexus stage transitions separately from canonical Nexus load improvement"},
        {"issue": "Zero-load split squats", "impact": "Bodyweight-only entries may be stored as 0kg", "treatment": "Retain 0kg rows but require positive baseline for percentage-change calculations"},
        {"issue": "Public result use", "impact": "A statistical candidate is not automatically a publishable story", "treatment": "Coach validation plus explicit member consent required"},
    ]

    write_csv(PUBLIC_OUT / "cohort_coverage.csv", coverage_rows)
    write_csv(PUBLIC_OUT / "movement_outcomes.csv", movement_rows)
    write_csv(PUBLIC_OUT / "standards_transitions.csv", transition_rows)
    write_csv(PUBLIC_OUT / "remarkable_candidates.csv", remarkable)
    write_csv(PUBLIC_OUT / "exercise_dictionary.csv", exercise_rows)
    write_csv(PUBLIC_OUT / "data_quality.csv", quality_rows)
    write_csv(PUBLIC_OUT / "deidentified_trajectories.csv", deidentified_trajectories)
    write_csv(PUBLIC_OUT / "movement_family_map.csv", movement_family_map_rows)
    write_csv(PUBLIC_OUT / "movement_family_exposure.csv", movement_family_exposure_rows)
    write_csv(PUBLIC_OUT / "squat_progression_outcomes.csv", squat_progression_outcomes)
    write_csv(PUBLIC_OUT / "deidentified_squat_progressions.csv", squat_progression_rows)
    write_csv(PUBLIC_OUT / "deidentified_squat_lifetime_progressions.csv", squat_lifetime_progression_rows)
    write_csv(PUBLIC_OUT / "marketing_evidence.csv", marketing_evidence_rows)
    write_csv(PUBLIC_OUT / "marketing_workout_milestones.csv", marketing_milestone_rows)
    write_csv(PRIVATE_OUT / "identified_member_trajectories.csv", private_trajectories)
    write_csv(PRIVATE_OUT / "identified_squat_progressions.csv", private_squat_progression_rows)
    write_csv(PRIVATE_OUT / "identified_squat_lifetime_progressions.csv", private_squat_lifetime_progression_rows)
    write_csv(
        PRIVATE_OUT / "account_state_changes.csv",
        [dict(row) for row in connection.execute("SELECT * FROM account_state_changes ORDER BY id")],
    )
    (PUBLIC_OUT / "audit_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    (PUBLIC_OUT / "audit_tables.json").write_text(
        json.dumps(
            {
                "summary": summary,
                "coverage": coverage_rows,
                "movement_outcomes": movement_rows,
                "standards_transitions": transition_rows,
                "remarkable_candidates": remarkable,
                "data_quality": quality_rows,
                "exercise_dictionary": exercise_rows,
                "trajectories": deidentified_trajectories,
                "movement_family_map": movement_family_map_rows,
                "movement_family_exposure": movement_family_exposure_rows,
                "squat_progression_outcomes": squat_progression_outcomes,
                "squat_progressions": squat_progression_rows,
                "squat_lifetime_progressions": squat_lifetime_progression_rows,
                "marketing_evidence": marketing_evidence_rows,
                "marketing_milestones": marketing_milestone_rows,
            },
            separators=(",", ":"),
        )
        + "\n"
    )
    (PRIVATE_OUT / "private_tables.json").write_text(
        json.dumps(
            {
                "summary": summary,
                "identified_trajectories": private_trajectories,
                "identified_squat_progressions": private_squat_progression_rows,
                "identified_squat_lifetime_progressions": private_squat_lifetime_progression_rows,
                "account_state_changes": [
                    dict(row)
                    for row in connection.execute(
                        "SELECT * FROM account_state_changes ORDER BY id"
                    )
                ],
            },
            separators=(",", ":"),
        )
        + "\n"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
