from __future__ import annotations

import hmac
import os
import threading
from datetime import datetime

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
from .contracts import validate_pt_minder, validate_summary
from .service import HubService


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
    return render_template("dashboard.html", data=service.dashboard_data())


@app.get("/api/v1/dashboard")
def dashboard_api():
    if not _authorised():
        return jsonify({"error": "unauthorised"}), 401
    return jsonify(service.dashboard_data())


@app.get("/api/v1/sources/<source>/latest")
def latest_source_snapshot(source: str):
    if not _authorised():
        return jsonify({"error": "unauthorised"}), 401
    if source not in {
        "google_kpi",
        "pt_minder",
        "retention_intelligence",
        "pt_booking_continuity",
        "revenue_control",
        "conversation_triage",
        "strength_assessment_prequalification",
        "trainerize_performance",
    }:
        return jsonify({"error": "unknown source"}), 404
    snapshot = service.store.latest_snapshot(source)
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
                "pt_bookings": metrics.get("pt_bookings"),
                "pt_booked_hours": metrics.get("pt_booked_hours"),
            },
            "source_health": {
                "accepted_sources": len(data["sources"]),
                "stale_sources": stale,
            },
            "open_exceptions": data["exceptions"],
        }
    )


@app.post("/api/v1/ingest/pt-minder")
def ingest_pt_minder():
    if not _authorised():
        return jsonify({"error": "unauthorised"}), 401
    try:
        payload = validate_pt_minder(request.get_json(silent=True))
        return jsonify(service.store.accept_snapshot("pt_minder", payload))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@app.post("/api/v1/ingest/<source>")
def ingest_summary(source: str):
    if not _authorised():
        return jsonify({"error": "unauthorised"}), 401
    allowed = {
        "retention_intelligence",
        "pt_booking_continuity",
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


def start_scheduler() -> None:
    global scheduler
    if not settings.scheduler_enabled or scheduler is not None:
        return
    scheduler = BackgroundScheduler(timezone=BRISBANE_TZ)
    scheduler.add_job(
        _run,
        "interval",
        minutes=15,
        args=["compatibility-health", service.poll_compatibility_health],
        id="compatibility-health",
        max_instances=1,
        coalesce=True,
        replace_existing=True,
    )
    scheduler.add_job(
        _run,
        "cron",
        hour=6,
        minute=5,
        args=["kpi-refresh", service.refresh_kpi],
        id="daily-kpi-refresh",
        max_instances=1,
        coalesce=True,
        replace_existing=True,
    )
    scheduler.start()


start_scheduler()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8080")))
