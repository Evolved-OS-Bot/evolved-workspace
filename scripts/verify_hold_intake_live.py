#!/usr/bin/env python3
"""Safely verify the live Billing OS hold-intake guard using a temporary GHL contact."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

import requests


GHL_BASE_URL = "https://services.leadconnectorhq.com"
BILLING_OS_URL = (
    "https://believable-happiness-production-9870.up.railway.app/ghl/hold-intake"
)

FIELD_IDS = {
    "start": "k40qV4w0HKj5KFbMnmq8",
    "weeks": "5ehOHA3T4GgAY1tGJ5i2",
    "reason": "AQAgNHACCUmEoygFk09t",
    "status": "huVhp3xNLYJDtPA9JdFA",
    "request_start": "q27VjAnQsEjFDGgeZuCW",
    "request_weeks": "zb2d6jSdRe8xgHnhy8Cu",
    "intake_status": "1x18pFJNhnyCfjsYsuWc",
}


def load_local_env() -> None:
    env_path = Path(__file__).with_name(".env")
    for line in env_path.read_text().splitlines():
        if not line or line.lstrip().startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("'\""))


def main() -> None:
    load_local_env()
    api_key = os.environ["GHL_API_KEY"]
    location_id = os.environ["GHL_LOCATION_ID"]
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Version": "2021-07-28",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    contact_id = None

    try:
        created = requests.post(
            f"{GHL_BASE_URL}/contacts/",
            headers=headers,
            json={
                "locationId": location_id,
                "firstName": "Billing OS",
                "lastName": "Hold Intake Test",
                "email": f"billing-os-hold-test-{time.time_ns()}@example.com",
            },
            timeout=30,
        )
        created.raise_for_status()
        contact_id = created.json()["contact"]["id"]

        seed = requests.put(
            f"{GHL_BASE_URL}/contacts/{contact_id}",
            headers=headers,
            json={
                "customFields": [
                    {"id": FIELD_IDS["start"], "fieldValue": "2026-08-10"},
                    {"id": FIELD_IDS["weeks"], "fieldValue": "3"},
                    {"id": FIELD_IDS["reason"], "fieldValue": "Holiday"},
                ]
            },
            timeout=30,
        )
        seed.raise_for_status()

        first = requests.post(
            BILLING_OS_URL,
            json={"contact_id": contact_id, "form_kind": "standard_membership"},
            timeout=30,
        )
        if not first.ok:
            print(
                json.dumps(
                    {
                        "hold_intake_status": first.status_code,
                        "hold_intake_response": first.text,
                    }
                )
            )
        first.raise_for_status()

        duplicate_seed = requests.put(
            f"{GHL_BASE_URL}/contacts/{contact_id}",
            headers=headers,
            json={
                "customFields": [
                    {"id": FIELD_IDS["status"], "fieldValue": "Pending Hold"},
                    {"id": FIELD_IDS["start"], "fieldValue": "2026-09-21"},
                    {"id": FIELD_IDS["weeks"], "fieldValue": "1"},
                    {"id": FIELD_IDS["reason"], "fieldValue": "Second request"},
                ]
            },
            timeout=30,
        )
        duplicate_seed.raise_for_status()

        duplicate = requests.post(
            BILLING_OS_URL,
            json={"contact_id": contact_id, "form_kind": "standard_membership"},
            timeout=30,
        )
        if not duplicate.ok:
            print(
                json.dumps(
                    {
                        "duplicate_status": duplicate.status_code,
                        "duplicate_response": duplicate.text,
                    }
                )
            )
        duplicate.raise_for_status()

        verified = requests.get(
            f"{GHL_BASE_URL}/contacts/{contact_id}",
            headers=headers,
            timeout=30,
        )
        verified.raise_for_status()
        fields = {
            item["id"]: item.get("fieldValue", item.get("value"))
            for item in verified.json()["contact"].get("customFields", [])
        }

        result = {
            "first": first.json(),
            "duplicate": duplicate.json(),
            "restored_start": fields.get(FIELD_IDS["start"]),
            "restored_weeks": fields.get(FIELD_IDS["weeks"]),
            "protected_start": fields.get(FIELD_IDS["request_start"]),
            "protected_weeks": fields.get(FIELD_IDS["request_weeks"]),
            "intake_status": fields.get(FIELD_IDS["intake_status"]),
        }
        assert result["first"]["status"] == "accepted"
        assert result["duplicate"]["status"] == "rejected_existing_hold"
        assert result["restored_start"].startswith("2026-08-10")
        assert str(result["restored_weeks"]) == "3"
        assert result["protected_start"].startswith("2026-08-10")
        assert str(result["protected_weeks"]) == "3"
        assert result["intake_status"] == "Rejected - Existing Hold"
        print(json.dumps(result, indent=2, sort_keys=True))
    finally:
        if contact_id:
            deleted = requests.delete(
                f"{GHL_BASE_URL}/contacts/{contact_id}",
                headers=headers,
                timeout=30,
            )
            print(
                json.dumps(
                    {
                        "temporary_contact_deleted": deleted.ok,
                        "delete_status": deleted.status_code,
                    }
                )
            )


if __name__ == "__main__":
    main()
