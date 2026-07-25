from __future__ import annotations

import hmac
import logging
import os
import threading
from pathlib import Path

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, jsonify, request

from .config import BRISBANE_TZ, Settings, load_local_env
from .service import RetentionService


load_local_env(Path(__file__).parent / ".env")

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
log = logging.getLogger(__name__)

settings = Settings.from_env()
service = RetentionService(settings)
app = Flask(__name__)
scheduler: BackgroundScheduler | None = None


def _authorised() -> bool:
    supplied = (
        request.headers.get("X-Webhook-Secret")
        or request.headers.get("Authorization", "").removeprefix("Bearer ").strip()
        or request.args.get("secret", "")
    )
    return bool(supplied) and hmac.compare_digest(
        supplied, settings.webhook_secret
    )


def _run(write_sheets: bool) -> None:
    try:
        service.run(write_sheets=write_sheets)
    except Exception:
        log.exception("Retention intelligence run failed")


@app.get("/health")
def health():
    latest = service.store.latest_summary() or {}
    return jsonify(
        {
            "status": "ok",
            "mode": "read_only_shadow",
            "schedulerEnabled": settings.scheduler_enabled,
            "sheetsWriteEnabled": settings.sheets_write_enabled,
            "latestRun": {
                "status": latest.get("status"),
                "completedAt": latest.get("completedAt"),
            },
            "consecutiveSuccessfulRuns": service.store.consecutive_successes(),
        }
    )


@app.post("/run")
def manual_run():
    if not _authorised():
        return jsonify({"error": "unauthorised"}), 401
    write_sheets = (
        str(request.args.get("writeSheets", "false")).lower() == "true"
    )
    if write_sheets and not settings.sheets_write_enabled:
        return jsonify({"error": "Sheet writes are disabled"}), 409
    thread = threading.Thread(
        target=_run,
        args=(write_sheets,),
        daemon=True,
        name="manual-retention-run",
    )
    thread.start()
    return jsonify({"status": "started", "writeSheets": write_sheets}), 202


@app.get("/runs/latest")
def latest_run():
    if not _authorised():
        return jsonify({"error": "unauthorised"}), 401
    summary = service.store.latest_summary()
    return jsonify(summary or {"status": "not_found"}), (200 if summary else 404)


@app.get("/preview")
def preview():
    if not _authorised():
        return jsonify({"error": "unauthorised"}), 401
    return jsonify(service.preview())


def start_scheduler() -> None:
    global scheduler
    if not settings.scheduler_enabled or scheduler is not None:
        return
    scheduler = BackgroundScheduler(timezone=BRISBANE_TZ)
    scheduler.add_job(
        _run,
        "cron",
        hour=5,
        minute=45,
        args=[settings.sheets_write_enabled],
        id="daily-retention-intelligence",
        max_instances=1,
        coalesce=True,
        replace_existing=True,
    )
    scheduler.start()
    log.info("Retention intelligence scheduler started")


start_scheduler()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8080")))
