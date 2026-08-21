from __future__ import annotations

from datetime import UTC, date, datetime, time, timedelta
from typing import Any, Iterable

from .config import BRISBANE_TZ
from .sa_attendance import GHLAttendanceClient, parse_datetime
from .trainerize_attendance import resolve_verified_appointments


TASK_MARKER_PREFIX = "Onboarding outcome closure key:"


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


def build_onboarding_followup_plan(
    onboarding_cases: Iterable[dict[str, Any]],
    onboarding_events: Iterable[dict[str, Any]],
    *,
    now: datetime,
    admin_user_id: str,
    lookback_days: int = 14,
) -> dict[str, Any]:
    observed_at = now.astimezone(UTC)
    events = {
        str(row.get("appointment_id") or ""): dict(row)
        for row in onboarding_events
        if row.get("appointment_id")
    }
    actions: list[dict[str, Any]] = []
    resolved: list[dict[str, str]] = []
    for case in onboarding_cases:
        appointment_id = str(
            case.get("first_onboarding_appointment_id") or ""
        ).strip()
        if not appointment_id:
            continue
        event = events.get(appointment_id)
        if not event:
            continue
        contact_id = str(event.get("contact_id") or "").strip()
        if not contact_id:
            continue
        end_at = parse_datetime(event["scheduled_end"], "scheduled_end")
        if end_at < observed_at - timedelta(days=lookback_days):
            continue
        if event.get("status") != "confirmed" or end_at >= observed_at:
            if event.get("status") in {
                "showed",
                "no_show",
                "cancelled",
                "invalid",
            }:
                resolved.append(
                    {
                        "appointment_id": appointment_id,
                        "contact_id": contact_id,
                    }
                )
            continue
        local_day = parse_datetime(
            event["scheduled_start"], "scheduled_start"
        ).astimezone(BRISBANE_TZ).date()
        followup_day = next_business_day(local_day)
        coach_id = str(event.get("assigned_user_id") or "").strip()
        base = {
            "appointment_id": appointment_id,
            "contact_id": contact_id,
            "scheduled_start": event["scheduled_start"],
            "appointment_type": event["appointment_type"],
            "followup_day": followup_day.isoformat(),
        }
        actions.append(
            {
                **base,
                "stage": "coach",
                "assigned_to": coach_id or admin_user_id,
                "due_at": _local_due(followup_day, 9),
                "marker": (
                    f"{TASK_MARKER_PREFIX} {appointment_id}:coach:v1"
                ),
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
            "routing_exceptions": sum(
                bool(row["routing_exception"]) for row in actions
            ),
            "resolved": len(resolved),
        },
    }


def _task_text(action: dict[str, Any]) -> tuple[str, str]:
    start = parse_datetime(
        action["scheduled_start"], "scheduled_start"
    ).astimezone(BRISBANE_TZ)
    when = start.strftime("%A %-d %B at %-I:%M %p")
    if action["stage"] == "admin":
        title = "ONBOARDING ESCALATION: Outcome still missing"
        opening = (
            "The trainer follow-up has not produced a recorded onboarding "
            "outcome by the next business day."
        )
    else:
        title = "ONBOARDING: Record the session outcome"
        opening = (
            "This onboarding or first PT session has ended but its outcome "
            "is still recorded as Confirmed."
        )
    body = (
        f"{opening}\n\n"
        f"Appointment: {when}\n"
        f"Appointment ID: {action['appointment_id']}\n\n"
        "Update the GHL appointment using the one outcome that actually "
        "occurred:\n"
        "1. Delivered: mark the appointment Showed.\n"
        "2. Did not attend: mark the appointment No show.\n"
        "3. Cancelled: mark or retain the appointment as Cancelled.\n\n"
        "Do not infer No show from a missing update. If another trainer "
        "delivered the session, tell Admin Eve who delivered it.\n\n"
        f"{action['marker']}"
    )
    return title, body


def _is_open(task: dict[str, Any]) -> bool:
    return not bool(task.get("completed"))


def execute_onboarding_followup_plan(
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
        raise RuntimeError("GHL onboarding task writes are disabled")
    created = 0
    already_open = 0
    deferred = 0
    completed = 0
    task_cache: dict[str, list[dict[str, Any]]] = {}
    created_task_ids: set[str] = set()
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
        if action["stage"] == "admin":
            coach_marker = (
                f"{TASK_MARKER_PREFIX} "
                f"{action['appointment_id']}:coach:v1"
            )
            prior_coach_task = next(
                (
                    task
                    for task in contact_tasks
                    if coach_marker in str(task.get("body") or "")
                    and _is_open(task)
                    and str(task.get("id") or "") not in created_task_ids
                ),
                None,
            )
            if prior_coach_task is None:
                deferred += 1
                continue
        if any(
            action["marker"] in str(task.get("body") or "")
            and _is_open(task)
            for task in contact_tasks
        ):
            already_open += 1
            continue
        title, body = _task_text(action)
        response = client.create_contact_task(
            action["contact_id"],
            title=title,
            body=body,
            due_at=action["due_at"],
            assigned_to=action["assigned_to"],
        )
        created_task = response.get("task") or response
        contact_tasks.append(created_task)
        if created_task.get("id"):
            created_task_ids.add(str(created_task["id"]))
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
        "already_open": already_open,
        "deferred": deferred,
        "completed": completed,
        "trainerize_precheck": {
            **evidence_resolution["counts"],
            "audit": evidence_resolution["audit"],
        },
    }
