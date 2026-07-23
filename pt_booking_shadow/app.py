from __future__ import annotations

import hmac
import logging
import os
import threading
import uuid
from pathlib import Path

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, jsonify, request

from .config import BRISBANE_TZ, Settings, load_local_env
from .service import ShadowAuditService


load_local_env(Path(__file__).parent / ".env")

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
log = logging.getLogger(__name__)

settings = Settings.from_env()
service = ShadowAuditService(settings)
app = Flask(__name__)
scheduler: BackgroundScheduler | None = None


def _authorised() -> bool:
    supplied = (
        request.headers.get("X-Webhook-Secret")
        or request.headers.get("Authorization", "").removeprefix("Bearer ").strip()
        or request.args.get("secret", "")
    )
    return bool(supplied) and hmac.compare_digest(supplied, settings.webhook_secret)


def _start_full_audit(send_email: bool) -> None:
    try:
        run_id, findings = service.run_full(send_email=send_email)
        log.info("Full shadow audit complete: run=%s contacts=%s", run_id, len(findings))
    except Exception:
        log.exception("Full shadow audit failed")


@app.get("/health")
def health():
    return jsonify(
        {
            "status": "ok",
            "shadowMode": settings.shadow_mode,
            "lastSuccessfulRun": service.store.last_successful_run(),
            "schedulerEnabled": settings.scheduler_enabled,
        }
    )


@app.post("/run")
def manual_run():
    if not _authorised():
        return jsonify({"error": "unauthorised"}), 401
    send_email = str(request.args.get("sendEmail", "false")).lower() == "true"
    thread = threading.Thread(
        target=_start_full_audit, args=(send_email,), daemon=True, name="manual-shadow-audit"
    )
    thread.start()
    return jsonify({"status": "started", "sendEmail": send_email}), 202


@app.post("/webhooks/ghl")
def ghl_webhook():
    if not _authorised():
        return jsonify({"error": "unauthorised"}), 401
    payload = request.get_json(silent=True) or {}
    contact_id = (
        payload.get("contactId")
        or payload.get("contact_id")
        or (payload.get("contact") or {}).get("id")
    )
    if not contact_id:
        return jsonify({"error": "contactId is required"}), 400
    event_id = str(payload.get("id") or payload.get("eventId") or uuid.uuid4())
    event_type = str(payload.get("type") or payload.get("eventType") or "unknown")
    inserted = service.store.enqueue_event(event_id, str(contact_id), event_type)
    return jsonify({"status": "queued" if inserted else "duplicate"}), 202


def start_scheduler() -> None:
    global scheduler
    if not settings.scheduler_enabled or scheduler is not None:
        return
    scheduler = BackgroundScheduler(timezone=BRISBANE_TZ)
    scheduler.add_job(
        _start_full_audit,
        "cron",
        day_of_week="mon",
        hour=5,
        minute=30,
        args=[True],
        id="weekly-full-audit",
        max_instances=1,
        coalesce=True,
        replace_existing=True,
    )
    scheduler.add_job(
        service.process_due_events,
        "interval",
        minutes=1,
        id="process-event-queue",
        max_instances=1,
        coalesce=True,
        replace_existing=True,
    )
    scheduler.start()
    log.info("PT shadow scheduler started")


start_scheduler()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8080")))
