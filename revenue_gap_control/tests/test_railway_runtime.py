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
    result.hub_pt_minder_state_path = tmp_path / "hub-pt-minder-parity.json"
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
                                "source_transaction_id": "gypsy-23",
                                "occurred_on": "2026-07-23",
                                "description": "Gypsy Program",
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
