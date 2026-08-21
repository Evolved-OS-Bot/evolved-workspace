#!/usr/bin/env python3
"""Safely verify the live Billing OS exception-task handoff in GHL."""

import os
import sys
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

import requests


GHL_BASE_URL = "https://services.leadconnectorhq.com"
BRISBANE_TZ = ZoneInfo("Australia/Brisbane")


def ghl_headers():
    return {
        "Authorization": f"Bearer {os.environ['GHL_API_KEY']}",
        "Version": "2021-07-28",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


def main():
    location_id = os.environ["GHL_LOCATION_ID"]
    admin_eve_user_id = os.environ["GHL_ADMIN_EVE_USER_ID"]
    billing_os_url = os.environ.get(
        "BILLING_OS_URL",
        "https://believable-happiness-production-9870.up.railway.app",
    ).rstrip("/")
    unique = uuid.uuid4().hex[:12]
    email = f"billing-exception-test-{unique}@example.invalid"

    contact_response = requests.post(
        f"{GHL_BASE_URL}/contacts/",
        headers=ghl_headers(),
        json={
            "locationId": location_id,
            "firstName": "Billing Exception",
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
            "email": email,
            "hold_start_date": "2026-08-10",
            "hold_end_date": "2026-08-31",
            "pre_return_date": "2026-08-24",
            "contact_name": "Billing Exception Test",
            "hold_type": "Membership",
        }
        first = requests.post(
            f"{billing_os_url}/stripe/pause-hold",
            json=payload,
            timeout=30,
        )
        second = requests.post(
            f"{billing_os_url}/stripe/pause-hold",
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
        matches = [
            task
            for task in tasks_response.json().get("tasks", [])
            if task.get("title")
            == "BILLING EXCEPTION: Hold - Manual action required"
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
        if "Stripe customer not found" not in task.get("body", ""):
            raise RuntimeError("Exception task does not contain the billing error")

        print(
            "PASS: one same-day Admin Eve billing exception task was created "
            "and a retry did not duplicate it"
        )
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
    main()
