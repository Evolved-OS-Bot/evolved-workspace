from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .registry import load_registry


def _artifact_status(
    root: Path, report: dict[str, Any], now: datetime
) -> dict[str, Any]:
    artifact = report["share_safe_artifact"]
    status = {
        "report_id": report["id"],
        "configured_state": report["state"],
        "runtime": report["runtime"],
        "schedule": report["schedule"],
        "owner": report["owner"],
        "status": "external-not-synchronised",
        "age_hours": None,
        "artifact": artifact,
    }
    if not artifact:
        if report["state"] == "migration-required":
            status["status"] = "migration-required"
        return status
    path = root / artifact
    if not path.exists():
        status["status"] = "missing"
        return status
    modified = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    age_hours = max(0.0, (now - modified).total_seconds() / 3600)
    status["age_hours"] = round(age_hours, 1)
    status["status"] = (
        "fresh" if age_hours <= report["max_age_hours"] else "stale"
    )
    return status


def _performance_metrics(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    metrics: dict[str, Any] = {}
    mappings = {
        "active_roster": "Current Trainerize active roster",
        "workout_coverage": (
            "Active clients with any recovered detailed workout"
        ),
        "reassessment_due": "Reassessment due or missing",
        "remarkable_candidates": "Remarkable-results candidates",
    }
    for key, label in mappings.items():
        match = re.search(
            rf"^\|\s*{re.escape(label)}\s*\|\s*([\d,]+)\s*\|$",
            text,
            re.MULTILINE,
        )
        if match:
            metrics[key] = int(match.group(1).replace(",", ""))
    source = re.search(
        r"^\*\*Detailed workout source through:\*\*\s*(.+)$",
        text,
        re.MULTILINE,
    )
    if source:
        metrics["detailed_workout_source_through"] = source.group(1).strip()
    return metrics


def build_executive_brief(
    *,
    root: Path,
    registry_path: Path,
    now: datetime | None = None,
) -> dict[str, Any]:
    now = now or datetime.now(timezone.utc)
    registry = load_registry(registry_path)
    kpi_path = root / "context" / "current-data.json"
    kpi = json.loads(kpi_path.read_text()) if kpi_path.exists() else {}
    report_status = [
        _artifact_status(root, report, now)
        for report in registry["reports"]
    ]
    counts: dict[str, int] = {}
    for row in report_status:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    return {
        "schema_version": 1,
        "report_id": "evolved-executive-brief",
        "generated_at": now.isoformat(timespec="seconds"),
        "privacy": "aggregate-share-safe",
        "report_status_counts": counts,
        "reports": report_status,
        "business_metrics": {
            "period": kpi.get("period"),
            "members": kpi.get("members"),
            "revenue": kpi.get("revenue"),
            "acquisition": kpi.get("acquisition"),
            "sales": kpi.get("sales"),
            "retention": kpi.get("retention"),
            "pt_utilisation": kpi.get("pt_utilisation"),
            "limitations": kpi.get("source", {}).get("limitations", []),
        },
        "trainerize_performance": _performance_metrics(
            root
            / "outputs"
            / "trainerize-reporting-reconciliation"
            / "latest-performance-summary.md"
        ),
        "architecture_alerts": [
            {
                "severity": "high",
                "report_id": "railway-only-scheduling",
                "message": (
                    "KPI refresh and Discord delivery still run as local "
                    "compatibility processes. Railway replacements have not "
                    "yet passed parity, so the Railway-only target is not complete."
                ),
            },
            {
                "severity": "medium",
                "report_id": "trainerize-performance",
                "message": (
                    "Performance reporting is restored as a snapshot-only "
                    "consumer; automated transfer of the latest aggregate "
                    "Railway reconciliation state is still pending."
                ),
            },
            {
                "severity": "medium",
                "report_id": "railway-control-plane",
                "message": (
                    "External Railway run state is not yet synchronised into "
                    "this local share-safe brief."
                ),
            },
            {
                "severity": "medium",
                "report_id": "shared-identity-controls",
                "message": (
                    "Revenue and PT share protected identity evidence, but "
                    "Retention Intelligence has not yet migrated to the same "
                    "PostgreSQL-backed control repository."
                ),
            },
        ],
    }


def render_markdown(brief: dict[str, Any]) -> str:
    business = brief["business_metrics"]
    period = (business.get("period") or {}).get("label", "Unavailable")
    members = business.get("members") or {}
    revenue = business.get("revenue") or {}
    performance = brief.get("trainerize_performance") or {}
    rows = [
        "# Evolved Executive Reporting Brief",
        "",
        f"**Generated:** {brief['generated_at']}",
        f"**Completed KPI period:** {period}",
        "",
        "## Decision Metrics",
        "",
        "| Metric | Value |",
        "|---|---:|",
        (
            "| Unique active roster clients | "
            f"{members.get('unique_active_roster_clients', 'Unavailable')} |"
        ),
        (
            "| SGPT service relationships | "
            f"{members.get('active_sgpt_service_relationships', 'Unavailable')} |"
        ),
        (
            "| PT service relationships | "
            f"{members.get('active_pt_service_relationships', 'Unavailable')} |"
        ),
        (
            "| Cross-service overlaps removed | "
            f"{members.get('cross_service_overlaps', 'Unavailable')} |"
        ),
        (
            "| Cash collected | "
            f"${revenue.get('cash_collected', 0):,.2f} |"
            if revenue.get("cash_collected") is not None
            else "| Cash collected | Unavailable |"
        ),
        (
            "| Trainerize reassessments due or missing | "
            f"{performance.get('reassessment_due', 'Unavailable')} |"
        ),
        "",
        "## Report Control",
        "",
        "| Report | Runtime | Status | Age |",
        "|---|---|---|---:|",
    ]
    for report in brief["reports"]:
        age = (
            f"{report['age_hours']:.1f}h"
            if report["age_hours"] is not None
            else "not synchronised"
        )
        rows.append(
            f"| {report['report_id']} | {report['runtime']} | "
            f"{report['status']} | {age} |"
        )
    rows += [
        "",
        "## Architecture Alerts",
        "",
    ]
    rows.extend(
        f"- **{alert['severity'].title()}:** {alert['message']}"
        for alert in brief["architecture_alerts"]
    )
    rows.append("")
    return "\n".join(rows)
