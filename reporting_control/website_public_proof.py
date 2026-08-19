"""Publish the latest aggregate Website V2 proof snapshot from Hub to WordPress."""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from datetime import UTC, datetime
from typing import Any

import requests


def build_payload(hub_snapshot: dict[str, Any]) -> dict[str, Any]:
    observed_at = str(hub_snapshot.get("observed_at") or "").strip()
    summary = (hub_snapshot.get("payload") or {}).get("summary") or {}
    proof = summary.get("publicMarketingStatistics")
    if not observed_at or not isinstance(proof, dict):
        raise ValueError("Hub snapshot has no public marketing statistics")
    if proof.get("schemaVersion") != "website-public-proof-v1":
        raise ValueError("Unsupported public proof schema")
    required = (
        "womenTrained",
        "trackedWorkouts",
        "strengthProgress",
        "strengthCohortWomen",
    )
    missing = [key for key in required if key not in proof]
    if missing:
        raise ValueError(
            "Hub public proof is incomplete: "
            + ", ".join(missing)
            + f"; status={proof.get('status')!r}"
            + f"; reason={proof.get('reason')!r}"
        )
    canonical = json.dumps(proof, sort_keys=True, separators=(",", ":"))
    return {
        "schemaVersion": "website-public-proof-delivery-v1",
        "snapshotId": hashlib.sha256(
            f"{observed_at}:{canonical}".encode()
        ).hexdigest(),
        "generatedAt": observed_at,
        "publishedAt": datetime.now(UTC).isoformat(),
        "publicMarketingStatistics": proof,
    }


def publish_latest(
    *,
    hub_url: str,
    hub_secret: str,
    wordpress_url: str,
    wordpress_secret: str,
    session: requests.Session | None = None,
    timestamp: int | None = None,
) -> dict[str, Any]:
    if not all((hub_url, hub_secret, wordpress_url, wordpress_secret)):
        raise ValueError("Hub and WordPress URLs and secrets are required")
    session = session or requests.Session()
    response = session.get(
        hub_url.rstrip("/") + "/api/v1/sources/trainerize_performance/latest",
        headers={"X-Hub-Secret": hub_secret},
        timeout=30,
    )
    response.raise_for_status()
    payload = build_payload(response.json())
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    sent_at = timestamp or int(time.time())
    signature = hmac.new(
        wordpress_secret.encode(),
        f"{sent_at}.{body}".encode(),
        hashlib.sha256,
    ).hexdigest()
    delivered = session.post(
        wordpress_url.rstrip("/") + "/wp-json/evolved/v1/public-proof",
        data=body.encode(),
        headers={
            "Content-Type": "application/json",
            "X-Evolved-Timestamp": str(sent_at),
            "X-Evolved-Signature": f"sha256={signature}",
        },
        timeout=30,
    )
    try:
        delivered.raise_for_status()
    except requests.HTTPError as exc:
        try:
            error_body = delivered.json()
        except ValueError:
            error_body = {}
        safe_error = {
            "status": delivered.status_code,
            "code": error_body.get("code"),
            "message": error_body.get("message"),
        }
        raise RuntimeError(
            "WordPress public-proof delivery rejected: "
            + json.dumps(safe_error, sort_keys=True)
        ) from exc
    try:
        result = delivered.json()
    except ValueError as exc:
        content = getattr(delivered, "content", b"") or b""
        headers = getattr(delivered, "headers", {}) or {}
        history = getattr(delivered, "history", []) or []
        safe_error = {
            "status": delivered.status_code,
            "contentType": headers.get("Content-Type"),
            "bytes": len(content),
            "sha256": hashlib.sha256(content).hexdigest(),
            "url": getattr(delivered, "url", None),
            "redirects": [
                {
                    "status": item.status_code,
                    "location": (getattr(item, "headers", {}) or {}).get(
                        "Location"
                    ),
                }
                for item in history
            ],
        }
        raise RuntimeError(
            "WordPress public-proof delivery returned non-JSON: "
            + json.dumps(safe_error, sort_keys=True)
        ) from exc
    if not isinstance(result, dict):
        raise RuntimeError("WordPress public-proof acknowledgement is invalid")
    return result
