import json
import sqlite3
from datetime import date

from scripts.trainerize_performance_reporting import (
    aggregate_strength_improvement,
    member_achievement_summaries,
    sgpt_booking_events,
    standards_evidence,
    strength_metrics,
)


def test_strength_horizons_use_governed_baseline_and_report_sample_size():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.execute(
        """
        CREATE TABLE exercise_results (
            trainerize_user_id INTEGER,
            workout_date TEXT,
            exercise_name TEXT,
            weight REAL,
            reps REAL
        )
        """
    )
    connection.executemany(
        "INSERT INTO exercise_results VALUES (?, ?, ?, ?, ?)",
        [
            (1, "2026-01-01", "Barbell Deadlift", 100, 1),
            (1, "2026-01-29", "Barbell Deadlift", 110, 1),
            (1, "2026-03-26", "Barbell Deadlift", 120, 1),
            (1, "2026-06-30", "Barbell Deadlift", 130, 1),
        ],
    )

    strengths = strength_metrics(
        connection,
        {1},
        today=date(2026, 7, 1),
    )
    result = aggregate_strength_improvement(strengths)

    assert result["fourWeeks"]["medianPercent"] == 10.0
    assert result["twelveWeeks"]["medianPercent"] == 20.0
    assert result["sixMonths"]["medianPercent"] == 30.0
    assert result["overall"]["medianPercent"] == 30.0
    assert result["overall"]["women"] == 1


def test_member_achievement_summaries_are_named_and_bounded():
    rows = [
        {
            "first_name": "Ava",
            "last_name": "Example",
            "best_improvement_percent": 25.0,
            "best_improving_movement": "Deadlift",
            "workouts_total": 98,
        },
        {
            "first_name": "Beth",
            "last_name": "Example",
            "best_improvement_percent": 15.0,
            "best_improving_movement": "Bench Press",
            "workouts_total": 52,
        },
    ]

    top, milestones = member_achievement_summaries(rows)

    assert top[0] == {
        "name": "Ava Example",
        "result": "25.0% Deadlift",
    }
    assert milestones[0]["name"] == "Beth Example"
    assert milestones[0]["status"] == "completed"
    assert milestones[1]["name"] == "Ava Example"
    assert milestones[1]["status"] == "approaching"


def test_sgpt_booking_event_uses_brisbane_date_and_explicit_outcome():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.execute(
        """
        CREATE TABLE calendar_items (
            trainerize_user_id INTEGER,
            calendar_date TEXT,
            item_id INTEGER,
            item_type TEXT,
            status TEXT,
            title TEXT,
            trainer_id INTEGER,
            trainer_name TEXT,
            event_category TEXT,
            raw_json TEXT
        )
        """
    )
    connection.execute(
        "INSERT INTO calendar_items VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            1,
            "2026-07-19",
            99,
            "appointmentV2",
            "scheduled",
            "Sculpt & Strength",
            2,
            "Piper Mae",
            "class",
            json.dumps(
                {
                    "detail": {
                        "startDate": "2026-07-19 19:30:00",
                        "endDate": "2026-07-19 20:30:00",
                        "trainerID": 2,
                        "trainerName": "Piper Mae",
                        "eventCategory": "class",
                        "isCheckedIn": True,
                    }
                }
            ),
        ),
    )

    result = sgpt_booking_events(
        connection,
        {1},
        today=date(2026, 7, 20),
    )

    assert result[0]["scheduled_date"] == "2026-07-20"
    assert result[0]["scheduled_local_time"] == "05:30"
    assert result[0]["attendance_outcome"] == "attended"
    assert result[0]["outcome_evidence"] == "trainerize_check_in"


def test_standards_evidence_preserves_raw_observations_without_classifying(
    tmp_path,
):
    database = tmp_path / "assessments.sqlite"
    connection = sqlite3.connect(database)
    connection.executescript(
        """
        CREATE TABLE assessments (
            daily_workout_id INTEGER PRIMARY KEY,
            trainerize_user_id INTEGER,
            assessment_date TEXT,
            status TEXT,
            workout_id INTEGER,
            schema_version TEXT
        );
        CREATE TABLE assessment_exercises (
            daily_workout_id INTEGER,
            exercise_position INTEGER,
            stat_position INTEGER,
            exercise_name TEXT,
            record_type TEXT,
            side TEXT,
            target TEXT,
            reps REAL,
            weight REAL,
            distance REAL,
            time_seconds REAL,
            level REAL
        );
        CREATE TABLE assessment_body_weights (
            daily_workout_id INTEGER,
            body_weight_kg REAL,
            measurement_date TEXT,
            day_offset INTEGER,
            timing_quality TEXT,
            selection_method TEXT
        );
        INSERT INTO assessments VALUES (
            101, 1, '2026-07-20', 'tracked', 55,
            'current_independent_v2'
        );
        INSERT INTO assessment_exercises VALUES (
            101, 0, 0, 'ATG Split Squat', 'reps', 'right',
            'Full depth', 10, 30, NULL, NULL, NULL
        );
        INSERT INTO assessment_body_weights VALUES (
            101, 60, '2026-07-20', 0, 'same_day', 'calendar'
        );
        """
    )
    connection.commit()
    connection.close()

    evidence, coverage = standards_evidence(database, {1})

    assert coverage == {
        "status": "complete",
        "activeMembersRequested": 1,
        "membersWithAssessmentEvidence": 1,
        "assessments": 1,
        "exerciseObservations": 1,
        "reason": None,
    }
    assert evidence[0]["trainerizeUserId"] == 1
    assert evidence[0]["bodyWeight"]["kg"] == 60
    assert evidence[0]["observations"][0]["exerciseName"] == (
        "ATG Split Squat"
    )
    assert "standard" not in evidence[0]["observations"][0]
