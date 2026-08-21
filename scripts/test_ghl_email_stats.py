#!/usr/bin/env python3
"""
scripts/test_ghl_email_stats.py

Discovery script — tests what GHL API endpoints are available for
workflow email statistics. Run this before building the full reporting script.

Usage:
    cd /Users/peterbrown/evolved-workspace
    source .venv/bin/activate
    python3 scripts/test_ghl_email_stats.py
"""

import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

API_KEY     = os.environ["GHL_API_KEY"]
LOCATION_ID = os.environ["GHL_LOCATION_ID"]

BASE    = "https://services.leadconnectorhq.com"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Version": "2021-07-28",
    "Accept": "application/json",
}

WAITLIST_KEYWORDS = ["waitlist", "nurture", "dnnc", "30 day", "30-day", "teen", "perimenopause", "postmenopause", "post menopause", "post-partum", "postpartum", "20s", "30s"]


def get(path, params=None):
    r = requests.get(f"{BASE}{path}", headers=HEADERS, params=params)
    return r.status_code, r.json() if r.headers.get("content-type", "").startswith("application/json") else r.text


def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)


# ── 1. List workflows, find the 5 waitlist sequences ─────────────
section("1. Workflows — looking for waitlist sequences")

status, data = get("/workflows/", params={"locationId": LOCATION_ID})
print(f"Status: {status}")

if status == 200:
    workflows = data.get("workflows", [])
    print(f"Total workflows found: {len(workflows)}")

    waitlist_workflows = []
    for wf in workflows:
        name = wf.get("name", "").lower()
        if any(kw in name for kw in WAITLIST_KEYWORDS):
            waitlist_workflows.append(wf)
            print(f"  MATCH  id={wf['id']}  name={wf['name']}  status={wf.get('status')}")

    if not waitlist_workflows:
        print("  No waitlist workflows matched — printing all workflow names:")
        for wf in workflows:
            print(f"    id={wf['id']}  name={wf['name']}")
else:
    print(json.dumps(data, indent=2))
    waitlist_workflows = []


# ── 2. Try per-workflow stats endpoint on first match ─────────────
if waitlist_workflows:
    wf = waitlist_workflows[0]
    wf_id = wf["id"]
    section(f"2. Workflow stats — {wf['name']}")

    for path in [
        f"/workflows/{wf_id}/stats",
        f"/workflows/{wf_id}/statistics",
        f"/workflows/{wf_id}/email-stats",
    ]:
        status, data = get(path, params={"locationId": LOCATION_ID})
        print(f"\n  GET {path}  →  {status}")
        if status == 200:
            print(json.dumps(data, indent=2)[:2000])
        else:
            msg = data.get("message", data) if isinstance(data, dict) else data
            print(f"  {msg}")


# ── 3. Try reporting / email stats endpoints ──────────────────────
section("3. Reporting endpoints")

reporting_paths = [
    "/reporting/email-stats",
    "/reporting/email/stats",
    f"/reporting/email-stats?locationId={LOCATION_ID}",
    "/email-statistics",
    f"/email-statistics/?locationId={LOCATION_ID}",
]

for path in reporting_paths:
    status, data = get(path, params={"locationId": LOCATION_ID} if "?" not in path else None)
    print(f"\n  GET {path}  →  {status}")
    if status == 200:
        print(json.dumps(data, indent=2)[:1000])
    else:
        msg = data.get("message", data) if isinstance(data, dict) else str(data)[:200]
        print(f"  {msg}")


# ── 4. Try contacts enrolled in a workflow (fallback approach) ────
if waitlist_workflows:
    wf = waitlist_workflows[0]
    section(f"4. Contacts in workflow — {wf['name']} (fallback approach)")

    status, data = get(
        "/contacts/",
        params={
            "locationId": LOCATION_ID,
            "workflowId": wf["id"],
            "limit": 5,
        }
    )
    print(f"Status: {status}")
    if status == 200:
        contacts = data.get("contacts", [])
        print(f"Contacts returned: {len(contacts)}")
        if contacts:
            print("First contact keys:", list(contacts[0].keys()))
    else:
        msg = data.get("message", data) if isinstance(data, dict) else data
        print(f"  {msg}")


print("\n\nDone. Review output above to determine which approach to use for the full script.")
