#!/usr/bin/env python3
"""Create the GHL fields required by the governed hold and Billing OS repair.

Safe to re-run: fields are matched by exact name and existing definitions are
validated before they are skipped.
"""

import os
import sys
from pathlib import Path

import requests


BASE_URL = "https://services.leadconnectorhq.com"
HOLD_FOLDER_ID = "I9yvxOR5SClRM6mhguDn"
CANCELLATION_FOLDER_ID = "6K5Faoqa02Be82SKmLv2"
STANDARD_WEEKS = ["1", "2", "3", "4"]
EXTENDED_WEEKS = ["5", "6", "7", "8", "9", "10", "11", "12"]
HOLD_REASONS = [
    "Holidays",
    "Work Travel",
    "Short-Term Injury",
    "Illness",
    "Temporary Financial Pressure",
    "Other",
]
ACTION_STATUSES = ["Not Started", "Processing", "Succeeded", "Exception"]
INTAKE_STATUSES = ["Received", "Accepted", "Rejected - Existing Hold", "Rejected - Invalid"]
RETURN_GUARD_STATUSES = [
    "Not Checked",
    "Passed - Returning",
    "Passed - Completed",
    "Exception",
]


def load_env():
    values = dict(os.environ)
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        for raw in env_path.read_text().splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            values.setdefault(key, value.strip().strip('"').strip("'"))
    return values


ENV = load_env()
API_KEY = ENV["GHL_API_KEY"]
LOCATION_ID = ENV["GHL_LOCATION_ID"]
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Version": "2021-07-28",
    "Content-Type": "application/json",
    "Accept": "application/json",
}


FIELDS = [
    {
        "name": "HS Request: Hold Start Date",
        "dataType": "DATE",
        "parentId": HOLD_FOLDER_ID,
    },
    {
        "name": "HS Request: Hold Weeks",
        "dataType": "SINGLE_OPTIONS",
        "options": STANDARD_WEEKS,
        "parentId": HOLD_FOLDER_ID,
    },
    {
        "name": "HS Request: Extended Hold Weeks",
        "dataType": "SINGLE_OPTIONS",
        "options": EXTENDED_WEEKS,
        "parentId": HOLD_FOLDER_ID,
    },
    {
        "name": "HS Request: Hold Reason",
        "dataType": "RADIO",
        "options": HOLD_REASONS,
        "parentId": HOLD_FOLDER_ID,
    },
    {
        "name": "HS Request: Hold Notes",
        "dataType": "LARGE_TEXT",
        "parentId": HOLD_FOLDER_ID,
    },
    {
        "name": "HS Request: Extended Explanation",
        "dataType": "LARGE_TEXT",
        "parentId": HOLD_FOLDER_ID,
    },
    {
        "name": "HS Request: Extended Hold Requested",
        "dataType": "RADIO",
        "options": ["Yes", "No"],
        "parentId": HOLD_FOLDER_ID,
    },
    {
        "name": "HS Request: Signature - Hold Request Confirmation",
        "dataType": "SIGNATURE",
        "parentId": HOLD_FOLDER_ID,
    },
    {
        "name": "HS Request: Intake Status",
        "dataType": "SINGLE_OPTIONS",
        "options": INTAKE_STATUSES,
        "parentId": HOLD_FOLDER_ID,
    },
    {
        "name": "HS: Return Guard Status",
        "dataType": "SINGLE_OPTIONS",
        "options": RETURN_GUARD_STATUSES,
        "parentId": HOLD_FOLDER_ID,
    },
    {
        "name": "HS: Return Guard Result",
        "dataType": "LARGE_TEXT",
        "parentId": HOLD_FOLDER_ID,
    },
    {
        "name": "HS: Return Guard Checked At",
        "dataType": "TEXT",
        "parentId": HOLD_FOLDER_ID,
    },
    {
        "name": "Billing OS: Hold Action Status",
        "dataType": "SINGLE_OPTIONS",
        "options": ACTION_STATUSES,
        "parentId": HOLD_FOLDER_ID,
    },
    {
        "name": "Billing OS: Cancellation Action Status",
        "dataType": "SINGLE_OPTIONS",
        "options": ACTION_STATUSES,
        "parentId": CANCELLATION_FOLDER_ID,
    },
    {
        "name": "Billing OS: Last Error",
        "dataType": "LARGE_TEXT",
        "parentId": CANCELLATION_FOLDER_ID,
    },
    {
        "name": "Billing OS: Last Action At",
        "dataType": "TEXT",
        "parentId": CANCELLATION_FOLDER_ID,
    },
    {
        "name": "Billing OS: Last Result",
        "dataType": "LARGE_TEXT",
        "parentId": CANCELLATION_FOLDER_ID,
    },
]


def get_existing_fields():
    response = requests.get(
        f"{BASE_URL}/locations/{LOCATION_ID}/customFields",
        headers=HEADERS,
        params={"model": "contact"},
        timeout=30,
    )
    response.raise_for_status()
    return {
        field["name"]: field
        for field in response.json().get("customFields", [])
    }


def normalized_options(field):
    return field.get("picklistOptions") or field.get("options") or []


def create_field(definition):
    payload = {**definition, "model": "contact"}
    response = requests.post(
        f"{BASE_URL}/locations/{LOCATION_ID}/customFields",
        headers=HEADERS,
        json=payload,
        timeout=30,
    )
    if not response.ok:
        print(
            f"FAIL  {definition['name']}: "
            f"{response.status_code} {response.text[:400]}"
        )
        return False
    field = response.json().get("customField", response.json())
    print(
        f"OK    {definition['name']} | {field.get('id', '?')} | "
        f"{field.get('fieldKey', '?')}"
    )
    return True


def main():
    existing = get_existing_fields()
    failures = 0
    for definition in FIELDS:
        current = existing.get(definition["name"])
        if current:
            expected_options = definition.get("options", [])
            current_options = normalized_options(current)
            if current.get("dataType") != definition["dataType"]:
                print(
                    f"FAIL  {definition['name']} | existing type "
                    f"{current.get('dataType')} should be {definition['dataType']}"
                )
                failures += 1
                continue
            if expected_options and current_options != expected_options:
                print(
                    f"FAIL  {definition['name']} | existing options "
                    f"{current_options} should be {expected_options}"
                )
                failures += 1
                continue
            print(
                f"SKIP  {definition['name']} | {current.get('id')} | already exists"
            )
            continue
        if not create_field(definition):
            failures += 1
    if failures:
        sys.exit(1)


if __name__ == "__main__":
    main()
