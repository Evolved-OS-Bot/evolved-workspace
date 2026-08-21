#!/usr/bin/env python3
"""Read-only acceptance replay for the live Strength Assessment rebook guards."""

from __future__ import annotations

import json
import os
import sys
from collections import Counter
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from operating_data_hub.sa_attendance import GHLAttendanceClient
from operating_data_hub.sa_rebook_guard import (
    CANCELLED_WORKFLOW_ID,
    NO_SHOW_WORKFLOW_ID,
    REBOOK_GUARD_VERSION,
    classify_rebook_guard,
)


CALENDAR_ID = "HSVEzfJH4nice96IxHem"
REPLAY_LIMIT = 20


def load_local_env() -> None:
    env_path = Path(__file__).with_name(".env")
    for line in env_path.read_text().splitlines():
        if not line or line.lstrip().startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("'\""))


def contact_evidence(
    client: GHLAttendanceClient,
    contact_id: str,
) -> dict[str, Any]:
    response = client._request("GET", f"/contacts/{contact_id}")
    contact = response.get("contact") or response
    return {
        "contact_id": contact_id,
        "name": str(contact.get("name") or "").strip(),
        "contact_type": str(contact.get("type") or "").strip(),
        "tags": list(contact.get("tags") or []),
    }


def main() -> None:
    load_local_env()
    client = GHLAttendanceClient(
        os.environ["GHL_API_KEY"],
        os.environ["GHL_LOCATION_ID"],
    )
    now = datetime.now(UTC)
    source = client.list_events(
        [CALENDAR_ID],
        now - timedelta(days=180),
        now + timedelta(days=1),
    )
    terminal = sorted(
        (
            row
            for row in source["rows"]
            if row["status"] in {"no_show", "cancelled"}
            and not row.get("deleted")
        ),
        key=lambda row: row["start_at"],
        reverse=True,
    )[:REPLAY_LIMIT]
    if len(terminal) < REPLAY_LIMIT:
        raise RuntimeError(
            f"Expected {REPLAY_LIMIT} terminal cases, found {len(terminal)}"
        )

    evidence_cache: dict[str, dict[str, Any]] = {}
    replay_rows = []
    for event in terminal:
        contact_id = event["contact_id"]
        if contact_id not in evidence_cache:
            evidence_cache[contact_id] = contact_evidence(client, contact_id)
        contact = evidence_cache[contact_id]
        replay_rows.append(
            {
                "appointment_id": event["appointment_id"],
                "contact_id": contact_id,
                "contact_name": contact["name"],
                "contact_type": contact["contact_type"],
                "start_at": event["start_at"],
                "status": event["status"],
                "guard_branch": classify_rebook_guard(
                    contact["tags"],
                    contact_type=contact["contact_type"],
                ),
                "all_tags": sorted(set(contact["tags"])),
                "guard_tags_present": sorted(
                    set(contact["tags"])
                    & {"member", "strength assessment showed"}
                ),
            }
        )

    branches = Counter(row["guard_branch"] for row in replay_rows)
    statuses = Counter(row["status"] for row in replay_rows)
    generated_at = datetime.now(UTC)
    result = {
        "definition_version": REBOOK_GUARD_VERSION,
        "generated_at": generated_at.isoformat(),
        "calendar_id": CALENDAR_ID,
        "workflow_ids": {
            "no_show": NO_SHOW_WORKFLOW_ID,
            "cancelled": CANCELLED_WORKFLOW_ID,
        },
        "replayed_cases": len(replay_rows),
        "status_counts": dict(statuses),
        "branch_counts": dict(branches),
        "all_cases_classified": len(replay_rows) == REPLAY_LIMIT,
        "rows": replay_rows,
    }

    private_dir = ROOT / "data" / "private" / "strength-assessments"
    private_dir.mkdir(parents=True, exist_ok=True)
    output_path = private_dir / (
        "sa-rebook-guard-replay-"
        f"{generated_at.strftime('%Y%m%dT%H%M%SZ')}.json"
    )
    output_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                key: value
                for key, value in result.items()
                if key != "rows"
            },
            indent=2,
            sort_keys=True,
        )
    )
    print(f"Identified replay saved privately: {output_path}")


if __name__ == "__main__":
    main()
