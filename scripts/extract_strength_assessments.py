#!/usr/bin/env python3
"""Extract Trainerize Strength Assessments into a private SQLite dataset."""

from __future__ import annotations

import argparse
import json
import sqlite3
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from trainerize_client import TrainerizeAPIError, TrainerizeClient


WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATABASE = (
    WORKSPACE_ROOT / "data" / "private" / "strength-assessments" / "strength_assessments.sqlite"
)
ASSESSMENT_WORKOUT_ID = 183960272
ASSESSMENT_TITLE_FRAGMENT = "strength assessment"
PROFILE_BATCH_SIZE = 40
DETAIL_BATCH_SIZE = 40


SCHEMA_SQL = """
PRAGMA busy_timeout = 30000;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS extraction_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    include_deactivated INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL,
    clients_discovered INTEGER NOT NULL DEFAULT 0,
    calendar_records_found INTEGER NOT NULL DEFAULT 0,
    assessments_stored INTEGER NOT NULL DEFAULT 0,
    errors_logged INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS clients (
    trainerize_user_id INTEGER PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    email TEXT,
    status TEXT,
    role TEXT,
    trainer_id INTEGER,
    trainer_name TEXT,
    location_id INTEGER,
    birth_date TEXT,
    sex TEXT,
    city TEXT,
    created_at TEXT,
    is_test_client INTEGER NOT NULL DEFAULT 0,
    last_weight REAL,
    last_weight_date TEXT,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS assessments (
    daily_workout_id INTEGER PRIMARY KEY,
    trainerize_user_id INTEGER NOT NULL,
    assessment_date TEXT NOT NULL,
    status TEXT,
    workout_id INTEGER,
    workout_name TEXT,
    schema_version TEXT NOT NULL,
    source TEXT,
    date_created TEXT,
    date_updated TEXT,
    extraction_run_id INTEGER NOT NULL,
    raw_json TEXT NOT NULL,
    FOREIGN KEY (trainerize_user_id) REFERENCES clients(trainerize_user_id),
    FOREIGN KEY (extraction_run_id) REFERENCES extraction_runs(id)
);

CREATE TABLE IF NOT EXISTS assessment_exercises (
    daily_workout_id INTEGER NOT NULL,
    exercise_position INTEGER NOT NULL,
    stat_position INTEGER NOT NULL,
    daily_exercise_id INTEGER,
    exercise_id INTEGER,
    exercise_name TEXT,
    record_type TEXT,
    side TEXT,
    target TEXT,
    note TEXT,
    set_id INTEGER,
    reps REAL,
    weight REAL,
    distance REAL,
    time_seconds REAL,
    calories REAL,
    level REAL,
    speed REAL,
    PRIMARY KEY (daily_workout_id, exercise_position, stat_position),
    FOREIGN KEY (daily_workout_id) REFERENCES assessments(daily_workout_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS assessment_body_weights (
    daily_workout_id INTEGER PRIMARY KEY,
    trainerize_user_id INTEGER NOT NULL,
    assessment_date TEXT NOT NULL,
    body_weight_kg REAL,
    measurement_date TEXT,
    day_offset INTEGER,
    timing_quality TEXT NOT NULL,
    selection_method TEXT NOT NULL,
    source TEXT NOT NULL,
    lookup_status TEXT NOT NULL,
    raw_json TEXT,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (daily_workout_id) REFERENCES assessments(daily_workout_id) ON DELETE CASCADE,
    FOREIGN KEY (trainerize_user_id) REFERENCES clients(trainerize_user_id)
);

CREATE TABLE IF NOT EXISTS extraction_errors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    extraction_run_id INTEGER NOT NULL,
    trainerize_user_id INTEGER,
    daily_workout_id INTEGER,
    stage TEXT NOT NULL,
    error_message TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (extraction_run_id) REFERENCES extraction_runs(id)
);

CREATE INDEX IF NOT EXISTS idx_assessments_user_date
ON assessments(trainerize_user_id, assessment_date);

CREATE INDEX IF NOT EXISTS idx_exercises_name
ON assessment_exercises(exercise_name);

DROP VIEW IF EXISTS baseline_component_results;
DROP VIEW IF EXISTS baseline_assessments;

CREATE VIEW baseline_assessments AS
SELECT a.*
FROM assessments a
JOIN clients c ON c.trainerize_user_id = a.trainerize_user_id
WHERE c.is_test_client = 0
  AND LOWER(c.sex) = 'female'
  AND a.daily_workout_id = (
      SELECT a2.daily_workout_id
      FROM assessments a2
      WHERE a2.trainerize_user_id = a.trainerize_user_id
        AND a2.status = 'tracked'
      ORDER BY a2.assessment_date, a2.daily_workout_id
      LIMIT 1
  );

CREATE VIEW baseline_component_results AS
SELECT
    b.trainerize_user_id,
    b.daily_workout_id,
    b.assessment_date,
    b.schema_version,
    w.body_weight_kg AS assessment_body_weight_kg,
    w.measurement_date AS body_weight_measurement_date,
    w.day_offset AS body_weight_day_offset,
    w.timing_quality AS body_weight_timing_quality,
    CAST(
        (julianday(b.assessment_date) - julianday(c.birth_date)) / 365.2425
        AS INTEGER
    ) AS age_at_assessment,
    CASE
        WHEN c.birth_date IS NULL THEN NULL
        WHEN CAST((julianday(b.assessment_date) - julianday(c.birth_date)) / 365.2425 AS INTEGER) < 30 THEN 'Under 30'
        WHEN CAST((julianday(b.assessment_date) - julianday(c.birth_date)) / 365.2425 AS INTEGER) < 40 THEN '30-39'
        WHEN CAST((julianday(b.assessment_date) - julianday(c.birth_date)) / 365.2425 AS INTEGER) < 50 THEN '40-49'
        WHEN CAST((julianday(b.assessment_date) - julianday(c.birth_date)) / 365.2425 AS INTEGER) < 60 THEN '50-59'
        ELSE '60+'
    END AS age_band,
    SUM(CASE
        WHEN e.exercise_name LIKE 'ATG Split Squat%'
         AND (e.reps IS NOT NULL OR e.weight IS NOT NULL)
        THEN 1 ELSE 0
    END) AS split_squat_recorded_variations,
    CASE WHEN SUM(CASE
        WHEN e.exercise_name LIKE 'ATG Split Squat%'
         AND (e.reps IS NOT NULL OR e.weight IS NOT NULL)
        THEN 1 ELSE 0
    END) = 1 THEN MAX(CASE
        WHEN e.exercise_name LIKE 'ATG Split Squat%'
         AND (e.reps IS NOT NULL OR e.weight IS NOT NULL)
        THEN e.exercise_name
    END) END AS split_squat_variation,
    CASE WHEN SUM(CASE
        WHEN e.exercise_name LIKE 'ATG Split Squat%'
         AND (e.reps IS NOT NULL OR e.weight IS NOT NULL)
        THEN 1 ELSE 0
    END) = 1 THEN MAX(CASE
        WHEN e.exercise_name LIKE 'ATG Split Squat%'
        THEN e.reps
    END) END AS split_squat_reps,
    MAX(CASE WHEN e.exercise_name = 'Farmer Walk' AND e.target LIKE 'Using 20%' THEN e.weight END) AS farmer_20_weight_kg,
    MAX(CASE WHEN e.exercise_name = 'Farmer Walk' AND e.target LIKE 'Using 20%' THEN e.reps END) AS farmer_20_recorded_result,
    MAX(CASE WHEN e.exercise_name = 'Farmer Walk' AND e.target LIKE 'Using 50%' THEN e.weight END) AS farmer_50_weight_kg,
    MAX(CASE WHEN e.exercise_name = 'Farmer Walk' AND e.target LIKE 'Using 50%' THEN e.reps END) AS farmer_50_recorded_result,
    MAX(CASE WHEN e.exercise_name = 'Farmer Walk' AND e.target LIKE 'Using 75%' THEN e.weight END) AS farmer_75_weight_kg,
    MAX(CASE WHEN e.exercise_name = 'Farmer Walk' AND e.target LIKE 'Using 75%' THEN e.reps END) AS farmer_75_recorded_result,
    MAX(CASE WHEN e.exercise_name = 'Farmer Walk' THEN e.weight END) AS farmer_best_load_kg,
    CASE
        WHEN w.body_weight_kg > 0
         AND MAX(CASE WHEN e.exercise_name = 'Farmer Walk' THEN e.weight END) IS NOT NULL
        THEN MAX(CASE WHEN e.exercise_name = 'Farmer Walk' THEN e.weight END) / w.body_weight_kg
    END AS farmer_load_bodyweight_ratio,
    MAX(CASE WHEN e.exercise_name = 'Half Plank (Knees)' THEN e.time_seconds END) AS half_plank_seconds,
    MAX(CASE WHEN e.exercise_name = 'Bear Plank' THEN e.time_seconds END) AS bear_plank_seconds,
    MAX(CASE WHEN e.exercise_name = 'High Plank' THEN e.time_seconds END) AS high_plank_seconds,
    MAX(CASE WHEN e.exercise_name = 'Side Plank' THEN e.time_seconds END) AS side_plank_max_seconds
FROM baseline_assessments b
JOIN clients c ON c.trainerize_user_id = b.trainerize_user_id
LEFT JOIN assessment_exercises e ON e.daily_workout_id = b.daily_workout_id
LEFT JOIN assessment_body_weights w ON w.daily_workout_id = b.daily_workout_id
GROUP BY b.trainerize_user_id, b.daily_workout_id, b.assessment_date,
         b.schema_version, c.birth_date, w.body_weight_kg, w.measurement_date,
         w.day_offset, w.timing_quality;
"""


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def chunks(values: list[Any], size: int) -> Iterable[list[Any]]:
    for start in range(0, len(values), size):
        yield values[start : start + size]


def calendar_windows(start_date: date, end_date: date) -> Iterable[tuple[date, date]]:
    """Yield calendar-year windows to keep Trainerize date requests bounded."""
    current = start_date
    while current <= end_date:
        window_end = min(date(current.year, 12, 31), end_date)
        yield current, window_end
        current = date(current.year + 1, 1, 1)


def is_strength_assessment(item: dict[str, Any]) -> bool:
    title = str(item.get("title") or "").lower()
    detail = item.get("detail") or {}
    workout_id = detail.get("workoutID") if isinstance(detail, dict) else None
    return ASSESSMENT_TITLE_FRAGMENT in title or workout_id == ASSESSMENT_WORKOUT_ID


def detect_schema_version(workout: dict[str, Any]) -> str:
    """Classify assessment structure without silently applying current standards."""
    exercises = workout.get("exercises") or []
    names = [str((exercise.get("def") or {}).get("name") or "").lower() for exercise in exercises]
    targets = [
        str((exercise.get("def") or {}).get("target") or "").lower()
        for exercise in exercises
    ]

    legacy_carry = any(
        "20% of" in target or "50% of" in target
        for name, target in zip(names, targets)
        if "farmer" in name
    )
    has_independent_sides = any(
        (exercise.get("def") or {}).get("side") in {"left", "right"}
        for exercise in exercises
    )
    has_current_advanced_core = any(
        "side plank" in name or "toes to bar" in name for name in names
    )

    if legacy_carry and not has_independent_sides:
        return "legacy_combined_v1"
    if has_independent_sides or has_current_advanced_core:
        return "current_independent_v2"
    return "unknown"


def connect_database(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.executescript(SCHEMA_SQL)
    return connection


def start_run(
    connection: sqlite3.Connection,
    start_date: date,
    end_date: date,
    include_deactivated: bool,
) -> int:
    cursor = connection.execute(
        """
        INSERT INTO extraction_runs (
            started_at, start_date, end_date, include_deactivated, status
        ) VALUES (?, ?, ?, ?, 'running')
        """,
        (utc_now(), start_date.isoformat(), end_date.isoformat(), int(include_deactivated)),
    )
    connection.commit()
    return int(cursor.lastrowid)


def log_error(
    connection: sqlite3.Connection,
    run_id: int,
    stage: str,
    error: Exception | str,
    *,
    user_id: int | None = None,
    workout_id: int | None = None,
) -> None:
    message = str(error)
    connection.execute(
        """
        INSERT INTO extraction_errors (
            extraction_run_id, trainerize_user_id, daily_workout_id,
            stage, error_message, created_at
        ) VALUES (?, ?, ?, ?, ?, ?)
        """,
        (run_id, user_id, workout_id, stage, message[:500], utc_now()),
    )


def fetch_clients(
    client: TrainerizeClient,
    *,
    include_deactivated: bool,
    limit: int | None,
) -> list[dict[str, Any]]:
    clients: list[dict[str, Any]] = []
    start = 0
    page_size = 100

    while True:
        page = client.get_active_clients(start=start, count=page_size)
        batch = page.get("users") or []
        clients.extend(batch)
        if not batch or len(clients) >= int(page.get("total") or 0):
            break
        start += len(batch)

    if include_deactivated:
        start = 0
        while True:
            page = client.get_client_list(
                view="deactivatedClient", start=start, count=page_size
            )
            batch = page.get("users") or []
            clients.extend(batch)
            if not batch or start + len(batch) >= int(page.get("total") or 0):
                break
            start += len(batch)

    deduplicated = {int(item["id"]): item for item in clients if item.get("id") is not None}
    result = list(deduplicated.values())
    if limit is not None:
        result = result[:limit]
    return result


def fetch_profiles(
    client: TrainerizeClient,
    users: list[dict[str, Any]],
    connection: sqlite3.Connection,
    run_id: int,
) -> dict[int, dict[str, Any]]:
    profiles: dict[int, dict[str, Any]] = {}
    user_ids = [int(user["id"]) for user in users if user.get("id") is not None]

    for batch in chunks(user_ids, PROFILE_BATCH_SIZE):
        try:
            response = client.post(
                "/user/getProfile", {"usersid": batch, "unitBodystats": "cm"}
            )
            for profile in response.get("usrProfile") or response.get("users") or []:
                if profile.get("id") is not None:
                    profiles[int(profile["id"])] = profile
        except TrainerizeAPIError as exc:
            for user_id in batch:
                log_error(connection, run_id, "profile", exc, user_id=user_id)
    return profiles


def upsert_clients(
    connection: sqlite3.Connection,
    users: list[dict[str, Any]],
    profiles: dict[int, dict[str, Any]],
) -> None:
    timestamp = utc_now()
    for user in users:
        user_id = int(user["id"])
        profile = profiles.get(user_id, {})
        connection.execute(
            """
            INSERT INTO clients (
                trainerize_user_id, first_name, last_name, email, status, role,
                trainer_id, trainer_name, location_id, birth_date, sex, city,
                created_at, is_test_client, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(trainerize_user_id) DO UPDATE SET
                first_name=excluded.first_name,
                last_name=excluded.last_name,
                email=excluded.email,
                status=excluded.status,
                role=excluded.role,
                trainer_id=excluded.trainer_id,
                trainer_name=excluded.trainer_name,
                location_id=excluded.location_id,
                birth_date=excluded.birth_date,
                sex=excluded.sex,
                city=excluded.city,
                created_at=excluded.created_at,
                is_test_client=excluded.is_test_client,
                updated_at=excluded.updated_at
            """,
            (
                user_id,
                profile.get("firstName") or user.get("firstName"),
                profile.get("lastName") or user.get("lastName"),
                profile.get("email") or user.get("email"),
                profile.get("status") or user.get("status"),
                profile.get("role") or user.get("role"),
                profile.get("trainerID") or user.get("trainerID"),
                profile.get("trainerName"),
                profile.get("locationID"),
                profile.get("birthDate"),
                profile.get("sex"),
                profile.get("city"),
                profile.get("created"),
                int(bool(profile.get("isTestClient"))),
                timestamp,
            ),
        )


def fetch_assessment_calendar_ids(
    client: TrainerizeClient,
    users: list[dict[str, Any]],
    start_date: date,
    end_date: date,
    connection: sqlite3.Connection,
    run_id: int,
) -> dict[int, int]:
    assessment_ids: dict[int, int] = {}

    for position, user in enumerate(users, start=1):
        user_id = int(user["id"])
        for window_start, window_end in calendar_windows(start_date, end_date):
            try:
                response = client.post(
                    "/calendar/getList",
                    {
                        "userID": user_id,
                        "startDate": window_start.isoformat(),
                        "endDate": window_end.isoformat(),
                        "unitDistance": "km",
                        "unitWeight": "kg",
                    },
                )
            except TrainerizeAPIError as exc:
                log_error(connection, run_id, "calendar", exc, user_id=user_id)
                continue

            for calendar_day in response.get("calendar") or []:
                for item in calendar_day.get("items") or []:
                    if is_strength_assessment(item) and item.get("id") is not None:
                        assessment_ids[int(item["id"])] = user_id

        if position % 25 == 0 or position == len(users):
            print(
                f"Calendar scan: {position}/{len(users)} clients; "
                f"{len(assessment_ids)} assessment records found"
            )
            connection.commit()
    return assessment_ids


def fetch_assessment_details(
    client: TrainerizeClient,
    assessment_ids: dict[int, int],
    connection: sqlite3.Connection,
    run_id: int,
) -> list[dict[str, Any]]:
    details: list[dict[str, Any]] = []
    workout_ids = list(assessment_ids)

    for batch in chunks(workout_ids, DETAIL_BATCH_SIZE):
        try:
            response = client.post("/dailyWorkout/get", {"ids": batch})
            details.extend(response.get("dailyWorkouts") or [])
        except TrainerizeAPIError:
            # A deactivated client can make a whole batch fail. Retry individually
            # so active-client records are not discarded.
            for workout_id in batch:
                try:
                    response = client.post("/dailyWorkout/get", {"ids": [workout_id]})
                    details.extend(response.get("dailyWorkouts") or [])
                except TrainerizeAPIError as exc:
                    log_error(
                        connection,
                        run_id,
                        "daily_workout",
                        exc,
                        user_id=assessment_ids.get(workout_id),
                        workout_id=workout_id,
                    )
    return details


def upsert_assessment(
    connection: sqlite3.Connection,
    workout: dict[str, Any],
    run_id: int,
    expected_user_id: int | None = None,
) -> None:
    daily_workout_id = int(workout["id"])
    # The calendar owner is authoritative. Trainerize occasionally returns a
    # different workout-level userID, which otherwise violates client ownership
    # and can abort an otherwise valid extraction batch.
    user_id = expected_user_id or int(workout["userID"])
    schema_version = detect_schema_version(workout)

    connection.execute(
        """
        INSERT INTO assessments (
            daily_workout_id, trainerize_user_id, assessment_date, status,
            workout_id, workout_name, schema_version, source, date_created,
            date_updated, extraction_run_id, raw_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(daily_workout_id) DO UPDATE SET
            trainerize_user_id=excluded.trainerize_user_id,
            assessment_date=excluded.assessment_date,
            status=excluded.status,
            workout_id=excluded.workout_id,
            workout_name=excluded.workout_name,
            schema_version=excluded.schema_version,
            source=excluded.source,
            date_created=excluded.date_created,
            date_updated=excluded.date_updated,
            extraction_run_id=excluded.extraction_run_id,
            raw_json=excluded.raw_json
        """,
        (
            daily_workout_id,
            user_id,
            workout.get("date"),
            workout.get("status"),
            workout.get("workoutID"),
            workout.get("name"),
            schema_version,
            workout.get("from"),
            workout.get("dateCreated"),
            workout.get("dateUpdated"),
            run_id,
            json.dumps(workout, separators=(",", ":"), ensure_ascii=False),
        ),
    )
    connection.execute(
        "DELETE FROM assessment_exercises WHERE daily_workout_id = ?",
        (daily_workout_id,),
    )

    for exercise_position, exercise in enumerate(workout.get("exercises") or []):
        definition = exercise.get("def") or {}
        stats = exercise.get("stats") or [{}]
        for stat_position, stat in enumerate(stats):
            connection.execute(
                """
                INSERT INTO assessment_exercises (
                    daily_workout_id, exercise_position, stat_position,
                    daily_exercise_id, exercise_id, exercise_name, record_type,
                    side, target, note, set_id, reps, weight, distance,
                    time_seconds, calories, level, speed
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    daily_workout_id,
                    exercise_position,
                    stat_position,
                    exercise.get("dailyExerciseID"),
                    definition.get("id"),
                    definition.get("name"),
                    definition.get("recordType"),
                    definition.get("side"),
                    definition.get("target"),
                    exercise.get("note"),
                    stat.get("setID"),
                    stat.get("reps"),
                    stat.get("weight"),
                    stat.get("distance"),
                    stat.get("time"),
                    stat.get("calories"),
                    stat.get("level"),
                    stat.get("speed"),
                ),
            )


def enrich_assessment_clients(
    client: TrainerizeClient,
    connection: sqlite3.Connection,
    run_id: int,
    user_ids: set[int],
) -> None:
    for user_id in sorted(user_ids):
        try:
            summary = client.post(
                "/user/getClientSummary", {"userID": user_id, "unitWeight": "kg"}
            )
            connection.execute(
                """
                UPDATE clients
                SET last_weight = ?, last_weight_date = ?, updated_at = ?
                WHERE trainerize_user_id = ?
                """,
                (
                    summary.get("lastWeight"),
                    summary.get("lastWeightDate"),
                    utc_now(),
                    user_id,
                ),
            )
        except TrainerizeAPIError as exc:
            log_error(connection, run_id, "client_summary", exc, user_id=user_id)


def body_weight_timing_quality(day_offset: int | None) -> str:
    if day_offset is None:
        return "Not available"
    absolute_offset = abs(day_offset)
    if absolute_offset == 0:
        return "Same day"
    if absolute_offset <= 7:
        return "Within 7 days"
    if absolute_offset <= 30:
        return "Within 30 days"
    return "Not suitable"


def extract_body_weight(response: dict[str, Any]) -> tuple[float | None, str | None]:
    measures = response.get("bodyMeasures")
    if isinstance(measures, list):
        measures = measures[0] if measures else None
    if not isinstance(measures, dict):
        return None, None
    value = measures.get("bodyWeight")
    measurement_date = measures.get("date")
    if value is None:
        return None, measurement_date
    return float(value), measurement_date


def upsert_assessment_body_weight(
    connection: sqlite3.Connection,
    *,
    daily_workout_id: int,
    trainerize_user_id: int,
    assessment_date: str,
    body_weight_kg: float | None,
    measurement_date: str | None,
    selection_method: str,
    lookup_status: str,
    raw_json: str | None = None,
) -> None:
    day_offset = None
    if measurement_date:
        day_offset = (
            date.fromisoformat(measurement_date) - date.fromisoformat(assessment_date)
        ).days
    connection.execute(
        """
        INSERT INTO assessment_body_weights (
            daily_workout_id, trainerize_user_id, assessment_date,
            body_weight_kg, measurement_date, day_offset, timing_quality,
            selection_method, source, lookup_status, raw_json, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'trainerize', ?, ?, ?)
        ON CONFLICT(daily_workout_id) DO UPDATE SET
            trainerize_user_id=excluded.trainerize_user_id,
            assessment_date=excluded.assessment_date,
            body_weight_kg=excluded.body_weight_kg,
            measurement_date=excluded.measurement_date,
            day_offset=excluded.day_offset,
            timing_quality=excluded.timing_quality,
            selection_method=excluded.selection_method,
            lookup_status=excluded.lookup_status,
            raw_json=excluded.raw_json,
            updated_at=excluded.updated_at
        """,
        (
            daily_workout_id,
            trainerize_user_id,
            assessment_date,
            body_weight_kg,
            measurement_date,
            day_offset,
            body_weight_timing_quality(day_offset),
            selection_method,
            lookup_status,
            raw_json,
            utc_now(),
        ),
    )


def enrich_assessment_body_weights(
    client: TrainerizeClient,
    connection: sqlite3.Connection,
) -> dict[str, int]:
    """Select an assessment-date weight, preserving timing and source quality."""
    counts: Counter[str] = Counter()
    rows = connection.execute(
        """
        SELECT a.daily_workout_id, a.trainerize_user_id, a.assessment_date,
               c.last_weight, c.last_weight_date
        FROM assessments a
        JOIN clients c ON c.trainerize_user_id = a.trainerize_user_id
        WHERE a.status = 'tracked'
        ORDER BY a.assessment_date, a.daily_workout_id
        """
    ).fetchall()

    for row in rows:
        assessment_date = row["assessment_date"]
        try:
            response = client.post(
                "/bodystats/get",
                {
                    "userID": row["trainerize_user_id"],
                    "date": assessment_date,
                    "unitBodystats": "cm",
                    "unitWeight": "kg",
                },
            )
            weight, measurement_date = extract_body_weight(response)
            if weight is not None:
                upsert_assessment_body_weight(
                    connection,
                    daily_workout_id=row["daily_workout_id"],
                    trainerize_user_id=row["trainerize_user_id"],
                    assessment_date=assessment_date,
                    body_weight_kg=weight,
                    measurement_date=measurement_date or assessment_date,
                    selection_method="exact_body_stat",
                    lookup_status="exact",
                    raw_json=json.dumps(response, separators=(",", ":"), ensure_ascii=False),
                )
                counts["exact"] += 1
                continue
        except TrainerizeAPIError as exc:
            counts[f"http_{exc.status_code or 'unknown'}"] += 1

        fallback_weight = row["last_weight"]
        fallback_date = row["last_weight_date"]
        fallback_offset = None
        if fallback_date:
            fallback_offset = (
                date.fromisoformat(fallback_date) - date.fromisoformat(assessment_date)
            ).days
        usable_fallback = (
            fallback_weight is not None
            and fallback_offset is not None
            and abs(fallback_offset) <= 30
        )
        upsert_assessment_body_weight(
            connection,
            daily_workout_id=row["daily_workout_id"],
            trainerize_user_id=row["trainerize_user_id"],
            assessment_date=assessment_date,
            body_weight_kg=float(fallback_weight) if usable_fallback else None,
            measurement_date=fallback_date if usable_fallback else None,
            selection_method="client_summary_fallback" if usable_fallback else "none",
            lookup_status="fallback" if usable_fallback else "unavailable",
        )
        counts["fallback" if usable_fallback else "unavailable"] += 1

    connection.commit()
    return dict(counts)


def summarize(connection: sqlite3.Connection, run_id: int) -> dict[str, Any]:
    schema_counts = {
        row["schema_version"]: row["count"]
        for row in connection.execute(
            """
            SELECT schema_version, COUNT(*) AS count
            FROM assessments
            GROUP BY schema_version
            ORDER BY schema_version
            """
        )
    }
    status_counts = {
        row["status"] or "unknown": row["count"]
        for row in connection.execute(
            """
            SELECT status, COUNT(*) AS count
            FROM assessments
            GROUP BY status
            ORDER BY status
            """
        )
    }
    row = connection.execute(
        """
        SELECT
            COUNT(*) AS baseline_women,
            MIN(assessment_date) AS earliest,
            MAX(assessment_date) AS latest
        FROM baseline_assessments
        """
    ).fetchone()
    errors = connection.execute(
        "SELECT COUNT(*) FROM extraction_errors WHERE extraction_run_id = ?",
        (run_id,),
    ).fetchone()[0]
    return {
        "baseline_women": row["baseline_women"],
        "earliest_baseline": row["earliest"],
        "latest_baseline": row["latest"],
        "assessment_statuses": status_counts,
        "schema_versions": schema_counts,
        "errors_this_run": errors,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract Trainerize Strength Assessments into private SQLite storage."
    )
    parser.add_argument("--start-date", type=date.fromisoformat, default=date(2026, 1, 1))
    parser.add_argument("--end-date", type=date.fromisoformat, default=date.today())
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE)
    parser.add_argument(
        "--include-deactivated",
        action="store_true",
        help="Scan deactivated clients. Their calendar is readable, but workout details may return 403.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit client count for a controlled validation run.",
    )
    parser.add_argument(
        "--body-weight-only",
        action="store_true",
        help="Backfill assessment-date body weights for assessments already stored.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.end_date < args.start_date:
        raise SystemExit("--end-date must be on or after --start-date")

    client = TrainerizeClient()
    connection = connect_database(args.database)
    run_id = start_run(
        connection, args.start_date, args.end_date, args.include_deactivated
    )

    try:
        if args.body_weight_only:
            counts = enrich_assessment_body_weights(client, connection)
            connection.execute(
                """
                UPDATE extraction_runs
                SET completed_at = ?, status = 'complete'
                WHERE id = ?
                """,
                (utc_now(), run_id),
            )
            connection.commit()
            print("Body-weight enrichment complete")
            print(json.dumps(counts, indent=2, sort_keys=True))
            print(f"Private database: {args.database}")
            return 0

        users = fetch_clients(
            client,
            include_deactivated=args.include_deactivated,
            limit=args.limit,
        )
        print(f"Clients discovered: {len(users)}")

        profiles = fetch_profiles(client, users, connection, run_id)
        upsert_clients(connection, users, profiles)
        connection.commit()

        assessment_ids = fetch_assessment_calendar_ids(
            client,
            users,
            args.start_date,
            args.end_date,
            connection,
            run_id,
        )
        details = fetch_assessment_details(
            client, assessment_ids, connection, run_id
        )
        for workout in details:
            daily_workout_id = int(workout["id"])
            upsert_assessment(
                connection,
                workout,
                run_id,
                expected_user_id=assessment_ids.get(daily_workout_id),
            )

        assessed_user_ids = {
            assessment_ids.get(int(workout["id"])) or int(workout["userID"])
            for workout in details
            if workout.get("id") is not None and workout.get("userID") is not None
        }
        enrich_assessment_clients(
            client, connection, run_id, assessed_user_ids
        )
        body_weight_counts = enrich_assessment_body_weights(client, connection)
        connection.commit()

        summary = summarize(connection, run_id)
        connection.execute(
            """
            UPDATE extraction_runs
            SET completed_at = ?, status = 'complete', clients_discovered = ?,
                calendar_records_found = ?, assessments_stored = ?, errors_logged = ?
            WHERE id = ?
            """,
            (
                utc_now(),
                len(users),
                len(assessment_ids),
                len(details),
                summary["errors_this_run"],
                run_id,
            ),
        )
        connection.commit()

        print("Extraction complete")
        print("Body-weight enrichment")
        print(json.dumps(body_weight_counts, indent=2, sort_keys=True))
        print(json.dumps(summary, indent=2, sort_keys=True))
        print(f"Private database: {args.database}")
        return 0
    except Exception:
        connection.execute(
            "UPDATE extraction_runs SET completed_at = ?, status = 'failed' WHERE id = ?",
            (utc_now(), run_id),
        )
        connection.commit()
        raise
    finally:
        connection.close()


if __name__ == "__main__":
    raise SystemExit(main())
