from __future__ import annotations

import hashlib
import io
import json
import sqlite3
from datetime import date

from trainerize_performance.bundle import install_bundle
from trainerize_performance.config import Settings
from trainerize_performance.cron import run_refresh
from trainerize_performance.refresh import (
    _upsert_recent_assessments,
    refresh_sources,
)
from trainerize_performance.service import PerformanceService


def database_bytes(tmp_path, name, schema):
    path = tmp_path / name
    connection = sqlite3.connect(path)
    connection.executescript(schema)
    connection.commit()
    connection.close()
    return path.read_bytes()


def source_files(tmp_path):
    today = date.today().isoformat()
    reconciliation = database_bytes(
        tmp_path,
        "source-reconciliation.sqlite",
        f"""
        CREATE TABLE runs (
            run_id TEXT PRIMARY KEY,
            started_at TEXT,
            finished_at TEXT,
            status TEXT
        );
        INSERT INTO runs VALUES (
            'run-1', '{today}T00:00:00+00:00',
            '{today}T00:01:00+00:00', 'complete'
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
        INSERT INTO trainerize_clients VALUES (
            'run-1', 1, 'member@example.com', 'Test', 'Member',
            'Full Access', 2, '{today}', '{{}}', 'active'
        );
        """,
    )
    longitudinal = database_bytes(
        tmp_path,
        "source-longitudinal.sqlite",
        f"""
        CREATE TABLE daily_workouts (
            daily_workout_id INTEGER PRIMARY KEY,
            trainerize_user_id INTEGER,
            workout_date TEXT,
            status TEXT
        );
        INSERT INTO daily_workouts VALUES (10, 1, '{today}', 'completed');
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
        CREATE TABLE source_observations (
            observed_at TEXT,
            status TEXT
        );
        INSERT INTO source_observations VALUES ('{today}', 'complete');
        """,
    )
    assessments = database_bytes(
        tmp_path,
        "source-assessments.sqlite",
        """
        CREATE TABLE assessments (
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
        CREATE TABLE assessment_exercises (
            daily_workout_id INTEGER,
            exercise_position INTEGER,
            stat_position INTEGER,
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
            PRIMARY KEY (
                daily_workout_id, exercise_position, stat_position
            )
        );
        CREATE TABLE assessment_body_weights (
            daily_workout_id INTEGER PRIMARY KEY,
            trainerize_user_id INTEGER,
            assessment_date TEXT,
            body_weight_kg REAL,
            measurement_date TEXT,
            day_offset INTEGER,
            timing_quality TEXT,
            selection_method TEXT,
            source TEXT,
            lookup_status TEXT,
            raw_json TEXT,
            updated_at TEXT
        );
        """,
    )
    return {
        "reconciliation.sqlite": reconciliation,
        "longitudinal.sqlite": longitudinal,
        "assessments.sqlite": assessments,
    }


def manifest_for(files):
    return {
        "schema_version": 1,
        "run_id": "run-1",
        "active_roster": 1,
        "latest_workout_date": date.today().isoformat(),
        "generated_at": date.today().isoformat(),
        "files": {
            name: {
                "bytes": len(content),
                "sha256": hashlib.sha256(content).hexdigest(),
            }
            for name, content in files.items()
        },
    }


def test_install_bundle_validates_and_atomically_installs(tmp_path):
    files = source_files(tmp_path)
    data_dir = tmp_path / "installed"

    result = install_bundle(
        data_dir,
        io.BytesIO(json.dumps(manifest_for(files)).encode()),
        {name: io.BytesIO(content) for name, content in files.items()},
    )

    assert result["status"] == "accepted"
    assert (data_dir / "longitudinal.sqlite").exists()
    assert json.loads(
        (data_dir / "manifest.json").read_text(encoding="utf-8")
    )["run_id"] == "run-1"


def test_install_bundle_rejects_checksum_mismatch(tmp_path):
    files = source_files(tmp_path)
    manifest = manifest_for(files)
    manifest["files"]["longitudinal.sqlite"]["sha256"] = "not-valid"

    try:
        install_bundle(
            tmp_path / "installed",
            io.BytesIO(json.dumps(manifest).encode()),
            {name: io.BytesIO(content) for name, content in files.items()},
        )
    except ValueError as exc:
        assert "checksum" in str(exc)
    else:
        raise AssertionError("invalid checksum was accepted")


def test_service_runs_read_only_report_and_publishes_summary(
    monkeypatch,
    tmp_path,
):
    files = source_files(tmp_path)
    data_dir = tmp_path / "installed"
    install_bundle(
        data_dir,
        io.BytesIO(json.dumps(manifest_for(files)).encode()),
        {name: io.BytesIO(content) for name, content in files.items()},
    )
    published = {}

    def fake_publish(source, summary):
        published.update({"source": source, "summary": summary})
        return {"status": "accepted"}

    monkeypatch.setattr(
        "trainerize_performance.service.publish_summary",
        fake_publish,
    )
    service = PerformanceService(
        Settings(
            data_dir=data_dir,
            webhook_secret="secret",
            max_reconciliation_age_days=8,
            max_workout_age_days=14,
            refresh_lookback_days=21,
        )
    )

    result = service.run()

    assert result["status"] == "complete"
    assert result["active_roster"] == 1
    assert published["source"] == "trainerize_performance"
    assert (
        published["summary"]["standardsEvidenceSchemaVersion"] == 1
    )
    assert (
        published["summary"]["standardsEvidenceCoverage"]["status"]
        == "complete"
    )
    assert (data_dir / "public/latest-performance-summary.md").exists()


def test_incremental_refresh_updates_roster_workouts_and_observation(
    tmp_path,
):
    files = source_files(tmp_path)
    data_dir = tmp_path / "installed"
    install_bundle(
        data_dir,
        io.BytesIO(json.dumps(manifest_for(files)).encode()),
        {name: io.BytesIO(content) for name, content in files.items()},
    )

    class FakeClient:
        def get_active_clients(self, *, start, count):
            return {
                "total": 1,
                "users": (
                    [
                        {
                            "id": 1,
                            "email": "member@example.com",
                            "firstName": "Test",
                            "lastName": "Member",
                            "type": "Full Access",
                        }
                    ]
                    if start == 0
                    else []
                ),
            }

        def post(self, endpoint, payload):
            if endpoint == "/calendar/getList":
                return {
                    "calendar": [
                        {
                            "date": date.today().isoformat(),
                            "items": [
                                {
                                    "id": 99,
                                    "type": "workoutRegular",
                                    "status": "tracked",
                                }
                            ],
                        }
                    ]
                }
            if endpoint == "/dailyWorkout/get":
                return {
                    "dailyWorkouts": [
                        {
                            "id": 99,
                            "date": date.today().isoformat(),
                            "status": "tracked",
                            "exercises": [
                                {
                                    "def": {"name": "Barbell Bench Press"},
                                    "stats": [{"weight": 40, "reps": 8}],
                                }
                            ],
                        }
                    ]
                }
            raise AssertionError(endpoint)

    result = refresh_sources(
        reconciliation_database=data_dir / "reconciliation.sqlite",
        longitudinal_database=data_dir / "longitudinal.sqlite",
        client=FakeClient(),
        today=date.today(),
    )

    assert result["active_roster"] == 1
    assert result["recent_workouts"] == 1
    assert result["calendar_items_updated"] == 1
    longitudinal = sqlite3.connect(data_dir / "longitudinal.sqlite")
    assert longitudinal.execute(
        "SELECT COUNT(*) FROM daily_workouts WHERE daily_workout_id=99"
    ).fetchone()[0] == 1
    assert longitudinal.execute(
        "SELECT COUNT(*) FROM calendar_items WHERE item_id=99"
    ).fetchone()[0] == 1
    assert longitudinal.execute(
        "SELECT COUNT(*) FROM source_observations"
    ).fetchone()[0] == 2
    longitudinal.close()


def test_incremental_assessment_refresh_preserves_raw_standard_evidence(
    tmp_path,
):
    database = tmp_path / "assessments.sqlite"
    connection = sqlite3.connect(database)
    connection.executescript(
        """
        CREATE TABLE assessments (
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
        CREATE TABLE assessment_exercises (
            daily_workout_id INTEGER,
            exercise_position INTEGER,
            stat_position INTEGER,
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
            PRIMARY KEY (
                daily_workout_id, exercise_position, stat_position
            )
        );
        CREATE TABLE assessment_body_weights (
            daily_workout_id INTEGER PRIMARY KEY,
            trainerize_user_id INTEGER,
            assessment_date TEXT,
            body_weight_kg REAL,
            measurement_date TEXT,
            day_offset INTEGER,
            timing_quality TEXT,
            selection_method TEXT,
            source TEXT,
            lookup_status TEXT,
            raw_json TEXT,
            updated_at TEXT
        );
        """
    )
    connection.commit()
    connection.close()
    workout = {
        "id": 501,
        "date": "2026-08-01",
        "status": "tracked",
        "workoutID": 183960272,
        "name": "Strength Assessment",
        "exercises": [
            {
                "def": {
                    "id": 91,
                    "name": "ATG Split Squat",
                    "recordType": "reps",
                    "side": "right",
                    "target": "Full depth",
                },
                "stats": [{"reps": 10, "weight": 30}],
            }
        ],
    }
    calendar = [
        (
            7,
            "2026-08-01",
            {
                "id": 501,
                "type": "workoutRegular",
                "title": "Strength Assessment",
                "detail": {"workoutID": 183960272},
            },
        ),
        (
            7,
            "2026-08-01",
            {
                "id": 502,
                "type": "bodyStat",
                "detail": {"weight": 60},
            },
        ),
    ]

    result = _upsert_recent_assessments(
        database,
        {501: 7},
        [workout],
        calendar,
        observed_at="2026-08-02T00:00:00+00:00",
    )

    assert result["assessments_updated"] == 1
    connection = sqlite3.connect(database)
    assert connection.execute(
        "SELECT exercise_name FROM assessment_exercises"
    ).fetchone()[0] == "ATG Split Squat"
    assert connection.execute(
        "SELECT body_weight_kg FROM assessment_body_weights"
    ).fetchone()[0] == 60
    connection.close()


def test_incremental_assessment_refresh_bootstraps_legacy_bundle_schema(
    tmp_path,
):
    database = tmp_path / "assessments.sqlite"
    connection = sqlite3.connect(database)
    connection.executescript(
        """
        CREATE TABLE assessments (
            trainerize_user_id INTEGER,
            assessment_date TEXT
        );
        INSERT INTO assessments VALUES (7, '2026-01-15');
        """
    )
    connection.commit()
    connection.close()
    workout = {
        "id": 501,
        "date": "2026-08-01",
        "status": "tracked",
        "workoutID": 183960272,
        "name": "Strength Assessment",
        "exercises": [],
    }

    result = _upsert_recent_assessments(
        database,
        {501: 7},
        [workout],
        [],
        observed_at="2026-08-02T00:00:00+00:00",
    )

    assert result["status"] == "complete"
    assert result["assessments_updated"] == 1
    connection = sqlite3.connect(database)
    assert {
        row[0]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
    } >= {
        "assessments",
        "assessment_exercises",
        "assessment_body_weights",
        "legacy_assessment_dates",
    }
    assert connection.execute(
        "SELECT COUNT(*) FROM assessments"
    ).fetchone()[0] == 2
    assert connection.execute(
        """
        SELECT COUNT(*) FROM assessments
        WHERE schema_version='legacy_date_only'
        """
    ).fetchone()[0] == 1
    connection.close()


def test_cron_triggers_refresh_and_waits_for_new_completion(monkeypatch):
    class Response:
        def __init__(self, status_code, payload):
            self.status_code = status_code
            self.payload = payload

        def raise_for_status(self):
            if self.status_code >= 400:
                raise RuntimeError(self.status_code)

        def json(self):
            return self.payload

    class Session:
        def __init__(self):
            self.get_count = 0

        def get(self, url, *, headers, timeout):
            self.get_count += 1
            if self.get_count == 1:
                return Response(
                    200,
                    {
                        "status": "complete",
                        "completedAt": "2026-07-27T00:00:00+00:00",
                    },
                )
            return Response(
                200,
                {
                    "status": "complete",
                    "completedAt": "2026-07-28T00:00:00+00:00",
                    "active_roster": 151,
                },
            )

        def post(self, url, *, headers, timeout):
            return Response(202, {"status": "started"})

    monkeypatch.setattr("trainerize_performance.cron.time.sleep", lambda _: None)

    result = run_refresh(
        base_url="https://performance.example",
        secret="secret",
        poll_seconds=1,
        session=Session(),
    )

    assert result["active_roster"] == 151
