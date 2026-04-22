#!/usr/bin/env python3
"""
stripe_handler/app.py
Flask webhook handler — receives POST from GHL on Pre-Hold-Start Date.

What it does:
  1. Validates payload (email, hold_start_date, hold_end_date required)
  2. Looks up Stripe customer by email
  3. Gets active subscription
  4. Calculates and applies overlap credit if billing period extends past hold start date
  5. Pauses subscription with behavior=void, resumes on Pre-Return Date (hold_end_date - 7 days)
  6. Logs everything

Billing policy: all members pay 1 week in advance. This webhook fires on
Pre-Hold-Start Date (Hold Start Date - 7 days) to intercept the advance payment.
Billing resumes on Pre-Return Date (Hold End Date - 7 days) so the payment
covering the return week fires on time.
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


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port)
