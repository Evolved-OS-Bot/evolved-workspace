#!/usr/bin/env python3
"""Extract Trainerize longitudinal member data into a private SQLite database.

The extractor is resumable and read-only. It never changes Trainerize account state.
Temporary reactivation, when required, is performed separately through the signed-in
Trainerize web interface and recorded in the private audit log.
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from collections import Counter
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any, Iterable

from trainerize_client import TrainerizeAPIError, TrainerizeClient


WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
PRIVATE_DIR = WORKSPACE_ROOT / "data" / "private" / "trainerize-longitudinal-audit"
DEFAULT_DATABASE = PRIVATE_DIR / "trainerize_longitudinal.sqlite"
DEFAULT_CANDIDATES = PRIVATE_DIR / "reactivation_candidates.json"
DEFAULT_START_YEAR = 2018
DETAIL_BATCH_SIZE = 20


SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS extraction_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    phase TEXT NOT NULL,
    status_filter TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'running',
    summary_json TEXT
);

CREATE TABLE IF NOT EXISTS clients (
    trainerize_user_id INTEGER PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    email TEXT,
    status TEXT,
    active_level TEXT,
    role TEXT,
    trainer_id INTEGER,
    trainer_name TEXT,
    location_id INTEGER,
    created_at TEXT,
    latest_signed_in TEXT,
    birth_date TEXT,
    sex TEXT,
    city TEXT,
    referral_source TEXT,
    is_test_client INTEGER NOT NULL DEFAULT 0,
    profile_json TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS calendar_windows (
    trainerize_user_id INTEGER NOT NULL,
    window_start TEXT NOT NULL,
    window_end TEXT NOT NULL,
    fetched_at TEXT NOT NULL,
    item_count INTEGER NOT NULL,
    PRIMARY KEY (trainerize_user_id, window_start, window_end),
    FOREIGN KEY (trainerize_user_id) REFERENCES clients(trainerize_user_id)
);

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
    PRIMARY KEY (trainerize_user_id, calendar_date, item_id, item_type),
    FOREIGN KEY (trainerize_user_id) REFERENCES clients(trainerize_user_id)
);

CREATE INDEX IF NOT EXISTS idx_calendar_type_status
ON calendar_items(item_type, status, calendar_date);

CREATE TABLE IF NOT EXISTS daily_workouts (
    daily_workout_id INTEGER PRIMARY KEY,
    trainerize_user_id INTEGER NOT NULL,
    workout_date TEXT,
    status TEXT,
    workout_id INTEGER,
    workout_name TEXT,
    workout_type TEXT,
    from_source TEXT,
    from_program TEXT,
    program_day TEXT,
    duration_seconds REAL,
    work_duration_seconds REAL,
    rpe REAL,
    date_created TEXT,
    date_updated TEXT,
    raw_json TEXT NOT NULL,
    fetched_at TEXT NOT NULL,
    FOREIGN KEY (trainerize_user_id) REFERENCES clients(trainerize_user_id)
);

CREATE INDEX IF NOT EXISTS idx_daily_workouts_user_date
ON daily_workouts(trainerize_user_id, workout_date);

CREATE TABLE IF NOT EXISTS exercise_results (
    daily_workout_id INTEGER NOT NULL,
    trainerize_user_id INTEGER NOT NULL,
    workout_date TEXT,
    exercise_position INTEGER NOT NULL,
    stat_position INTEGER NOT NULL,
    daily_exercise_id INTEGER,
    exercise_id INTEGER,
    exercise_name TEXT,
    record_type TEXT,
    exercise_type TEXT,
    side TEXT,
    target TEXT,
    target_detail TEXT,
    tags_json TEXT,
    note TEXT,
    stat_id INTEGER,
    set_id INTEGER,
    reps REAL,
    weight REAL,
    distance REAL,
    time_seconds REAL,
    calories REAL,
    level REAL,
    speed REAL,
    PRIMARY KEY (daily_workout_id, exercise_position, stat_position),
    FOREIGN KEY (daily_workout_id) REFERENCES daily_workouts(daily_workout_id) ON DELETE CASCADE,
    FOREIGN KEY (trainerize_user_id) REFERENCES clients(trainerize_user_id)
);

CREATE INDEX IF NOT EXISTS idx_exercise_user_name_date
ON exercise_results(trainerize_user_id, exercise_name, workout_date);

CREATE TABLE IF NOT EXISTS client_extras (
    trainerize_user_id INTEGER PRIMARY KEY,
    client_summary_json TEXT,
    accomplishments_json TEXT,
    goals_json TEXT,
    training_plans_json TEXT,
    fetched_at TEXT NOT NULL,
    FOREIGN KEY (trainerize_user_id) REFERENCES clients(trainerize_user_id)
);

CREATE TABLE IF NOT EXISTS extraction_errors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    extraction_run_id INTEGER NOT NULL,
    trainerize_user_id INTEGER,
    item_id INTEGER,
    stage TEXT NOT NULL,
    http_status INTEGER,
    message TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (extraction_run_id) REFERENCES extraction_runs(id)
);

CREATE TABLE IF NOT EXISTS account_state_changes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trainerize_user_id INTEGER NOT NULL,
    original_status TEXT NOT NULL,
    temporary_status TEXT NOT NULL,
    changed_at TEXT,
    restored_at TEXT,
    verification_status TEXT,
    notes TEXT,
    FOREIGN KEY (trainerize_user_id) REFERENCES clients(trainerize_user_id)
);
"""


def utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def open_database(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    os.chmod(path.parent, 0o700)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.executescript(SCHEMA)
    connection.commit()
    os.chmod(path, 0o600)
    return connection


def begin_run(connection: sqlite3.Connection, phase: str, status_filter: str) -> int:
    cursor = connection.execute(
        "INSERT INTO extraction_runs (started_at, phase, status_filter) VALUES (?, ?, ?)",
        (utc_now(), phase, status_filter),
    )
    connection.commit()
    return int(cursor.lastrowid)


def finish_run(
    connection: sqlite3.Connection,
    run_id: int,
    *,
    status: str,
    summary: dict[str, Any],
) -> None:
    connection.execute(
        "UPDATE extraction_runs SET finished_at=?, status=?, summary_json=? WHERE id=?",
        (utc_now(), status, json.dumps(summary, sort_keys=True), run_id),
    )
    connection.commit()


def log_error(
    connection: sqlite3.Connection,
    run_id: int,
    stage: str,
    error: Exception,
    *,
    user_id: int | None = None,
    item_id: int | None = None,
) -> None:
    status = error.status_code if isinstance(error, TrainerizeAPIError) else None
    connection.execute(
        """
        INSERT INTO extraction_errors (
            extraction_run_id, trainerize_user_id, item_id, stage,
            http_status, message, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (run_id, user_id, item_id, stage, status, str(error)[:500], utc_now()),
    )


def collect_client_page(client: TrainerizeClient, view: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    start = 0
    while True:
        response = client.get_client_list(
            view=view,
            start=start,
            count=100,
            location_id=client.location_id,
        )
        batch = response.get("users") or []
        rows.extend(batch)
        start += len(batch)
        if not batch or start >= int(response.get("total") or 0):
            return rows


def chunks(values: list[int], size: int) -> Iterable[list[int]]:
    for start in range(0, len(values), size):
        yield values[start : start + size]


def fetch_profiles(
    client: TrainerizeClient, user_ids: list[int]
) -> dict[int, dict[str, Any]]:
    profiles: dict[int, dict[str, Any]] = {}
    for batch in chunks(user_ids, 100):
        response = client.post(
            "/user/getProfile", {"usersid": batch, "unitBodystats": "cm"}
        )
        for profile in response.get("usrProfile") or response.get("users") or []:
            if profile.get("id") is not None:
                profiles[int(profile["id"])] = profile
    return profiles


def extract_roster(
    client: TrainerizeClient,
    connection: sqlite3.Connection,
    run_id: int,
) -> dict[str, int]:
    active = collect_client_page(client, "activeClient")
    deactivated = collect_client_page(client, "deactivatedClient")
    source_rows = [("active", row) for row in active] + [
        ("deactivated", row) for row in deactivated
    ]
    user_ids = sorted(
        {int(row["id"]) for _, row in source_rows if row.get("id") is not None}
    )
    profiles = fetch_profiles(client, user_ids)
    now = utc_now()
    for source_status, roster_row in source_rows:
        user_id = int(roster_row["id"])
        profile = profiles.get(user_id, {})
        status = str(profile.get("status") or roster_row.get("status") or source_status)
        connection.execute(
            """
            INSERT INTO clients (
                trainerize_user_id, first_name, last_name, email, status,
                active_level, role, trainer_id, trainer_name, location_id,
                created_at, latest_signed_in, birth_date, sex, city,
                referral_source, is_test_client, profile_json, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(trainerize_user_id) DO UPDATE SET
                first_name=excluded.first_name,
                last_name=excluded.last_name,
                email=excluded.email,
                status=excluded.status,
                active_level=excluded.active_level,
                role=excluded.role,
                trainer_id=excluded.trainer_id,
                trainer_name=excluded.trainer_name,
                location_id=excluded.location_id,
                created_at=excluded.created_at,
                latest_signed_in=excluded.latest_signed_in,
                birth_date=excluded.birth_date,
                sex=excluded.sex,
                city=excluded.city,
                referral_source=excluded.referral_source,
                is_test_client=excluded.is_test_client,
                profile_json=excluded.profile_json,
                updated_at=excluded.updated_at
            """,
            (
                user_id,
                profile.get("firstName") or roster_row.get("firstName"),
                profile.get("lastName") or roster_row.get("lastName"),
                profile.get("email") or roster_row.get("email"),
                source_status,
                profile.get("activeLevel"),
                profile.get("role") or roster_row.get("role"),
                profile.get("trainerID") or roster_row.get("trainerID"),
                profile.get("trainerName"),
                profile.get("locationID"),
                profile.get("created"),
                profile.get("latestSignedIn"),
                profile.get("birthDate"),
                profile.get("sex"),
                profile.get("city"),
                profile.get("referralSource"),
                int(bool(profile.get("isTestClient"))),
                json.dumps(profile or roster_row, separators=(",", ":"), ensure_ascii=False),
                now,
            ),
        )
    connection.commit()
    return {
        "active": len(active),
        "deactivated": len(deactivated),
        "profiles": len(profiles),
    }


def calendar_year_windows(created_at: str | None) -> Iterable[tuple[str, str]]:
    start_year = DEFAULT_START_YEAR
    if created_at and len(created_at) >= 4 and created_at[:4].isdigit():
        start_year = max(DEFAULT_START_YEAR, int(created_at[:4]))
    current = date.today()
    for year in range(start_year, current.year + 1):
        yield f"{year}-01-01", min(f"{year}-12-31", current.isoformat())


def number(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def text_value(value: Any) -> str | None:
    if value is None or value == "":
        return None
    if isinstance(value, (dict, list)):
        return json.dumps(value, separators=(",", ":"), ensure_ascii=False)
    return str(value)


def upsert_calendar_item(
    connection: sqlite3.Connection,
    user_id: int,
    calendar_date: str,
    item: dict[str, Any],
) -> None:
    detail = item.get("detail") or {}
    if not isinstance(detail, dict):
        detail = {}
    item_type = str(item.get("type") or "unknown")
    item_id = int(item.get("id") or 0)
    connection.execute(
        """
        INSERT INTO calendar_items (
            trainerize_user_id, calendar_date, item_id, item_type, status,
            title, workout_id, exercise_id, trainer_id, trainer_name,
            location_id, event_category, duration_seconds, rpe,
            body_weight_kg, body_fat_percent, bmi, resting_heart_rate,
            blood_pressure_systolic, blood_pressure_diastolic, raw_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(trainerize_user_id, calendar_date, item_id, item_type) DO UPDATE SET
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
            item_id,
            item_type,
            item.get("status"),
            item.get("title"),
            detail.get("workoutID"),
            detail.get("exerciseID"),
            detail.get("trainerID"),
            detail.get("trainerName"),
            detail.get("locationID"),
            detail.get("eventCategory"),
            number(detail.get("time")),
            number(detail.get("rpe")),
            number(detail.get("weight")),
            number(detail.get("fat") or detail.get("bodyFatPercent")),
            number(detail.get("bodyMassIndex")),
            number(detail.get("restingHeartRate")),
            number(detail.get("bloodPressureSystolic")),
            number(detail.get("bloodPressureDiastolic")),
            json.dumps(item, separators=(",", ":"), ensure_ascii=False),
        ),
    )


def selected_clients(
    connection: sqlite3.Connection,
    status_filter: str,
    user_ids: set[int] | None,
) -> list[sqlite3.Row]:
    query = "SELECT * FROM clients WHERE is_test_client=0"
    parameters: list[Any] = []
    if status_filter != "all":
        query += " AND status=?"
        parameters.append(status_filter)
    if user_ids:
        placeholders = ",".join("?" for _ in user_ids)
        query += f" AND trainerize_user_id IN ({placeholders})"
        parameters.extend(sorted(user_ids))
    query += " ORDER BY trainerize_user_id"
    return connection.execute(query, parameters).fetchall()


def extract_calendars(
    client: TrainerizeClient,
    connection: sqlite3.Connection,
    run_id: int,
    *,
    status_filter: str,
    user_ids: set[int] | None,
    refresh: bool,
) -> dict[str, int]:
    rows = selected_clients(connection, status_filter, user_ids)
    counts: Counter[str] = Counter()
    for position, row in enumerate(rows, start=1):
        user_id = int(row["trainerize_user_id"])
        for window_start, window_end in calendar_year_windows(row["created_at"]):
            if not refresh:
                existing = connection.execute(
                    """
                    SELECT 1 FROM calendar_windows
                    WHERE trainerize_user_id=? AND window_start=? AND window_end=?
                    """,
                    (user_id, window_start, window_end),
                ).fetchone()
                if existing:
                    counts["windows_skipped"] += 1
                    continue
            try:
                response = client.post(
                    "/calendar/getList",
                    {
                        "userID": user_id,
                        "startDate": window_start,
                        "endDate": window_end,
                        "unitDistance": "km",
                        "unitWeight": "kg",
                    },
                )
                item_count = 0
                for calendar_day in response.get("calendar") or []:
                    calendar_date = str(calendar_day.get("date") or "")[:10]
                    for item in calendar_day.get("items") or []:
                        upsert_calendar_item(connection, user_id, calendar_date, item)
                        counts[f"item_{item.get('type') or 'unknown'}"] += 1
                        item_count += 1
                connection.execute(
                    """
                    INSERT OR REPLACE INTO calendar_windows (
                        trainerize_user_id, window_start, window_end, fetched_at, item_count
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (user_id, window_start, window_end, utc_now(), item_count),
                )
                counts["windows_fetched"] += 1
            except Exception as exc:  # continue the resumable audit
                log_error(connection, run_id, "calendar", exc, user_id=user_id)
                counts["calendar_errors"] += 1
            connection.commit()
        if position % 10 == 0 or position == len(rows):
            print(
                {
                    "calendar_clients_processed": position,
                    "calendar_clients_total": len(rows),
                    "tracked_workout_items": counts["item_workoutRegular"],
                    "errors": counts["calendar_errors"],
                },
                flush=True,
            )
    counts["clients"] = len(rows)
    return dict(counts)


def owner_map_for_workouts(
    connection: sqlite3.Connection,
    *,
    status_filter: str,
    user_ids: set[int] | None,
) -> dict[int, int]:
    query = """
    SELECT ci.item_id, ci.trainerize_user_id
    FROM calendar_items ci
    JOIN clients c ON c.trainerize_user_id=ci.trainerize_user_id
    WHERE ci.item_type='workoutRegular' AND ci.status='tracked'
      AND c.is_test_client=0
    """
    parameters: list[Any] = []
    if status_filter != "all":
        query += " AND c.status=?"
        parameters.append(status_filter)
    if user_ids:
        placeholders = ",".join("?" for _ in user_ids)
        query += f" AND c.trainerize_user_id IN ({placeholders})"
        parameters.extend(sorted(user_ids))
    rows = connection.execute(query, parameters).fetchall()
    return {int(row["item_id"]): int(row["trainerize_user_id"]) for row in rows}


def save_daily_workout(
    connection: sqlite3.Connection,
    workout: dict[str, Any],
    expected_user_id: int,
) -> None:
    daily_workout_id = int(workout["id"])
    workout_date = str(workout.get("date") or "")[:10] or None
    tracking_stats = workout.get("trackingStats") or {}
    if not isinstance(tracking_stats, dict):
        tracking_stats = {}
    connection.execute(
        """
        INSERT INTO daily_workouts (
            daily_workout_id, trainerize_user_id, workout_date, status,
            workout_id, workout_name, workout_type, from_source, from_program,
            program_day, duration_seconds, work_duration_seconds, rpe,
            date_created, date_updated, raw_json, fetched_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(daily_workout_id) DO UPDATE SET
            trainerize_user_id=excluded.trainerize_user_id,
            workout_date=excluded.workout_date,
            status=excluded.status,
            workout_id=excluded.workout_id,
            workout_name=excluded.workout_name,
            workout_type=excluded.workout_type,
            from_source=excluded.from_source,
            from_program=excluded.from_program,
            program_day=excluded.program_day,
            duration_seconds=excluded.duration_seconds,
            work_duration_seconds=excluded.work_duration_seconds,
            rpe=excluded.rpe,
            date_created=excluded.date_created,
            date_updated=excluded.date_updated,
            raw_json=excluded.raw_json,
            fetched_at=excluded.fetched_at
        """,
        (
            daily_workout_id,
            expected_user_id,
            workout_date,
            workout.get("status"),
            workout.get("workoutID"),
            workout.get("name"),
            workout.get("type"),
            text_value(workout.get("from")),
            str(workout.get("fromProgram") or "") or None,
            str(workout.get("programDay") or "") or None,
            number(workout.get("duration")),
            number(workout.get("workDuration")),
            number(tracking_stats.get("rpe")),
            workout.get("dateCreated"),
            workout.get("dateUpdated"),
            json.dumps(workout, separators=(",", ":"), ensure_ascii=False),
            utc_now(),
        ),
    )
    connection.execute(
        "DELETE FROM exercise_results WHERE daily_workout_id=?", (daily_workout_id,)
    )
    for exercise_position, exercise in enumerate(workout.get("exercises") or []):
        definition = exercise.get("def") or {}
        stats = exercise.get("stats") or [{}]
        for stat_position, stat in enumerate(stats):
            connection.execute(
                """
                INSERT INTO exercise_results (
                    daily_workout_id, trainerize_user_id, workout_date,
                    exercise_position, stat_position, daily_exercise_id,
                    exercise_id, exercise_name, record_type, exercise_type,
                    side, target, target_detail, tags_json, note, stat_id,
                    set_id, reps, weight, distance, time_seconds, calories,
                    level, speed
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    daily_workout_id,
                    expected_user_id,
                    workout_date,
                    exercise_position,
                    stat_position,
                    exercise.get("dailyExerciseID"),
                    definition.get("id"),
                    definition.get("name"),
                    definition.get("recordType"),
                    definition.get("type"),
                    text_value(definition.get("side")),
                    text_value(definition.get("target")),
                    text_value(definition.get("targetDetail")),
                    json.dumps(definition.get("tags") or [], separators=(",", ":")),
                    text_value(exercise.get("note")),
                    stat.get("id"),
                    stat.get("setID"),
                    number(stat.get("reps")),
                    number(stat.get("weight")),
                    number(stat.get("distance")),
                    number(stat.get("time")),
                    number(stat.get("calories")),
                    number(stat.get("level")),
                    number(stat.get("speed")),
                ),
            )


def extract_details(
    client: TrainerizeClient,
    connection: sqlite3.Connection,
    run_id: int,
    *,
    status_filter: str,
    user_ids: set[int] | None,
    refresh: bool,
) -> dict[str, int]:
    owner_map = owner_map_for_workouts(
        connection, status_filter=status_filter, user_ids=user_ids
    )
    workout_ids = sorted(owner_map)
    if not refresh:
        existing = {
            int(row[0])
            for row in connection.execute("SELECT daily_workout_id FROM daily_workouts")
        }
        workout_ids = [workout_id for workout_id in workout_ids if workout_id not in existing]
    counts: Counter[str] = Counter()

    def fetch_detail_batch(batch: list[int]) -> None:
        """Fetch accessible workouts while isolating forbidden IDs efficiently."""
        try:
            response = client.post("/dailyWorkout/get", {"ids": batch})
            returned_ids: set[int] = set()
            for workout in response.get("dailyWorkouts") or []:
                workout_id = int(workout["id"])
                returned_ids.add(workout_id)
                save_daily_workout(connection, workout, owner_map[workout_id])
                counts["workouts_saved"] += 1
            for missing_id in set(batch) - returned_ids:
                counts["workouts_missing"] += 1
                log_error(
                    connection,
                    run_id,
                    "daily_workout_missing",
                    RuntimeError("Trainerize returned no detailed workout"),
                    user_id=owner_map[missing_id],
                    item_id=missing_id,
                )
        except TrainerizeAPIError as exc:
            if len(batch) > 1:
                midpoint = len(batch) // 2
                fetch_detail_batch(batch[:midpoint])
                fetch_detail_batch(batch[midpoint:])
            else:
                workout_id = batch[0]
                log_error(
                    connection,
                    run_id,
                    "daily_workout",
                    exc,
                    user_id=owner_map[workout_id],
                    item_id=workout_id,
                )
                counts[f"http_{exc.status_code or 'unknown'}"] += 1

    for position, batch in enumerate(chunks(workout_ids, DETAIL_BATCH_SIZE), start=1):
        fetch_detail_batch(batch)
        connection.commit()
        if position % 25 == 0 or position * DETAIL_BATCH_SIZE >= len(workout_ids):
            print(
                {
                    "detail_batches_processed": position,
                    "detail_batches_total": (len(workout_ids) + DETAIL_BATCH_SIZE - 1)
                    // DETAIL_BATCH_SIZE,
                    "workouts_saved": counts["workouts_saved"],
                    "http_403": counts["http_403"],
                },
                flush=True,
            )
    counts["workouts_requested"] = len(workout_ids)
    return dict(counts)


def extract_extras(
    client: TrainerizeClient,
    connection: sqlite3.Connection,
    run_id: int,
    *,
    status_filter: str,
    user_ids: set[int] | None,
) -> dict[str, int]:
    rows = selected_clients(connection, status_filter, user_ids)
    counts: Counter[str] = Counter()
    for position, row in enumerate(rows, start=1):
        user_id = int(row["trainerize_user_id"])
        results: dict[str, str | None] = {}
        calls = {
            "client_summary_json": (
                "/user/getClientSummary",
                {"userID": user_id, "unitWeight": "kg"},
            ),
            "accomplishments_json": (
                "/accomplishment/getList",
                {"userID": user_id},
            ),
            "goals_json": ("/goal/getList", {"userID": user_id}),
            "training_plans_json": ("/trainingPlan/getList", {"userID": user_id}),
        }
        for field, (endpoint, payload) in calls.items():
            try:
                response = client.post(endpoint, payload)
                results[field] = json.dumps(
                    response, separators=(",", ":"), ensure_ascii=False
                )
                counts[field] += 1
            except Exception as exc:
                results[field] = None
                counts[f"{field}_errors"] += 1
                log_error(connection, run_id, field, exc, user_id=user_id)
        connection.execute(
            """
            INSERT INTO client_extras (
                trainerize_user_id, client_summary_json, accomplishments_json,
                goals_json, training_plans_json, fetched_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(trainerize_user_id) DO UPDATE SET
                client_summary_json=excluded.client_summary_json,
                accomplishments_json=excluded.accomplishments_json,
                goals_json=excluded.goals_json,
                training_plans_json=excluded.training_plans_json,
                fetched_at=excluded.fetched_at
            """,
            (
                user_id,
                results["client_summary_json"],
                results["accomplishments_json"],
                results["goals_json"],
                results["training_plans_json"],
                utc_now(),
            ),
        )
        connection.commit()
        if position % 20 == 0 or position == len(rows):
            print(
                {"extras_clients_processed": position, "extras_clients_total": len(rows)},
                flush=True,
            )
    counts["clients"] = len(rows)
    return dict(counts)


def write_reactivation_candidates(
    connection: sqlite3.Connection, path: Path
) -> dict[str, Any]:
    rows = connection.execute(
        """
        WITH workout_coverage AS (
            SELECT
                c.trainerize_user_id,
                c.first_name,
                c.last_name,
                c.email,
                c.created_at,
                COUNT(*) AS tracked_workouts,
                COUNT(DISTINCT ci.calendar_date) AS workout_days,
                MIN(ci.calendar_date) AS first_workout_date,
                MAX(ci.calendar_date) AS last_workout_date,
                CAST(julianday(MAX(ci.calendar_date))-julianday(MIN(ci.calendar_date)) AS INT)
                    AS span_days
            FROM clients c
            JOIN calendar_items ci ON ci.trainerize_user_id=c.trainerize_user_id
            WHERE c.status='deactivated'
              AND c.is_test_client=0
              AND ci.item_type='workoutRegular'
              AND ci.status='tracked'
            GROUP BY c.trainerize_user_id
        )
        SELECT * FROM workout_coverage
        WHERE tracked_workouts >= 8 AND span_days >= 56
        ORDER BY tracked_workouts DESC, trainerize_user_id
        """
    ).fetchall()
    candidates = [dict(row) for row in rows]
    payload = {
        "generated_at": utc_now(),
        "definition": "Deactivated non-test clients with at least 8 tracked workouts across at least 56 days.",
        "candidate_count": len(candidates),
        "candidates": candidates,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    os.chmod(path, 0o600)
    return {
        "candidate_count": len(candidates),
        "tracked_workouts": sum(int(row["tracked_workouts"]) for row in candidates),
    }


def load_user_ids(path: Path | None) -> set[int] | None:
    if path is None:
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and "candidates" in data:
        return {int(row["trainerize_user_id"]) for row in data["candidates"]}
    if isinstance(data, dict) and "results" in data:
        return {
            int(row["trainerize_user_id"])
            for row in data["results"]
            if row.get("success", True)
        }
    if isinstance(data, list):
        return {int(value) for value in data}
    raise ValueError("User ID file must be a list or a candidate-report object")


def database_summary(connection: sqlite3.Connection) -> dict[str, Any]:
    return {
        "clients": connection.execute("SELECT COUNT(*) FROM clients").fetchone()[0],
        "calendar_items": connection.execute(
            "SELECT COUNT(*) FROM calendar_items"
        ).fetchone()[0],
        "tracked_workout_items": connection.execute(
            """
            SELECT COUNT(*) FROM calendar_items
            WHERE item_type='workoutRegular' AND status='tracked'
            """
        ).fetchone()[0],
        "detailed_workouts": connection.execute(
            "SELECT COUNT(*) FROM daily_workouts"
        ).fetchone()[0],
        "exercise_result_rows": connection.execute(
            "SELECT COUNT(*) FROM exercise_results"
        ).fetchone()[0],
        "body_stat_items": connection.execute(
            "SELECT COUNT(*) FROM calendar_items WHERE item_type='bodyStat'"
        ).fetchone()[0],
        "errors": connection.execute("SELECT COUNT(*) FROM extraction_errors").fetchone()[0],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--phase",
        choices=("roster", "calendar", "details", "extras", "candidates", "all"),
        default="all",
    )
    parser.add_argument(
        "--status", choices=("active", "basic", "deactivated", "all"), default="all"
    )
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE)
    parser.add_argument("--user-ids-file", type=Path)
    parser.add_argument(
        "--user-id",
        type=int,
        action="append",
        dest="user_ids",
        help="Limit extraction to one Trainerize user ID; repeat for multiple users.",
    )
    parser.add_argument("--refresh", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    connection = open_database(args.database)
    user_ids = load_user_ids(args.user_ids_file)
    if args.user_ids:
        user_ids = (user_ids or set()) | set(args.user_ids)
    client = TrainerizeClient(timeout=60)
    run_id = begin_run(connection, args.phase, args.status)
    summary: dict[str, Any] = {}
    try:
        if args.phase in {"roster", "all"}:
            summary["roster"] = extract_roster(client, connection, run_id)
        if args.phase in {"calendar", "all"}:
            summary["calendar"] = extract_calendars(
                client,
                connection,
                run_id,
                status_filter=args.status,
                user_ids=user_ids,
                refresh=args.refresh,
            )
        if args.phase in {"details", "all"}:
            summary["details"] = extract_details(
                client,
                connection,
                run_id,
                status_filter=args.status,
                user_ids=user_ids,
                refresh=args.refresh,
            )
        if args.phase in {"extras", "all"}:
            summary["extras"] = extract_extras(
                client,
                connection,
                run_id,
                status_filter=args.status,
                user_ids=user_ids,
            )
        if args.phase in {"candidates", "all"}:
            summary["reactivation_candidates"] = write_reactivation_candidates(
                connection, DEFAULT_CANDIDATES
            )
        summary["database"] = database_summary(connection)
        finish_run(connection, run_id, status="complete", summary=summary)
        print(summary)
    except Exception as exc:
        log_error(connection, run_id, "fatal", exc)
        connection.commit()
        summary["database"] = database_summary(connection)
        finish_run(connection, run_id, status="failed", summary=summary)
        raise
    finally:
        connection.close()
        if args.database.exists():
            os.chmod(args.database, 0o600)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted; committed checkpoints remain available for resume.", file=sys.stderr)
        raise SystemExit(130)
