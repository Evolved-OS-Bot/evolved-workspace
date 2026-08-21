#!/usr/bin/env python3
"""Apply Peter's approved COLD opportunity status reconciliation safely.

The approved ID set and classification come from the private 4 August audit
snapshot. The script aborts before the first write unless the complete current
pipeline, every approved record and all 56 protected Open records still match
that snapshot. Use --apply for mutation; the default is a read-only preflight.
"""

from __future__ import annotations

import collections
import concurrent.futures
import json
import sys
import threading
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import document_ghl as ghl
from membership_reconciliation import GHLReader


PIPELINE_ID = "57MQJY8hc7VoOrNkNhZw"
SOURCE = (
    ROOT
    / "data/private/integration-reporting/cold-pipeline-audit-20260804.json"
)
RESULT = (
    ROOT
    / "data/private/integration-reporting/"
    "cold-pipeline-reconciliation-result-20260804.json"
)
APPLY = "--apply" in sys.argv
EXPECTED = {
    "won_cold_to_warm_or_client": 354,
    "abandoned_course_complete_without_assessment": 152,
    "abandoned_stale_incomplete": 198,
    "retain_current_course_progress": 56,
}
TARGET_STATUS = {
    "won_cold_to_warm_or_client": "won",
    "abandoned_course_complete_without_assessment": "abandoned",
    "abandoned_stale_incomplete": "abandoned",
}


def request(session: requests.Session, method: str, path: str, **kwargs):
    url = f"{ghl.BASE_URL}{path}"
    for attempt in range(7):
        response = session.request(method, url, timeout=30, **kwargs)
        if response.status_code != 429:
            response.raise_for_status()
            return response
        time.sleep(1.5 * (attempt + 1))
    response.raise_for_status()


approved = json.loads(SOURCE.read_text())
rows = approved["rows"]
approved_counts = collections.Counter(row["proposed_state"] for row in rows)
if dict(approved_counts) != EXPECTED:
    raise RuntimeError(
        f"Approved snapshot counts changed: {dict(approved_counts)} != {EXPECTED}"
    )

reader = GHLReader(ghl.API_KEY, ghl.LOCATION_ID)
current_rows = reader._paginate(
    "/opportunities/search",
    {
        "location_id": reader.location_id,
        "pipeline_id": PIPELINE_ID,
        "limit": 100,
    },
    "opportunities",
)
current_by_id = {row["id"]: row for row in current_rows}
approved_by_id = {row["opportunity_id"]: row for row in rows}
pipeline = next(
    item for item in ghl.fetch_pipelines() if item.get("id") == PIPELINE_ID
)
stage_id_by_name = {
    stage["name"]: stage["id"] for stage in pipeline.get("stages") or []
}

if set(current_by_id) != set(approved_by_id):
    missing = sorted(set(approved_by_id) - set(current_by_id))
    added = sorted(set(current_by_id) - set(approved_by_id))
    raise RuntimeError(
        "Live COLD ID set drifted after approval: "
        f"missing={len(missing)}, added={len(added)}"
    )

precondition_errors = []
for opportunity_id, snapshot in approved_by_id.items():
    current = current_by_id[opportunity_id]
    target_status = TARGET_STATUS.get(snapshot["proposed_state"])
    current_status = str(current.get("status") or "").lower()
    allowed_status = (
        current_status == "open"
        if target_status is None
        else current_status in {"open", target_status}
    )
    checks = {
        "status": allowed_status,
        "pipeline": current.get("pipelineId") == PIPELINE_ID,
        "stage": current.get("pipelineStageId")
        == stage_id_by_name[snapshot["stage"]],
        "updated_at": current_status == target_status
        or current.get("updatedAt") == snapshot.get("updated_at"),
    }
    if not all(checks.values()):
        precondition_errors.append(
            {"opportunity_id": opportunity_id, "checks": checks}
        )

if precondition_errors:
    raise RuntimeError(
        f"{len(precondition_errors)} approved records changed after approval; "
        "aborting before any write"
    )

actions = [
    row for row in rows if row["proposed_state"] in TARGET_STATUS
]
protected = [
    row
    for row in rows
    if row["proposed_state"] == "retain_current_course_progress"
]
if len(actions) != 704 or len(protected) != 56:
    raise RuntimeError(
        f"Unexpected action boundary: actions={len(actions)}, protected={len(protected)}"
    )

thread_state = threading.local()


def worker_session():
    if not hasattr(thread_state, "session"):
        thread_state.session = requests.Session()
        thread_state.session.headers.update(
            {**ghl.HEADERS, "Content-Type": "application/json"}
        )
    return thread_state.session


def apply_one(row):
    opportunity_id = row["opportunity_id"]
    target_status = TARGET_STATUS[row["proposed_state"]]
    current_status = str(
        current_by_id[opportunity_id].get("status") or ""
    ).lower()
    result = {
        "opportunity_id": opportunity_id,
        "contact_id": row["contact_id"],
        "classification": row["proposed_state"],
        "before_status": current_status,
        "target_status": target_status,
        "applied": False,
        "verified": False,
    }
    if current_status == target_status:
        result["verified"] = True
        result["already_correct"] = True
    elif APPLY:
        session = worker_session()
        request(
            session,
            "PUT",
            f"/opportunities/{opportunity_id}",
            json={"status": target_status},
        )
        result["applied"] = True
        payload = request(
            session, "GET", f"/opportunities/{opportunity_id}"
        ).json()
        after = payload.get("opportunity") or payload
        result["after_status"] = str(after.get("status") or "").lower()
        result["verified"] = result["after_status"] == target_status
    return result


results = []
if APPLY:
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(apply_one, row) for row in actions]
        for index, future in enumerate(concurrent.futures.as_completed(futures), 1):
            result = future.result()
            results.append(result)
            if not result["verified"]:
                raise RuntimeError(
                    "Read-back failed for " + result["opportunity_id"]
                )
            if index % 25 == 0 or index == len(actions):
                print(f"processed {index}/{len(actions)}", flush=True)
else:
    results = [apply_one(row) for row in actions]
    for index in range(25, len(actions) + 1, 25):
        print(f"processed {index}/{len(actions)}", flush=True)
    print(f"processed {len(actions)}/{len(actions)}", flush=True)

post_rows = reader._paginate(
    "/opportunities/search",
    {
        "location_id": reader.location_id,
        "pipeline_id": PIPELINE_ID,
        "limit": 100,
    },
    "opportunities",
)
post_by_status = dict(
    collections.Counter(str(row.get("status") or "").lower() for row in post_rows)
)
protected_open = sum(
    str(next(row for row in post_rows if row["id"] == item["opportunity_id"]).get("status") or "").lower()
    == "open"
    for item in protected
)

summary = {
    "apply": APPLY,
    "planned": len(actions),
    "applied": sum(result["applied"] for result in results),
    "verified": sum(result["verified"] for result in results),
    "protected_open": protected_open,
    "post_by_status": post_by_status,
}
RESULT.write_text(json.dumps({"summary": summary, "results": results}, indent=2))
print(json.dumps(summary, indent=2))
