#!/usr/bin/env python3
"""Backfill governed cancellation contact evidence on one GHL contact."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import requests


BASE_URL = "https://services.leadconnectorhq.com"
TAG = "cs: contact made"
SOURCE_FIELD_ID = "wIhH5FlD4tZlw4vrzuck"
AT_FIELD_ID = "dMZBb1wwQW9OqZ42df5d"
VALID_SOURCES = (
    "Member Reply",
    "Qualified Connected Call",
    "Manual Live Contact",
)


def load_env() -> None:
    env_path = Path(__file__).with_name(".env")
    for raw in env_path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("'\""))


def headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {os.environ['GHL_API_KEY']}",
        "Version": "2021-07-28",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


def evidence_fields(contact: dict) -> dict[str, object]:
    return {
        item["id"]: item.get("fieldValue", item.get("value"))
        for item in contact.get("customFields", [])
        if item.get("id") in {SOURCE_FIELD_ID, AT_FIELD_ID}
    }


def read_contact(contact_id: str) -> dict:
    response = requests.get(
        f"{BASE_URL}/contacts/{contact_id}",
        headers=headers(),
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["contact"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contact-id", required=True)
    parser.add_argument("--source", required=True, choices=VALID_SOURCES)
    parser.add_argument(
        "--evidence-at",
        required=True,
        help="ISO-8601 timestamp for the qualifying evidence event",
    )
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    load_env()
    before = read_contact(args.contact_id)
    print(
        {
            "contact_id": args.contact_id,
            "name": " ".join(
                value
                for value in (before.get("firstName"), before.get("lastName"))
                if value
            ),
            "tag_present_before": TAG in set(before.get("tags") or []),
            "evidence_before": evidence_fields(before),
            "mode": "apply" if args.apply else "dry-run",
        }
    )
    if not args.apply:
        return 0

    tag_response = requests.post(
        f"{BASE_URL}/contacts/{args.contact_id}/tags",
        headers=headers(),
        json={"tags": [TAG]},
        timeout=30,
    )
    tag_response.raise_for_status()
    field_response = requests.put(
        f"{BASE_URL}/contacts/{args.contact_id}",
        headers=headers(),
        json={
            "customFields": [
                {"id": SOURCE_FIELD_ID, "fieldValue": args.source},
                {"id": AT_FIELD_ID, "fieldValue": args.evidence_at},
            ]
        },
        timeout=30,
    )
    field_response.raise_for_status()

    after = read_contact(args.contact_id)
    fields = evidence_fields(after)
    result = {
        "contact_id": args.contact_id,
        "tag_present_after": TAG in set(after.get("tags") or []),
        "evidence_after": fields,
    }
    print(result)
    if (
        not result["tag_present_after"]
        or fields.get(SOURCE_FIELD_ID) != args.source
        or fields.get(AT_FIELD_ID) != args.evidence_at
    ):
        raise RuntimeError("GHL read-back did not match the requested backfill")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
