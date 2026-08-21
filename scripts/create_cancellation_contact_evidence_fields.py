#!/usr/bin/env python3
"""Create governed GHL cancellation contact-evidence fields.

Safe to re-run: fields are matched by exact name and existing definitions are
validated before they are skipped.
"""

from __future__ import annotations

import os
from pathlib import Path

import requests


BASE_URL = "https://services.leadconnectorhq.com"
CANCELLATION_FOLDER_ID = "6K5Faoqa02Be82SKmLv2"
FIELD_SPECS = [
    (
        "CS: Contact Evidence Source",
        "SINGLE_OPTIONS",
        ["Member Reply", "Qualified Connected Call", "Manual Live Contact"],
    ),
    ("CS: Contact Evidence At", "TEXT", []),
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
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Version": "2021-07-28",
    "Content-Type": "application/json",
    "Accept": "application/json",
}


def normalized_options(field: dict) -> list[str]:
    return field.get("picklistOptions") or field.get("options") or []


def main() -> int:
    response = requests.get(
        f"{BASE_URL}/locations/{LOCATION_ID}/customFields",
        headers=HEADERS,
        params={"model": "contact"},
        timeout=30,
    )
    response.raise_for_status()
    existing = {
        field.get("name"): field
        for field in response.json().get("customFields", [])
    }

    failures = 0
    for name, data_type, options in FIELD_SPECS:
        current = existing.get(name)
        if current:
            correct = (
                current.get("dataType") == data_type
                and current.get("parentId") == CANCELLATION_FOLDER_ID
                and (not options or normalized_options(current) == options)
            )
            if not correct:
                print(f"FAIL  {name} has a conflicting live definition")
                failures += 1
            else:
                print(
                    f"SKIP  {name} | {current.get('id')} | "
                    f"{current.get('fieldKey')}"
                )
            continue

        definition = {
            "name": name,
            "dataType": data_type,
            "parentId": CANCELLATION_FOLDER_ID,
            "model": "contact",
        }
        if options:
            definition["options"] = options
        created = requests.post(
            f"{BASE_URL}/locations/{LOCATION_ID}/customFields",
            headers=HEADERS,
            json=definition,
            timeout=30,
        )
        if not created.ok:
            print(f"FAIL  {name}: {created.status_code} {created.text[:300]}")
            failures += 1
            continue
        field = created.json().get("customField", created.json())
        print(
            f"OK    {name} | {field.get('id')} | {field.get('fieldKey')}"
        )

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
