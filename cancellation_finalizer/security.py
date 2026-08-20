from __future__ import annotations

import hashlib
import hmac
import json
import logging
import re
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Callable


SIGNATURE_RE = re.compile(r"^sha256=([0-9a-f]{64})$")
NONCE_RE = re.compile(r"^[A-Za-z0-9_-]{16,128}$")
security_logger = logging.getLogger("cancellation_finalizer.security")


def signed_message(timestamp: str, nonce: str, body: bytes) -> bytes:
    return timestamp.encode("ascii") + b"." + nonce.encode("ascii") + b"." + body


def calculate_signature(secret: str, timestamp: str, nonce: str, body: bytes) -> str:
    digest = hmac.new(
        secret.encode("utf-8"), signed_message(timestamp, nonce, body), hashlib.sha256
    ).hexdigest()
    return f"sha256={digest}"


@dataclass(frozen=True)
class SignatureResult:
    accepted: bool
    reason: str
    timestamp: datetime | None = None
    nonce: str = ""


def verify_signature(
    *,
    secret: str,
    timestamp: str,
    nonce: str,
    signature: str,
    body: bytes,
    now: datetime,
    tolerance_seconds: int,
) -> SignatureResult:
    if not secret:
        return SignatureResult(False, "signing_not_configured")
    if not timestamp.isdigit() or not NONCE_RE.fullmatch(nonce):
        return SignatureResult(False, "malformed_signature_metadata")
    signature_match = SIGNATURE_RE.fullmatch(signature)
    if not signature_match:
        return SignatureResult(False, "malformed_signature")
    supplied_at = datetime.fromtimestamp(int(timestamp), tz=UTC)
    if abs((now - supplied_at).total_seconds()) > tolerance_seconds:
        return SignatureResult(False, "stale_signature")
    expected = calculate_signature(secret, timestamp, nonce, body)
    if not hmac.compare_digest(signature, expected):
        return SignatureResult(False, "invalid_signature")
    return SignatureResult(True, "accepted", supplied_at, nonce)


class FixedWindowRateLimiter:
    def __init__(
        self,
        limit: int,
        *,
        window_seconds: int = 60,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.limit = max(1, limit)
        self.window_seconds = max(1, window_seconds)
        self.clock = clock
        self.events: dict[str, deque[float]] = defaultdict(deque)
        self.lock = threading.Lock()

    def allow(self, key: str) -> bool:
        current = self.clock()
        boundary = current - self.window_seconds
        with self.lock:
            events = self.events[key]
            while events and events[0] <= boundary:
                events.popleft()
            if len(events) >= self.limit:
                return False
            events.append(current)
            return True


def network_fingerprint(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]


def log_security_event(event: str, outcome: str, **details: str | int | bool) -> None:
    payload = {
        "event": event,
        "outcome": outcome,
        "recorded_at": datetime.now(UTC).isoformat(),
        **details,
    }
    security_logger.info(json.dumps(payload, sort_keys=True, separators=(",", ":")))
