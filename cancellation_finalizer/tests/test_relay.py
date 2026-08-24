from __future__ import annotations

import unittest

from cancellation_finalizer.relay import RelayPayloadError, canonical_relay_request


class RelayTest(unittest.TestCase):
    def test_canonical_body_is_stable_and_binds_route_service(self):
        first, payload = canonical_relay_request(
            b'{"email":"member@example.com","contact_id":"contact-1","final_access_date":"2099-01-01"}',
            "membership",
        )
        second, _ = canonical_relay_request(
            b'{"final_access_date":"2099-01-01","contact_id":"contact-1","email":"member@example.com"}',
            "membership",
        )
        self.assertEqual(first, second)
        self.assertEqual(payload["cancellation_type"], "membership")
        self.assertIn(b'"cancellation_type":"membership"', first)

    def test_rejects_invalid_utf8_and_non_object_json(self):
        with self.assertRaises(RelayPayloadError):
            canonical_relay_request(b"\xff", "membership")
        with self.assertRaises(RelayPayloadError):
            canonical_relay_request(b"[]", "membership")
        with self.assertRaises(RelayPayloadError):
            canonical_relay_request(b'{"scope":NaN}', "membership")


if __name__ == "__main__":
    unittest.main()
