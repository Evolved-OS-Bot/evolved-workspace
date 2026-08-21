import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from preview_trainerize_membership import build_preview


class MembershipPreviewTests(unittest.TestCase):
    def valid_event(self):
        return {
            "correlation_id": "sale-test-001",
            "email": "test.member@example.com",
            "trainerize_user_id": 12345,
            "offer": "Strong, Fit & Flexible",
            "agreement_signed": True,
            "upfront_payment_status": "succeeded",
            "membership_start_date": "2026-08-03",
        }

    def test_ready_preview_uses_recorded_start_date(self):
        result = build_preview(self.valid_event())
        self.assertEqual(result["status"], "ready_for_review")
        self.assertFalse(result["external_write"])
        self.assertEqual(
            result["proposed_action"]["product_start_date"], "2026-08-03"
        )
        self.assertFalse(result["proposed_action"]["create_client"])
        self.assertFalse(result["proposed_action"]["send_second_invitation"])
        self.assertEqual(
            result["proposed_action"]["expected_configuration"]["client_type"],
            "Full Access / 1-way messaging",
        )
        self.assertEqual(
            result["proposed_action"]["expected_configuration"]["trainer"],
            "Evolved All Female Gym",
        )

    def test_legacy_limited_maps_to_fit_flexible(self):
        event = self.valid_event()
        event["offer"] = "limited"
        result = build_preview(event)
        self.assertEqual(result["proposed_action"]["canonical_offer"], "fit_flexible")
        self.assertIsNone(
            result["proposed_action"]["expected_configuration"]["add_on_program"]
        )
        self.assertIsNone(
            result["proposed_action"]["expected_configuration"]["group"]
        )

    def test_pt_frequency_tag_is_not_a_fit_flexible_offer_alias(self):
        event = self.valid_event()
        event["offer"] = "1 p.wk"
        result = build_preview(event)
        self.assertEqual(result["status"], "exception")

    def test_missing_payment_and_start_date_stop_the_action(self):
        event = self.valid_event()
        event["upfront_payment_status"] = "pending"
        event["membership_start_date"] = ""
        result = build_preview(event)
        self.assertEqual(result["status"], "exception")
        self.assertFalse(result["external_write"])
        self.assertEqual(len(result["errors"]), 2)


if __name__ == "__main__":
    unittest.main()
