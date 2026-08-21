#!/usr/bin/env python3
"""
document_ghl.py
Pulls key GHL account data and writes a structured markdown doc to outputs/.
Covers: pipelines, custom fields, forms, surveys, workflows, tags, calendars.
"""

import os
import sys
import json
import requests
from pathlib import Path
from datetime import datetime


def load_local_env(path):
    """Load simple KEY=VALUE entries without requiring python-dotenv."""
    if not path.exists():
        return
    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_local_env(Path(__file__).parent / ".env")

API_KEY     = os.environ["GHL_API_KEY"]
LOCATION_ID = os.environ["GHL_LOCATION_ID"]

BASE_URL = "https://services.leadconnectorhq.com"
HEADERS  = {
    "Authorization": f"Bearer {API_KEY}",
    "Version":       "2021-07-28",
    "Accept":        "application/json",
}


def get(path, params=None):
    url = f"{BASE_URL}{path}"
    r = requests.get(url, headers=HEADERS, params=params)
    if not r.ok:
        print(f"  WARN {r.status_code} {path}: {r.text[:200]}")
        return None
    return r.json()


# ── Fetchers ──────────────────────────────────────────────────────────────────

def fetch_pipelines():
    data = get(f"/opportunities/search", params={"location_id": LOCATION_ID, "limit": 1})
    # Use dedicated pipelines endpoint
    data = get(f"/opportunities/pipelines", params={"locationId": LOCATION_ID})
    if not data:
        return []
    return data.get("pipelines", [])


def fetch_custom_fields():
    data = get(f"/locations/{LOCATION_ID}/customFields")
    if not data:
        return []
    return data.get("customFields", [])


def fetch_custom_field_folders():
    data = get(f"/locations/{LOCATION_ID}/customFields/folders")
    if not data:
        return []
    return data.get("folders", [])


def fetch_forms():
    data = get(f"/forms/", params={"locationId": LOCATION_ID, "limit": 100})
    if not data:
        return []
    return data.get("forms", [])


def fetch_surveys():
    data = get(f"/surveys/", params={"locationId": LOCATION_ID, "limit": 50})
    if not data:
        return []
    return data.get("surveys", [])


def fetch_workflows():
    data = get(f"/workflows/", params={"locationId": LOCATION_ID})
    if not data:
        return []
    return data.get("workflows", [])


def fetch_calendars():
    data = get(f"/calendars/", params={"locationId": LOCATION_ID})
    if not data:
        return []
    return data.get("calendars", [])


def fetch_tags():
    data = get(f"/locations/{LOCATION_ID}/tags")
    if not data:
        return []
    return data.get("tags", [])


def fetch_custom_values():
    data = get(f"/locations/{LOCATION_ID}/customValues")
    if not data:
        return []
    return data.get("customValues", [])


def fetch_location_info():
    data = get(f"/locations/{LOCATION_ID}")
    if not data:
        return {}
    return data.get("location", data)


# ── Renderers ─────────────────────────────────────────────────────────────────

def render_pipelines(pipelines):
    lines = ["## Pipelines\n"]
    if not pipelines:
        lines.append("_None found._\n")
        return "\n".join(lines)
    for p in pipelines:
        lines.append(f"### {p.get('name', 'Unnamed')} `{p.get('id', '')}`")
        stages = p.get("stages", [])
        if stages:
            lines.append(f"{'Position':<6} {'Stage Name':<40} ID")
            lines.append(f"{'-'*6} {'-'*40} {'-'*36}")
            for s in sorted(stages, key=lambda x: x.get("position", 0)):
                lines.append(f"{s.get('position',''):<6} {s.get('name',''):<40} {s.get('id','')}")
        lines.append("")
    return "\n".join(lines)


def render_custom_fields(fields, folders):
    lines = ["## Custom Fields\n"]
    folder_map = {f["id"]: f["name"] for f in folders}

    # Group by folder
    grouped = {}
    for field in fields:
        folder_id = field.get("parentId") or field.get("folderId") or "_root"
        folder_name = folder_map.get(folder_id, "No Folder" if folder_id == "_root" else folder_id)
        grouped.setdefault(folder_name, []).append(field)

    for folder_name in sorted(grouped.keys()):
        lines.append(f"### {folder_name}")
        lines.append(f"{'Field Name':<40} {'Type':<20} {'Key':<50} ID")
        lines.append(f"{'-'*40} {'-'*20} {'-'*50} {'-'*36}")
        for f in sorted(grouped[folder_name], key=lambda x: x.get("name", "")):
            name     = f.get("name", "")[:39]
            dtype    = f.get("dataType", f.get("fieldType", ""))[:19]
            key      = f.get("fieldKey", "")[:49]
            fid      = f.get("id", "")
            lines.append(f"{name:<40} {dtype:<20} {key:<50} {fid}")

            # Show dropdown options if present
            options = f.get("options") or f.get("picklistOptions") or []
            if options:
                opt_names = [o if isinstance(o, str) else o.get("label", o.get("value", str(o))) for o in options]
                lines.append(f"  Options: {', '.join(opt_names)}")
        lines.append("")
    return "\n".join(lines)


def render_forms(forms):
    lines = ["## Forms\n"]
    if not forms:
        lines.append("_None found._\n")
        return "\n".join(lines)
    lines.append(f"{'Form Name':<50} {'Type':<15} ID")
    lines.append(f"{'-'*50} {'-'*15} {'-'*36}")
    for f in sorted(forms, key=lambda x: x.get("name", "")):
        name = f.get("name", "")[:49]
        ftype = f.get("formType", f.get("type", ""))[:14]
        fid   = f.get("id", "")
        lines.append(f"{name:<50} {ftype:<15} {fid}")
    lines.append("")
    return "\n".join(lines)


def render_surveys(surveys):
    lines = ["## Surveys\n"]
    if not surveys:
        lines.append("_None found._\n")
        return "\n".join(lines)
    lines.append(f"{'Survey Name':<50} ID")
    lines.append(f"{'-'*50} {'-'*36}")
    for s in sorted(surveys, key=lambda x: x.get("name", "")):
        lines.append(f"{s.get('name','')[:49]:<50} {s.get('id','')}")
    lines.append("")
    return "\n".join(lines)


def render_workflows(workflows):
    lines = ["## Workflows\n"]
    if not workflows:
        lines.append("_None found._\n")
        return "\n".join(lines)
    lines.append(f"{'Workflow Name':<50} {'Status':<12} ID")
    lines.append(f"{'-'*50} {'-'*12} {'-'*36}")
    for w in sorted(workflows, key=lambda x: x.get("name", "")):
        name   = w.get("name", "")[:49]
        status = w.get("status", "")[:11]
        wid    = w.get("id", "")
        lines.append(f"{name:<50} {status:<12} {wid}")
    lines.append("")
    return "\n".join(lines)


def render_calendars(calendars):
    lines = ["## Calendars\n"]
    if not calendars:
        lines.append("_None found._\n")
        return "\n".join(lines)
    lines.append(f"{'Calendar Name':<50} {'Type':<20} ID")
    lines.append(f"{'-'*50} {'-'*20} {'-'*36}")
    for c in sorted(calendars, key=lambda x: x.get("name", "")):
        name  = c.get("name", "")[:49]
        ctype = c.get("calendarType", c.get("type", ""))[:19]
        cid   = c.get("id", "")
        lines.append(f"{name:<50} {ctype:<20} {cid}")
    lines.append("")
    return "\n".join(lines)


def render_tags(tags):
    lines = ["## Tags\n"]
    if not tags:
        lines.append("_None found._\n")
        return "\n".join(lines)
    for t in sorted(tags, key=lambda x: x.get("name", "") if isinstance(x, dict) else x):
        name = t.get("name", t) if isinstance(t, dict) else t
        lines.append(f"- {name}")
    lines.append("")
    return "\n".join(lines)


def render_custom_values(values):
    lines = ["## Custom Values\n"]
    if not values:
        lines.append("_None found._\n")
        return "\n".join(lines)
    lines.append(f"{'Name':<40} {'Key':<50} Value")
    lines.append(f"{'-'*40} {'-'*50} {'-'*30}")
    for v in sorted(values, key=lambda x: x.get("name", "")):
        name  = v.get("name", "")[:39]
        key   = v.get("fieldKey", v.get("key", ""))[:49]
        value = str(v.get("value", ""))[:60]
        lines.append(f"{name:<40} {key:<50} {value}")
    lines.append("")
    return "\n".join(lines)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("Fetching GHL account data...")

    print("  → Location info")
    location = fetch_location_info()

    print("  → Pipelines")
    pipelines = fetch_pipelines()

    print("  → Custom field folders")
    folders = fetch_custom_field_folders()

    print("  → Custom fields")
    fields = fetch_custom_fields()

    print("  → Forms")
    forms = fetch_forms()

    print("  → Surveys")
    surveys = fetch_surveys()

    print("  → Workflows")
    workflows = fetch_workflows()

    print("  → Calendars")
    calendars = fetch_calendars()

    print("  → Tags")
    tags = fetch_tags()

    print("  → Custom values")
    custom_values = fetch_custom_values()

    # Summary counts
    print(f"\nResults:")
    print(f"  Pipelines:     {len(pipelines)}")
    print(f"  Custom fields: {len(fields)} across {len(folders)} folders")
    print(f"  Forms:         {len(forms)}")
    print(f"  Surveys:       {len(surveys)}")
    print(f"  Workflows:     {len(workflows)}")
    print(f"  Calendars:     {len(calendars)}")
    print(f"  Tags:          {len(tags)}")
    print(f"  Custom values: {len(custom_values)}")

    # Build markdown
    biz_name = location.get("name", "GHL Account")
    date_str  = datetime.now().strftime("%Y-%m-%d")

    doc = f"""# GHL Account Documentation
**Account:** {biz_name}
**Location ID:** {LOCATION_ID}
**Generated:** {date_str}

---

{render_pipelines(pipelines)}
---

{render_custom_fields(fields, folders)}
---

{render_forms(forms)}
---

{render_surveys(surveys)}
---

{render_workflows(workflows)}
---

{render_calendars(calendars)}
---

{render_tags(tags)}
---

{render_custom_values(custom_values)}
"""

    out_dir = Path(__file__).parent.parent / "outputs"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / f"ghl-account-documentation-{date_str}.md"
    out_path.write_text(doc)
    print(f"\nWritten to: {out_path}")


if __name__ == "__main__":
    main()
