from __future__ import annotations

import unittest
from datetime import UTC, datetime

from cancellation_finalizer.security import (
    FixedWindowRateLimiter,
    calculate_signature,
    verify_signature,
)


class SecurityTest(unittest.TestCase):
    def test_signature_binds_timestamp_nonce_and_exact_body(self):
        body = b'{"contact_id":"contact-1"}'
        timestamp = "1787280000"
        nonce = "nonce-secure-123456"
        signature = calculate_signature("secret", timestamp, nonce, body)

        accepted = verify_signature(
            secret="secret",
            timestamp=timestamp,
            nonce=nonce,
            signature=signature,
            body=body,
            now=datetime.fromtimestamp(int(timestamp), tz=UTC),
            tolerance_seconds=300,
        )
        changed = verify_signature(
            secret="secret",
            timestamp=timestamp,
            nonce=nonce,
            signature=signature,
            body=body + b" ",
            now=datetime.fromtimestamp(int(timestamp), tz=UTC),
            tolerance_seconds=300,
        )

        self.assertTrue(accepted.accepted)
        self.assertFalse(changed.accepted)

    def test_rate_limiter_recovers_after_window(self):
        current = [100.0]
        limiter = FixedWindowRateLimiter(
            2, window_seconds=60, clock=lambda: current[0]
        )

        self.assertTrue(limiter.allow("caller"))
        self.assertTrue(limiter.allow("caller"))
        self.assertFalse(limiter.allow("caller"))
        current[0] = 161.0
        self.assertTrue(limiter.allow("caller"))


if __name__ == "__main__":
    unittest.main()
