import unittest
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory

from extract_strength_assessments import (
    body_weight_timing_quality,
    calendar_windows,
    connect_database,
    detect_schema_version,
    extract_body_weight,
    is_strength_assessment,
)


class StrengthAssessmentExtractorTests(unittest.TestCase):
    def test_identifies_assessment_by_title(self):
        self.assertTrue(
            is_strength_assessment(
                {"id": 1, "title": "Women's Standard Strength Assessment"}
            )
        )
        self.assertFalse(is_strength_assessment({"id": 2, "title": "Sculpt & Strength"}))

    def test_identifies_assessment_by_workout_id(self):
        self.assertTrue(
            is_strength_assessment(
                {"id": 1, "title": "Renamed", "detail": {"workoutID": 183960272}}
            )
        )

    def test_detects_legacy_schema(self):
        workout = {
            "exercises": [
                {
                    "def": {
                        "name": "Farmer Walk",
                        "target": "Using 20% of the individual's body weight",
                        "side": None,
                    }
                }
            ]
        }
        self.assertEqual(detect_schema_version(workout), "legacy_combined_v1")

    def test_detects_current_schema(self):
        workout = {
            "exercises": [
                {"def": {"name": "ATG Split Squat", "side": "right"}},
                {"def": {"name": "Side Plank", "side": "left"}},
            ]
        }
        self.assertEqual(detect_schema_version(workout), "current_independent_v2")

    def test_unknown_schema_is_explicit(self):
        self.assertEqual(detect_schema_version({"exercises": []}), "unknown")

    def test_calendar_windows_split_years(self):
        windows = list(calendar_windows(date(2025, 11, 1), date(2026, 2, 1)))
        self.assertEqual(
            windows,
            [
                (date(2025, 11, 1), date(2025, 12, 31)),
                (date(2026, 1, 1), date(2026, 2, 1)),
            ],
        )

    def test_body_weight_timing_quality(self):
        self.assertEqual(body_weight_timing_quality(0), "Same day")
        self.assertEqual(body_weight_timing_quality(-7), "Within 7 days")
        self.assertEqual(body_weight_timing_quality(30), "Within 30 days")
        self.assertEqual(body_weight_timing_quality(31), "Not suitable")
        self.assertEqual(body_weight_timing_quality(None), "Not available")

    def test_extract_body_weight(self):
        self.assertEqual(
            extract_body_weight(
                {"bodyMeasures": {"date": "2026-07-20", "bodyWeight": 67.4}}
            ),
            (67.4, "2026-07-20"),
        )

    def test_baseline_view_selects_one_earliest_tracked_assessment(self):
        with TemporaryDirectory() as directory:
            connection = connect_database(Path(directory) / "test.sqlite")
            connection.execute(
                """
                INSERT INTO extraction_runs (
                    id, started_at, start_date, end_date, status
                ) VALUES (1, '2026-01-01', '2026-01-01', '2026-12-31', 'complete')
                """
            )
            connection.execute(
                """
                INSERT INTO clients (
                    trainerize_user_id, sex, is_test_client, updated_at
                ) VALUES (10, 'female', 0, '2026-01-01')
                """
            )
            for workout_id, assessment_date, status in (
                (102, "2026-02-01", "tracked"),
                (101, "2026-01-01", "tracked"),
                (100, "2025-12-01", "scheduled"),
            ):
                connection.execute(
                    """
                    INSERT INTO assessments (
                        daily_workout_id, trainerize_user_id, assessment_date,
                        status, schema_version, extraction_run_id, raw_json
                    ) VALUES (?, 10, ?, ?, 'legacy_combined_v1', 1, '{}')
                    """,
                    (workout_id, assessment_date, status),
                )
            row = connection.execute(
                "SELECT daily_workout_id FROM baseline_assessments"
            ).fetchone()
            self.assertEqual(row[0], 101)
            connection.close()


if __name__ == "__main__":
    unittest.main()
