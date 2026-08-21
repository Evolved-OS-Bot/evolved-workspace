#!/usr/bin/env python3
"""Read-only search across rendered GHL email builder templates."""

from __future__ import annotations

import argparse
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests


BASE_URL = "https://services.leadconnectorhq.com"


def load_env() -> None:
    path = Path(__file__).parent / ".env"
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("text")
    args = parser.parse_args()
    load_env()
    location_id = os.environ["GHL_LOCATION_ID"]
    headers = {
        "Authorization": f"Bearer {os.environ['GHL_API_KEY']}",
        "Version": "2021-07-28",
        "Accept": "application/json",
    }
    templates: list[dict] = []
    seen: set[str] = set()

    def walk(parent_id: str | None = None) -> None:
        params = {"locationId": location_id, "limit": 100}
        if parent_id:
            params["parentId"] = parent_id
        response = requests.get(
            f"{BASE_URL}/emails/builder",
            headers=headers,
            params=params,
            timeout=30,
        )
        response.raise_for_status()
        payload = response.json()
        items = payload.get(
            "builders", payload.get("templates", payload.get("data", []))
        )
        for item in items:
            item_id = str(item.get("id") or "")
            if not item_id or item_id in seen:
                continue
            seen.add(item_id)
            if item.get("previewUrl"):
                templates.append(item)
            else:
                walk(item_id)

    walk()
    needle = args.text.casefold()
    def search(template: dict) -> dict | None:
        try:
            preview = requests.get(template["previewUrl"], timeout=15)
            preview.raise_for_status()
        except requests.RequestException:
            return None
        if needle not in preview.text.casefold():
            return None
        return {
            "id": template.get("id"),
            "name": template.get("name"),
            "previewUrl": template.get("previewUrl"),
        }

    with ThreadPoolExecutor(max_workers=16) as pool:
        matches = [
            match for match in pool.map(search, templates) if match is not None
        ]
    for match in matches:
        print(
            f"{match['id']}\t{match['name']}\t{match['previewUrl']}"
        )
    return 0 if matches else 1


if __name__ == "__main__":
    raise SystemExit(main())
