import unittest
from datetime import date
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from trainerize_performance_reporting import (
    _explicit_class_outcome,
    _trainerize_local_datetime,
    build_member_rows,
    canonical_movement,
    estimated_one_rep_max,
)


class TrainerizePerformanceReportingTests(unittest.TestCase):
    def test_trainerize_utc_start_resolves_brisbane_service_date(self):
        observed = _trainerize_local_datetime("2026-07-19 19:30:00")
        self.assertEqual(observed.isoformat(), "2026-07-20T05:30:00+10:00")

    def test_false_check_in_does_not_become_no_show(self):
        self.assertEqual(
            _explicit_class_outcome(
                "scheduled",
                {"checkedIn": False},
            ),
            (None, None, False),
        )

    def test_only_explicit_terminal_status_proves_outcome(self):
        self.assertEqual(
            _explicit_class_outcome("cancelled", {}),
            ("cancelled", "trainerize_terminal_status", None),
        )
        self.assertEqual(
            _explicit_class_outcome("no_show", {}),
            ("no_show", "trainerize_terminal_status", None),
        )
        self.assertEqual(
            _explicit_class_outcome("scheduled", {"checkedIn": True}),
            ("attended", "trainerize_check_in", True),
        )

    def test_nexus_aliases_share_one_canonical_movement(self):
        self.assertEqual(
            canonical_movement("Barbell Front Squat"), "Nexus Point Squat"
        )
        self.assertEqual(
            canonical_movement("Barbell Back Squat"), "Nexus Point Squat"
        )
        self.assertEqual(canonical_movement("Nexus Point Squat"), "Nexus Point Squat")

    def test_estimated_one_rep_max_rejects_invalid_sets(self):
        self.assertIsNone(estimated_one_rep_max(0, 10))
        self.assertIsNone(estimated_one_rep_max(50, 25))
        self.assertAlmostEqual(estimated_one_rep_max(50, 10), 66.6666, places=3)

    def test_remarkable_candidate_requires_training_volume(self):
        roster = {
            1: {
                "first_name": "Test",
                "last_name": "Member",
                "email": "test@example.com",
                "client_type": "Full Access",
            }
        }
        strengths = {
            1: {
                "Bench Press": {
                    "improvement_percent": 30.0,
                    "baseline_e1rm": 30,
                    "current_e1rm": 39,
                }
            }
        }
        low_volume = {
            1: {
                "workouts_total": 20,
                "workouts_365d": 20,
                "workouts_30d": 3,
                "workouts_90d": 8,
            }
        }
        rows = build_member_rows(
            roster, low_volume, strengths, {}, today=date(2026, 7, 23)
        )
        self.assertFalse(rows[0]["remarkable_candidate"])

        high_volume = {
            1: {
                "workouts_total": 80,
                "workouts_365d": 80,
                "workouts_30d": 8,
                "workouts_90d": 24,
            }
        }
        rows = build_member_rows(
            roster, high_volume, strengths, {}, today=date(2026, 7, 23)
        )
        self.assertTrue(rows[0]["remarkable_candidate"])


if __name__ == "__main__":
    unittest.main()
