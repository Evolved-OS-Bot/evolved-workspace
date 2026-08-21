from datetime import UTC, datetime

import pytest

from operating_data_hub.contracts import (
    classify_pt_minder_transaction,
    validate_commercial_evidence,
    validate_membership_reconciliation,
    validate_active_client_cohort,
    validate_active_roster_candidate,
    validate_payment_service_overrides,
    validate_pt_minder,
    validate_service_change_event,
)
from operating_data_hub.store import HubStore


def pt_minder_payload():
    return {
        "observed_at": datetime.now(UTC).isoformat(),
        "rows": [
            {
                "source_account_id": "ptm-1",
                "email": "member@example.com",
                "agreement_id": "agreement-1",
                "product": "PT weekly",
                "state": "active",
                "amount": "120",
                "last_successful_payment": "2026-07-24",
                "next_scheduled_payment": "2026-07-31",
            }
        ],
    }


def test_pt_minder_contract_accepts_minimum_complete_snapshot():
    raw = pt_minder_payload()
    raw["rows"][0]["weekly_amount"] = "120"
    payload = validate_pt_minder(raw)
    assert payload["complete"] is True
    assert payload["transaction_detail_complete"] is False
    assert payload["rows"][0]["amount"] == "120.00"
    assert payload["rows"][0]["weekly_amount"] == "120.00"


def test_pt_minder_contract_discards_displayed_debt_fields():
    raw = pt_minder_payload()
    raw["rows"][0]["amount_due"] = "590"
    raw["rows"][0]["displayed_balance"] = "590"
    raw["rows"][0]["internal_charges"] = [{"amount": "99"}]

    payload = validate_pt_minder(raw)

    assert "amount_due" not in payload["rows"][0]
    assert "displayed_balance" not in payload["rows"][0]
    assert "internal_charges" not in payload["rows"][0]


def test_pt_minder_contract_discards_internal_charge_entries():
    raw = pt_minder_payload()
    raw["transaction_detail_complete"] = True
    raw["rows"][0]["transactions"] = [
        {
            "source_transaction_id": "charge-1",
            "entry_type": "charge",
        },
        {
            "source_transaction_id": "payment-1",
            "entry_type": "payment",
            "occurred_on": "2026-07-03",
            "description": "Bronze Package Weekly",
            "amount": "99",
            "status": "completed",
            "next_scheduled_payment": "2026-07-10",
        },
    ]

    payload = validate_pt_minder(raw)

    transaction_ids = [
        item["source_transaction_id"]
        for item in payload["rows"][0]["transactions"]
    ]
    assert transaction_ids == ["payment-1"]


def test_pt_minder_contract_rejects_empty_or_duplicate_snapshot():
    with pytest.raises(ValueError, match="cannot be empty"):
        validate_pt_minder(
            {
                "observed_at": datetime.now(UTC).isoformat(),
                "rows": [],
            }
        )
    raw = pt_minder_payload()
    raw["rows"].append(dict(raw["rows"][0]))
    with pytest.raises(ValueError, match="duplicate"):
        validate_pt_minder(raw)


def test_store_is_idempotent_and_preserves_latest_complete(tmp_path):
    store = HubStore(f"sqlite:///{tmp_path / 'hub.db'}")
    payload = validate_pt_minder(pt_minder_payload())
    first = store.accept_snapshot("pt_minder", payload)
    second = store.accept_snapshot("pt_minder", payload)

    assert first["status"] == "accepted"
    assert second["status"] == "duplicate"
    assert store.latest_snapshot("pt_minder")["record_count"] == 1


def test_store_closes_jobs_interrupted_by_process_replacement(tmp_path):
    store = HubStore(f"sqlite:///{tmp_path / 'hub.db'}")
    run_id = store.start_job("long-running-cash-backfill")

    assert store.close_interrupted_jobs() == 1
    row = next(
        item
        for item in store.recent_jobs()
        if item["run_id"] == run_id
    )
    assert row["status"] == "failed"
    assert row["completed_at"] is not None
    assert "Railway process ended" in row["error"]


def test_latest_snapshots_returns_one_row_when_observation_times_tie(tmp_path):
    store = HubStore(f"sqlite:///{tmp_path / 'hub.db'}")
    payload = {
        "schema_version": 1,
        "source": "retention_intelligence",
        "observed_at": "2026-07-27T10:00:00+00:00",
        "status": "healthy",
        "complete": True,
        "summary": {"run": 1},
    }
    store.accept_snapshot("retention_intelligence", payload)
    store.accept_snapshot(
        "retention_intelligence",
        {**payload, "summary": {"run": 2}},
    )

    snapshots = store.latest_snapshots()

    assert len(snapshots) == 1
    assert snapshots[0]["payload"]["summary"]["run"] == 2


def test_latest_snapshot_prefers_newest_acceptance_when_observation_ties(
    tmp_path,
):
    store = HubStore(f"sqlite:///{tmp_path / 'hub.db'}")
    first = {
        "schema_version": 1,
        "observed_at": "2026-07-29T01:31:44+00:00",
        "status": "complete",
        "complete": True,
        "summary": {"run": 1},
    }
    second = {
        **first,
        "summary": {"run": 2},
    }

    store.accept_snapshot("revenue_control", first)
    store.accept_snapshot("revenue_control", second)

    assert (
        store.latest_snapshot("revenue_control")["payload"]["summary"]["run"]
        == 2
    )


def test_recurring_income_projection_uses_latest_complete_cash_bridge(
    tmp_path,
):
    store = HubStore(f"sqlite:///{tmp_path / 'hub.db'}")
    observed_at = datetime.now(UTC).isoformat()
    store.accept_snapshot(
        "revenue_control",
        {
            "schema_version": 1,
            "observed_at": observed_at,
            "status": "complete",
            "complete": True,
            "summary": {
                "windowStart": "2026-07-20",
                "windowEnd": "2026-07-26",
                "cashBridge": {
                    "confirmed_current_income": "10250.00",
                    "scheduled_run_rate": "10650.00",
                },
            },
        },
    )
    store.accept_snapshot(
        "revenue_control",
        {
            "schema_version": 1,
            "observed_at": observed_at,
            "status": "complete",
            "complete": True,
            "summary": {
                "completedAt": observed_at,
                "status": "complete",
            },
        },
    )

    projection = store.recurring_income_projection_preview()

    assert projection["available"] is True
    assert projection["projected_weekly_recurring_income"] == "10650.00"
    assert projection["confirmed_weekly_recurring_income"] == "10250.00"


def test_membership_snapshot_projects_shared_canonical_state(tmp_path):
    store = HubStore(f"sqlite:///{tmp_path / 'hub.db'}")
    payload = validate_membership_reconciliation(
        {
            "observed_at": "2026-07-27T10:00:00+00:00",
            "source_run_id": "membership-run-1",
            "rows": [
                {
                    "canonical_key": "member@example.com",
                    "email": "member@example.com",
                    "source_ids": {
                        "ghl": ["ghl-1"],
                        "stripe": ["cus-1"],
                        "trainerize": ["123"],
                    },
                    "service_type": "fast_track",
                    "service_name": "Fast Track",
                    "lifecycle_status": "cancelling",
                    "ghl_active": True,
                    "stripe_entitled": True,
                    "trainerize_active": True,
                    "pt_block_trainer": "Piper Mae",
                    "cancellation_status": "Notice Active",
                    "cancellation_type": "PT",
                    "notice_end_date": "2026-08-01",
                    "final_access_date": "2026-08-03",
                }
            ],
        }
    )

    result = store.accept_membership_snapshot(payload)

    assert payload["rows"][0]["pt_block_trainer"] == "Piper Mae"
    assert payload["rows"][0]["cancellation_type"] == "PT"
    assert payload["rows"][0]["notice_end_date"] == "2026-08-01"
    assert result["canonical"] == {
        "people": 1,
        "active_people": 1,
        "legacy_lifecycle_active_people": 1,
        "active_source_signal_people": 1,
        "commercial_entitlement_signal_people": 1,
        "authoritative_active_clients": 0,
        "decision_required_people": 0,
        "source_identities": 3,
        "service_relationships": 1,
        "active_service_relationships": 1,
        "projected_active_service_relationship_rows": 1,
        "payment_accounts": 0,
        "payment_events": 0,
        "entitlements": 0,
        "lifecycle_states": 1,
    }
    cohort = validate_active_client_cohort(
        {
            "observed_at": "2026-07-27T10:01:00+00:00",
            "as_of_date": "2026-07-27",
            "rule_version": "active-client-cohort-v1",
            "source_refs": {"roster": "run-1"},
            "rows": [
                {
                    "canonical_key": "member@example.com",
                    "in_legacy_cohort": True,
                    "active_signal": True,
                    "confirmed_active": True,
                    "paid_or_entitled": True,
                    "disposition": "confirmed_active",
                    "primary_reason": "governed_active_roster",
                    "decision_required": False,
                    "evidence": {
                        "governed_roster": [
                            {
                                "service": "SGPT",
                                "status": "Active",
                                "product": "Strong",
                            },
                            {
                                "service": "PT",
                                "status": "Active",
                                "product": "30 min PT",
                            },
                        ]
                    },
                }
            ],
        }
    )
    store.accept_active_client_cohort(cohort)
    delivery_identities = store.sgpt_delivery_identity_context()
    assert delivery_identities["active_member_ids"] == [
        next(iter(delivery_identities["active_members"]))
    ]
    assert delivery_identities["trainerize_to_person_id"]["123"] == (
        delivery_identities["active_member_ids"][0]
    )
    notice_periods = store.active_notice_periods(
        as_of=datetime(2026, 7, 29, tzinfo=UTC).date()
    )
    assert notice_periods["active_count"] == 1
    assert notice_periods["downgrade_count"] == 1
    assert notice_periods["full_cancellation_count"] == 0
    assert notice_periods["pt_cancellation_count"] == 0
    assert notice_periods["periods"][0]["transition"] == (
        "Fast Track → Strength & Sculpt"
    )
    assert notice_periods["periods"][0]["notice_type"] == "Downgrade"
    assert notice_periods["periods"][0]["current_service"] == (
        "Fast Track (Strength & Sculpt + 1:1 PT)"
    )
    assert notice_periods["periods"][0]["future_service"] == (
        "Strength & Sculpt"
    )
    assert notice_periods["periods"][0]["effective_end_date"] == (
        "2026-08-03"
    )
    after_downgrade = store.governed_state(
        as_of=datetime(2026, 8, 4, tzinfo=UTC).date()
    )
    assert after_downgrade["service_breakdown"]["fast_track"] == 0
    assert (
        after_downgrade["service_breakdown"][
            "strength_and_sculpt_only"
        ]
        == 1
    )


def test_active_client_cohort_contract_and_store_keep_measures_separate(
    tmp_path,
):
    payload = validate_active_client_cohort(
        {
            "observed_at": "2026-07-27T10:00:00+00:00",
            "as_of_date": "2026-07-27",
            "rule_version": "active-client-cohort-v1",
            "source_refs": {"membership": "snapshot-1", "roster": "run-1"},
            "rows": [
                {
                    "canonical_key": "member@example.com",
                    "in_legacy_cohort": True,
                    "active_signal": True,
                    "confirmed_active": True,
                    "paid_or_entitled": None,
                    "disposition": "confirmed_active",
                    "primary_reason": "governed_active_roster",
                    "decision_required": False,
                    "evidence": {
                        "roster": True,
                        "governed_roster": [
                            {
                                "service": "SGPT",
                                "status": "Active",
                                "classification": "CLEAN_COLLECTING",
                                "product": "LIMITED (2/wk)",
                            },
                            {
                                "service": "PT",
                                "status": "Active",
                                "classification": "CLEAN_COLLECTING",
                                "product": "30 min PT",
                            },
                        ],
                    },
                },
                {
                    "canonical_key": "review@example.com",
                    "in_legacy_cohort": True,
                    "active_signal": True,
                    "confirmed_active": False,
                    "paid_or_entitled": None,
                    "disposition": "decision_required",
                    "primary_reason": "source_signal_absent_from_roster",
                    "decision_required": True,
                    "owner": "Peter",
                    "evidence": {"trainerize": True},
                },
            ],
        }
    )
    store = HubStore(f"sqlite:///{tmp_path / 'hub.db'}")
    result = store.accept_active_client_cohort(payload)

    summary = store.latest_cohort_summary()
    governed = store.governed_state()

    assert summary["legacy_inflated_cohort"] == 2
    assert summary["active_source_signal_people"] == 2
    assert summary["confirmed_active_clients"] == 1
    assert summary["decision_required"] == 1
    assert governed["persisted"] is True
    assert governed["union_people"] == 2
    assert governed["confirmed_active_clients"] == 1
    assert governed["active_service_relationships"] == 2
    assert governed["paid_or_entitled_confirmed"] == 0
    assert governed["paid_or_entitled_unverified"] == 1
    assert governed["decision_required"] == 1
    assert governed["service_breakdown"]["fast_track"] == 1
    assert governed["service_breakdown"]["strength_and_sculpt_only"] == 0
    assert governed["service_breakdown"]["sgpt_with_pt_add_on"] == 0
    assert result["canonical"]["authoritative_active_clients"] == 1
    assert result["canonical"]["active_people"] == 1
    assert result["canonical"]["active_service_relationships"] == 2
    assert result["canonical"]["decision_required_people"] == 1
    assert result["canonical"]["entitlements"] == 2

    commercial = validate_commercial_evidence(
        {
            "source_system": "stripe",
            "source_run_id": "stripe-run-1",
            "observed_at": "2026-07-28T10:00:00+00:00",
            "rows": [
                {
                    "canonical_key": "member@example.com",
                    "source_identity_ids": ["cus-1"],
                    "entitlements": [
                        {
                            "source_record_id": "sub-1",
                            "service_type": "sgpt",
                            "status": "confirmed",
                            "effective_from": "2026-07-20",
                            "effective_to": "2026-07-26",
                            "basis": "paid_invoice",
                            "payment_reference": "in_123",
                        },
                        {
                            "source_record_id": "sub-2",
                            "service_type": "personal_training",
                            "status": "confirmed",
                            "effective_from": "2026-07-20",
                            "effective_to": "2026-08-03",
                            "basis": "paid_invoice",
                        }
                    ],
                    "payment_accounts": [],
                    "payment_events": [],
                }
            ],
        }
    )
    store.accept_commercial_evidence(commercial)

    governed_after_payment = store.governed_state()
    assert governed_after_payment["paid_or_entitled_confirmed"] == 0
    assert governed_after_payment["paid_or_entitled_unverified"] == 1


def test_commercial_contract_rejects_backwards_entitlement_dates():
    with pytest.raises(
        ValueError,
        match="effective_from cannot follow effective_to",
    ):
        validate_commercial_evidence(
            {
                "source_system": "governed_manual",
                "source_run_id": "term-run-1",
                "observed_at": "2026-07-28T10:00:00+00:00",
                "rows": [
                    {
                        "canonical_key": "member@example.com",
                        "entitlements": [
                            {
                                "source_record_id": "term-1",
                                "service_type": "sgpt",
                                "status": "confirmed",
                                "effective_from": "2026-08-01",
                                "effective_to": "2026-07-01",
                            }
                        ],
                    }
                ],
            }
        )


def test_membership_snapshot_retires_services_missing_from_latest_run(
    tmp_path,
):
    store = HubStore(f"sqlite:///{tmp_path / 'hub.db'}")
    first = validate_membership_reconciliation(
        {
            "observed_at": "2026-07-27T10:00:00+00:00",
            "source_run_id": "membership-run-1",
            "rows": [
                {
                    "canonical_key": "member@example.com",
                    "email": "member@example.com",
                    "source_ids": {"ghl": ["ghl-1"]},
                    "services": [
                        {
                            "service_type": "fast_track",
                            "service_name": "Fast Track",
                        },
                        {
                            "service_type": "personal_training",
                            "service_name": "Second weekly PT",
                        },
                    ],
                    "lifecycle_status": "active",
                    "ghl_active": True,
                    "stripe_entitled": True,
                    "trainerize_active": True,
                }
            ],
        }
    )
    second = validate_membership_reconciliation(
        {
            "observed_at": "2026-07-28T10:00:00+00:00",
            "source_run_id": "membership-run-2",
            "rows": [
                {
                    "canonical_key": "member@example.com",
                    "email": "member@example.com",
                    "source_ids": {"ghl": ["ghl-1"]},
                    "services": [
                        {
                            "service_type": "fast_track",
                            "service_name": "Fast Track",
                        }
                    ],
                    "lifecycle_status": "active",
                    "ghl_active": True,
                    "stripe_entitled": True,
                    "trainerize_active": True,
                }
            ],
        }
    )

    store.accept_membership_snapshot(first)
    result = store.accept_membership_snapshot(second)

    assert result["canonical"]["service_relationships"] == 2
    assert result["canonical"]["active_service_relationships"] == 1


def test_commercial_evidence_projects_entitlement_and_payment_events(
    tmp_path,
):
    payload = validate_commercial_evidence(
        {
            "source_system": "stripe",
            "source_run_id": "stripe-run-1",
            "observed_at": "2026-07-28T10:00:00+00:00",
            "rows": [
                {
                    "canonical_key": "member@example.com",
                    "email": "member@example.com",
                    "source_identity_ids": ["cus_123"],
                    "entitlements": [
                        {
                            "source_record_id": "sub_123",
                            "service_type": "sgpt",
                            "status": "confirmed",
                            "effective_from": "2026-07-01",
                            "basis": "active_subscription",
                        }
                    ],
                    "payment_accounts": [
                        {
                            "source_account_id": "cus_123",
                            "agreement_id": "sub_123",
                            "status": "collecting",
                            "weekly_amount": "99",
                        }
                    ],
                    "payment_events": [
                        {
                            "source_event_id": "pi_123",
                            "source_account_id": "cus_123",
                            "occurred_on": "2026-07-25",
                            "amount": "99",
                            "status": "completed",
                            "service_type": "sgpt",
                            "cadence": "recurring",
                            "description": "Weekly membership",
                            "coverage_start": "2026-07-20",
                            "coverage_end": "2026-07-27",
                        }
                    ],
                }
            ],
        }
    )
    store = HubStore(f"sqlite:///{tmp_path / 'hub.db'}")

    result = store.accept_commercial_evidence(payload)

    assert result["status"] == "accepted"
    assert result["canonical"]["people"] == 1
    assert result["canonical"]["source_identities"] == 1
    assert result["canonical"]["entitlements"] == 1
    assert result["canonical"]["payment_accounts"] == 1
    assert result["canonical"]["payment_events"] == 1
    assert payload["rows"][0]["payment_events"][0][
        "coverage_end"
    ] == "2026-07-27"


def test_non_governed_commercial_evidence_is_not_counted_as_covered(
    tmp_path,
):
    store = HubStore(f"sqlite:///{tmp_path / 'hub.db'}")
    cohort = validate_active_client_cohort(
        {
            "observed_at": "2026-07-28T10:00:00+00:00",
            "as_of_date": "2026-07-28",
            "rule_version": "active-client-cohort-v1",
            "source_refs": {"roster": "run-1"},
            "rows": [
                {
                    "canonical_key": "governed@example.com",
                    "in_legacy_cohort": True,
                    "active_signal": True,
                    "confirmed_active": True,
                    "paid_or_entitled": None,
                    "disposition": "confirmed_active",
                    "primary_reason": "governed_active_roster",
                    "decision_required": False,
                    "evidence": {
                        "governed_roster": [
                            {
                                "service": "SGPT",
                                "status": "Active",
                                "product": "Strong",
                            }
                        ]
                    },
                }
            ],
        }
    )
    store.accept_active_client_cohort(cohort)
    commercial = validate_commercial_evidence(
        {
            "source_system": "stripe",
            "source_run_id": "stripe-run-1",
            "observed_at": "2026-07-28T10:01:00+00:00",
            "rows": [
                {
                    "canonical_key": "not-governed@example.com",
                    "source_identity_ids": ["cus-1"],
                    "entitlements": [
                        {
                            "source_record_id": "sub-1",
                            "service_type": "sgpt",
                            "status": "confirmed",
                        }
                    ],
                }
            ],
        }
    )
    store.accept_commercial_evidence(commercial)

    governed = store.governed_state()
    assert governed["paid_or_entitled_confirmed"] == 0
    assert governed["paid_or_entitled_unverified"] == 1


def test_roster_candidate_compares_exact_identities_without_cutover(tmp_path):
    store = HubStore(f"sqlite:///{tmp_path / 'hub.db'}")
    cohort = validate_active_client_cohort(
        {
            "observed_at": "2026-07-27T10:00:00+00:00",
            "as_of_date": "2026-07-27",
            "rule_version": "active-client-cohort-v1",
            "source_refs": {"roster": "accepted-1"},
            "rows": [
                {
                    "canonical_key": "unchanged@example.com",
                    "in_legacy_cohort": True,
                    "active_signal": True,
                    "confirmed_active": True,
                    "paid_or_entitled": None,
                    "disposition": "confirmed_active",
                    "primary_reason": "governed_active_roster",
                    "decision_required": False,
                    "evidence": {
                        "governed_roster": [
                            {
                                "service": "SGPT",
                                "status": "Active",
                                "product": "Strong",
                            }
                        ]
                    },
                },
                {
                    "canonical_key": "removed@example.com",
                    "in_legacy_cohort": True,
                    "active_signal": True,
                    "confirmed_active": True,
                    "paid_or_entitled": None,
                    "disposition": "confirmed_active",
                    "primary_reason": "governed_active_roster",
                    "decision_required": False,
                    "evidence": {
                        "governed_roster": [
                            {
                                "service": "PT",
                                "status": "Active",
                                "product": "PT",
                            }
                        ]
                    },
                },
            ],
        }
    )
    store.accept_active_client_cohort(cohort)
    candidate = validate_active_roster_candidate(
        {
            "source_system": "google_sheet",
            "source_run_id": "revenue-run-2",
            "observed_at": "2026-07-28T10:00:00+00:00",
            "as_of_date": "2026-07-28",
            "rows": [
                {
                    "canonical_key": "unchanged@example.com",
                    "services": [
                        {
                            "service_type": "SGPT",
                            "status": "Active",
                            "source_row": 2,
                        }
                    ],
                },
                {
                    "canonical_key": "added@example.com",
                    "services": [
                        {
                            "service_type": "PT",
                            "status": "Active",
                            "source_row": 3,
                        }
                    ],
                },
            ],
        }
    )
    store.accept_snapshot("active_roster_candidate", candidate)

    comparison = store.roster_candidate_state()

    assert comparison["candidate_active_clients"] == 2
    assert comparison["accepted_active_clients"] == 2
    assert comparison["unchanged_clients"] == 1
    assert comparison["added_since_accepted"] == 1
    assert comparison["removed_since_accepted"] == 1
    assert comparison["exact_match"] is False
    assert store.governed_state()["confirmed_active_clients"] == 2


def test_roster_candidate_promotion_accepts_supported_and_quarantines_unknown(
    tmp_path,
):
    store = HubStore(f"sqlite:///{tmp_path / 'hub.db'}")
    cohort = validate_active_client_cohort(
        {
            "observed_at": "2026-07-27T10:00:00+00:00",
            "as_of_date": "2026-07-27",
            "rule_version": "active-client-cohort-v1",
            "source_refs": {"roster": "accepted-1"},
            "rows": [
                {
                    "canonical_key": "existing@example.com",
                    "in_legacy_cohort": True,
                    "active_signal": True,
                    "confirmed_active": True,
                    "paid_or_entitled": None,
                    "disposition": "confirmed_active",
                    "primary_reason": "governed_active_roster",
                    "decision_required": False,
                    "evidence": {
                        "governed_roster": [
                            {
                                "service": "SGPT",
                                "status": "Active",
                            }
                        ]
                    },
                },
                {
                    "canonical_key": "supported@example.com",
                    "in_legacy_cohort": True,
                    "active_signal": True,
                    "confirmed_active": False,
                    "paid_or_entitled": None,
                    "disposition": "decision_required",
                    "primary_reason": "absent_from_old_roster",
                    "decision_required": True,
                    "evidence": {"trainerize": True},
                },
                {
                    "canonical_key": "unknown@example.com",
                    "in_legacy_cohort": True,
                    "active_signal": True,
                    "confirmed_active": False,
                    "paid_or_entitled": None,
                    "disposition": "timing_difference",
                    "primary_reason": "new_roster_row",
                    "decision_required": False,
                    "evidence": {"trainerize": True},
                },
                {
                    "canonical_key": "pack@example.com",
                    "in_legacy_cohort": True,
                    "active_signal": True,
                    "confirmed_active": False,
                    "paid_or_entitled": None,
                    "disposition": "decision_required",
                    "primary_reason": "prepaid_pack_pending",
                    "decision_required": True,
                    "evidence": {"trainerize": True},
                },
            ],
        }
    )
    store.accept_active_client_cohort(cohort)
    membership = validate_membership_reconciliation(
        {
            "observed_at": "2026-07-28T09:00:00+00:00",
            "source_run_id": "membership-2",
            "rows": [
                {
                    "canonical_key": "supported@example.com",
                    "email": "supported@example.com",
                    "source_ids": {"ghl": ["ghl-1"]},
                    "service_type": "sgpt",
                    "lifecycle_status": "active",
                    "ghl_active": True,
                    "stripe_entitled": True,
                    "trainerize_active": True,
                },
                {
                    "canonical_key": "unknown@example.com",
                    "email": "unknown@example.com",
                    "source_ids": {"trainerize": ["trainerize-1"]},
                    "service_type": "personal_training",
                    "lifecycle_status": "review_required",
                    "ghl_active": False,
                    "stripe_entitled": False,
                    "trainerize_active": True,
                },
                {
                    "canonical_key": "pack@example.com",
                    "email": "pack@example.com",
                    "source_ids": {"ghl": ["ghl-pack"]},
                    "service_type": "personal_training",
                    "lifecycle_status": "active",
                    "ghl_active": True,
                    "stripe_entitled": False,
                    "trainerize_active": True,
                },
            ],
        }
    )
    store.accept_membership_snapshot(membership)
    commercial = validate_commercial_evidence(
        {
            "source_system": "stripe",
            "source_run_id": "stripe-2",
            "observed_at": "2026-07-28T09:01:00+00:00",
            "rows": [
                {
                    "canonical_key": "supported@example.com",
                    "entitlements": [
                        {
                            "source_record_id": "sub-1",
                            "service_type": "sgpt",
                            "status": "confirmed",
                        }
                    ],
                }
            ],
        }
    )
    store.accept_commercial_evidence(commercial)
    pack_commercial = validate_commercial_evidence(
        {
            "source_system": "stripe_pack",
            "source_run_id": "pt-pack-1",
            "observed_at": "2026-07-28T09:02:00+00:00",
            "rows": [
                {
                    "canonical_key": "pack@example.com",
                    "entitlements": [
                        {
                            "source_record_id": (
                                "pi-pack:personal_training"
                            ),
                            "service_type": "personal_training",
                            "status": "confirmed",
                        }
                    ],
                }
            ],
        }
    )
    store.accept_commercial_evidence(pack_commercial)
    candidate = validate_active_roster_candidate(
        {
            "source_system": "google_sheet",
            "source_run_id": "roster-2",
            "observed_at": "2026-07-28T10:00:00+00:00",
            "as_of_date": "2026-07-28",
            "rows": [
                {
                    "canonical_key": "existing@example.com",
                    "services": [
                        {
                            "service_type": "SGPT",
                            "status": "Active",
                            "source_row": 2,
                        }
                    ],
                },
                {
                    "canonical_key": "supported@example.com",
                    "services": [
                        {
                            "service_type": "SGPT",
                            "status": "Active",
                            "source_row": 3,
                        }
                    ],
                },
                {
                    "canonical_key": "unknown@example.com",
                    "services": [
                        {
                            "service_type": "PT",
                            "status": "Active",
                            "source_row": 4,
                        }
                    ],
                },
                {
                    "canonical_key": "pack@example.com",
                    "services": [
                        {
                            "service_type": "PT",
                            "status": "Active",
                            "source_row": 5,
                        }
                    ],
                },
            ],
        }
    )
    accepted = store.accept_snapshot("active_roster_candidate", candidate)

    result = store.promote_roster_candidate(
        expected_snapshot_id=accepted["snapshot_id"]
    )

    assert result["promotion"]["promoted_additions"] == 2
    assert result["promotion"]["candidate_decisions_required"] == 1
    governed = store.governed_state()
    assert governed["confirmed_active_clients"] == 3
    assert governed["decision_required"] == 1
    comparison = store.roster_candidate_state()
    assert comparison["added_since_accepted"] == 1
    assert comparison["removed_since_accepted"] == 0


def test_pt_minder_snapshot_projects_accounts_and_events(tmp_path):
    store = HubStore(f"sqlite:///{tmp_path / 'hub.db'}")
    raw = pt_minder_payload()
    raw["transaction_detail_complete"] = True
    raw["rows"][0]["transactions"] = [
        {
            "source_transaction_id": "payment-1",
            "occurred_on": "2026-07-24",
            "description": "PT weekly",
            "amount": "120",
            "status": "completed",
        }
    ]
    payload = validate_pt_minder(raw)

    result = store.accept_pt_minder_snapshot(payload)

    assert result["canonical"]["people"] == 1
    assert result["canonical"]["payment_accounts"] == 1
    assert result["canonical"]["payment_events"] == 1


def test_pt_minder_contract_classifies_recurring_membership_and_ad_hoc_pt():
    raw = pt_minder_payload()
    raw["transaction_detail_complete"] = True
    raw["rows"][0]["transactions"] = [
        {
            "source_transaction_id": "txn-evolved-anywhere",
            "occurred_on": "2026-07-23",
            "description": "Evolved Anywhere Program - from 23/07/2026 to 29/07/2026",
            "amount": "69",
            "status": "completed",
            "next_scheduled_payment": "2026-07-30",
        },
        {
            "source_transaction_id": "txn-pt",
            "occurred_on": "2026-07-22",
            "description": "1xPT 24/7",
            "amount": "60",
            "status": "completed",
        },
    ]

    payload = validate_pt_minder(raw)

    assert payload["schema_version"] == 2
    membership, pt = payload["rows"][0]["transactions"]
    assert membership["service_type"] == "sgpt"
    assert membership["cadence"] == "recurring"
    assert pt["service_type"] == "personal_training"
    assert pt["cadence"] == "ad_hoc"


def test_pt_minder_transaction_override_requires_explanation():
    raw = pt_minder_payload()
    raw["transaction_detail_complete"] = True
    raw["rows"][0]["transactions"] = [
        {
            "source_transaction_id": "txn-1",
            "occurred_on": "2026-07-23",
            "description": "Manual adjustment",
            "amount": "69",
            "status": "completed",
            "service_type": "sgpt",
            "cadence": "recurring",
        }
    ]

    with pytest.raises(ValueError, match="classification override"):
        validate_pt_minder(raw)


def test_payment_service_override_requires_governance_and_exact_target():
    payload = validate_payment_service_overrides(
        {
            "observed_at": "2026-07-29T12:00:00+10:00",
            "rows": [
                {
                    "source": "pt_minder",
                    "agreement_id": "343361",
                    "service_type": "sgpt",
                    "cadence": "recurring",
                    "expected_weekly_amount": "99",
                    "approved_by": "Peter Brown",
                    "reason": (
                        "Owner confirmed this immutable PT Minder label "
                        "represents Strength and Sculpt."
                    ),
                }
            ],
        }
    )

    assert payload["rows"][0]["agreement_id"] == "343361"
    assert payload["rows"][0]["expected_weekly_amount"] == "99.00"
    assert payload["rows"][0]["active"] is True


def test_governed_pt_minder_snapshot_preserves_raw_label_and_applies_override(
    tmp_path,
):
    store = HubStore(f"sqlite:///{tmp_path / 'hub.db'}")
    raw = pt_minder_payload()
    raw["rows"][0]["weekly_amount"] = "99"
    raw["rows"][0]["product"] = "1:1 PT Leisa (2 x 30 mins)"
    raw["transaction_detail_complete"] = True
    raw["rows"][0]["transactions"] = [
        {
            "source_transaction_id": "txn-nirvana",
            "occurred_on": "2026-07-24",
            "description": (
                "1:1 PT Leisa (2 x 30 mins) - from 24/07/2026 "
                "to 30/07/2026 (recurring payment)"
            ),
            "amount": "99",
            "status": "completed",
        }
    ]
    store.accept_pt_minder_snapshot(validate_pt_minder(raw))
    store.accept_payment_service_overrides(
        validate_payment_service_overrides(
            {
                "observed_at": "2026-07-29T12:00:00+10:00",
                "rows": [
                    {
                        "source": "pt_minder",
                        "agreement_id": "agreement-1",
                        "service_type": "sgpt",
                        "cadence": "recurring",
                        "expected_weekly_amount": "99",
                        "approved_by": "Peter Brown",
                        "reason": (
                            "Owner confirmed the immutable source label "
                            "represents Strength and Sculpt membership."
                        ),
                    }
                ],
            }
        )
    )

    raw_snapshot = store.latest_snapshot("pt_minder")
    governed = store.latest_governed_snapshot("pt_minder")
    raw_transaction = raw_snapshot["payload"]["rows"][0]["transactions"][0]
    transaction = governed["payload"]["rows"][0]["transactions"][0]

    assert raw_transaction["service_type"] == "personal_training"
    assert transaction["raw_service_type"] == "personal_training"
    assert transaction["service_type"] == "sgpt"
    assert transaction["classification"] == "governed_override"
    assert governed["payload"]["rows"][0]["product"] == (
        "1:1 PT Leisa (2 x 30 mins)"
    )
    assert governed["governance"] == {
        "payment_service_overrides_applied": 1,
        "raw_source_payload_preserved": True,
    }


def test_pt_minder_classifier_keeps_service_and_cadence_separate():
    assert classify_pt_minder_transaction("PT weekly") == {
        "service_type": "personal_training",
        "cadence": "recurring",
    }
    assert classify_pt_minder_transaction("2x30 min PT with Megan") == {
        "service_type": "personal_training",
        "cadence": "ad_hoc",
    }
    assert classify_pt_minder_transaction(
        "SGPT (LIMITED 2 PER WEEK) - recurring payment"
    ) == {
        "service_type": "sgpt",
        "cadence": "recurring",
    }
    assert classify_pt_minder_transaction(
        "Bronze Package (Weekly) - recurring payment"
    ) == {
        "service_type": "sgpt",
        "cadence": "recurring",
    }
    assert classify_pt_minder_transaction(
        "Silver Package (Fortnightly) - recurring payment"
    ) == {
        "service_type": "fast_track",
        "cadence": "recurring",
    }


def test_pt_minder_inferred_transaction_refreshes_service_and_period():
    raw = pt_minder_payload()
    raw["transaction_detail_complete"] = True
    raw["rows"][0]["transactions"] = [
        {
            "source_transaction_id": "txn-silver",
            "occurred_on": "2026-07-16",
            "description": (
                "Silver Package (Fortnightly) - from 16/07/2026 "
                "to 29/07/2026 (recurring payment)"
            ),
            "amount": "298",
            "status": "completed",
            "service_type": "other",
            "cadence": "recurring",
            "classification": "inferred",
        }
    ]

    payload = validate_pt_minder(raw)
    transaction = payload["rows"][0]["transactions"][0]

    assert transaction["service_type"] == "fast_track"
    assert transaction["coverage_start"] == "2026-07-16"
    assert transaction["coverage_end"] == "2026-07-29"


def service_change_payload(
    *,
    event_type: str = "requested",
    event_version: int = 1,
    request_id: str = "msc-2026-0001",
    canonical_key: str = "member@example.com",
) -> dict:
    statuses = {
        "billing": "pending",
        "ghl": "pending",
        "trainerize": "pending",
        "appointments": "pending",
        "workbook": "pending",
        "reporting": "pending",
    }
    if event_type == "accepted":
        statuses = {key: "succeeded" for key in statuses}
    return {
        "event_type": event_type,
        "event_version": event_version,
        "request_id": request_id,
        "canonical_key": canonical_key,
        "email": canonical_key,
        "contact_id": "ghl-contact-1",
        "occurred_at": (
            "2026-08-05T09:00:00+10:00"
            if event_type != "requested"
            else "2026-07-02T09:00:00+10:00"
        ),
        "request_date": "2026-07-02",
        "effective_date": "2026-08-05",
        "effective_at": "2026-08-05T00:00:00+10:00",
        "offer_version": "evolved-anywhere-legacy-v1",
        "agreement_version": "legacy-hybrid-survey-v1",
        "signed_at": "2026-07-02T09:00:00+10:00",
        "signature_document": "ghl://submission/submission-1",
        "prior_services": [
            {
                "service_type": "sgpt",
                "service_name": "Strong, Fit & Flexible Membership",
                "weekly_price_cents": 9900,
            }
        ],
        "requested_services": [
            {
                "service_type": "hybrid",
                "service_name": "Evolved Anywhere",
                "weekly_price_cents": 6900,
                "quantity": "1",
                "unit": "30-minute PT every 4 weeks",
            }
        ],
        "surface_statuses": statuses,
        "source_workflow_id": "workflow-1",
        "source_submission_id": "submission-1",
    }


def seed_service_change_prior_state(store: HubStore) -> None:
    store.accept_membership_snapshot(
        validate_membership_reconciliation(
            {
                "observed_at": "2026-07-30T00:00:00+10:00",
                "source_run_id": "service-change-prior-state",
                "rows": [
                    {
                        "canonical_key": "member@example.com",
                        "email": "member@example.com",
                        "source_ids": {"ghl": ["ghl-contact-1"]},
                        "service_type": "sgpt",
                        "service_name": "Strong, Fit & Flexible Membership",
                        "lifecycle_status": "active",
                        "ghl_active": True,
                        "stripe_entitled": True,
                        "trainerize_active": True,
                    }
                ],
            }
        )
    )


def test_service_change_contract_requires_all_surfaces_before_acceptance():
    payload = service_change_payload(
        event_type="accepted",
        event_version=2,
    )
    payload["surface_statuses"]["trainerize"] = "pending"
    with pytest.raises(ValueError, match="every surface"):
        validate_service_change_event(payload)


def test_service_change_contract_rejects_acceptance_before_effective_date():
    payload = service_change_payload(
        event_type="accepted",
        event_version=2,
    )
    payload["occurred_at"] = "2026-08-04T23:59:59+10:00"
    cleaned = validate_service_change_event(payload)
    store = HubStore("sqlite:///:memory:")
    seed_service_change_prior_state(store)
    store.accept_service_change_event(
        validate_service_change_event(service_change_payload())
    )
    with pytest.raises(ValueError, match="cannot precede"):
        store.accept_service_change_event(cleaned)


def test_service_change_events_are_idempotent_and_project_only_on_acceptance():
    store = HubStore("sqlite:///:memory:")
    seed_service_change_prior_state(store)
    requested = validate_service_change_event(service_change_payload())
    first = store.accept_service_change_event(requested)
    duplicate = store.accept_service_change_event(requested)
    assert first["status"] == "accepted"
    assert duplicate["status"] == "duplicate"
    assert store.canonical_counts()["active_service_relationships"] == 1

    accepted = validate_service_change_event(
        service_change_payload(
            event_type="accepted",
            event_version=2,
        )
    )
    result = store.accept_service_change_event(accepted)
    assert result["canonical_projection_updated"] is True
    assert store.canonical_counts()["active_service_relationships"] == 1
    state = store.service_change_state("msc-2026-0001")
    assert state["status"] == "accepted"
    assert [event["event_type"] for event in state["events"]] == [
        "requested",
        "accepted",
    ]


def test_service_change_acceptance_fails_when_prior_state_is_stale():
    store = HubStore("sqlite:///:memory:")
    store.accept_service_change_event(
        validate_service_change_event(service_change_payload())
    )
    accepted = validate_service_change_event(
        service_change_payload(
            event_type="accepted",
            event_version=2,
        )
    )
    with pytest.raises(ValueError, match="current service state"):
        store.accept_service_change_event(accepted)


def test_service_change_rejects_duplicate_and_concurrent_requests():
    store = HubStore("sqlite:///:memory:")
    store.accept_service_change_event(
        validate_service_change_event(service_change_payload())
    )
    concurrent = service_change_payload(
        request_id="msc-2026-0002",
        canonical_key="member@example.com",
    )
    with pytest.raises(ValueError, match="already pending"):
        store.accept_service_change_event(
            validate_service_change_event(concurrent)
        )


def test_service_change_rejects_changed_request_at_acceptance():
    store = HubStore("sqlite:///:memory:")
    store.accept_service_change_event(
        validate_service_change_event(service_change_payload())
    )
    changed = service_change_payload(
        event_type="accepted",
        event_version=2,
    )
    changed["requested_services"][0]["weekly_price_cents"] = 7000
    with pytest.raises(ValueError, match="immutable requested"):
        store.accept_service_change_event(
            validate_service_change_event(changed)
        )


def test_service_change_exception_can_be_repaired_and_then_accepted():
    store = HubStore("sqlite:///:memory:")
    seed_service_change_prior_state(store)
    store.accept_service_change_event(
        validate_service_change_event(service_change_payload())
    )
    exception = service_change_payload(
        event_type="exception",
        event_version=2,
    )
    exception["last_error"] = "Trainerize provisioning failed"
    exception["surface_statuses"]["billing"] = "succeeded"
    store.accept_service_change_event(validate_service_change_event(exception))

    accepted = service_change_payload(
        event_type="accepted",
        event_version=3,
    )
    result = store.accept_service_change_event(
        validate_service_change_event(accepted)
    )

    assert result["canonical_projection_updated"] is True
    state = store.service_change_state("msc-2026-0001")
    assert state["status"] == "accepted"
    assert [event["event_type"] for event in state["events"]] == [
        "requested",
        "exception",
        "accepted",
    ]


def test_service_change_rejects_out_of_order_event_version():
    store = HubStore("sqlite:///:memory:")
    seed_service_change_prior_state(store)
    store.accept_service_change_event(
        validate_service_change_event(service_change_payload())
    )
    accepted = service_change_payload(
        event_type="accepted",
        event_version=3,
    )
    with pytest.raises(ValueError, match="next version"):
        store.accept_service_change_event(
            validate_service_change_event(accepted)
        )
