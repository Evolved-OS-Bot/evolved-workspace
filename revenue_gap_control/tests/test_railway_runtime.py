from __future__ import annotations

import csv
from pathlib import Path
from types import SimpleNamespace
from zoneinfo import ZoneInfo

import pytest

from revenue_gap_control.railway_runtime import RailwayRevenueRuntime


def runtime(tmp_path: Path) -> RailwayRevenueRuntime:
    result = object.__new__(RailwayRevenueRuntime)
    result.settings = SimpleNamespace(timezone=ZoneInfo("Australia/Brisbane"))
    result.legacy_evidence_path = tmp_path / "legacy-payment-evidence.csv"
    result.identity_links_path = tmp_path / "identity-links.csv"
    result.account_classifications_path = tmp_path / "account-classifications.csv"
    result.purchased_service_terms_path = (
        tmp_path / "purchased-service-terms.csv"
    )
    result.hub_pt_minder_state_path = tmp_path / "hub-pt-minder-parity.json"
    result.pt_roster_self_mending_path = (
        tmp_path / "pt-roster-self-mending.json"
    )
    result._roster_refresh_lock = __import__("threading").Lock()
    return result


def valid_row() -> dict[str, str]:
    return {
        "email": " Member@Example.com ",
        "payment_rail": "EziDebit",
        "status": "collecting",
        "weekly_amount": "99",
        "last_receipt_date": "2026-07-22",
        "next_due_date": "2026-07-29",
        "notes": "  Verified   in PTMinder. ",
    }


def test_replace_legacy_evidence_normalises_and_hashes(tmp_path):
    service = runtime(tmp_path)

    result = service.replace_legacy_evidence([valid_row()])

    assert result["status"] == "replaced"
    assert result["rowCount"] == 1
    assert len(result["sha256"]) == 64
    with service.legacy_evidence_path.open(newline="", encoding="utf-8") as handle:
        row = next(csv.DictReader(handle))
    assert row == {
        "email": "member@example.com",
        "payment_rail": "PTMinder/EziDebit",
        "status": "collecting",
        "weekly_amount": "99.00",
        "last_receipt_date": "2026-07-22",
        "next_due_date": "2026-07-29",
        "notes": "Verified in PTMinder.",
    }
    assert service.legacy_evidence_status()["rowCount"] == 1


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("email", "not-an-email"),
        ("payment_rail", "Stripe"),
        ("status", "maybe"),
        ("weekly_amount", "zero"),
        ("last_receipt_date", "22/07/2026"),
    ],
)
def test_replace_legacy_evidence_rejects_invalid_rows(tmp_path, field, value):
    service = runtime(tmp_path)
    row = valid_row()
    row[field] = value

    with pytest.raises(ValueError):
        service.replace_legacy_evidence([row])


def test_replace_legacy_evidence_rejects_duplicate_email(tmp_path):
    service = runtime(tmp_path)
    row = valid_row()

    with pytest.raises(ValueError, match="duplicate email"):
        service.replace_legacy_evidence([row, row])


def test_replace_purchased_service_terms_normalises_governed_record(
    tmp_path,
):
    service = runtime(tmp_path)

    result = service.replace_purchased_service_terms(
        [
            {
                "term_id": "term-1",
                "stripe_invoice_id": "in_123",
                "additional_stripe_invoice_ids": ["in_456"],
                "purchaser_email": " Buyer@Example.com ",
                "beneficiary_email": " Member@Example.com ",
                "service_type": "SGPT",
                "quantity": "12",
                "unit": "sessions",
                "state": "APPROVED",
                "effective_from": "2026-07-20",
                "effective_to": "2026-10-20",
                "approved_by": " Peter Brown ",
                "approved_on": "2026-07-28",
                "note": "  Twelve-session package. ",
            }
        ]
    )

    assert result["status"] == "replaced"
    with service.purchased_service_terms_path.open(
        newline="", encoding="utf-8"
    ) as handle:
        row = next(csv.DictReader(handle))
    assert row["purchaser_email"] == "buyer@example.com"
    assert row["beneficiary_email"] == "member@example.com"
    assert row["additional_stripe_invoice_ids"] == "in_456"
    assert row["service_type"] == "sgpt"
    assert row["quantity"] == "12"
    assert row["state"] == "approved"
    assert row["approved_by"] == "Peter Brown"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("stripe_invoice_id", "pi_123"),
        ("additional_stripe_invoice_ids", ["in_123"]),
        ("beneficiary_email", "unknown"),
        ("service_type", "other"),
        ("state", "draft"),
        ("effective_from", ""),
        ("effective_to", "2026-07-01"),
        ("approved_by", ""),
        ("quantity", "zero"),
    ],
)
def test_replace_purchased_service_terms_rejects_incomplete_terms(
    tmp_path, field, value
):
    service = runtime(tmp_path)
    row = {
        "term_id": "term-1",
        "stripe_invoice_id": "in_123",
        "purchaser_email": "buyer@example.com",
        "beneficiary_email": "member@example.com",
        "service_type": "sgpt",
        "quantity": "12",
        "unit": "sessions",
        "state": "approved",
        "effective_from": "2026-07-20",
        "effective_to": "2026-10-20",
        "approved_by": "Peter Brown",
        "approved_on": "2026-07-28",
    }
    row[field] = value

    with pytest.raises(ValueError):
        service.replace_purchased_service_terms([row])


def test_refresh_commercial_evidence_uses_protected_shared_paths(
    tmp_path, monkeypatch
):
    service = runtime(tmp_path)
    service.audit_database = tmp_path / "audit.sqlite"
    captured = {}

    def publish(database, **kwargs):
        captured["database"] = database
        captured.update(kwargs)
        return {"status": "accepted"}

    monkeypatch.setattr(
        "revenue_gap_control.railway_runtime."
        "publish_revenue_commercial_evidence",
        publish,
    )

    result = service.refresh_commercial_evidence_shadow()

    assert result == {"status": "accepted"}
    assert captured == {
        "database": service.audit_database,
        "identity_links_path": service.identity_links_path,
        "legacy_evidence_path": service.legacy_evidence_path,
        "account_classifications_path": (
            service.account_classifications_path
        ),
        "purchased_service_terms_path": (
            service.purchased_service_terms_path
        ),
    }


def test_roster_acceptance_blocks_existing_service_change(
    tmp_path, monkeypatch
):
    service = runtime(tmp_path)
    candidate = {
        "rows": [
            {
                "canonical_key": "member@example.com",
                "services": [
                    {
                        "service_type": "PT",
                        "status": "Active",
                        "classification": None,
                        "product": "PT",
                    }
                ],
            }
        ]
    }
    cohort = {
        "snapshot_id": "cohort-1",
        "payload": {
            "source_refs": {},
            "rows": [
                {
                    "canonical_key": "member@example.com",
                    "confirmed_active": True,
                    "evidence": {
                        "governed_roster": [
                            {"service": "SGPT"}
                        ]
                    },
                }
            ],
        },
    }
    snapshots = {
        "active_roster_candidate": None,
        "active_client_cohort": cohort,
    }
    monkeypatch.setattr(
        service,
        "_latest_source_or_none",
        lambda source: snapshots.get(source),
    )
    monkeypatch.setattr(
        "revenue_gap_control.railway_runtime."
        "publish_roster_candidate_payload",
        lambda payload: {
            "status": "accepted",
            "snapshot_id": "candidate-1",
        },
    )

    result = service._publish_and_promote_roster_candidate(candidate)

    assert result["acceptance"]["status"] == "review_required"
    assert result["acceptance"]["changedServices"] == 1


def test_unchanged_roster_still_publishes_new_freshness_observation(
    tmp_path,
    monkeypatch,
):
    service = runtime(tmp_path)
    candidate = {
        "rows": [
            {
                "canonical_key": "member@example.com",
                "services": [
                    {
                        "service_type": "SGPT",
                        "status": "Active",
                        "classification": None,
                        "product": "Strong",
                    }
                ],
            }
        ]
    }
    snapshots = {
        "active_roster_candidate": {
            "snapshot_id": "candidate-old",
            "payload": candidate,
        },
        "active_client_cohort": {
            "snapshot_id": "cohort-1",
            "payload": {
                "source_refs": {},
                "rows": [
                    {
                        "canonical_key": "member@example.com",
                        "confirmed_active": True,
                        "evidence": {
                            "governed_roster": [
                                {"service": "SGPT"}
                            ]
                        },
                    }
                ],
            },
        },
    }
    monkeypatch.setattr(
        service,
        "_latest_source_or_none",
        lambda source: snapshots.get(source),
    )
    published = []
    monkeypatch.setattr(
        "revenue_gap_control.railway_runtime."
        "publish_roster_candidate_payload",
        lambda payload: (
            published.append(payload)
            or {
                "status": "accepted",
                "snapshot_id": "candidate-new",
            }
        ),
    )

    result = service._publish_and_promote_roster_candidate(candidate)

    assert published == [candidate]
    assert result["snapshot_id"] == "candidate-new"
    assert result["contentUnchanged"] is True


def test_roster_acceptance_promotes_supported_addition(
    tmp_path, monkeypatch
):
    service = runtime(tmp_path)
    candidate = {
        "rows": [
            {
                "canonical_key": "existing@example.com",
                "services": [
                    {
                        "service_type": "SGPT",
                        "status": "Active",
                        "classification": None,
                        "product": "Strong",
                    }
                ],
            },
            {
                "canonical_key": "new@example.com",
                "services": [
                    {
                        "service_type": "SGPT",
                        "status": "Active",
                        "classification": None,
                        "product": "Strong",
                    }
                ],
            },
        ]
    }
    snapshots = {
        "active_roster_candidate": None,
        "active_client_cohort": {
            "snapshot_id": "cohort-1",
            "payload": {
                "source_refs": {},
                "rows": [
                    {
                        "canonical_key": "existing@example.com",
                        "confirmed_active": True,
                        "evidence": {
                            "governed_roster": [
                                {"service": "SGPT"}
                            ]
                        },
                    }
                ],
            },
        },
        "membership_reconciliation": {
            "snapshot_id": "membership-1",
            "payload": {},
        },
        "commercial_evidence_stripe": {
            "snapshot_id": "commercial-1",
            "payload": {},
        },
    }
    monkeypatch.setattr(
        service,
        "_latest_source_or_none",
        lambda source: snapshots.get(source),
    )
    monkeypatch.setattr(
        "revenue_gap_control.railway_runtime."
        "publish_roster_candidate_payload",
        lambda payload: {
            "status": "accepted",
            "snapshot_id": "candidate-1",
        },
    )
    monkeypatch.setattr(
        "revenue_gap_control.railway_runtime."
        "promote_roster_candidate_payload",
        lambda snapshot_id: {
            "status": "accepted",
            "promoted": snapshot_id,
        },
    )

    result = service._publish_and_promote_roster_candidate(candidate)

    assert result["acceptance"] == {
        "status": "accepted",
        "promoted": "candidate-1",
    }


def test_hub_pt_minder_shadow_reports_status_differences(
    tmp_path, monkeypatch
):
    service = runtime(tmp_path)
    service.replace_legacy_evidence(
        [
            valid_row(),
            {
                **valid_row(),
                "email": "review@example.com",
                "status": "review_required",
                "weekly_amount": "149",
                "last_receipt_date": "2026-07-21",
                "next_due_date": "2026-08-04",
            },
        ]
    )
    monkeypatch.setattr(
        "revenue_gap_control.railway_runtime.fetch_latest_source",
        lambda *args, **kwargs: {
            "snapshot_id": "snapshot-1",
            "fingerprint": "a" * 64,
            "observed_at": "2026-07-27T10:00:00+10:00",
            "payload": {
                "rows": [
                    {
                        "email": "member@example.com",
                        "state": "collecting",
                        "amount": "99",
                        "last_successful_payment": "2026-07-22",
                        "next_scheduled_payment": "2026-07-29",
                    },
                    {
                        "email": "review@example.com",
                        "state": "collecting",
                        "amount": "298",
                        "last_successful_payment": "2026-07-21",
                        "next_scheduled_payment": "2026-08-04",
                    },
                ]
            },
        },
    )

    status = service.refresh_hub_pt_minder_shadow()

    assert status["hubEligibleRows"] == 2
    assert status["matchedRows"] == 1
    assert status["mismatchedRows"] == 1
    assert status["cutoverEligible"] is False
    assert status["mismatchFieldCounts"]["status"] == 1
    assert "privateDifferences" not in service.hub_pt_minder_status()


def test_hub_pt_minder_shadow_applies_approved_identity_link(
    tmp_path, monkeypatch
):
    service = runtime(tmp_path)
    service.replace_legacy_evidence([valid_row()])
    service.replace_identity_links(
        [
            {
                "canonical_email": "member@example.com",
                "linked_email": "new-address@example.com",
                "confirmed_name": "Member Example",
                "confirmed_by": "Peter Brown",
                "confirmed_date": "2026-07-27",
                "note": "Approved exact account link.",
            }
        ]
    )
    monkeypatch.setattr(
        "revenue_gap_control.railway_runtime.fetch_latest_source",
        lambda *args, **kwargs: {
            "snapshot_id": "snapshot-2",
            "fingerprint": "b" * 64,
            "observed_at": "2026-07-27T10:00:00+10:00",
            "payload": {
                "rows": [
                    {
                        "email": "new-address@example.com",
                        "state": "collecting",
                        "amount": "99",
                        "last_successful_payment": "2026-07-22",
                        "next_scheduled_payment": "2026-07-29",
                    }
                ]
            },
        },
    )

    status = service.refresh_hub_pt_minder_shadow()

    assert status["matchedRows"] == 1
    assert status["hubOnlyRows"] == 0
    assert status["legacyOnlyRows"] == 0
    assert status["status"] == "source_contract_incomplete"
    assert status["cutoverEligible"] is False


def test_hub_pt_minder_shadow_separates_recurring_and_ad_hoc_pt(
    tmp_path, monkeypatch
):
    service = runtime(tmp_path)
    service.replace_legacy_evidence(
        [
            {
                **valid_row(),
                "email": "anne@example.com",
                "weekly_amount": "69",
                "last_receipt_date": "2026-07-23",
                "next_due_date": "2026-07-30",
            }
        ]
    )
    monkeypatch.setattr(
        "revenue_gap_control.railway_runtime.fetch_latest_source",
        lambda *args, **kwargs: {
            "snapshot_id": "snapshot-v2",
            "fingerprint": "c" * 64,
            "observed_at": "2026-07-27T10:00:00+10:00",
            "payload": {
                "schema_version": 2,
                "transaction_detail_complete": True,
                "rows": [
                    {
                        "email": "anne@example.com",
                        "state": "collecting",
                        "transactions": [
                            {
                                "source_transaction_id": "evolved-anywhere-23",
                                "occurred_on": "2026-07-23",
                                "description": "Evolved Anywhere Program",
                                "amount": "69.00",
                                "status": "completed",
                                "service_type": "sgpt",
                                "cadence": "recurring",
                                "next_scheduled_payment": "2026-07-30",
                            },
                            {
                                "source_transaction_id": "pt-22",
                                "occurred_on": "2026-07-22",
                                "description": "1xPT 24/7",
                                "amount": "60.00",
                                "status": "completed",
                                "service_type": "personal_training",
                                "cadence": "ad_hoc",
                                "next_scheduled_payment": None,
                            },
                            {
                                "source_transaction_id": "pt-20",
                                "occurred_on": "2026-07-20",
                                "description": "2x30 min PT with Megan",
                                "amount": "120.00",
                                "status": "completed",
                                "service_type": "personal_training",
                                "cadence": "ad_hoc",
                                "next_scheduled_payment": None,
                            },
                        ],
                    }
                ],
            },
        },
    )

    status = service.refresh_hub_pt_minder_shadow()

    assert status["status"] == "parity"
    assert status["matchedRows"] == 1
    assert status["adHocPtTransactions"] == 2
    assert status["adHocPtCash"] == "180.00"
    assert status["cutoverEligible"] is True


def test_recurring_evidence_uses_current_schedule_after_hold_and_product_change():
    evidence, ambiguous = RailwayRevenueRuntime._recurring_transaction_evidence(
        {
            "weekly_amount": "99.00",
            "last_successful_payment": "2026-07-03",
            "next_scheduled_payment": "2026-07-31",
            "transactions": [
                {
                    "source_transaction_id": "return-pending",
                    "occurred_on": "2026-07-24",
                    "amount": "99.00",
                    "status": "pending",
                    "service_type": "sgpt",
                    "cadence": "recurring",
                },
                {
                    "source_transaction_id": "last-success",
                    "occurred_on": "2026-07-03",
                    "amount": "99.00",
                    "status": "completed",
                    "service_type": "sgpt",
                    "cadence": "recurring",
                    "next_scheduled_payment": "2026-07-10",
                },
                {
                    "source_transaction_id": "historical-product",
                    "occurred_on": "2026-03-10",
                    "amount": "27.00",
                    "status": "completed",
                    "service_type": "other",
                    "cadence": "recurring",
                    "next_scheduled_payment": "2026-03-17",
                },
            ],
        }
    )

    assert ambiguous is False
    assert evidence == {
        "status": "collecting",
        "weekly_amount": "99.00",
        "last_receipt_date": "2026-07-03",
        "next_due_date": "2026-07-31",
    }


def test_recurring_evidence_ignores_stale_retry_due_date():
    evidence, ambiguous = RailwayRevenueRuntime._recurring_transaction_evidence(
        {
            "weekly_amount": "149.00",
            "last_successful_payment": "2026-07-16",
            "next_scheduled_payment": "2026-03-26",
            "transactions": [
                {
                    "source_transaction_id": "stale-retry",
                    "occurred_on": "2026-07-24",
                    "amount": "298.00",
                    "status": "failed",
                    "service_type": "sgpt",
                    "cadence": "recurring",
                    "next_scheduled_payment": "2026-03-26",
                },
                {
                    "source_transaction_id": "current-success",
                    "occurred_on": "2026-07-16",
                    "amount": "298.00",
                    "status": "completed",
                    "service_type": "sgpt",
                    "cadence": "recurring",
                    "next_scheduled_payment": "2026-07-30",
                },
            ],
        }
    )

    assert ambiguous is False
    assert evidence == {
        "status": "collecting",
        "weekly_amount": "149.00",
        "last_receipt_date": "2026-07-16",
        "next_due_date": "2026-07-30",
    }


def test_hub_pt_minder_shadow_excludes_product_marked_paused(
    tmp_path, monkeypatch
):
    service = runtime(tmp_path)
    monkeypatch.setattr(
        "revenue_gap_control.railway_runtime.fetch_latest_source",
        lambda *args, **kwargs: {
            "snapshot_id": "snapshot-paused",
            "fingerprint": "d" * 64,
            "observed_at": "2026-07-27T10:00:00+10:00",
            "payload": {
                "schema_version": 2,
                "transaction_detail_complete": True,
                "rows": [
                    {
                        "email": "paused@example.com",
                        "product": "1:1 PT, paused (paused)",
                        "state": "collecting",
                        "weekly_amount": "110.00",
                        "last_successful_payment": "2026-06-23",
                        "next_scheduled_payment": "2026-06-30",
                        "transactions": [
                            {
                                "source_transaction_id": "old-success",
                                "occurred_on": "2026-06-23",
                                "amount": "110.00",
                                "status": "completed",
                                "service_type": "personal_training",
                                "cadence": "recurring",
                                "next_scheduled_payment": "2026-06-30",
                            }
                        ],
                    }
                ],
            },
        },
    )

    status = service.refresh_hub_pt_minder_shadow()

    assert status["hubEligibleRows"] == 0
    assert status["hubOnlyRows"] == 0
    assert status["cutoverEligible"] is False


def test_replace_shared_identity_and_account_evidence(tmp_path):
    service = runtime(tmp_path)

    identity = service.replace_identity_links(
        [
            {
                "canonical_email": "Member@Example.com",
                "linked_email": "payer@example.com",
                "confirmed_name": "Member Example",
                "confirmed_by": "Peter Brown",
                "confirmed_date": "2026-07-27",
                "note": "Approved Stripe alias.",
            }
        ]
    )
    account = service.replace_account_classifications(
        [
            {
                "email": "member@example.com",
                "name": "Member Example",
                "classification": "external_payment_client",
                "approved_active_without_local_entitlement": True,
                "confirmed_by": "Peter Brown",
                "confirmed_date": "2026-07-27",
                "note": "Pays through another Stripe account.",
            }
        ]
    )

    assert identity["rowCount"] == 1
    assert account["rowCount"] == 1
    status = service.shared_evidence_status()
    assert status["identityLinks"]["rowCount"] == 1
    assert status["accountClassifications"]["rowCount"] == 1


def test_purchased_service_terms_can_be_read_back(tmp_path):
    service = runtime(tmp_path)
    service.replace_purchased_service_terms(
        [
            {
                "term_id": "term-1",
                "stripe_invoice_id": "in_example",
                "purchaser_email": "payer@example.com",
                "beneficiary_email": "member@example.com",
                "service_type": "personal_training",
                "quantity": "4",
                "unit": "30-minute sessions",
                "state": "approved",
                "effective_from": "2026-07-01",
                "effective_to": "2026-07-28",
                "approved_by": "Peter Brown",
                "approved_on": "2026-07-29",
                "note": "Fast Track onboarding term.",
            }
        ]
    )

    result = service.purchased_service_terms()

    assert result["status"] == "ready"
    assert result["rowCount"] == 1
    assert result["rows"][0]["term_id"] == "term-1"
