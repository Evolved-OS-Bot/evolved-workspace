#!/usr/bin/env python3
"""Create the missing GHL fields for four scored Strength Assessment results.

Safe to re-run: existing fields are matched by exact name and validated before
being skipped.
"""

import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv


load_dotenv(Path(__file__).parent / ".env")

API_KEY = os.environ["GHL_API_KEY"]
LOCATION_ID = os.environ["GHL_LOCATION_ID"]
BASE_URL = "https://services.leadconnectorhq.com"
STRENGTH_ASSESSMENT_FOLDER_ID = "9My8zVPIm9hqJA0XqRND"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Version": "2021-07-28",
    "Content-Type": "application/json",
    "Accept": "application/json",
}

RESULT_OPTIONS = ["Below Live", "Live", "Long", "Perform"]
ELEVATION_SOURCE_FIELD = "SA: ATG Split Squat Elevation Level"


def get_existing_fields():
    response = requests.get(
        f"{BASE_URL}/locations/{LOCATION_ID}/customFields",
        headers=HEADERS,
        timeout=30,
    )
    if not response.ok:
        print(f"ERROR fetching custom fields: {response.status_code} {response.text[:400]}")
        sys.exit(1)
    fields = response.json().get("customFields", [])
    return {field["name"]: field for field in fields}


def field_definitions(existing):
    source_field = existing.get(ELEVATION_SOURCE_FIELD, {})
    elevation_options = source_field.get("options") or source_field.get("picklistOptions")
    if not elevation_options:
        print(f"ERROR: could not copy options from '{ELEVATION_SOURCE_FIELD}'.")
        print("Matching live fields:")
        for name in sorted(existing):
            if "split squat" in name.lower() or "elevation" in name.lower():
                print(f"  {name}")
        print(f"Source field keys: {sorted(source_field)}")
        sys.exit(1)

    return [
        {"name": "SA: Single-Leg Capacity Right Result", "dataType": "SINGLE_OPTIONS", "options": RESULT_OPTIONS},
        {"name": "SA: Single-Leg Capacity Left Result", "dataType": "SINGLE_OPTIONS", "options": RESULT_OPTIONS},
        {"name": "SA: ATG Split Squat Right Elevation Level", "dataType": "SINGLE_OPTIONS", "options": elevation_options},
        {"name": "SA: ATG Split Squat Left Elevation Level", "dataType": "SINGLE_OPTIONS", "options": elevation_options},
        {"name": "SA: ATG Split Squat Right Reps Performed", "dataType": "NUMERICAL"},
        {"name": "SA: ATG Split Squat Left Reps Performed", "dataType": "NUMERICAL"},
        {"name": "SA: ATG Split Squat Right Weight Used (kg)", "dataType": "NUMERICAL"},
        {"name": "SA: ATG Split Squat Left Weight Used (kg)", "dataType": "NUMERICAL"},
        {"name": "SA: Grip Endurance Result", "dataType": "SINGLE_OPTIONS", "options": RESULT_OPTIONS},
        {"name": "SA: Farmer Walk Seconds Held", "dataType": "NUMERICAL"},
        {"name": "SA: Spinal Control Result", "dataType": "SINGLE_OPTIONS", "options": RESULT_OPTIONS},
        {"name": "SA: Side Plank Right Seconds Held", "dataType": "NUMERICAL"},
        {"name": "SA: Side Plank Left Seconds Held", "dataType": "NUMERICAL"},
        {"name": "SA: Toes to Bar Reps", "dataType": "NUMERICAL"},
    ]


def create_field(field):
    payload = {
        **field,
        "model": "contact",
        "parentId": STRENGTH_ASSESSMENT_FOLDER_ID,
    }
    response = requests.post(
        f"{BASE_URL}/locations/{LOCATION_ID}/customFields",
        headers=HEADERS,
        json=payload,
        timeout=30,
    )
    if not response.ok:
        print(f"FAIL  {field['name']}: {response.status_code} {response.text[:400]}")
        return False
    created = response.json().get("customField", response.json())
    print(f"OK    {field['name']} | {created.get('id', '?')} | {created.get('fieldKey', '?')}")
    return True


def main():
    existing = get_existing_fields()
    failures = 0
    for field in field_definitions(existing):
        if field["name"] in existing:
            current = existing[field["name"]]
            if current.get("dataType") != field["dataType"]:
                print(
                    f"FAIL  {field['name']} | existing type "
                    f"{current.get('dataType', '?')} should be {field['dataType']}"
                )
                failures += 1
                continue
            print(f"SKIP  {field['name']} | {current.get('id', '?')} | already exists")
            continue
        if not create_field(field):
            failures += 1
    if failures:
        sys.exit(1)


if __name__ == "__main__":
    main()
