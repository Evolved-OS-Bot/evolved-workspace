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
from datetime import datetime, timedelta, timezone
from flask import Flask, request, jsonify
import stripe

stripe.api_key = os.environ["STRIPE_API_KEY"]

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


@app.route("/stripe/pause-hold", methods=["POST"])
def pause_hold():
    data = request.get_json(silent=True) or {}

    # 1. Validate payload
    email = data.get("email", "").strip()
    hold_start_str = data.get("hold_start_date", "").strip()
    hold_end_str = data.get("hold_end_date", "").strip()
    contact_name = data.get("contact_name", "Unknown")
    hold_type = data.get("hold_type", "")

    if not email or not hold_start_str or not hold_end_str:
        log.warning(f"Missing required fields — payload: {data}")
        return jsonify({"error": "Missing required fields"}), 400

    try:
        hold_start_date = parse_date(hold_start_str)
        hold_end_date = parse_date(hold_end_str)
    except ValueError as e:
        log.warning(f"Date parse error: {e} — payload: {data}")
        return jsonify({"error": str(e)}), 400

    # 2. Look up Stripe customer by email
    customers = stripe.Customer.list(email=email, limit=1)
    if not customers.data:
        log.error(
            f"ADMIN ALERT — Stripe customer not found: {contact_name} ({email}) | "
            f"Hold type: {hold_type} | Hold: {hold_start_date} → {hold_end_date} | "
            f"Manual Stripe pause required."
        )
        return jsonify({"status": "no_customer"}), 200

    customer = customers.data[0]
    customer_id = customer.id

    # 3. Get active subscription
    subscriptions = stripe.Subscription.list(
        customer=customer_id, status="active", limit=1
    )
    if not subscriptions.data:
        log.error(
            f"ADMIN ALERT — No active subscription: {contact_name} ({email}) | "
            f"Hold type: {hold_type} | Hold: {hold_start_date} → {hold_end_date} | "
            f"Manual Stripe pause required."
        )
        return jsonify({"status": "no_subscription"}), 200

    subscription = subscriptions.data[0]
    sub_id = subscription.id

    # 4. Calculate overlap credit
    # If billing period extends past hold start date, member has pre-paid for days
    # during their hold — credit those days back to their customer balance.
    period_end_ts = subscription["current_period_end"]
    period_end_date = datetime.fromtimestamp(period_end_ts, tz=timezone.utc).date()
    overlap_days = max(0, (period_end_date - hold_start_date).days)

    if overlap_days > 0:
        interval_days = get_interval_days(subscription)
        amount_cents = subscription["items"]["data"][0]["plan"]["amount"]
        daily_rate_cents = amount_cents / interval_days
        credit_cents = -round(overlap_days * daily_rate_cents)  # negative = credit

        stripe.Customer.create_balance_transaction(
            customer_id,
            amount=credit_cents,
            currency=subscription["currency"],
            description=(
                f"Hold overlap credit — {overlap_days} days "
                f"from {hold_start_date} to {period_end_date}"
            ),
        )
        log.info(
            f"Credit applied: {contact_name} | {overlap_days} days overlap | "
            f"Credit: {abs(credit_cents)}c {subscription['currency'].upper()}"
        )
    else:
        log.info(f"No overlap credit needed for {contact_name}")

    # 5. Calculate resumes_at
    # Per billing policy: payments resume on Pre-Return Date (hold_end_date - 7 days)
    # so the advance payment covering the return week fires on time.
    pre_return_date = hold_end_date - timedelta(days=7)
    resumes_at_ts = int(
        datetime.combine(pre_return_date, datetime.min.time())
        .replace(tzinfo=timezone.utc)
        .timestamp()
    )

    # 6. Pause subscription
    stripe.Subscription.modify(
        sub_id,
        pause_collection={"behavior": "void", "resumes_at": resumes_at_ts},
    )

    log.info(
        f"PAUSED: {contact_name} ({email}) | "
        f"sub={sub_id} | "
        f"hold={hold_start_date} → {hold_end_date} | "
        f"resumes={pre_return_date} | "
        f"overlap={overlap_days}d | "
        f"hold_type={hold_type}"
    )

    return jsonify({"status": "ok"}), 200


@app.route("/stripe/cancel", methods=["POST"])
def cancel_membership():
    data = request.get_json(silent=True) or {}

    # 1. Validate payload
    email = data.get("email", "").strip()
    notice_end_str = data.get("notice_end_date", "").strip()
    contact_name = data.get("contact_name", "Unknown")
    cancellation_type = data.get("cancellation_type", "")

    if not email or not notice_end_str:
        log.warning(f"Missing required fields — payload: {data}")
        return jsonify({"error": "Missing required fields"}), 400

    try:
        notice_end_date = parse_date(notice_end_str)
    except ValueError as e:
        log.warning(f"Date parse error: {e} — payload: {data}")
        return jsonify({"error": str(e)}), 400

    # 2. Look up Stripe customer by email
    customers = stripe.Customer.list(email=email, limit=1)
    if not customers.data:
        log.error(
            f"ADMIN ALERT — Stripe customer not found: {contact_name} ({email}) | "
            f"Cancellation type: {cancellation_type} | Notice end: {notice_end_date} | "
            f"Manual Stripe cancellation required."
        )
        return jsonify({"status": "no_customer"}), 200

    customer = customers.data[0]
    customer_id = customer.id

    # 3. Get active subscription
    subscriptions = stripe.Subscription.list(
        customer=customer_id, status="active", limit=1
    )
    if not subscriptions.data:
        log.error(
            f"ADMIN ALERT — No active subscription: {contact_name} ({email}) | "
            f"Cancellation type: {cancellation_type} | "
            f"Manual cancellation required."
        )
        return jsonify({"status": "no_subscription"}), 200

    subscription = subscriptions.data[0]
    sub_id = subscription.id

    # 4. Calculate cancel_at
    # Find the last payment date within the 30-day notice period, then set
    # cancel_at to the end of that billing period (last_payment_date + interval).
    # Policy: member pays until their last scheduled payment within notice period;
    # access ends when that period closes.
    period_start_ts = subscription["current_period_start"]
    current_period_start = datetime.fromtimestamp(period_start_ts, tz=timezone.utc).date()
    interval_days = get_interval_days(subscription)

    days_elapsed = (notice_end_date - current_period_start).days
    num_periods = max(0, days_elapsed // interval_days)
    last_payment_date = current_period_start + timedelta(days=num_periods * interval_days)
    cancel_date = last_payment_date + timedelta(days=interval_days)

    cancel_at_ts = int(
        datetime.combine(cancel_date, datetime.min.time())
        .replace(tzinfo=timezone.utc)
        .timestamp()
    )

    # 5. Schedule cancellation
    stripe.Subscription.modify(sub_id, cancel_at=cancel_at_ts)

    log.info(
        f"CANCELLATION SCHEDULED: {contact_name} ({email}) | "
        f"sub={sub_id} | "
        f"notice_end={notice_end_date} | "
        f"last_payment={last_payment_date} | "
        f"cancel_at={cancel_date} | "
        f"cancellation_type={cancellation_type}"
    )

    return jsonify({"status": "ok", "cancel_at": str(cancel_date)}), 200


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port)
