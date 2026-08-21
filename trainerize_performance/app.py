from __future__ import annotations

import hmac
import os
import threading

from flask import Flask, jsonify, request

from .bundle import REQUIRED_FILES, install_bundle
from .config import Settings
from .service import PerformanceService


settings = Settings.from_env()
service = PerformanceService(settings)
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024


def authorised() -> bool:
    supplied = (
        request.headers.get("X-Webhook-Secret")
        or request.headers.get("Authorization", "")
        .removeprefix("Bearer ")
        .strip()
    )
    return bool(supplied) and hmac.compare_digest(
        supplied,
        settings.webhook_secret,
    )


def background_run() -> None:
    try:
        service.run()
    except Exception:
        app.logger.exception("Trainerize performance run failed")


def background_refresh() -> None:
    try:
        service.refresh_and_run()
    except Exception:
        app.logger.exception("Trainerize source refresh failed")


@app.get("/health")
def health():
    latest = service.latest()
    latest_refresh = service.latest_refresh()
    return jsonify(
        {
            "status": "ok" if service.sources_ready() else "waiting_for_sources",
            "mode": "read_only_shadow",
            "schedulerEnabled": False,
            "sourcesReady": service.sources_ready(),
            "latestRun": {
                "status": latest.get("status"),
                "completedAt": latest.get("completedAt"),
            },
            "latestRefresh": {
                "status": latest_refresh.get("status"),
                "completedAt": latest_refresh.get("completedAt"),
            },
        }
    )


@app.post("/run")
def run():
    if not authorised():
        return jsonify({"error": "unauthorised"}), 401
    if not service.sources_ready():
        return jsonify({"error": "source bundle is not installed"}), 409
    thread = threading.Thread(
        target=background_run,
        daemon=True,
        name="trainerize-performance-run",
    )
    thread.start()
    return jsonify({"status": "started", "mode": "read_only_shadow"}), 202


@app.post("/refresh")
def refresh():
    if not authorised():
        return jsonify({"error": "unauthorised"}), 401
    if not service.sources_ready():
        return jsonify({"error": "source bundle is not installed"}), 409
    thread = threading.Thread(
        target=background_refresh,
        daemon=True,
        name="trainerize-performance-refresh",
    )
    thread.start()
    return jsonify(
        {
            "status": "started",
            "mode": "read_only_shadow",
            "lookbackDays": settings.refresh_lookback_days,
        }
    ), 202


@app.get("/runs/latest")
def latest():
    if not authorised():
        return jsonify({"error": "unauthorised"}), 401
    result = service.latest()
    return jsonify(result), (200 if result["status"] != "not_found" else 404)


@app.get("/refresh/latest")
def latest_refresh():
    if not authorised():
        return jsonify({"error": "unauthorised"}), 401
    result = service.latest_refresh()
    return jsonify(result), (200 if result["status"] != "not_found" else 404)


@app.post("/admin/bundle")
def upload_bundle():
    if not authorised():
        return jsonify({"error": "unauthorised"}), 401
    manifest = request.files.get("manifest.json")
    files = {
        name: request.files[name].stream
        for name in REQUIRED_FILES
        if name in request.files
    }
    if manifest is None:
        return jsonify({"error": "manifest.json is required"}), 400
    try:
        result = install_bundle(
            settings.data_dir,
            manifest.stream,
            files,
        )
        return jsonify(result)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8080")))
