from __future__ import annotations

import os
from datetime import UTC, datetime
from typing import Any

import requests


class HubSourceError(RuntimeError):
    pass


def fetch_latest_source(
    source: str,
    *,
    max_age_hours: int,
    timeout: int = 20,
) -> dict[str, Any]:
    base_url = os.getenv("HUB_SOURCE_BASE_URL", "").rstrip("/")
    secret = os.getenv("HUB_WEBHOOK_SECRET", "")
    if not base_url or not secret:
        raise HubSourceError("hub source reader is not configured")
    response = requests.get(
        f"{base_url}/{source}/latest",
        headers={"X-Hub-Secret": secret},
        timeout=timeout,
    )
    response.raise_for_status()
    snapshot = response.json()
    if snapshot.get("source") != source or not snapshot.get("complete"):
        raise HubSourceError(f"hub returned an incomplete {source} snapshot")
    try:
        observed = datetime.fromisoformat(
            str(snapshot["observed_at"]).replace("Z", "+00:00")
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise HubSourceError("hub snapshot has an invalid observation time") from exc
    if observed.tzinfo is None:
        observed = observed.replace(tzinfo=UTC)
    age_hours = (datetime.now(UTC) - observed).total_seconds() / 3600
    if age_hours < -1 or age_hours > max_age_hours:
        raise HubSourceError(
            f"{source} snapshot is outside the {max_age_hours}-hour freshness window"
        )
    payload = snapshot.get("payload")
    if not isinstance(payload, dict):
        raise HubSourceError("hub snapshot payload is missing")
    return snapshot
