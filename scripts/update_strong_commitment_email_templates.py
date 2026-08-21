#!/usr/bin/env python3
"""Govern the two GHL onboarding templates that mention the COMMIT offer."""

from __future__ import annotations

import argparse
import copy
import os
from pathlib import Path
from typing import Any

import requests


BASE_URL = "https://services.leadconnectorhq.com"
TEMPLATE_IDS = {
    "66e8c462e086d061d587b062": "Email #3 - The Week That Sets Up Your Next 12 Weeks",
    "66e8e226e99a016eb88dabda": "Email #7 - Milestone T-Shirts",
}
REPLACEMENTS = {
    (
        "If you’re ready to commit to 12 months of training, we reward that "
        "decision by reducing your Small Group Personal Training rate by $10 "
        "per week."
    ): (
        "If you’re currently on our Strong, Fit & Flexible membership and "
        "you’re ready to commit to 12 months of consistent training, you can "
        "apply for our Strong commitment price: $10 per week off your regular "
        "$99 weekly rate."
    ),
    (
        "Simply reply to this email with the word COMMIT, and our team will "
        "take care of the rest."
    ): (
        "Reply to this email with the single word COMMIT. We’ll confirm your "
        "eligibility and send the written variation for you to review and "
        "sign. Your price does not change from the reply alone."
    ),
    (
        "*This option is available on full memberships only and reflects a "
        "commitment to yourself, not just a cheaper rate."
    ): (
        "*Available only to eligible Strong, Fit & Flexible members. It is not "
        "available on Fit & Flexible or Fast Track. The four-week upfront "
        "payment is unchanged. Full terms, cooling-off rights and any early "
        "exit discount recovery are provided before signing."
    ),
    (
        "Members who commit long term receive $10 per week off Small Group "
        "Personal Training as a recognition of consistency and trust in the "
        "process."
    ): (
        "Eligible Strong, Fit & Flexible members who sign a 12-month "
        "commitment variation receive $10 per week off their regular $99 "
        "weekly rate."
    ),
    (
        "If that feels right for you, reply to this email with the word COMMIT "
        "and our team will walk you through the options."
    ): (
        "If that feels right for you, reply with the single word COMMIT. "
        "We’ll confirm eligibility and send the written variation. Your reply "
        "records interest only and does not change your price."
    ),
}


def load_env() -> None:
    path = Path(__file__).parent / ".env"
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


def replace_strings(value: Any, counts: dict[str, int]) -> Any:
    if isinstance(value, str):
        result = value
        for old, new in REPLACEMENTS.items():
            occurrences = result.count(old)
            if occurrences:
                result = result.replace(old, new)
                counts[old] = counts.get(old, 0) + occurrences
        return result
    if isinstance(value, list):
        return [replace_strings(item, counts) for item in value]
    if isinstance(value, dict):
        return {
            key: replace_strings(item, counts)
            for key, item in value.items()
        }
    return value


def count_governed_strings(value: Any) -> int:
    """Count already-governed replacement strings in nested editor content."""
    if isinstance(value, str):
        return sum(value.count(text) for text in REPLACEMENTS.values())
    if isinstance(value, list):
        return sum(count_governed_strings(item) for item in value)
    if isinstance(value, dict):
        return sum(count_governed_strings(item) for item in value.values())
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    load_env()
    location_id = os.environ["GHL_LOCATION_ID"]
    headers = {
        "Authorization": f"Bearer {os.environ['GHL_API_KEY']}",
        "Version": "2023-02-21",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    failures = 0
    for template_id, expected_name in TEMPLATE_IDS.items():
        url = (
            f"{BASE_URL}/emails/public/v2/locations/{location_id}/templates/"
            f"{template_id}"
        )
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        template = response.json()
        if str(template.get("name") or "").strip() != expected_name:
            raise RuntimeError(
                f"{template_id} is {template.get('name')!r}, expected "
                f"{expected_name!r}"
            )
        editor_content = copy.deepcopy(template.get("editorContent"))
        if editor_content is None and template.get("editorContentUrl"):
            content_response = requests.get(
                template["editorContentUrl"],
                timeout=30,
            )
            content_response.raise_for_status()
            if "json" in content_response.headers.get("Content-Type", ""):
                editor_content = content_response.json()
            else:
                editor_content = content_response.text
        if editor_content is None:
            raise RuntimeError(
                f"{expected_name} has no editable content; response fields: "
                + ", ".join(sorted(template))
            )
        counts: dict[str, int] = {}
        updated_content = replace_strings(editor_content, counts)
        matched = sum(counts.values())
        governed = count_governed_strings(editor_content)
        print(
            f"{'APPLY' if args.apply else 'CHECK'}  {expected_name}: "
            f"{matched} legacy match(es), {governed} current match(es)"
        )
        if matched == 0:
            if governed >= 1:
                print(f"CURRENT {expected_name}: no update required")
                continue
            failures += 1
            continue
        if not args.apply:
            continue
        payload = {
            "name": template["name"],
            "editorContent": updated_content,
            "editorType": template["editorType"],
            "previewText": template.get("previewText") or "",
            "subjectLine": (
                template.get("subjectLine") or template.get("subject") or ""
            ),
            "fromName": template.get("fromName") or "",
            "fromEmail": template.get("fromEmail") or "",
            "archived": bool(template.get("archived", False)),
            "parentFolderId": template.get("parentFolderId"),
        }
        write = requests.patch(
            url,
            headers=headers,
            json=payload,
            timeout=30,
        )
        if not write.ok:
            raise RuntimeError(
                f"GHL rejected {expected_name}: {write.status_code} "
                f"{write.text[:500]}"
            )
        print(f"OK     {expected_name}: updated")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
