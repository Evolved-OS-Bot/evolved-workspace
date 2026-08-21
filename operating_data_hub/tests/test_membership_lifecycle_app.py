from operating_data_hub.tests.test_app import make_app


def test_lifecycle_and_current_people_endpoints_are_protected_and_shadow(
    monkeypatch,
    tmp_path,
):
    app = make_app(monkeypatch, tmp_path)
    client = app.test_client()
    headers = {"X-Hub-Secret": "test-secret"}

    assert (
        client.get("/api/v2/reporting/membership-lifecycle").status_code
        == 401
    )
    accepted = client.post(
        "/api/v1/ingest/membership-reconciliation",
        headers=headers,
        json={
            "observed_at": "2026-08-02T00:00:00+00:00",
            "source_run_id": "membership-live-1",
            "rows": [
                {
                    "canonical_key": "member@example.com",
                    "email": "member@example.com",
                    "first_name": "Sam",
                    "last_name": "Member",
                    "source_ids": {"ghl": ["ghl-1"]},
                    "services": [
                        {
                            "service_type": "sgpt",
                            "service_name": "Strength & Sculpt",
                        }
                    ],
                    "lifecycle_status": "cancelling",
                    "ghl_active": True,
                    "stripe_entitled": True,
                    "trainerize_active": True,
                    "cancellation_status": "Notice Active",
                    "cancellation_type": "Membership",
                    "notice_end_date": "2026-08-15",
                    "final_access_date": "2026-08-15",
                }
            ],
        },
    )
    assert accepted.status_code == 200
    accepted_payload = accepted.get_json()
    assert (
        accepted_payload["membership_lifecycle_shadow"][
            "accepted_event_versions"
        ]
        == 2
    )

    lifecycle = client.get(
        "/api/v2/reporting/membership-lifecycle?period=28d",
        headers=headers,
    )
    assert lifecycle.status_code == 200
    lifecycle_payload = lifecycle.get_json()
    assert lifecycle_payload["mode"] == "shadow"
    assert lifecycle_payload["acceptance"]["cutover_authorised"] is False
    assert lifecycle_payload["attrition_rate"] is None

    cohort = client.post(
        "/api/v2/reporting/membership-lifecycle/backfill",
        headers=headers,
        json={
            "observed_at": "2026-08-02T00:00:00+00:00",
            "source_run_id": "historical-opening-1",
            "records": [],
            "opening_cohorts": [
                {
                    "as_of_date": lifecycle_payload["period"]["start"],
                    "canonical_keys": ["member@example.com"],
                    "coverage_complete": True,
                    "confidence": "high",
                    "source_record_id": "opening-28d-1",
                    "evidence": {"source": "protected accepted comparison"},
                }
            ],
        },
    )
    assert cohort.status_code == 200
    assert cohort.get_json()["accepted_event_versions"] == 1

    assert client.get("/api/v2/reporting/current-people").status_code == 401
    current = client.get(
        "/api/v2/reporting/current-people?period=28d",
        headers=headers,
    )
    assert current.status_code == 200
    current_payload = current.get_json()
    assert current_payload["protected"] is True
    assert current_payload["rows"][0]["person_id"]
    assert current_payload["rows"][0]["display"]["email"] == (
        "member@example.com"
    )
    assert current_payload["rows"][0]["lifecycle"]["status"] == "cancelling"
    assert (
        "active_cancellation_notice"
        in current_payload["rows"][0]["suppression_reasons"]
    )
