#!/usr/bin/env python3
"""Safely verify live Hold Return current-cycle guards with disposable contacts."""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import requests


GHL_BASE_URL = "https://services.leadconnectorhq.com"
BILLING_OS_URL = (
    "https://believable-happiness-production-9870.up.railway.app"
)
FIELD_NAMES = {
    "hold_status": "HS: Hold Status",
    "hold_start": "HS: Hold Start Date",
    "hold_end": "HS: Hold End Date",
    "pre_return": "HS: Pre-Return Date",
    "request_hold_start": "HS Request: Hold Start Date",
    "request_intake_status": "HS Request: Intake Status",
    "guard_status": "HS: Return Guard Status",
}
BRISBANE_TZ = ZoneInfo("Australia/Brisbane")


def load_env():
    values = dict(os.environ)
    env_path = Path(__file__).parent / ".env"
    for raw in env_path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values.setdefault(key, value.strip().strip('"').strip("'"))
    return values


ENV = load_env()
LOCATION_ID = ENV["GHL_LOCATION_ID"]
HEADERS = {
    "Authorization": f"Bearer {ENV['GHL_API_KEY']}",
    "Version": "2021-07-28",
    "Content-Type": "application/json",
    "Accept": "application/json",
}


def field_ids():
    response = requests.get(
        f"{GHL_BASE_URL}/locations/{LOCATION_ID}/customFields",
        headers=HEADERS,
        params={"model": "contact"},
        timeout=30,
    )
    response.raise_for_status()
    by_name = {
        item["name"]: item["id"]
        for item in response.json().get("customFields", [])
    }
    missing = [name for name in FIELD_NAMES.values() if name not in by_name]
    if missing:
        raise RuntimeError("Missing Hold Return fields: " + ", ".join(missing))
    return {key: by_name[name] for key, name in FIELD_NAMES.items()}


def create_contact(suffix):
    response = requests.post(
        f"{GHL_BASE_URL}/contacts/",
        headers=HEADERS,
        json={
            "locationId": LOCATION_ID,
            "firstName": "Codex",
            "lastName": f"Hold Return Guard Test {suffix}",
            "source": "Controlled Hold Return guard verification",
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["contact"]["id"]


def update_fields(contact_id, ids, values):
    response = requests.put(
        f"{GHL_BASE_URL}/contacts/{contact_id}",
        headers=HEADERS,
        json={
            "customFields": [
                {"id": ids[key], "fieldValue": value}
                for key, value in values.items()
            ]
        },
        timeout=30,
    )
    response.raise_for_status()


def read_fields(contact_id):
    response = requests.get(
        f"{GHL_BASE_URL}/contacts/{contact_id}",
        headers=HEADERS,
        timeout=30,
    )
    response.raise_for_status()
    return {
        item["id"]: item.get("fieldValue", item.get("value", ""))
        for item in response.json()["contact"].get("customFields", [])
    }


def call_guard(contact_id, phase):
    response = requests.post(
        f"{BILLING_OS_URL}/ghl/hold-return-guard",
        json={
            "contact_id": contact_id,
            "contact_name": "Controlled Hold Return Guard Test",
            "phase": phase,
        },
        timeout=30,
    )
    return response.status_code, response.json()


def open_exception_tasks(contact_id):
    response = requests.get(
        f"{GHL_BASE_URL}/contacts/{contact_id}/tasks",
        headers=HEADERS,
        timeout=30,
    )
    response.raise_for_status()
    return [
        task
        for task in response.json().get("tasks", [])
        if task.get("title")
        == "HOLD RETURN EXCEPTION: Cycle mismatch - review required"
        and not task.get("completed")
    ]


def delete_contact(contact_id):
    response = requests.delete(
        f"{GHL_BASE_URL}/contacts/{contact_id}",
        headers=HEADERS,
        timeout=30,
    )
    if response.status_code not in {200, 204}:
        raise RuntimeError(
            f"Unable to delete test contact {contact_id}: "
            f"HTTP {response.status_code}"
        )


def main():
    ids = field_ids()
    today = datetime.now(BRISBANE_TZ).date()
    normal_id = ""
    mismatch_id = ""
    try:
        normal_id = create_contact("Normal")
        update_fields(
            normal_id,
            ids,
            {
                "hold_status": "On Hold",
                "hold_start": (today - timedelta(days=7)).isoformat(),
                "hold_end": today.isoformat(),
                "pre_return": (today - timedelta(days=7)).isoformat(),
                "request_hold_start": (
                    today - timedelta(days=7)
                ).isoformat(),
                "request_intake_status": "Accepted",
            },
        )
        status_code, payload = call_guard(normal_id, "returning")
        if status_code != 200 or payload.get("status") != "passed":
            raise RuntimeError(f"Normal Returning guard failed: {payload}")
        values = read_fields(normal_id)
        if values.get(ids["guard_status"]) != "Passed - Returning":
            raise RuntimeError("Returning guard status did not read back")

        update_fields(
            normal_id,
            ids,
            {
                "hold_status": "Returning",
                "hold_start": (today - timedelta(days=10)).isoformat(),
                "hold_end": (today - timedelta(days=3)).isoformat(),
                "pre_return": (today - timedelta(days=10)).isoformat(),
                "request_hold_start": (
                    today - timedelta(days=10)
                ).isoformat(),
            },
        )
        status_code, payload = call_guard(normal_id, "completed")
        if status_code != 200 or payload.get("status") != "passed":
            raise RuntimeError(f"Normal Completed guard failed: {payload}")
        values = read_fields(normal_id)
        if values.get(ids["guard_status"]) != "Passed - Completed":
            raise RuntimeError("Completed guard status did not read back")
        if open_exception_tasks(normal_id):
            raise RuntimeError("Normal path created an exception task")

        mismatch_id = create_contact("Mismatch")
        update_fields(
            mismatch_id,
            ids,
            {
                "hold_status": "On Hold",
                "hold_start": (today + timedelta(days=20)).isoformat(),
                "hold_end": (today + timedelta(days=27)).isoformat(),
                "pre_return": (today + timedelta(days=20)).isoformat(),
                "request_hold_start": (
                    today + timedelta(days=20)
                ).isoformat(),
                "request_intake_status": "Accepted",
            },
        )
        first_code, first = call_guard(mismatch_id, "returning")
        second_code, second = call_guard(mismatch_id, "returning")
        if first_code != 200 or second_code != 200:
            raise RuntimeError("Mismatch guard did not return controlled 200")
        if first.get("status") != "exception" or second.get("status") != "exception":
            raise RuntimeError("Mismatch path did not fail closed")
        if not first.get("workflow_stopped") or not second.get("workflow_stopped"):
            raise RuntimeError("Mismatch path did not stop the workflow")
        tasks = open_exception_tasks(mismatch_id)
        if len(tasks) != 1:
            raise RuntimeError(
                f"Expected one deduplicated exception task, found {len(tasks)}"
            )
        values = read_fields(mismatch_id)
        if values.get(ids["guard_status"]) != "Exception":
            raise RuntimeError("Mismatch guard status did not read back")

        print("PASS  normal Returning guard")
        print("PASS  normal Completed guard")
        print("PASS  cross-cycle mismatch stopped")
        print("PASS  one Admin Eve exception task after retry")
    finally:
        cleanup_errors = []
        for contact_id in (normal_id, mismatch_id):
            if not contact_id:
                continue
            try:
                delete_contact(contact_id)
                print(f"CLEAN deleted temporary contact {contact_id}")
            except Exception as exc:
                cleanup_errors.append(str(exc))
        if cleanup_errors:
            print("\n".join(cleanup_errors), file=sys.stderr)
            sys.exit(2)


if __name__ == "__main__":
    main()
