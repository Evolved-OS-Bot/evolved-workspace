#!/usr/bin/env python3
"""
create_milestone_fields.py
Creates the 8 custom contact fields required for the Milestone T-Shirt Order Form.
Safe to re-run — checks for existing fields and skips duplicates.
"""

import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

API_KEY     = os.environ["GHL_API_KEY"]
LOCATION_ID = os.environ["GHL_LOCATION_ID"]
BASE_URL    = "https://services.leadconnectorhq.com"
HEADERS     = {
    "Authorization": f"Bearer {API_KEY}",
    "Version":       "2021-07-28",
    "Content-Type":  "application/json",
    "Accept":        "application/json",
}

# Fields to create
# dataType values: TEXT, LARGE_TEXT, NUMERICAL, DATE, CHECKBOX, SINGLE_OPTIONS, MULTIPLE_OPTIONS
FIELDS = [
    {
        "name":     "Milestone T-Shirt Earned",
        "dataType": "MULTIPLE_OPTIONS",
        "options":  ["100", "200", "500", "750", "1000"],
    },
    {
        "name":     "Milestone T-Shirt Last Ordered",
        "dataType": "DATE",
    },
    {
        "name":     "Milestone T-Shirt Size",
        "dataType": "SINGLE_OPTIONS",
        "options":  ["XS", "S", "M", "L", "XL", "XXL"],
    },
    {
        "name":     "Milestone T-Shirt Style",
        "dataType": "SINGLE_OPTIONS",
        "options":  ["Shirt", "Singlet"],
    },
    {
        "name":     "Member Satisfaction Rating",
        "dataType": "NUMERICAL",
    },
    {
        "name":     "Member Google Review Left",
        "dataType": "CHECKBOX",
    },
    {
        "name":     "Milestone Feedback Notes",
        "dataType": "LARGE_TEXT",
    },
    {
        "name":     "Member Referral Count",
        "dataType": "NUMERICAL",
    },
]


def get_existing_fields():
    """Fetch all existing custom contact fields for this location."""
    r = requests.get(
        f"{BASE_URL}/locations/{LOCATION_ID}/customFields",
        headers=HEADERS,
    )
    if not r.ok:
        print(f"ERROR fetching existing fields: {r.status_code} — {r.text[:400]}")
        sys.exit(1)
    data = r.json()
    fields = data.get("customFields", data.get("customField", []))
    return {f["name"]: f for f in fields}


def create_field(field_def, existing):
    name = field_def["name"]

    if name in existing:
        print(f"  SKIP  '{name}' — already exists (id: {existing[name].get('id', '?')})")
        return

    payload = {
        "name":     name,
        "dataType": field_def["dataType"],
    }
    if "options" in field_def:
        payload["options"] = field_def["options"]

    r = requests.post(
        f"{BASE_URL}/locations/{LOCATION_ID}/customFields",
        headers=HEADERS,
        json=payload,
    )

    if r.ok:
        created = r.json()
        field_id = (
            created.get("customField", {}).get("id")
            or created.get("id")
            or "?"
        )
        print(f"  OK    '{name}' created (id: {field_id})")
    else:
        print(f"  FAIL  '{name}' — {r.status_code}: {r.text[:400]}")


def main():
    print("\nMilestone T-Shirt — Creating custom contact fields\n")

    existing = get_existing_fields()
    print(f"Found {len(existing)} existing custom fields in this location.\n")

    for field_def in FIELDS:
        create_field(field_def, existing)

    print("\nDone.\n")


if __name__ == "__main__":
    main()
