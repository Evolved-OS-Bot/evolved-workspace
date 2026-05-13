#!/usr/bin/env python3
"""
scripts/audit-ghl-urls.py

Scans GHL workflows, email templates, and SMS templates for hardcoded
theevolvedgym.com.au and blog.theevolvedgym.com.au URLs.

Run before DNS migration to identify every place that needs updating.

Usage:
    cd scripts && python3 audit-ghl-urls.py
    python3 scripts/audit-ghl-urls.py --output outputs/systems/ghl-url-audit.md
"""

import os
import re
import sys
import json
import requests
import argparse
from datetime import datetime
from zoneinfo import ZoneInfo

# Load env
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

GHL_API_KEY     = os.environ["GHL_API_KEY"]
GHL_LOCATION_ID = os.environ["GHL_LOCATION_ID"]
BRISBANE_TZ     = ZoneInfo("Australia/Brisbane")

GHL_BASE    = "https://services.leadconnectorhq.com"
GHL_HEADERS = {
    "Authorization": f"Bearer {GHL_API_KEY}",
    "Version": "2021-07-28",
    "Accept": "application/json",
}

DOMAINS_TO_FIND = [
    "theevolvedgym.com.au",
    "blog.theevolvedgym.com.au",
]

findings = []


def find_urls(text, source_type, source_name, field=""):
    """Search text for target domain references and record findings."""
    if not text or not isinstance(text, str):
        return
    for domain in DOMAINS_TO_FIND:
        # Find all URLs containing the domain
        pattern = rf'https?://[^\s"\'<>]*{re.escape(domain)}[^\s"\'<>]*'
        matches = re.findall(pattern, text)
        for url in set(matches):
            findings.append({
                "source_type": source_type,
                "source_name": source_name,
                "field": field,
                "domain": domain,
                "url": url,
            })


def scan_object(obj, source_type, source_name, path=""):
    """Recursively scan any dict/list/str for URLs."""
    if isinstance(obj, str):
        find_urls(obj, source_type, source_name, field=path)
    elif isinstance(obj, dict):
        for key, val in obj.items():
            scan_object(val, source_type, source_name, path=f"{path}.{key}" if path else key)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            scan_object(item, source_type, source_name, path=f"{path}[{i}]")


def fetch_workflows():
    """Fetch all workflows from GHL."""
    print("Scanning workflows...")
    r = requests.get(
        f"{GHL_BASE}/workflows/",
        headers=GHL_HEADERS,
        params={"locationId": GHL_LOCATION_ID},
    )
    if not r.ok:
        print(f"  Workflows API error {r.status_code}: {r.text[:200]}")
        return
    workflows = r.json().get("workflows", [])
    print(f"  Found {len(workflows)} workflows")
    for wf in workflows:
        name = wf.get("name", "Unknown")
        scan_object(wf, "Workflow", name)


def fetch_email_templates():
    """Fetch all email templates from GHL."""
    print("Scanning email templates...")
    r = requests.get(
        f"{GHL_BASE}/emails/builder",
        headers=GHL_HEADERS,
        params={"locationId": GHL_LOCATION_ID, "limit": 100},
    )
    if not r.ok:
        # Try alternative endpoint
        r = requests.get(
            f"{GHL_BASE}/templates/",
            headers=GHL_HEADERS,
            params={"locationId": GHL_LOCATION_ID, "limit": 100, "type": "email"},
        )
        if not r.ok:
            print(f"  Email templates API error {r.status_code}: {r.text[:200]}")
            return
    data = r.json()
    templates = data.get("templates", data.get("data", []))
    print(f"  Found {len(templates)} email templates")
    for tmpl in templates:
        name = tmpl.get("name", "Unknown")
        scan_object(tmpl, "Email Template", name)


def fetch_sms_templates():
    """Fetch SMS templates from GHL."""
    print("Scanning SMS templates...")
    r = requests.get(
        f"{GHL_BASE}/templates/",
        headers=GHL_HEADERS,
        params={"locationId": GHL_LOCATION_ID, "limit": 100, "type": "sms"},
    )
    if not r.ok:
        print(f"  SMS templates API error {r.status_code}: {r.text[:200]}")
        return
    templates = r.json().get("templates", [])
    print(f"  Found {len(templates)} SMS templates")
    for tmpl in templates:
        name = tmpl.get("name", "Unknown")
        scan_object(tmpl, "SMS Template", name)


def fetch_custom_values():
    """Fetch custom values from GHL — check for hardcoded URLs."""
    print("Scanning custom values...")
    r = requests.get(
        f"{GHL_BASE}/locations/{GHL_LOCATION_ID}/customValues",
        headers=GHL_HEADERS,
    )
    if not r.ok:
        print(f"  Custom values API error {r.status_code}: {r.text[:200]}")
        return
    values = r.json().get("customValues", [])
    print(f"  Found {len(values)} custom values")
    for val in values:
        name = val.get("name", "Unknown")
        value = val.get("value", "")
        find_urls(value, "Custom Value", name, field="value")


def format_report():
    """Format findings as a Markdown report."""
    now = datetime.now(BRISBANE_TZ).strftime("%Y-%m-%d %H:%M AEST")

    if not findings:
        return f"""# GHL URL Audit — The Evolved
**Run:** {now}

## Result

No hardcoded `theevolvedgym.com.au` or `blog.theevolvedgym.com.au` URLs found in GHL workflows, templates, or custom values.

All clear for DNS migration.
"""

    # Group by source type
    by_type = {}
    for f in findings:
        key = f["source_type"]
        by_type.setdefault(key, []).append(f)

    lines = [
        f"# GHL URL Audit — The Evolved",
        f"**Run:** {now}",
        f"**Total findings:** {len(findings)}",
        "",
        "---",
        "",
        "## Summary",
        "",
    ]

    for source_type, items in sorted(by_type.items()):
        lines.append(f"- **{source_type}:** {len(items)} URL(s) found")

    lines += ["", "---", ""]

    for source_type, items in sorted(by_type.items()):
        lines.append(f"## {source_type}")
        lines.append("")
        lines.append("| Source Name | Field | URL Found |")
        lines.append("|---|---|---|")
        for item in items:
            lines.append(f"| {item['source_name']} | `{item['field']}` | `{item['url']}` |")
        lines.append("")

    lines += [
        "---",
        "",
        "## Required Updates",
        "",
        "For each URL above:",
        "",
        "1. **`theevolvedgym.com.au/strength-assessment`** → `go.theevolvedgym.com.au/strength-assessment`",
        "2. **`blog.theevolvedgym.com.au/[slug]`** → `theevolvedgym.com.au/blog/[slug]` (or leave — 301 redirect handles it)",
        "3. **`theevolvedgym.com.au` (root, no path)** → `go.theevolvedgym.com.au` (if GHL page) or `theevolvedgym.com.au` (if WordPress page — no change needed)",
        "",
    ]

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Audit GHL for hardcoded domain URLs")
    parser.add_argument("--output", help="Write report to this file path", default=None)
    args = parser.parse_args()

    print(f"\nGHL URL Audit — {datetime.now(BRISBANE_TZ).strftime('%Y-%m-%d %H:%M AEST')}")
    print("=" * 60)

    fetch_workflows()
    fetch_email_templates()
    fetch_sms_templates()
    fetch_custom_values()

    print(f"\nAudit complete. {len(findings)} URLs found.")

    report = format_report()

    if args.output:
        os.makedirs(os.path.dirname(args.output), exist_ok=True)
        with open(args.output, "w") as f:
            f.write(report)
        print(f"Report written to: {args.output}")
    else:
        print("\n" + report)


if __name__ == "__main__":
    main()
