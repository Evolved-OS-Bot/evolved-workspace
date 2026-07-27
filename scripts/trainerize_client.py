"""Small, reusable client for The Evolved's ABC Trainerize API access."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import requests


SCRIPT_DIR = Path(__file__).resolve().parent


def _load_workspace_env(path: Path) -> None:
    """Load simple KEY=VALUE entries without overriding the process environment."""
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_workspace_env(SCRIPT_DIR / ".env")


class TrainerizeAPIError(RuntimeError):
    """Raised when Trainerize rejects a request or returns invalid data."""

    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class TrainerizeClient:
    """Authenticated client for the ABC Trainerize v03 JSON API."""

    def __init__(
        self,
        group_id: str | None = None,
        api_token: str | None = None,
        base_url: str | None = None,
        location_id: int | None = None,
        timeout: int = 30,
    ) -> None:
        self.group_id = group_id or os.environ.get("TRAINERIZE_GROUP_ID", "")
        self.api_token = api_token or os.environ.get("TRAINERIZE_API_TOKEN", "")
        self.base_url = (
            base_url
            or os.environ.get("TRAINERIZE_API_BASE_URL")
            or "https://api.trainerize.com/v03"
        ).rstrip("/")
        configured_location = os.environ.get("TRAINERIZE_LOCATION_ID", "")
        self.location_id = location_id or (
            int(configured_location) if configured_location.isdigit() else None
        )
        self.timeout = timeout

        if not self.group_id or not self.api_token:
            raise TrainerizeAPIError(
                "TRAINERIZE_GROUP_ID and TRAINERIZE_API_TOKEN must be set in scripts/.env"
            )

        self.session = requests.Session()
        self.session.auth = (self.group_id, self.api_token)
        self.session.headers.update(
            {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "The-Evolved-Workspace/1.0",
            }
        )

    def post(self, endpoint: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        """POST JSON to a Trainerize endpoint and return the decoded response."""
        path = endpoint if endpoint.startswith("/") else f"/{endpoint}"

        try:
            response = self.session.post(
                f"{self.base_url}{path}",
                json=payload or {},
                timeout=self.timeout,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            status = getattr(exc.response, "status_code", None)
            suffix = f" (HTTP {status})" if status else ""
            raise TrainerizeAPIError(
                f"Trainerize request failed{suffix}", status_code=status
            ) from exc

        try:
            data = response.json()
        except ValueError as exc:
            raise TrainerizeAPIError("Trainerize returned a non-JSON response") from exc

        if not isinstance(data, dict):
            raise TrainerizeAPIError("Trainerize returned an unexpected response shape")
        return data

    def get_client_list(
        self,
        *,
        view: str = "allActive",
        start: int = 0,
        count: int = 10,
        verbose: bool = False,
        user_id: int | None = None,
        location_id: int | None = None,
    ) -> dict[str, Any]:
        """Return a page of clients without exposing credentials."""
        payload: dict[str, Any] = {
            "view": view,
            "sort": "name",
            "start": start,
            "count": count,
            "verbose": verbose,
        }
        if user_id is not None:
            payload["userID"] = user_id
        if location_id is not None:
            payload["locationID"] = location_id

        return self.post(
            "/user/getClientList",
            payload,
        )

    def get_active_clients(
        self,
        *,
        start: int = 0,
        count: int = 100,
        location_id: int | None = None,
    ) -> dict[str, Any]:
        """Return active clients for the configured business location."""
        resolved_location = location_id or self.location_id
        if resolved_location is None:
            raise TrainerizeAPIError(
                "TRAINERIZE_LOCATION_ID must be set for location-level client access"
            )
        return self.get_client_list(
            view="activeClient",
            start=start,
            count=count,
            location_id=resolved_location,
        )

    def check_connection(self) -> int:
        """Verify authentication and return the active-client total."""
        result = self.get_active_clients(count=1)
        total = result.get("total")
        if not isinstance(total, int):
            raise TrainerizeAPIError("Authentication succeeded but no client total was returned")
        return total
