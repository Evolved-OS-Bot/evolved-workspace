from datetime import UTC, datetime

import pytest

from reporting_control.hub_source_client import (
    HubSourceError,
    fetch_latest_source,
)


class Response:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


def test_fetch_latest_source_validates_auth_and_freshness(monkeypatch):
    monkeypatch.setenv("HUB_SOURCE_BASE_URL", "https://hub/api/v1/sources")
    monkeypatch.setenv("HUB_WEBHOOK_SECRET", "secret")
    captured = {}

    def get(url, headers, timeout):
        captured.update(url=url, headers=headers, timeout=timeout)
        return Response(
            {
                "source": "pt_minder",
                "complete": True,
                "observed_at": datetime.now(UTC).isoformat(),
                "payload": {"rows": [{"email": "member@example.com"}]},
            }
        )

    monkeypatch.setattr(
        "reporting_control.hub_source_client.requests.get",
        get,
    )
    result = fetch_latest_source("pt_minder", max_age_hours=192)
    assert result["payload"]["rows"][0]["email"] == "member@example.com"
    assert captured["headers"] == {"X-Hub-Secret": "secret"}


def test_fetch_latest_source_rejects_missing_configuration(monkeypatch):
    monkeypatch.delenv("HUB_SOURCE_BASE_URL", raising=False)
    monkeypatch.delenv("HUB_WEBHOOK_SECRET", raising=False)
    with pytest.raises(HubSourceError, match="not configured"):
        fetch_latest_source("pt_minder", max_age_hours=192)
