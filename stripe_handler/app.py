#!/usr/bin/env python3
"""
stripe_handler/app.py
Flask webhook handler for GHL → Stripe automation.

Endpoints:
  POST /stripe/pause-hold    — fires on Pre-Hold-Start Date (Hold Start Date - 7 days)
  POST /stripe/cancel        — fires on cancellation form submission (Membership or PT)
  POST /stripe/service-change — schedules an allowlisted continuing-service change
  POST /stripe/commitment-clawback/quote — calculates, records and returns a
    member-visible discount-recovery quote without creating a charge
  POST /ghl/pt-hold-clearance — previews or clears unpaid PT hold appointments

Hold logic:
  Membership/SGPT pauses remain date based. PT holds are session based and
  return a side-effect-free entitlement proposal for human approval.

Cancellation logic:
  Receives notice_end_date from GHL (CS: Notice End Date field). Finds the last
  scheduled payment within that notice period, then sets cancel_at to the end of
  that billing period (last_payment_date + interval). Access ends when that period closes.
"""

import os
import logging
import hashlib
import json
import hmac
import math
import calendar
from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo
from flask import Flask, request, jsonify
import requests
import stripe

try:
    from .pt_entitlement_reconciliation import reconcile_pt_hold
except ImportError:  # Railway starts app.py directly from stripe_handler/.
    from pt_entitlement_reconciliation import reconcile_pt_hold

stripe.api_key = os.environ["STRIPE_API_KEY"]

GHL_API_KEY = os.environ.get("GHL_API_KEY", "")
GHL_LOCATION_ID = os.environ.get("GHL_LOCATION_ID", "")
GHL_ADMIN_EVE_USER_ID = os.environ.get("GHL_ADMIN_EVE_USER_ID", "")
PT_HOLD_ENTITLEMENT_RECONCILIATION_ENABLED = (
    os.environ.get("PT_HOLD_ENTITLEMENT_RECONCILIATION_ENABLED", "false")
    .strip()
    .lower()
    in {"1", "true", "yes"}
)
GHL_AUTOMATION_USER_ID = (
    os.environ.get("GHL_AUTOMATION_USER_ID", "")
    or GHL_ADMIN_EVE_USER_ID
)
PT_HOLD_CLEARANCE_SECRET = os.environ.get("PT_HOLD_CLEARANCE_SECRET", "")
GHL_PT_CALENDAR_IDS = {
    calendar_id.strip()
    for calendar_id in os.environ.get("GHL_PT_CALENDAR_IDS", "").split(",")
    if calendar_id.strip()
}
GHL_BASE_URL = "https://services.leadconnectorhq.com"
GHL_FIELD_NAMES = {
    "hold_status": "Billing OS: Hold Action Status",
    "cancellation_status": "Billing OS: Cancellation Action Status",
    "service_change_status": "SC: Billing Action Status",
    "service_change_effective_date": "SC: Effective Date",
    "service_change_billing_boundary_date": "SC: Billing Boundary Date",
    "service_change_notice_waiver_status": "SC: Notice Waiver Status",
    "service_change_notice_waiver_approved_by": (
        "SC: Notice Waiver Approved By"
    ),
    "service_change_notice_waiver_approved_at": (
        "SC: Notice Waiver Approved At"
    ),
    "service_change_notice_waiver_reason": "SC: Notice Waiver Reason",
    "service_change_final_prior_service_date": (
        "SC: Final Prior Service Date"
    ),
    "service_change_change_status": "SC: Change Status",
    "service_change_commitment_start_date": "SC: Commitment Start Date",
    "service_change_commitment_end_date": "SC: Commitment End Date",
    "service_change_continuation_reminder_date": (
        "SC: Continuation Reminder Date"
    ),
    "service_change_clawback_quote_cents": "SC: Clawback Quote Cents",
    "service_change_clawback_status": "SC: Clawback Status",
    "last_error": "Billing OS: Last Error",
    "last_action_at": "Billing OS: Last Action At",
    "last_result": "Billing OS: Last Result",
    "hold_start": "HS: Hold Start Date",
    "hold_end": "HS: Hold End Date",
    "pre_return": "HS: Pre-Return Date",
    "hold_type": "HS: Hold Type",
    "hold_weeks": "HS: Hold Weeks",
    "extended_hold_weeks": "HS: Extended Hold - Weeks",
    "hold_reason": "HS: Hold Reason",
    "hold_notes": "HS: Hold Notes",
    "extended_explanation": "HS: Extended Explanation",
    "extended_requested": "HS: Extended Hold Requested",
    "hold_signature": "HS: Signature - Hold Request Confirmation",
    "hold_lifecycle_status": "HS: Hold Status",
    "request_hold_start": "HS Request: Hold Start Date",
    "request_hold_weeks": "HS Request: Hold Weeks",
    "request_extended_hold_weeks": "HS Request: Extended Hold Weeks",
    "request_hold_reason": "HS Request: Hold Reason",
    "request_hold_notes": "HS Request: Hold Notes",
    "request_extended_explanation": "HS Request: Extended Explanation",
    "request_extended_requested": "HS Request: Extended Hold Requested",
    "request_signature": "HS Request: Signature - Hold Request Confirmation",
    "request_intake_status": "HS Request: Intake Status",
    "hold_return_guard_status": "HS: Return Guard Status",
    "hold_return_guard_result": "HS: Return Guard Result",
    "hold_return_guard_checked_at": "HS: Return Guard Checked At",
}
_ghl_field_ids = {}
BRISBANE_TZ = ZoneInfo("Australia/Brisbane")
OPEN_HOLD_STATUSES = {
    "Pending Hold",
    "Escalated Hold",
    "On Hold",
    "Returning",
}
HOLD_FORM_KINDS = {
    "standard_membership": "standard",
    "standard_pt": "standard",
    "extended_membership": "extended",
    "extended_pt": "extended",
}
CANCELLATION_WORKFLOW_IDS = {
    "membership": "73345f90-6ca8-444c-a694-8d1b25cdfdc6",
    "pt": "bdd09a42-d00d-43ba-9201-d6cd0057e3ae",
}
HOLD_RETURN_WORKFLOW_ID = "f6dc65cb-d5e0-4ff0-90ba-b94d832b86ab"
SERVICE_CHANGE_HUB_URL = os.environ.get("SERVICE_CHANGE_HUB_URL", "").rstrip("/")
SERVICE_CHANGE_HUB_SECRET = os.environ.get(
    "SERVICE_CHANGE_HUB_SECRET", ""
).strip()

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger(__name__)


def parse_date(date_str):
    """Parse date string from GHL — tries common formats."""
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Cannot parse date: '{date_str}'")


def get_interval_days(subscription):
    """Return billing cycle length in days."""
    plan = subscription["items"]["data"][0]["plan"]
    interval = plan.get("interval", "week")
    count = plan.get("interval_count", 1)
    mapping = {"day": 1, "week": 7, "month": 30, "year": 365}
    return mapping.get(interval, 7) * count


def calculate_cancellation_boundary(subscription, notice_end_date):
    """Return the first paid-period boundary on/after the final access boundary.

    GHL notice dates are Brisbane calendar dates and are inclusive. Stripe
    periods are exact UTC timestamps. Keeping the Stripe timestamp avoids a
    same-day timezone shift that can otherwise create one more invoice.
    """
    plan = subscription["items"]["data"][0]["plan"]
    interval = plan.get("interval", "week")
    interval_count = int(plan.get("interval_count", 1))
    interval_seconds = {
        "day": 24 * 60 * 60,
        "week": 7 * 24 * 60 * 60,
    }.get(interval)
    if interval_seconds is None:
        raise ValueError(
            f"Unsupported cancellation interval '{interval}'; manual review required"
        )
    interval_seconds *= interval_count

    final_access_boundary = datetime.combine(
        notice_end_date + timedelta(days=1),
        time.min,
        tzinfo=BRISBANE_TZ,
    )
    final_access_boundary_ts = int(final_access_boundary.timestamp())
    current_period_end_ts = int(subscription["current_period_end"])

    if current_period_end_ts >= final_access_boundary_ts:
        cancel_at_ts = current_period_end_ts
    else:
        periods_to_advance = math.ceil(
            (final_access_boundary_ts - current_period_end_ts)
            / interval_seconds
        )
        cancel_at_ts = current_period_end_ts + (
            periods_to_advance * interval_seconds
        )

    last_payment_ts = cancel_at_ts - interval_seconds
    return cancel_at_ts, last_payment_ts


class GHLStatusError(RuntimeError):
    """Raised when Billing OS cannot persist its result back to GHL."""


def _ghl_headers():
    return {
        "Authorization": f"Bearer {GHL_API_KEY}",
        "Version": "2021-07-28",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


def _resolve_ghl_field_ids():
    if _ghl_field_ids:
        return _ghl_field_ids
    if not GHL_API_KEY or not GHL_LOCATION_ID:
        raise GHLStatusError("GHL_API_KEY and GHL_LOCATION_ID are required")

    response = requests.get(
        f"{GHL_BASE_URL}/locations/{GHL_LOCATION_ID}/customFields",
        headers=_ghl_headers(),
        params={"model": "contact"},
        timeout=20,
    )
    if not response.ok:
        raise GHLStatusError(
            f"Unable to resolve GHL custom fields: HTTP {response.status_code}"
        )

    by_name = {
        field.get("name"): field.get("id")
        for field in response.json().get("customFields", [])
    }
    missing = [name for name in GHL_FIELD_NAMES.values() if not by_name.get(name)]
    if missing:
        raise GHLStatusError(
            "Missing required GHL custom fields: " + ", ".join(missing)
        )

    _ghl_field_ids.update(
        {key: by_name[name] for key, name in GHL_FIELD_NAMES.items()}
    )
    return _ghl_field_ids


def update_ghl_status(contact_id, action, status, error="", result=""):
    """Persist the verified Billing OS outcome on the GHL contact."""
    if not contact_id:
        raise GHLStatusError("contact_id is required for Billing OS acknowledgement")
    if action not in {"hold", "cancellation", "service_change"}:
        raise GHLStatusError(f"Unsupported Billing OS action: {action}")

    field_ids = _resolve_ghl_field_ids()
    update_ghl_fields(
        contact_id,
        {
            f"{action}_status": status,
            "last_error": error[:4000],
            "last_action_at": datetime.now(timezone.utc).isoformat(),
            "last_result": result[:4000],
        },
        field_ids=field_ids,
    )


def billing_exception_key(contact_id, action, message):
    raw = "|".join(
        [
            str(contact_id or "").strip(),
            str(action or "").strip().lower(),
            str(message or "").strip(),
        ]
    )
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def same_day_admin_due_date():
    """Return 5:00 pm Brisbane today, or now if the exception occurs later."""
    now = datetime.now(BRISBANE_TZ)
    due_local = datetime.combine(
        now.date(),
        time(hour=17),
        tzinfo=BRISBANE_TZ,
    )
    if now > due_local:
        due_local = now
    return (
        due_local.astimezone(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def create_admin_exception_task(
    contact_id,
    action,
    message,
    contact_name="Unknown",
    requested_action="",
):
    """Create one open same-day Billing OS exception task for Admin Eve."""
    if not contact_id:
        log.error("ADMIN TASK FAILED: contact_id is required")
        return False
    if not GHL_ADMIN_EVE_USER_ID:
        log.error("ADMIN TASK FAILED: GHL_ADMIN_EVE_USER_ID is required")
        return False

    action_label = str(action or "billing").strip().replace("_", " ").title()
    exception_key = billing_exception_key(contact_id, action, message)
    marker = f"Billing OS exception key: {exception_key}"
    requested = requested_action or f"Manually complete the {action_label.lower()}"

    try:
        existing_response = requests.get(
            f"{GHL_BASE_URL}/contacts/{contact_id}/tasks",
            headers=_ghl_headers(),
            timeout=20,
        )
        if not existing_response.ok:
            raise GHLStatusError(
                "Unable to check existing Billing OS tasks: "
                f"HTTP {existing_response.status_code}"
            )
        for task in existing_response.json().get("tasks", []):
            if marker in str(task.get("body", "")) and not task.get("completed"):
                log.info(
                    "ADMIN TASK ALREADY OPEN: contact=%s | action=%s | key=%s",
                    contact_id,
                    action,
                    exception_key,
                )
                return True

        title = f"BILLING EXCEPTION: {action_label} - Manual action required"
        body = (
            f"Billing OS could not complete this {action_label.lower()}.\n\n"
            f"Contact: {contact_name or 'Unknown'}\n"
            f"Requested action: {requested}\n"
            f"Error: {message}\n\n"
            "Action required today: manually complete or reconcile the action "
            "in Stripe, verify the GHL billing status and dates, then complete "
            "this task.\n\n"
            f"{marker}"
        )
        create_response = requests.post(
            f"{GHL_BASE_URL}/contacts/{contact_id}/tasks",
            headers=_ghl_headers(),
            json={
                "title": title,
                "body": body,
                "dueDate": same_day_admin_due_date(),
                "completed": False,
                "assignedTo": GHL_ADMIN_EVE_USER_ID,
            },
            timeout=20,
        )
        if create_response.status_code != 201:
            raise GHLStatusError(
                "Unable to create Billing OS exception task: "
                f"HTTP {create_response.status_code}"
            )
        log.info(
            "ADMIN TASK CREATED: contact=%s | action=%s | key=%s",
            contact_id,
            action,
            exception_key,
        )
        return True
    except (requests.RequestException, GHLStatusError) as exc:
        log.error("ADMIN TASK FAILED: %s", exc)
        return False


def create_hold_return_exception_task(
    contact_id,
    message,
    contact_name="Unknown",
):
    """Create one open same-day Hold Return cycle exception for Admin Eve."""
    if not contact_id:
        log.error("HOLD RETURN TASK FAILED: contact_id is required")
        return False
    if not GHL_ADMIN_EVE_USER_ID:
        log.error("HOLD RETURN TASK FAILED: GHL_ADMIN_EVE_USER_ID is required")
        return False

    exception_key = billing_exception_key(
        contact_id,
        "hold_return_guard",
        message,
    )
    marker = f"Hold Return Guard exception key: {exception_key}"
    try:
        existing_response = requests.get(
            f"{GHL_BASE_URL}/contacts/{contact_id}/tasks",
            headers=_ghl_headers(),
            timeout=20,
        )
        if not existing_response.ok:
            raise GHLStatusError(
                "Unable to check existing Hold Return tasks: "
                f"HTTP {existing_response.status_code}"
            )
        for task in existing_response.json().get("tasks", []):
            if marker in str(task.get("body", "")) and not task.get("completed"):
                log.info(
                    "HOLD RETURN TASK ALREADY OPEN: contact=%s | key=%s",
                    contact_id,
                    exception_key,
                )
                return True

        body = (
            "The Hold Return Journey stopped before a lifecycle write because "
            "the current contact state did not prove that this enrolment belongs "
            "to the accepted hold cycle.\n\n"
            f"Contact: {contact_name or 'Unknown'}\n"
            f"Mismatch: {message}\n\n"
            "Action required today: reconcile the accepted protected request, "
            "current hold dates, Hold Status and Hold OS opportunity. Do not "
            "message the member or change Stripe merely because this guard "
            "failed. Complete this task only after the current cycle is verified.\n\n"
            f"{marker}"
        )
        create_response = requests.post(
            f"{GHL_BASE_URL}/contacts/{contact_id}/tasks",
            headers=_ghl_headers(),
            json={
                "title": (
                    "HOLD RETURN EXCEPTION: Cycle mismatch - review required"
                ),
                "body": body,
                "dueDate": same_day_admin_due_date(),
                "completed": False,
                "assignedTo": GHL_ADMIN_EVE_USER_ID,
            },
            timeout=20,
        )
        if create_response.status_code != 201:
            raise GHLStatusError(
                "Unable to create Hold Return exception task: "
                f"HTTP {create_response.status_code}"
            )
        log.info(
            "HOLD RETURN TASK CREATED: contact=%s | key=%s",
            contact_id,
            exception_key,
        )
        return True
    except (requests.RequestException, GHLStatusError) as exc:
        log.error("HOLD RETURN TASK FAILED: %s", exc)
        return False


def update_ghl_fields(contact_id, values, field_ids=None):
    if not contact_id:
        raise GHLStatusError("contact_id is required for a GHL field update")
    field_ids = field_ids or _resolve_ghl_field_ids()
    missing_keys = [key for key in values if key not in field_ids]
    if missing_keys:
        raise GHLStatusError(
            "Unknown Billing OS field keys: " + ", ".join(missing_keys)
        )
    payload_values = {
        field_ids[key]: value
        for key, value in values.items()
    }
    response = requests.put(
        f"{GHL_BASE_URL}/contacts/{contact_id}",
        headers=_ghl_headers(),
        json={
            "customFields": [
                {"id": field_id, "fieldValue": value}
                for field_id, value in payload_values.items()
            ]
        },
        timeout=20,
    )
    if not response.ok:
        raise GHLStatusError(
            f"Unable to update GHL contact: HTTP {response.status_code}"
        )


def get_ghl_contact_fields(contact_id):
    if not contact_id:
        raise GHLStatusError("contact_id is required for a GHL contact read")
    field_ids = _resolve_ghl_field_ids()
    response = requests.get(
        f"{GHL_BASE_URL}/contacts/{contact_id}",
        headers=_ghl_headers(),
        timeout=20,
    )
    if not response.ok:
        raise GHLStatusError(
            f"Unable to read GHL contact: HTTP {response.status_code}"
        )
    contact = response.json().get("contact", {})
    by_id = {}
    for field in contact.get("customFields", []):
        by_id[field.get("id")] = field.get(
            "fieldValue", field.get("value", "")
        )
    return {
        key: by_id.get(field_id, "")
        for key, field_id in field_ids.items()
    }


def parse_ghl_date(value):
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value / 1000, tz=timezone.utc).date()
    text = str(value or "").strip()
    if text.isdigit():
        return datetime.fromtimestamp(int(text) / 1000, tz=timezone.utc).date()
    return parse_date(text)


class PTHoldClearanceError(RuntimeError):
    """Raised when PT appointment clearance cannot proceed safely."""


def _ghl_v3_headers():
    headers = _ghl_headers()
    headers["Version"] = "v3"
    return headers


def parse_event_datetime(value):
    """Return a calendar event timestamp as an aware UTC datetime."""
    if isinstance(value, (int, float)):
        timestamp = float(value)
        if timestamp > 100_000_000_000:
            timestamp /= 1000
        return datetime.fromtimestamp(timestamp, tz=timezone.utc)

    text = str(value or "").strip()
    if not text:
        raise ValueError("Calendar event has no start time")
    if text.isdigit():
        return parse_event_datetime(int(text))
    parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=BRISBANE_TZ)
    return parsed.astimezone(timezone.utc)


def pt_hold_window(hold_start_date, hold_end_date):
    """Return the Brisbane hold interval as UTC, with return day exclusive."""
    start = datetime.combine(
        hold_start_date,
        time.min,
        tzinfo=BRISBANE_TZ,
    )
    end = datetime.combine(
        hold_end_date,
        time.min,
        tzinfo=BRISBANE_TZ,
    )
    return start.astimezone(timezone.utc), end.astimezone(timezone.utc)


def event_is_recurring(event):
    recurring_flag = str(event.get("isRecurring", "")).strip().lower()
    return bool(
        recurring_flag in {"true", "1", "yes"}
        or event.get("rrule")
        or event.get("masterEventId")
        or event.get("recurringEventId")
    )


def get_pt_hold_calendar_events(contact_id, hold_start_date, hold_end_date):
    """Fetch exact-contact events from every approved PT calendar."""
    if not GHL_PT_CALENDAR_IDS:
        raise PTHoldClearanceError("No approved PT calendars are configured")

    start, end = pt_hold_window(hold_start_date, hold_end_date)
    events_by_id = {}
    for calendar_id in sorted(GHL_PT_CALENDAR_IDS):
        response = requests.get(
            f"{GHL_BASE_URL}/calendars/events",
            headers=_ghl_v3_headers(),
            params={
                "locationId": GHL_LOCATION_ID,
                "calendarId": calendar_id,
                "startTime": int(start.timestamp() * 1000),
                "endTime": int(end.timestamp() * 1000),
            },
            timeout=20,
        )
        if not response.ok:
            raise PTHoldClearanceError(
                "Unable to read PT calendar "
                f"{calendar_id}: HTTP {response.status_code}"
            )
        for event in response.json().get("events", []):
            if str(event.get("contactId", "")).strip() != contact_id:
                continue
            event_id = str(event.get("id", "")).strip()
            if not event_id:
                raise PTHoldClearanceError(
                    f"PT calendar {calendar_id} returned an event without an ID"
                )
            actual_calendar_id = str(event.get("calendarId", "")).strip()
            if actual_calendar_id and actual_calendar_id not in GHL_PT_CALENDAR_IDS:
                raise PTHoldClearanceError(
                    f"Event {event_id} is not on an approved PT calendar"
                )
            event["calendarId"] = actual_calendar_id or calendar_id
            events_by_id[event_id] = event
    return list(events_by_id.values())


def classify_pt_hold_event(event, hold_start_date, hold_end_date, now=None):
    """Classify one exact-contact PT event without mutating it."""
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    start_window, end_window = pt_hold_window(hold_start_date, hold_end_date)
    event_id = str(event.get("id", "")).strip()
    try:
        start = parse_event_datetime(event.get("startTime"))
    except (TypeError, ValueError) as exc:
        return "manual_review", f"Invalid start time: {exc}"

    status = str(
        event.get("appointmentStatus") or event.get("status") or "new"
    ).strip().lower()
    if status not in {"new", "confirmed", "active"}:
        return "skip", f"Status is {status or 'blank'}"
    if not start_window <= start < end_window:
        return "skip", "Outside actual hold interval"
    if start <= now:
        return "skip", "Appointment has already started"
    if event_is_recurring(event):
        return "manual_review", "Recurring appointment requires instance review"
    if start - now <= timedelta(hours=24):
        return "cancel", "Inside the 24-hour forfeiture window"
    if not event_id:
        return "manual_review", "Appointment has no event ID"
    return "delete", "Approved PT hold; unpaid advance appointment"


def pt_hold_clearance_run_key(contact_id, hold_start_date, hold_end_date):
    raw = f"{contact_id}|{hold_start_date}|{hold_end_date}"
    return hashlib.sha256(raw.encode()).hexdigest()[:20]


def pt_hold_audit_title(hold_start_date, hold_end_date):
    return f"PT hold clearance: {hold_start_date} to {hold_end_date}"


def format_pt_hold_audit_section(
    run_key,
    phase,
    hold_start_date,
    hold_end_date,
    records,
    now=None,
):
    checked_at = (now or datetime.now(timezone.utc)).astimezone(
        BRISBANE_TZ
    ).isoformat()
    lines = [
        f"PT HOLD CLEARANCE [{run_key}]",
        f"Phase: {phase}",
        f"Checked: {checked_at}",
        f"Actual hold interval: {hold_start_date} to {hold_end_date} "
        "(return date excluded)",
    ]
    if not records:
        lines.append("Appointments: none")
        return "\n".join(lines)

    lines.append("Appointments:")
    for record in records:
        event = record["event"]
        try:
            start = parse_event_datetime(event.get("startTime")).astimezone(
                BRISBANE_TZ
            ).isoformat()
        except (TypeError, ValueError):
            start = str(event.get("startTime", "unknown"))
        lines.append(
            "- "
            f"event={event.get('id', 'unknown')} | start={start} | "
            f"calendar={event.get('calendarId', 'unknown')} | "
            f"trainer={event.get('assignedUserId', 'unknown')} | "
            "prior_status="
            f"{event.get('appointmentStatus') or event.get('status') or 'unknown'} | "
            f"decision={record.get('decision')} | "
            f"result={record.get('result', 'planned')} | "
            f"reason={record.get('reason', '')}"
        )
    return "\n".join(lines)


def find_pt_hold_audit_note(contact_id, title):
    response = requests.get(
        f"{GHL_BASE_URL}/contacts/{contact_id}/notes",
        headers=_ghl_v3_headers(),
        params={"limit": 100},
        timeout=20,
    )
    if not response.ok:
        raise PTHoldClearanceError(
            f"Unable to read PT clearance notes: HTTP {response.status_code}"
        )
    for note in response.json().get("notes", []):
        if str(note.get("title", "")).strip() == title:
            return note
    return None


def write_pt_hold_audit_note(contact_id, title, section):
    """Create or append to the single audit note for this hold interval."""
    if not GHL_AUTOMATION_USER_ID:
        raise PTHoldClearanceError(
            "GHL_AUTOMATION_USER_ID is required for clearance audit notes"
        )
    existing = find_pt_hold_audit_note(contact_id, title)
    if existing:
        note_id = str(existing.get("id", "")).strip()
        existing_body = str(existing.get("body", "")).strip()
        body = f"{existing_body}\n\n{section}" if existing_body else section
        response = requests.put(
            f"{GHL_BASE_URL}/contacts/{contact_id}/notes/{note_id}",
            headers=_ghl_v3_headers(),
            json={
                "userId": GHL_AUTOMATION_USER_ID,
                "title": title,
                "body": body,
                "pinned": False,
            },
            timeout=20,
        )
        expected_status = 200
    else:
        body = section
        response = requests.post(
            f"{GHL_BASE_URL}/contacts/{contact_id}/notes",
            headers=_ghl_v3_headers(),
            json={
                "userId": GHL_AUTOMATION_USER_ID,
                "title": title,
                "body": body,
                "pinned": False,
            },
            timeout=20,
        )
        expected_status = 201
    if response.status_code != expected_status:
        raise PTHoldClearanceError(
            f"Unable to persist PT clearance audit: HTTP {response.status_code}"
        )
    note = response.json().get("note", {})
    return str(note.get("id") or (existing or {}).get("id", ""))


def delete_pt_hold_event(event_id):
    response = requests.delete(
        f"{GHL_BASE_URL}/calendars/events/{event_id}",
        headers=_ghl_v3_headers(),
        timeout=20,
    )
    if response.status_code not in {200, 201, 204, 404}:
        raise PTHoldClearanceError(
            f"Unable to delete appointment {event_id}: "
            f"HTTP {response.status_code}"
        )
    return "already absent" if response.status_code == 404 else "deleted"


def cancel_late_pt_hold_event(event):
    event_id = str(event.get("id", "")).strip()
    payload = {
        "appointmentStatus": "cancelled",
        "toNotify": False,
    }
    for key in (
        "title",
        "calendarId",
        "startTime",
        "endTime",
        "assignedUserId",
        "meetingLocationType",
        "meetingLocationId",
        "address",
        "description",
    ):
        if event.get(key) not in (None, ""):
            payload[key] = event[key]
    response = requests.put(
        f"{GHL_BASE_URL}/calendars/events/appointments/{event_id}",
        headers=_ghl_v3_headers(),
        json=payload,
        timeout=20,
    )
    if not response.ok:
        raise PTHoldClearanceError(
            f"Unable to retain late-cancelled appointment {event_id}: "
            f"HTTP {response.status_code}"
        )
    return "cancelled and retained"


def validate_hold_request(fields, request_kind):
    required = ["hold_start", "hold_reason"]
    week_key = "hold_weeks" if request_kind == "standard" else "extended_hold_weeks"
    required.append(week_key)
    missing = [key for key in required if fields.get(key) in ("", None, [])]
    if missing:
        return "Missing required hold request fields: " + ", ".join(missing)

    try:
        start_date = parse_ghl_date(fields["hold_start"])
        weeks = int(str(fields[week_key]).strip())
    except (TypeError, ValueError) as exc:
        return f"Invalid hold request values: {exc}"

    allowed = range(1, 5) if request_kind == "standard" else range(5, 13)
    if weeks not in allowed:
        return (
            f"{request_kind.title()} hold weeks must be "
            f"{min(allowed)} to {max(allowed)}"
        )

    today = datetime.now(BRISBANE_TZ).date()
    minimum = today + timedelta(days=10)
    maximum = today + timedelta(days=40)
    if not minimum <= start_date <= maximum:
        return f"Hold Start Date must be between {minimum} and {maximum}"
    return ""


def snapshot_hold_request(contact_id, fields, request_kind):
    values = {
        "request_hold_start": fields.get("hold_start", ""),
        "request_hold_reason": fields.get("hold_reason", ""),
        "request_hold_notes": fields.get("hold_notes", ""),
        "request_extended_explanation": fields.get(
            "extended_explanation", ""
        ),
        "request_extended_requested": fields.get("extended_requested", ""),
        "request_signature": fields.get("hold_signature", ""),
        "request_intake_status": "Accepted",
    }
    if request_kind == "standard":
        values["request_hold_weeks"] = fields.get("hold_weeks", "")
        values["request_extended_hold_weeks"] = ""
    else:
        values["request_hold_weeks"] = ""
        values["request_extended_hold_weeks"] = fields.get(
            "extended_hold_weeks", ""
        )
    update_ghl_fields(contact_id, values)


def restore_protected_hold(contact_id, fields):
    standard_weeks = fields.get("request_hold_weeks", "")
    extended_weeks = fields.get("request_extended_hold_weeks", "")
    values = {
        "hold_start": fields.get("request_hold_start", ""),
        "hold_reason": fields.get("request_hold_reason", ""),
        "hold_notes": fields.get("request_hold_notes", ""),
        "extended_explanation": fields.get(
            "request_extended_explanation", ""
        ),
        "extended_requested": fields.get(
            "request_extended_requested", ""
        ),
        "hold_signature": fields.get("request_signature", ""),
        "hold_weeks": standard_weeks,
        "extended_hold_weeks": extended_weeks,
        "request_intake_status": "Rejected - Existing Hold",
    }
    update_ghl_fields(contact_id, values)


def ghl_payload_value(data, *keys):
    """Read a value from direct or nested GHL webhook data."""
    if not isinstance(data, (dict, list)):
        return ""
    if isinstance(data, dict):
        for key in keys:
            value = data.get(key)
            if value not in ("", None, [], {}):
                return value
        for value in data.values():
            nested = ghl_payload_value(value, *keys)
            if nested not in ("", None, [], {}):
                return nested
    else:
        for value in data:
            nested = ghl_payload_value(value, *keys)
            if nested not in ("", None, [], {}):
                return nested
    return ""


@app.route("/ghl/hold-intake", methods=["POST"])
def hold_intake():
    data = request.get_json(silent=True) or {}
    contact_id = str(
        ghl_payload_value(data, "contact_id", "contactId")
    ).strip()
    form_kind = str(
        ghl_payload_value(data, "form_kind", "formKind")
        or request.headers.get("form_kind", "")
    ).strip()
    request_kind = HOLD_FORM_KINDS.get(form_kind)

    if not contact_id or not request_kind:
        return jsonify({"status": "exception", "error": "Invalid intake payload"}), 400

    try:
        fields = get_ghl_contact_fields(contact_id)
        hold_status = str(fields.get("hold_lifecycle_status", "")).strip()
        if hold_status in OPEN_HOLD_STATUSES:
            protected_start = fields.get("request_hold_start")
            protected_weeks = (
                fields.get("request_hold_weeks")
                or fields.get("request_extended_hold_weeks")
            )
            if not protected_start or not protected_weeks:
                message = (
                    "Open hold has no protected request snapshot; "
                    "manual restoration required"
                )
                update_ghl_fields(
                    contact_id,
                    {
                        "request_intake_status": "Rejected - Invalid",
                        "last_error": message,
                    },
                )
                return jsonify({"status": "exception", "error": message}), 409
            restore_protected_hold(contact_id, fields)
            return jsonify(
                {
                    "status": "rejected_existing_hold",
                    "hold_status": hold_status,
                }
            ), 200

        validation_error = validate_hold_request(fields, request_kind)
        if validation_error:
            update_ghl_fields(
                contact_id,
                {
                    "request_intake_status": "Rejected - Invalid",
                    "last_error": validation_error,
                },
            )
            return jsonify(
                {"status": "exception", "error": validation_error}
            ), 422

        snapshot_hold_request(contact_id, fields, request_kind)
        return jsonify({"status": "accepted", "form_kind": form_kind}), 200
    except GHLStatusError as exc:
        log.error("Hold intake guard failed: %s", exc)
        return jsonify(
            {"status": "exception", "error": "GHL intake guard failed"}
        ), 502


def validate_hold_return_cycle(fields, phase, today=None):
    """Validate that a Return Journey write belongs to the accepted cycle."""
    if phase not in {"returning", "completed"}:
        return "Invalid Hold Return guard phase"

    today = today or datetime.now(BRISBANE_TZ).date()
    expected_status = "On Hold" if phase == "returning" else "Returning"
    actual_status = str(fields.get("hold_lifecycle_status", "")).strip()
    if actual_status != expected_status:
        return (
            f"{phase.title()} write expected Hold Status {expected_status}; "
            f"found {actual_status or 'blank'}"
        )

    intake_status = str(fields.get("request_intake_status", "")).strip()
    if intake_status != "Accepted":
        return (
            "Protected hold intake is not Accepted; "
            f"found {intake_status or 'blank'}"
        )

    try:
        hold_start = parse_ghl_date(fields.get("hold_start"))
        hold_end = parse_ghl_date(fields.get("hold_end"))
        pre_return = parse_ghl_date(fields.get("pre_return"))
        protected_start = parse_ghl_date(fields.get("request_hold_start"))
    except (TypeError, ValueError) as exc:
        return f"Current-cycle dates are missing or invalid: {exc}"

    if hold_end <= hold_start:
        return (
            f"Hold chronology is invalid: start {hold_start}, end {hold_end}"
        )
    if pre_return != hold_end - timedelta(days=7):
        return (
            f"Pre-Return Date {pre_return} does not equal "
            f"Hold End Date minus 7 days ({hold_end - timedelta(days=7)})"
        )
    if protected_start != hold_start:
        return (
            f"Protected accepted start {protected_start} does not match "
            f"current Hold Start Date {hold_start}"
        )

    expected_day = (
        hold_end if phase == "returning" else hold_end + timedelta(days=3)
    )
    if today != expected_day:
        return (
            f"{phase.title()} write expected on {expected_day}; "
            f"guard ran on {today}"
        )
    return ""


def stop_hold_return_workflow(contact_id):
    """Remove every active Hold Return Journey execution for the contact."""
    response = requests.delete(
        (
            f"{GHL_BASE_URL}/contacts/{contact_id}/workflow/"
            f"{HOLD_RETURN_WORKFLOW_ID}"
        ),
        headers=_ghl_headers(),
        timeout=20,
    )
    if not response.ok:
        raise GHLStatusError(
            "Unable to stop stale Hold Return Journey: "
            f"HTTP {response.status_code}"
        )


@app.route("/ghl/hold-return-guard", methods=["POST"])
def hold_return_guard():
    """Fail closed before Returning or Completed lifecycle mutations."""
    data = request.get_json(silent=True) or {}
    contact_id = str(data.get("contact_id", "")).strip()
    contact_name = str(data.get("contact_name", "")).strip() or "Unknown"
    phase = str(data.get("phase", "")).strip().lower()
    if not contact_id or phase not in {"returning", "completed"}:
        return jsonify(
            {"status": "exception", "error": "Invalid Hold Return payload"}
        ), 400

    checked_at = datetime.now(BRISBANE_TZ).isoformat()
    try:
        fields = get_ghl_contact_fields(contact_id)
        mismatch = validate_hold_return_cycle(fields, phase)
        if mismatch:
            update_ghl_fields(
                contact_id,
                {
                    "hold_return_guard_status": "Exception",
                    "hold_return_guard_result": mismatch,
                    "hold_return_guard_checked_at": checked_at,
                },
            )
            task_created = create_hold_return_exception_task(
                contact_id,
                mismatch,
                contact_name=contact_name,
            )
            stopped = False
            try:
                stop_hold_return_workflow(contact_id)
                stopped = True
            except GHLStatusError as exc:
                log.error("HOLD RETURN WORKFLOW STOP FAILED: %s", exc)
            return jsonify(
                {
                    "status": "exception",
                    "error": mismatch,
                    "workflow_stopped": stopped,
                    "task_created": task_created,
                }
            ), 200

        guard_status = (
            "Passed - Returning"
            if phase == "returning"
            else "Passed - Completed"
        )
        result = (
            f"Accepted current cycle verified for {phase} write on "
            f"{datetime.now(BRISBANE_TZ).date()}"
        )
        update_ghl_fields(
            contact_id,
            {
                "hold_return_guard_status": guard_status,
                "hold_return_guard_result": result,
                "hold_return_guard_checked_at": checked_at,
            },
        )
        return jsonify(
            {"status": "passed", "phase": phase, "result": result}
        ), 200
    except GHLStatusError as exc:
        message = f"Hold Return guard could not verify GHL state: {exc}"
        log.error(message)
        create_hold_return_exception_task(
            contact_id,
            message,
            contact_name=contact_name,
        )
        return jsonify({"status": "exception", "error": message}), 502
def normalise_pt_hold_type(value):
    return str(value or "").strip().lower() in {
        "pt",
        "personal training",
    }


def validate_live_pt_hold(
    contact_id,
    hold_start_date,
    hold_end_date,
    mode,
):
    fields = get_ghl_contact_fields(contact_id)
    if not normalise_pt_hold_type(fields.get("hold_type")):
        raise PTHoldClearanceError("Live hold type is not PT")

    lifecycle_status = str(
        fields.get("hold_lifecycle_status", "")
    ).strip()
    if lifecycle_status not in {"Pending Hold", "On Hold"}:
        raise PTHoldClearanceError(
            "Live PT hold is not approved and pending/active"
        )

    try:
        live_start = parse_ghl_date(fields.get("hold_start"))
        live_end = parse_ghl_date(fields.get("hold_end"))
    except (TypeError, ValueError) as exc:
        raise PTHoldClearanceError(
            f"Live PT hold dates are invalid: {exc}"
        ) from exc
    if live_start != hold_start_date or live_end != hold_end_date:
        raise PTHoldClearanceError(
            "Requested clearance dates do not match the live PT hold"
        )

    billing_status = str(fields.get("hold_status", "")).strip()
    if mode == "apply" and billing_status != "Succeeded":
        raise PTHoldClearanceError(
            "Billing pause is not confirmed Succeeded; no appointments changed"
        )
    return fields


def run_pt_hold_clearance(
    contact_id,
    hold_start_date,
    hold_end_date,
    mode="preview",
    now=None,
):
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    events = get_pt_hold_calendar_events(
        contact_id,
        hold_start_date,
        hold_end_date,
    )
    records = []
    for event in sorted(
        events,
        key=lambda item: str(item.get("startTime", "")),
    ):
        decision, reason = classify_pt_hold_event(
            event,
            hold_start_date,
            hold_end_date,
            now=now,
        )
        records.append(
            {
                "event": event,
                "decision": decision,
                "reason": reason,
                "result": "preview" if mode == "preview" else "planned",
            }
        )

    counts = {
        decision: sum(
            1 for record in records if record["decision"] == decision
        )
        for decision in ("delete", "cancel", "manual_review", "skip")
    }
    if mode == "preview":
        return {
            "status": "preview",
            "counts": counts,
            "records": records,
        }

    if not any(
        record["decision"] in {"delete", "cancel", "manual_review"}
        for record in records
    ):
        counts["failed"] = 0
        return {
            "status": "ok",
            "counts": counts,
            "records": records,
        }

    run_key = pt_hold_clearance_run_key(
        contact_id,
        hold_start_date,
        hold_end_date,
    )
    title = pt_hold_audit_title(hold_start_date, hold_end_date)
    planned_section = format_pt_hold_audit_section(
        run_key,
        "PLANNED",
        hold_start_date,
        hold_end_date,
        records,
        now=now,
    )
    write_pt_hold_audit_note(contact_id, title, planned_section)

    if counts["manual_review"]:
        for record in records:
            if record["decision"] in {"delete", "cancel"}:
                record["result"] = "not processed; review required"
            elif record["decision"] == "manual_review":
                record["result"] = "needs review"
            else:
                record["result"] = "skipped"
        review_section = format_pt_hold_audit_section(
            run_key,
            "NEEDS REVIEW — NO MUTATIONS",
            hold_start_date,
            hold_end_date,
            records,
        )
        write_pt_hold_audit_note(contact_id, title, review_section)
        return {
            "status": "needs_review",
            "counts": counts,
            "records": records,
        }

    mutation_failed = False
    for record in records:
        decision = record["decision"]
        if decision == "skip":
            record["result"] = "skipped"
            continue
        if mutation_failed:
            record["result"] = "not processed after earlier failure"
            continue
        event_id = str(record["event"].get("id", "")).strip()
        try:
            if decision == "delete":
                record["result"] = delete_pt_hold_event(event_id)
            elif decision == "cancel":
                record["result"] = cancel_late_pt_hold_event(record["event"])
        except PTHoldClearanceError as exc:
            record["result"] = f"failed: {exc}"
            mutation_failed = True

    final_phase = "PARTIAL FAILURE" if mutation_failed else "COMPLETED"
    final_section = format_pt_hold_audit_section(
        run_key,
        final_phase,
        hold_start_date,
        hold_end_date,
        records,
    )
    write_pt_hold_audit_note(contact_id, title, final_section)
    counts["failed"] = sum(
        1 for record in records if record["result"].startswith("failed:")
    )
    return {
        "status": "partial_failure" if mutation_failed else "ok",
        "counts": counts,
        "records": records,
    }


def clearance_response_payload(result):
    return {
        "status": result["status"],
        "counts": result["counts"],
        "appointments": [
            {
                "event_id": record["event"].get("id"),
                "calendar_id": record["event"].get("calendarId"),
                "start_time": record["event"].get("startTime"),
                "decision": record["decision"],
                "result": record["result"],
                "reason": record["reason"],
            }
            for record in result["records"]
        ],
    }


@app.route("/ghl/pt-hold-clearance", methods=["POST"])
def pt_hold_clearance():
    supplied_secret = request.headers.get(
        "X-PT-Hold-Clearance-Secret", ""
    )
    if (
        not PT_HOLD_CLEARANCE_SECRET
        or not supplied_secret
        or not hmac.compare_digest(
            supplied_secret,
            PT_HOLD_CLEARANCE_SECRET,
        )
    ):
        return jsonify({"status": "exception", "error": "Unauthorized"}), 401

    data = request.get_json(silent=True) or {}
    contact_id = str(data.get("contact_id", "")).strip()
    hold_start_str = str(data.get("hold_start_date", "")).strip()
    hold_end_str = str(data.get("hold_end_date", "")).strip()
    hold_type = data.get("hold_type", "")
    mode = str(data.get("mode", "preview")).strip().lower()
    if (
        not contact_id
        or not hold_start_str
        or not hold_end_str
        or not normalise_pt_hold_type(hold_type)
        or mode not in {"preview", "apply"}
    ):
        return jsonify(
            {"status": "exception", "error": "Invalid clearance payload"}
        ), 400

    try:
        hold_start_date = parse_date(hold_start_str)
        hold_end_date = parse_date(hold_end_str)
        if hold_end_date <= hold_start_date:
            raise PTHoldClearanceError(
                "Hold End Date must be after Hold Start Date"
            )
        validate_live_pt_hold(
            contact_id,
            hold_start_date,
            hold_end_date,
            mode,
        )
        result = run_pt_hold_clearance(
            contact_id,
            hold_start_date,
            hold_end_date,
            mode=mode,
        )
        status_code = {
            "preview": 200,
            "ok": 200,
            "needs_review": 409,
            "partial_failure": 502,
        }[result["status"]]
        return jsonify(clearance_response_payload(result)), status_code
    except (ValueError, PTHoldClearanceError, GHLStatusError) as exc:
        log.error(
            "PT HOLD CLEARANCE STOPPED: contact=%s | error=%s",
            contact_id,
            exc,
        )
        return jsonify(
            {"status": "exception", "error": str(exc)}
        ), 422


def record_exception(
    contact_id,
    action,
    message,
    contact_name="Unknown",
    requested_action="",
):
    """Record an exception and create the owned Admin Eve handoff."""
    status_written = False
    try:
        update_ghl_status(contact_id, action, "Exception", error=message)
        status_written = True
    except GHLStatusError as exc:
        log.error("GHL STATUS WRITE FAILED: %s", exc)
    create_admin_exception_task(
        contact_id,
        action,
        message,
        contact_name=contact_name,
        requested_action=requested_action,
    )
    return status_written


def resolve_contact_id(data, email=""):
    """Resolve the GHL contact from standard or custom webhook payload data."""
    nested_contact = data.get("contact") if isinstance(data, dict) else None
    candidates = [
        ghl_payload_value(data, "contact_id", "contactId"),
        nested_contact.get("id") if isinstance(nested_contact, dict) else "",
    ]
    for candidate in candidates:
        if candidate:
            return str(candidate).strip()

    if not email:
        return ""
    try:
        response = requests.get(
            f"{GHL_BASE_URL}/contacts/",
            headers=_ghl_headers(),
            params={
                "locationId": GHL_LOCATION_ID,
                "query": email,
                "limit": 20,
            },
            timeout=20,
        )
        if not response.ok:
            raise GHLStatusError(
                f"Unable to search GHL contacts: HTTP {response.status_code}"
            )
        contacts = response.json().get("contacts", [])
        exact = [
            contact
            for contact in contacts
            if str(contact.get("email", "")).strip().lower() == email.lower()
        ]
        if len(exact) == 1:
            return str(exact[0].get("id", "")).strip()
        if len(exact) > 1:
            raise GHLStatusError(
                "Multiple GHL contacts share the cancellation email"
            )
    except (requests.RequestException, GHLStatusError) as exc:
        log.error("GHL CONTACT RESOLUTION FAILED: %s", exc)
    return ""


def cancellation_workflow_id(cancellation_type):
    normalized = str(cancellation_type or "").strip().lower()
    if normalized in {"pt", "personal training"} or "personal training" in normalized:
        return CANCELLATION_WORKFLOW_IDS["pt"]
    return CANCELLATION_WORKFLOW_IDS["membership"]


def stop_failed_cancellation(contact_id, cancellation_type):
    """Remove a failed cancellation from its workflow before confirmations run."""
    if not contact_id:
        raise GHLStatusError(
            "Cannot stop cancellation workflow without a contact_id"
        )
    workflow_id = cancellation_workflow_id(cancellation_type)
    response = requests.delete(
        f"{GHL_BASE_URL}/contacts/{contact_id}/workflow/{workflow_id}",
        headers=_ghl_headers(),
        timeout=20,
    )
    if not response.ok:
        raise GHLStatusError(
            "Unable to stop failed cancellation workflow: "
            f"HTTP {response.status_code}"
        )


def fail_cancellation(
    contact_id,
    cancellation_type,
    message,
    status_code,
    contact_name="Unknown",
    notice_end_date="",
):
    """Write the exception and fail closed before any member confirmation."""
    requested_action = (
        f"{cancellation_type or 'Membership'} cancellation"
        + (
            f" with notice ending {notice_end_date}"
            if notice_end_date
            else ""
        )
    )
    status_written = bool(
        record_exception(
            contact_id,
            "cancellation",
            message,
            contact_name=contact_name,
            requested_action=requested_action,
        )
    )
    stopped = False
    try:
        stop_failed_cancellation(contact_id, cancellation_type)
        stopped = True
    except GHLStatusError as exc:
        log.error("CANCELLATION WORKFLOW STOP FAILED: %s", exc)
    payload = {
        "status": "exception",
        "error": message,
        "workflow_stopped": stopped,
        "status_written": status_written,
    }
    return jsonify(payload), status_code


def stripe_idempotency_key(action, contact_id, *parts):
    raw = "|".join([action, contact_id, *[str(part) for part in parts]])
    return f"billing-os-{action}-{hashlib.sha256(raw.encode()).hexdigest()[:32]}"


def service_change_boundary(effective_date):
    return int(
        datetime.combine(
            effective_date,
            time.min,
            tzinfo=BRISBANE_TZ,
        ).timestamp()
    )


def approved_service_change_offers():
    """Return the deployment-owned allowlist of approved target prices."""
    raw = os.environ.get("SERVICE_CHANGE_OFFERS_JSON", "").strip()
    if not raw:
        raise ValueError(
            "SERVICE_CHANGE_OFFERS_JSON is required for automatic service changes"
        )
    try:
        offers = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError("SERVICE_CHANGE_OFFERS_JSON is invalid JSON") from exc
    if not isinstance(offers, dict) or not offers:
        raise ValueError("SERVICE_CHANGE_OFFERS_JSON must contain approved offers")
    return offers


def approved_service_change_offer(target_service):
    normalized = str(target_service or "").strip().lower().replace("-", "_")
    offer = approved_service_change_offers().get(normalized)
    if not isinstance(offer, dict):
        raise ValueError("Target service is not approved for automatic fulfilment")
    required = ("price_id", "weekly_price_cents", "service_name", "service_type")
    missing = [key for key in required if not offer.get(key)]
    if missing:
        raise ValueError(
            "Approved target service is missing configuration: "
            + ", ".join(missing)
        )
    return normalized, {
        **offer,
        "weekly_price_cents": int(offer["weekly_price_cents"]),
    }


def service_change_notice_boundary(subscription, request_date):
    """Return the first weekly Stripe boundary after 30 paid days."""
    notice_boundary = datetime.combine(
        request_date + timedelta(days=30),
        time.min,
        tzinfo=BRISBANE_TZ,
    )
    notice_boundary_ts = int(notice_boundary.timestamp())
    current_period_end = int(subscription.get("current_period_end") or 0)
    if not current_period_end:
        raise ValueError("Current subscription has no billing-period boundary")
    if subscription_weekly_amount(subscription) <= 0:
        raise ValueError("Current subscription has no valid weekly amount")
    if current_period_end >= notice_boundary_ts:
        return current_period_end
    return current_period_end + (
        math.ceil((notice_boundary_ts - current_period_end) / (7 * 86400))
        * 7
        * 86400
    )


def next_subscription_boundary(subscription, request_date):
    """Return the next normal weekly boundary, without a notice delay."""
    boundary_ts = int(subscription.get("current_period_end") or 0)
    if not boundary_ts:
        raise ValueError("Current subscription has no billing-period boundary")
    boundary_date = datetime.fromtimestamp(
        boundary_ts, BRISBANE_TZ
    ).date()
    if boundary_date < request_date:
        raise ValueError("Current subscription billing boundary is stale")
    return boundary_ts


def approved_waived_service_boundary(
    subscription,
    request_date,
    service_effective_date,
):
    """Return the next debit boundary funding an approved service week.

    The signed service date must be a Monday and fall from the debit boundary
    through the following six calendar days. This keeps the commercial service
    boundary distinct from an earlier advance-payment timestamp.
    """
    if service_effective_date.weekday() != 0:
        raise ValueError("Waived Strong service effective date must be a Monday")
    boundary_ts = next_subscription_boundary(subscription, request_date)
    boundary_date = datetime.fromtimestamp(boundary_ts, BRISBANE_TZ).date()
    if not (
        boundary_date <= service_effective_date
        <= boundary_date + timedelta(days=6)
    ):
        raise ValueError(
            "Waived Strong service date is not funded by the next normal "
            "weekly billing boundary"
        )
    return boundary_ts


def validate_notice_waiver_evidence(data, service_effective_date):
    """Fail closed unless the signed request carries complete owner approval."""
    status = str(data.get("notice_waiver_status") or "").strip()
    approved_by = str(data.get("notice_waiver_approved_by") or "").strip()
    approved_at_text = str(data.get("notice_waiver_approved_at") or "").strip()
    reason = str(data.get("notice_waiver_reason") or "").strip()
    final_prior_text = str(data.get("final_prior_service_date") or "").strip()
    if status != "Approved":
        raise ValueError("Notice waiver status must be Approved")
    if approved_by != "Peter Brown":
        raise ValueError("Notice waiver must be approved by Peter Brown")
    if not approved_at_text:
        raise ValueError("Notice waiver approval timestamp is required")
    try:
        approved_at = datetime.fromisoformat(
            approved_at_text.replace("Z", "+00:00")
        )
    except ValueError as exc:
        raise ValueError(
            "Notice waiver approval timestamp must be ISO 8601"
        ) from exc
    if approved_at.tzinfo is None:
        raise ValueError("Notice waiver approval timestamp requires a timezone")
    if not reason:
        raise ValueError("Notice waiver reason is required")
    if not final_prior_text:
        raise ValueError("Final prior service date is required")
    final_prior_date = parse_date(final_prior_text)
    if final_prior_date != service_effective_date - timedelta(days=1):
        raise ValueError(
            "Final prior service date must be the day before the Strong "
            "service effective date"
        )
    return {
        "notice_waiver_status": status,
        "notice_waiver_approved_by": approved_by,
        "notice_waiver_approved_at": approved_at.isoformat(),
        "notice_waiver_reason": reason,
        "final_prior_service_date": final_prior_date.isoformat(),
    }


def notice_waiver_requested(value):
    """Interpret the governed GHL waiver status used by the reusable workflow."""
    if value is True:
        return True
    return str(value or "").strip().lower() in {"true", "approved"}


def add_calendar_months(value, months):
    """Add calendar months without turning a 12-month term into 365 days."""
    month_index = value.month - 1 + int(months)
    year = value.year + month_index // 12
    month = month_index % 12 + 1
    day = min(value.day, calendar.monthrange(year, month)[1])
    return value.replace(year=year, month=month, day=day)


def weekly_boundary_on_or_after(start_ts, target_date):
    """Return the first seven-day billing boundary on/after target_date."""
    start = datetime.fromtimestamp(start_ts, BRISBANE_TZ)
    target = datetime.combine(target_date, start.timetz())
    if target <= start:
        return start_ts
    return start_ts + math.ceil(
        (target.timestamp() - start_ts) / (7 * 86400)
    ) * 7 * 86400


def subscription_weekly_amount(subscription):
    items = subscription.get("items", {}).get("data", [])
    if len(items) != 1:
        raise ValueError(
            "Service-change billing requires exactly one subscription item"
        )
    plan = items[0].get("plan") or items[0].get("price") or {}
    interval = plan.get("interval") or (plan.get("recurring") or {}).get(
        "interval"
    )
    interval_count = int(
        plan.get("interval_count")
        or (plan.get("recurring") or {}).get("interval_count")
        or 1
    )
    amount = plan.get("amount")
    if amount is None:
        amount = plan.get("unit_amount")
    if interval != "week" or interval_count != 1 or amount is None:
        raise ValueError(
            "Service-change billing requires one weekly recurring price"
        )
    return int(amount)


def validate_target_price(price, offer):
    if str(price.get("id") or "") != str(offer["price_id"]):
        raise ValueError("Stripe target price does not match the approved offer")
    if not price.get("active", True):
        raise ValueError("Approved Stripe target price is inactive")
    if str(price.get("currency") or "").lower() != "aud":
        raise ValueError("Approved Stripe target price must use AUD")
    recurring = price.get("recurring") or {}
    if (
        recurring.get("interval") != "week"
        or int(recurring.get("interval_count") or 1) != 1
        or int(price.get("unit_amount") or 0)
        != int(offer["weekly_price_cents"])
    ):
        raise ValueError(
            "Stripe target price does not match the approved weekly amount"
        )


def exact_service_change_schedule(
    schedules,
    *,
    request_id,
    boundary_ts,
    target_price_cents,
    reversion_ts=None,
    original_price_cents=None,
):
    matches = []
    for schedule in schedules:
        if schedule.get("status") not in {"not_started", "active"}:
            continue
        metadata = schedule.get("metadata") or {}
        same_request = str(metadata.get("service_change_request_id") or "") == request_id
        phase = schedule_target_phase(
            schedule,
            boundary_ts,
            target_price_cents,
        )
        if phase and reversion_ts:
            phase = schedule_target_phase(
                schedule,
                reversion_ts,
                int(original_price_cents or 0),
            )
        if same_request or phase:
            if not phase:
                raise ValueError(
                    "Existing request schedule does not match the approved boundary"
                )
            matches.append(schedule)
    if len(matches) > 1:
        raise ValueError("Multiple Stripe schedules match the service change")
    return matches[0] if matches else None


def schedule_phase_weekly_amount(phase):
    items = phase.get("items") or []
    if len(items) != 1:
        return None
    quantity = int(items[0].get("quantity") or 1)
    price = items[0].get("price")
    if isinstance(price, str):
        price = stripe.Price.retrieve(price)
    recurring = (price or {}).get("recurring") or {}
    if (
        recurring.get("interval") != "week"
        or int(recurring.get("interval_count") or 1) != 1
    ):
        return None
    return int((price or {}).get("unit_amount") or 0) * quantity


def commitment_phase_defaults(phase):
    """Carry forward Stripe billing settings that must survive phase updates."""
    unsupported = [
        key
        for key in ("add_invoice_items", "coupon", "discounts", "trial", "trial_end")
        if phase.get(key) not in (None, "", [], {}, False)
    ]
    if unsupported:
        raise ValueError(
            "Strong schedule has billing adjustments requiring manual review: "
            + ", ".join(unsupported)
        )
    allowed = {
        "application_fee_percent",
        "automatic_tax",
        "billing_cycle_anchor",
        "billing_thresholds",
        "collection_method",
        "currency",
        "default_payment_method",
        "default_tax_rates",
        "description",
        "invoice_settings",
        "on_behalf_of",
        "transfer_data",
    }
    return {
        key: phase[key]
        for key in allowed
        if phase.get(key) not in (None, "")
    }


def commitment_dates(boundary_ts, term_months):
    effective_at = datetime.fromtimestamp(boundary_ts, BRISBANE_TZ)
    anniversary = add_calendar_months(
        effective_at, int(term_months)
    ).date()
    reversion_ts = weekly_boundary_on_or_after(boundary_ts, anniversary)
    return (
        effective_at,
        reversion_ts,
        add_calendar_months(
            datetime.fromtimestamp(reversion_ts, BRISBANE_TZ), -2
        ).date(),
    )


def commitment_schedule_phases(
    *,
    request_id,
    offer,
    boundary_ts,
    reversion_ts,
    source_phase,
    include_current_phase=None,
):
    defaults = commitment_phase_defaults(source_phase)
    phases = []
    if include_current_phase:
        current_metadata = dict(include_current_phase.get("metadata") or {})
        phases.append(
            {
                **commitment_phase_defaults(include_current_phase),
                "start_date": int(include_current_phase["start_date"]),
                "end_date": boundary_ts,
                "items": [{
                    "price": offer["original_price_id"],
                    "quantity": 1,
                }],
                "metadata": {
                    **current_metadata,
                    "service_change_request_id": request_id,
                    "commitment_pre_discount": "true",
                },
                "proration_behavior": "none",
            }
        )
    phases.extend(
        [
            {
                **defaults,
                "start_date": boundary_ts,
                "end_date": reversion_ts,
                "items": [{
                    "price": offer["price_id"],
                    "quantity": 1,
                }],
                "metadata": {
                    "service_change_request_id": request_id,
                    "commitment_offer_version": str(
                        offer.get("offer_version") or ""
                    ),
                    "commitment_weekly_discount_cents": str(
                        offer.get("weekly_discount_cents") or ""
                    ),
                    "commitment_maximum_clawback_cents": str(
                        offer.get("maximum_clawback_cents") or ""
                    ),
                    "commitment_end_ts": str(reversion_ts),
                },
                "proration_behavior": "none",
            },
            {
                **defaults,
                "start_date": reversion_ts,
                "items": [{
                    "price": offer["original_price_id"],
                    "quantity": 1,
                }],
                "metadata": {
                    "service_change_request_id": request_id,
                    "commitment_reverted": "true",
                },
                "proration_behavior": "none",
            },
        ]
    )
    return phases


def schedule_existing_strong_commitment(
    *,
    schedules,
    subscriptions,
    customer_id,
    contact_id,
    request_id,
    request_date,
    supplied_effective_date,
    offer,
    execute,
):
    """Modify one existing A$99 schedule without creating parallel billing."""
    original_cents = int(offer["original_weekly_price_cents"])
    candidates = []
    for schedule in schedules:
        if schedule.get("status") not in {"active", "not_started"}:
            continue
        if any(
            schedule_phase_weekly_amount(phase) == original_cents
            for phase in schedule.get("phases") or []
        ):
            candidates.append(schedule)
    if not candidates:
        return None
    if len(candidates) != 1:
        raise ValueError(
            "Expected exactly one active or future Strong billing schedule"
        )
    schedule = candidates[0]
    metadata = schedule.get("metadata") or {}
    existing_request = str(
        metadata.get("service_change_request_id") or ""
    )
    if existing_request and existing_request != request_id:
        raise ValueError(
            "Strong billing schedule already belongs to another request"
        )

    include_current = None
    subscription_id = None
    if schedule.get("status") == "not_started":
        phases = schedule.get("phases") or []
        if not phases or not int(phases[0].get("start_date") or 0):
            raise ValueError("Future Strong schedule has no start boundary")
        boundary_ts = int(phases[0]["start_date"])
        if boundary_ts < int(
            datetime.combine(
                request_date, time.min, tzinfo=BRISBANE_TZ
            ).timestamp()
        ):
            raise ValueError("Future Strong schedule start boundary is stale")
        source_phase = phases[0]
    else:
        matching_subscriptions = [
            subscription
            for subscription in subscriptions
            if str(subscription.get("schedule") or "") == str(schedule["id"])
            and subscription_weekly_amount(subscription) == original_cents
        ]
        if len(matching_subscriptions) != 1:
            raise ValueError(
                "Expected one A$99 subscription controlled by the Strong schedule"
            )
        current_subscription = matching_subscriptions[0]
        if current_subscription.get("pause_collection"):
            raise ValueError("Current subscription is paused; commitment is blocked")
        boundary_ts = next_subscription_boundary(
            current_subscription, request_date
        )
        subscription_id = current_subscription["id"]
        now_ts = int(datetime.now(timezone.utc).timestamp())
        current_phases = [
            phase
            for phase in schedule.get("phases") or []
            if int(phase.get("start_date") or 0) <= now_ts
            and (
                not phase.get("end_date")
                or int(phase["end_date"]) > now_ts
            )
            and schedule_phase_weekly_amount(phase) == original_cents
        ]
        if len(current_phases) != 1:
            raise ValueError(
                "Expected one current A$99 phase in the Strong schedule"
            )
        include_current = current_phases[0]
        source_phase = include_current

    effective_at, reversion_ts, reminder_date = commitment_dates(
        boundary_ts, offer["term_months"]
    )
    effective_date = effective_at.date()
    if supplied_effective_date and parse_date(
        supplied_effective_date
    ) != effective_date:
        raise ValueError(
            "Supplied effective date does not match the exact approved "
            "weekly billing boundary"
        )
    exact_discount = schedule_target_phase(
        schedule, boundary_ts, offer["weekly_price_cents"]
    )
    exact_reversion = schedule_target_phase(
        schedule, reversion_ts, original_cents
    )
    mutation = "none"
    if not (existing_request == request_id and exact_discount and exact_reversion):
        if execute:
            stripe.SubscriptionSchedule.modify(
                schedule["id"],
                end_behavior="release",
                phases=commitment_schedule_phases(
                    request_id=request_id,
                    offer=offer,
                    boundary_ts=boundary_ts,
                    reversion_ts=reversion_ts,
                    source_phase=source_phase,
                    include_current_phase=include_current,
                ),
                proration_behavior="none",
                metadata={
                    **metadata,
                    "service_change_request_id": request_id,
                    "ghl_contact_id": contact_id,
                    "target_service": "strong_12_month_commitment",
                },
                idempotency_key=stripe_idempotency_key(
                    "strong-commitment-schedule",
                    contact_id,
                    request_id,
                    schedule["id"],
                    boundary_ts,
                    reversion_ts,
                ),
            )
            mutation = "scheduled"
    return {
        "status": "scheduled",
        "subscription_id": subscription_id,
        "schedule_id": schedule["id"],
        "boundary_ts": boundary_ts,
        "effective_at": effective_at.isoformat(),
        "effective_date": effective_date.isoformat(),
        "target_service": "strong_12_month_commitment",
        "current_price_cents": original_cents,
        "target_price_cents": int(offer["weekly_price_cents"]),
        "commitment_end_ts": reversion_ts,
        "commitment_end_date": datetime.fromtimestamp(
            reversion_ts, BRISBANE_TZ
        ).date().isoformat(),
        "continuation_reminder_date": reminder_date.isoformat(),
        "mutation": mutation if execute else "none",
        "evidence": (
            "one existing Strong schedule preserves the normal billing "
            "boundary, applies A$89 for the governed term and reverts to A$99"
        ),
    }


def schedule_service_change_billing(
    customer_id,
    *,
    contact_id,
    request_id,
    request_date,
    current_price_cents=0,
    target_service,
    supplied_effective_date="",
    notice_waived=False,
    execute=True,
):
    """Idempotently schedule the approved Stripe transition."""
    target_key, offer = approved_service_change_offer(target_service)
    target_price = stripe.Price.retrieve(offer["price_id"])
    validate_target_price(target_price, offer)

    subscriptions = stripe.Subscription.list(
        customer=customer_id,
        status="all",
        limit=20,
    ).data
    relevant = [
        subscription
        for subscription in subscriptions
        if subscription.get("status")
        in {"active", "trialing", "past_due", "unpaid"}
    ]
    is_commitment = int(offer.get("term_months") or 0) > 0
    signed_service_date = None
    if notice_waived:
        if not offer.get("allow_notice_waiver"):
            raise ValueError(
                "Target offer does not allow an owner-approved notice waiver"
            )
        if not supplied_effective_date:
            raise ValueError(
                "Owner-approved notice waiver requires a signed effective date"
            )
        signed_service_date = parse_date(supplied_effective_date)

    if is_commitment:
        original_price_id = str(offer.get("original_price_id") or "").strip()
        if not original_price_id:
            raise ValueError(
                "Strong commitment is missing the original Stripe price"
            )
        original_price = stripe.Price.retrieve(original_price_id)
        validate_target_price(
            original_price,
            {
                "price_id": original_price_id,
                "weekly_price_cents": int(
                    offer["original_weekly_price_cents"]
                ),
            },
        )
        schedules = stripe.SubscriptionSchedule.list(
            customer=customer_id,
            limit=20,
        ).data
        managed = schedule_existing_strong_commitment(
            schedules=schedules,
            subscriptions=relevant,
            customer_id=customer_id,
            contact_id=contact_id,
            request_id=request_id,
            request_date=request_date,
            supplied_effective_date=supplied_effective_date,
            offer=offer,
            execute=execute,
        )
        if managed is not None:
            return managed
    if current_price_cents:
        current = [
            subscription
            for subscription in relevant
            if subscription_weekly_amount(subscription) == current_price_cents
        ]
    else:
        current = relevant
    if len(current) != 1:
        qualifier = (
            " at the current weekly price" if current_price_cents else ""
        )
        raise ValueError(f"Expected exactly one active subscription{qualifier}")
    current_subscription = current[0]
    resolved_current_price_cents = subscription_weekly_amount(
        current_subscription
    )
    if current_subscription.get("pause_collection"):
        raise ValueError("Current subscription is paused; service change is blocked")
    if current_subscription.get("schedule"):
        raise ValueError(
            "Current subscription is schedule-managed; manual review required"
        )

    if is_commitment:
        if resolved_current_price_cents != int(
            offer.get("original_weekly_price_cents") or 0
        ):
            raise ValueError(
                "Strong commitment requires the approved original weekly price"
            )
        boundary_ts = next_subscription_boundary(
            current_subscription,
            request_date,
        )
    elif notice_waived:
        boundary_ts = approved_waived_service_boundary(
            current_subscription,
            request_date,
            signed_service_date,
        )
    else:
        boundary_ts = service_change_notice_boundary(
            current_subscription,
            request_date,
        )
    billing_boundary_at = datetime.fromtimestamp(
        boundary_ts,
        BRISBANE_TZ,
    )
    effective_at = (
        datetime.combine(
            signed_service_date,
            time.min,
            tzinfo=BRISBANE_TZ,
        )
        if notice_waived
        else billing_boundary_at
    )
    effective_date = effective_at.date()
    if supplied_effective_date and not notice_waived:
        supplied = parse_date(supplied_effective_date)
        if supplied != effective_date:
            if is_commitment:
                raise ValueError(
                    "Supplied effective date does not match the exact approved "
                    "weekly billing boundary"
                )
            raise ValueError(
                "Supplied effective date does not match the exact 30-day "
                "weekly billing boundary"
            )
    existing_cancel_at = int(current_subscription.get("cancel_at") or 0)
    if existing_cancel_at not in {0, boundary_ts}:
        raise ValueError(
            "Current subscription already has a different cancellation boundary"
        )

    reversion_ts = None
    if is_commitment:
        original_price_id = str(offer.get("original_price_id") or "").strip()
        original_offer = {
            "price_id": original_price_id,
            "weekly_price_cents": int(
                offer["original_weekly_price_cents"]
            ),
        }
        validate_target_price(original_price, original_offer)
        anniversary = add_calendar_months(
            effective_at, int(offer["term_months"])
        ).date()
        reversion_ts = weekly_boundary_on_or_after(
            boundary_ts, anniversary
        )

    schedules = stripe.SubscriptionSchedule.list(
        customer=customer_id,
        limit=20,
    ).data
    schedule = exact_service_change_schedule(
        schedules,
        request_id=request_id,
        boundary_ts=boundary_ts,
        target_price_cents=offer["weekly_price_cents"],
        reversion_ts=reversion_ts,
        original_price_cents=(
            offer.get("original_weekly_price_cents")
            if reversion_ts
            else None
        ),
    )
    created_schedule = None
    if schedule is None and execute:
        phases = [
            {
                "items": [
                    {
                        "price": offer["price_id"],
                        "quantity": 1,
                    }
                ],
                **({"end_date": reversion_ts} if reversion_ts else {}),
                "metadata": {
                    "service_change_request_id": request_id,
                    "commitment_offer_version": str(
                        offer.get("offer_version") or ""
                    ),
                    "commitment_weekly_discount_cents": str(
                        offer.get("weekly_discount_cents") or ""
                    ),
                    "commitment_maximum_clawback_cents": str(
                        offer.get("maximum_clawback_cents") or ""
                    ),
                    "commitment_end_ts": str(reversion_ts or ""),
                },
            }
        ]
        if reversion_ts:
            phases.append(
                {
                    "items": [
                        {
                            "price": original_price["id"],
                            "quantity": 1,
                        }
                    ],
                    "metadata": {
                        "service_change_request_id": request_id,
                        "commitment_reverted": "true",
                    },
                }
            )
        created_schedule = stripe.SubscriptionSchedule.create(
            customer=customer_id,
            start_date=boundary_ts,
            end_behavior="release",
            phases=phases,
            metadata={
                "service_change_request_id": request_id,
                "ghl_contact_id": contact_id,
                "target_service": target_key,
            },
            idempotency_key=stripe_idempotency_key(
                "service-change-schedule",
                contact_id,
                request_id,
                boundary_ts,
                offer["price_id"],
            ),
        )
        schedule = created_schedule
    if existing_cancel_at != boundary_ts and execute:
        try:
            stripe.Subscription.modify(
                current_subscription["id"],
                cancel_at=boundary_ts,
                proration_behavior="none",
                metadata={
                    **(current_subscription.get("metadata") or {}),
                    "service_change_request_id": request_id,
                },
                idempotency_key=stripe_idempotency_key(
                    "service-change-current-end",
                    contact_id,
                    request_id,
                    boundary_ts,
                    current_subscription["id"],
                ),
            )
        except stripe.error.StripeError:
            if created_schedule is not None:
                try:
                    stripe.SubscriptionSchedule.cancel(
                        created_schedule["id"],
                    )
                except stripe.error.StripeError:
                    log.exception(
                        "SERVICE CHANGE ROLLBACK FAILED: schedule=%s",
                        created_schedule.get("id"),
                    )
            raise

    return {
        "status": "scheduled",
        "subscription_id": current_subscription["id"],
        "schedule_id": schedule["id"] if schedule else None,
        "boundary_ts": boundary_ts,
        "billing_boundary_at": billing_boundary_at.isoformat(),
        "billing_boundary_date": billing_boundary_at.date().isoformat(),
        "effective_at": effective_at.isoformat(),
        "effective_date": effective_date.isoformat(),
        "target_service": target_key,
        "current_price_cents": resolved_current_price_cents,
        "target_price_cents": offer["weekly_price_cents"],
        "commitment_end_ts": reversion_ts,
        "commitment_end_date": (
            datetime.fromtimestamp(reversion_ts, BRISBANE_TZ).date().isoformat()
            if reversion_ts
            else None
        ),
        "continuation_reminder_date": (
            add_calendar_months(
                datetime.fromtimestamp(reversion_ts, BRISBANE_TZ), -2
            ).date().isoformat()
            if reversion_ts
            else None
        ),
        "mutation": (
            "none"
            if not execute
            or (created_schedule is None and existing_cancel_at == boundary_ts)
            else "scheduled"
        ),
        "notice_waived": bool(notice_waived),
        "evidence": (
            "current subscription end and approved A$99 schedule meet at the "
            "normal advance-payment boundary funding the signed Strong week"
            if notice_waived
            else "current subscription end and approved future weekly schedule "
            "meet at the exact 30-day billing boundary"
        ),
    }


def publish_service_change_event(event):
    if not SERVICE_CHANGE_HUB_URL or not SERVICE_CHANGE_HUB_SECRET:
        raise ValueError(
            "Operating-data hub service-change connection is not configured"
        )
    response = requests.post(
        f"{SERVICE_CHANGE_HUB_URL}/api/v1/service-changes/events",
        headers={
            "X-Hub-Secret": SERVICE_CHANGE_HUB_SECRET,
            "Content-Type": "application/json",
        },
        json=event,
        timeout=30,
    )
    if response.status_code not in {200, 409}:
        detail = ""
        try:
            detail = str(response.json().get("error") or "")
        except ValueError:
            detail = ""
        raise ValueError(
            "Operating-data hub rejected the service-change event"
            + (f": {detail}" if detail else "")
        )
    payload = response.json()
    if response.status_code == 409:
        raise ValueError(
            str(payload.get("error") or "Service-change request conflicts")
        )
    return payload


def publish_service_change_exception(requested_event, message):
    """Append one recoverable exception event after a requested event exists."""
    if not SERVICE_CHANGE_HUB_URL or not SERVICE_CHANGE_HUB_SECRET:
        return False
    status_response = requests.get(
        (
            f"{SERVICE_CHANGE_HUB_URL}/api/v1/service-changes/"
            f"{requested_event['request_id']}"
        ),
        headers={"X-Hub-Secret": SERVICE_CHANGE_HUB_SECRET},
        timeout=30,
    )
    if not status_response.ok:
        return False
    state = status_response.json()
    if state.get("status") == "accepted":
        return True
    surfaces = dict(requested_event.get("surface_statuses") or {})
    surfaces["billing"] = "exception"
    exception_event = {
        **requested_event,
        "event_type": "exception",
        "event_version": int(state.get("event_version") or 1) + 1,
        "occurred_at": datetime.now(timezone.utc).isoformat(),
        "surface_statuses": surfaces,
        "last_error": str(message)[:4000],
    }
    publish_service_change_event(exception_event)
    return True


def requested_service_change_event(data, billing_preview):
    event = data.get("hub_event")
    if not isinstance(event, dict):
        event = default_service_change_hub_event(data, billing_preview)
    event = dict(event)
    event.update(
        {
            "event_type": "requested",
            "event_version": 1,
            "request_id": str(data.get("request_id") or "").strip(),
            "canonical_key": str(data.get("email") or "").strip().lower(),
            "email": str(data.get("email") or "").strip().lower(),
            "contact_id": str(data.get("contact_id") or "").strip(),
            "request_date": parse_date(
                str(data.get("request_date") or "")
            ).isoformat(),
            "effective_date": billing_preview["effective_date"],
            "effective_at": billing_preview["effective_at"],
        }
    )
    return event


def inferred_service_type(service_name):
    normalized = str(service_name or "").strip().lower()
    if "fast track" in normalized:
        return "fast_track"
    if normalized in {"evolved anywhere", "hybrid"}:
        return "hybrid"
    if "online" in normalized:
        return "online"
    if "personal training" in normalized or normalized.startswith("pt"):
        return "personal_training"
    if any(
        marker in normalized
        for marker in ("sculpt", "strong", "fit & flexible", "membership")
    ):
        return "sgpt"
    return "other"


def default_service_change_hub_event(data, billing_preview):
    """Build the immutable request from the signed, form-scoped GHL handoff."""
    request_date = parse_date(str(data.get("request_date") or "")).isoformat()
    target_key, offer = approved_service_change_offer(
        data.get("target_service")
    )
    source_form_id = str(
        data.get("source_form_id") or offer.get("survey_id") or ""
    ).strip()
    if not source_form_id:
        raise ValueError("source_form_id is required for signed request evidence")
    configured_form_id = str(offer.get("survey_id") or "").strip()
    if configured_form_id and source_form_id != configured_form_id:
        raise ValueError(
            "Signed request source form does not match the approved target offer"
        )
    signed_at = str(data.get("signed_at") or "").strip()
    if not signed_at:
        signed_at = f"{request_date}T00:00:00+10:00"
    prior_service = (
        " ".join(str(data.get("prior_service") or "").split())
        or "Current continuing membership"
    )
    return {
        "occurred_at": signed_at,
        "offer_version": str(
            offer.get("offer_version") or f"{target_key}-v1"
        ),
        "agreement_version": str(
            offer.get("agreement_version")
            or "membership-service-change-v1"
        ),
        "signed_at": signed_at,
        "signature_document": str(
            data.get("signature_document")
            or f"ghl://survey/{source_form_id}"
        ),
        "prior_services": [
            {
                "service_type": inferred_service_type(prior_service),
                "service_name": prior_service,
                "weekly_price_cents": billing_preview[
                    "current_price_cents"
                ],
            }
        ],
        "requested_services": [
            {
                "service_type": offer["service_type"],
                "service_name": offer["service_name"],
                "weekly_price_cents": offer["weekly_price_cents"],
            }
        ],
        "surface_statuses": {
            "billing": "pending",
            "ghl": "pending",
            "trainerize": "pending",
            "appointments": "pending",
            "workbook": "pending",
            "reporting": "pending",
        },
        "source_workflow_id": str(
            data.get("source_workflow_id") or ""
        ).strip(),
        "source_submission_id": str(
            data.get("source_submission_id") or ""
        ).strip(),
    }


def service_change_request_id(data):
    """Return a stable request ID even when GHL cannot generate a UUID."""
    supplied = str(data.get("request_id") or "").strip()
    if supplied:
        return supplied
    hub_event = data.get("hub_event")
    if not isinstance(hub_event, dict):
        hub_event = {}
    parts = (
        str(data.get("contact_id") or "").strip(),
        str(data.get("target_service") or "").strip().lower(),
        str(data.get("request_date") or "").strip(),
        str(
            data.get("source_submission_id")
            or hub_event.get("signed_at")
            or data.get("signed_at")
            or data.get("source_form_id")
            or ""
        ).strip(),
        str(
            hub_event.get("signature_document")
            or data.get("signature_document")
            or data.get("source_form_id")
            or ""
        ).strip(),
    )
    if not all(parts):
        return ""
    fingerprint = hashlib.sha256("|".join(parts).encode()).hexdigest()[:24]
    return f"msc-{fingerprint}"


def schedule_target_phase(schedule, boundary_ts, target_price_cents):
    phases = schedule.get("phases", [])
    for phase in phases:
        if int(phase.get("start_date") or 0) != boundary_ts:
            continue
        items = phase.get("items") or []
        if len(items) != 1:
            continue
        price = items[0].get("price")
        if isinstance(price, str):
            price = stripe.Price.retrieve(price)
        if int((price or {}).get("unit_amount") or 0) != target_price_cents:
            continue
        recurring = (price or {}).get("recurring") or {}
        if (
            recurring.get("interval") == "week"
            and int(recurring.get("interval_count") or 1) == 1
        ):
            return phase
    return None


def verify_service_change_billing(
    customer_id,
    *,
    effective_date,
    current_price_cents,
    target_price_cents,
):
    """Return exact read-only Stripe evidence for a governed price change."""
    boundary_ts = service_change_boundary(effective_date)
    subscriptions = stripe.Subscription.list(
        customer=customer_id,
        status="all",
        limit=20,
    ).data
    relevant = [
        subscription
        for subscription in subscriptions
        if subscription.get("status")
        in {"active", "trialing", "past_due", "unpaid"}
    ]
    target_current = [
        subscription
        for subscription in relevant
        if subscription_weekly_amount(subscription) == target_price_cents
    ]
    now_ts = int(datetime.now(timezone.utc).timestamp())
    if len(target_current) == 1 and now_ts >= boundary_ts:
        return {
            "status": "succeeded",
            "subscription_id": target_current[0]["id"],
            "boundary_ts": boundary_ts,
            "mutation": "none",
            "evidence": "target weekly subscription is active at the effective boundary",
        }
    if len(target_current) > 1:
        raise ValueError(
            "Multiple active subscriptions match the target weekly price"
        )

    current = [
        subscription
        for subscription in relevant
        if subscription_weekly_amount(subscription) == current_price_cents
    ]
    if len(current) != 1:
        raise ValueError(
            "Expected exactly one active subscription at the current weekly price"
        )
    current_subscription = current[0]
    if int(current_subscription.get("cancel_at") or 0) != boundary_ts:
        raise ValueError(
            "Current subscription does not end at the approved effective boundary"
        )

    schedules = stripe.SubscriptionSchedule.list(
        customer=customer_id,
        limit=20,
    ).data
    matching_schedules = [
        schedule
        for schedule in schedules
        if schedule.get("status") in {"not_started", "active"}
        and schedule_target_phase(
            schedule,
            boundary_ts,
            target_price_cents,
        )
    ]
    if len(matching_schedules) != 1:
        raise ValueError(
            "Expected exactly one future schedule at the target weekly price"
        )
    return {
        "status": "succeeded" if now_ts >= boundary_ts else "scheduled",
        "subscription_id": current_subscription["id"],
        "schedule_id": matching_schedules[0]["id"],
        "boundary_ts": boundary_ts,
        "mutation": "none",
        "evidence": (
            "current subscription end and future weekly schedule match "
            "the approved effective boundary"
        ),
    }


def commitment_clawback_quote(
    invoices,
    *,
    discounted_price_id,
    weekly_discount_cents=1000,
    maximum_clawback_cents=52000,
):
    """Calculate discount actually received, net of payment refunds.

    This returns a quote only. It never creates an invoice or charge.
    """
    successful_discounted_payments = 0
    net_discount_cents = 0
    refunded_discount_cents = 0
    for invoice in invoices:
        if str(invoice.get("status") or "") != "paid":
            continue
        matching_quantity = 0
        for line in (invoice.get("lines") or {}).get("data", []):
            price = line.get("price") or {}
            price_id = price if isinstance(price, str) else price.get("id")
            if str(price_id or "") == discounted_price_id:
                matching_quantity += int(line.get("quantity") or 1)
        if not matching_quantity:
            continue
        successful_discounted_payments += matching_quantity
        gross_discount = weekly_discount_cents * matching_quantity
        charge = invoice.get("charge") or {}
        if isinstance(charge, str):
            charge = stripe.Charge.retrieve(charge)
        amount_paid = int(invoice.get("amount_paid") or 0)
        amount_refunded = int((charge or {}).get("amount_refunded") or 0)
        if amount_paid > 0 and amount_refunded > 0:
            refunded = min(
                gross_discount,
                round(gross_discount * amount_refunded / amount_paid),
            )
        else:
            refunded = 0
        refunded_discount_cents += refunded
        net_discount_cents += gross_discount - refunded
    return {
        "successful_discounted_payments": successful_discounted_payments,
        "gross_discount_cents": (
            successful_discounted_payments * weekly_discount_cents
        ),
        "refunded_discount_cents": refunded_discount_cents,
        "quote_cents": min(net_discount_cents, maximum_clawback_cents),
        "maximum_clawback_cents": maximum_clawback_cents,
        "collection_authorized": False,
    }


@app.route("/stripe/commitment-clawback/quote", methods=["POST"])
def quote_commitment_clawback():
    """Return and record a member-visible quote; never collect it."""
    data = request.get_json(silent=True) or {}
    contact_id = str(data.get("contact_id") or "").strip()
    email = str(data.get("email") or "").strip().lower()
    trigger = str(data.get("trigger") or "").strip().lower()
    target_service = str(
        data.get("target_service") or "strong_12_month_commitment"
    ).strip()
    if not contact_id or not email or trigger not in {
        "early_cancellation",
        "downgrade",
    }:
        return jsonify(
            {
                "status": "exception",
                "error": (
                    "contact_id, email and an eligible clawback trigger are "
                    "required"
                ),
            }
        ), 400
    try:
        _, offer = approved_service_change_offer(target_service)
        if int(offer.get("term_months") or 0) != 12:
            raise ValueError("Target offer is not the Strong commitment")
        start_ts = int(data.get("commitment_start_ts") or 0)
        end_ts = int(data.get("quote_boundary_ts") or 0)
        if not start_ts or not end_ts or end_ts <= start_ts:
            raise ValueError("Valid commitment and quote boundaries are required")
        customers = stripe.Customer.list(email=email, limit=10).data
        exact = [
            customer
            for customer in customers
            if str(customer.get("email") or "").strip().lower() == email
        ]
        if len(exact) != 1:
            raise ValueError(
                "Expected exactly one Stripe customer with the exact email"
            )
        invoices = stripe.Invoice.list(
            customer=exact[0]["id"],
            status="paid",
            created={"gte": start_ts, "lt": end_ts},
            limit=100,
            expand=["data.charge"],
        ).data
        quote = commitment_clawback_quote(
            invoices,
            discounted_price_id=offer["price_id"],
            weekly_discount_cents=int(
                offer.get("weekly_discount_cents") or 1000
            ),
            maximum_clawback_cents=int(
                offer.get("maximum_clawback_cents") or 52000
            ),
        )
        field_ids = _resolve_ghl_field_ids()
        update_ghl_fields(
            contact_id,
            {
                "service_change_clawback_quote_cents": quote["quote_cents"],
                "service_change_clawback_status": "Quoted",
            },
            field_ids=field_ids,
        )
        return jsonify(
            {
                "status": "quoted",
                "trigger": trigger,
                "member_notice_required": True,
                **quote,
            }
        ), 200
    except (
        ValueError,
        stripe.error.StripeError,
        GHLStatusError,
    ) as exc:
        message = str(exc)
        record_exception(
            contact_id,
            "service_change",
            message,
            requested_action=f"Commitment clawback quote for {trigger}",
        )
        return jsonify({"status": "exception", "error": message}), 422


@app.route("/stripe/service-change", methods=["POST"])
def service_change_billing():
    data = request.get_json(silent=True) or {}
    requested_event = None
    contact_id = str(data.get("contact_id") or "").strip()
    request_id = service_change_request_id(data)
    data["request_id"] = request_id
    email = str(data.get("email") or "").strip().lower()
    request_date_text = str(data.get("request_date") or "").strip()
    effective_date_text = str(data.get("effective_date") or "").strip()
    target_service = str(data.get("target_service") or "").strip()
    notice_waived = notice_waiver_requested(data.get("notice_waived"))
    contact_name = str(data.get("contact_name") or "Unknown").strip()
    try:
        current_price_cents = int(data.get("current_price_cents"))
        target_price_cents = int(data.get("target_price_cents") or 0)
    except (TypeError, ValueError):
        current_price_cents = 0
        target_price_cents = 0
    required = {
        "contact_id": contact_id,
        "request_id": request_id,
        "email": email,
        "request_date": request_date_text,
        "target_service": target_service,
    }
    missing = [key for key, value in required.items() if not value]
    requested_action = (
        f"Service change {request_id or 'unknown'} from "
        f"{current_price_cents or 'unknown'} to "
        f"{target_service or 'unknown'}, requested "
        f"{request_date_text or 'unknown'}"
    )
    if missing:
        message = "Missing required service-change billing fields: " + ", ".join(
            missing
        )
        record_exception(
            contact_id,
            "service_change",
            message,
            contact_name=contact_name,
            requested_action=requested_action,
        )
        return jsonify({"status": "exception", "error": message}), 400
    if target_price_cents and current_price_cents == target_price_cents:
        message = "Current and target weekly prices cannot be equal"
        record_exception(
            contact_id,
            "service_change",
            message,
            contact_name=contact_name,
            requested_action=requested_action,
        )
        return jsonify({"status": "exception", "error": message}), 422
    try:
        request_date = parse_date(request_date_text)
        waiver_evidence = None
        if notice_waived:
            if not effective_date_text:
                raise ValueError(
                    "Owner-approved notice waiver requires an effective date"
                )
            waiver_evidence = validate_notice_waiver_evidence(
                data,
                parse_date(effective_date_text),
            )
        customers = stripe.Customer.list(email=email, limit=10).data
        exact_customers = [
            customer
            for customer in customers
            if str(customer.get("email") or "").strip().lower() == email
        ]
        if len(exact_customers) != 1:
            raise ValueError(
                "Expected exactly one Stripe customer with the exact email"
            )
        preview = schedule_service_change_billing(
            exact_customers[0]["id"],
            contact_id=contact_id,
            request_id=request_id,
            request_date=request_date,
            current_price_cents=current_price_cents,
            target_service=target_service,
            supplied_effective_date=effective_date_text,
            notice_waived=notice_waived,
            execute=False,
        )
        current_price_cents = preview["current_price_cents"]
        requested_action = (
            f"Service change {request_id} from {current_price_cents} to "
            f"{target_service}, requested {request_date_text}"
        )
        if (
            target_price_cents
            and current_price_cents == target_price_cents
        ):
            raise ValueError("Current and target weekly prices cannot be equal")
        requested_event = requested_service_change_event(data, preview)
        hub_result = publish_service_change_event(requested_event)
        evidence = schedule_service_change_billing(
            exact_customers[0]["id"],
            contact_id=contact_id,
            request_id=request_id,
            request_date=request_date,
            current_price_cents=current_price_cents,
            target_service=target_service,
            supplied_effective_date=effective_date_text,
            notice_waived=notice_waived,
            execute=True,
        )
        result_text = (
            f"request={request_id}; status={evidence['status']}; "
            f"subscription={evidence['subscription_id']}; "
            f"schedule={evidence.get('schedule_id', '')}; "
            f"boundary={evidence['boundary_ts']}; "
            f"mutation={evidence['mutation']}; "
            f"hub={hub_result.get('status', '')}"
        )
        field_ids = _resolve_ghl_field_ids()
        update_ghl_fields(
            contact_id,
            {
                "service_change_effective_date": evidence["effective_date"],
                "service_change_billing_boundary_date": evidence.get(
                    "billing_boundary_date"
                ),
                "service_change_change_status": "Pending Effective Date",
                **(
                    {"service_change_notice_waiver_status": "Used"}
                    if waiver_evidence
                    else {}
                ),
                **(
                    {
                        "service_change_commitment_start_date": evidence[
                            "effective_date"
                        ],
                        "service_change_commitment_end_date": evidence[
                            "commitment_end_date"
                        ],
                        "service_change_continuation_reminder_date": evidence[
                            "continuation_reminder_date"
                        ],
                    }
                    if evidence.get("commitment_end_date")
                    else {}
                ),
            },
            field_ids=field_ids,
        )
        update_ghl_status(
            contact_id,
            "service_change",
            "Scheduled",
            result=result_text,
        )
        return jsonify(
            {
                "status": "scheduled",
                "request_id": request_id,
                "billing": evidence,
                "hub": hub_result,
            }
        ), 200
    except (
        ValueError,
        stripe.error.StripeError,
        requests.RequestException,
        GHLStatusError,
    ) as exc:
        message = str(exc)
        if requested_event is not None:
            try:
                publish_service_change_exception(requested_event, message)
            except (requests.RequestException, ValueError):
                log.exception(
                    "SERVICE CHANGE HUB EXCEPTION WRITE FAILED: request=%s",
                    request_id,
                )
        record_exception(
            contact_id,
            "service_change",
            message,
            contact_name=contact_name,
            requested_action=requested_action,
        )
        return jsonify({"status": "exception", "error": message}), 422


@app.route("/stripe/pause-hold", methods=["POST"])
def pause_hold():
    data = request.get_json(silent=True) or {}

    # 1. Validate payload
    contact_id = data.get("contact_id", "").strip()
    email = data.get("email", "").strip()
    hold_start_str = data.get("hold_start_date", "").strip()
    hold_end_str = data.get("hold_end_date", "").strip()
    pre_return_str = data.get("pre_return_date", "").strip()
    contact_name = data.get("contact_name", "Unknown")
    hold_type = data.get("hold_type", "")
    normalized_hold_type = str(hold_type).strip().lower()
    requested_action = (
        f"{hold_type or 'Membership'} hold from "
        f"{hold_start_str or 'unknown'} to {hold_end_str or 'unknown'}"
    )

    # PT value is delivered as discrete appointments. Keep it completely out
    # of the date-proration and Stripe customer-balance-credit path. Missing or
    # ambiguous evidence is expressed in the proposal itself so this branch
    # never creates a duplicate Billing OS exception task.
    if (
        normalized_hold_type in {"pt", "personal training"}
        and PT_HOLD_ENTITLEMENT_RECONCILIATION_ENABLED
    ):
        proposal = reconcile_pt_hold(data)
        log.info(
            "PT HOLD PROPOSAL: status=%s | proposal=%s | mutations=0",
            proposal["status"],
            proposal.get("proposal_id") or "review-required",
        )
        return jsonify(proposal), 200

    # Preserve the legacy blank value as Membership, but fail closed for any
    # other unknown value before a Stripe lookup or mutation.
    if normalized_hold_type not in {"", "membership", "sgpt"}:
        message = "Unsupported hold type; no billing action performed"
        log.warning("%s: %r", message, hold_type)
        record_exception(
            contact_id,
            "hold",
            message,
            contact_name=contact_name,
            requested_action=requested_action,
        )
        return jsonify({"status": "exception", "error": message}), 422

    if (
        not contact_id
        or not email
        or not hold_start_str
        or not hold_end_str
        or not pre_return_str
    ):
        message = "Missing required hold fields"
        log.warning("%s — contact=%s", message, contact_id or "unknown")
        record_exception(
            contact_id,
            "hold",
            message,
            contact_name=contact_name,
            requested_action=requested_action,
        )
        return jsonify({"error": "Missing required fields"}), 400

    try:
        hold_start_date = parse_date(hold_start_str)
        hold_end_date = parse_date(hold_end_str)
        pre_return_date = parse_date(pre_return_str)
    except ValueError as e:
        log.warning("Date parse error: %s — contact=%s", e, contact_id)
        record_exception(
            contact_id,
            "hold",
            str(e),
            contact_name=contact_name,
            requested_action=requested_action,
        )
        return jsonify({"error": str(e)}), 400

    if hold_end_date <= hold_start_date:
        message = "Hold End Date must be after Hold Start Date"
        log.warning("%s — contact=%s", message, contact_id)
        record_exception(
            contact_id,
            "hold",
            message,
            contact_name=contact_name,
            requested_action=requested_action,
        )
        return jsonify({"error": message}), 422

    expected_pre_return = hold_end_date - timedelta(days=7)
    if pre_return_date != expected_pre_return:
        message = (
            f"Pre-Return Date must equal Hold End Date minus 7 days "
            f"({expected_pre_return})"
        )
        log.warning("%s — contact=%s", message, contact_id)
        record_exception(
            contact_id,
            "hold",
            message,
            contact_name=contact_name,
            requested_action=requested_action,
        )
        return jsonify({"error": message}), 422

    try:
        # 2. Look up Stripe customer by email
        customers = stripe.Customer.list(email=email, limit=1)
        if not customers.data:
            message = "Stripe customer not found; manual pause required"
            log.error(
                "ADMIN ALERT — %s: %s (%s) | Hold type: %s | Hold: %s → %s",
                message,
                contact_name,
                email,
                hold_type,
                hold_start_date,
                hold_end_date,
            )
            record_exception(
                contact_id,
                "hold",
                message,
                contact_name=contact_name,
                requested_action=requested_action,
            )
            return jsonify({"status": "exception", "error": message}), 422

        customer = customers.data[0]
        customer_id = customer.id

        # 3. Get active subscription
        subscriptions = stripe.Subscription.list(
            customer=customer_id, status="active", limit=100
        )
        if not subscriptions.data:
            message = "No active Stripe subscription; manual pause required"
            log.error(
                "ADMIN ALERT — %s: %s (%s) | Hold type: %s | Hold: %s → %s",
                message,
                contact_name,
                email,
                hold_type,
                hold_start_date,
                hold_end_date,
            )
            record_exception(
                contact_id,
                "hold",
                message,
                contact_name=contact_name,
                requested_action=requested_action,
            )
            return jsonify({"status": "exception", "error": message}), 422

        subscription = subscriptions.data[0]
        sub_id = subscription["id"]
        idempotency_key = stripe_idempotency_key(
            "hold", contact_id, hold_start_date, hold_end_date, sub_id
        )

        # 4. Calculate overlap credit
        # If billing period extends past hold start date, member has pre-paid for days
        # during their hold — credit those days back to their customer balance.
        period_end_ts = subscription["current_period_end"]
        period_end_date = datetime.fromtimestamp(
            period_end_ts, tz=timezone.utc
        ).date()
        overlap_days = max(0, (period_end_date - hold_start_date).days)

        if overlap_days > 0:
            interval_days = get_interval_days(subscription)
            amount_cents = subscription["items"]["data"][0]["plan"]["amount"]
            daily_rate_cents = amount_cents / interval_days
            credit_cents = -round(overlap_days * daily_rate_cents)

            stripe.Customer.create_balance_transaction(
                customer_id,
                amount=credit_cents,
                currency=subscription["currency"],
                description=(
                    f"Hold overlap credit — {overlap_days} days "
                    f"from {hold_start_date} to {period_end_date}"
                ),
                idempotency_key=f"{idempotency_key}-credit",
            )
            log.info(
                "Credit applied: %s | %s days overlap | Credit: %sc %s",
                contact_name,
                overlap_days,
                abs(credit_cents),
                subscription["currency"].upper(),
            )
        else:
            log.info("No overlap credit needed for %s", contact_name)

        # 5. Calculate resumes_at from the verified GHL Pre-Return Date.
        resumes_at_ts = int(
            datetime.combine(pre_return_date, datetime.min.time())
            .replace(tzinfo=timezone.utc)
            .timestamp()
        )

        # 6. Pause subscription
        stripe.Subscription.modify(
            sub_id,
            pause_collection={"behavior": "void", "resumes_at": resumes_at_ts},
            idempotency_key=f"{idempotency_key}-pause",
        )

        result = (
            f"Paused subscription {sub_id}; hold {hold_start_date} to "
            f"{hold_end_date}; billing resumes {pre_return_date}; "
            f"overlap credit {overlap_days} day(s)"
        )
        update_ghl_status(contact_id, "hold", "Succeeded", result=result)

        log.info(
            "PAUSED: %s (%s) | sub=%s | hold=%s → %s | resumes=%s | "
            "overlap=%sd | hold_type=%s",
            contact_name,
            email,
            sub_id,
            hold_start_date,
            hold_end_date,
            pre_return_date,
            overlap_days,
            hold_type,
        )
        return jsonify({"status": "ok"}), 200
    except GHLStatusError as exc:
        log.error("Billing succeeded but GHL acknowledgement failed: %s", exc)
        create_admin_exception_task(
            contact_id,
            "hold",
            "GHL acknowledgement failed after Stripe hold",
            contact_name=contact_name,
            requested_action=requested_action,
        )
        return jsonify(
            {"status": "exception", "error": "GHL acknowledgement failed"}
        ), 502
    except Exception:
        message = "Stripe hold operation failed; manual review required"
        log.exception("%s — contact=%s", message, contact_id)
        record_exception(
            contact_id,
            "hold",
            message,
            contact_name=contact_name,
            requested_action=requested_action,
        )
        return jsonify({"status": "exception", "error": message}), 502


@app.route("/stripe/cancel", methods=["POST"])
def cancel_membership():
    data = request.get_json(silent=True) or {}

    # 1. Validate payload
    email = str(ghl_payload_value(data, "email") or "").strip()
    contact_id = resolve_contact_id(data, email)
    notice_end_str = str(
        ghl_payload_value(data, "notice_end_date", "noticeEndDate") or ""
    ).strip()
    contact_name = str(
        ghl_payload_value(data, "contact_name", "contactName") or "Unknown"
    ).strip()
    cancellation_type = str(
        ghl_payload_value(data, "cancellation_type", "cancellationType") or ""
    ).strip()

    if not contact_id or not email or not notice_end_str:
        message = "Missing required cancellation fields"
        log.warning("%s — contact=%s", message, contact_id or "unknown")
        return fail_cancellation(
            contact_id,
            cancellation_type,
            message,
            400,
            contact_name=contact_name,
            notice_end_date=notice_end_str,
        )

    try:
        notice_end_date = parse_date(notice_end_str)
    except ValueError as e:
        log.warning("Date parse error: %s — contact=%s", e, contact_id)
        return fail_cancellation(
            contact_id,
            cancellation_type,
            str(e),
            400,
            contact_name=contact_name,
            notice_end_date=notice_end_str,
        )

    try:
        # 2. Look up Stripe customer by email
        customers = stripe.Customer.list(email=email, limit=1)
        if not customers.data:
            message = "Stripe customer not found; manual cancellation required"
            log.error(
                "ADMIN ALERT — %s: %s (%s) | Cancellation type: %s | "
                "Notice end: %s",
                message,
                contact_name,
                email,
                cancellation_type,
                notice_end_date,
            )
            return fail_cancellation(
                contact_id,
                cancellation_type,
                message,
                422,
                contact_name=contact_name,
                notice_end_date=notice_end_date,
            )

        customer = customers.data[0]
        customer_id = customer.id

        # 3. Get active subscription
        subscriptions = stripe.Subscription.list(
            customer=customer_id, status="active", limit=1
        )
        if not subscriptions.data:
            message = "No active Stripe subscription; manual cancellation required"
            log.error(
                "ADMIN ALERT — %s: %s (%s) | Cancellation type: %s",
                message,
                contact_name,
                email,
                cancellation_type,
            )
            return fail_cancellation(
                contact_id,
                cancellation_type,
                message,
                422,
                contact_name=contact_name,
                notice_end_date=notice_end_date,
            )
        if len(subscriptions.data) != 1:
            message = (
                "Multiple active Stripe subscriptions; manual selection required"
            )
            log.error(
                "ADMIN ALERT — %s: %s (%s) | Cancellation type: %s",
                message,
                contact_name,
                email,
                cancellation_type,
            )
            return fail_cancellation(
                contact_id,
                cancellation_type,
                message,
                422,
                contact_name=contact_name,
                notice_end_date=notice_end_date,
            )

        subscription = subscriptions.data[0]
        sub_id = subscription["id"]

        # 4. Calculate cancel_at
        cancel_at_ts, last_payment_ts = calculate_cancellation_boundary(
            subscription, notice_end_date
        )
        cancel_at_local = datetime.fromtimestamp(
            cancel_at_ts, tz=BRISBANE_TZ
        )
        last_payment_local = datetime.fromtimestamp(
            last_payment_ts, tz=BRISBANE_TZ
        )

        # 5. Schedule cancellation. Subscription schedules own their
        # cancellation state and reject direct subscription updates. An exact
        # existing cancel_at is already authoritative, so treat it as an
        # idempotent success; otherwise route a schedule-managed case to manual
        # review instead of attempting a mutation Stripe will reject.
        existing_cancel_at = int(subscription.get("cancel_at") or 0)
        if existing_cancel_at != cancel_at_ts:
            if subscription.get("schedule"):
                message = (
                    "Stripe subscription is schedule-managed; manual schedule "
                    "update required"
                )
                log.error(
                    "ADMIN ALERT — %s: %s (%s) | sub=%s | schedule=%s",
                    message,
                    contact_name,
                    email,
                    sub_id,
                    subscription.get("schedule"),
                )
                return fail_cancellation(
                    contact_id,
                    cancellation_type,
                    message,
                    422,
                    contact_name=contact_name,
                    notice_end_date=notice_end_date,
                )
            idempotency_key = stripe_idempotency_key(
                "cancel", contact_id, notice_end_date, sub_id, cancel_at_ts
            )
            stripe.Subscription.modify(
                sub_id,
                cancel_at=cancel_at_ts,
                idempotency_key=idempotency_key,
            )

        result = (
            f"Scheduled subscription {sub_id} to cancel at "
            f"{cancel_at_local.isoformat()}; notice end {notice_end_date}; "
            f"last payment boundary {last_payment_local.isoformat()}"
        )
        update_ghl_status(
            contact_id, "cancellation", "Succeeded", result=result
        )

        log.info(
            "CANCELLATION SCHEDULED: %s (%s) | sub=%s | notice_end=%s | "
            "last_payment=%s | cancel_at=%s | cancellation_type=%s",
            contact_name,
            email,
            sub_id,
            notice_end_date,
            last_payment_local.isoformat(),
            cancel_at_local.isoformat(),
            cancellation_type,
        )
        return jsonify(
            {"status": "ok", "cancel_at": cancel_at_local.isoformat()}
        ), 200
    except GHLStatusError as exc:
        log.error("Billing succeeded but GHL acknowledgement failed: %s", exc)
        return fail_cancellation(
            contact_id,
            cancellation_type,
            "GHL acknowledgement failed after Stripe cancellation",
            502,
            contact_name=contact_name,
            notice_end_date=notice_end_date,
        )
    except Exception:
        message = "Stripe cancellation operation failed; manual review required"
        log.exception("%s — contact=%s", message, contact_id)
        return fail_cancellation(
            contact_id,
            cancellation_type,
            message,
            502,
            contact_name=contact_name,
            notice_end_date=notice_end_date,
        )


@app.route("/stripe/pt-hold/reconcile", methods=["POST"])
def reconcile_pt_hold_endpoint():
    """Build a PT entitlement proposal without mutating any live system."""
    if not PT_HOLD_ENTITLEMENT_RECONCILIATION_ENABLED:
        return jsonify({"error": "PT reconciliation is not enabled"}), 404
    proposal = reconcile_pt_hold(request.get_json(silent=True) or {})
    return jsonify(proposal), 200


@app.route("/health", methods=["GET"])
def health():
    return jsonify(
        {
            "status": "ok",
            "pt_hold_entitlement_reconciliation": (
                "enabled"
                if PT_HOLD_ENTITLEMENT_RECONCILIATION_ENABLED
                else "disabled"
            ),
            "pt_hold_clearance": {
                "configured": bool(
                    GHL_PT_CALENDAR_IDS
                    and GHL_AUTOMATION_USER_ID
                    and PT_HOLD_CLEARANCE_SECRET
                ),
                "approved_calendar_count": len(GHL_PT_CALENDAR_IDS),
            },
        }
    ), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port)
