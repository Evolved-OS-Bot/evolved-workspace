import importlib
from datetime import UTC, datetime, timedelta


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


def test_reporting_v2_endpoints_are_shadow_and_inputs_fail_closed(
    monkeypatch,
    tmp_path,
):
    app = make_app(monkeypatch, tmp_path)
    client = app.test_client()
    headers = {"X-Hub-Secret": "test-secret"}

    assert client.get("/api/v2/reporting/status").status_code == 401
    status = client.get(
        "/api/v2/reporting/status",
        headers=headers,
    )
    assert status.status_code == 200
    assert status.get_json()["mode"] == "shadow"
    assert status.get_json()["publication_authority"] == "none"

    assert (
        client.get("/api/v2/reporting/cutover-status").status_code
        == 401
    )
    cutover = client.get(
        "/api/v2/reporting/cutover-status?period=28d",
        headers=headers,
    )
    assert cutover.status_code == 200
    cutover_payload = cutover.get_json()
    assert cutover_payload["mode"] == "metric_by_metric"
    assert cutover_payload["period"]["id"] == "28d"
    assert cutover_payload["kpi_workbook_cutover_authorised"] is False
    assert cutover_payload["accepted_metric_count"] == 0
    assert any(
        row["metric_id"] == "cash_goal_progress"
        for row in cutover_payload["metrics"]
    )
    assert any(
        row["metric_id"]
        == "consumer_retention_intelligence_contract"
        and row["definition_version"] == "retention-hub-read-v1"
        and row["cutover"]["promotion_authorised"] is False
        and row["cutover"]["legacy_fallback_available"] is True
        for row in cutover_payload["metrics"]
    )
    assert any(
        row["metric_id"] == "evolved_standards"
        and row["definition_version"] == "evolved-standards-v1-shadow"
        and row["cutover"]["promotion_authorised"] is False
        for row in cutover_payload["metrics"]
    )

    assert (
        client.post(
            "/api/v2/reporting/publication-decisions",
            json={},
        ).status_code
        == 401
    )
    blocked_publication = client.post(
        "/api/v2/reporting/publication-decisions",
        headers=headers,
        json={
            "metric_id": "leads_created",
            "definition_version": "ghl-leads-v1",
            "action": "approve",
            "decided_by": "Peter Brown",
            "reason": "Test must remain fail closed.",
            "period": "28d",
        },
    )
    assert blocked_publication.status_code == 400
    assert "cannot be promoted" in blocked_publication.get_json()["error"]

    assert client.get("/api/v2/reporting/acquisition-preview").status_code == 401
    acquisition_preview = client.get(
        "/api/v2/reporting/acquisition-preview",
        headers=headers,
    )
    assert acquisition_preview.status_code == 200
    acquisition_payload = acquisition_preview.get_json()
    assert acquisition_payload["mode"] == "shadow"
    assert acquisition_payload["publication_impact"] == "none"

    assert (
        client.get("/api/v2/reporting/ceo-scorecard").status_code
        == 401
    )
    scorecard = client.get(
        "/api/v2/reporting/ceo-scorecard?period=28d",
        headers=headers,
    )
    assert scorecard.status_code == 200
    scorecard_payload = scorecard.get_json()
    assert scorecard_payload["mode"] == "shadow"
    assert scorecard_payload["period"]["id"] == "28d"
    assert scorecard_payload["acceptance"]["cutover_authorised"] is False
    assert client.get("/api/v2/reporting/sgpt-delivery").status_code == 401
    sgpt_delivery = client.get(
        "/api/v2/reporting/sgpt-delivery?period=28d",
        headers=headers,
    )
    assert sgpt_delivery.status_code == 200
    assert sgpt_delivery.get_json()["publication_impact"] == "none"
    invalid_scorecard = client.get(
        "/api/v2/reporting/ceo-scorecard?period=month",
        headers=headers,
    )
    assert invalid_scorecard.status_code == 400

    parallel_payload = {
        "metric_id": "leads_created",
        "definition_version": "ghl-leads-v1",
        "period_start": "2026-07-20",
        "period_end": "2026-07-26",
        "legacy_value": 4,
        "v2_value": 17,
        "variance_classification": "approved_definition_change",
        "unexplained_event_count": 0,
        "unexplained_cents": 0,
        "evidence": {
            "comparison_cycle": "test-cycle",
            "publication_impact": "none",
        },
        "request_cutover_acceptance": True,
    }
    assert client.post(
        "/api/v2/reporting/parallel-results",
        json=parallel_payload,
    ).status_code == 401
    parallel = client.post(
        "/api/v2/reporting/parallel-results",
        headers=headers,
        json=parallel_payload,
    )
    assert parallel.status_code == 200
    assert parallel.get_json()["status"] == "passed"
    status_after_parallel = client.get(
        "/api/v2/reporting/status",
        headers=headers,
    ).get_json()
    comparison = next(
        row
        for row in status_after_parallel["latest_parallel_results"]
        if row["metric_id"] == "leads_created"
    )
    assert comparison["acceptance_state"] == "passed"

    assert (
        client.post("/api/v2/reporting/cash-events", json={}).status_code
        == 401
    )
    cash = client.post(
        "/api/v2/reporting/cash-events",
        headers=headers,
        json={
            "source_system": "stripe",
            "source_run_id": "stripe-cash-1",
            "observed_at": "2026-07-30T12:00:00+00:00",
            "complete": True,
            "events": [
                {
                    "source_event_id": "in_1",
                    "occurred_at": "2026-07-29T01:00:00+00:00",
                    "event_type": "settled_cash",
                    "gross_amount_cents": 11000,
                    "gst_amount_cents": 1000,
                }
            ],
        },
    )
    assert cash.status_code == 200
    assert cash.get_json()["mode"] == "shadow"
    assert cash.get_json()["publication_impact"] == "none"
    assert cash.get_json()["cash_goal"]["available"] is False
    assert (
        client.post(
            "/api/v2/reporting/jobs/cash-refresh"
        ).status_code
        == 401
    )

    assert (
        client.get("/api/v2/reporting/onboarding-followup-preview").status_code
        == 401
    )
    onboarding_preview = client.get(
        "/api/v2/reporting/onboarding-followup-preview",
        headers=headers,
    )
    assert onboarding_preview.status_code == 409

    onboarding_write = client.post(
        "/api/v2/reporting/jobs/onboarding-followups",
        headers=headers,
    )
    assert onboarding_write.status_code == 409

    definitions = client.get(
        "/api/v2/reporting/metric-definitions",
        headers=headers,
    )
    assert definitions.status_code == 200
    assert any(
        row["metric_id"] == "sa_show_rate"
        for row in definitions.get_json()["definitions"]
    )
    assert any(
        row["metric_id"] == "sa_listed_show_rate"
        for row in definitions.get_json()["definitions"]
    )

    board_pack = client.get(
        "/api/v2/reporting/board-pack-contract",
        headers=headers,
    )
    assert board_pack.status_code == 200
    assert board_pack.get_json()["publication_enabled"] is False
    assert board_pack.get_json()["sheet_calculation_allowed"] is False

    manual = client.post(
        "/api/v2/reporting/manual-inputs",
        headers=headers,
        json={},
    )
    assert manual.status_code == 409


def test_governed_payment_service_override_reaches_latest_source_and_ceo(
    monkeypatch,
    tmp_path,
):
    app = make_app(monkeypatch, tmp_path)
    client = app.test_client()
    headers = {"X-Hub-Secret": "test-secret"}
    accepted = client.post(
        "/api/v1/ingest/pt-minder",
        headers=headers,
        json={
            "observed_at": "2026-07-27T10:00:00+10:00",
            "transaction_detail_complete": True,
            "rows": [
                {
                    "source_account_id": "1490780",
                    "agreement_id": "343361",
                    "email": "member@example.com",
                    "product": "1:1 PT Leisa (2 x 30 mins)",
                    "state": "collecting",
                    "amount": "99",
                    "weekly_amount": "99",
                    "transactions": [
                        {
                            "source_transaction_id": "txn-1",
                            "occurred_on": "2026-07-24",
                            "description": (
                                "1:1 PT Leisa (2 x 30 mins) - from "
                                "24/07/2026 to 30/07/2026 "
                                "(recurring payment)"
                            ),
                            "amount": "99",
                            "status": "completed",
                        }
                    ],
                }
            ],
        },
    )
    assert accepted.status_code == 200
    override = client.post(
        "/api/v1/governance/payment-service-overrides",
        headers=headers,
        json={
            "observed_at": "2026-07-29T12:00:00+10:00",
            "rows": [
                {
                    "source": "pt_minder",
                    "agreement_id": "343361",
                    "service_type": "sgpt",
                    "cadence": "recurring",
                    "expected_weekly_amount": "99",
                    "approved_by": "Peter Brown",
                    "reason": (
                        "Owner confirmed the immutable source label "
                        "represents Strength and Sculpt membership."
                    ),
                }
            ],
        },
    )
    assert override.status_code == 200

    latest = client.get(
        "/api/v1/sources/pt_minder/latest",
        headers=headers,
    ).get_json()
    row = latest["payload"]["rows"][0]
    transaction = row["transactions"][0]
    assert row["product"] == "1:1 PT Leisa (2 x 30 mins)"
    assert transaction["raw_service_type"] == "personal_training"
    assert transaction["service_type"] == "sgpt"

    ceo = client.get("/api/v1/ceo-report", headers=headers).get_json()
    assert ceo["payment_service_governance"]["active_overrides"] == 1
    dashboard = client.get(
        "/api/v1/dashboard",
        headers=headers,
    ).get_json()
    override_source = next(
        source
        for source in dashboard["sources"]
        if source["source"] == "payment_service_overrides"
    )
    assert override_source["freshness"] == "fresh"
    assert override_source["max_age_hours"] is None


def test_membership_ingestion_populates_canonical_status(
    monkeypatch, tmp_path
):
    app = make_app(monkeypatch, tmp_path)
    client = app.test_client()
    headers = {"X-Hub-Secret": "test-secret"}
    response = client.post(
        "/api/v1/ingest/membership-reconciliation",
        headers=headers,
        json={
            "observed_at": "2026-07-27T10:00:00+00:00",
            "source_run_id": "membership-run-1",
            "rows": [
                {
                    "canonical_key": "member@example.com",
                    "email": "member@example.com",
                    "source_ids": {
                        "ghl": ["ghl-1"],
                        "stripe": ["cus-1"],
                        "trainerize": ["123"],
                    },
                    "service_type": "sgpt",
                    "service_name": "Strong",
                    "lifecycle_status": "active",
                    "ghl_active": True,
                    "stripe_entitled": True,
                    "trainerize_active": True,
                }
            ],
        },
    )
    assert response.status_code == 200
    status = client.get("/api/v1/canonical/status", headers=headers)
    assert status.status_code == 200
    assert status.get_json()["counts"]["people"] == 1


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
    assert client.get("/dashboard/system-health").status_code == 200


def test_reporting_v2_dashboard_preview_is_login_protected_and_gated(
    monkeypatch,
    tmp_path,
):
    app = make_app(monkeypatch, tmp_path)
    client = app.test_client()

    assert client.get("/dashboard/reporting-preview").status_code == 302
    client.post(
        "/login",
        data={"password": "dashboard-secret"},
    )
    preview = client.get("/dashboard/reporting-preview?period=28d")
    assert preview.status_code == 200
    assert b"Last 28 completed days" in preview.data
    assert b"Preview only" in preview.data
    assert b"0 of 10 foundation metrics ready" in preview.data
    assert b"Cash and the goal" in preview.data
    assert b"The next seven days" in preview.data
    assert b"Strength Assessments booked" in preview.data
    assert b"Assessments pre-qualified" in preview.data
    assert b"Projected recurring income" in preview.data
    assert b"The next accepted Xero refresh will populate expenses" in (
        preview.data
    )
    assert b"Subscribers booking an assessment" in preview.data
    assert b"Assessments becoming new members" in preview.data
    assert b"Successful first week" in preview.data
    assert b"Future-Proofing Score" in preview.data
    assert b"Six primary standards" in preview.data
    assert b"recorded member endings" in preview.data
    assert b"Website analytics is connected and collecting" in preview.data
    assert b"Shadow: six-standard evidence required" in preview.data
    assert b"Provisional history" in preview.data
    assert b'href="#marketing"' in preview.data
    assert b'href="#sales"' in preview.data
    assert b'href="#onboarding"' in preview.data
    assert b'href="#delivery"' in preview.data
    assert b'href="#attrition"' in preview.data
    assert b"Historical Analytics is connected" in preview.data
    assert b"The loss count is visible, but the rate is not accepted yet" in (
        preview.data
    )
    assert b"Active members and membership mix" in preview.data
    assert b"Assessment outcomes" in preview.data
    assert b"Personal training delivery" in preview.data
    assert b"Strength improvement" in preview.data
    assert b"Current week" in preview.data
    invalid = client.get("/dashboard/reporting-preview?period=month")
    assert invalid.status_code == 400
    assert b"period must be week, 28d or 90d" in invalid.data


def test_reporting_v2_preview_shows_xero_expenses_without_transfers(
    monkeypatch,
    tmp_path,
):
    app = make_app(monkeypatch, tmp_path)
    module = importlib.import_module("operating_data_hub.app")
    periods = module.service.reporting_v2.ceo_scorecard_preview(
        "week", as_of="2026-07-30T00:00:00+00:00"
    )["period"]
    module.service.store.accept_snapshot(
        "xero_accounting",
        {
            "schema_version": 2,
            "observed_at": "2026-07-30T00:00:00+00:00",
            "status": "complete",
            "complete": True,
            "rows": [],
            "summary": {"record_count": 0},
            "profit_and_loss": {
                "week": {
                    "period_start": periods["start"],
                    "period_end": periods["end"],
                    "summary": {
                        "complete": True,
                        "total_expenses": "9750.00",
                        "income": "20000.00",
                        "accounting_basis": "accrual",
                        "transfers_excluded": True,
                    },
                }
            },
        },
    )
    client = app.test_client()
    client.post("/login", data={"password": "dashboard-secret"})
    preview = client.get("/dashboard/reporting-preview?period=week")

    assert preview.status_code == 200
    assert b"$9,750" in preview.data
    assert b"Recorded business expenses; transfers and card repayments excluded" in (
        preview.data
    )


def test_reporting_v2_preview_shows_available_rolling_cash_goal(
    monkeypatch,
    tmp_path,
):
    app = make_app(monkeypatch, tmp_path)
    client = app.test_client()
    headers = {"X-Hub-Secret": "test-secret"}
    observed_at = datetime.now(UTC)
    for source, event_id, gross_cents, gst_cents in (
        ("stripe", "pi_1:settled", 11000, 1000),
        ("pt_minder", "debit_1", 9900, 900),
    ):
        response = client.post(
            "/api/v2/reporting/cash-events",
            headers=headers,
            json={
                "source_system": source,
                "source_run_id": f"{source}-cash-current",
                "observed_at": observed_at.isoformat(),
                "complete": True,
                "events": [
                    {
                        "source_event_id": event_id,
                        "occurred_at": (
                            observed_at - timedelta(hours=1)
                        ).isoformat(),
                        "event_type": "settled_cash",
                        "gross_amount_cents": gross_cents,
                        "gst_amount_cents": gst_cents,
                    }
                ],
            },
        )
        assert response.status_code == 200

    client.post("/login", data={"password": "dashboard-secret"})
    preview = client.get("/dashboard/reporting-preview?period=week")

    assert preview.status_code == 200
    assert b"Automatic Stripe and PT Minder cash" in preview.data
    assert b"$190" in preview.data
    assert b"$999,810 remaining" in preview.data
    assert b'class="goal-progress"' in preview.data


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
    assert "entitlement_exception_queue" in payload


def test_identified_entitlement_queue_requires_auth(monkeypatch, tmp_path):
    app = make_app(monkeypatch, tmp_path)
    client = app.test_client()
    assert client.get("/api/v1/entitlement-exceptions").status_code == 401
    response = client.get(
        "/api/v1/entitlement-exceptions",
        headers={"X-Hub-Secret": "test-secret"},
    )
    assert response.status_code == 200
    assert response.get_json()["identified"] is True


def test_sa_feedback_ingestion_is_authenticated_and_idempotent(
    monkeypatch, tmp_path
):
    app = make_app(monkeypatch, tmp_path)
    client = app.test_client()
    payload = {
        "contact_id": "contact-1",
        "form_submission_id": "submission-1",
        "submitted_at": (
            __import__("datetime").datetime.now(
                __import__("datetime").UTC
            ).isoformat()
        ),
        "sales_outcome": "No Sale",
        "delivered_by": "Megan",
        "delivery_key": "submission-1",
    }
    assert client.post("/api/v1/ingest/sa-feedback", json=payload).status_code == 401
    headers = {"X-Hub-Secret": "test-secret"}
    first = client.post(
        "/api/v1/ingest/sa-feedback",
        headers=headers,
        json=payload,
    )
    second = client.post(
        "/api/v1/ingest/sa-feedback",
        headers=headers,
        json=payload,
    )
    assert first.status_code == 200
    assert first.get_json()["status"] == "accepted"
    assert second.get_json()["status"] == "duplicate"


def test_sa_attendance_privacy_boundaries(monkeypatch, tmp_path):
    app = make_app(monkeypatch, tmp_path)
    client = app.test_client()
    headers = {"X-Hub-Secret": "test-secret"}
    assert client.get("/api/v1/sa-attendance/summary").status_code == 401
    aggregate = client.get(
        "/api/v1/sa-attendance/summary",
        headers=headers,
    )
    identified = client.get(
        "/api/v1/sa-attendance/exceptions",
        headers=headers,
    )
    assert aggregate.status_code == 200
    aggregate_body = aggregate.get_json()
    assert "rows" not in aggregate_body
    assert (
        aggregate_body.get("source") is None
        or "payload" not in aggregate_body["source"]
    )
    assert identified.status_code == 200
    assert "rows" in identified.get_json()


def test_sa_followup_preview_is_protected_and_write_free(monkeypatch, tmp_path):
    app = make_app(monkeypatch, tmp_path)
    client = app.test_client()
    path = "/api/v1/sa-attendance/followup-preview"
    assert client.get(path).status_code == 401
    response = client.get(
        path,
        headers={"X-Hub-Secret": "test-secret"},
    )
    assert response.status_code == 200
    assert response.get_json()["result"]["mode"] == "preview"


def test_trainerize_performance_populates_dashboard_and_ceo_report(
    monkeypatch,
    tmp_path,
):
    app = make_app(monkeypatch, tmp_path)
    client = app.test_client()
    headers = {"X-Hub-Secret": "test-secret"}
    accepted = client.post(
        "/api/v1/ingest/trainerize_performance",
        headers=headers,
        json={
            "observed_at": "2026-07-28T00:00:00+00:00",
            "status": "complete",
            "summary": {
                "runId": "performance-run-1",
                "activeRoster": 149,
                "membersWithDetailedWorkouts": 147,
                "reassessmentDue": 100,
                "remarkableCandidates": 68,
                "detailedWorkoutSourceThrough": "2026-07-21",
            },
        },
    )
    assert accepted.status_code == 200

    dashboard = client.get("/api/v1/dashboard", headers=headers).get_json()
    performance = dashboard["trainerize_performance"]
    assert performance["active_roster"] == 149
    assert performance["members_with_detailed_workouts"] == 147
    assert performance["reassessment_due"] == 100
    assert performance["remarkable_candidates"] == 68

    ceo = client.get("/api/v1/ceo-report", headers=headers).get_json()
    assert ceo["trainerize_performance"]["run_id"] == "performance-run-1"


def test_pt_roster_self_mending_populates_dashboard_and_ceo_report(
    monkeypatch,
    tmp_path,
):
    app = make_app(monkeypatch, tmp_path)
    client = app.test_client()
    headers = {"X-Hub-Secret": "test-secret"}
    accepted = client.post(
        "/api/v1/ingest/pt_roster_self_mending",
        headers=headers,
        json={
            "observed_at": "2026-07-29T06:20:00+10:00",
            "status": "complete",
            "summary": {
                "mode": "read_only_shadow",
                "active_pt_rows": 47,
                "confirmed_current_pt": 40,
                "pending_terms": 3,
                "pending_provisioning": 2,
                "exceptions": 2,
                "exact_sales_links": 43,
                "historical_sales_links": 1,
                "legacy_sales_history_unavailable": 15,
                "future_starts": 1,
                "pt_minder_payment_links": 1,
                "absent_sales_history": 1,
                "duplicate_active_identities": 1,
                "duplicate_dominant_pairs_identified": 1,
                "proposed_patches": 9,
                "proposals_eligible_for_owner_approval": 7,
                "proposals_requiring_manual_evidence": 2,
                "writes_enabled": False,
                "action_items": [
                    {
                        "client_name": "Emma Example",
                        "email": "emma@example.com",
                        "state": "pending_provisioning",
                        "reason": "missing_payment_evidence",
                    }
                ],
            },
        },
    )
    assert accepted.status_code == 200

    dashboard = client.get("/api/v1/dashboard", headers=headers).get_json()
    self_mending = dashboard["pt_roster_self_mending"]
    assert self_mending["active_pt_rows"] == 47
    assert self_mending["proposed_patches"] == 9
    assert self_mending["historical_sales_links"] == 1
    assert self_mending["legacy_sales_history_unavailable"] == 15
    assert self_mending["future_starts"] == 1
    assert self_mending["pt_minder_payment_links"] == 1
    assert self_mending["absent_sales_history"] == 1
    assert self_mending["duplicate_active_identities"] == 1
    assert self_mending["duplicate_dominant_pairs_identified"] == 1
    assert self_mending["action_items"][0]["client_name"] == "Emma Example"
    assert (
        self_mending["action_items"][0]["issue"]
        == "Payment or account status needs review"
    )
    assert self_mending["proposals_eligible_for_owner_approval"] == 7
    assert self_mending["proposals_requiring_manual_evidence"] == 2
    assert self_mending["writes_enabled"] is False

    ceo = client.get("/api/v1/ceo-report", headers=headers).get_json()
    assert ceo["pt_roster_self_mending"]["exceptions"] == 2


def test_cohort_ingestion_keeps_ceo_report_aggregate(monkeypatch, tmp_path):
    app = make_app(monkeypatch, tmp_path)
    client = app.test_client()
    headers = {"X-Hub-Secret": "test-secret"}
    accepted = client.post(
        "/api/v1/ingest/active-client-cohort",
        headers=headers,
        json={
            "observed_at": "2026-07-27T10:00:00+00:00",
            "as_of_date": "2026-07-27",
            "rule_version": "active-client-cohort-v1",
            "source_refs": {"membership": "snapshot-1", "roster": "run-1"},
            "rows": [
                {
                    "canonical_key": "member@example.com",
                    "in_legacy_cohort": True,
                    "active_signal": True,
                    "confirmed_active": True,
                    "paid_or_entitled": None,
                    "disposition": "confirmed_active",
                    "primary_reason": "governed_active_roster",
                    "decision_required": False,
                    "evidence": {
                        "roster": True,
                        "governed_roster": [
                            {
                                "service": "SGPT",
                                "status": "Active",
                                "classification": "CLEAN_COLLECTING",
                                "product": "LIMITED (2/wk)",
                            }
                        ],
                    },
                }
            ],
        },
    )
    assert accepted.status_code == 200

    status = client.get("/api/v1/canonical/status", headers=headers)
    assert status.get_json()["cohort"]["confirmed_active_clients"] == 1
    assert status.get_json()["governed"]["confirmed_active_clients"] == 1
    assert status.get_json()["governed"][
        "active_service_relationships"
    ] == 1
    ceo = client.get("/api/v1/ceo-report", headers=headers).get_json()
    assert ceo["active_client_cohort"]["confirmed_active_clients"] == 1
    assert ceo["governed_operating_state"][
        "confirmed_active_clients"
    ] == 1
    assert "member@example.com" not in str(ceo)


def test_commercial_evidence_ingestion_is_authenticated(
    monkeypatch,
    tmp_path,
):
    app = make_app(monkeypatch, tmp_path)
    client = app.test_client()
    payload = {
        "source_system": "stripe",
        "source_run_id": "stripe-run-1",
        "observed_at": "2026-07-28T10:00:00+00:00",
        "rows": [
            {
                "canonical_key": "member@example.com",
                "source_identity_ids": ["cus_123"],
                "entitlements": [
                    {
                        "source_record_id": "sub_123",
                        "service_type": "sgpt",
                        "status": "confirmed",
                        "basis": "active_subscription",
                    }
                ],
                "payment_accounts": [],
                "payment_events": [],
            }
        ],
    }
    assert (
        client.post(
            "/api/v1/ingest/commercial-evidence",
            json=payload,
        ).status_code
        == 401
    )
    response = client.post(
        "/api/v1/ingest/commercial-evidence",
        headers={"X-Hub-Secret": "test-secret"},
        json=payload,
    )

    assert response.status_code == 200
    assert response.get_json()["canonical"]["entitlements"] == 1


def test_roster_candidate_ingestion_populates_acceptance_comparison(
    monkeypatch,
    tmp_path,
):
    app = make_app(monkeypatch, tmp_path)
    client = app.test_client()
    headers = {"X-Hub-Secret": "test-secret"}
    response = client.post(
        "/api/v1/ingest/active-roster-candidate",
        headers=headers,
        json={
            "source_system": "google_sheet",
            "source_run_id": "revenue-run-1",
            "observed_at": "2026-07-28T10:00:00+00:00",
            "as_of_date": "2026-07-28",
            "rows": [
                {
                    "canonical_key": "member@example.com",
                    "services": [
                        {
                            "service_type": "SGPT",
                            "status": "Active",
                            "source_row": 2,
                        }
                    ],
                }
            ],
        },
    )

    assert response.status_code == 200
    dashboard = client.get("/api/v1/dashboard", headers=headers).get_json()
    assert dashboard["roster_candidate"]["candidate_active_clients"] == 1
    assert dashboard["roster_candidate"]["added_since_accepted"] == 1
    ceo = client.get("/api/v1/ceo-report", headers=headers).get_json()
    assert ceo["roster_acceptance"]["candidate_active_clients"] == 1
    assert "member@example.com" not in str(ceo)


def test_service_change_endpoints_are_authenticated_idempotent_and_fail_closed(
    monkeypatch,
    tmp_path,
):
    app = make_app(monkeypatch, tmp_path)
    client = app.test_client()
    path = "/api/v1/service-changes/events"
    requested = {
        "event_type": "requested",
        "event_version": 1,
        "request_id": "msc-test-1",
        "canonical_key": "member@example.com",
        "email": "member@example.com",
        "contact_id": "contact-1",
        "occurred_at": "2026-07-02T09:00:00+10:00",
        "request_date": "2026-07-02",
        "effective_date": "2026-08-05",
        "effective_at": "2026-08-05T00:00:00+10:00",
        "offer_version": "evolved-anywhere-legacy-v1",
        "agreement_version": "legacy-hybrid-survey-v1",
        "signed_at": "2026-07-02T09:00:00+10:00",
        "signature_document": "ghl://submission/submission-1",
        "prior_services": [
            {
                "service_type": "sgpt",
                "service_name": "Strong, Fit & Flexible Membership",
                "weekly_price_cents": 9900,
            }
        ],
        "requested_services": [
            {
                "service_type": "hybrid",
                "service_name": "Evolved Anywhere",
                "weekly_price_cents": 6900,
            }
        ],
        "surface_statuses": {
            "billing": "pending",
            "ghl": "pending",
            "trainerize": "pending",
            "appointments": "pending",
            "workbook": "pending",
            "reporting": "pending",
        },
    }
    assert client.post(path, json=requested).status_code == 401
    headers = {"X-Hub-Secret": "test-secret"}
    prior = client.post(
        "/api/v1/ingest/membership-reconciliation",
        headers=headers,
        json={
            "observed_at": "2026-07-30T00:00:00+10:00",
            "source_run_id": "service-change-prior-state",
            "rows": [
                {
                    "canonical_key": "member@example.com",
                    "email": "member@example.com",
                    "source_ids": {"ghl": ["contact-1"]},
                    "service_type": "sgpt",
                    "service_name": "Strong, Fit & Flexible Membership",
                    "lifecycle_status": "active",
                    "ghl_active": True,
                    "stripe_entitled": True,
                    "trainerize_active": True,
                }
            ],
        },
    )
    assert prior.status_code == 200
    first = client.post(path, headers=headers, json=requested)
    duplicate = client.post(path, headers=headers, json=requested)
    assert first.status_code == 200
    assert duplicate.get_json()["status"] == "duplicate"

    accepted = dict(requested)
    accepted["event_type"] = "accepted"
    accepted["event_version"] = 2
    accepted["occurred_at"] = "2026-08-05T09:00:00+10:00"
    accepted["surface_statuses"] = {
        key: "succeeded"
        for key in requested["surface_statuses"]
    }
    accepted["surface_statuses"]["workbook"] = "pending"
    blocked = client.post(path, headers=headers, json=accepted)
    assert blocked.status_code == 400
    assert "every surface" in blocked.get_json()["error"]

    accepted["surface_statuses"]["workbook"] = "succeeded"
    completed = client.post(path, headers=headers, json=accepted)
    assert completed.status_code == 200
    status = client.get(
        "/api/v1/service-changes/msc-test-1",
        headers=headers,
    )
    assert status.status_code == 200
    assert status.get_json()["status"] == "accepted"
    assert len(status.get_json()["events"]) == 2
