from __future__ import annotations

import json
from typing import Any


ALLOWED_SERVICES = {"membership", "pt"}
ALLOWED_FIELDS = {
    "contact_id",
    "email",
    "final_access_date",
    "scope",
    "final_task_id",
    "requested_at",
    "cancellation_type",
}


class RelayPayloadError(ValueError):
    """A relay request that cannot be forwarded to the signed boundary."""


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise RelayPayloadError("duplicate JSON field")
        result[key] = value
    return result


def _reject_nonstandard_number(_value: str) -> None:
    raise RelayPayloadError("non-standard JSON number")


def canonical_relay_request(body: bytes, service: str) -> tuple[bytes, dict[str, Any]]:
    normalized_service = service.strip().lower()
    if normalized_service not in ALLOWED_SERVICES:
        raise RelayPayloadError("unsupported cancellation service")
    try:
        decoded = body.decode("utf-8", errors="strict")
        payload = json.loads(
            decoded,
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_nonstandard_number,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RelayPayloadError("invalid JSON payload") from exc
    if not isinstance(payload, dict):
        raise RelayPayloadError("JSON payload must be an object")
    unknown = set(payload) - ALLOWED_FIELDS
    if unknown:
        raise RelayPayloadError("unexpected JSON field")
    supplied_type = str(payload.get("cancellation_type") or "").strip().lower()
    if supplied_type and supplied_type != normalized_service:
        raise RelayPayloadError("cancellation type does not match relay route")
    payload["cancellation_type"] = normalized_service
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return canonical, payload
