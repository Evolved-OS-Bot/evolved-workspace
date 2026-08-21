#!/usr/bin/env python3
"""Safely verify the live service-change exception and task deduplication path."""

from __future__ import annotations

import os
import sys
import uuid
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import requests


WORKSPACE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(WORKSPACE))

from scripts.membership_reconciliation import load_env


GHL_BASE_URL = "https://services.leadconnectorhq.com"
BRISBANE_TZ = ZoneInfo("Australia/Brisbane")


def ghl_headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {os.environ['GHL_API_KEY']}",
        "Version": "2021-07-28",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


def main() -> int:
    os.environ.update(load_env())
    location_id = os.environ["GHL_LOCATION_ID"]
    admin_eve_user_id = os.environ["GHL_ADMIN_EVE_USER_ID"]
    billing_os_url = os.environ.get(
        "BILLING_OS_URL",
        "https://believable-happiness-production-9870.up.railway.app",
    ).rstrip("/")
    unique = uuid.uuid4().hex[:12]
    request_id = f"msc-live-exception-{unique}"
    email = f"service-change-exception-{unique}@example.invalid"

    contact_response = requests.post(
        f"{GHL_BASE_URL}/contacts/",
        headers=ghl_headers(),
        json={
            "locationId": location_id,
            "firstName": "Service Change Exception",
            "lastName": "Test",
            "email": email,
        },
        timeout=20,
    )
    contact_response.raise_for_status()
    contact_id = contact_response.json()["contact"]["id"]

    try:
        payload = {
            "contact_id": contact_id,
            "request_id": request_id,
            "contact_name": "Service Change Exception Test",
            "email": email,
            "request_date": datetime.now(BRISBANE_TZ).date().isoformat(),
            "target_service": "online_only",
            "current_price_cents": 9900,
            "target_price_cents": 2700,
            "source_form_id": "XBpTy848fvJXjMtGfnu2",
        }
        first = requests.post(
            f"{billing_os_url}/stripe/service-change",
            json=payload,
            timeout=30,
        )
        second = requests.post(
            f"{billing_os_url}/stripe/service-change",
            json=payload,
            timeout=30,
        )
        if first.status_code != 422 or second.status_code != 422:
            raise RuntimeError(
                "Expected safe no-Stripe-customer exceptions, got "
                f"{first.status_code} and {second.status_code}"
            )

        tasks_response = requests.get(
            f"{GHL_BASE_URL}/contacts/{contact_id}/tasks",
            headers=ghl_headers(),
            timeout=20,
        )
        tasks_response.raise_for_status()
        accepted_titles = {
            "BILLING EXCEPTION: Service Change - Manual action required",
            "BILLING EXCEPTION: Service_Change - Manual action required",
        }
        matches = [
            task
            for task in tasks_response.json().get("tasks", [])
            if task.get("title") in accepted_titles
        ]
        if len(matches) != 1:
            raise RuntimeError(
                f"Expected one deduplicated exception task, found {len(matches)}"
            )
        task = matches[0]
        if task.get("assignedTo") != admin_eve_user_id:
            raise RuntimeError("Exception task is not assigned to Admin Eve")
        due_local = datetime.fromisoformat(
            task["dueDate"].replace("Z", "+00:00")
        ).astimezone(BRISBANE_TZ)
        if due_local.date() != datetime.now(BRISBANE_TZ).date():
            raise RuntimeError("Exception task is not due on the Brisbane test date")
        body = task.get("body", "")
        if "Expected exactly one Stripe customer" not in body:
            raise RuntimeError("Exception task does not contain the billing error")
        if request_id not in body:
            raise RuntimeError("Exception task does not identify the request")

        print(
            "PASS: one same-day Admin Eve service-change exception task was "
            "created and an exact retry did not duplicate it; title="
            f"{task.get('title')}"
        )
        return 0
    finally:
        delete_response = requests.delete(
            f"{GHL_BASE_URL}/contacts/{contact_id}",
            headers=ghl_headers(),
            timeout=20,
        )
        if not delete_response.ok:
            print(
                f"WARNING: temporary contact {contact_id} could not be deleted",
                file=sys.stderr,
            )


if __name__ == "__main__":
    raise SystemExit(main())
