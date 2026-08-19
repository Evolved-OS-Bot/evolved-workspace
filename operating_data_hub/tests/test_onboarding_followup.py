from datetime import UTC, datetime, timedelta

from operating_data_hub.onboarding_followup import (
    build_onboarding_followup_plan,
    execute_onboarding_followup_plan,
)
from operating_data_hub.trainerize_attendance import attach_evidence


NOW = datetime(2026, 7, 30, 2, 0, tzinfo=UTC)


def event(
    appointment_id: str,
    *,
    status: str = "confirmed",
    assigned_user_id: str = "coach-1",
):
    start = datetime(2026, 7, 29, 4, 0, tzinfo=UTC)
    return {
        "appointment_id": appointment_id,
        "contact_id": f"contact-{appointment_id}",
        "scheduled_start": start.isoformat(),
        "scheduled_end": (start + timedelta(minutes=30)).isoformat(),
        "appointment_type": "onboarding",
        "status": status,
        "assigned_user_id": assigned_user_id,
    }


def case(appointment_id: str):
    return {
        "first_onboarding_appointment_id": appointment_id,
        "completion_state": "elapsed_unverified",
    }


def test_elapsed_confirmed_onboarding_routes_to_coach_then_admin():
    plan = build_onboarding_followup_plan(
        [case("one")],
        [event("one")],
        now=NOW,
        admin_user_id="admin-1",
    )
    assert [row["stage"] for row in plan["actions"]] == ["coach", "admin"]
    assert plan["actions"][0]["assigned_to"] == "coach-1"
    assert plan["actions"][1]["assigned_to"] == "admin-1"


def test_missing_trainer_routes_to_admin_without_guessing():
    plan = build_onboarding_followup_plan(
        [case("one")],
        [event("one", assigned_user_id="")],
        now=NOW,
        admin_user_id="admin-1",
    )
    assert plan["actions"][0]["assigned_to"] == "admin-1"
    assert plan["actions"][0]["routing_exception"] is True


def test_terminal_outcome_resolves_governed_tasks():
    plan = build_onboarding_followup_plan(
        [case("one")],
        [event("one", status="showed")],
        now=NOW,
        admin_user_id="admin-1",
    )
    assert plan["actions"] == []
    assert plan["resolved"][0]["appointment_id"] == "one"


class FakeClient:
    write_enabled = True

    def __init__(self):
        self.tasks = {}
        self.created = []
        self.completed = []

    def list_contact_tasks(self, contact_id):
        return self.tasks.setdefault(contact_id, [])

    def create_contact_task(self, contact_id, **payload):
        task = {
            "id": f"new-{len(self.created)}",
            "completed": False,
            **payload,
        }
        self.created.append((contact_id, payload))
        return {"task": task}

    def complete_contact_task(self, contact_id, task_id):
        self.completed.append((contact_id, task_id))
        return {}


def test_execution_is_idempotent_and_closes_tasks_after_outcome():
    active = build_onboarding_followup_plan(
        [case("one")],
        [event("one")],
        now=NOW,
        admin_user_id="admin-1",
    )
    client = FakeClient()
    first = execute_onboarding_followup_plan(
        client,
        active,
        write_enabled=True,
    )
    assert first["created"] == 1
    assert first["deferred"] == 1
    second = execute_onboarding_followup_plan(
        client,
        active,
        write_enabled=True,
    )
    assert second["created"] == 1
    assert second["already_open"] == 1
    assert second["deferred"] == 0

    resolved = build_onboarding_followup_plan(
        [case("one")],
        [event("one", status="showed")],
        now=NOW,
        admin_user_id="admin-1",
    )
    closed = execute_onboarding_followup_plan(
        client,
        resolved,
        write_enabled=True,
    )
    assert closed["completed"] == 2


def test_trainerize_verified_onboarding_is_resolved_before_task_creation():
    plan = build_onboarding_followup_plan(
        [case("one")],
        [event("one")],
        now=NOW,
        admin_user_id="admin-1",
    )
    plan = attach_evidence(
        plan,
        {
            "source_status": "complete",
            "counts": {
                "requested": 1,
                "verified_showed": 1,
                "unresolved": 0,
            },
            "results": [
                {
                    "appointment_id": "one",
                    "contact_id": "contact-one",
                    "target_date": "2026-07-29",
                    "kind": "onboarding",
                    "decision": "verified_showed",
                    "matching_sessions": [
                        {"session_id": "trainerize-1"}
                    ],
                }
            ],
        },
    )
    client = FakeClient()
    status = "confirmed"

    def get_appointment_state(appointment_id):
        return {
            "appointment_id": appointment_id,
            "contact_id": "contact-one",
            "start_at": "2026-07-29T04:00:00+00:00",
            "status": status,
        }

    def update(event, evidence, *, idempotency_key):
        nonlocal status
        status = "showed"
        return {}

    client.get_appointment_state = get_appointment_state
    client.update_trainerize_verified_to_showed = update

    result = execute_onboarding_followup_plan(
        client,
        plan,
        write_enabled=True,
    )

    assert result["created"] == 0
    assert result["trainerize_precheck"]["resolved"] == 1
    assert client.created == []
