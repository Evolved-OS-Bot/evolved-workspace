from __future__ import annotations

import hashlib
import logging
import time
from collections import Counter
from datetime import UTC, datetime, timedelta
from typing import Any, Iterable

import requests

from .config import BRISBANE_TZ


log = logging.getLogger(__name__)

ATTENDANCE_DEFINITION_VERSION = "sa-attendance-v2"
LEGACY_UNRECORDED_COACH = "Unrecorded - legacy form"
NORMALIZED_STATUSES = {
    "confirmed",
    "showed",
    "no_show",
    "cancelled",
    "invalid",
    "unknown",
}
TERMINAL_STATUSES = {"showed", "no_show", "cancelled", "invalid"}
SHOW_RATE_STATUSES = {"showed", "no_show"}
EXCLUDED_STATUSES = {"cancelled", "invalid"}


def parse_datetime(value: Any, field: str) -> datetime:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{field} is required")
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field} must be an ISO datetime") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"{field} must include a timezone")
    return parsed.astimezone(UTC)


def normalize_status(value: Any) -> str:
    text = " ".join(str(value or "").strip().lower().replace("-", " ").split())
    aliases = {
        "confirm": "confirmed",
        "confirmed": "confirmed",
        "show": "showed",
        "showed": "showed",
        "attended": "showed",
        "no show": "no_show",
        "noshow": "no_show",
        "cancel": "cancelled",
        "canceled": "cancelled",
        "cancelled": "cancelled",
        "invalid": "invalid",
    }
    return aliases.get(text, "unknown")


def normalise_event(raw: dict[str, Any], *, observed_at: datetime) -> dict[str, Any]:
    event_id = str(raw.get("id") or raw.get("appointment_id") or "").strip()
    contact_id = str(raw.get("contactId") or raw.get("contact_id") or "").strip()
    calendar_id = str(raw.get("calendarId") or raw.get("calendar_id") or "").strip()
    if not event_id or not contact_id or not calendar_id:
        raise ValueError("appointment requires event, contact and calendar IDs")
    start = parse_datetime(
        raw.get("startTime") or raw.get("start_at"),
        "start_at",
    )
    end = parse_datetime(
        raw.get("endTime") or raw.get("end_at"),
        "end_at",
    )
    if end <= start:
        raise ValueError("appointment end_at must be after start_at")
    return {
        "appointment_id": event_id,
        "contact_id": contact_id,
        "calendar_id": calendar_id,
        "booked_at": (
            parse_datetime(
                raw.get("dateAdded") or raw.get("booked_at"),
                "booked_at",
            ).isoformat()
            if raw.get("dateAdded") or raw.get("booked_at")
            else None
        ),
        "start_at": start.isoformat(),
        "end_at": end.isoformat(),
        "status": normalize_status(
            raw.get("appointmentStatus")
            or raw.get("appoinmentStatus")
            or raw.get("status")
        ),
        "assigned_user_id": str(
            raw.get("assignedUserId")
            or raw.get("assigned_user_id")
            or ""
        ).strip()
        or None,
        "updated_at": (
            parse_datetime(
                raw.get("updatedAt")
                or raw.get("dateUpdated")
                or raw.get("updated_at"),
                "updated_at",
            ).isoformat()
            if (
                raw.get("updatedAt")
                or raw.get("dateUpdated")
                or raw.get("updated_at")
            )
            else None
        ),
        "deleted": bool(raw.get("deleted", False)),
        "observed_at": observed_at.astimezone(UTC).isoformat(),
    }


def feedback_delivery_key(payload: dict[str, Any]) -> str:
    supplied = str(payload.get("delivery_key") or "").strip()
    if supplied:
        return supplied
    material = "|".join(
        [
            str(payload.get("contact_id") or "").strip(),
            str(payload.get("form_submission_id") or "").strip(),
            str(payload.get("submitted_at") or "").strip(),
        ]
    )
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def normalise_feedback_submission(
    raw: dict[str, Any],
    *,
    sales_outcome_field_id: str,
) -> dict[str, Any]:
    submission_id = str(raw.get("id") or "").strip()
    contact_id = str(raw.get("contactId") or "").strip()
    if not submission_id or not contact_id:
        raise ValueError("feedback submission requires submission and contact IDs")
    others = raw.get("others") if isinstance(raw.get("others"), dict) else {}
    return {
        "contact_id": contact_id,
        "form_submission_id": submission_id,
        "submitted_at": parse_datetime(
            raw.get("createdAt"), "createdAt"
        ).isoformat(),
        "sales_outcome": str(
            others.get(sales_outcome_field_id) or ""
        ).strip()
        or None,
        "delivered_by": LEGACY_UNRECORDED_COACH,
        "workflow_execution_id": None,
        "delivery_key": f"ghl-form:{submission_id}",
        "attribution_confidence": "assigned_calendar_trainer",
    }


def _eligible_feedback_candidates(
    feedback: dict[str, Any],
    events: Iterable[dict[str, Any]],
    *,
    matching_window: timedelta,
) -> list[dict[str, Any]]:
    submitted_at = parse_datetime(feedback["submitted_at"], "submitted_at")
    candidates = []
    for event in events:
        if event["contact_id"] != feedback["contact_id"]:
            continue
        if event.get("deleted") or event["status"] in EXCLUDED_STATUSES:
            continue
        end_at = parse_datetime(event["end_at"], "end_at")
        if end_at > submitted_at:
            continue
        if submitted_at - end_at > matching_window:
            continue
        candidates.append(event)
    candidates = sorted(
        candidates,
        key=lambda row: abs(
            (
                submitted_at
                - parse_datetime(row["end_at"], "end_at")
            ).total_seconds()
        ),
    )
    same_local_day = [
        row
        for row in candidates
        if parse_datetime(row["end_at"], "end_at")
        .astimezone(BRISBANE_TZ)
        .date()
        == submitted_at.astimezone(BRISBANE_TZ).date()
    ]
    return same_local_day or candidates


def reconcile_attendance(
    events: Iterable[dict[str, Any]],
    feedback_rows: Iterable[dict[str, Any]] = (),
    *,
    now: datetime | None = None,
    grace_period: timedelta = timedelta(minutes=60),
    matching_window: timedelta = timedelta(days=7),
    legacy_showed_before: datetime | None = None,
) -> dict[str, Any]:
    observed_now = (now or datetime.now(UTC)).astimezone(UTC)
    legacy_cutoff = (
        legacy_showed_before.astimezone(UTC)
        if legacy_showed_before is not None
        else None
    )
    event_rows = [dict(row) for row in events if not row.get("deleted")]
    feedback = [dict(row) for row in feedback_rows]
    feedback_by_event: dict[str, list[dict[str, Any]]] = {}
    feedback_exceptions: list[dict[str, Any]] = []

    for item in feedback:
        candidates = _eligible_feedback_candidates(
            item,
            event_rows,
            matching_window=matching_window,
        )
        if len(candidates) != 1:
            feedback_exceptions.append(
                {
                    "appointment_id": None,
                    "contact_id": item["contact_id"],
                    "code": (
                        "feedback_without_match"
                        if not candidates
                        else "ambiguous_feedback_match"
                    ),
                    "severity": "high",
                    "owner": "Admin Eve",
                    "form_submission_id": item["form_submission_id"],
                    "candidate_appointment_ids": [
                        row["appointment_id"] for row in candidates
                    ],
                }
            )
            continue
        feedback_by_event.setdefault(
            candidates[0]["appointment_id"], []
        ).append(item)

    reconciled: list[dict[str, Any]] = []
    exceptions = list(feedback_exceptions)
    for event in event_rows:
        matched_feedback = feedback_by_event.get(event["appointment_id"], [])
        status = event["status"]
        start_at = parse_datetime(event["start_at"], "start_at")
        end_at = parse_datetime(event["end_at"], "end_at")
        elapsed = observed_now > end_at + grace_period
        legacy_period = bool(legacy_cutoff and start_at < legacy_cutoff)
        state = "terminal_consistent" if status in TERMINAL_STATUSES else "pending"
        proposed_status = None
        exception_code = None
        canonical_status = status
        evidence_class = "explicit_ghl_status"

        if status == "confirmed" and matched_feedback:
            state = "feedback_closes_confirmed"
            proposed_status = "showed"
        elif status == "confirmed" and elapsed and legacy_period:
            state = "legacy_attended"
            canonical_status = "showed"
            evidence_class = "legacy_surviving_appointment"
        elif status == "confirmed" and elapsed:
            state = "elapsed_confirmed"
            exception_code = state
        elif status == "no_show" and matched_feedback:
            state = "terminal_conflict"
            exception_code = state
        elif status == "showed" and not matched_feedback:
            state = "terminal_consistent"
            exception_code = "showed_without_feedback"
        elif status == "unknown" and elapsed:
            state = "elapsed_confirmed"
            exception_code = "unknown_elapsed_status"

        row = {
            **event,
            "canonical_status": canonical_status,
            "reconciliation_state": state,
            "proposed_status": proposed_status,
            "attendance_evidence_class": evidence_class,
            "attendance_confidence": (
                "legacy_aggregate"
                if state == "legacy_attended"
                else "verified"
                if state == "terminal_consistent"
                else "high"
                if state == "feedback_closes_confirmed"
                else "unresolved"
                if state in {"terminal_conflict", "elapsed_confirmed"}
                else "medium"
            ),
            "show_rate_eligible": not legacy_period,
            "cancellation_rate_eligible": not legacy_period,
            "conversion_eligible": canonical_status == "showed",
            "legacy_cutoff_at": (
                legacy_cutoff.isoformat() if legacy_cutoff else None
            ),
            "feedback_submission_ids": [
                item["form_submission_id"] for item in matched_feedback
            ],
            "feedback_submitted_at": (
                max(
                    (
                        parse_datetime(item["submitted_at"], "submitted_at")
                        for item in matched_feedback
                    ),
                    default=None,
                ).isoformat()
                if matched_feedback
                else None
            ),
            "delivered_by": (
                event.get("assigned_user_name")
                or event.get("assigned_user_id")
                or None
            ),
            "trainer_attribution_source": "assigned_calendar_trainer",
            "exception_code": exception_code,
            "rule_version": ATTENDANCE_DEFINITION_VERSION,
        }
        reconciled.append(row)
        if exception_code:
            exceptions.append(
                {
                    "appointment_id": event["appointment_id"],
                    "contact_id": event["contact_id"],
                    "code": exception_code,
                    "severity": (
                        "critical"
                        if state == "terminal_conflict"
                        else "high"
                    ),
                    "owner": "Admin Eve",
                    "assigned_user_id": event.get("assigned_user_id"),
                    "scheduled_start": event["start_at"],
                    "corrective_action": (
                        "Review the appointment and feedback evidence, then "
                        "set the exact GHL event to its correct terminal status."
                    ),
                }
            )

    summary = summarise_attendance(reconciled, now=observed_now)
    summary.update(
        {
            "feedback_count": len(feedback),
            "matched_feedback_count": sum(
                bool(row["feedback_submission_ids"]) for row in reconciled
            ),
            "exception_count": len(exceptions),
            "complete": True,
            "definition_version": ATTENDANCE_DEFINITION_VERSION,
        }
    )
    return {
        "rows": reconciled,
        "exceptions": exceptions,
        "summary": summary,
    }


def summarise_attendance(
    rows: Iterable[dict[str, Any]],
    *,
    now: datetime | None = None,
    period_start: datetime | None = None,
    period_end: datetime | None = None,
) -> dict[str, Any]:
    observed_now = (now or datetime.now(UTC)).astimezone(UTC)
    selected = []
    for row in rows:
        start_at = parse_datetime(row["start_at"], "start_at")
        if period_start and start_at < period_start.astimezone(UTC):
            continue
        if period_end and start_at >= period_end.astimezone(UTC):
            continue
        selected.append(row)
    counts = Counter(
        str(row.get("canonical_status") or row.get("status") or "unknown")
        for row in selected
    )
    showed = counts["showed"]
    no_show = counts["no_show"]
    eligible_rows = [
        row for row in selected if row.get("show_rate_eligible", True)
    ]
    eligible_counts = Counter(
        str(row.get("canonical_status") or row.get("status") or "unknown")
        for row in eligible_rows
    )
    tracked_showed = eligible_counts["showed"]
    tracked_no_show = eligible_counts["no_show"]
    tracked_cancelled = eligible_counts["cancelled"]
    show_rate_denominator = tracked_showed + tracked_no_show
    cancellation_denominator = (
        tracked_showed + tracked_no_show + tracked_cancelled
    )
    legacy_showed = sum(
        str(row.get("canonical_status") or "") == "showed"
        and not row.get("show_rate_eligible", True)
        for row in selected
    )
    unresolved = sum(
        row.get("reconciliation_state") in {"elapsed_confirmed", "pending"}
        and parse_datetime(row["end_at"], "end_at") < observed_now
        for row in selected
    )
    return {
        "booked": len(selected),
        "showed": showed,
        "legacy_showed": legacy_showed,
        "tracked_showed": tracked_showed,
        "no_show": no_show,
        "tracked_no_show": tracked_no_show,
        "cancelled": counts["cancelled"],
        "tracked_cancelled": tracked_cancelled,
        "invalid": counts["invalid"],
        "confirmed": counts["confirmed"],
        "unknown": counts["unknown"],
        "unresolved": unresolved,
        "show_rate": (
            tracked_showed / show_rate_denominator
            if show_rate_denominator
            else None
        ),
        "show_rate_denominator": show_rate_denominator,
        "cancellation_rate": (
            tracked_cancelled / cancellation_denominator
            if cancellation_denominator
            else None
        ),
        "cancellation_rate_denominator": cancellation_denominator,
        "show_rate_provisional": unresolved > 0,
    }


def validate_confirmed_to_showed(
    event: dict[str, Any],
    decision: dict[str, Any],
) -> None:
    if event.get("status") != "confirmed":
        raise ValueError("only confirmed appointments can be changed to showed")
    if decision.get("reconciliation_state") != "feedback_closes_confirmed":
        raise ValueError("a deterministic matched feedback decision is required")
    if decision.get("proposed_status") != "showed":
        raise ValueError("decision does not propose showed")
    if event.get("appointment_id") != decision.get("appointment_id"):
        raise ValueError("appointment identity mismatch")
    if event.get("contact_id") != decision.get("contact_id"):
        raise ValueError("contact identity mismatch")
    if not decision.get("feedback_submission_ids"):
        raise ValueError("feedback evidence is required")


def validate_trainerize_verified_to_showed(
    event: dict[str, Any],
    evidence: dict[str, Any],
) -> None:
    if event.get("status") != "confirmed":
        raise ValueError("only confirmed appointments can be changed to showed")
    if evidence.get("decision") != "verified_showed":
        raise ValueError("verified Trainerize evidence is required")
    if event.get("appointment_id") != evidence.get("appointment_id"):
        raise ValueError("appointment identity mismatch")
    if event.get("contact_id") != evidence.get("contact_id"):
        raise ValueError("contact identity mismatch")
    start_at = parse_datetime(event.get("start_at"), "start_at")
    if (
        start_at.astimezone(BRISBANE_TZ).date().isoformat()
        != evidence.get("target_date")
    ):
        raise ValueError("appointment date does not match Trainerize evidence")
    sessions = evidence.get("matching_sessions") or []
    if len(sessions) != 1 or not sessions[0].get("session_id"):
        raise ValueError("one exact tracked Trainerize session is required")


class GHLAttendanceClient:
    base_url = "https://services.leadconnectorhq.com"

    def __init__(
        self,
        api_key: str,
        location_id: str,
        *,
        timeout: int = 60,
        write_enabled: bool = False,
    ):
        self.location_id = location_id
        self.timeout = timeout
        self.write_enabled = write_enabled
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {api_key}",
                "Version": "2021-07-28",
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        url = path if path.startswith("http") else f"{self.base_url}{path}"
        last_error: Exception | None = None
        for attempt in range(6):
            try:
                response = self.session.request(
                    method,
                    url,
                    params=params,
                    json=json,
                    timeout=self.timeout,
                )
                if response.status_code == 429 or response.status_code >= 500:
                    time.sleep(min(8, 2**attempt))
                    continue
                response.raise_for_status()
                return response.json() if response.content else {}
            except (requests.RequestException, ValueError) as exc:
                last_error = exc
                if (
                    isinstance(exc, requests.HTTPError)
                    and exc.response is not None
                    and 400 <= exc.response.status_code < 500
                    and exc.response.status_code != 429
                ):
                    break
                if attempt < 5:
                    time.sleep(min(8, 2**attempt))
        raise RuntimeError(f"GHL request failed for {path}: {last_error}") from last_error

    def list_events(
        self,
        calendar_ids: Iterable[str],
        start: datetime,
        end: datetime,
    ) -> dict[str, Any]:
        observed_at = datetime.now(UTC)
        requested = list(calendar_ids)
        rows: list[dict[str, Any]] = []
        completed_calendars: list[str] = []
        for calendar_id in requested:
            data = self._request(
                "GET",
                "/calendars/events",
                params={
                    "locationId": self.location_id,
                    "calendarId": calendar_id,
                    "startTime": int(start.timestamp() * 1000),
                    "endTime": int(end.timestamp() * 1000),
                },
            )
            rows.extend(
                normalise_event(item, observed_at=observed_at)
                for item in data.get("events", [])
                if item.get("id")
            )
            completed_calendars.append(calendar_id)
        complete = set(completed_calendars) == set(requested)
        return {
            "schema_version": 1,
            "source": "strength_assessment_attendance",
            "source_run_id": observed_at.strftime("%Y%m%dT%H%M%SZ"),
            "observed_at": observed_at.isoformat(),
            "status": "complete" if complete else "partial",
            "complete": complete,
            "calendar_ids_requested": requested,
            "calendar_ids_completed": completed_calendars,
            "rows": rows,
        }

    def list_form_submissions(
        self,
        form_id: str,
        start: datetime,
        end: datetime,
        *,
        sales_outcome_field_id: str,
    ) -> list[dict[str, Any]]:
        if not form_id:
            return []
        rows: list[dict[str, Any]] = []
        page = 1
        while True:
            data = self._request(
                "GET",
                "/forms/submissions",
                params={
                    "locationId": self.location_id,
                    "formId": form_id,
                    "startAt": start.date().isoformat(),
                    "endAt": end.date().isoformat(),
                    "page": page,
                    "limit": 100,
                },
            )
            rows.extend(
                normalise_feedback_submission(
                    item,
                    sales_outcome_field_id=sales_outcome_field_id,
                )
                for item in data.get("submissions", [])
                if item.get("id") and item.get("contactId")
            )
            next_page = (data.get("meta") or {}).get("nextPage")
            if not next_page:
                break
            page = int(next_page)
        return rows

    def update_confirmed_to_showed(
        self,
        event: dict[str, Any],
        decision: dict[str, Any],
        *,
        idempotency_key: str,
    ) -> dict[str, Any]:
        if not self.write_enabled:
            raise RuntimeError("GHL attendance writes are disabled")
        validate_confirmed_to_showed(event, decision)
        if not idempotency_key.strip():
            raise ValueError("idempotency_key is required")
        return self._request(
            "PUT",
            f"/calendars/events/appointments/{event['appointment_id']}",
            json={
                "appointmentStatus": "showed",
                "idempotencyKey": idempotency_key,
            },
        )

    def get_contact(self, contact_id: str) -> dict[str, Any]:
        response = self._request("GET", f"/contacts/{contact_id}")
        contact = response.get("contact") or response
        return {
            "contact_id": contact_id,
            "email": str(contact.get("email") or "").strip(),
            "firstName": str(contact.get("firstName") or "").strip(),
            "lastName": str(contact.get("lastName") or "").strip(),
            "name": str(contact.get("name") or "").strip(),
        }

    def get_appointment_state(
        self,
        appointment_id: str,
    ) -> dict[str, Any]:
        response = self._request(
            "GET",
            f"/calendars/events/appointments/{appointment_id}",
        )
        event = response.get("appointment") or response
        return {
            "appointment_id": str(
                event.get("id") or appointment_id
            ).strip(),
            "contact_id": str(
                event.get("contactId") or event.get("contact_id") or ""
            ).strip(),
            "start_at": parse_datetime(
                event.get("startTime") or event.get("start_at"),
                "start_at",
            ).isoformat(),
            "status": normalize_status(
                event.get("appointmentStatus")
                or event.get("appoinmentStatus")
                or event.get("status")
            ),
        }

    def update_trainerize_verified_to_showed(
        self,
        event: dict[str, Any],
        evidence: dict[str, Any],
        *,
        idempotency_key: str,
    ) -> dict[str, Any]:
        if not self.write_enabled:
            raise RuntimeError("GHL attendance writes are disabled")
        validate_trainerize_verified_to_showed(event, evidence)
        if not idempotency_key.strip():
            raise ValueError("idempotency_key is required")
        return self._request(
            "PUT",
            f"/calendars/events/appointments/{event['appointment_id']}",
            json={
                "appointmentStatus": "showed",
                "idempotencyKey": idempotency_key,
            },
        )

    def list_contact_tasks(self, contact_id: str) -> list[dict[str, Any]]:
        return self._request(
            "GET", f"/contacts/{contact_id}/tasks"
        ).get("tasks", [])

    def create_contact_task(
        self,
        contact_id: str,
        *,
        title: str,
        body: str,
        due_at: str,
        assigned_to: str,
    ) -> dict[str, Any]:
        if not self.write_enabled:
            raise RuntimeError("GHL attendance task writes are disabled")
        if not assigned_to:
            raise ValueError("assigned_to is required")
        return self._request(
            "POST",
            f"/contacts/{contact_id}/tasks",
            json={
                "title": title,
                "body": body,
                "dueDate": due_at,
                "completed": False,
                "assignedTo": assigned_to,
            },
        )

    def update_contact_task(
        self,
        contact_id: str,
        task_id: str,
        *,
        title: str,
        body: str,
        due_at: str,
        assigned_to: str,
    ) -> dict[str, Any]:
        if not self.write_enabled:
            raise RuntimeError("GHL attendance task writes are disabled")
        return self._request(
            "PUT",
            f"/contacts/{contact_id}/tasks/{task_id}",
            json={
                "title": title,
                "body": body,
                "dueDate": due_at,
                "completed": False,
                "assignedTo": assigned_to,
            },
        )

    def complete_contact_task(
        self,
        contact_id: str,
        task_id: str,
    ) -> dict[str, Any]:
        if not self.write_enabled:
            raise RuntimeError("GHL attendance task writes are disabled")
        return self._request(
            "PUT",
            f"/contacts/{contact_id}/tasks/{task_id}/completed",
            json={"completed": True},
        )
