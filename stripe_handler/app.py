#!/usr/bin/env python3
"""
stripe_handler/app.py
Flask webhook handler for GHL → Stripe automation.

Endpoints:
  POST /stripe/pause-hold    — fires on Pre-Hold-Start Date (Hold Start Date - 7 days)
  POST /stripe/cancel        — fires on cancellation form submission (Membership or PT)

Hold logic:
  Pauses subscription with behavior=void, applies overlap credit for any pre-paid
  days during the hold, resumes billing on Pre-Return Date (Hold End Date - 7 days).

Cancellation logic:
  Receives notice_end_date from GHL (CS: Notice End Date field). Finds the last
  scheduled payment within that notice period, then sets cancel_at to the end of
  that billing period (last_payment_date + interval). Access ends when that period closes.
"""

import os
import logging
import hashlib
import math
from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo
from flask import Flask, request, jsonify
import requests
import stripe

stripe.api_key = os.environ["STRIPE_API_KEY"]

GHL_API_KEY = os.environ.get("GHL_API_KEY", "")
GHL_LOCATION_ID = os.environ.get("GHL_LOCATION_ID", "")
GHL_ADMIN_EVE_USER_ID = os.environ.get("GHL_ADMIN_EVE_USER_ID", "")
GHL_BASE_URL = "https://services.leadconnectorhq.com"
GHL_FIELD_NAMES = {
    "hold_status": "Billing OS: Hold Action Status",
    "cancellation_status": "Billing OS: Cancellation Action Status",
    "last_error": "Billing OS: Last Error",
    "last_action_at": "Billing OS: Last Action At",
    "last_result": "Billing OS: Last Result",
    "hold_start": "HS: Hold Start Date",
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
    if action not in {"hold", "cancellation"}:
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

    action_label = str(action or "billing").strip().title()
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


@app.route("/ghl/hold-intake", methods=["POST"])
def hold_intake():
    data = request.get_json(silent=True) or {}
    contact_id = str(data.get("contact_id", "")).strip()
    form_kind = str(data.get("form_kind", "")).strip()
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
    nested_contact = data.get("contact")
    candidates = [
        data.get("contact_id"),
        data.get("contactId"),
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
    requested_action = (
        f"{hold_type or 'Membership'} hold from "
        f"{hold_start_str or 'unknown'} to {hold_end_str or 'unknown'}"
    )

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
    email = data.get("email", "").strip()
    contact_id = resolve_contact_id(data, email)
    notice_end_str = data.get("notice_end_date", "").strip()
    contact_name = data.get("contact_name", "Unknown")
    cancellation_type = data.get("cancellation_type", "")

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


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port)
