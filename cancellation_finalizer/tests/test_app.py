from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from cancellation_finalizer.app import create_app
from cancellation_finalizer.config import Settings
from cancellation_finalizer.repository import Repository

from .test_engine import FakeIntegrations


class AppTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        database = Path(self.temp.name) / "cases.db"
        self.settings = Settings(
            database_url=f"sqlite:///{database}",
            api_secret="test-secret",
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
            trainerize_deactivate_webhook_url="",
            trainerize_deactivate_webhook_secret="",
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

    def test_requires_secret(self):
        response = self.client.post("/api/v1/cancellations/finalize", json={})
        self.assertEqual(response.status_code, 401)

    def test_validates_required_payload(self):
        response = self.client.post(
            "/api/v1/cancellations/finalize",
            headers={"X-Cancellation-Secret": "test-secret"},
            json={"contact_id": "contact-1"},
        )
        self.assertEqual(response.status_code, 400)

    def test_final_task_id_is_optional_for_date_triggered_workflow(self):
        response = self.client.post(
            "/api/v1/cancellations/finalize",
            headers={"X-Cancellation-Secret": "test-secret"},
            json={
                "contact_id": "contact-1",
                "email": "member@example.com",
                "cancellation_type": "PT",
                "final_access_date": "2099-01-01",
            },
        )
        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.get_json()["current_step"], "boundary_wait")

    def test_health_reports_fail_closed_configuration(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertFalse(payload["writeEnabled"])
        self.assertIn("GHL_API_KEY", payload["missingLiveConfiguration"])


if __name__ == "__main__":
    unittest.main()
