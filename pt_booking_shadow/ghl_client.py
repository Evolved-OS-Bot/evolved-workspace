from __future__ import annotations

import logging
import time
from datetime import datetime
from typing import Any
from urllib.parse import parse_qs, urlparse

import requests

from .models import Appointment


log = logging.getLogger(__name__)


class GHLReadOnlyClient:
    """GHL reader. Intentionally exposes no mutation methods."""

    base_url = "https://services.leadconnectorhq.com"

    def __init__(self, api_key: str, location_id: str, timeout: int = 30):
        self.location_id = location_id
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {api_key}",
                "Version": "2021-07-28",
                "Accept": "application/json",
            }
        )

    def _get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        url = path if path.startswith("http") else f"{self.base_url}{path}"
        last_error: Exception | None = None
        for attempt in range(4):
            try:
                response = self.session.get(url, params=params, timeout=self.timeout)
                if response.status_code == 429 or response.status_code >= 500:
                    delay = min(8, 2**attempt)
                    log.warning("GHL read retry: status=%s delay=%ss", response.status_code, delay)
                    time.sleep(delay)
                    continue
                response.raise_for_status()
                return response.json()
            except (requests.RequestException, ValueError) as exc:
                last_error = exc
                if attempt == 3:
                    break
                time.sleep(min(8, 2**attempt))
        raise RuntimeError(f"GHL read failed for {path}: {last_error}") from last_error

    @staticmethod
    def _next_params(meta: dict[str, Any]) -> dict[str, Any] | None:
        if meta.get("startAfter") is None or not meta.get("startAfterId"):
            return None
        return {
            "startAfter": meta["startAfter"],
            "startAfterId": meta["startAfterId"],
        }

    def list_contacts(self) -> list[dict[str, Any]]:
        contacts: list[dict[str, Any]] = []
        params: dict[str, Any] = {"locationId": self.location_id, "limit": 100}
        while True:
            data = self._get("/contacts/", params)
            contacts.extend(data.get("contacts", []))
            next_bits = self._next_params(data.get("meta", {}))
            if not next_bits:
                break
            params.update(next_bits)
        return contacts

    def get_contact(self, contact_id: str) -> dict[str, Any]:
        return self._get(f"/contacts/{contact_id}").get("contact", {})

    def list_opportunities(self) -> list[dict[str, Any]]:
        opportunities: list[dict[str, Any]] = []
        params: dict[str, Any] = {"location_id": self.location_id, "limit": 100}
        while True:
            data = self._get("/opportunities/search", params)
            opportunities.extend(data.get("opportunities", []))
            next_bits = self._next_params(data.get("meta", {}))
            if not next_bits:
                break
            params.update(next_bits)
        return opportunities

    def list_contact_opportunities(self, contact_id: str) -> list[dict[str, Any]]:
        data = self._get(
            "/opportunities/search",
            {"location_id": self.location_id, "contact_id": contact_id, "limit": 100},
        )
        return data.get("opportunities", [])

    def list_calendars(self) -> list[dict[str, Any]]:
        return self._get("/calendars/", {"locationId": self.location_id}).get("calendars", [])

    def list_users(self) -> list[dict[str, Any]]:
        return self._get("/users/", {"locationId": self.location_id}).get("users", [])

    def list_events(
        self, calendar_id: str, start: datetime, end: datetime
    ) -> list[Appointment]:
        data = self._get(
            "/calendars/events",
            {
                "locationId": self.location_id,
                "calendarId": calendar_id,
                "startTime": int(start.timestamp() * 1000),
                "endTime": int(end.timestamp() * 1000),
            },
        )
        result: list[Appointment] = []
        for raw in data.get("events", []):
            if not raw.get("contactId") or not raw.get("startTime") or not raw.get("endTime"):
                continue
            result.append(
                Appointment(
                    id=str(raw.get("id", "")),
                    contact_id=str(raw["contactId"]),
                    calendar_id=str(raw.get("calendarId") or calendar_id),
                    start=datetime.fromisoformat(raw["startTime"].replace("Z", "+00:00")),
                    end=datetime.fromisoformat(raw["endTime"].replace("Z", "+00:00")),
                    status=str(
                        raw.get("appointmentStatus")
                        or raw.get("appoinmentStatus")
                        or "unknown"
                    ).lower(),
                    assigned_user_id=raw.get("assignedUserId"),
                    deleted=bool(raw.get("deleted", False)),
                )
            )
        return result
