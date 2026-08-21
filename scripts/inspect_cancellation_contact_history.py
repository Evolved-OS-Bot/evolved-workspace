#!/usr/bin/env python3
"""Read recent GHL conversation events for cancellation evidence review."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import requests


BASE_URL = "https://services.leadconnectorhq.com"


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
        "Version": "2021-04-15",
        "Accept": "application/json",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contact-id", required=True)
    parser.add_argument("--limit", type=int, default=30)
    args = parser.parse_args()
    load_env()

    location_id = os.environ["GHL_LOCATION_ID"]
    search = requests.get(
        f"{BASE_URL}/conversations/search",
        headers=headers(),
        params={"locationId": location_id, "contactId": args.contact_id},
        timeout=30,
    )
    search.raise_for_status()
    conversations = search.json().get("conversations", [])
    if not conversations:
        print({"contact_id": args.contact_id, "events": []})
        return 0

    conversation_id = conversations[0]["id"]
    messages_response = requests.get(
        f"{BASE_URL}/conversations/{conversation_id}/messages",
        headers=headers(),
        params={"limit": args.limit},
        timeout=30,
    )
    messages_response.raise_for_status()
    payload = messages_response.json()
    messages = payload.get("messages", payload)
    if isinstance(messages, dict):
        messages = messages.get("messages", [])

    events = []
    for message in messages:
        body = (
            message.get("body")
            or message.get("message")
            or message.get("subject")
            or ""
        )
        events.append(
            {
                "id": message.get("id"),
                "date_added": message.get("dateAdded"),
                "direction": message.get("direction"),
                "type": message.get("type"),
                "status": message.get("status"),
                "call_duration": message.get("callDuration"),
                "body_preview": " ".join(str(body).split())[:120],
            }
        )
    print({"contact_id": args.contact_id, "conversation_id": conversation_id})
    for event in events:
        print(event)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
