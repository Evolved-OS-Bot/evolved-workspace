from reporting_control.hub_client import publish_summary


def test_hub_client_is_noop_when_not_configured(monkeypatch):
    monkeypatch.delenv("HUB_INGEST_BASE_URL", raising=False)
    monkeypatch.delenv("HUB_WEBHOOK_SECRET", raising=False)
    assert publish_summary("retention_intelligence", {}) == {
        "status": "not_configured"
    }
