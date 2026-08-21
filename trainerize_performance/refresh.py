from __future__ import annotations

import json
import sqlite3
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any

from scripts.trainerize_client import TrainerizeClient


DETAIL_BATCH_SIZE = 20
ASSESSMENT_WORKOUT_ID = 183960272
ASSESSMENT_TITLE_FRAGMENT = "strength assessment"

ASSESSMENT_EVIDENCE_SCHEMA = """
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
    raw_json TEXT NOT NULL
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
    PRIMARY KEY (daily_workout_id, exercise_position, stat_position)
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
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_assessments_user_date
ON assessments(trainerize_user_id, assessment_date);
CREATE INDEX IF NOT EXISTS idx_assessment_exercises_name
ON assessment_exercises(exercise_name);
"""
MOVEMENT_NAMES = {
    "Barbell Bench Press",
    "Barbell Deadlift",
    "Nexus Point Squat",
    "Barbell Front Squat",
    "Barbell Back Squat",
}


def _now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def _number(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _chunks(values: list[int], size: int):
    for start in range(0, len(values), size):
        yield values[start : start + size]


def _active_clients(client: TrainerizeClient) -> list[dict[str, Any]]:
    rows = []
    start = 0
    while True:
        response = client.get_active_clients(start=start, count=100)
        batch = response.get("users") or []
        rows.extend(batch)
        start += len(batch)
        total = int(response.get("total") or 0)
        if not batch or start >= total:
            break
    unique_ids = {
        int(row["id"])
        for row in rows
        if row.get("id") is not None
    }
    if len(unique_ids) != len(rows):
        raise RuntimeError("Trainerize active roster contains duplicate IDs")
    return rows


def _recent_workout_owners(
    client: TrainerizeClient,
    users: list[dict[str, Any]],
    *,
    start_date: date,
    end_date: date,
) -> dict[int, int]:
    owners, _ = _recent_calendar(
        client,
        users,
        start_date=start_date,
        end_date=end_date,
    )
    return owners


def _recent_calendar(
    client: TrainerizeClient,
    users: list[dict[str, Any]],
    *,
    start_date: date,
    end_date: date,
) -> tuple[dict[int, int], list[tuple[int, str, dict[str, Any]]]]:
    owners: dict[int, int] = {}
    calendar_items: list[tuple[int, str, dict[str, Any]]] = []
    for user in users:
        user_id = int(user["id"])
        response = client.post(
            "/calendar/getList",
            {
                "userID": user_id,
                "startDate": start_date.isoformat(),
                "endDate": end_date.isoformat(),
                "unitDistance": "km",
                "unitWeight": "kg",
            },
        )
        for day in response.get("calendar") or []:
            calendar_date = str(day.get("date") or "")[:10]
            for item in day.get("items") or []:
                if calendar_date and item.get("id") is not None:
                    calendar_items.append((user_id, calendar_date, item))
                if (
                    item.get("type") == "workoutRegular"
                    and item.get("status") == "tracked"
                    and item.get("id") is not None
                ):
                    workout_id = int(item["id"])
                    previous = owners.get(workout_id)
                    if previous is not None and previous != user_id:
                        raise RuntimeError(
                            "Trainerize workout has conflicting owners"
                        )
                    owners[workout_id] = user_id
    return owners, calendar_items


def _upsert_calendar_items(
    database: Path,
    rows: list[tuple[int, str, dict[str, Any]]],
) -> int:
    connection = sqlite3.connect(database)
    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS calendar_items (
                trainerize_user_id INTEGER NOT NULL,
                calendar_date TEXT NOT NULL,
                item_id INTEGER NOT NULL,
                item_type TEXT,
                status TEXT,
                title TEXT,
                workout_id INTEGER,
                exercise_id INTEGER,
                trainer_id INTEGER,
                trainer_name TEXT,
                location_id INTEGER,
                event_category TEXT,
                duration_seconds REAL,
                rpe REAL,
                body_weight_kg REAL,
                body_fat_percent REAL,
                bmi REAL,
                resting_heart_rate REAL,
                blood_pressure_systolic REAL,
                blood_pressure_diastolic REAL,
                raw_json TEXT NOT NULL,
                PRIMARY KEY (
                    trainerize_user_id,
                    calendar_date,
                    item_id,
                    item_type
                )
            )
            """
        )
        for user_id, calendar_date, item in rows:
            detail = item.get("detail") or {}
            if not isinstance(detail, dict):
                detail = {}
            connection.execute(
                """
                INSERT INTO calendar_items (
                    trainerize_user_id, calendar_date, item_id, item_type,
                    status, title, workout_id, exercise_id, trainer_id,
                    trainer_name, location_id, event_category,
                    duration_seconds, rpe, body_weight_kg, body_fat_percent,
                    bmi, resting_heart_rate, blood_pressure_systolic,
                    blood_pressure_diastolic, raw_json
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?
                )
                ON CONFLICT(
                    trainerize_user_id, calendar_date, item_id, item_type
                ) DO UPDATE SET
                    status=excluded.status,
                    title=excluded.title,
                    workout_id=excluded.workout_id,
                    exercise_id=excluded.exercise_id,
                    trainer_id=excluded.trainer_id,
                    trainer_name=excluded.trainer_name,
                    location_id=excluded.location_id,
                    event_category=excluded.event_category,
                    duration_seconds=excluded.duration_seconds,
                    rpe=excluded.rpe,
                    body_weight_kg=excluded.body_weight_kg,
                    body_fat_percent=excluded.body_fat_percent,
                    bmi=excluded.bmi,
                    resting_heart_rate=excluded.resting_heart_rate,
                    blood_pressure_systolic=excluded.blood_pressure_systolic,
                    blood_pressure_diastolic=excluded.blood_pressure_diastolic,
                    raw_json=excluded.raw_json
                """,
                (
                    user_id,
                    calendar_date,
                    int(item.get("id") or 0),
                    str(item.get("type") or "unknown"),
                    item.get("status"),
                    item.get("title"),
                    detail.get("workoutID"),
                    detail.get("exerciseID"),
                    detail.get("trainerID"),
                    detail.get("trainerName"),
                    detail.get("locationID"),
                    detail.get("eventCategory"),
                    _number(detail.get("time")),
                    _number(detail.get("rpe")),
                    _number(detail.get("weight")),
                    _number(
                        detail.get("fat")
                        or detail.get("bodyFatPercent")
                    ),
                    _number(detail.get("bodyMassIndex")),
                    _number(detail.get("restingHeartRate")),
                    _number(detail.get("bloodPressureSystolic")),
                    _number(detail.get("bloodPressureDiastolic")),
                    json.dumps(
                        item,
                        separators=(",", ":"),
                        ensure_ascii=False,
                    ),
                ),
            )
        connection.commit()
        return len(rows)
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def _workout_details(
    client: TrainerizeClient,
    owners: dict[int, int],
) -> list[dict[str, Any]]:
    workout_ids = sorted(owners)
    results = []
    for batch in _chunks(workout_ids, DETAIL_BATCH_SIZE):
        response = client.post("/dailyWorkout/get", {"ids": batch})
        returned = response.get("dailyWorkouts") or []
        returned_ids = {
            int(workout["id"])
            for workout in returned
            if workout.get("id") is not None
        }
        missing = set(batch) - returned_ids
        if missing:
            raise RuntimeError(
                f"Trainerize omitted {len(missing)} requested workouts"
            )
        results.extend(returned)
    return results


def _replace_roster(
    database: Path,
    users: list[dict[str, Any]],
    *,
    observed_at: str,
) -> str:
    run_id = (
        "trainerize-performance-"
        + observed_at.replace(":", "").replace("-", "")
    )
    connection = sqlite3.connect(database)
    try:
        connection.execute("BEGIN")
        connection.execute("DELETE FROM trainerize_clients")
        connection.execute("DELETE FROM runs")
        connection.execute(
            "INSERT INTO runs VALUES (?, ?, ?, 'complete')",
            (run_id, observed_at, observed_at),
        )
        connection.executemany(
            """
            INSERT INTO trainerize_clients VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active'
            )
            """,
            [
                (
                    run_id,
                    int(user["id"]),
                    user.get("email"),
                    user.get("firstName"),
                    user.get("lastName"),
                    user.get("type") or user.get("clientType"),
                    user.get("trainerID"),
                    user.get("latestSignedIn"),
                    json.dumps(user, separators=(",", ":")),
                )
                for user in users
            ],
        )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
    return run_id


def _validate_roster_change(database: Path, current: int) -> None:
    connection = sqlite3.connect(database)
    previous = int(
        connection.execute(
            "SELECT COUNT(*) FROM trainerize_clients"
        ).fetchone()[0]
    )
    connection.close()
    if previous and not (previous * 0.75 <= current <= previous * 1.25):
        raise RuntimeError(
            "Trainerize active roster changed by more than 25%"
        )


def _upsert_workouts(
    database: Path,
    owners: dict[int, int],
    workouts: list[dict[str, Any]],
    *,
    observed_at: str,
) -> None:
    connection = sqlite3.connect(database)
    try:
        connection.execute("BEGIN")
        for workout in workouts:
            workout_id = int(workout["id"])
            workout_date = str(workout.get("date") or "")[:10] or None
            connection.execute(
                """
                INSERT INTO daily_workouts VALUES (?, ?, ?, ?)
                ON CONFLICT(daily_workout_id) DO UPDATE SET
                    trainerize_user_id=excluded.trainerize_user_id,
                    workout_date=excluded.workout_date,
                    status=excluded.status
                """,
                (
                    workout_id,
                    owners[workout_id],
                    workout_date,
                    workout.get("status"),
                ),
            )
            connection.execute(
                "DELETE FROM exercise_results WHERE daily_workout_id=?",
                (workout_id,),
            )
            for exercise_position, exercise in enumerate(
                workout.get("exercises") or []
            ):
                definition = exercise.get("def") or {}
                if definition.get("name") not in MOVEMENT_NAMES:
                    continue
                for stat_position, stat in enumerate(
                    exercise.get("stats") or [{}]
                ):
                    connection.execute(
                        """
                        INSERT INTO exercise_results VALUES (
                            ?, ?, ?, ?, ?, ?, ?, ?
                        )
                        """,
                        (
                            workout_id,
                            owners[workout_id],
                            workout_date,
                            exercise_position,
                            stat_position,
                            definition.get("name"),
                            _number(stat.get("weight")),
                            _number(stat.get("reps")),
                        ),
                    )
        connection.execute(
            "INSERT INTO source_observations VALUES (?, 'complete')",
            (observed_at,),
        )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def _is_strength_assessment(
    workout: dict[str, Any],
    calendar_item: dict[str, Any] | None = None,
) -> bool:
    item = calendar_item or {}
    detail = item.get("detail") or {}
    title = " ".join(
        str(
            item.get("title")
            or workout.get("name")
            or ""
        ).lower().split()
    )
    workout_id = (
        detail.get("workoutID")
        if isinstance(detail, dict)
        else None
    ) or workout.get("workoutID")
    return (
        ASSESSMENT_TITLE_FRAGMENT in title
        or workout_id == ASSESSMENT_WORKOUT_ID
    )


def _assessment_schema_version(workout: dict[str, Any]) -> str:
    definitions = [
        exercise.get("def") or {}
        for exercise in workout.get("exercises") or []
    ]
    independent = any(
        str(definition.get("side") or "").lower()
        in {"left", "right"}
        for definition in definitions
    )
    advanced_core = any(
        (
            "side plank" in str(definition.get("name") or "").lower()
            or "toes to bar"
            in str(definition.get("name") or "").lower()
        )
        for definition in definitions
    )
    return (
        "current_independent_v2"
        if independent or advanced_core
        else "unknown"
    )


def _upsert_recent_assessments(
    database: Path | None,
    owners: dict[int, int],
    workouts: list[dict[str, Any]],
    calendar_items: list[tuple[int, str, dict[str, Any]]],
    *,
    observed_at: str,
) -> dict[str, Any]:
    if database is None or not database.exists():
        return {
            "status": "unavailable",
            "assessments_updated": 0,
            "reason": "assessment database is unavailable",
        }
    connection = sqlite3.connect(database)
    tables = {
        str(row[0])
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
    }
    if "assessments" in tables:
        assessment_columns = {
            str(row[1])
            for row in connection.execute("PRAGMA table_info(assessments)")
        }
        if "daily_workout_id" not in assessment_columns:
            connection.execute(
                "ALTER TABLE assessments RENAME TO legacy_assessment_dates"
            )
            connection.executescript(ASSESSMENT_EVIDENCE_SCHEMA)
            connection.execute(
                """
                INSERT INTO assessments (
                    daily_workout_id, trainerize_user_id, assessment_date,
                    status, schema_version, extraction_run_id, raw_json
                )
                SELECT -rowid, trainerize_user_id, assessment_date,
                       'historical_date_only', 'legacy_date_only', 0, '{}'
                FROM legacy_assessment_dates
                """
            )
            connection.commit()
        else:
            connection.executescript(ASSESSMENT_EVIDENCE_SCHEMA)
    else:
        connection.executescript(ASSESSMENT_EVIDENCE_SCHEMA)
    tables = {
        str(row[0])
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
    }
    calendar_by_id = {
        int(item["id"]): (user_id, calendar_date, item)
        for user_id, calendar_date, item in calendar_items
        if item.get("id") is not None
    }
    assessment_workouts = [
        workout
        for workout in workouts
        if _is_strength_assessment(
            workout,
            (
                calendar_by_id.get(int(workout["id"]), (None, None, None))[2]
                if int(workout["id"]) in calendar_by_id
                else None
            ),
        )
    ]
    if not assessment_workouts:
        connection.close()
        return {
            "status": "complete",
            "assessments_updated": 0,
            "reason": None,
        }
    extraction_run_id = 0
    if "extraction_runs" in tables:
        extraction_run_id = int(
            connection.execute(
                "SELECT COALESCE(MAX(id), 0) FROM extraction_runs"
            ).fetchone()[0]
        )
    body_stats: dict[int, list[tuple[date, float]]] = {}
    for user_id, calendar_date, item in calendar_items:
        detail = item.get("detail") or {}
        if (
            str(item.get("type") or "") != "bodyStat"
            or not isinstance(detail, dict)
        ):
            continue
        weight = _number(detail.get("weight"))
        try:
            observed = date.fromisoformat(calendar_date)
        except ValueError:
            continue
        if weight is not None and weight > 0:
            body_stats.setdefault(user_id, []).append((observed, weight))
    try:
        connection.execute("BEGIN")
        for workout in assessment_workouts:
            workout_id = int(workout["id"])
            user_id = owners[workout_id]
            observed_on = str(workout.get("date") or "")[:10]
            connection.execute(
                """
                INSERT INTO assessments (
                    daily_workout_id, trainerize_user_id, assessment_date,
                    status, workout_id, workout_name, schema_version, source,
                    date_created, date_updated, extraction_run_id, raw_json
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
                    raw_json=excluded.raw_json
                """,
                (
                    workout_id,
                    user_id,
                    observed_on,
                    workout.get("status"),
                    workout.get("workoutID"),
                    workout.get("name"),
                    _assessment_schema_version(workout),
                    workout.get("from"),
                    workout.get("dateCreated"),
                    workout.get("dateUpdated"),
                    extraction_run_id,
                    json.dumps(workout, separators=(",", ":")),
                ),
            )
            connection.execute(
                "DELETE FROM assessment_exercises WHERE daily_workout_id=?",
                (workout_id,),
            )
            for exercise_position, exercise in enumerate(
                workout.get("exercises") or []
            ):
                definition = exercise.get("def") or {}
                for stat_position, stat in enumerate(
                    exercise.get("stats") or [{}]
                ):
                    connection.execute(
                        """
                        INSERT INTO assessment_exercises (
                            daily_workout_id, exercise_position, stat_position,
                            daily_exercise_id, exercise_id, exercise_name,
                            record_type, side, target, note, set_id, reps,
                            weight, distance, time_seconds, calories, level,
                            speed
                        ) VALUES (
                            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                            ?, ?
                        )
                        """,
                        (
                            workout_id,
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
                            _number(stat.get("reps")),
                            _number(stat.get("weight")),
                            _number(stat.get("distance")),
                            _number(stat.get("time")),
                            _number(stat.get("calories")),
                            _number(stat.get("level")),
                            _number(stat.get("speed")),
                        ),
                    )
            if "assessment_body_weights" not in tables:
                continue
            assessment_day = date.fromisoformat(observed_on)
            nearby = sorted(
                (
                    (abs((weight_day - assessment_day).days), weight_day, weight)
                    for weight_day, weight in body_stats.get(user_id, [])
                    if abs((weight_day - assessment_day).days) <= 30
                ),
                key=lambda item: (item[0], item[1]),
            )
            if nearby:
                _, weight_day, weight = nearby[0]
                day_offset = (weight_day - assessment_day).days
                quality = (
                    "Same day"
                    if day_offset == 0
                    else "Within 7 days"
                    if abs(day_offset) <= 7
                    else "Within 30 days"
                )
                connection.execute(
                    """
                    INSERT INTO assessment_body_weights (
                        daily_workout_id, trainerize_user_id, assessment_date,
                        body_weight_kg, measurement_date, day_offset,
                        timing_quality, selection_method, source,
                        lookup_status, raw_json, updated_at
                    ) VALUES (
                        ?, ?, ?, ?, ?, ?, ?, 'calendar_body_stat',
                        'trainerize', 'incremental', NULL, ?
                    )
                    ON CONFLICT(daily_workout_id) DO UPDATE SET
                        body_weight_kg=excluded.body_weight_kg,
                        measurement_date=excluded.measurement_date,
                        day_offset=excluded.day_offset,
                        timing_quality=excluded.timing_quality,
                        selection_method=excluded.selection_method,
                        lookup_status=excluded.lookup_status,
                        updated_at=excluded.updated_at
                    """,
                    (
                        workout_id,
                        user_id,
                        observed_on,
                        weight,
                        weight_day.isoformat(),
                        day_offset,
                        quality,
                        observed_at,
                    ),
                )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
    return {
        "status": "complete",
        "assessments_updated": len(assessment_workouts),
        "reason": None,
    }


def refresh_sources(
    *,
    reconciliation_database: Path,
    longitudinal_database: Path,
    assessment_database: Path | None = None,
    client: TrainerizeClient | None = None,
    lookback_days: int = 21,
    today: date | None = None,
) -> dict[str, Any]:
    client = client or TrainerizeClient(timeout=60)
    today = today or date.today()
    observed_at = _now()
    users = _active_clients(client)
    if not users:
        raise RuntimeError("Trainerize returned an empty active roster")
    _validate_roster_change(reconciliation_database, len(users))
    owners, calendar_items = _recent_calendar(
        client,
        users,
        start_date=today - timedelta(days=max(1, lookback_days) - 1),
        end_date=today + timedelta(days=7),
    )
    calendar_items_updated = _upsert_calendar_items(
        longitudinal_database,
        calendar_items,
    )
    workouts = _workout_details(client, owners)
    _upsert_workouts(
        longitudinal_database,
        owners,
        workouts,
        observed_at=observed_at,
    )
    assessment_refresh = _upsert_recent_assessments(
        assessment_database,
        owners,
        workouts,
        calendar_items,
        observed_at=observed_at,
    )
    run_id = _replace_roster(
        reconciliation_database,
        users,
        observed_at=observed_at,
    )
    return {
        "status": "complete",
        "observed_at": observed_at,
        "run_id": run_id,
        "active_roster": len(users),
        "recent_workouts": len(workouts),
        "calendar_items_updated": calendar_items_updated,
        "assessment_refresh": assessment_refresh,
        "lookback_days": lookback_days,
    }
