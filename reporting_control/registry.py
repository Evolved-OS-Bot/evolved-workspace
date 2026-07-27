from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REQUIRED_FIELDS = {
    "id",
    "purpose",
    "owner",
    "runtime",
    "schedule",
    "period_rule",
    "sources",
    "dependencies",
    "share_safe_artifact",
    "identified_artifact",
    "destinations",
    "max_age_hours",
    "state",
}


def load_registry(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != 1:
        raise ValueError("Unsupported report registry schema")
    reports = payload.get("reports")
    if not isinstance(reports, list) or not reports:
        raise ValueError("Report registry must contain reports")
    ids = set()
    for report in reports:
        missing = REQUIRED_FIELDS - set(report)
        if missing:
            raise ValueError(
                f"{report.get('id', '<unknown>')} missing: {sorted(missing)}"
            )
        if report["id"] in ids:
            raise ValueError(f"Duplicate report id: {report['id']}")
        ids.add(report["id"])
        if report["max_age_hours"] <= 0:
            raise ValueError(f"{report['id']} has invalid freshness")
    for report in reports:
        unknown = set(report["dependencies"]) - ids
        if unknown:
            raise ValueError(
                f"{report['id']} has unknown dependencies: {sorted(unknown)}"
            )
    return payload
