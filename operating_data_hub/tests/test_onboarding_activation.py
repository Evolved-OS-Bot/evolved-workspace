from datetime import UTC, datetime

from operating_data_hub.onboarding_activation import (
    build_onboarding_activation_evidence,
)


class TrainerizeClient:
    def attendance_clients(self):
        return [
            {
                "id": 41,
                "email": "member@example.com",
                "firstName": "Test",
                "lastName": "Member",
            }
        ]

    def calendar(self, user_id, start_date, end_date):
        assert user_id == 41
        return [
            {
                "date": f"2026-07-{day:02d}",
                "items": [
                    {
                        "id": day,
                        "type": "workoutRegular",
                        "status": "tracked",
                        "title": (
                            "On Boarding Session"
                            if day == 3
                            else "Training Program"
                        ),
                    }
                ],
            }
            for day in (3, 5, 7)
        ]


class GHLClient:
    def list_contact_tasks(self, contact_id):
        assert contact_id == "contact-1"
        return [
            {
                "id": "task-1",
                "title": "Day 7 positive reply: respond and verify",
                "completed": True,
                "dueDate": "2026-07-09T14:00:00.000Z",
            }
        ]


def test_successful_first_week_requires_all_three_evidence_components():
    result = build_onboarding_activation_evidence(
        trainerize_client=TrainerizeClient(),
        ghl_client=GHLClient(),
        onboarding_cases=[
            {
                "sale_id": "sale-1",
                "contact_id": "contact-1",
                "sold_at": "2026-07-01T01:00:00+00:00",
                "entitlement_type": "kickstart",
                "first_onboarding_completed_at": (
                    "2026-07-02T02:00:00+00:00"
                ),
            }
        ],
        identities={
            "contact-1": {
                "email": "member@example.com",
                "name": "Test Member",
            }
        },
        observed_at=datetime(2026, 7, 15, tzinfo=UTC),
    )

    case = result["cases"][0]
    assert case["requirements"] == {
        "onboarding_attended": True,
        "three_training_records": True,
        "first_week_confirmed": True,
    }
    assert case["activation_days"] == 9
    assert result["summary"]["activated"] == 1


def test_open_positive_task_does_not_confirm_first_week():
    class OpenTaskGHLClient:
        def list_contact_tasks(self, contact_id):
            return [
                {
                    "id": "task-1",
                    "title": "Day 7 positive reply: respond and verify",
                    "completed": False,
                    "dueDate": "2026-07-09T14:00:00.000Z",
                }
            ]

    result = build_onboarding_activation_evidence(
        trainerize_client=TrainerizeClient(),
        ghl_client=OpenTaskGHLClient(),
        onboarding_cases=[
            {
                "sale_id": "sale-1",
                "contact_id": "contact-1",
                "sold_at": "2026-07-01T01:00:00+00:00",
                "entitlement_type": "kickstart",
                "first_onboarding_completed_at": (
                    "2026-07-02T02:00:00+00:00"
                ),
            }
        ],
        identities={"contact-1": {"email": "member@example.com"}},
        observed_at=datetime(2026, 7, 15, tzinfo=UTC),
    )

    case = result["cases"][0]
    assert case["requirements"]["first_week_confirmed"] is False
    assert case["activation_at"] is None
    assert result["summary"]["activated"] == 0


def test_exact_date_tracked_onboarding_can_prove_attendance():
    result = build_onboarding_activation_evidence(
        trainerize_client=TrainerizeClient(),
        ghl_client=GHLClient(),
        onboarding_cases=[
            {
                "sale_id": "sale-1",
                "contact_id": "contact-1",
                "sold_at": "2026-07-01T01:00:00+00:00",
                "entitlement_type": "kickstart",
                "first_onboarding_scheduled_at": (
                    "2026-07-03T02:00:00+00:00"
                ),
                "first_onboarding_completed_at": None,
            }
        ],
        identities={"contact-1": {"email": "member@example.com"}},
        observed_at=datetime(2026, 7, 15, tzinfo=UTC),
    )

    case = result["cases"][0]
    assert case["requirements"]["onboarding_attended"] is True
    assert case["onboarding_attendance_source"] == (
        "trainerize_exact_date_tracked_session"
    )
