import copy
import unittest

from stripe_handler.pt_entitlement_reconciliation import reconcile_pt_hold


def appointment(appointment_id, appointment_date, status="scheduled"):
    return {"id": appointment_id, "date": appointment_date, "status": status}


def payment(payment_id, payment_date, status):
    item = {"id": payment_id, "date": payment_date, "status": status}
    if status == "skipped":
        item["skip_reason"] = "hold"
    return item


def jody_payload():
    """Jody Burke's exact hold boundary, with historical cadence evidence noted."""
    return {
        "conversation_id": "ghl-conversation-jody",
        "contact_name": "Jody Burke",
        "email": "jody@example.com",
        "hold_type": "PT",
        "hold_start_date": "2026-09-09",
        "hold_end_date": "2026-10-07",
        "payment_cadence_days": 7,
        "sessions_per_payment": 2,
        "billing_to_service_offset_days": 7,
        "offset_validated": True,
        "appointments": [
            appointment("sep-01", "2026-09-01", "completed"),
            appointment("sep-03", "2026-09-03", "completed"),
            appointment("sep-08", "2026-09-08", "completed"),
            appointment("sep-10", "2026-09-10"),
            appointment("sep-15", "2026-09-15"),
            appointment("sep-17", "2026-09-17"),
            appointment("sep-22", "2026-09-22"),
            appointment("sep-24", "2026-09-24"),
            appointment("sep-29", "2026-09-29"),
            appointment("oct-01", "2026-10-01"),
            appointment("oct-06", "2026-10-06"),
            appointment("oct-08", "2026-10-08"),
            appointment("oct-13", "2026-10-13"),
            appointment("oct-15", "2026-10-15"),
        ],
        "payments": [
            payment("pay-2026-08-24", "2026-08-24", "paid"),
            payment("pay-2026-08-31", "2026-08-31", "paid"),
            payment("pay-2026-09-07", "2026-09-07", "skipped"),
            payment("pay-2026-09-14", "2026-09-14", "skipped"),
            payment("pay-2026-09-21", "2026-09-21", "skipped"),
            payment("pay-2026-09-28", "2026-09-28", "skipped"),
            payment("pay-2026-10-05", "2026-10-05", "paid"),
        ],
        "existing_adjustments": [],
        "risk_flags": [],
        "acceptance_evidence": {
            "initial_pack": "A$1,200 paid 2025-11-27 for 20 x 30-minute sessions",
            "first_session": "2025-12-03",
            "session_20": "2026-02-05",
            "manual_payment_2026_02_09": "A$120 for 10 and 12 Feb",
            "first_recurring_payment_2026_02_09": "A$120 for 17 and 19 Feb",
        },
    }


class PTEntitlementReconciliationTests(unittest.TestCase):
    def test_jody_exact_boundary_transfers_only_sep_10_to_oct_8(self):
        result = reconcile_pt_hold(jody_payload())

        self.assertEqual(result["status"], "proposal_ready")
        self.assertTrue(result["safe_to_approve"])
        self.assertEqual(
            [item["date"] for item in result["classifications"]["pre_hold"]],
            ["2026-09-01", "2026-09-03", "2026-09-08"],
        )
        self.assertEqual(
            [item["date"] for item in result["classifications"]["in_hold"]],
            [
                "2026-09-10", "2026-09-15", "2026-09-17", "2026-09-22",
                "2026-09-24", "2026-09-29", "2026-10-01", "2026-10-06",
            ],
        )
        self.assertEqual(result["funding"]["paid_in_hold_appointment_ids"], ["sep-10"])
        self.assertEqual(result["funding"]["unfunded_post_hold_appointment_ids"], ["oct-08"])
        aug_31_window = next(
            item for item in result["funding"]["payment_windows"]
            if item["payment_id"] == "pay-2026-08-31"
        )
        self.assertEqual(aug_31_window["appointment_ids"], ["sep-08", "sep-10"])
        self.assertEqual(
            result["funding"]["skipped_payment_dates"],
            ["2026-09-07", "2026-09-14", "2026-09-21", "2026-09-28"],
        )
        self.assertEqual(
            result["proposed_transfers"],
            [{
                "type": "pt_session_entitlement_transfer",
                "source_appointment_id": "sep-10",
                "source_appointment_date": "2026-09-10",
                "source_payment_id": "pay-2026-08-31",
                "target_appointment_id": "oct-08",
                "target_appointment_date": "2026-10-08",
                "skipped_payment_id": "pay-2026-09-28",
                "cash_adjustment": None,
            }],
        )
        self.assertIsNone(result["cash_adjustment"])
        self.assertEqual(result["mutations_performed"], [])
        self.assertEqual(result["hold"]["pre_hold_billing_control_date"], "2026-09-02")
        self.assertEqual(result["hold"]["pre_return_billing_control_date"], "2026-09-30")
        self.assertFalse(result["work_item"]["create_task"])
        self.assertFalse(result["work_item"]["create_tracker"])

    def test_aligned_hold_needs_no_transfer(self):
        payload = jody_payload()
        payload["hold_start_date"] = "2026-09-14"
        payload["hold_end_date"] = "2026-10-04"
        payload["payments"][5]["status"] = "paid"
        result = reconcile_pt_hold(payload)

        self.assertEqual(result["status"], "no_transfer_needed")
        self.assertEqual(result["proposed_transfers"], [])
        self.assertIsNone(result["cash_adjustment"])

    def test_partial_week_boundary_produces_one_safe_transfer(self):
        result = reconcile_pt_hold(jody_payload())
        self.assertEqual(len(result["proposed_transfers"]), 1)

    def test_irregular_cadence_fails_closed(self):
        payload = jody_payload()
        payload["payments"][3]["date"] = "2026-09-15"
        result = reconcile_pt_hold(payload)

        self.assertEqual(result["status"], "review_required")
        self.assertTrue(any("irregular payment cadence" in reason for reason in result["reasons"]))
        self.assertEqual(result["proposed_transfers"], [])

    def test_missing_appointment_evidence_fails_closed(self):
        payload = jody_payload()
        payload["appointments"] = [item for item in payload["appointments"] if item["id"] != "sep-17"]
        result = reconcile_pt_hold(payload)

        self.assertEqual(result["status"], "review_required")
        self.assertTrue(any("expected 2" in reason for reason in result["reasons"]))

    def test_mismatched_boundary_counts_fail_closed(self):
        payload = jody_payload()
        payload["payments"][5]["status"] = "paid"
        result = reconcile_pt_hold(payload)

        self.assertEqual(result["status"], "review_required")
        self.assertTrue(any("counts mismatch" in reason for reason in result["reasons"]))

    def test_cancellation_or_makeup_status_fails_closed(self):
        for status in ("cancelled", "makeup", "forfeited"):
            with self.subTest(status=status):
                payload = jody_payload()
                payload["appointments"][3]["status"] = status
                result = reconcile_pt_hold(payload)
                self.assertEqual(result["status"], "review_required")
                self.assertEqual(result["proposed_transfers"], [])

    def test_duplicate_cash_or_session_adjustment_fails_closed(self):
        for adjustment in (
            {"type": "stripe_credit", "amount_cents": 6000},
            {"type": "entitlement_transfer", "source_appointment_id": "sep-10"},
        ):
            with self.subTest(adjustment=adjustment):
                payload = copy.deepcopy(jody_payload())
                payload["existing_adjustments"] = [adjustment]
                result = reconcile_pt_hold(payload)
                self.assertEqual(result["status"], "review_required")
                self.assertTrue(any("duplicate-credit" in reason for reason in result["reasons"]))
                self.assertEqual(result["cash_adjustment"], None)

    def test_missing_conversation_or_offset_validation_fails_closed(self):
        payload = jody_payload()
        payload["conversation_id"] = ""
        payload["offset_validated"] = False
        result = reconcile_pt_hold(payload)

        self.assertEqual(result["status"], "review_required")
        self.assertIn("missing existing GHL Conversation ID", result["reasons"])
        self.assertIn("billing-to-service offset is not validated", result["reasons"])

    def test_billing_exception_or_unverified_skip_reason_fails_closed(self):
        payload = jody_payload()
        payload["risk_flags"] = ["billing_exception"]
        payload["payments"][2]["skip_reason"] = "failed_payment"
        result = reconcile_pt_hold(payload)

        self.assertEqual(result["status"], "review_required")
        self.assertTrue(any("billing_exception" in reason for reason in result["reasons"]))
        self.assertTrue(any("skip reason" in reason for reason in result["reasons"]))


if __name__ == "__main__":
    unittest.main()
