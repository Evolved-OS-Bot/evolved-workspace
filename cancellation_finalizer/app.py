from __future__ import annotations

import hmac
import os
import uuid
from datetime import UTC, datetime

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, g, jsonify, request
from werkzeug.exceptions import RequestEntityTooLarge

from .config import Settings
from .engine import Finalizer, normalize_payload
from .integrations import ProductionIntegrations
from .repository import FinalizationCase, Repository
from .security import (
    FixedWindowRateLimiter,
    log_security_event,
    network_fingerprint,
    verify_signature,
)


def _webhook_case(case: FinalizationCase) -> dict[str, object]:
    return {
        "idempotency_key": case.idempotency_key,
        "status": case.status,
        "current_step": case.current_step,
    }


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
    webhook_limiter = FixedWindowRateLimiter(
        configured.webhook_rate_limit_per_minute
    )
    admin_limiter = FixedWindowRateLimiter(configured.admin_rate_limit_per_minute)

    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = 32_768
    app.config["SETTINGS"] = configured
    app.config["REPOSITORY"] = repo
    app.config["FINALIZER"] = finalizer

    def request_network_key() -> str:
        return network_fingerprint(request.remote_addr or "unknown")

    def audit(event: str, outcome: str, **details: str | int | bool) -> None:
        log_security_event(
            event,
            outcome,
            request_id=g.request_id,
            network=request_network_key(),
            **details,
        )

    def admin_authorised() -> tuple[bool, str]:
        if not admin_limiter.allow(request_network_key()):
            audit("admin_auth", "rate_limited")
            return False, "rate_limited"
        supplied = request.headers.get("X-Cancellation-Admin-Secret", "").strip()
        accepted = bool(supplied and configured.admin_secret) and hmac.compare_digest(
            supplied, configured.admin_secret
        )
        if not accepted:
            audit("admin_auth", "rejected")
            return False, "rejected"
        return True, "accepted"

    def require_admin():
        accepted, reason = admin_authorised()
        if accepted:
            return None
        if reason == "rate_limited":
            return jsonify({"error": "request rejected"}), 429
        return jsonify({"error": "unauthorised"}), 401

    def webhook_authorised(body: bytes) -> tuple[bool, str]:
        if not webhook_limiter.allow(request_network_key()):
            audit("webhook_auth", "rate_limited")
            return False, "rate_limited"
        timestamp = request.headers.get("X-Cancellation-Timestamp", "").strip()
        nonce = request.headers.get("X-Cancellation-Nonce", "").strip()
        signature = request.headers.get("X-Cancellation-Signature", "").strip()
        current = datetime.now(UTC)
        result = verify_signature(
            secret=configured.webhook_signing_secret,
            timestamp=timestamp,
            nonce=nonce,
            signature=signature,
            body=body,
            now=current,
            tolerance_seconds=configured.signature_tolerance_seconds,
        )
        if not result.accepted or result.timestamp is None:
            audit("webhook_auth", "rejected", reason=result.reason)
            return False, result.reason
        claimed = repo.claim_webhook_nonce(
            nonce=result.nonce,
            body=body,
            signed_at=result.timestamp,
            now=current,
            tolerance_seconds=configured.signature_tolerance_seconds,
        )
        if not claimed:
            audit("webhook_auth", "replay_rejected")
            return False, "replayed_nonce"
        audit("webhook_auth", "accepted")
        return True, "accepted"

    @app.before_request
    def assign_request_id():
        g.request_id = uuid.uuid4().hex

    @app.after_request
    def secure_response(response):
        response.headers["Cache-Control"] = "no-store"
        response.headers["Content-Security-Policy"] = "default-src 'none'"
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
        response.headers["Permissions-Policy"] = (
            "camera=(), geolocation=(), microphone=(), payment=(), usb=()"
        )
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Request-Id"] = g.get("request_id", "")
        return response

    @app.errorhandler(RequestEntityTooLarge)
    def request_too_large(_error):
        audit("request", "rejected", reason="payload_too_large")
        return jsonify({"error": "request rejected"}), 413

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    @app.get("/api/v1/admin/readiness")
    def readiness():
        denied = require_admin()
        if denied is not None:
            return denied
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
        body = request.get_data(cache=True, as_text=False)
        accepted, reason = webhook_authorised(body)
        if not accepted:
            status_code = (
                429
                if reason == "rate_limited"
                else 409
                if reason == "replayed_nonce"
                else 401
            )
            return jsonify({"error": "request rejected"}), status_code
        try:
            payload = normalize_payload(request.get_json(silent=True) or {})
            case = repo.upsert(payload, now=datetime.now(UTC))
            case = finalizer.process(case.idempotency_key)
        except ValueError:
            audit("webhook_request", "rejected", reason="invalid_payload")
            return jsonify({"error": "invalid cancellation request"}), 400
        audit("webhook_request", "processed", status=case.status)
        status_code = 200 if case.status == "completed" else 202
        return jsonify(_webhook_case(case)), status_code

    @app.get("/api/v1/admin/cancellations/<key>")
    def status(key: str):
        denied = require_admin()
        if denied is not None:
            return denied
        case = repo.get(key)
        if case is None:
            return jsonify({"status": "not_found"}), 404
        return jsonify(case.public())

    @app.post("/api/v1/admin/jobs/process-due")
    def process_due():
        denied = require_admin()
        if denied is not None:
            return denied
        processed = finalizer.process_due()
        audit("admin_job", "processed", cases=processed)
        return jsonify({"processed": processed})

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
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "8080")))
