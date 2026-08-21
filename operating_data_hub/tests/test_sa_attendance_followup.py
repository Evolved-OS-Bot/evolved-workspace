from datetime import UTC, datetime, timedelta

from operating_data_hub.sa_attendance_followup import (
    TASK_MARKER_PREFIX,
    build_followup_plan,
    execute_followup_plan,
    next_business_day,
)
from operating_data_hub.trainerize_attendance import attach_evidence


NOW = datetime(2026, 7, 30, 2, 0, tzinfo=UTC)  # Thursday noon Brisbane


def row(
    appointment_id: str,
    *,
    state: str = "elapsed_confirmed",
    start_at: datetime | None = None,
    assigned_user_id: str = "coach-1",
):
    start = start_at or datetime(2026, 7, 29, 4, 0, tzinfo=UTC)
    return {
        "appointment_id": appointment_id,
        "contact_id": f"contact-{appointment_id}",
        "start_at": start.isoformat(),
        "end_at": (start + timedelta(hours=1)).isoformat(),
        "reconciliation_state": state,
        "assigned_user_id": assigned_user_id,
    }


def test_next_business_day_skips_weekend():
    assert next_business_day(datetime(2026, 7, 31).date()).isoformat() == (
        "2026-08-03"
    )


def test_coach_is_first_owner_and_admin_escalates_next_business_day():
    before_escalation = datetime(2026, 7, 29, 23, 30, tzinfo=UTC)
    early = build_followup_plan(
        [row("one")],
        now=before_escalation,
        admin_user_id="admin-1",
    )
    assert [item["stage"] for item in early["actions"]] == ["coach"]
    assert early["actions"][0]["assigned_to"] == "coach-1"

    escalated = build_followup_plan(
        [row("one")],
        now=NOW,
        admin_user_id="admin-1",
    )
    assert [item["stage"] for item in escalated["actions"]] == [
        "coach",
        "admin",
    ]
    assert escalated["actions"][1]["assigned_to"] == "admin-1"


def test_missing_coach_routes_first_action_to_admin_without_guessing():
    plan = build_followup_plan(
        [row("one", assigned_user_id="")],
        now=NOW,
        admin_user_id="admin-1",
    )
    assert plan["actions"][0]["assigned_to"] == "admin-1"
    assert plan["actions"][0]["routing_exception"] is True


def test_resolved_and_old_rows_do_not_create_tasks():
    plan = build_followup_plan(
        [
            row("resolved", state="terminal_consistent"),
            row(
                "old",
                start_at=datetime(2026, 7, 1, 4, 0, tzinfo=UTC),
            ),
        ],
        now=NOW,
        admin_user_id="admin-1",
        lookback_days=7,
    )
    assert plan["actions"] == []
    assert plan["resolved"][0]["appointment_id"] == "resolved"


class FakeClient:
    write_enabled = True

    def __init__(self, tasks=None):
        self.tasks = tasks or {}
        self.created = []
        self.updated = []
        self.completed = []

    def list_contact_tasks(self, contact_id):
        return self.tasks.setdefault(contact_id, [])

    def create_contact_task(self, contact_id, **payload):
        task = {"id": f"new-{len(self.created)}", **payload}
        self.created.append((contact_id, payload))
        return {"task": task}

    def update_contact_task(self, contact_id, task_id, **payload):
        self.updated.append((contact_id, task_id, payload))
        return {"task": {"id": task_id, **payload}}

    def complete_contact_task(self, contact_id, task_id):
        self.completed.append((contact_id, task_id))
        return {}


def test_execution_is_idempotent_and_closes_governed_tasks():
    active = build_followup_plan(
        [row("one")],
        now=NOW,
        admin_user_id="admin-1",
    )
    client = FakeClient()
    first = execute_followup_plan(client, active, write_enabled=True)
    assert first["created"] == 2
    second = execute_followup_plan(client, active, write_enabled=True)
    assert second["created"] == 0
    assert second["already_open"] == 2

    resolved = build_followup_plan(
        [row("one", state="terminal_consistent")],
        now=NOW,
        admin_user_id="admin-1",
    )
    closed = execute_followup_plan(client, resolved, write_enabled=True)
    assert closed["completed"] == 2


def test_existing_workflow_task_is_adopted_not_duplicated():
    active = build_followup_plan(
        [row("one")],
        now=datetime(2026, 7, 29, 23, 30, tzinfo=UTC),
        admin_user_id="admin-1",
    )
    contact_id = "contact-one"
    client = FakeClient(
        {
            contact_id: [
                {
                    "id": "legacy-1",
                    "title": "SA Feedback: Prospect",
                    "body": "old workflow task",
                    "dueDate": "2026-07-29T23:00:00Z",
                    "assignedTo": "coach-1",
                    "completed": False,
                }
            ]
        }
    )
    result = execute_followup_plan(client, active, write_enabled=True)
    assert result["created"] == 0
    assert result["adopted"] == 1
    assert TASK_MARKER_PREFIX in client.updated[0][2]["body"]


def test_trainerize_verified_assessment_is_resolved_before_task_creation():
    plan = build_followup_plan(
        [row("one")],
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
                    "kind": "strength_assessment",
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

    result = execute_followup_plan(
        client,
        plan,
        write_enabled=True,
    )

    assert result["created"] == 0
    assert result["trainerize_precheck"]["resolved"] == 1
    assert client.created == []
