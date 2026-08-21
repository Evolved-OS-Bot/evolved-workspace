#!/usr/bin/env python3
"""Build the minimum private databases required by performance reporting.

The bundle contains no API credentials. It remains identified private data and
must only be transferred to the protected Railway performance-service volume.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from trainerize_performance_reporting import (
    ASSESSMENT_DB,
    LONGITUDINAL_DB,
    RECON_DB,
)
from trainerize_performance.refresh import ASSESSMENT_EVIDENCE_SCHEMA


def latest_run(source: sqlite3.Connection) -> str:
    row = source.execute(
        """
        SELECT run_id FROM runs
        WHERE status='complete'
        ORDER BY started_at DESC LIMIT 1
        """
    ).fetchone()
    if not row:
        raise RuntimeError("No completed reconciliation run exists")
    return str(row[0])


def build_reconciliation(source_path: Path, target_path: Path) -> dict[str, Any]:
    source = sqlite3.connect(source_path)
    source.row_factory = sqlite3.Row
    run_id = latest_run(source)
    run = source.execute(
        "SELECT run_id, started_at, finished_at, status FROM runs WHERE run_id=?",
        (run_id,),
    ).fetchone()
    roster = source.execute(
        """
        SELECT run_id, trainerize_user_id, email, first_name, last_name,
               client_type, trainer_id, latest_signed_in, raw_json, roster_view
        FROM trainerize_clients
        WHERE run_id=? AND roster_view='active'
        ORDER BY trainerize_user_id
        """,
        (run_id,),
    ).fetchall()
    source.close()

    target = sqlite3.connect(target_path)
    target.executescript(
        """
        CREATE TABLE runs (
            run_id TEXT PRIMARY KEY,
            started_at TEXT,
            finished_at TEXT,
            status TEXT
        );
        CREATE TABLE trainerize_clients (
            run_id TEXT,
            trainerize_user_id INTEGER,
            email TEXT,
            first_name TEXT,
            last_name TEXT,
            client_type TEXT,
            trainer_id INTEGER,
            latest_signed_in TEXT,
            raw_json TEXT,
            roster_view TEXT
        );
        CREATE INDEX idx_performance_roster
        ON trainerize_clients(run_id, roster_view, trainerize_user_id);
        """
    )
    target.execute(
        "INSERT INTO runs VALUES (?, ?, ?, ?)",
        tuple(run),
    )
    target.executemany(
        "INSERT INTO trainerize_clients VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        [tuple(row) for row in roster],
    )
    target.commit()
    target.execute("VACUUM")
    target.close()
    return {"run_id": run_id, "active_roster": len(roster)}


def build_longitudinal(
    source_path: Path,
    target_path: Path,
    active_ids: set[int],
) -> dict[str, Any]:
    source = sqlite3.connect(source_path)
    source.row_factory = sqlite3.Row
    target = sqlite3.connect(target_path)
    target.executescript(
        """
        CREATE TABLE daily_workouts (
            daily_workout_id INTEGER PRIMARY KEY,
            trainerize_user_id INTEGER,
            workout_date TEXT,
            status TEXT
        );
        CREATE INDEX idx_performance_workouts
        ON daily_workouts(trainerize_user_id, workout_date);
        CREATE TABLE exercise_results (
            daily_workout_id INTEGER,
            trainerize_user_id INTEGER,
            workout_date TEXT,
            exercise_position INTEGER,
            stat_position INTEGER,
            exercise_name TEXT,
            weight REAL,
            reps REAL,
            PRIMARY KEY (
                daily_workout_id,
                exercise_position,
                stat_position
            )
        );
        CREATE INDEX idx_performance_strength
        ON exercise_results(trainerize_user_id, exercise_name, workout_date);
        CREATE TABLE source_observations (
            observed_at TEXT NOT NULL,
            status TEXT NOT NULL
        );
        """
    )
    placeholders = ",".join("?" for _ in active_ids)
    workout_rows = source.execute(
        f"""
        SELECT daily_workout_id, trainerize_user_id, workout_date, status
        FROM daily_workouts
        WHERE trainerize_user_id IN ({placeholders})
        """,
        tuple(sorted(active_ids)),
    ).fetchall()
    strength_rows = source.execute(
        f"""
        SELECT daily_workout_id, trainerize_user_id, workout_date,
               exercise_position, stat_position, exercise_name, weight, reps
        FROM exercise_results
        WHERE trainerize_user_id IN ({placeholders})
          AND exercise_name IN (
            'Barbell Bench Press',
            'Barbell Deadlift',
            'Nexus Point Squat',
            'Barbell Front Squat',
            'Barbell Back Squat'
          )
          AND weight > 0 AND reps > 0 AND reps <= 20
        """,
        tuple(sorted(active_ids)),
    ).fetchall()
    source.close()
    target.executemany(
        "INSERT INTO daily_workouts VALUES (?, ?, ?, ?)",
        [tuple(row) for row in workout_rows],
    )
    target.executemany(
        "INSERT INTO exercise_results VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        [tuple(row) for row in strength_rows],
    )
    target.commit()
    latest = target.execute(
        "SELECT MAX(workout_date) FROM daily_workouts"
    ).fetchone()[0]
    source_observed_at = datetime.now(UTC).isoformat()
    target.execute(
        "INSERT INTO source_observations VALUES (?, 'complete')",
        (source_observed_at,),
    )
    target.commit()
    target.execute("VACUUM")
    target.close()
    return {
        "workout_rows": len(workout_rows),
        "strength_rows": len(strength_rows),
        "latest_workout_date": latest,
        "source_observed_at": source_observed_at,
    }


def build_assessments(
    source_path: Path,
    target_path: Path,
    active_ids: set[int],
) -> dict[str, int]:
    target = sqlite3.connect(target_path)
    target.executescript(ASSESSMENT_EVIDENCE_SCHEMA)
    if not source_path.exists():
        target.commit()
        target.close()
        return {
            "assessment_rows": 0,
            "assessment_exercise_rows": 0,
            "assessment_body_weight_rows": 0,
        }
    source = sqlite3.connect(source_path)
    placeholders = ",".join("?" for _ in active_ids)
    source_tables = {
        str(row[0])
        for row in source.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
    }
    assessment_columns = {
        str(row[1])
        for row in source.execute("PRAGMA table_info(assessments)")
    }
    active_parameters = tuple(sorted(active_ids))
    if "daily_workout_id" in assessment_columns:
        rows = source.execute(
            f"""
            SELECT daily_workout_id, trainerize_user_id, assessment_date,
                   status, workout_id, workout_name, schema_version, source,
                   date_created, date_updated, extraction_run_id, raw_json
            FROM assessments
            WHERE trainerize_user_id IN ({placeholders})
            """,
            active_parameters,
        ).fetchall()
    else:
        rows = source.execute(
            f"""
            SELECT -rowid, trainerize_user_id, assessment_date,
                   'historical_date_only', NULL, NULL, 'legacy_date_only',
                   NULL, NULL, NULL, 0, '{{}}'
            FROM assessments
            WHERE trainerize_user_id IN ({placeholders})
            """,
            active_parameters,
        ).fetchall()
    target.executemany(
        "INSERT INTO assessments VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        rows,
    )
    assessment_ids = tuple(int(row[0]) for row in rows)
    exercise_rows: list[tuple[Any, ...]] = []
    body_weight_rows: list[tuple[Any, ...]] = []
    if assessment_ids and "assessment_exercises" in source_tables:
        assessment_placeholders = ",".join("?" for _ in assessment_ids)
        exercise_rows = source.execute(
            f"""
            SELECT daily_workout_id, exercise_position, stat_position,
                   daily_exercise_id, exercise_id, exercise_name, record_type,
                   side, target, note, set_id, reps, weight, distance,
                   time_seconds, calories, level, speed
            FROM assessment_exercises
            WHERE daily_workout_id IN ({assessment_placeholders})
            """,
            assessment_ids,
        ).fetchall()
        target.executemany(
            """
            INSERT INTO assessment_exercises
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            exercise_rows,
        )
    if assessment_ids and "assessment_body_weights" in source_tables:
        assessment_placeholders = ",".join("?" for _ in assessment_ids)
        body_weight_rows = source.execute(
            f"""
            SELECT daily_workout_id, trainerize_user_id, assessment_date,
                   body_weight_kg, measurement_date, day_offset,
                   timing_quality, selection_method, source, lookup_status,
                   raw_json, updated_at
            FROM assessment_body_weights
            WHERE daily_workout_id IN ({assessment_placeholders})
            """,
            assessment_ids,
        ).fetchall()
        target.executemany(
            """
            INSERT INTO assessment_body_weights
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            body_weight_rows,
        )
    source.close()
    target.commit()
    target.close()
    return {
        "assessment_rows": len(rows),
        "assessment_exercise_rows": len(exercise_rows),
        "assessment_body_weight_rows": len(body_weight_rows),
    }


def digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def build_bundle(
    *,
    reconciliation_database: Path,
    longitudinal_database: Path,
    assessment_database: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    reconciliation_target = output_dir / "reconciliation.sqlite"
    longitudinal_target = output_dir / "longitudinal.sqlite"
    assessment_target = output_dir / "assessments.sqlite"
    for path in (
        reconciliation_target,
        longitudinal_target,
        assessment_target,
    ):
        if path.exists():
            path.unlink()

    reconciliation = build_reconciliation(
        reconciliation_database,
        reconciliation_target,
    )
    roster_connection = sqlite3.connect(reconciliation_target)
    active_ids = {
        int(row[0])
        for row in roster_connection.execute(
            "SELECT trainerize_user_id FROM trainerize_clients"
        )
    }
    roster_connection.close()
    longitudinal = build_longitudinal(
        longitudinal_database,
        longitudinal_target,
        active_ids,
    )
    assessments = build_assessments(
        assessment_database,
        assessment_target,
        active_ids,
    )
    files = {}
    for path in (
        reconciliation_target,
        longitudinal_target,
        assessment_target,
    ):
        files[path.name] = {
            "bytes": path.stat().st_size,
            "sha256": digest(path),
        }
        path.chmod(0o600)
    manifest = {
        "schema_version": 1,
        "generated_at": datetime.now(UTC).isoformat(),
        **reconciliation,
        **longitudinal,
        **assessments,
        "files": files,
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_dir / "manifest.json").chmod(0o600)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--reconciliation-database",
        type=Path,
        default=RECON_DB,
    )
    parser.add_argument(
        "--longitudinal-database",
        type=Path,
        default=LONGITUDINAL_DB,
    )
    parser.add_argument(
        "--assessment-database",
        type=Path,
        default=ASSESSMENT_DB,
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    result = build_bundle(
        reconciliation_database=args.reconciliation_database,
        longitudinal_database=args.longitudinal_database,
        assessment_database=args.assessment_database,
        output_dir=args.output_dir,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
