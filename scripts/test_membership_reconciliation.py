import unittest
from datetime import date
from pathlib import Path
import sys
import tempfile
import csv
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parent))

from membership_reconciliation import (
    GHLReader,
    build_identity_records,
    canonicalise_control_keys,
    classify_exceptions,
    custom_field_map,
    insert_snapshots,
    is_ghl_active,
    is_stripe_entitled,
    load_account_classifications,
    load_authoritative_stripe_customers,
    load_identity_links,
    load_identity_record_links,
    normalise_email,
    open_database,
)


def mock_json_response(payload, status_code=200):
    response = Mock()
    response.status_code = status_code
    response.json.return_value = payload
    response.raise_for_status.return_value = None
    return response


class MembershipReconciliationTests(unittest.TestCase):
    def test_owner_controls_follow_confirmed_email_alias(self):
        controls = {
            "linked@example.com": {
                "classification": "current_pt_client",
                "approved_active_without_local_entitlement": True,
            }
        }
        links = {
            "canonical@example.com": "canonical@example.com",
            "linked@example.com": "canonical@example.com",
        }
        resolved = canonicalise_control_keys(controls, links)
        self.assertIn("canonical@example.com", resolved)
        self.assertNotIn("linked@example.com", resolved)

    def test_old_pt_client_tag_overrides_stale_active_pipeline_stage(self):
        contact = {
            "id": "ghl-1",
            "email": "former-pt@example.com",
            "tags": ["personal training", "old pt client"],
            "customFields": [],
        }
        opportunity = {
            "pipelineStageId": "01d615da-4bd4-4bf3-a5c6-54332588367d",
            "status": "open",
        }
        self.assertFalse(is_ghl_active(contact, opportunity))

    def test_old_pt_client_does_not_hide_current_group_membership(self):
        contact = {
            "id": "ghl-1",
            "email": "current-group@example.com",
            "tags": ["member", "old pt client"],
            "customFields": [],
        }
        self.assertTrue(is_ghl_active(contact, None))

    def test_personal_training_tag_alone_is_not_current_entitlement(self):
        contact = {
            "id": "ghl-1",
            "email": "current-pt@example.com",
            "tags": ["personal training"],
            "customFields": [],
        }
        self.assertFalse(is_ghl_active(contact, None))

    def test_ghl_contact_search_collects_numbered_pages(self):
        reader = GHLReader("test-key", "test-location")
        reader.session.post = Mock(
            side_effect=[
                mock_json_response(
                    {
                        "contacts": [{"id": f"contact-{index}"} for index in range(100)],
                        "total": 101,
                    }
                ),
                mock_json_response(
                    {"contacts": [{"id": "contact-100"}], "total": 101}
                ),
            ]
        )

        contacts = reader.contacts()

        self.assertEqual(len(contacts), 101)
        self.assertEqual(reader.session.post.call_count, 2)
        self.assertEqual(
            reader.session.post.call_args_list[1].kwargs["json"]["page"], 2
        )

    def test_ghl_contact_search_restarts_if_total_changes(self):
        reader = GHLReader("test-key", "test-location")
        reader.session.post = Mock(
            side_effect=[
                mock_json_response(
                    {
                        "contacts": [{"id": f"old-{index}"} for index in range(100)],
                        "total": 101,
                    }
                ),
                mock_json_response(
                    {"contacts": [{"id": "old-100"}], "total": 102}
                ),
                mock_json_response(
                    {
                        "contacts": [{"id": f"new-{index}"} for index in range(100)],
                        "total": 101,
                    }
                ),
                mock_json_response(
                    {"contacts": [{"id": "new-100"}], "total": 101}
                ),
            ]
        )

        contacts = reader.contacts()

        self.assertEqual(len(contacts), 101)
        self.assertEqual(contacts[0]["id"], "new-0")
        self.assertEqual(reader.session.post.call_count, 4)

    def test_ghl_contact_search_rejects_duplicate_ids(self):
        reader = GHLReader("test-key", "test-location")
        first_page = [{"id": f"contact-{index}"} for index in range(100)]
        repeated_page = [{"id": "contact-99"}, {"id": "contact-100"}]
        reader.session.post = Mock(
            side_effect=[
                mock_json_response({"contacts": first_page, "total": 101}),
                mock_json_response({"contacts": repeated_page, "total": 101}),
            ]
            * 3
        )

        with self.assertRaisesRegex(RuntimeError, "remained unstable"):
            reader.contacts()

    def test_owner_approved_staff_access_is_not_an_unexplained_exception(self):
        identities, missing = build_identity_records(
            [],
            [],
            [],
            [],
            [],
            [{"id": 101, "email": "staff@example.com"}],
            [],
        )
        exceptions = classify_exceptions(
            identities,
            missing,
            account_classifications={
                "staff@example.com": {
                    "classification": "staff",
                    "approved_active_without_local_entitlement": True,
                }
            },
        )
        self.assertFalse(
            any(
                row["exception_type"]
                == "trainerize_active_without_current_entitlement_signal"
                for row in exceptions
            )
        )

    def test_owner_approved_external_payment_is_not_a_billing_exception(self):
        identities, missing = build_identity_records(
            [
                {
                    "id": "ghl-1",
                    "email": "external@example.com",
                    "tags": ["member"],
                    "customFields": [],
                }
            ],
            [],
            [],
            [],
            [],
            [{"id": 101, "email": "external@example.com"}],
            [],
        )
        exceptions = classify_exceptions(
            identities,
            missing,
            account_classifications={
                "external@example.com": {
                    "classification": "external_payment_client",
                    "approved_active_without_local_entitlement": True,
                }
            },
        )
        self.assertFalse(
            any(
                row["exception_type"] == "ghl_member_without_stripe_entitlement"
                for row in exceptions
            )
        )

    def test_owner_approved_staff_contact_is_not_missing_trainerize_access(self):
        identities, missing = build_identity_records(
            [
                {
                    "id": "ghl-1",
                    "email": "employee@example.com",
                    "tags": ["trainer"],
                    "customFields": [],
                }
            ],
            [
                {
                    "id": "opp-1",
                    "contactId": "ghl-1",
                    "pipelineId": "fkEvrFkTihYkdb3bpprd",
                    "pipelineStageId": "58247f13-4a47-40f8-8289-35d62fc138b3",
                    "status": "won",
                }
            ],
            [],
            [],
            [],
            [],
            [],
        )
        exceptions = classify_exceptions(
            identities,
            missing,
            account_classifications={
                "employee@example.com": {
                    "classification": "staff",
                    "approved_active_without_local_entitlement": True,
                }
            },
        )
        self.assertFalse(
            any(
                row["exception_type"] == "ghl_member_without_trainerize_access"
                for row in exceptions
            )
        )

    def test_account_classification_loader_requires_explicit_true(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "classifications.csv"
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=[
                        "email",
                        "classification",
                        "approved_active_without_local_entitlement",
                    ],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "email": "staff@example.com",
                        "classification": "Staff",
                        "approved_active_without_local_entitlement": "true",
                    }
                )
            classifications = load_account_classifications(path)
            self.assertTrue(
                classifications["staff@example.com"][
                    "approved_active_without_local_entitlement"
                ]
            )

    def test_owner_confirmed_record_link_resolves_missing_email(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "record-links.csv"
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(
                    handle, fieldnames=["canonical_email", "source", "source_id"]
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "canonical_email": "member@example.com",
                        "source": "ghl",
                        "source_id": "ghl-1",
                    }
                )
            record_links = load_identity_record_links(path)
            identities, missing = build_identity_records(
                [{"id": "ghl-1", "email": "", "tags": ["member"]}],
                [],
                [],
                [],
                [],
                [{"id": 101, "email": "member@example.com"}],
                [],
                {},
                record_links,
            )
            self.assertEqual(len(identities), 1)
            self.assertEqual(missing, [])

    def test_reviewed_stripe_duplicate_is_suppressed_only_when_consistent(self):
        identity = {
            "identity_key": "member@example.com",
            "email": "member@example.com",
            "ghl_contacts": [],
            "stripe_customers": [
                {"id": "cus-old", "email": "member@example.com"},
                {"id": "cus-current", "email": "member@example.com"},
            ],
            "stripe_subscriptions": [
                {
                    "id": "sub-current",
                    "customer": "cus-current",
                    "status": "active",
                }
            ],
            "trainerize_active": [],
            "trainerize_deactivated": [],
            "ghl_active_signal": False,
            "stripe_entitled_signal": True,
            "trainerize_active_signal": False,
            "membership_type": None,
            "membership_stage": None,
            "cancellation_status": None,
            "final_access_date": None,
            "stripe_statuses": ["active"],
        }
        exceptions = classify_exceptions(
            [identity],
            [],
            authoritative_stripe_customers={
                "member@example.com": "cus-current"
            },
        )
        self.assertFalse(
            any(row["exception_type"] == "duplicate_stripe_email" for row in exceptions)
        )
        inconsistent = classify_exceptions(
            [identity],
            [],
            authoritative_stripe_customers={"member@example.com": "cus-old"},
        )
        self.assertTrue(
            any(row["exception_type"] == "duplicate_stripe_email" for row in inconsistent)
        )

    def test_paused_stripe_subscription_is_not_current_entitlement(self):
        self.assertFalse(
            is_stripe_entitled(
                {
                    "status": "active",
                    "pause_collection": {
                        "behavior": "void",
                        "resumes_at": None,
                    },
                }
            )
        )
        self.assertTrue(
            is_stripe_entitled(
                {
                    "status": "active",
                    "pause_collection": None,
                }
            )
        )

    def test_load_authoritative_stripe_customers(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "authoritative-stripe.csv"
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=["email", "authoritative_customer_id"],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "email": "MEMBER@example.com",
                        "authoritative_customer_id": "cus-current",
                    }
                )
            self.assertEqual(
                load_authoritative_stripe_customers(path),
                {"member@example.com": "cus-current"},
            )

    def test_owner_confirmed_identity_links_merge_email_variants(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "links.csv"
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(
                    handle, fieldnames=["canonical_email", "linked_email"]
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "canonical_email": "member@example.com",
                        "linked_email": "billing@example.com",
                    }
                )
            links = load_identity_links(path)
            identities, _ = build_identity_records(
                [{"id": "ghl-1", "email": "member@example.com"}],
                [],
                [{"id": "cus-1", "email": "billing@example.com"}],
                [{"id": "sub-1", "customer": "cus-1", "status": "active"}],
                [],
                [{"id": 101, "email": "member@example.com"}],
                [],
                links,
            )
            self.assertEqual(len(identities), 1)
            self.assertTrue(identities[0]["stripe_entitled_signal"])
            self.assertTrue(identities[0]["trainerize_active_signal"])

    def test_multi_select_custom_fields_are_stored_as_text(self):
        fields = custom_field_map(
            {"customFields": [{"id": "membership", "value": ["Strong", "Online"]}]}
        )
        self.assertEqual(fields["membership"], "Strong, Online")

    def test_email_normalisation_is_exact_and_case_insensitive(self):
        self.assertEqual(normalise_email("  MEMBER@Example.com "), "member@example.com")

    def test_paid_member_without_active_trainerize_is_high_severity(self):
        contacts = [
            {
                "id": "ghl-1",
                "email": "member@example.com",
                "tags": ["member"],
                "customFields": [],
            }
        ]
        customers = [{"id": "cus-1", "email": "member@example.com"}]
        subscriptions = [
            {"id": "sub-1", "customer": "cus-1", "status": "active"}
        ]
        identities, missing = build_identity_records(
            contacts, [], customers, subscriptions, [], [], []
        )
        exceptions = classify_exceptions(
            identities, missing, today=date(2026, 7, 23)
        )
        matching = [
            row
            for row in exceptions
            if row["exception_type"] == "paid_without_trainerize_access"
        ]
        self.assertEqual(len(matching), 1)
        self.assertEqual(matching[0]["severity"], "high")
        self.assertFalse(matching[0]["auto_action_allowed"])

    def test_active_access_after_final_date_is_critical(self):
        contacts = [
            {
                "id": "ghl-1",
                "email": "cancelled@example.com",
                "tags": ["member"],
                "customFields": [
                    {"id": "vqTZezcOELXVjVLRTiCR", "value": "Cancelled"},
                    {"id": "3mZzBYcUk7ZAvB9Fs7lH", "value": "2026-07-20"},
                ],
            }
        ]
        trainerize = [
            {"id": 101, "email": "cancelled@example.com", "status": "active"}
        ]
        identities, missing = build_identity_records(
            contacts, [], [], [], [], trainerize, []
        )
        exceptions = classify_exceptions(
            identities, missing, today=date(2026, 7, 23)
        )
        matching = [
            row
            for row in exceptions
            if row["exception_type"] == "trainerize_active_after_final_access"
        ]
        self.assertEqual(len(matching), 1)
        self.assertEqual(matching[0]["severity"], "critical")

    def test_name_only_matching_is_not_attempted(self):
        contacts = [
            {
                "id": "ghl-1",
                "email": "one@example.com",
                "firstName": "Same",
                "lastName": "Name",
                "tags": ["member"],
                "customFields": [],
            }
        ]
        trainerize = [
            {
                "id": 100,
                "email": "different@example.com",
                "firstName": "Same",
                "lastName": "Name",
            }
        ]
        identities, _ = build_identity_records(
            contacts, [], [], [], [], trainerize, []
        )
        self.assertEqual(len(identities), 2)

    def test_missing_email_is_an_exception_not_a_name_match(self):
        contacts = [{"id": "ghl-1", "email": "", "firstName": "No Email"}]
        identities, missing = build_identity_records(
            contacts, [], [], [], [], [], []
        )
        self.assertEqual(identities, [])
        exceptions = classify_exceptions(missing_email=missing, identities=[])
        self.assertEqual(exceptions[0]["exception_type"], "missing_email")
        self.assertEqual(exceptions[0]["severity"], "low")

    def test_active_ghl_contact_missing_email_is_high_severity(self):
        contacts = [{"id": "ghl-1", "email": "", "tags": ["member"]}]
        identities, missing = build_identity_records(
            contacts, [], [], [], [], [], []
        )
        exceptions = classify_exceptions(identities, missing)
        self.assertEqual(exceptions[0]["severity"], "high")

    def test_inactive_ghl_duplicate_is_low_priority(self):
        contacts = [
            {"id": "ghl-1", "email": "lead@example.com", "tags": []},
            {"id": "ghl-2", "email": "lead@example.com", "tags": []},
        ]
        identities, missing = build_identity_records(
            contacts, [], [], [], [], [], []
        )
        exceptions = classify_exceptions(identities, missing)
        duplicate = next(
            row for row in exceptions if row["exception_type"] == "duplicate_ghl_email"
        )
        self.assertEqual(duplicate["severity"], "low")

    def test_one_entitled_stripe_customer_among_duplicates_is_medium(self):
        customers = [
            {"id": "cus-active", "email": "member@example.com"},
            {"id": "cus-old", "email": "member@example.com"},
        ]
        subscriptions = [
            {"id": "sub-1", "customer": "cus-active", "status": "active"},
            {"id": "sub-2", "customer": "cus-old", "status": "canceled"},
        ]
        identities, missing = build_identity_records(
            [], [], customers, subscriptions, [], [], []
        )
        exceptions = classify_exceptions(identities, missing)
        duplicate = next(
            row
            for row in exceptions
            if row["exception_type"] == "duplicate_stripe_email"
        )
        self.assertEqual(duplicate["severity"], "medium")

    def test_snapshot_schema_accepts_each_source_record(self):
        with tempfile.TemporaryDirectory() as directory:
            connection = open_database(Path(directory) / "test.sqlite")
            contacts = [{"id": "ghl-1", "email": "member@example.com"}]
            customers = [{"id": "cus-1", "email": "member@example.com"}]
            subscriptions = [
                {"id": "sub-1", "customer": "cus-1", "status": "active"}
            ]
            invoices = [
                {"id": "in-1", "customer": "cus-1", "status": "paid", "paid": True}
            ]
            active = [{"id": 101, "email": "member@example.com"}]
            identities, missing = build_identity_records(
                contacts, [], customers, subscriptions, invoices, active, []
            )
            exceptions = classify_exceptions(identities, missing)
            insert_snapshots(
                connection,
                "test-run",
                contacts,
                [],
                customers,
                subscriptions,
                invoices,
                active,
                [],
                identities,
                exceptions,
            )
            connection.commit()
            self.assertEqual(
                connection.execute(
                    "SELECT COUNT(*) FROM identity_register"
                ).fetchone()[0],
                1,
            )
            connection.close()


if __name__ == "__main__":
    unittest.main()
