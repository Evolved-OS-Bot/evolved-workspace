from __future__ import annotations

from datetime import UTC, date, datetime, time, timedelta
from typing import Any, Iterable

from .config import BRISBANE_TZ
from .sa_attendance import GHLAttendanceClient, parse_datetime
from .trainerize_attendance import resolve_verified_appointments


TASK_MARKER_PREFIX = "SA attendance closure key:"
FEEDBACK_FORM_URL = (
    "https://links.theevolvedgym.com.au/widget/form/Z83KtjAPMclhe8bsFJwS"
)


def next_business_day(value: date) -> date:
    candidate = value + timedelta(days=1)
    while candidate.weekday() >= 5:
        candidate += timedelta(days=1)
    return candidate


def _local_due(value: date, hour: int) -> str:
    return (
        datetime.combine(value, time(hour=hour), tzinfo=BRISBANE_TZ)
        .astimezone(UTC)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def build_followup_plan(
    rows: Iterable[dict[str, Any]],
    *,
    now: datetime,
    admin_user_id: str,
    lookback_days: int = 7,
) -> dict[str, Any]:
    observed_at = now.astimezone(UTC)
    actions: list[dict[str, Any]] = []
    resolved: list[dict[str, str]] = []
    for source in rows:
        row = dict(source)
        appointment_id = str(row.get("appointment_id") or "").strip()
        contact_id = str(row.get("contact_id") or "").strip()
        if not appointment_id or not contact_id:
            continue
        end_at = parse_datetime(row["end_at"], "end_at")
        local_day = parse_datetime(row["start_at"], "start_at").astimezone(
            BRISBANE_TZ
        ).date()
        if end_at < observed_at - timedelta(days=lookback_days):
            continue
        if row.get("reconciliation_state") != "elapsed_confirmed":
            resolved.append(
                {
                    "appointment_id": appointment_id,
                    "contact_id": contact_id,
                }
            )
            continue
        coach_id = str(row.get("assigned_user_id") or "").strip()
        followup_day = next_business_day(local_day)
        base = {
            "appointment_id": appointment_id,
            "contact_id": contact_id,
            "scheduled_start": row["start_at"],
            "followup_day": followup_day.isoformat(),
        }
        actions.append(
            {
                **base,
                "stage": "coach",
                "assigned_to": coach_id or admin_user_id,
                "due_at": _local_due(followup_day, 9),
                "marker": f"{TASK_MARKER_PREFIX} {appointment_id}:coach:v1",
                "routing_exception": not bool(coach_id),
            }
        )
        escalation_at = datetime.combine(
            followup_day,
            time(hour=10),
            tzinfo=BRISBANE_TZ,
        ).astimezone(UTC)
        if observed_at >= escalation_at:
            actions.append(
                {
                    **base,
                    "stage": "admin",
                    "assigned_to": admin_user_id,
                    "due_at": _local_due(followup_day, 17),
                    "marker": (
                        f"{TASK_MARKER_PREFIX} {appointment_id}:admin:v1"
                    ),
                    "routing_exception": False,
                }
            )
    return {
        "observed_at": observed_at.isoformat(),
        "actions": actions,
        "resolved": resolved,
        "counts": {
            "coach_due": sum(row["stage"] == "coach" for row in actions),
            "admin_due": sum(row["stage"] == "admin" for row in actions),
            "resolved": len(resolved),
        },
    }


def _task_text(action: dict[str, Any]) -> tuple[str, str]:
    start = parse_datetime(
        action["scheduled_start"], "scheduled_start"
    ).astimezone(BRISBANE_TZ)
    when = start.strftime("%A %-d %B at %-I:%M %p")
    if action["stage"] == "admin":
        title = "SA ATTENDANCE ESCALATION: Outcome still missing"
        opening = (
            "The coach follow-up has not produced a recorded attendance "
            "outcome by the next business day."
        )
    else:
        title = "SA ATTENDANCE: Record the assessment outcome"
        opening = (
            "This Strength Assessment has ended but its attendance outcome "
            "is still recorded as Confirmed."
        )
    body = (
        f"{opening}\n\n"
        f"Appointment: {when}\n"
        f"Appointment ID: {action['appointment_id']}\n\n"
        "Close it using the one outcome that actually occurred:\n"
        f"1. Delivered: submit the Consultant Feedback form at "
        f"{FEEDBACK_FORM_URL} and mark the appointment Showed.\n"
        "2. Did not attend: mark the appointment No show.\n"
        "3. Cancelled: mark or retain the appointment as Cancelled.\n\n"
        "Do not infer No show from missing feedback. If another coach "
        "covered the assessment, tell Admin Eve who delivered it.\n\n"
        f"{action['marker']}"
    )
    return title, body


def _is_open(task: dict[str, Any]) -> bool:
    return not bool(task.get("completed"))


def _matches_legacy_task(
    task: dict[str, Any],
    action: dict[str, Any],
) -> bool:
    if not _is_open(task) or not task.get("id"):
        return False
    title = str(task.get("title") or "").strip().lower()
    expected_prefix = (
        "sa feedback:"
        if action["stage"] == "coach"
        else "chase : sa feedback not submitted"
    )
    if not title.startswith(expected_prefix):
        return False
    if str(task.get("assignedTo") or "") != action["assigned_to"]:
        return False
    due_at = str(task.get("dueDate") or "").strip()
    if not due_at:
        return False
    try:
        due_day = parse_datetime(due_at, "dueDate").astimezone(
            BRISBANE_TZ
        ).date()
    except ValueError:
        return False
    return due_day.isoformat() == action["followup_day"]


def execute_followup_plan(
    client: GHLAttendanceClient,
    plan: dict[str, Any],
    *,
    write_enabled: bool,
) -> dict[str, Any]:
    evidence_ids = {
        row["appointment_id"]
        for row in plan["actions"]
        if (row.get("trainerize_evidence") or {}).get("decision")
        == "verified_showed"
    }
    proposed = sum(
        row["appointment_id"] not in evidence_ids
        for row in plan["actions"]
    )
    if not write_enabled:
        return {
            "mode": "preview",
            "proposed": proposed,
            "created": 0,
            "already_open": 0,
            "completed": 0,
            "trainerize_verified": len(evidence_ids),
        }
    if not client.write_enabled:
        raise RuntimeError("GHL attendance task writes are disabled")
    created = 0
    adopted = 0
    already_open = 0
    completed = 0
    task_cache: dict[str, list[dict[str, Any]]] = {}
    evidence_resolution = resolve_verified_appointments(client, plan)
    evidence_resolved_ids = evidence_resolution["resolved_ids"]
    proposed = sum(
        row["appointment_id"] not in evidence_resolved_ids
        for row in plan["actions"]
    )

    def tasks(contact_id: str) -> list[dict[str, Any]]:
        if contact_id not in task_cache:
            task_cache[contact_id] = client.list_contact_tasks(contact_id)
        return task_cache[contact_id]

    for action in plan["actions"]:
        if action["appointment_id"] in evidence_resolved_ids:
            continue
        contact_tasks = tasks(action["contact_id"])
        if any(
            action["marker"] in str(task.get("body") or "")
            and _is_open(task)
            for task in contact_tasks
        ):
            already_open += 1
            continue
        title, body = _task_text(action)
        legacy_task = next(
            (
                task
                for task in contact_tasks
                if _matches_legacy_task(task, action)
            ),
            None,
        )
        if legacy_task is not None:
            client.update_contact_task(
                action["contact_id"],
                str(legacy_task["id"]),
                title=title,
                body=body,
                due_at=action["due_at"],
                assigned_to=action["assigned_to"],
            )
            legacy_task.update(
                {
                    "title": title,
                    "body": body,
                    "dueDate": action["due_at"],
                    "assignedTo": action["assigned_to"],
                }
            )
            adopted += 1
            continue
        response = client.create_contact_task(
            action["contact_id"],
            title=title,
            body=body,
            due_at=action["due_at"],
            assigned_to=action["assigned_to"],
        )
        contact_tasks.append(response.get("task") or response)
        created += 1

    resolved_rows = [
        *(plan["resolved"]),
        *(evidence_resolution["resolved"]),
    ]
    for row in resolved_rows:
        for task in tasks(row["contact_id"]):
            body = str(task.get("body") or "")
            if (
                f"{TASK_MARKER_PREFIX} {row['appointment_id']}:" in body
                and _is_open(task)
                and task.get("id")
            ):
                client.complete_contact_task(
                    row["contact_id"], str(task["id"])
                )
                task["completed"] = True
                completed += 1
    return {
        "mode": "live",
        "proposed": proposed,
        "created": created,
        "adopted": adopted,
        "already_open": already_open,
        "completed": completed,
        "trainerize_precheck": {
            **evidence_resolution["counts"],
            "audit": evidence_resolution["audit"],
        },
    }
