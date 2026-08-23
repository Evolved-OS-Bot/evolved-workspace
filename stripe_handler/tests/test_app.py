import os
import unittest
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import patch

os.environ.setdefault("STRIPE_API_KEY", "sk_test_local_only")

from stripe_handler import app as app_module  # noqa: E402
from stripe_handler.tests.test_pt_entitlement_reconciliation import jody_payload  # noqa: E402


class StripeObject(dict):
    __getattr__ = dict.__getitem__


class AppIntegrationTests(unittest.TestCase):
    def setUp(self):
        app_module.app.config.update(TESTING=True)
        self.flag_patch = patch.object(
            app_module,
            "PT_HOLD_ENTITLEMENT_RECONCILIATION_ENABLED",
            True,
        )
        self.flag_patch.start()
        self.addCleanup(self.flag_patch.stop)
        self.client = app_module.app.test_client()

    @patch.object(app_module.stripe.Subscription, "modify")
    @patch.object(app_module.stripe.Subscription, "list")
    @patch.object(app_module.stripe.Customer, "list")
    def test_pt_pause_route_returns_proposal_without_stripe_calls(
        self, customer_list, subscription_list, subscription_modify
    ):
        response = self.client.post("/stripe/pause-hold", json=jody_payload())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "proposal_ready")
        customer_list.assert_not_called()
        subscription_list.assert_not_called()
        subscription_modify.assert_not_called()

    def test_proposal_endpoint_is_side_effect_free(self):
        response = self.client.post("/stripe/pt-hold/reconcile", json=jody_payload())
        body = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(body["mutations_performed"], [])
        self.assertEqual(body["work_item"]["conversation_id"], "ghl-conversation-jody")

    def test_dark_deployment_readback_exposes_disabled_gate(self):
        with patch.object(
            app_module,
            "PT_HOLD_ENTITLEMENT_RECONCILIATION_ENABLED",
            False,
        ):
            health = self.client.get("/health")
            reconcile = self.client.post(
                "/stripe/pt-hold/reconcile", json=jody_payload()
            )

        self.assertEqual(
            health.get_json()["pt_hold_entitlement_reconciliation"],
            "disabled",
        )
        self.assertEqual(reconcile.status_code, 404)

    @patch.object(app_module, "record_exception")
    @patch.object(app_module, "update_ghl_status")
    @patch.object(app_module, "create_admin_exception_task")
    def test_ambiguous_pt_evidence_creates_no_duplicate_work_item(
        self, create_task, status_write, record_exception
    ):
        payload = jody_payload()
        payload["appointments"] = []

        response = self.client.post("/stripe/pause-hold", json=payload)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "review_required")
        create_task.assert_not_called()
        status_write.assert_not_called()
        record_exception.assert_not_called()

    @patch.object(app_module.stripe.Customer, "list")
    def test_unknown_hold_type_fails_before_stripe(self, customer_list):
        with patch.object(app_module, "record_exception") as exception_write:
            response = self.client.post(
                "/stripe/pause-hold",
                json={
                    "contact_id": "ghl-member",
                    "email": "member@example.com",
                    "hold_start_date": "2026-09-09",
                    "hold_end_date": "2026-10-07",
                    "pre_return_date": "2026-09-30",
                    "hold_type": "Mystery",
                },
            )

        self.assertEqual(response.status_code, 422)
        customer_list.assert_not_called()
        exception_write.assert_called_once()

    @patch.object(app_module.stripe.Subscription, "modify")
    @patch.object(app_module.stripe.Subscription, "list")
    @patch.object(app_module.stripe.Customer, "list")
    def test_membership_hold_retains_date_based_stripe_path(
        self, customer_list, subscription_list, subscription_modify
    ):
        customer_list.return_value = SimpleNamespace(data=[SimpleNamespace(id="cus_member")])
        period_end = int(datetime(2026, 9, 9, tzinfo=timezone.utc).timestamp())
        subscription = StripeObject(
            id="sub_member",
            current_period_end=period_end,
            currency="aud",
            items={"data": [{"plan": {"interval": "week", "interval_count": 1, "amount": 9900}}]},
        )
        subscription_list.return_value = SimpleNamespace(data=[subscription])

        with patch.object(app_module, "update_ghl_status") as status_write:
            response = self.client.post(
                "/stripe/pause-hold",
                json={
                    "contact_id": "ghl-member",
                    "email": "member@example.com",
                    "contact_name": "Member Example",
                    "hold_type": "Membership",
                    "hold_start_date": "2026-09-09",
                    "hold_end_date": "2026-10-07",
                    "pre_return_date": "2026-09-30",
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "ok")
        customer_list.assert_called_once()
        subscription_list.assert_called_once()
        subscription_modify.assert_called_once()
        status_write.assert_called_once()


if __name__ == "__main__":
    unittest.main()
