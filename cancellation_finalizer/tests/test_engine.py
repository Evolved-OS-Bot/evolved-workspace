from __future__ import annotations

import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path

from cancellation_finalizer.engine import Finalizer, RetryLater, normalize_payload
from cancellation_finalizer.repository import Repository


class FakeIntegrations:
    def __init__(self):
        self.calls = []
        self.fail_step = None
        self.retry_reporting = False

    def _ok(self, step):
        self.calls.append(step)
        if self.fail_step == step:
            raise RuntimeError(f"{step} failed")
        return {"verified": True, "step": step}

    def preflight(self, payload):
        return self._ok("preflight")

    def verify_billing(self, context):
        return self._ok("billing")

    def reconcile_trainerize(self, context):
        return self._ok("trainerize")

    def reconcile_roster(self, context):
        return self._ok("roster")

    def reconcile_ghl(self, context):
        return self._ok("ghl")

    def verify_reporting(self, context):
        self.calls.append("reporting")
        if self.retry_reporting:
            raise RetryLater("waiting for Hub refresh")
        return {"verified": True, "step": "reporting"}

    def complete_task(self, context):
        return self._ok("task")

    def create_exception(self, context, error):
        self.calls.append("exception")
        return {"verified": True, "error": error}


class FinalizerTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        database = Path(self.temp.name) / "cases.db"
        self.repository = Repository(f"sqlite:///{database}")
        self.repository.create_schema()
        self.integrations = FakeIntegrations()

    def tearDown(self):
        self.temp.cleanup()

    @staticmethod
    def payload(final_access_date="2026-08-19"):
        return normalize_payload(
            {
                "contact_id": "contact-1",
                "email": "member@example.com",
                "cancellation_type": "Membership",
                "final_access_date": final_access_date,
                "final_task_id": "task-1",
                "scope": "all_services",
                "requested_at": "2026-08-20T00:00:00Z",
            }
        )

    def test_completes_every_verified_step_in_order(self):
        payload = self.payload()
        case = self.repository.upsert(
            payload, now=datetime(2026, 8, 20, 2, tzinfo=UTC)
        )
        finalizer = Finalizer(
            self.repository,
            self.integrations,
            now=lambda: datetime(2026, 8, 20, 2, tzinfo=UTC),
        )

        result = finalizer.process(case.idempotency_key)

        self.assertEqual(result.status, "completed")
        self.assertEqual(
            self.integrations.calls,
            ["preflight", "billing", "trainerize", "roster", "ghl", "reporting", "task"],
        )
        self.assertEqual(set(result.receipts), set(self.integrations.calls))

    def test_waits_until_first_brisbane_day_after_final_access(self):
        payload = self.payload(final_access_date="2026-08-20")
        case = self.repository.upsert(
            payload, now=datetime(2026, 8, 20, 2, tzinfo=UTC)
        )
        finalizer = Finalizer(
            self.repository,
            self.integrations,
            now=lambda: datetime(2026, 8, 20, 2, tzinfo=UTC),
        )

        result = finalizer.process(case.idempotency_key)

        self.assertEqual(result.status, "retry_scheduled")
        self.assertEqual(result.current_step, "boundary_wait")
        self.assertEqual(self.integrations.calls, [])

    def test_reporting_delay_keeps_task_open_and_retries(self):
        self.integrations.retry_reporting = True
        payload = self.payload()
        case = self.repository.upsert(
            payload, now=datetime(2026, 8, 20, 2, tzinfo=UTC)
        )
        finalizer = Finalizer(
            self.repository,
            self.integrations,
            now=lambda: datetime(2026, 8, 20, 2, tzinfo=UTC),
        )

        result = finalizer.process(case.idempotency_key)

        self.assertEqual(result.status, "retry_scheduled")
        self.assertNotIn("task", self.integrations.calls)
        self.assertIn("ghl", result.receipts)

    def test_failure_creates_one_exception_and_preserves_prior_receipts(self):
        self.integrations.fail_step = "roster"
        payload = self.payload()
        case = self.repository.upsert(
            payload, now=datetime(2026, 8, 20, 2, tzinfo=UTC)
        )
        finalizer = Finalizer(
            self.repository,
            self.integrations,
            now=lambda: datetime(2026, 8, 20, 2, tzinfo=UTC),
        )

        result = finalizer.process(case.idempotency_key)

        self.assertEqual(result.status, "exception")
        self.assertIn("preflight", result.receipts)
        self.assertIn("billing", result.receipts)
        self.assertIn("trainerize", result.receipts)
        self.assertNotIn("ghl", result.receipts)
        self.assertEqual(self.integrations.calls.count("exception"), 1)

    def test_replay_of_completed_case_is_noop(self):
        payload = self.payload()
        case = self.repository.upsert(
            payload, now=datetime(2026, 8, 20, 2, tzinfo=UTC)
        )
        finalizer = Finalizer(
            self.repository,
            self.integrations,
            now=lambda: datetime(2026, 8, 20, 2, tzinfo=UTC),
        )
        finalizer.process(case.idempotency_key)
        calls = list(self.integrations.calls)

        result = finalizer.process(case.idempotency_key)

        self.assertEqual(result.status, "completed")
        self.assertEqual(self.integrations.calls, calls)


if __name__ == "__main__":
    unittest.main()
