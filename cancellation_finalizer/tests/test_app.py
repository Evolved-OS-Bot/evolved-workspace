from __future__ import annotations

import json
import tempfile
import time
import unittest
from pathlib import Path

from cancellation_finalizer.app import create_app
from cancellation_finalizer.config import Settings
from cancellation_finalizer.repository import Repository
from cancellation_finalizer.security import calculate_signature

from .test_engine import FakeIntegrations


class AppTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        database = Path(self.temp.name) / "cases.db"
        self.settings = Settings(
            database_url=f"sqlite:///{database}",
            webhook_signing_secret="webhook-secret",
            admin_secret="admin-secret",
            signature_tolerance_seconds=300,
            webhook_rate_limit_per_minute=30,
            admin_rate_limit_per_minute=60,
            write_enabled=False,
            ghl_api_key="",
            ghl_location_id="",
            ghl_admin_eve_user_id="",
            stripe_api_key="",
            google_spreadsheet_id="",
            google_service_account_json="",
            trainerize_group_id="",
            trainerize_api_token="",
            trainerize_api_base_url="https://api.trainerize.com/v03",
            trainerize_location_id=None,
            hub_base_url="",
            hub_api_key="",
            worker_enabled=False,
        )
        repo = Repository(self.settings.database_url)
        self.app = create_app(
            self.settings, repository=repo, integrations=FakeIntegrations()
        )
        self.client = self.app.test_client()

    def tearDown(self):
        self.temp.cleanup()

    def signed_headers(
        self,
        body: bytes,
        *,
        nonce: str = "nonce-1234567890",
        timestamp: str | None = None,
    ) -> dict[str, str]:
        timestamp = timestamp or str(int(time.time()))
        return {
            "Content-Type": "application/json",
            "X-Cancellation-Timestamp": timestamp,
            "X-Cancellation-Nonce": nonce,
            "X-Cancellation-Signature": calculate_signature(
                self.settings.webhook_signing_secret, timestamp, nonce, body
            ),
        }

    def post_signed(self, payload: dict, **header_options):
        body = json.dumps(payload, separators=(",", ":")).encode()
        return self.client.post(
            "/api/v1/cancellations/finalize",
            data=body,
            headers=self.signed_headers(body, **header_options),
        )

    def test_requires_valid_signature(self):
        response = self.client.post("/api/v1/cancellations/finalize", json={})
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json(), {"error": "request rejected"})

    def test_rejects_stale_signature(self):
        response = self.post_signed(
            {},
            nonce="nonce-stale-123456",
            timestamp=str(int(time.time()) - 301),
        )
        self.assertEqual(response.status_code, 401)

    def test_rejects_replayed_nonce(self):
        payload = {
            "contact_id": "contact-1",
            "email": "member@example.com",
            "cancellation_type": "PT",
            "final_access_date": "2099-01-01",
        }
        first = self.post_signed(payload, nonce="nonce-replay-12345")
        second = self.post_signed(payload, nonce="nonce-replay-12345")
        self.assertEqual(first.status_code, 202)
        self.assertEqual(second.status_code, 409)

    def test_validates_required_payload_after_signature(self):
        response = self.post_signed(
            {"contact_id": "contact-1"}, nonce="nonce-invalid-12345"
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.get_json(), {"error": "invalid cancellation request"}
        )

    def test_final_task_id_is_optional_for_date_triggered_workflow(self):
        response = self.post_signed(
            {
                "contact_id": "contact-1",
                "email": "member@example.com",
                "cancellation_type": "PT",
                "final_access_date": "2099-01-01",
            },
            nonce="nonce-optional-123456",
        )
        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.get_json()["current_step"], "boundary_wait")
        self.assertNotIn("contact_id", response.get_json())

    def test_health_is_minimal_and_sets_security_headers(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"status": "ok"})
        self.assertEqual(response.headers["Cache-Control"], "no-store")
        self.assertEqual(response.headers["X-Content-Type-Options"], "nosniff")
        self.assertIn("max-age=31536000", response.headers["Strict-Transport-Security"])
        self.assertIn("camera=()", response.headers["Permissions-Policy"])
        self.assertTrue(response.headers["X-Request-Id"])

    def test_readiness_requires_separate_admin_secret(self):
        denied = self.client.get(
            "/api/v1/admin/readiness",
            headers={"X-Cancellation-Admin-Secret": "webhook-secret"},
        )
        accepted = self.client.get(
            "/api/v1/admin/readiness",
            headers={"X-Cancellation-Admin-Secret": "admin-secret"},
        )
        self.assertEqual(denied.status_code, 401)
        self.assertEqual(accepted.status_code, 200)
        self.assertFalse(accepted.get_json()["writeEnabled"])
        self.assertIn(
            "GHL_API_KEY", accepted.get_json()["missingLiveConfiguration"]
        )


if __name__ == "__main__":
    unittest.main()
