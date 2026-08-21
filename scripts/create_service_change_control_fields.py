#!/usr/bin/env python3
"""Create the governed GHL Membership Service Change control fields.

Safe to re-run: the dedicated folder is resolved by exact name, fields are
matched by exact name, and existing definitions are validated before skip.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import requests


BASE_URL = "https://services.leadconnectorhq.com"
FOLDER_NAME = "6. Membership Service Change"
CHANGE_STATUSES = [
    "Not Started",
    "Requested",
    "Pending Effective Date",
    "Processing",
    "Accepted",
    "Completed",
    "Exception",
    "Cancelled",
]
ACTION_STATUSES = [
    "Not Started",
    "Scheduled",
    "Processing",
    "Succeeded",
    "Not Applicable",
    "Exception",
]
CLAWBACK_STATUSES = [
    "Not Applicable",
    "Accruing",
    "Quote Required",
    "Quoted",
    "Waived",
    "Collected",
    "Exception",
]
REMINDER_STATUSES = [
    "Not Scheduled",
    "Scheduled",
    "Sent",
    "Exception",
]
LIFECYCLE_STATUSES = [
    "Active",
    "Pending Service Change",
    "On Hold",
    "Cancellation Notice",
    "Cancelled",
    "Exception",
]


def load_env() -> dict[str, str]:
    values = dict(os.environ)
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        for raw in env_path.read_text().splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            values.setdefault(key.strip(), value.strip().strip('"').strip("'"))
    return values


ENV = load_env()
API_KEY = ENV["GHL_API_KEY"]
LOCATION_ID = ENV["GHL_LOCATION_ID"]
FOLDER_ID = ENV.get(
    "GHL_SERVICE_CHANGE_FOLDER_ID",
    "6gmIZo2Eg2BQmf8f1xDH",
)
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Version": "2021-07-28",
    "Content-Type": "application/json",
    "Accept": "application/json",
}


FIELD_SPECS = [
    ("SC: Request ID", "TEXT"),
    ("SC: Prior Service Components", "LARGE_TEXT"),
    ("SC: Selected Service Components", "LARGE_TEXT"),
    ("SC: Request Date", "DATE"),
    ("SC: Effective Date", "DATE"),
    ("SC: Change Status", "SINGLE_OPTIONS", CHANGE_STATUSES),
    ("SC: Offer Version", "TEXT"),
    ("SC: Agreement Version", "TEXT"),
    ("SC: Signed Timestamp", "TEXT"),
    ("SC: Signature Document", "TEXT"),
    ("SC: Billing Action Status", "SINGLE_OPTIONS", ACTION_STATUSES),
    ("SC: GHL Lifecycle Status", "SINGLE_OPTIONS", ACTION_STATUSES),
    ("SC: Trainerize Provisioning Status", "SINGLE_OPTIONS", ACTION_STATUSES),
    ("SC: Appointment Provisioning Status", "SINGLE_OPTIONS", ACTION_STATUSES),
    ("SC: Workbook Reconciliation Status", "SINGLE_OPTIONS", ACTION_STATUSES),
    ("SC: Reporting Acceptance Status", "SINGLE_OPTIONS", ACTION_STATUSES),
    ("SC: Last Error", "LARGE_TEXT"),
    ("SC: Completed Timestamp", "TEXT"),
    ("SC: Change Type", "TEXT"),
    ("SC: Commitment Start Date", "DATE"),
    ("SC: Commitment End Date", "DATE"),
    ("SC: Original Weekly Price Cents", "NUMERICAL"),
    ("SC: Discounted Weekly Price Cents", "NUMERICAL"),
    ("SC: Weekly Discount Cents", "NUMERICAL"),
    ("SC: Maximum Clawback Cents", "NUMERICAL"),
    ("SC: Clawback Quote Cents", "NUMERICAL"),
    ("SC: Clawback Status", "SINGLE_OPTIONS", CLAWBACK_STATUSES),
    ("SC: Continuation Reminder Date", "DATE"),
    ("SC: Continuation Reminder Status", "SINGLE_OPTIONS", REMINDER_STATUSES),
    ("Member: Current Service Components", "LARGE_TEXT"),
    ("Member: Lifecycle Status", "SINGLE_OPTIONS", LIFECYCLE_STATUSES),
    ("Member: Current Service Version", "TEXT"),
    ("Member: Service State Updated At", "TEXT"),
]


def get_existing_fields() -> list[dict]:
    response = requests.get(
        f"{BASE_URL}/locations/{LOCATION_ID}/customFields",
        headers=HEADERS,
        params={"model": "contact"},
        timeout=30,
    )
    response.raise_for_status()
    return response.json().get("customFields", [])


def normalized_options(field: dict) -> list[str]:
    return field.get("picklistOptions") or field.get("options") or []


def main() -> int:
    fields = get_existing_fields()
    folder_id = FOLDER_ID
    if not folder_id:
        print(
            "FAIL  set GHL_SERVICE_CHANGE_FOLDER_ID to the ID shown in the "
            f"GHL URL after opening the Contact folder named {FOLDER_NAME}"
        )
        return 1
    existing = {field.get("name"): field for field in fields}
    failures = 0
    for spec in FIELD_SPECS:
        name, data_type, *option_groups = spec
        options = option_groups[0] if option_groups else []
        current = existing.get(name)
        if current:
            if current.get("dataType") != data_type:
                print(
                    f"FAIL  {name} | existing type "
                    f"{current.get('dataType')} should be {data_type}"
                )
                failures += 1
                continue
            if options and normalized_options(current) != options:
                print(
                    f"FAIL  {name} | existing options "
                    f"{normalized_options(current)} should be {options}"
                )
                failures += 1
                continue
            if current.get("parentId") != folder_id:
                print(
                    f"FAIL  {name} | existing folder "
                    f"{current.get('parentId')} should be {folder_id}"
                )
                failures += 1
                continue
            print(f"SKIP  {name} | {current.get('id')} | already exists")
            continue
        definition = {
            "name": name,
            "dataType": data_type,
            "parentId": folder_id,
            "model": "contact",
        }
        if options:
            definition["options"] = options
        response = requests.post(
            f"{BASE_URL}/locations/{LOCATION_ID}/customFields",
            headers=HEADERS,
            json=definition,
            timeout=30,
        )
        if not response.ok:
            print(
                f"FAIL  {name}: {response.status_code} "
                f"{response.text[:400]}"
            )
            failures += 1
            continue
        field = response.json().get("customField", response.json())
        print(
            f"OK    {name} | {field.get('id', '?')} | "
            f"{field.get('fieldKey', '?')}"
        )
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
