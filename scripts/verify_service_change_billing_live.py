#!/usr/bin/env python3
"""Read-only live verification for a governed Stripe service change.

The default mode does not write to Stripe or GHL. It verifies that one exact
customer has the expected current weekly subscription ending at the approved
Brisbane boundary and one future weekly schedule beginning at that boundary.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.membership_reconciliation import load_env


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--email", required=True)
    parser.add_argument("--effective-date", required=True)
    parser.add_argument("--current-price-cents", required=True, type=int)
    parser.add_argument("--target-price-cents", required=True, type=int)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    os.environ.update(load_env())
    if not os.environ.get("STRIPE_API_KEY"):
        restricted_key = os.environ.get("STRIPE_RESTRICTED_KEY")
        if restricted_key:
            os.environ["STRIPE_API_KEY"] = restricted_key
    from stripe_handler.app import (
        parse_date,
        stripe,
        verify_service_change_billing,
    )

    email = args.email.strip().lower()
    customers = stripe.Customer.list(email=email, limit=10).data
    exact = [
        customer
        for customer in customers
        if str(customer.get("email") or "").strip().lower() == email
    ]
    if len(exact) != 1:
        raise RuntimeError(
            "Expected exactly one Stripe customer with the exact email"
        )
    evidence = verify_service_change_billing(
        exact[0]["id"],
        effective_date=parse_date(args.effective_date),
        current_price_cents=args.current_price_cents,
        target_price_cents=args.target_price_cents,
    )
    print(
        {
            "mode": "read_only",
            "status": evidence["status"],
            "subscription_id": evidence["subscription_id"],
            "schedule_id": evidence.get("schedule_id"),
            "boundary_ts": evidence["boundary_ts"],
            "mutation": evidence["mutation"],
            "evidence": evidence["evidence"],
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
