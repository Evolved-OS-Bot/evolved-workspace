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

    @patch.object(app_module.stripe.Customer, "list")
    def test_unknown_hold_type_fails_before_stripe(self, customer_list):
        response = self.client.post(
            "/stripe/pause-hold",
            json={
                "email": "member@example.com",
                "hold_start_date": "2026-09-09",
                "hold_end_date": "2026-10-07",
                "hold_type": "",
            },
        )

        self.assertEqual(response.status_code, 400)
        customer_list.assert_not_called()

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

        response = self.client.post(
            "/stripe/pause-hold",
            json={
                "email": "member@example.com",
                "contact_name": "Member Example",
                "hold_type": "Membership",
                "hold_start_date": "2026-09-09",
                "hold_end_date": "2026-10-07",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "ok")
        customer_list.assert_called_once()
        subscription_list.assert_called_once()
        subscription_modify.assert_called_once()


if __name__ == "__main__":
    unittest.main()
