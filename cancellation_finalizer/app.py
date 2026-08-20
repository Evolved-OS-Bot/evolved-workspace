from __future__ import annotations

import hmac
import os
from datetime import UTC, datetime

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, jsonify, request

from .config import Settings
from .engine import Finalizer, normalize_payload
from .integrations import ProductionIntegrations
from .repository import Repository


def create_app(
    settings: Settings | None = None,
    *,
    repository: Repository | None = None,
    integrations=None,
) -> Flask:
    configured = settings or Settings.from_env()
    repo = repository or Repository(configured.database_url)
    repo.create_schema()
    external = integrations or ProductionIntegrations(configured)
    finalizer = Finalizer(repo, external)

    app = Flask(__name__)
    app.config["SETTINGS"] = configured
    app.config["REPOSITORY"] = repo
    app.config["FINALIZER"] = finalizer

    def authorised() -> bool:
        supplied = request.headers.get("X-Cancellation-Secret", "").strip()
        return bool(supplied and configured.api_secret) and hmac.compare_digest(
            supplied, configured.api_secret
        )

    @app.get("/health")
    def health():
        return jsonify(
            {
                "status": "ok",
                "writeEnabled": configured.write_enabled,
                "workerEnabled": configured.worker_enabled,
                "missingLiveConfiguration": configured.missing_live_configuration(),
            }
        )

    @app.post("/api/v1/cancellations/finalize")
    def finalize():
        if not authorised():
            return jsonify({"error": "unauthorised"}), 401
        if request.content_length and request.content_length > 32_768:
            return jsonify({"error": "payload too large"}), 413
        try:
            payload = normalize_payload(request.get_json(silent=True) or {})
            case = repo.upsert(payload, now=datetime.now(UTC))
            case = finalizer.process(case.idempotency_key)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        status = 200 if case.status == "completed" else 202
        return jsonify(case.public()), status

    @app.get("/api/v1/cancellations/<key>")
    def status(key: str):
        if not authorised():
            return jsonify({"error": "unauthorised"}), 401
        case = repo.get(key)
        if case is None:
            return jsonify({"status": "not_found"}), 404
        return jsonify(case.public())

    @app.post("/api/v1/jobs/process-due")
    def process_due():
        if not authorised():
            return jsonify({"error": "unauthorised"}), 401
        return jsonify({"processed": finalizer.process_due()})

    return app


scheduler: BackgroundScheduler | None = None


def start_scheduler(app: Flask, settings: Settings) -> None:
    global scheduler
    if scheduler is not None or not settings.worker_enabled:
        return
    scheduler = BackgroundScheduler(timezone="Australia/Brisbane")
    scheduler.add_job(
        app.config["FINALIZER"].process_due,
        "interval",
        minutes=10,
        id="cancellation-finalizer-due-worker",
        max_instances=1,
        coalesce=True,
        replace_existing=True,
    )
    scheduler.start()


if __name__ == "__main__":
    settings = Settings.from_env()
    app = create_app(settings)
    start_scheduler(app, settings)
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8080")))
