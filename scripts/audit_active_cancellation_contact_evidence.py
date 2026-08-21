#!/usr/bin/env python3
"""Audit active cancellation notices for missing member-reply evidence."""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

import requests


BASE_URL = "https://services.leadconnectorhq.com"
PIPELINE_ID = "Tl3wKQfNYnAlcgWpORMD"
NOTICE_STAGE_ID = "4f133549-260c-4bb4-bbb6-3b913b185e1b"
TAG = "cs: contact made"
SOURCE_FIELD_ID = "wIhH5FlD4tZlw4vrzuck"


def load_env() -> None:
    env_path = Path(__file__).with_name(".env")
    for raw in env_path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("'\""))


def headers(version: str = "2021-07-28") -> dict[str, str]:
    return {
        "Authorization": f"Bearer {os.environ['GHL_API_KEY']}",
        "Version": version,
        "Accept": "application/json",
    }


def iso(raw: str | None) -> datetime | None:
    if not raw:
        return None
    return datetime.fromisoformat(raw.replace("Z", "+00:00"))


def contact_field(contact: dict, field_id: str) -> object:
    for item in contact.get("customFields", []):
        if item.get("id") == field_id:
            return item.get("fieldValue", item.get("value"))
    return None


def member_replies(contact_id: str, since: datetime | None) -> list[dict]:
    location_id = os.environ["GHL_LOCATION_ID"]
    search = requests.get(
        f"{BASE_URL}/conversations/search",
        headers=headers("2021-04-15"),
        params={"locationId": location_id, "contactId": contact_id},
        timeout=30,
    )
    search.raise_for_status()
    conversations = search.json().get("conversations", [])
    if not conversations:
        return []
    response = requests.get(
        f"{BASE_URL}/conversations/{conversations[0]['id']}/messages",
        headers=headers("2021-04-15"),
        params={"limit": 100},
        timeout=30,
    )
    response.raise_for_status()
    messages = response.json().get("messages", [])
    if isinstance(messages, dict):
        messages = messages.get("messages", [])
    replies = []
    for message in messages:
        added = iso(message.get("dateAdded"))
        if (
            message.get("direction") == "inbound"
            and message.get("type") == 2
            and added
            and (since is None or added >= since)
        ):
            replies.append(
                {
                    "id": message.get("id"),
                    "date_added": message.get("dateAdded"),
                    "preview": " ".join(
                        str(message.get("body") or message.get("message") or "").split()
                    )[:100],
                }
            )
    return sorted(replies, key=lambda item: item["date_added"])


def main() -> int:
    load_env()
    location_id = os.environ["GHL_LOCATION_ID"]
    response = requests.get(
        f"{BASE_URL}/opportunities/search",
        headers=headers(),
        params={
            "location_id": location_id,
            "pipeline_id": PIPELINE_ID,
            "limit": 100,
        },
        timeout=30,
    )
    response.raise_for_status()
    opportunities = [
        item
        for item in response.json().get("opportunities", [])
        if item.get("pipelineStageId") == NOTICE_STAGE_ID
        and item.get("status") == "open"
    ]
    print({"active_notice_count": len(opportunities)})
    for opportunity in opportunities:
        contact_id = opportunity["contactId"]
        contact_response = requests.get(
            f"{BASE_URL}/contacts/{contact_id}",
            headers=headers(),
            timeout=30,
        )
        contact_response.raise_for_status()
        contact = contact_response.json()["contact"]
        replies = member_replies(contact_id, iso(opportunity.get("createdAt")))
        print(
            {
                "opportunity_id": opportunity.get("id"),
                "contact_id": contact_id,
                "name": " ".join(
                    value
                    for value in (
                        contact.get("firstName"),
                        contact.get("lastName"),
                    )
                    if value
                ),
                "notice_created_at": opportunity.get("createdAt"),
                "tag_present": TAG in set(contact.get("tags") or []),
                "evidence_source": contact_field(contact, SOURCE_FIELD_ID),
                "member_reply_count": len(replies),
                "first_member_reply": replies[0] if replies else None,
            }
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
