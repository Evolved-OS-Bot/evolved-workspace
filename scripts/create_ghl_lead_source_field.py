#!/usr/bin/env python3
"""
create_ghl_lead_source_field.py
Deletes existing 'Lead Source' text field and recreates it as a dropdown
in the 'Marketing OS' folder.
One-time run.
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
    "Content-Type":  "application/json",
}

FIELD_ID = None  # already deleted

DROPDOWN_OPTIONS = [
    "Paid Social - Facebook",
    "Paid Social - Instagram",
    "Paid Search - Google",
    "Organic",
]


MARKETING_OS_FOLDER_ID = "yCGIA0tMjIzAVjRjSQXq"


def delete_field(field_id):
    url = f"{BASE_URL}/locations/{LOCATION_ID}/customFields/{field_id}"
    r = requests.delete(url, headers=HEADERS)
    r.raise_for_status()
    print(f"Deleted field {field_id}")


def create_dropdown_field(folder_id):
    url = f"{BASE_URL}/locations/{LOCATION_ID}/customFields"
    payload = {
        "name":     "Lead Source",
        "dataType": "SINGLE_OPTIONS",
        "model":    "contact",
        "options":  DROPDOWN_OPTIONS,
        "parentId": folder_id,
    }
    r = requests.post(url, headers=HEADERS, json=payload)
    if not r.ok:
        print(f"Error {r.status_code}: {r.text}")
        r.raise_for_status()
    return r.json()


def main():
    # Recreate as dropdown in Marketing OS folder
    print("Creating dropdown field in Marketing OS folder...")
    result = create_dropdown_field(MARKETING_OS_FOLDER_ID)
    field  = result.get("customField", result)
    print(f"Created successfully:")
    print(f"  Name:    {field['name']}")
    print(f"  ID:      {field['id']}")
    print(f"  Key:     {field.get('fieldKey', 'n/a')}")
    print(f"  Folder:  Marketing OS")
    print(f"  Options: {', '.join(DROPDOWN_OPTIONS)}")


if __name__ == "__main__":
    main()
