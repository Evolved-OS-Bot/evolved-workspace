from retention_intelligence.trainerize_usage import tracked_workout_dates


def test_only_tracked_regular_workouts_count():
    payload = {
        "calendar": [
            {
                "date": "2026-07-20",
                "items": [
                    {"type": "workoutRegular", "status": "tracked"},
                    {"type": "workoutRegular", "status": "scheduled"},
                    {"type": "cardio", "status": "tracked"},
                ],
            },
            {
                "date": "2026-07-21",
                "items": [
                    {
                        "type": "workoutRegular",
                        "detail": {"status": "completed"},
                    }
                ],
            },
        ]
    }
    assert [item.isoformat() for item in tracked_workout_dates(payload)] == [
        "2026-07-20",
        "2026-07-21",
    ]
