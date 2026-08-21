from __future__ import annotations

import os
from datetime import UTC, datetime
from typing import Any

import requests


def publish_summary(
    source: str,
    summary: dict[str, Any],
    *,
    observed_at: str | None = None,
    status: str = "complete",
) -> dict[str, Any]:
    """Publish an aggregate compatibility snapshot when the hub is configured."""
    base_url = os.getenv("HUB_INGEST_BASE_URL", "").rstrip("/")
    secret = os.getenv("HUB_WEBHOOK_SECRET", "")
    if not base_url or not secret:
        return {"status": "not_configured"}
    response = requests.post(
        f"{base_url}/{source}",
        headers={"X-Hub-Secret": secret},
        json={
            "schema_version": 1,
            "observed_at": observed_at or datetime.now(UTC).isoformat(),
            "status": status,
            "summary": summary,
        },
        timeout=20,
    )
    response.raise_for_status()
    return response.json()

