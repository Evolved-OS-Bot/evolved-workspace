from __future__ import annotations

import os
import time
from typing import Any

import requests


def _latest(
    session: requests.Session,
    base_url: str,
    headers: dict[str, str],
) -> dict[str, Any]:
    response = session.get(
        f"{base_url}/refresh/latest",
        headers=headers,
        timeout=30,
    )
    if response.status_code == 404:
        return {}
    response.raise_for_status()
    return response.json()


def run_refresh(
    *,
    base_url: str,
    secret: str,
    timeout_seconds: int = 900,
    poll_seconds: int = 10,
    session: requests.Session | None = None,
) -> dict[str, Any]:
    if not base_url or not secret:
        raise RuntimeError(
            "TRAINERIZE_PERFORMANCE_URL and WEBHOOK_SHARED_SECRET are required"
        )
    session = session or requests.Session()
    base_url = base_url.rstrip("/")
    headers = {"X-Webhook-Secret": secret}
    before = _latest(session, base_url, headers)
    before_completed = before.get("completedAt")

    response = session.post(
        f"{base_url}/refresh",
        headers=headers,
        timeout=30,
    )
    response.raise_for_status()

    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        time.sleep(poll_seconds)
        latest = _latest(session, base_url, headers)
        if latest.get("completedAt") == before_completed:
            continue
        if latest.get("status") != "complete":
            raise RuntimeError(
                f"Trainerize refresh failed: {latest.get('error') or latest}"
            )
        return latest
    raise TimeoutError(
        f"Trainerize refresh did not complete within {timeout_seconds} seconds"
    )


def main() -> int:
    result = run_refresh(
        base_url=os.getenv("TRAINERIZE_PERFORMANCE_URL", ""),
        secret=os.getenv("WEBHOOK_SHARED_SECRET", ""),
        timeout_seconds=int(os.getenv("REFRESH_TIMEOUT_SECONDS", "900")),
        poll_seconds=int(os.getenv("REFRESH_POLL_SECONDS", "10")),
    )
    print(
        "Trainerize refresh complete: "
        f"{result.get('active_roster')} active accounts, "
        f"{result.get('recent_workouts')} recent workouts"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
