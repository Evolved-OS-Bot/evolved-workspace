#!/usr/bin/env python3
"""Read-only preflight for approved Strong commitment candidates."""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import requests


GHL_BASE = "https://services.leadconnectorhq.com"
STRIPE_BASE = "https://api.stripe.com/v1"
BRISBANE = ZoneInfo("Australia/Brisbane")
CANDIDATES = {
    "Jodie Doran": "dG72hoBRxdPAlV2tkkfK",
    "Rene Van der Spuy": "Mgg0g4v55ZDJg8NCyPDL",
}


def load_env() -> None:
    for raw_line in (Path(__file__).parent / ".env").read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


def main() -> int:
    load_env()
    ghl_headers = {
        "Authorization": f"Bearer {os.environ['GHL_API_KEY']}",
        "Version": "2021-07-28",
        "Accept": "application/json",
    }
    stripe_auth = (os.environ["STRIPE_RESTRICTED_KEY"], "")
    for name, contact_id in CANDIDATES.items():
        contact_response = requests.get(
            f"{GHL_BASE}/contacts/{contact_id}",
            headers=ghl_headers,
            timeout=30,
        )
        contact_response.raise_for_status()
        contact = contact_response.json().get("contact", {})
        email = str(contact.get("email") or "").strip().lower()
        customers_response = requests.get(
            f"{STRIPE_BASE}/customers/search",
            auth=stripe_auth,
            params={"query": f"email:'{email}'", "limit": 10},
            timeout=30,
        )
        customers_response.raise_for_status()
        customers = [
            customer
            for customer in customers_response.json().get("data", [])
            if str(customer.get("email") or "").strip().lower() == email
        ]
        print(f"{name}: exact Stripe customers={len(customers)}")
        if len(customers) != 1:
            continue
        customer_id = customers[0]["id"]
        subscriptions_response = requests.get(
            f"{STRIPE_BASE}/subscriptions",
            auth=stripe_auth,
            params={"customer": customer_id, "status": "all", "limit": 20},
            timeout=30,
        )
        subscriptions_response.raise_for_status()
        subscriptions = subscriptions_response.json().get("data", [])
        schedules_response = requests.get(
            f"{STRIPE_BASE}/subscription_schedules",
            auth=stripe_auth,
            params={"customer": customer_id, "limit": 20},
            timeout=30,
        )
        schedules_response.raise_for_status()
        schedules = schedules_response.json().get("data", [])
        for subscription in subscriptions:
            items = (subscription.get("items") or {}).get("data", [])
            amount = (
                ((items[0].get("price") or {}).get("unit_amount"))
                if len(items) == 1
                else None
            )
            boundary = subscription.get("current_period_end")
            boundary_text = (
                datetime.fromtimestamp(boundary, BRISBANE).isoformat()
                if boundary
                else None
            )
            print(
                "  subscription "
                f"{subscription.get('status')}; weekly_cents={amount}; "
                f"next_boundary={boundary_text}; "
                f"schedule_managed={bool(subscription.get('schedule'))}"
            )
        for schedule in schedules:
            phases = schedule.get("phases") or []
            phase_summaries = []
            for phase in phases:
                items = phase.get("items") or []
                if len(items) == 1:
                    price = items[0].get("price") or {}
                    price_id = price.get("id") if isinstance(price, dict) else price
                    price_response = requests.get(
                        f"{STRIPE_BASE}/prices/{price_id}",
                        auth=stripe_auth,
                        timeout=30,
                    )
                    price_response.raise_for_status()
                    price_data = price_response.json()
                    phase_summaries.append(
                        {
                            "price_id": price_id,
                            "weekly_cents": price_data.get("unit_amount"),
                            "quantity": items[0].get("quantity"),
                            "start_date": phase.get("start_date"),
                            "end_date": phase.get("end_date"),
                            "configured_keys": sorted(
                                key
                                for key, value in phase.items()
                                if value not in (None, "", [], {})
                            ),
                        }
                    )
            print(
                "  schedule "
                f"{schedule.get('status')}; id={schedule.get('id')}; "
                f"phases={phase_summaries}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
