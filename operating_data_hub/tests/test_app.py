import importlib


def make_app(monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'app.db'}")
    monkeypatch.setenv("HUB_WEBHOOK_SECRET", "test-secret")
    monkeypatch.setenv("HUB_DASHBOARD_PASSWORD", "dashboard-secret")
    monkeypatch.setenv("HUB_FLASK_SECRET", "flask-secret")
    monkeypatch.setenv("HUB_SCHEDULER_ENABLED", "false")
    module = importlib.import_module("operating_data_hub.app")
    module = importlib.reload(module)
    return module.app


def test_health_and_authenticated_pt_minder_ingestion(monkeypatch, tmp_path):
    app = make_app(monkeypatch, tmp_path)
    client = app.test_client()
    assert client.get("/health").status_code == 200
    unauthorised = client.post("/api/v1/ingest/pt-minder", json={})
    assert unauthorised.status_code == 401
    accepted = client.post(
        "/api/v1/ingest/pt-minder",
        headers={"X-Hub-Secret": "test-secret"},
        json={
            "observed_at": "2026-07-27T10:00:00+10:00",
            "rows": [
                {
                    "source_account_id": "ptm-1",
                    "email": "member@example.com",
                    "state": "active",
                    "amount": "99",
                }
            ],
        },
    )
    assert accepted.status_code == 200
    assert accepted.get_json()["status"] == "accepted"
    latest = client.get(
        "/api/v1/sources/pt_minder/latest",
        headers={"X-Hub-Secret": "test-secret"},
    )
    assert latest.status_code == 200
    assert latest.get_json()["record_count"] == 1
    assert latest.get_json()["payload"]["rows"][0]["email"] == (
        "member@example.com"
    )


def test_latest_source_requires_auth_and_known_source(monkeypatch, tmp_path):
    app = make_app(monkeypatch, tmp_path)
    client = app.test_client()
    assert client.get("/api/v1/sources/pt_minder/latest").status_code == 401
    assert (
        client.get(
            "/api/v1/sources/not-real/latest",
            headers={"X-Hub-Secret": "test-secret"},
        ).status_code
        == 404
    )


def test_dashboard_requires_login(monkeypatch, tmp_path):
    app = make_app(monkeypatch, tmp_path)
    client = app.test_client()
    assert client.get("/dashboard").status_code == 302
    assert (
        client.post(
            "/login",
            data={"password": "dashboard-secret"},
        ).status_code
        == 302
    )
    assert client.get("/dashboard").status_code == 200


def test_ceo_report_is_authenticated_and_aggregate(monkeypatch, tmp_path):
    app = make_app(monkeypatch, tmp_path)
    client = app.test_client()
    assert client.get("/api/v1/ceo-report").status_code == 401
    response = client.get(
        "/api/v1/ceo-report",
        headers={"X-Hub-Secret": "test-secret"},
    )
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["report_id"] == "ceo-report"
    assert "email" not in str(payload).lower()
