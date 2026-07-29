import importlib
import os
import sys
import unittest
from datetime import date, datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock, patch


os.environ.setdefault("STRIPE_API_KEY", "sk_test_unit")
os.environ.setdefault("GHL_API_KEY", "ghl_test_unit")
os.environ.setdefault("GHL_LOCATION_ID", "location_test")

if "app" in sys.modules:
    billing = importlib.reload(sys.modules["app"])
else:
    billing = importlib.import_module("app")


def subscription():
    period_start = int(
        datetime(2026, 7, 27, tzinfo=timezone.utc).timestamp()
    )
    period_end = int(
        datetime(2026, 8, 3, tzinfo=timezone.utc).timestamp()
    )
    return {
        "id": "sub_test",
        "current_period_start": period_start,
        "current_period_end": period_end,
        "currency": "aud",
        "items": {
            "data": [
                {
                    "plan": {
                        "interval": "week",
                        "interval_count": 1,
                        "amount": 9900,
                    }
                }
            ]
        },
    }


class BillingOSTest(unittest.TestCase):
    def setUp(self):
        self.client = billing.app.test_client()
        billing._ghl_field_ids.clear()

    def test_cancellation_boundary_uses_brisbane_final_access_day(self):
        sub = subscription()
        sub["current_period_start"] = int(
            datetime(2026, 7, 22, 14, tzinfo=timezone.utc).timestamp()
        )
        sub["current_period_end"] = int(
            datetime(2026, 7, 29, 14, tzinfo=timezone.utc).timestamp()
        )

        cancel_at, last_payment = billing.calculate_cancellation_boundary(
            sub, date(2026, 7, 29)
        )

        self.assertEqual(
            datetime.fromtimestamp(cancel_at, billing.BRISBANE_TZ).isoformat(),
            "2026-07-30T00:00:00+10:00",
        )
        self.assertEqual(
            datetime.fromtimestamp(
                last_payment, billing.BRISBANE_TZ
            ).isoformat(),
            "2026-07-23T00:00:00+10:00",
        )

    def test_cancellation_boundary_advances_by_exact_weekly_periods(self):
        sub = subscription()
        sub["current_period_end"] = int(
            datetime(2026, 8, 3, 0, tzinfo=timezone.utc).timestamp()
        )

        cancel_at, _ = billing.calculate_cancellation_boundary(
            sub, date(2026, 8, 28)
        )

        self.assertEqual(
            datetime.fromtimestamp(cancel_at, timezone.utc).isoformat(),
            "2026-08-31T00:00:00+00:00",
        )

    def test_cancellation_boundary_rejects_approximate_months(self):
        sub = subscription()
        sub["items"]["data"][0]["plan"]["interval"] = "month"

        with self.assertRaisesRegex(ValueError, "manual review"):
            billing.calculate_cancellation_boundary(sub, date(2026, 8, 28))

    @patch.object(billing, "record_exception")
    def test_hold_requires_contact_id_and_all_dates(self, record_exception):
        response = self.client.post(
            "/stripe/pause-hold",
            json={
                "email": "member@example.com",
                "hold_start_date": "2026-08-10",
                "hold_end_date": "2026-08-31",
                "pre_return_date": "2026-08-24",
            },
        )
        self.assertEqual(response.status_code, 400)
        record_exception.assert_called_once()

    @patch.object(billing, "record_exception")
    def test_hold_rejects_end_before_start(self, record_exception):
        response = self.client.post(
            "/stripe/pause-hold",
            json={
                "contact_id": "contact_1",
                "email": "member@example.com",
                "hold_start_date": "2026-08-31",
                "hold_end_date": "2026-08-10",
                "pre_return_date": "2026-08-03",
            },
        )
        self.assertEqual(response.status_code, 422)
        self.assertIn("after Hold Start", response.get_json()["error"])
        record_exception.assert_called_once()

    @patch.object(billing, "record_exception")
    def test_hold_rejects_inconsistent_pre_return(self, record_exception):
        response = self.client.post(
            "/stripe/pause-hold",
            json={
                "contact_id": "contact_1",
                "email": "member@example.com",
                "hold_start_date": "2026-08-10",
                "hold_end_date": "2026-08-31",
                "pre_return_date": "2026-08-22",
            },
        )
        self.assertEqual(response.status_code, 422)
        self.assertIn("minus 7 days", response.get_json()["error"])
        record_exception.assert_called_once()

    @patch.object(billing, "update_ghl_status")
    @patch.object(billing.stripe.Subscription, "modify")
    @patch.object(billing.stripe.Subscription, "list")
    @patch.object(billing.stripe.Customer, "list")
    def test_hold_success_writes_acknowledgement(
        self, customer_list, subscription_list, modify, update_status
    ):
        customer_list.return_value = SimpleNamespace(
            data=[SimpleNamespace(id="cus_test")]
        )
        sub = subscription()
        sub["current_period_end"] = int(
            datetime(2026, 8, 10, tzinfo=timezone.utc).timestamp()
        )
        subscription_list.return_value = SimpleNamespace(data=[sub])

        response = self.client.post(
            "/stripe/pause-hold",
            json={
                "contact_id": "contact_1",
                "email": "member@example.com",
                "hold_start_date": "2026-08-10",
                "hold_end_date": "2026-08-31",
                "pre_return_date": "2026-08-24",
                "contact_name": "Test Member",
                "hold_type": "Membership",
            },
        )

        self.assertEqual(response.status_code, 200)
        modify.assert_called_once()
        self.assertIn("idempotency_key", modify.call_args.kwargs)
        update_status.assert_called_once()
        self.assertEqual(update_status.call_args.args[:3], ("contact_1", "hold", "Succeeded"))

    @patch.object(billing, "record_exception")
    @patch.object(billing.stripe.Customer, "list")
    def test_cancellation_no_customer_is_exception(
        self, customer_list, record_exception
    ):
        customer_list.return_value = SimpleNamespace(data=[])
        response = self.client.post(
            "/stripe/cancel",
            json={
                "contact_id": "contact_1",
                "email": "member@example.com",
                "notice_end_date": "2026-08-28",
                "cancellation_type": "Membership",
            },
        )
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.get_json()["status"], "exception")
        record_exception.assert_called_once()

    @patch.object(billing, "record_exception")
    @patch.object(billing.stripe.Subscription, "list")
    @patch.object(billing.stripe.Customer, "list")
    def test_cancellation_multiple_subscriptions_fails_closed(
        self, customer_list, subscription_list, record_exception
    ):
        customer_list.return_value = SimpleNamespace(
            data=[SimpleNamespace(id="cus_test")]
        )
        subscription_list.return_value = SimpleNamespace(
            data=[subscription(), subscription()]
        )
        response = self.client.post(
            "/stripe/cancel",
            json={
                "contact_id": "contact_1",
                "email": "member@example.com",
                "notice_end_date": "2026-08-28",
                "cancellation_type": "PT",
            },
        )
        self.assertEqual(response.status_code, 422)
        self.assertIn("Multiple active", response.get_json()["error"])
        record_exception.assert_called_once()

    @patch.object(billing, "update_ghl_status")
    @patch.object(billing.stripe.Subscription, "modify")
    @patch.object(billing.stripe.Subscription, "list")
    @patch.object(billing.stripe.Customer, "list")
    def test_cancellation_success_is_idempotent_and_acknowledged(
        self, customer_list, subscription_list, modify, update_status
    ):
        customer_list.return_value = SimpleNamespace(
            data=[SimpleNamespace(id="cus_test")]
        )
        subscription_list.return_value = SimpleNamespace(data=[subscription()])

        response = self.client.post(
            "/stripe/cancel",
            json={
                "contact_id": "contact_1",
                "email": "member@example.com",
                "notice_end_date": "2026-08-28",
                "contact_name": "Test Member",
                "cancellation_type": "PT",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("idempotency_key", modify.call_args.kwargs)
        update_status.assert_called_once()
        self.assertEqual(
            update_status.call_args.args[:3],
            ("contact_1", "cancellation", "Succeeded"),
        )

    @patch.object(billing, "snapshot_hold_request")
    @patch.object(billing, "get_ghl_contact_fields")
    def test_hold_intake_accepts_and_snapshots_first_request(
        self, get_fields, snapshot
    ):
        get_fields.return_value = {
            "hold_lifecycle_status": "Completed",
            "hold_start": int(
                (
                    datetime.now(billing.BRISBANE_TZ)
                    + billing.timedelta(days=14)
                ).timestamp()
                * 1000
            ),
            "hold_reason": "Holidays",
            "hold_weeks": "3",
        }
        response = self.client.post(
            "/ghl/hold-intake",
            json={
                "contact_id": "contact_1",
                "form_kind": "standard_membership",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "accepted")
        snapshot.assert_called_once()

    @patch.object(billing, "restore_protected_hold")
    @patch.object(billing, "get_ghl_contact_fields")
    def test_hold_intake_restores_original_when_hold_is_open(
        self, get_fields, restore
    ):
        get_fields.return_value = {
            "hold_lifecycle_status": "Pending Hold",
            "request_hold_start": 1786320000000,
            "request_hold_weeks": "3",
            "request_extended_hold_weeks": "",
        }
        response = self.client.post(
            "/ghl/hold-intake",
            json={
                "contact_id": "contact_1",
                "form_kind": "standard_membership",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json()["status"], "rejected_existing_hold"
        )
        restore.assert_called_once()

    @patch.object(billing, "update_ghl_fields")
    @patch.object(billing, "get_ghl_contact_fields")
    def test_hold_intake_rejects_open_hold_without_snapshot(
        self, get_fields, update_fields
    ):
        get_fields.return_value = {
            "hold_lifecycle_status": "On Hold",
            "request_hold_start": "",
            "request_hold_weeks": "",
            "request_extended_hold_weeks": "",
        }
        response = self.client.post(
            "/ghl/hold-intake",
            json={
                "contact_id": "contact_1",
                "form_kind": "standard_pt",
            },
        )
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.get_json()["status"], "exception")
        update_fields.assert_called_once()


if __name__ == "__main__":
    unittest.main()
