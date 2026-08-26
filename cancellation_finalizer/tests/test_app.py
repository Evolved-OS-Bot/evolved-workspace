from __future__ import annotations

import json
import tempfile
import time
import unittest
from dataclasses import replace
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
            relay_enabled=True,
            relay_membership_secret="membership-relay-secret-0123456789abcdef",
            relay_pt_secret="pt-relay-secret-0123456789abcdef012345",
            signature_tolerance_seconds=300,
            webhook_rate_limit_per_minute=30,
            relay_rate_limit_per_minute=10,
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
            hub_current_people_read_key="",
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

    def post_relay(
        self,
        service: str,
        payload: dict | bytes,
        *,
        token: str | None = None,
        content_type: str = "application/json",
    ):
        body = (
            payload
            if isinstance(payload, bytes)
            else json.dumps(payload, separators=(",", ":")).encode()
        )
        return self.client.post(
            f"/api/v1/relay/cancellations/{service}",
            data=body,
            headers={
                "Authorization": f"Bearer {token or self.settings.relay_membership_secret}",
                "Content-Type": content_type,
            },
        )

    def client_for(self, settings: Settings):
        database = Path(self.temp.name) / f"cases-{time.time_ns()}.db"
        configured = replace(settings, database_url=f"sqlite:///{database}")
        app = create_app(
            configured,
            repository=Repository(configured.database_url),
            integrations=FakeIntegrations(),
        )
        return app, app.test_client()

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
        self.assertTrue(accepted.get_json()["relayEnabled"])
        self.assertIn(
            "GHL_API_KEY", accepted.get_json()["missingLiveConfiguration"]
        )

    def test_relay_requires_service_specific_bearer_secret(self):
        payload = {
            "contact_id": "contact-1",
            "email": "member@example.com",
            "final_access_date": "2099-01-01",
        }
        missing = self.client.post(
            "/api/v1/relay/cancellations/membership", json=payload
        )
        wrong_service = self.post_relay(
            "pt", payload, token=self.settings.relay_membership_secret
        )
        accepted_pt = self.post_relay(
            "pt", payload, token=self.settings.relay_pt_secret
        )
        self.assertEqual(missing.status_code, 401)
        self.assertEqual(wrong_service.status_code, 401)
        self.assertEqual(accepted_pt.status_code, 202)

    def test_relay_inserts_route_service_and_processes_in_safe_mode(self):
        response = self.post_relay(
            "membership",
            {
                "contact_id": "contact-1",
                "email": "member@example.com",
                "final_access_date": "2099-01-01",
                "scope": "service_only",
            },
        )
        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.get_json()["current_step"], "boundary_wait")
        self.assertNotIn("contact_id", response.get_json())
        case = self.app.config["REPOSITORY"].get(
            response.get_json()["idempotency_key"]
        )
        self.assertEqual(case.cancellation_type, "membership")

    def test_relay_rejects_route_type_mismatch_unknown_and_duplicate_fields(self):
        common = {
            "contact_id": "contact-1",
            "email": "member@example.com",
            "final_access_date": "2099-01-01",
        }
        mismatch = self.post_relay(
            "membership", {**common, "cancellation_type": "PT"}
        )
        unknown = self.post_relay("membership", {**common, "admin": True})
        duplicate = self.post_relay(
            "membership",
            b'{"contact_id":"one","contact_id":"two","email":"member@example.com","final_access_date":"2099-01-01"}',
        )
        self.assertEqual(mismatch.status_code, 400)
        self.assertEqual(unknown.status_code, 400)
        self.assertEqual(duplicate.status_code, 400)

    def test_relay_rejects_non_json_and_unknown_service(self):
        non_json = self.post_relay(
            "membership", b"not-json", content_type="text/plain"
        )
        unknown = self.post_relay("online", {})
        self.assertEqual(non_json.status_code, 415)
        self.assertEqual(unknown.status_code, 404)

    def test_relay_rejects_oversized_payload_before_processing(self):
        response = self.post_relay(
            "membership",
            b'{"contact_id":"' + (b"x" * 33_000) + b'"}',
        )
        self.assertEqual(response.status_code, 413)
        self.assertEqual(response.get_json(), {"error": "request rejected"})

    def test_relay_retry_is_idempotent_when_requested_at_is_omitted(self):
        payload = {
            "contact_id": "contact-1",
            "email": "member@example.com",
            "final_access_date": "2099-01-01",
        }
        first = self.post_relay("membership", payload)
        second = self.post_relay("membership", payload)
        self.assertEqual(first.status_code, 202)
        self.assertEqual(second.status_code, 202)
        self.assertEqual(
            first.get_json()["idempotency_key"],
            second.get_json()["idempotency_key"],
        )

    def test_relay_retry_cannot_change_meaningful_payload(self):
        payload = {
            "contact_id": "contact-1",
            "email": "member@example.com",
            "final_access_date": "2099-01-01",
        }
        first = self.post_relay("membership", payload)
        changed = self.post_relay(
            "membership", {**payload, "email": "different@example.com"}
        )
        self.assertEqual(first.status_code, 202)
        self.assertEqual(changed.status_code, 400)
        self.assertEqual(
            changed.get_json(), {"error": "invalid cancellation request"}
        )

    def test_disabled_relay_is_not_exposed(self):
        _app, client = self.client_for(replace(self.settings, relay_enabled=False))
        response = client.post(
            "/api/v1/relay/cancellations/membership",
            json={},
            headers={
                "Authorization": f"Bearer {self.settings.relay_membership_secret}"
            },
        )
        self.assertEqual(response.status_code, 404)

    def test_relay_fails_closed_when_signing_secret_is_missing(self):
        _app, client = self.client_for(
            replace(self.settings, webhook_signing_secret="")
        )
        response = client.post(
            "/api/v1/relay/cancellations/membership",
            json={
                "contact_id": "contact-1",
                "email": "member@example.com",
                "final_access_date": "2099-01-01",
            },
            headers={
                "Authorization": f"Bearer {self.settings.relay_membership_secret}"
            },
        )
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.get_json(), {"error": "service unavailable"})

    def test_relay_has_a_separate_rate_limit(self):
        _app, client = self.client_for(
            replace(self.settings, relay_rate_limit_per_minute=1)
        )
        headers = {
            "Authorization": f"Bearer {self.settings.relay_membership_secret}",
            "Content-Type": "application/json",
        }
        first = client.post(
            "/api/v1/relay/cancellations/membership", data=b"{}", headers=headers
        )
        second = client.post(
            "/api/v1/relay/cancellations/membership", data=b"{}", headers=headers
        )
        self.assertEqual(first.status_code, 400)
        self.assertEqual(second.status_code, 429)

    def test_relay_fails_closed_on_short_or_reused_secrets(self):
        _app, client = self.client_for(
            replace(
                self.settings,
                relay_membership_secret="short",
                relay_pt_secret="short",
            )
        )
        response = client.post(
            "/api/v1/relay/cancellations/membership",
            json={},
            headers={"Authorization": "Bearer short"},
        )
        self.assertEqual(response.status_code, 503)
        readiness = client.get(
            "/api/v1/admin/readiness",
            headers={"X-Cancellation-Admin-Secret": "admin-secret"},
        )
        missing = readiness.get_json()["missingLiveConfiguration"]
        self.assertIn("CANCELLATION_RELAY_MEMBERSHIP_SECRET", missing)
        self.assertIn("CANCELLATION_RELAY_PT_SECRET", missing)
        self.assertIn("CANCELLATION_RELAY_SERVICE_SECRETS_DISTINCT", missing)


if __name__ == "__main__":
    unittest.main()
