from __future__ import annotations

import hmac
import os
import secrets
import uuid
from datetime import UTC, datetime

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, g, jsonify, request
from werkzeug.exceptions import RequestEntityTooLarge

from .config import Settings
from .engine import Finalizer, normalize_payload
from .integrations import ProductionIntegrations
from .repository import FinalizationCase, Repository
from .relay import RelayPayloadError, canonical_relay_request
from .security import (
    FixedWindowRateLimiter,
    calculate_signature,
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
    relay_limiter = FixedWindowRateLimiter(configured.relay_rate_limit_per_minute)
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

    def signed_webhook_authorised(
        body: bytes,
        *,
        timestamp: str,
        nonce: str,
        signature: str,
    ) -> tuple[bool, str]:
        if not webhook_limiter.allow(request_network_key()):
            audit("webhook_auth", "rate_limited")
            return False, "rate_limited"
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

    def webhook_authorised(body: bytes) -> tuple[bool, str]:
        return signed_webhook_authorised(
            body,
            timestamp=request.headers.get("X-Cancellation-Timestamp", "").strip(),
            nonce=request.headers.get("X-Cancellation-Nonce", "").strip(),
            signature=request.headers.get("X-Cancellation-Signature", "").strip(),
        )

    def relay_authorised(service: str) -> tuple[bool, str]:
        if not configured.relay_enabled:
            return False, "disabled"
        if configured.relay_configuration_issues():
            audit("relay_auth", "rejected", reason="misconfigured", service=service)
            return False, "misconfigured"
        if not relay_limiter.allow(request_network_key()):
            audit("relay_auth", "rate_limited", service=service)
            return False, "rate_limited"
        expected = {
            "membership": configured.relay_membership_secret,
            "pt": configured.relay_pt_secret,
        }.get(service, "")
        authorization = request.headers.get("Authorization", "")
        scheme, separator, supplied = authorization.partition(" ")
        accepted = bool(
            expected
            and separator
            and scheme == "Bearer"
            and supplied
            and " " not in supplied
        ) and hmac.compare_digest(supplied, expected)
        if not accepted:
            audit("relay_auth", "rejected", service=service)
            return False, "rejected"
        audit("relay_auth", "accepted", service=service)
        return True, "accepted"

    def process_payload(payload: dict, *, audit_event: str):
        try:
            normalized = normalize_payload(payload)
            case = repo.upsert(normalized, now=datetime.now(UTC))
            case = finalizer.process(case.idempotency_key)
        except ValueError:
            audit(audit_event, "rejected", reason="invalid_payload")
            return jsonify({"error": "invalid cancellation request"}), 400
        audit(audit_event, "processed", status=case.status)
        status_code = 200 if case.status == "completed" else 202
        return jsonify(_webhook_case(case)), status_code

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
                "relayEnabled": configured.relay_enabled,
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
        return process_payload(
            request.get_json(silent=True) or {}, audit_event="webhook_request"
        )

    @app.post("/api/v1/relay/cancellations/<service>")
    def relay_finalize(service: str):
        service = service.strip().lower()
        accepted, reason = relay_authorised(service)
        if not accepted:
            if reason == "disabled" or service not in {"membership", "pt"}:
                return jsonify({"error": "not found"}), 404
            if reason == "misconfigured":
                return jsonify({"error": "service unavailable"}), 503
            if reason == "rate_limited":
                return jsonify({"error": "request rejected"}), 429
            return jsonify({"error": "unauthorised"}), 401
        if request.mimetype != "application/json":
            audit("relay_request", "rejected", reason="invalid_content_type")
            return jsonify({"error": "content type must be application/json"}), 415
        body = request.get_data(cache=True, as_text=False)
        try:
            canonical_body, payload = canonical_relay_request(body, service)
        except RelayPayloadError:
            audit("relay_request", "rejected", reason="invalid_payload")
            return jsonify({"error": "invalid cancellation request"}), 400
        if not configured.webhook_signing_secret:
            audit("relay_request", "rejected", reason="signing_not_configured")
            return jsonify({"error": "service unavailable"}), 503
        timestamp = str(int(datetime.now(UTC).timestamp()))
        nonce = secrets.token_urlsafe(24)
        signature = calculate_signature(
            configured.webhook_signing_secret,
            timestamp,
            nonce,
            canonical_body,
        )
        signed, signed_reason = signed_webhook_authorised(
            canonical_body,
            timestamp=timestamp,
            nonce=nonce,
            signature=signature,
        )
        if not signed:
            audit("relay_request", "rejected", reason=signed_reason)
            return jsonify({"error": "service unavailable"}), 503
        return process_payload(payload, audit_event="relay_request")

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
