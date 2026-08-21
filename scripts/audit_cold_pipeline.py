#!/usr/bin/env python3
"""Read-only classification snapshot for the GHL [COLD] Marketing Pipeline."""

from __future__ import annotations

import collections
import datetime as dt
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import document_ghl as ghl
from membership_reconciliation import GHLReader


PIPELINE_ID = "57MQJY8hc7VoOrNkNhZw"
SNAPSHOT_DATE = dt.date(2026, 8, 4)
OUTPUT = ROOT / "data/private/integration-reporting/cold-pipeline-audit-20260804.json"


def norm_tags(contact: dict) -> set[str]:
    return {str(tag).strip().lower() for tag in contact.get("tags") or []}


def iso_date(raw: object) -> dt.date | None:
    if not raw:
        return None
    try:
        return dt.date.fromisoformat(str(raw)[:10])
    except ValueError:
        return None


def name(contact: dict) -> str:
    return (
        contact.get("name")
        or " ".join(
            part
            for part in (contact.get("firstName"), contact.get("lastName"))
            if part
        )
        or "(unnamed)"
    )


reader = GHLReader(ghl.API_KEY, ghl.LOCATION_ID)
pipelines = ghl.fetch_pipelines()
pipeline = next(item for item in pipelines if item.get("id") == PIPELINE_ID)
stage_names = {
    stage["id"]: stage["name"] for stage in pipeline.get("stages") or []
}

print("Loading complete GHL contact snapshot...", flush=True)
contacts = reader.contacts()
contact_by_id = {contact["id"]: contact for contact in contacts}
print(f"Loaded {len(contacts)} contacts.", flush=True)

print("Loading complete COLD opportunity snapshot...", flush=True)
opportunities = reader._paginate(
    "/opportunities/search",
    {
        "location_id": reader.location_id,
        "pipeline_id": PIPELINE_ID,
        "limit": 100,
    },
    "opportunities",
)
print(f"Loaded {len(opportunities)} COLD opportunities.", flush=True)

print("Loading complete cross-pipeline opportunity snapshot...", flush=True)
all_opportunities = reader.opportunities()
by_contact = collections.defaultdict(list)
for opportunity in all_opportunities:
    by_contact[opportunity.get("contactId")].append(opportunity)
print(f"Loaded {len(all_opportunities)} opportunities across all pipelines.", flush=True)

active_cohort_path = (
    ROOT
    / "data/private/reporting-control-plane/active-client-cohort-20260727/"
    "cohort-decision-snapshot.json"
)
active_emails: set[str] = set()
if active_cohort_path.exists():
    with active_cohort_path.open() as handle:
        cohort = json.load(handle)
    active_emails = {
        str(row.get("canonical_key") or "").strip().lower()
        for row in cohort.get("rows") or []
        if row.get("confirmed_active")
    }

terminal_tags = {
    "old member",
    "old pt client",
    "terminated",
    "lost",
    "not interested",
}
conversion_tags = {
    "member",
    "personal training",
    "strength assessment booked",
    "strength assessment showed",
    "strength assessment cancelled",
    "strength assessment no show",
}
course_tags = {
    "30dnnc complete",
    "30dnnc 25%",
    "30dnnc 50%",
    "30dnnc 75%",
    "30dnnc 100%",
}

rows = []
for opportunity in opportunities:
    contact = contact_by_id.get(opportunity.get("contactId"), {})
    tags = norm_tags(contact)
    email = str(contact.get("email") or "").strip().lower()
    related = by_contact.get(opportunity.get("contactId"), [])
    other_pipeline = [
        item
        for item in related
        if item.get("pipelineId") != PIPELINE_ID
    ]
    created = iso_date(opportunity.get("createdAt"))
    updated = iso_date(opportunity.get("updatedAt"))
    booked_assessment = "strength assessment booked" in tags
    active_client = email in active_emails
    updated_age_days = (SNAPSHOT_DATE - updated).days if updated else None
    stage_name = stage_names.get(opportunity.get("pipelineStageId"), "UNKNOWN")
    if booked_assessment or active_client:
        proposed_state = "won_cold_to_warm_or_client"
    elif stage_name == "Course Complete | 30DNNC":
        proposed_state = "abandoned_course_complete_without_assessment"
    elif updated_age_days is not None and updated_age_days > 45:
        proposed_state = "abandoned_stale_incomplete"
    else:
        proposed_state = "retain_current_course_progress"
    rows.append(
        {
            "opportunity_id": opportunity.get("id"),
            "contact_id": opportunity.get("contactId"),
            "name": name(contact),
            "email": email,
            "status": opportunity.get("status"),
            "stage": stage_name,
            "created_at": opportunity.get("createdAt"),
            "updated_at": opportunity.get("updatedAt"),
            "created_age_days": (SNAPSHOT_DATE - created).days if created else None,
            "updated_age_days": updated_age_days,
            "active_client_cohort": active_client,
            "proposed_state": proposed_state,
            "dnd": bool(contact.get("dnd")),
            "date_added": contact.get("dateAdded"),
            "source": contact.get("source"),
            "contact_type": contact.get("type"),
            "assigned_to": contact.get("assignedTo"),
            "terminal_tags": sorted(tags.intersection(terminal_tags)),
            "conversion_tags": sorted(tags.intersection(conversion_tags)),
            "course_tags": sorted(tags.intersection(course_tags)),
            "all_tags": sorted(tags),
            "other_pipeline_records": [
                {
                    "id": item.get("id"),
                    "pipeline_id": item.get("pipelineId"),
                    "stage_id": item.get("pipelineStageId"),
                    "status": item.get("status"),
                    "created_at": item.get("createdAt"),
                    "updated_at": item.get("updatedAt"),
                }
                for item in other_pipeline
            ],
        }
    )

summary = {
    "snapshot_date": SNAPSHOT_DATE.isoformat(),
    "pipeline_id": PIPELINE_ID,
    "pipeline_name": pipeline.get("name"),
    "total": len(rows),
    "by_status": dict(collections.Counter(row["status"] for row in rows)),
    "by_stage": dict(collections.Counter(row["stage"] for row in rows)),
    "by_stage_status": {
        f"{stage} | {status}": count
        for (stage, status), count in collections.Counter(
            (row["stage"], row["status"]) for row in rows
        ).items()
    },
    "open_total": sum(row["status"] == "open" for row in rows),
    "open_active_clients": sum(
        row["status"] == "open" and row["active_client_cohort"] for row in rows
    ),
    "open_with_other_pipeline": sum(
        row["status"] == "open" and bool(row["other_pipeline_records"])
        for row in rows
    ),
    "open_with_conversion_tags": sum(
        row["status"] == "open" and bool(row["conversion_tags"]) for row in rows
    ),
    "open_with_terminal_tags": sum(
        row["status"] == "open" and bool(row["terminal_tags"]) for row in rows
    ),
    "open_dnd": sum(row["status"] == "open" and row["dnd"] for row in rows),
    "proposed_state_counts": dict(
        collections.Counter(row["proposed_state"] for row in rows)
    ),
}

payload = {"summary": summary, "rows": rows}
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
with OUTPUT.open("w") as handle:
    json.dump(payload, handle, indent=2)

print(json.dumps(summary, indent=2))
print(f"Wrote {OUTPUT}")
