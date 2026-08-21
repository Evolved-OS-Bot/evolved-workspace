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
os.environ.setdefault("GHL_ADMIN_EVE_USER_ID", "admin_eve_test")

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
        "status": "active",
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
        self.offer_patch = patch.dict(
            os.environ,
            {
                "SERVICE_CHANGE_OFFERS_JSON": (
                    '{"evolved_anywhere":{'
                    '"price_id":"price_evolved-anywhere",'
                    '"weekly_price_cents":6900,'
                    '"service_name":"Evolved Anywhere",'
                    '"service_type":"hybrid"},'
                    '"online_only":{'
                    '"price_id":"price_online-only",'
                    '"weekly_price_cents":2700,'
                    '"service_name":"Online Only",'
                    '"service_type":"online"},'
                    '"strong_12_month_commitment":{'
                    '"price_id":"price_strong-89",'
                    '"weekly_price_cents":8900,'
                    '"service_name":"Strong, Fit & Flexible Membership",'
                    '"service_type":"sgpt",'
                    '"offer_version":"strong-12-month-commitment-v1",'
                    '"agreement_version":"strong-12-month-commitment-variation-v1",'
                    '"original_price_id":"price_strong-99",'
                    '"original_weekly_price_cents":9900,'
                    '"weekly_discount_cents":1000,'
                    '"maximum_clawback_cents":52000,'
                    '"term_months":12}}'
                )
            },
        )
        self.offer_patch.start()

    def tearDown(self):
        self.offer_patch.stop()

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

    @patch.object(billing.requests, "post")
    @patch.object(billing.requests, "get")
    def test_exception_task_is_assigned_to_admin_eve_and_due_same_day(
        self, request_get, request_post
    ):
        request_get.return_value = MagicMock(
            ok=True,
            json=lambda: {"tasks": []},
        )
        request_post.return_value = MagicMock(status_code=201)

        created = billing.create_admin_exception_task(
            "contact_1",
            "hold",
            "Stripe customer not found",
            contact_name="Test Member",
            requested_action="Membership hold from 2026-08-10 to 2026-08-31",
        )

        self.assertTrue(created)
        payload = request_post.call_args.kwargs["json"]
        self.assertEqual(payload["assignedTo"], "admin_eve_test")
        self.assertEqual(
            payload["title"],
            "BILLING EXCEPTION: Hold - Manual action required",
        )
        self.assertIn("Test Member", payload["body"])
        self.assertIn("Stripe customer not found", payload["body"])
        due_date = datetime.fromisoformat(
            payload["dueDate"].replace("Z", "+00:00")
        ).astimezone(billing.BRISBANE_TZ)
        self.assertEqual(due_date.date(), datetime.now(billing.BRISBANE_TZ).date())

    @patch.object(billing.requests, "post")
    @patch.object(billing.requests, "get")
    def test_service_change_exception_task_uses_staff_readable_title(
        self, request_get, request_post
    ):
        request_get.return_value = MagicMock(
            ok=True,
            json=lambda: {"tasks": []},
        )
        request_post.return_value = MagicMock(status_code=201)

        created = billing.create_admin_exception_task(
            "contact_1",
            "service_change",
            "Trainerize provisioning failed",
        )

        self.assertTrue(created)
        payload = request_post.call_args.kwargs["json"]
        self.assertEqual(
            payload["title"],
            "BILLING EXCEPTION: Service Change - Manual action required",
        )

    @patch.object(billing.requests, "post")
    @patch.object(billing.requests, "get")
    def test_exception_task_deduplicates_an_existing_open_task(
        self, request_get, request_post
    ):
        key = billing.billing_exception_key(
            "contact_1", "cancellation", "Stripe customer not found"
        )
        request_get.return_value = MagicMock(
            ok=True,
            json=lambda: {
                "tasks": [
                    {
                        "body": f"Billing OS exception key: {key}",
                        "completed": False,
                    }
                ]
            },
        )

        created = billing.create_admin_exception_task(
            "contact_1",
            "cancellation",
            "Stripe customer not found",
        )

        self.assertTrue(created)
        request_post.assert_not_called()

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

    @patch.object(billing, "stop_failed_cancellation")
    @patch.object(billing, "record_exception")
    @patch.object(billing.stripe.Customer, "list")
    def test_cancellation_no_customer_is_exception(
        self, customer_list, record_exception, stop_workflow
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
        stop_workflow.assert_called_once_with("contact_1", "Membership")
        self.assertTrue(response.get_json()["workflow_stopped"])

    @patch.object(billing, "stop_failed_cancellation")
    @patch.object(billing, "record_exception")
    @patch.object(billing.stripe.Subscription, "list")
    @patch.object(billing.stripe.Customer, "list")
    def test_cancellation_multiple_subscriptions_fails_closed(
        self,
        customer_list,
        subscription_list,
        record_exception,
        stop_workflow,
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
        stop_workflow.assert_called_once_with("contact_1", "PT")

    @patch.object(billing.requests, "get")
    def test_cancellation_resolves_contact_by_exact_email(self, request_get):
        request_get.return_value = MagicMock(
            ok=True,
            json=lambda: {
                "contacts": [
                    {
                        "id": "contact_1",
                        "email": "member@example.com",
                    }
                ]
            },
        )

        contact_id = billing.resolve_contact_id(
            {}, "member@example.com"
        )

        self.assertEqual(contact_id, "contact_1")

    @patch.object(billing.requests, "delete")
    def test_failed_pt_cancellation_removes_contact_from_pt_workflow(
        self, request_delete
    ):
        request_delete.return_value = MagicMock(ok=True)

        billing.stop_failed_cancellation(
            "contact_1", "Personal Training"
        )

        self.assertIn(
            billing.CANCELLATION_WORKFLOW_IDS["pt"],
            request_delete.call_args.args[0],
        )

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
        self.assertEqual(
            modify.call_args.kwargs["idempotency_key"],
            billing.stripe_idempotency_key(
                "cancel",
                "contact_1",
                billing.parse_date("2026-08-28"),
                "sub_test",
                modify.call_args.kwargs["cancel_at"],
            ),
        )
        update_status.assert_called_once()
        self.assertEqual(
            update_status.call_args.args[:3],
            ("contact_1", "cancellation", "Succeeded"),
        )

    @patch.object(billing, "update_ghl_status")
    @patch.object(billing.stripe.Subscription, "modify")
    @patch.object(billing.stripe.Subscription, "list")
    @patch.object(billing.stripe.Customer, "list")
    def test_existing_exact_cancellation_is_acknowledged_without_mutation(
        self, customer_list, subscription_list, modify, update_status
    ):
        customer_list.return_value = SimpleNamespace(
            data=[SimpleNamespace(id="cus_test")]
        )
        sub = subscription()
        cancel_at, _ = billing.calculate_cancellation_boundary(
            sub, billing.parse_date("2026-08-03")
        )
        sub["cancel_at"] = cancel_at
        sub["schedule"] = "sub_sched_test"
        subscription_list.return_value = SimpleNamespace(data=[sub])

        response = self.client.post(
            "/stripe/cancel",
            json={
                "contact_id": "contact_1",
                "email": "member@example.com",
                "notice_end_date": "2026-08-03",
                "contact_name": "Test Member",
                "cancellation_type": "Membership",
            },
        )

        self.assertEqual(response.status_code, 200)
        modify.assert_not_called()
        update_status.assert_called_once()
        self.assertEqual(
            update_status.call_args.args[:3],
            ("contact_1", "cancellation", "Succeeded"),
        )

    @patch.object(billing, "update_ghl_status")
    @patch.object(billing, "update_ghl_fields")
    @patch.object(billing, "_resolve_ghl_field_ids", return_value={
        "service_change_effective_date": "effective",
        "service_change_change_status": "change_status",
    })
    @patch.object(billing, "publish_service_change_event")
    @patch.object(billing.stripe.Price, "retrieve")
    @patch.object(billing.stripe.SubscriptionSchedule, "list")
    @patch.object(billing.stripe.Subscription, "list")
    @patch.object(billing.stripe.Customer, "list")
    def test_service_change_acknowledges_exact_future_schedule_without_mutation(
        self,
        customer_list,
        subscription_list,
        schedule_list,
        price_retrieve,
        publish_event,
        resolve_fields,
        update_fields,
        update_status,
    ):
        publish_event.return_value = {"status": "accepted"}
        customer_list.return_value = SimpleNamespace(
            data=[
                {
                    "id": "cus_test",
                    "email": "member@example.com",
                }
            ]
        )
        sub = subscription()
        boundary = billing.service_change_boundary(date(2026, 8, 5))
        sub["current_period_end"] = boundary
        sub["cancel_at"] = boundary
        subscription_list.return_value = SimpleNamespace(data=[sub])
        schedule_list.return_value = SimpleNamespace(
            data=[
                {
                    "id": "sub_sched_test",
                    "status": "not_started",
                    "phases": [
                        {
                            "start_date": boundary,
                            "items": [{"price": "price_evolved-anywhere"}],
                        }
                    ],
                }
            ]
        )
        price_retrieve.return_value = {
            "id": "price_evolved-anywhere",
            "unit_amount": 6900,
            "currency": "aud",
            "active": True,
            "recurring": {
                "interval": "week",
                "interval_count": 1,
            },
        }

        response = self.client.post(
            "/stripe/service-change",
            json={
                "contact_id": "contact_1",
                "request_id": "msc-1",
                "email": "member@example.com",
                "request_date": "2026-07-02",
                "effective_date": "2026-08-05",
                "target_service": "evolved_anywhere",
                "current_price_cents": 9900,
                "hub_event": {
                    "occurred_at": "2026-07-02T09:00:00+10:00",
                    "offer_version": "evolved-anywhere-v1",
                    "agreement_version": "service-change-v1",
                    "signed_at": "2026-07-02T09:00:00+10:00",
                    "signature_document": "ghl://submission/1",
                    "prior_services": [{
                        "service_type": "sgpt",
                        "service_name": "Strong, Fit & Flexible Membership",
                        "weekly_price_cents": 9900,
                    }],
                    "requested_services": [{
                        "service_type": "hybrid",
                        "service_name": "Evolved Anywhere",
                        "weekly_price_cents": 6900,
                    }],
                    "surface_statuses": {
                        "billing": "pending",
                        "ghl": "pending",
                        "trainerize": "pending",
                        "appointments": "pending",
                        "workbook": "pending",
                        "reporting": "pending",
                    },
                },
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "scheduled")
        self.assertEqual(
            update_status.call_args.args[:3],
            ("contact_1", "service_change", "Scheduled"),
        )
        publish_event.assert_called_once()
        self.assertEqual(
            publish_event.call_args.args[0]["effective_at"],
            "2026-08-05T00:00:00+10:00",
        )

    @patch.object(billing, "record_exception")
    @patch.object(billing.stripe.Price, "retrieve")
    @patch.object(billing.stripe.Subscription, "list")
    @patch.object(billing.stripe.Customer, "list")
    def test_service_change_fails_closed_when_current_boundary_is_wrong(
        self,
        customer_list,
        subscription_list,
        price_retrieve,
        record_exception,
    ):
        price_retrieve.return_value = {
            "id": "price_evolved-anywhere",
            "unit_amount": 6900,
            "currency": "aud",
            "active": True,
            "recurring": {"interval": "week", "interval_count": 1},
        }
        customer_list.return_value = SimpleNamespace(
            data=[
                {
                    "id": "cus_test",
                    "email": "member@example.com",
                }
            ]
        )
        subscription_list.return_value = SimpleNamespace(data=[subscription()])

        response = self.client.post(
            "/stripe/service-change",
            json={
                "contact_id": "contact_1",
                "request_id": "msc-1",
                "email": "member@example.com",
                "request_date": "2026-07-02",
                "effective_date": "2026-08-05",
                "target_service": "evolved_anywhere",
                "current_price_cents": 9900,
                "hub_event": {},
            },
        )

        self.assertEqual(response.status_code, 422)
        self.assertIn(
            "30-day weekly billing boundary",
            response.get_json()["error"],
        )
        record_exception.assert_called_once()

    @patch.object(billing, "record_exception")
    def test_service_change_requires_idempotency_identity_and_prices(
        self,
        record_exception,
    ):
        response = self.client.post(
            "/stripe/service-change",
            json={
                "contact_id": "contact_1",
                "email": "member@example.com",
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("request_id", response.get_json()["error"])
        record_exception.assert_called_once()

    def test_service_change_derives_stable_request_id_from_signed_submission(self):
        payload = {
            "contact_id": "contact_1",
            "target_service": "online_only",
            "request_date": "2026-08-02",
            "hub_event": {
                "signed_at": "2026-08-02T09:30:00+10:00",
                "signature_document": "ghl://survey/XBpTy848fvJXjMtGfnu2/submission/1",
            },
        }
        first = billing.service_change_request_id(payload)
        second = billing.service_change_request_id(payload)

        self.assertTrue(first.startswith("msc-"))
        self.assertEqual(first, second)

    def test_service_change_derives_id_and_event_from_minimal_ghl_handoff(self):
        payload = {
            "contact_id": "contact_1",
            "email": "member@example.com",
            "target_service": "online_only",
            "request_date": "08/02/2026",
            "source_form_id": "survey-online",
            "prior_service": "Strong, Fit & Flexible Membership",
        }
        request_id = billing.service_change_request_id(payload)
        payload["request_id"] = request_id
        preview = {
            "current_price_cents": 9900,
            "effective_date": "2026-09-02",
            "effective_at": "2026-09-02T00:00:00+10:00",
        }

        event = billing.requested_service_change_event(payload, preview)

        self.assertTrue(request_id.startswith("msc-"))
        self.assertEqual(event["request_date"], "2026-08-02")
        self.assertEqual(event["offer_version"], "online_only-v1")
        self.assertEqual(
            event["signature_document"],
            "ghl://survey/survey-online",
        )
        self.assertEqual(event["prior_services"][0]["service_type"], "sgpt")
        self.assertEqual(
            event["requested_services"][0]["weekly_price_cents"],
            2700,
        )

    @patch.object(billing.stripe.Subscription, "modify")
    @patch.object(billing.stripe.SubscriptionSchedule, "create")
    @patch.object(billing.stripe.SubscriptionSchedule, "list")
    @patch.object(billing.stripe.Subscription, "list")
    @patch.object(billing.stripe.Price, "retrieve")
    def test_service_change_can_resolve_one_current_subscription_amount(
        self,
        price_retrieve,
        subscription_list,
        schedule_list,
        schedule_create,
        subscription_modify,
    ):
        price_retrieve.return_value = {
            "id": "price_online-only",
            "unit_amount": 2700,
            "currency": "aud",
            "active": True,
            "recurring": {"interval": "week", "interval_count": 1},
        }
        current = subscription()
        current["current_period_end"] = billing.service_change_boundary(
            date(2026, 8, 5)
        )
        subscription_list.return_value = SimpleNamespace(data=[current])
        schedule_list.return_value = SimpleNamespace(data=[])
        schedule_create.return_value = {"id": "sub_sched_online"}

        result = billing.schedule_service_change_billing(
            "cus_test",
            contact_id="contact_1",
            request_id="msc-derived",
            request_date=date(2026, 7, 2),
            target_service="online_only",
        )

        self.assertEqual(result["current_price_cents"], 9900)
        self.assertEqual(result["target_price_cents"], 2700)
        subscription_modify.assert_called_once()

    @patch.object(billing.stripe.Subscription, "modify")
    @patch.object(billing.stripe.SubscriptionSchedule, "create")
    @patch.object(billing.stripe.SubscriptionSchedule, "list")
    @patch.object(billing.stripe.Subscription, "list")
    @patch.object(billing.stripe.Price, "retrieve")
    def test_service_change_schedules_both_sides_at_one_exact_boundary(
        self,
        price_retrieve,
        subscription_list,
        schedule_list,
        schedule_create,
        subscription_modify,
    ):
        price_retrieve.return_value = {
            "id": "price_evolved-anywhere",
            "unit_amount": 6900,
            "currency": "aud",
            "active": True,
            "recurring": {"interval": "week", "interval_count": 1},
        }
        sub = subscription()
        sub["current_period_end"] = billing.service_change_boundary(
            date(2026, 7, 29)
        )
        subscription_list.return_value = SimpleNamespace(data=[sub])
        schedule_list.return_value = SimpleNamespace(data=[])
        schedule_create.return_value = {"id": "sub_sched_new"}

        result = billing.schedule_service_change_billing(
            "cus_test",
            contact_id="contact_1",
            request_id="msc-1",
            request_date=date(2026, 7, 2),
            current_price_cents=9900,
            target_service="evolved_anywhere",
        )

        boundary = billing.service_change_boundary(date(2026, 8, 5))
        self.assertEqual(result["boundary_ts"], boundary)
        self.assertEqual(
            schedule_create.call_args.kwargs["start_date"],
            boundary,
        )
        self.assertEqual(
            subscription_modify.call_args.kwargs["cancel_at"],
            boundary,
        )
        self.assertTrue(
            schedule_create.call_args.kwargs["idempotency_key"].startswith(
                "billing-os-service-change-schedule-"
            )
        )

    @patch.object(billing.stripe.Subscription, "modify")
    @patch.object(billing.stripe.SubscriptionSchedule, "create")
    @patch.object(billing.stripe.SubscriptionSchedule, "list")
    @patch.object(billing.stripe.Subscription, "list")
    @patch.object(billing.stripe.Price, "retrieve")
    def test_service_change_exact_replay_makes_no_stripe_mutation(
        self,
        price_retrieve,
        subscription_list,
        schedule_list,
        schedule_create,
        subscription_modify,
    ):
        price_retrieve.return_value = {
            "id": "price_evolved-anywhere",
            "unit_amount": 6900,
            "currency": "aud",
            "active": True,
            "recurring": {"interval": "week", "interval_count": 1},
        }
        boundary = billing.service_change_boundary(date(2026, 8, 5))
        sub = subscription()
        sub["current_period_end"] = boundary
        sub["cancel_at"] = boundary
        subscription_list.return_value = SimpleNamespace(data=[sub])
        schedule_list.return_value = SimpleNamespace(
            data=[{
                "id": "sub_sched_existing",
                "status": "not_started",
                "metadata": {"service_change_request_id": "msc-1"},
                "phases": [{
                    "start_date": boundary,
                    "items": [{
                        "price": {
                            "id": "price_evolved-anywhere",
                            "unit_amount": 6900,
                            "recurring": {
                                "interval": "week",
                                "interval_count": 1,
                            },
                        }
                    }],
                }],
            }]
        )

        result = billing.schedule_service_change_billing(
            "cus_test",
            contact_id="contact_1",
            request_id="msc-1",
            request_date=date(2026, 7, 2),
            current_price_cents=9900,
            target_service="evolved_anywhere",
        )

        self.assertEqual(result["mutation"], "none")
        schedule_create.assert_not_called()
        subscription_modify.assert_not_called()

    @patch.object(billing.stripe.SubscriptionSchedule, "cancel")
    @patch.object(billing.stripe.Subscription, "modify")
    @patch.object(billing.stripe.SubscriptionSchedule, "create")
    @patch.object(billing.stripe.SubscriptionSchedule, "list")
    @patch.object(billing.stripe.Subscription, "list")
    @patch.object(billing.stripe.Price, "retrieve")
    def test_service_change_rolls_back_new_schedule_when_current_end_fails(
        self,
        price_retrieve,
        subscription_list,
        schedule_list,
        schedule_create,
        subscription_modify,
        schedule_cancel,
    ):
        price_retrieve.return_value = {
            "id": "price_evolved-anywhere",
            "unit_amount": 6900,
            "currency": "aud",
            "active": True,
            "recurring": {"interval": "week", "interval_count": 1},
        }
        sub = subscription()
        sub["current_period_end"] = billing.service_change_boundary(
            date(2026, 7, 29)
        )
        subscription_list.return_value = SimpleNamespace(data=[sub])
        schedule_list.return_value = SimpleNamespace(data=[])
        schedule_create.return_value = {"id": "sub_sched_new"}
        subscription_modify.side_effect = billing.stripe.error.InvalidRequestError(
            "failed",
            "cancel_at",
        )

        with self.assertRaises(billing.stripe.error.StripeError):
            billing.schedule_service_change_billing(
                "cus_test",
                contact_id="contact_1",
                request_id="msc-1",
                request_date=date(2026, 7, 2),
                current_price_cents=9900,
                target_service="evolved_anywhere",
            )

        schedule_cancel.assert_called_once_with("sub_sched_new")

    @patch.object(billing.stripe.Subscription, "modify")
    @patch.object(billing.stripe.SubscriptionSchedule, "create")
    @patch.object(billing.stripe.SubscriptionSchedule, "list")
    @patch.object(billing.stripe.Subscription, "list")
    @patch.object(billing.stripe.Price, "retrieve")
    def test_strong_commitment_schedules_discount_then_original_price(
        self,
        price_retrieve,
        subscription_list,
        schedule_list,
        schedule_create,
        subscription_modify,
    ):
        def price(price_id):
            amounts = {
                "price_strong-89": 8900,
                "price_strong-99": 9900,
            }
            return {
                "id": price_id,
                "unit_amount": amounts[price_id],
                "currency": "aud",
                "active": True,
                "recurring": {"interval": "week", "interval_count": 1},
            }

        price_retrieve.side_effect = price
        sub = subscription()
        sub["current_period_end"] = billing.service_change_boundary(
            date(2026, 8, 5)
        )
        subscription_list.return_value = SimpleNamespace(data=[sub])
        schedule_list.return_value = SimpleNamespace(data=[])
        schedule_create.return_value = {"id": "sub_sched_commitment"}

        result = billing.schedule_service_change_billing(
            "cus_test",
            contact_id="contact_1",
            request_id="msc-commitment-1",
            request_date=date(2026, 8, 3),
            current_price_cents=9900,
            target_service="strong_12_month_commitment",
        )

        phases = schedule_create.call_args.kwargs["phases"]
        self.assertEqual(phases[0]["items"][0]["price"], "price_strong-89")
        self.assertEqual(phases[1]["items"][0]["price"], "price_strong-99")
        self.assertEqual(result["effective_date"], "2026-08-05")
        self.assertEqual(result["commitment_end_date"], "2027-08-11")
        self.assertEqual(result["continuation_reminder_date"], "2027-06-11")
        self.assertEqual(
            subscription_modify.call_args.kwargs["cancel_at"],
            billing.service_change_boundary(date(2026, 8, 5)),
        )

    @patch.object(billing.stripe.SubscriptionSchedule, "modify")
    @patch.object(billing.stripe.SubscriptionSchedule, "list")
    @patch.object(billing.stripe.Subscription, "list")
    @patch.object(billing.stripe.Price, "retrieve")
    def test_strong_commitment_updates_one_not_started_schedule_in_place(
        self,
        price_retrieve,
        subscription_list,
        schedule_list,
        schedule_modify,
    ):
        def price(price_id):
            amounts = {
                "price_strong-89": 8900,
                "price_strong-99": 9900,
            }
            return {
                "id": price_id,
                "unit_amount": amounts[price_id],
                "currency": "aud",
                "active": True,
                "recurring": {"interval": "week", "interval_count": 1},
            }

        price_retrieve.side_effect = price
        subscription_list.return_value = SimpleNamespace(data=[])
        boundary = billing.service_change_boundary(date(2026, 8, 10))
        schedule_list.return_value = SimpleNamespace(data=[{
            "id": "sub_sched_future",
            "status": "not_started",
            "metadata": {},
            "phases": [{
                "start_date": boundary,
                "items": [{"price": price("price_strong-99")}],
                "automatic_tax": {"enabled": True},
                "invoice_settings": {"days_until_due": 7},
            }],
        }])

        result = billing.schedule_service_change_billing(
            "cus_test",
            contact_id="contact_1",
            request_id="msc-future",
            request_date=date(2026, 8, 3),
            current_price_cents=9900,
            target_service="strong_12_month_commitment",
        )

        phases = schedule_modify.call_args.kwargs["phases"]
        self.assertEqual(result["schedule_id"], "sub_sched_future")
        self.assertIsNone(result["subscription_id"])
        self.assertEqual(phases[0]["items"][0]["price"], "price_strong-89")
        self.assertEqual(phases[1]["items"][0]["price"], "price_strong-99")
        self.assertEqual(phases[0]["automatic_tax"], {"enabled": True})
        self.assertEqual(phases[1]["invoice_settings"], {"days_until_due": 7})
        self.assertEqual(
            schedule_modify.call_args.kwargs["proration_behavior"], "none"
        )

    @patch.object(billing.stripe.SubscriptionSchedule, "modify")
    @patch.object(billing.stripe.SubscriptionSchedule, "list")
    @patch.object(billing.stripe.Subscription, "list")
    @patch.object(billing.stripe.Price, "retrieve")
    def test_strong_commitment_updates_active_managed_schedule_in_place(
        self,
        price_retrieve,
        subscription_list,
        schedule_list,
        schedule_modify,
    ):
        def price(price_id):
            amounts = {
                "price_strong-89": 8900,
                "price_strong-99": 9900,
            }
            return {
                "id": price_id,
                "unit_amount": amounts[price_id],
                "currency": "aud",
                "active": True,
                "recurring": {"interval": "week", "interval_count": 1},
            }

        price_retrieve.side_effect = price
        sub = subscription()
        sub["schedule"] = "sub_sched_active"
        sub["current_period_end"] = billing.service_change_boundary(
            date(2026, 8, 5)
        )
        subscription_list.return_value = SimpleNamespace(data=[sub])
        schedule_list.return_value = SimpleNamespace(data=[{
            "id": "sub_sched_active",
            "status": "active",
            "metadata": {},
            "phases": [{
                "start_date": billing.service_change_boundary(
                    date(2026, 7, 29)
                ),
                "items": [{"price": price("price_strong-99")}],
                "default_payment_method": "pm_existing",
            }],
        }])

        result = billing.schedule_service_change_billing(
            "cus_test",
            contact_id="contact_1",
            request_id="msc-active",
            request_date=date(2026, 8, 3),
            current_price_cents=9900,
            target_service="strong_12_month_commitment",
        )

        phases = schedule_modify.call_args.kwargs["phases"]
        self.assertEqual(result["subscription_id"], "sub_test")
        self.assertEqual(len(phases), 3)
        self.assertEqual(phases[0]["items"][0]["price"], "price_strong-99")
        self.assertEqual(phases[1]["items"][0]["price"], "price_strong-89")
        self.assertEqual(phases[2]["items"][0]["price"], "price_strong-99")
        self.assertTrue(all(
            phase["default_payment_method"] == "pm_existing"
            for phase in phases
        ))
        self.assertTrue(all(
            phase["proration_behavior"] == "none"
            for phase in phases
        ))

    def test_commitment_clawback_quotes_only_discount_actually_received(self):
        quote = billing.commitment_clawback_quote(
            [
                {
                    "status": "paid",
                    "amount_paid": 8900,
                    "charge": {"amount_refunded": 0},
                    "lines": {
                        "data": [{
                            "price": {"id": "price_strong-89"},
                            "quantity": 1,
                        }]
                    },
                },
                {
                    "status": "paid",
                    "amount_paid": 8900,
                    "charge": {"amount_refunded": 4450},
                    "lines": {
                        "data": [{
                            "price": {"id": "price_strong-89"},
                            "quantity": 1,
                        }]
                    },
                },
                {
                    "status": "open",
                    "amount_paid": 0,
                    "lines": {
                        "data": [{
                            "price": {"id": "price_strong-89"},
                            "quantity": 1,
                        }]
                    },
                },
            ],
            discounted_price_id="price_strong-89",
        )

        self.assertEqual(quote["successful_discounted_payments"], 2)
        self.assertEqual(quote["gross_discount_cents"], 2000)
        self.assertEqual(quote["refunded_discount_cents"], 500)
        self.assertEqual(quote["quote_cents"], 1500)
        self.assertFalse(quote["collection_authorized"])

    @patch.object(billing, "stop_failed_cancellation")
    @patch.object(billing, "record_exception")
    @patch.object(billing.stripe.Subscription, "list")
    @patch.object(billing.stripe.Customer, "list")
    def test_schedule_managed_cancellation_fails_closed_when_not_aligned(
        self, customer_list, subscription_list, record_exception, stop_workflow
    ):
        customer_list.return_value = SimpleNamespace(
            data=[SimpleNamespace(id="cus_test")]
        )
        sub = subscription()
        sub["schedule"] = "sub_sched_test"
        subscription_list.return_value = SimpleNamespace(data=[sub])
        record_exception.return_value = True

        response = self.client.post(
            "/stripe/cancel",
            json={
                "contact_id": "contact_1",
                "email": "member@example.com",
                "notice_end_date": "2026-08-28",
                "contact_name": "Test Member",
                "cancellation_type": "Membership",
            },
        )

        self.assertEqual(response.status_code, 422)
        self.assertIn("schedule-managed", response.get_json()["error"])
        stop_workflow.assert_called_once()

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

    def test_hold_return_guard_accepts_current_returning_cycle(self):
        mismatch = billing.validate_hold_return_cycle(
            {
                "hold_lifecycle_status": "On Hold",
                "request_intake_status": "Accepted",
                "hold_start": "2026-08-03",
                "hold_end": "2026-08-10",
                "pre_return": "2026-08-03",
                "request_hold_start": "2026-08-03",
            },
            "returning",
            today=date(2026, 8, 10),
        )

        self.assertEqual(mismatch, "")

    def test_hold_return_guard_accepts_current_completed_cycle(self):
        mismatch = billing.validate_hold_return_cycle(
            {
                "hold_lifecycle_status": "Returning",
                "request_intake_status": "Accepted",
                "hold_start": "2026-08-03",
                "hold_end": "2026-08-10",
                "pre_return": "2026-08-03",
                "request_hold_start": "2026-08-03",
            },
            "completed",
            today=date(2026, 8, 13),
        )

        self.assertEqual(mismatch, "")

    def test_hold_return_guard_rejects_an_older_cycle_against_new_dates(self):
        mismatch = billing.validate_hold_return_cycle(
            {
                "hold_lifecycle_status": "On Hold",
                "request_intake_status": "Accepted",
                "hold_start": "2026-08-31",
                "hold_end": "2026-09-14",
                "pre_return": "2026-09-07",
                "request_hold_start": "2026-08-31",
            },
            "returning",
            today=date(2026, 8, 10),
        )

        self.assertIn("expected on 2026-09-14", mismatch)

    def test_hold_return_guard_rejects_unprotected_or_mismatched_start(self):
        mismatch = billing.validate_hold_return_cycle(
            {
                "hold_lifecycle_status": "On Hold",
                "request_intake_status": "Accepted",
                "hold_start": "2026-08-31",
                "hold_end": "2026-09-14",
                "pre_return": "2026-09-07",
                "request_hold_start": "2026-08-03",
            },
            "returning",
            today=date(2026, 9, 14),
        )

        self.assertIn("does not match current Hold Start Date", mismatch)

    @patch.object(billing, "stop_hold_return_workflow")
    @patch.object(billing, "create_hold_return_exception_task")
    @patch.object(billing, "update_ghl_fields")
    @patch.object(billing, "get_ghl_contact_fields")
    def test_hold_return_endpoint_stops_mismatch_and_creates_one_task(
        self,
        get_fields,
        update_fields,
        create_task,
        stop_workflow,
    ):
        get_fields.return_value = {
            "hold_lifecycle_status": "Pending Hold",
            "request_intake_status": "Accepted",
        }
        create_task.return_value = True

        response = self.client.post(
            "/ghl/hold-return-guard",
            json={
                "contact_id": "contact_1",
                "contact_name": "Test Member",
                "phase": "returning",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "exception")
        update_fields.assert_called_once()
        self.assertEqual(
            update_fields.call_args.args[1]["hold_return_guard_status"],
            "Exception",
        )
        create_task.assert_called_once()
        stop_workflow.assert_called_once_with("contact_1")

    @patch.object(billing.requests, "post")
    @patch.object(billing.requests, "get")
    def test_hold_return_exception_task_is_deduplicated(
        self,
        request_get,
        request_post,
    ):
        message = "Returning write expected Hold Status On Hold; found Pending Hold"
        key = billing.billing_exception_key(
            "contact_1",
            "hold_return_guard",
            message,
        )
        request_get.return_value = MagicMock(
            ok=True,
            json=lambda: {
                "tasks": [
                    {
                        "body": f"Hold Return Guard exception key: {key}",
                        "completed": False,
                    }
                ]
            },
        )

        created = billing.create_hold_return_exception_task(
            "contact_1",
            message,
            contact_name="Test Member",
        )

        self.assertTrue(created)
        request_post.assert_not_called()


if __name__ == "__main__":
    unittest.main()
