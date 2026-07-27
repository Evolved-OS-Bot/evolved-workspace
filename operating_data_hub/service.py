from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import requests

from .config import Settings
from .contracts import validate_summary
from .kpi_adapter import collect_kpi_snapshot
from .store import HubStore


SOURCE_MAX_AGE_HOURS = {
    "google_kpi": 26,
    "retention_intelligence": 26,
    "pt_booking_continuity": 192,
    "revenue_control": 96,
    "conversation_triage": 26,
    "strength_assessment_prequalification": 26,
    "trainerize_performance": 192,
    "pt_minder": 192,
}


class HubService:
    def __init__(self, settings: Settings, store: HubStore | None = None):
        self.settings = settings
        self.store = store or HubStore(settings.database_url)

    def run_job(self, job_id: str, function):
        run_id = self.store.start_job(job_id)
        try:
            result = function()
            self.store.finish_job(
                run_id, status="complete", summary=result
            )
            return result
        except Exception as exc:
            self.store.finish_job(
                run_id, status="failed", error=str(exc)
            )
            raise

    def refresh_kpi(self) -> dict[str, Any]:
        payload = collect_kpi_snapshot()
        return self.store.accept_snapshot("google_kpi", payload)

    def poll_compatibility_health(self) -> dict[str, Any]:
        results = {}
        endpoints = {
            "retention_intelligence": self.settings.retention_health_url,
            "pt_booking_continuity": self.settings.pt_health_url,
        }
        for source, url in endpoints.items():
            try:
                response = requests.get(url, timeout=20)
                response.raise_for_status()
                body = response.json()
                observed_at = datetime.now(UTC).isoformat()
                if source == "retention_intelligence":
                    observed_at = (
                        body.get("latestRun", {}).get("completedAt")
                        or observed_at
                    )
                if source == "pt_booking_continuity":
                    observed_at = (
                        body.get("lastSuccessfulRun")
                        or body.get("latestRevenueRun", {}).get("completedAt")
                        or observed_at
                    )
                payload = validate_summary(
                    source,
                    {
                        "observed_at": observed_at,
                        "status": (
                            "healthy"
                            if body.get("status") == "ok"
                            else "failed"
                        ),
                        "summary": body,
                    },
                )
                results[source] = self.store.accept_snapshot(source, payload)
                if source == "pt_booking_continuity":
                    revenue = body.get("latestRevenueRun") or {}
                    if revenue.get("completedAt"):
                        revenue_payload = validate_summary(
                            "revenue_control",
                            {
                                "observed_at": revenue["completedAt"],
                                "status": revenue.get("status", "failed"),
                                "summary": revenue,
                            },
                        )
                        results["revenue_control"] = self.store.accept_snapshot(
                            "revenue_control", revenue_payload
                        )
            except Exception as exc:
                results[source] = {
                    "status": "failed",
                    "error": type(exc).__name__,
                }
        return results

    def dashboard_data(self) -> dict[str, Any]:
        now = datetime.now(UTC)
        sources = []
        for snapshot in self.store.latest_snapshots():
            observed_at = datetime.fromisoformat(
                snapshot["observed_at"].replace("Z", "+00:00")
            )
            if observed_at.tzinfo is None:
                observed_at = observed_at.replace(tzinfo=UTC)
            age = (
                now - observed_at
            ).total_seconds() / 3600
            max_age = SOURCE_MAX_AGE_HOURS.get(snapshot["source"], 26)
            sources.append(
                {
                    **{key: value for key, value in snapshot.items() if key != "payload"},
                    "age_hours": round(max(0, age), 1),
                    "max_age_hours": max_age,
                    "freshness": "fresh" if age <= max_age else "stale",
                }
            )
        kpi = self.store.latest_snapshot("google_kpi") or {}
        metrics = (
            kpi.get("payload", {})
            .get("summary", {})
            .get("metrics", {})
        )
        return {
            "generated_at": now.isoformat(timespec="seconds"),
            "mode": "shadow",
            "sources": sorted(sources, key=lambda row: row["source"]),
            "metrics": metrics,
            "jobs": self.store.recent_jobs(),
            "exceptions": self.store.open_exception_counts(),
        }
