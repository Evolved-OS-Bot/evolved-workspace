from __future__ import annotations

import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from cancellation_finalizer.integrations import ProductionIntegrations


class TrainerizeIntegrationTest(unittest.TestCase):
    def test_deactivation_uses_guarded_api_and_exact_roster_readback(self):
        settings = SimpleNamespace(
            stripe_api_key="",
            trainerize_api_base_url="https://api.trainerize.com/v03",
            trainerize_group_id="group",
            trainerize_api_token="token",
        )
        session = Mock()
        integration = ProductionIntegrations(settings, session=session)
        integration._require_writes = Mock()
        integration._trainerize_rows = Mock(
            side_effect=[
                [{"id": 42, "email": "member@example.com"}],
                [],
                [],
                [{"id": 42, "email": "member@example.com"}],
            ]
        )

        receipt = integration.reconcile_trainerize(
            {
                "email": "member@example.com",
                "idempotency_key": "case-1",
                "preflight": {"deactivate_trainerize": True},
            }
        )

        self.assertEqual(receipt["action"], "deactivated")
        session.post.assert_called_once_with(
            "https://api.trainerize.com/v03/user/setStatus",
            auth=("group", "token"),
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            json={
                "userID": 42,
                "accountStatus": "deactivated",
                "enableSignin": False,
                "enableMessage": False,
            },
            timeout=30,
        )


if __name__ == "__main__":
    unittest.main()
