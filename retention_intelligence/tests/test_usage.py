from datetime import date

from retention_intelligence.trainerize_usage import (
    retained_past_class_booking_dates,
    tracked_workout_dates,
)


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


def test_retained_past_group_class_booking_is_attendance_proxy():
    payload = {
        "calendar": [
            {
                "date": "2026-07-20",
                "items": [
                    {
                        "type": "appointmentV2",
                        "status": "scheduled",
                        "detail": {
                            "isGroupAppointment": True,
                            "eventCategory": "class",
                        },
                    },
                    {
                        "type": "appointmentV2",
                        "detail": {
                            "isGroupAppointment": False,
                            "eventCategory": "appointment",
                        },
                    },
                ],
            },
            {
                "date": "2026-07-28",
                "items": [
                    {
                        "type": "appointmentV2",
                        "detail": {
                            "isGroupAppointment": True,
                            "eventCategory": "class",
                        },
                    }
                ],
            },
        ]
    }

    observed = retained_past_class_booking_dates(
        payload,
        today=date(2026, 7, 26),
    )

    assert [item.isoformat() for item in observed] == ["2026-07-20"]
