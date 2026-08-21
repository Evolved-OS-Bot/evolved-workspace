from __future__ import annotations

import hmac
import os
import threading
from datetime import UTC, datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from flask import (
    Flask,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from .config import BRISBANE_TZ, Settings
from .contracts import (
    validate_commercial_evidence,
    validate_membership_reconciliation,
    validate_active_client_cohort,
    validate_active_roster_candidate,
    validate_payment_service_overrides,
    validate_pt_minder,
    validate_sa_feedback,
    validate_service_change_event,
    validate_summary,
)
from .service import HubService
from .xero_adapter import new_oauth_state
from .workflow_extensions import DecisionContractError


settings = Settings.from_env()
service = HubService(settings)
app = Flask(__name__)
app.secret_key = settings.flask_secret
scheduler: BackgroundScheduler | None = None


def _authorised() -> bool:
    supplied = (
        request.headers.get("X-Hub-Secret")
        or request.headers.get("Authorization", "")
        .removeprefix("Bearer ")
        .strip()
    )
    return bool(supplied) and hmac.compare_digest(
        supplied, settings.webhook_secret
    )


def _run(job_id: str, function) -> None:
    try:
        service.run_job(job_id, function)
    except Exception:
        app.logger.exception("Hub job failed: %s", job_id)


@app.get("/health")
def health():
    data = service.dashboard_data()
    return jsonify(
        {
            "status": "ok",
            "mode": "shadow",
            "schedulerEnabled": settings.scheduler_enabled,
            "sourceCount": len(data["sources"]),
            "staleSources": [
                row["source"]
                for row in data["sources"]
                if row["freshness"] == "stale"
            ],
        }
    )


@app.post("/login")
def login():
    supplied = str(request.form.get("password") or "")
    if hmac.compare_digest(supplied, settings.dashboard_password):
        session["hub_dashboard"] = True
        return redirect(url_for("dashboard"))
    return render_template("login.html", error="Incorrect password"), 401


@app.get("/login")
def login_page():
    return render_template("login.html", error=None)


@app.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("login_page"))


@app.get("/")
@app.get("/dashboard")
def dashboard():
    if not session.get("hub_dashboard"):
        return redirect(url_for("login_page"))
    return render_template(
        "dashboard.html",
        data=service.dashboard_data(),
        current_view="ceo",
    )


@app.get("/dashboard/system-health")
def system_health_dashboard():
    if not session.get("hub_dashboard"):
        return redirect(url_for("login_page"))
    return render_template(
        "dashboard.html",
        data=service.dashboard_data(),
        current_view="system",
    )


@app.get("/dashboard/reporting-preview")
def reporting_v2_dashboard_preview():
    if not session.get("hub_dashboard"):
        return redirect(url_for("login_page"))
    period_id = request.args.get("period", "week")
    delivery = service.dashboard_data()
    try:
        scorecard = service.reporting_v2_ceo_scorecard(period_id)
    except ValueError as exc:
        return render_template(
            "reporting_preview.html",
            scorecard=None,
            delivery=delivery,
            selected_period=period_id,
            error=str(exc),
        ), 400
    scorecard["metrics_by_id"] = {
        metric["metric_id"]: metric
        for metric in scorecard.get("metrics", [])
    }
    return render_template(
        "reporting_preview.html",
        scorecard=scorecard,
        delivery=delivery,
        selected_period=period_id,
        error=None,
    )


@app.get("/api/v1/xero/connect")
def xero_connect():
    if not session.get("hub_dashboard"):
        return redirect(url_for("login_page"))
    try:
        client = service.xero_client()
        oauth_state = new_oauth_state()
        session["xero_oauth_state"] = oauth_state
        return redirect(client.authorization_url(oauth_state))
    except RuntimeError as exc:
        return jsonify({"error": str(exc), "mode": "read_only"}), 503


@app.get("/api/v1/xero/callback")
def xero_callback():
    if not session.get("hub_dashboard"):
        return redirect(url_for("login_page"))
    expected_state = str(session.pop("xero_oauth_state", ""))
    supplied_state = str(request.args.get("state") or "")
    if (
        not expected_state
        or not supplied_state
        or not hmac.compare_digest(expected_state, supplied_state)
    ):
        return jsonify({"error": "Invalid Xero OAuth state"}), 400
    if request.args.get("error"):
        return jsonify(
            {
                "error": str(request.args.get("error")),
                "description": str(
                    request.args.get("error_description") or ""
                ),
            }
        ), 400
    code = str(request.args.get("code") or "").strip()
    if not code:
        return jsonify({"error": "Xero did not return an authorisation code"}), 400
    try:
        service.xero_client().connect(code)
        service.run_job(
            "reporting-v2-xero-accounting-refresh",
            service.refresh_xero_accounting,
        )
    except Exception as exc:
        app.logger.exception("Xero connection failed")
        return jsonify({"error": str(exc), "mode": "read_only"}), 502
    return redirect(url_for("system_health_dashboard", xero="connected"))


@app.get("/api/v1/xero/status")
def xero_status():
    if not (_authorised() or session.get("hub_dashboard")):
        return jsonify({"error": "unauthorised"}), 401
    return jsonify(service.xero_status())




@app.get("/api/v1/dashboard")
def dashboard_api():
    if not _authorised():
        return jsonify({"error": "unauthorised"}), 401
    return jsonify(service.dashboard_data())


@app.get("/api/v1/entitlement-exceptions")
def entitlement_exceptions():
    if not _authorised():
        return jsonify({"error": "unauthorised"}), 401
    return jsonify(
        service.store.entitlement_exception_queue(identified=True)
    )


@app.get("/api/v1/workflow-extensions/policies")
def workflow_extension_policies():
    if not _authorised():
        return jsonify({"error": "unauthorised"}), 401
    return jsonify(service.workflow_extension_policies())


@app.get("/api/v1/workflow-extensions/outbox")
def workflow_extension_outbox():
    if not _authorised():
        return jsonify({"error": "unauthorised"}), 401
    try:
        limit = int(request.args.get("limit", "250"))
    except ValueError:
        return jsonify({"error": "limit must be an integer"}), 400
    return jsonify(
        service.workflow_extension_outbox(
            workflow_key=request.args.get("workflowKey"),
            person_id=request.args.get("personId"),
            limit=limit,
        )
    )


@app.post("/api/v1/workflow-extensions/preview")
def workflow_extension_preview():
    if not _authorised():
        return jsonify({"error": "unauthorised"}), 401
    try:
        return jsonify(
            service.accept_workflow_extension_decision(
                request.get_json(force=True),
                persist=False,
            )
        )
    except DecisionContractError as exc:
        return jsonify({"error": str(exc)}), 400


@app.post("/api/v1/workflow-extensions/decisions")
def workflow_extension_decision():
    if not _authorised():
        return jsonify({"error": "unauthorised"}), 401
    try:
        result = service.accept_workflow_extension_decision(
            request.get_json(force=True),
            persist=True,
        )
    except DecisionContractError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(result), 202


@app.get("/api/v1/sources/<source>/latest")
def latest_source_snapshot(source: str):
    if not _authorised():
        return jsonify({"error": "unauthorised"}), 401
    if source not in {
        "google_kpi",
        "pt_minder",
        "membership_reconciliation",
        "active_client_cohort",
        "active_roster_candidate",
        "retention_intelligence",
        "pt_booking_continuity",
        "pt_roster_self_mending",
        "revenue_control",
        "conversation_triage",
        "strength_assessment_prequalification",
        "trainerize_performance",
        "commercial_evidence_stripe",
        "commercial_evidence_stripe_pack",
        "commercial_evidence_pt_minder",
        "commercial_evidence_governed_manual",
        "commercial_evidence_revenue_control",
        "strength_assessment_attendance",
        "ghl_acquisition_v2",
        "xero_accounting",
        "website_analytics_v2",
    }:
        return jsonify({"error": "unknown source"}), 404
    snapshot = service.store.latest_governed_snapshot(source)
    if not snapshot:
        return jsonify({"status": "not_found", "source": source}), 404
    return jsonify(snapshot)


@app.get("/api/v1/ceo-report")
def ceo_report():
    if not _authorised():
        return jsonify({"error": "unauthorised"}), 401
    data = service.dashboard_data()
    metrics = data["metrics"]
    members = metrics.get("members") or {}
    stale = [
        source["source"]
        for source in data["sources"]
        if source["freshness"] == "stale"
    ]
    return jsonify(
        {
            "schema_version": 1,
            "report_id": "ceo-report",
            "generated_at": data["generated_at"],
            "mode": data["mode"],
            "period": metrics.get("period"),
            "decision_metrics": {
                "unique_active_clients": members.get("unique_clients"),
                "service_relationships": members.get(
                    "service_relationships"
                ),
                "cross_service_overlaps": members.get(
                    "cross_service_overlaps"
                ),
                "cash_collected": metrics.get("cash_collected"),
                "recurring_cash_collected": metrics.get(
                    "recurring_cash_collected"
                ),
                "new_cash_collected": metrics.get("new_cash_collected"),
                "year_to_date_cash_collected": metrics.get(
                    "year_to_date_cash_collected"
                ),
                "sales_total": metrics.get("sales_total"),
                "leads_total": metrics.get("leads_total"),
                "bookings_total": metrics.get("bookings_total"),
                "show_rate": metrics.get("show_rate"),
                "conversion_rate": metrics.get("conversion_rate"),
                "sgpt_net": metrics.get("sgpt_net"),
                "pt_net": metrics.get("pt_net"),
                "net_service_movement": metrics.get(
                    "net_service_movement"
                ),
                "pt_bookings": metrics.get("pt_bookings"),
                "pt_booked_hours": metrics.get("pt_booked_hours"),
                "pt_trainer_breakdown": metrics.get(
                    "pt_trainer_breakdown"
                ),
            },
            "acquisition_funnel": data["acquisition_funnel"],
            "strength_assessment_attendance": data[
                "strength_assessment_attendance"
            ],
            "source_health": {
                "accepted_sources": len(data["sources"]),
                "stale_sources": stale,
            },
            "canonical_state": data["canonical"],
            "active_client_cohort": data["cohort"],
            "governed_operating_state": data["governed"],
            "payment_service_governance": data[
                "payment_service_overrides"
            ],
            "pt_roster_self_mending": data[
                "pt_roster_self_mending"
            ],
            "entitlement_exception_queue": data["entitlement_queue"],
            "roster_acceptance": data["roster_candidate"],
            "trainerize_performance": data["trainerize_performance"],
            "open_exceptions": data["exceptions"],
        }
    )


@app.post("/api/v1/ingest/sa-feedback")
def ingest_sa_feedback():
    if not _authorised():
        return jsonify({"error": "unauthorised"}), 401
    if request.content_length and request.content_length > 16_384:
        return jsonify({"error": "payload too large"}), 413
    try:
        payload = validate_sa_feedback(request.get_json(silent=True))
        submitted_at = datetime.fromisoformat(payload["submitted_at"])
        now = datetime.now(UTC)
        if submitted_at > now + timedelta(minutes=10):
            raise ValueError("submitted_at cannot be in the future")
        if submitted_at < now - timedelta(days=7):
            raise ValueError("submitted_at is outside the ingestion window")
        return jsonify(service.ingest_sa_feedback(payload))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@app.get("/api/v1/sa-attendance/summary")
def sa_attendance_summary():
    if not _authorised():
        return jsonify({"error": "unauthorised"}), 401
    return jsonify(service.sa_attendance_state(identified=False))


@app.get("/api/v1/sa-attendance/exceptions")
def sa_attendance_exceptions():
    if not _authorised():
        return jsonify({"error": "unauthorised"}), 401
    return jsonify(service.sa_attendance_state(identified=True))


@app.get("/api/v2/reporting/status")
def reporting_v2_status():
    if not _authorised():
        return jsonify({"error": "unauthorised"}), 401
    return jsonify(service.reporting_v2_state())


@app.get("/api/v2/reporting/cutover-status")
def reporting_v2_cutover_status():
    if not _authorised():
        return jsonify({"error": "unauthorised"}), 401
    try:
        return jsonify(
            service.reporting_v2_cutover_status(
                request.args.get("period", "week")
            )
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@app.post("/api/v2/reporting/publication-decisions")
def reporting_v2_publication_decision():
    if not _authorised():
        return jsonify({"error": "unauthorised"}), 401
    if request.content_length and request.content_length > 16_384:
        return jsonify({"error": "payload too large"}), 413
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "payload must be an object"}), 400
    try:
        return jsonify(
            service.decide_reporting_v2_publication(payload)
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@app.get("/api/v2/reporting/metric-definitions")
def reporting_v2_metric_definitions():
    if not _authorised():
        return jsonify({"error": "unauthorised"}), 401
    return jsonify(
        {
            "schema_version": 1,
            "mode": "shadow",
            "definitions": service.reporting_v2_definitions(),
        }
    )


@app.get("/api/v2/reporting/membership-lifecycle")
def reporting_v2_membership_lifecycle():
    if not _authorised():
        return jsonify({"error": "unauthorised"}), 401
    try:
        return jsonify(
            service.reporting_v2_membership_lifecycle(
                request.args.get("period", "week")
            )
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@app.post("/api/v2/reporting/membership-lifecycle/backfill")
def reporting_v2_membership_lifecycle_backfill():
    if not _authorised():
        return jsonify({"error": "unauthorised"}), 401
    if request.content_length and request.content_length > 2_000_000:
        return jsonify({"error": "payload too large"}), 413
    try:
        return jsonify(
            service.reporting_v2_membership_lifecycle_backfill(
                request.get_json(silent=True) or {}
            )
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@app.get("/api/v2/reporting/current-people")
def reporting_v2_current_people():
    if not _authorised():
        return jsonify({"error": "unauthorised"}), 401
    try:
        return jsonify(
            service.reporting_v2_current_people(
                request.args.get("period", "week")
            )
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@app.get("/api/v2/reporting/board-pack-contract")
def reporting_v2_board_pack_contract():
    if not _authorised():
        return jsonify({"error": "unauthorised"}), 401
    return jsonify(service.reporting_v2_board_pack_contract())


@app.get("/api/v2/reporting/acquisition-preview")
def reporting_v2_acquisition_preview():
    if not _authorised():
        return jsonify({"error": "unauthorised"}), 401
    return jsonify(service.reporting_v2_acquisition_preview())


@app.get("/api/v2/reporting/sgpt-delivery")
def reporting_v2_sgpt_delivery():
    if not _authorised():
        return jsonify({"error": "unauthorised"}), 401
    try:
        return jsonify(
            service.reporting_v2_sgpt_delivery(
                period=request.args.get("period", "week"),
                identified=True,
            )
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@app.get("/api/v2/reporting/ceo-scorecard")
def reporting_v2_ceo_scorecard():
    if not _authorised():
        return jsonify({"error": "unauthorised"}), 401
    try:
        return jsonify(
            service.reporting_v2_ceo_scorecard(
                request.args.get("period", "week")
            )
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@app.post("/api/v2/reporting/parallel-results")
def reporting_v2_parallel_results():
    if not _authorised():
        return jsonify({"error": "unauthorised"}), 401
    if request.content_length and request.content_length > 65_536:
        return jsonify({"error": "payload too large"}), 413
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "payload must be an object"}), 400
    try:
        return jsonify(
            service.record_reporting_v2_parallel_result(payload)
        )
    except (TypeError, ValueError) as exc:
        return jsonify({"error": str(exc)}), 400


@app.post("/api/v2/reporting/cash-events")
def reporting_v2_cash_events():
    if not _authorised():
        return jsonify({"error": "unauthorised"}), 401
    if request.content_length and request.content_length > 2_000_000:
        return jsonify({"error": "payload too large"}), 413
    try:
        return jsonify(
            service.submit_reporting_v2_cash_batch(
                request.get_json(silent=True) or {}
            )
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@app.post("/api/v2/reporting/manual-inputs")
def reporting_v2_manual_input():
    if not _authorised():
        return jsonify({"error": "unauthorised"}), 401
    if not settings.reporting_v2_manual_inputs_enabled:
        return jsonify({"error": "manual inputs are disabled"}), 409
    if request.content_length and request.content_length > 16_384:
        return jsonify({"error": "payload too large"}), 413
    try:
        return jsonify(
            service.submit_reporting_v2_manual_input(
                request.get_json(silent=True) or {}
            )
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@app.post("/api/v2/reporting/manual-inputs/<input_id>/decision")
def reporting_v2_manual_input_decision(input_id: str):
    if not _authorised():
        return jsonify({"error": "unauthorised"}), 401
    if not settings.reporting_v2_manual_inputs_enabled:
        return jsonify({"error": "manual inputs are disabled"}), 409
    try:
        return jsonify(
            service.decide_reporting_v2_manual_input(
                input_id,
                request.get_json(silent=True) or {},
            )
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@app.post("/api/v1/ingest/pt-minder")
def ingest_pt_minder():
    if not _authorised():
        return jsonify({"error": "unauthorised"}), 401
    try:
        payload = validate_pt_minder(request.get_json(silent=True))
        return jsonify(service.store.accept_pt_minder_snapshot(payload))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@app.post("/api/v1/ingest/membership-reconciliation")
def ingest_membership_reconciliation():
    if not _authorised():
        return jsonify({"error": "unauthorised"}), 401
    try:
        payload = validate_membership_reconciliation(
            request.get_json(silent=True)
        )
        return jsonify(service.accept_membership_snapshot(payload))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@app.post("/api/v1/service-changes/events")
def ingest_service_change_event():
    if not _authorised():
        return jsonify({"error": "unauthorised"}), 401
    try:
        payload = validate_service_change_event(
            request.get_json(silent=True)
        )
        return jsonify(service.store.accept_service_change_event(payload))
    except ValueError as exc:
        status_code = 409 if any(
            marker in str(exc)
            for marker in (
                "already pending",
                "already used",
                "does not match",
                "current service state",
                "no longer pending",
                "has not been accepted",
                "already exists",
            )
        ) else 400
        return jsonify({"error": str(exc)}), status_code


@app.get("/api/v1/service-changes/<request_id>")
def service_change_status(request_id: str):
    if not _authorised():
        return jsonify({"error": "unauthorised"}), 401
    state = service.store.service_change_state(request_id)
    if not state:
        return jsonify({"status": "not_found"}), 404
    return jsonify(state)


@app.post("/api/v1/ingest/active-client-cohort")
def ingest_active_client_cohort():
    if not _authorised():
        return jsonify({"error": "unauthorised"}), 401
    try:
        payload = validate_active_client_cohort(
            request.get_json(silent=True)
        )
        return jsonify(
            service.store.accept_active_client_cohort(payload)
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@app.post("/api/v1/ingest/active-roster-candidate")
def ingest_active_roster_candidate():
    if not _authorised():
        return jsonify({"error": "unauthorised"}), 401
    try:
        payload = validate_active_roster_candidate(
            request.get_json(silent=True)
        )
        return jsonify(
            service.store.accept_snapshot("active_roster_candidate", payload)
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@app.post("/api/v1/governance/promote-roster-candidate")
def promote_active_roster_candidate():
    if not _authorised():
        return jsonify({"error": "unauthorised"}), 401
    payload = request.get_json(silent=True)
    expected_snapshot_id = (
        str(payload.get("expected_snapshot_id") or "").strip()
        if isinstance(payload, dict)
        else ""
    )
    if not expected_snapshot_id:
        return jsonify({"error": "expected_snapshot_id is required"}), 400
    try:
        return jsonify(
            service.store.promote_roster_candidate(
                expected_snapshot_id=expected_snapshot_id
            )
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 409


@app.post("/api/v1/governance/payment-service-overrides")
def ingest_payment_service_overrides():
    if not _authorised():
        return jsonify({"error": "unauthorised"}), 401
    try:
        payload = validate_payment_service_overrides(
            request.get_json(silent=True)
        )
        return jsonify(
            service.store.accept_payment_service_overrides(payload)
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@app.get("/api/v1/governance/payment-service-overrides")
def payment_service_override_status():
    if not _authorised():
        return jsonify({"error": "unauthorised"}), 401
    return jsonify(service.store.payment_service_override_state())


@app.post("/api/v1/ingest/commercial-evidence")
def ingest_commercial_evidence():
    if not _authorised():
        return jsonify({"error": "unauthorised"}), 401
    try:
        payload = validate_commercial_evidence(
            request.get_json(silent=True)
        )
        return jsonify(
            service.store.accept_commercial_evidence(payload)
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@app.get("/api/v1/canonical/status")
def canonical_status():
    if not _authorised():
        return jsonify({"error": "unauthorised"}), 401
    return jsonify(
        {
            "status": "ok",
            "mode": "shadow",
            "counts": service.store.canonical_counts(),
            "cohort": service.store.latest_cohort_summary(),
            "governed": service.store.governed_state(),
            "roster_candidate": service.store.roster_candidate_state(),
        }
    )


@app.post("/api/v1/ingest/<source>")
def ingest_summary(source: str):
    if not _authorised():
        return jsonify({"error": "unauthorised"}), 401
    allowed = {
        "retention_intelligence",
        "pt_booking_continuity",
        "pt_roster_self_mending",
        "revenue_control",
        "conversation_triage",
        "strength_assessment_prequalification",
        "trainerize_performance",
        "google_kpi",
    }
    if source not in allowed:
        return jsonify({"error": "unregistered source"}), 404
    try:
        payload = validate_summary(source, request.get_json(silent=True))
        return jsonify(service.store.accept_snapshot(source, payload))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@app.post("/api/v1/jobs/poll-health")
def manual_poll():
    if not _authorised():
        return jsonify({"error": "unauthorised"}), 401
    thread = threading.Thread(
        target=_run,
        args=("compatibility-health", service.poll_compatibility_health),
        daemon=True,
    )
    thread.start()
    return jsonify({"status": "started"}), 202


@app.post("/api/v1/jobs/kpi-refresh")
def manual_kpi_refresh():
    if not _authorised():
        return jsonify({"error": "unauthorised"}), 401
    thread = threading.Thread(
        target=_run,
        args=("kpi-refresh", service.refresh_kpi),
        daemon=True,
    )
    thread.start()
    return jsonify({"status": "started"}), 202


@app.post("/api/v1/jobs/sa-attendance-refresh")
def manual_sa_attendance_refresh():
    if not _authorised():
        return jsonify({"error": "unauthorised"}), 401
    thread = threading.Thread(
        target=_run,
        args=("sa-attendance-refresh", service.refresh_sa_attendance),
        daemon=True,
    )
    thread.start()
    return jsonify({"status": "started"}), 202


@app.get("/api/v1/sa-attendance/followup-preview")
def sa_attendance_followup_preview():
    if not _authorised():
        return jsonify({"error": "unauthorised"}), 401
    return jsonify(service.sa_attendance_followup(execute=False))


@app.post("/api/v1/jobs/sa-attendance-followups")
def manual_sa_attendance_followups():
    if not _authorised():
        return jsonify({"error": "unauthorised"}), 401
    if not settings.sa_task_write_enabled:
        return jsonify({"error": "Task writes are disabled"}), 409
    thread = threading.Thread(
        target=_run,
        args=(
            "sa-attendance-followups",
            lambda: service.sa_attendance_followup(execute=True),
        ),
        daemon=True,
    )
    thread.start()
    return jsonify({"status": "started"}), 202


@app.post("/api/v2/reporting/jobs/ghl-acquisition-refresh")
def manual_reporting_v2_ghl_acquisition_refresh():
    if not _authorised():
        return jsonify({"error": "unauthorised"}), 401
    thread = threading.Thread(
        target=_run,
        args=(
            "reporting-v2-ghl-acquisition-refresh",
            service.refresh_reporting_v2_ghl_acquisition,
        ),
        daemon=True,
    )
    thread.start()
    return jsonify({"status": "started", "mode": "shadow"}), 202


@app.post("/api/v2/reporting/jobs/website-analytics-refresh")
def manual_website_analytics_refresh():
    if not _authorised():
        return jsonify({"error": "unauthorised"}), 401
    thread = threading.Thread(
        target=_run,
        args=(
            "reporting-v2-website-analytics-refresh",
            service.refresh_website_analytics,
        ),
        daemon=True,
    )
    thread.start()
    return jsonify({"status": "started", "mode": "shadow"}), 202


@app.post("/api/v2/reporting/jobs/cash-refresh")
def manual_reporting_v2_cash_refresh():
    if not _authorised():
        return jsonify({"error": "unauthorised"}), 401
    thread = threading.Thread(
        target=_run,
        args=(
            "reporting-v2-cash-refresh",
            service.refresh_reporting_v2_cash,
        ),
        daemon=True,
    )
    thread.start()
    return jsonify({"status": "started", "mode": "shadow"}), 202


@app.post("/api/v2/reporting/jobs/sa-listed-history-refresh")
def manual_sa_listed_history_refresh():
    if not _authorised():
        return jsonify({"error": "unauthorised"}), 401
    thread = threading.Thread(
        target=_run,
        args=(
            "reporting-v2-sa-listed-history-refresh",
            service.refresh_sa_listed_history,
        ),
        daemon=True,
    )
    thread.start()
    return jsonify({"status": "started", "mode": "shadow"}), 202


@app.get("/api/v2/reporting/onboarding-followup-preview")
def reporting_v2_onboarding_followup_preview():
    if not _authorised():
        return jsonify({"error": "unauthorised"}), 401
    try:
        return jsonify(
            service.onboarding_completion_followup(execute=False)
        )
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 409


@app.post("/api/v2/reporting/jobs/onboarding-followups")
def manual_reporting_v2_onboarding_followups():
    if not _authorised():
        return jsonify({"error": "unauthorised"}), 401
    if not settings.onboarding_task_write_enabled:
        return jsonify({"error": "Task writes are disabled"}), 409
    thread = threading.Thread(
        target=_run,
        args=(
            "reporting-v2-onboarding-followups",
            lambda: service.onboarding_completion_followup(execute=True),
        ),
        daemon=True,
    )
    thread.start()
    return jsonify({"status": "started", "mode": "governed_task"}), 202


@app.post("/api/v1/jobs/sa-attendance-publish")
def manual_sa_attendance_publish():
    if not _authorised():
        return jsonify({"error": "unauthorised"}), 401
    if not settings.sa_sheets_write_enabled:
        return jsonify({"error": "Sheet writes are disabled"}), 409
    thread = threading.Thread(
        target=_run,
        args=(
            "sa-attendance-publish",
            service.publish_sa_attendance_sheet,
        ),
        daemon=True,
    )
    thread.start()
    return jsonify({"status": "started"}), 202


@app.post("/api/v1/jobs/xero-accounting-refresh")
def manual_xero_accounting_refresh():
    if not _authorised():
        return jsonify({"error": "unauthorised"}), 401
    if not service.xero_status().get("connected"):
        return jsonify({"error": "Xero is not connected"}), 409
    thread = threading.Thread(
        target=_run,
        args=(
            "reporting-v2-xero-accounting-refresh",
            service.refresh_xero_accounting,
        ),
        daemon=True,
    )
    thread.start()
    return jsonify({"status": "started", "mode": "shadow"}), 202


def start_scheduler() -> None:
    global scheduler
    if not settings.scheduler_enabled or scheduler is not None:
        return
    scheduler = BackgroundScheduler(timezone=BRISBANE_TZ)
    scheduler.add_job(
        _run,
        "cron",
        hour="6,18",
        minute=2,
        args=[
            "reporting-v2-website-analytics-refresh",
            service.refresh_website_analytics,
        ],
        id="twice-daily-reporting-v2-website-analytics",
        max_instances=1,
        coalesce=True,
        replace_existing=True,
    )
    scheduler.add_job(
        _run,
        "cron",
        hour="6,18",
        minute=18,
        args=[
            "reporting-v2-ghl-acquisition-refresh",
            service.refresh_reporting_v2_ghl_acquisition,
        ],
        id="twice-daily-reporting-v2-ghl-acquisition",
        max_instances=1,
        coalesce=True,
        replace_existing=True,
    )
    scheduler.add_job(
        _run,
        "cron",
        hour="6,18",
        minute=10,
        args=["sa-attendance-refresh", service.refresh_sa_attendance],
        id="twice-daily-sa-attendance-refresh",
        max_instances=1,
        coalesce=True,
        replace_existing=True,
    )
    scheduler.add_job(
        _run,
        "cron",
        hour="6,18",
        minute=15,
        args=[
            "sa-attendance-followups",
            lambda: service.sa_attendance_followup(
                execute=settings.sa_task_write_enabled
            ),
        ],
        id="twice-daily-sa-attendance-followups",
        max_instances=1,
        coalesce=True,
        replace_existing=True,
    )
    scheduler.add_job(
        _run,
        "cron",
        hour="6,18",
        minute=20,
        args=[
            "reporting-v2-cash-refresh",
            service.refresh_reporting_v2_cash,
        ],
        id="twice-daily-reporting-v2-cash",
        max_instances=1,
        coalesce=True,
        replace_existing=True,
    )
    scheduler.add_job(
        _run,
        "cron",
        hour="6,18",
        minute=22,
        args=[
            "reporting-v2-sa-listed-history-refresh",
            service.refresh_sa_listed_history,
        ],
        id="twice-daily-reporting-v2-sa-listed-history",
        max_instances=1,
        coalesce=True,
        replace_existing=True,
    )
    if service.xero_status().get("connected"):
        scheduler.add_job(
            _run,
            "cron",
            hour="6,18",
            minute=24,
            args=[
                "reporting-v2-xero-accounting-refresh",
                service.refresh_xero_accounting,
            ],
            id="twice-daily-reporting-v2-xero-accounting",
            max_instances=1,
            coalesce=True,
            replace_existing=True,
        )
    scheduler.add_job(
        _run,
        "cron",
        hour="6,18",
        minute=25,
        args=["compatibility-health", service.poll_compatibility_health],
        id="twice-daily-compatibility-health",
        max_instances=1,
        coalesce=True,
        replace_existing=True,
    )
    scheduler.add_job(
        _run,
        "cron",
        hour="6,18",
        minute=30,
        args=[
            "reporting-v2-onboarding-followups",
            lambda: service.onboarding_completion_followup(
                execute=settings.onboarding_task_write_enabled
            ),
        ],
        id="twice-daily-reporting-v2-onboarding-followups",
        max_instances=1,
        coalesce=True,
        replace_existing=True,
    )
    scheduler.add_job(
        _run,
        "cron",
        hour="6,18",
        minute=5,
        args=["kpi-refresh", service.refresh_kpi],
        id="twice-daily-kpi-refresh",
        max_instances=1,
        coalesce=True,
        replace_existing=True,
    )
    scheduler.start()


start_scheduler()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8080")))
