#!/usr/bin/env python3
"""
create_hold_date_fields.py
Creates HS: Pre-Hold-Start Date and HS: Pre-Return Date custom fields
in the 4. Hold System folder in GHL.
"""

import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

API_KEY     = os.environ["GHL_API_KEY"]
LOCATION_ID = os.environ["GHL_LOCATION_ID"]

BASE_URL = "https://services.leadconnectorhq.com"
HEADERS  = {
    "Authorization": f"Bearer {API_KEY}",
    "Version":       "2021-07-28",
    "Accept":        "application/json",
    "Content-Type":  "application/json",
}


def get_hold_system_folder_id():
    # Get folder ID by looking at an existing Hold System field (HS: Hold Start Date id: k40qV4w0HKj5KFbMnmq8)
    r = requests.get(
        f"{BASE_URL}/locations/{LOCATION_ID}/customFields/k40qV4w0HKj5KFbMnmq8",
        headers=HEADERS,
    )
    r.raise_for_status()
    field = r.json().get("customField", r.json())
    folder_id = field.get("parentId") or field.get("folderId")
    if not folder_id:
        print(f"  Field data: {field}")
        print("  ERROR: Could not determine folder ID from existing field")
        sys.exit(1)
    print(f"  Hold System folder ID: {folder_id}")
    return folder_id


def create_custom_field(name, folder_id):
    payload = {
        "name":       name,
        "dataType":   "DATE",
        "parentId":   folder_id,
        "placeholder": "",
    }
    r = requests.post(
        f"{BASE_URL}/locations/{LOCATION_ID}/customFields",
        headers=HEADERS,
        json=payload,
    )
    if not r.ok:
        print(f"  ERROR {r.status_code}: {r.text}")
        return None
    field = r.json().get("customField", r.json())
    print(f"  Created: {field.get('name')} → key: {field.get('fieldKey')} → id: {field.get('id')}")
    return field


def main():
    print("Finding Hold System folder...")
    folder_id = get_hold_system_folder_id()

    print("\nCreating custom fields...")
    f1 = create_custom_field("HS: Pre-Hold-Start Date", folder_id)
    f2 = create_custom_field("HS: Pre-Return Date", folder_id)

    if f1 and f2:
        print("\nDone. Add these to the plan reference table:")
        print(f"  HS: Pre-Hold-Start Date → {{{{contact.{f1.get('fieldKey', '').split('.')[-1]}}}}}")
        print(f"  HS: Pre-Return Date     → {{{{contact.{f2.get('fieldKey', '').split('.')[-1]}}}}}")


if __name__ == "__main__":
    main()
