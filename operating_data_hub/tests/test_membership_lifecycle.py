from datetime import UTC, datetime

from operating_data_hub.contracts import (
    validate_active_client_cohort,
    validate_membership_reconciliation,
)
from operating_data_hub.current_people import (
    _roster_attributes,
    build_current_people_contract,
)
from operating_data_hub.membership_lifecycle import (
    MembershipLifecycleRepository,
    project_snapshot_row,
)
from operating_data_hub.reporting_v2 import ReportingV2Repository
from operating_data_hub.store import HubStore


def setup_repositories(tmp_path):
    store = HubStore(f"sqlite:///{tmp_path / 'hub.db'}")
    reporting = ReportingV2Repository(store.engine)
    lifecycle = MembershipLifecycleRepository(store.engine, reporting)
    return store, reporting, lifecycle


def membership_payload(rows):
    return validate_membership_reconciliation(
        {
            "observed_at": "2026-07-30T00:00:00+00:00",
            "source_run_id": "membership-run-1",
            "rows": rows,
        }
    )


def member(
    email,
    contact_id,
    *,
    services,
    lifecycle_status="active",
    cancellation_status=None,
    cancellation_type=None,
    final_access_date=None,
    hold_status=None,
    hold_start_date=None,
    hold_end_date=None,
):
    return {
        "canonical_key": email,
        "email": email,
        "source_ids": {"ghl": [contact_id]},
        "services": [
            {"service_type": service, "service_name": service}
            for service in services
        ],
        "lifecycle_status": lifecycle_status,
        "ghl_active": lifecycle_status in {"active", "cancelling"},
        "stripe_entitled": lifecycle_status in {"active", "cancelling"},
        "trainerize_active": lifecycle_status in {"active", "cancelling"},
        "cancellation_status": cancellation_status,
        "cancellation_type": cancellation_type,
        "final_access_date": final_access_date,
        "hold_status": hold_status,
        "hold_type": "Membership" if hold_status else None,
        "hold_start_date": hold_start_date,
        "hold_end_date": hold_end_date,
    }


def test_fast_track_pt_ending_is_downgrade_not_member_loss():
    projection = project_snapshot_row(
        member(
            "fast@example.com",
            "ghl-fast",
            services=["sgpt", "personal_training"],
            lifecycle_status="cancelling",
            cancellation_status="Notice Active",
            cancellation_type="PT",
            final_access_date="2026-07-25",
        ),
        person_id="person-fast",
    )

    assert [row["event_type"] for row in projection["events"]] == [
        "downgrade_only"
    ]
    assert projection["exceptions"] == []


def test_missing_final_date_is_quarantined_and_never_counted(tmp_path):
    store, _reporting, lifecycle = setup_repositories(tmp_path)
    payload = membership_payload(
        [
            member(
                "ambiguous@example.com",
                "ghl-ambiguous",
                services=["sgpt"],
                lifecycle_status="cancelling",
                cancellation_status="Notice Active",
                cancellation_type="Membership",
            )
        ]
    )
    accepted = store.accept_membership_snapshot(payload)
    result = lifecycle.record_membership_snapshot(
        payload,
        source_snapshot_id=accepted["snapshot_id"],
    )
    preview = lifecycle.preview(
        "28d",
        as_of="2026-07-30T00:00:00+00:00",
    )

    assert result["quarantined_event_versions"] == 1
    assert result["exceptions"][0]["code"] == "missing_final_access_date"
    assert preview["final_membership_endings"] == 0
    assert preview["active_notice"]["missing_final_access_date"] == 1
    assert preview["complete"] is False


def test_period_metrics_use_unique_people_and_exact_opening_cohort(tmp_path):
    store, reporting, lifecycle = setup_repositories(tmp_path)
    payload = membership_payload(
        [
            member(
                "fast@example.com",
                "ghl-fast",
                services=["sgpt", "personal_training"],
                lifecycle_status="cancelling",
                cancellation_status="Notice Active",
                cancellation_type="PT",
                final_access_date="2026-07-25",
            ),
            member(
                "ended@example.com",
                "ghl-ended",
                services=["sgpt"],
                lifecycle_status="cancelled",
                cancellation_status="Cancelled",
                cancellation_type="Membership",
                final_access_date="2026-07-24",
            ),
            member(
                "hold@example.com",
                "ghl-hold",
                services=["sgpt"],
                hold_status="On Hold",
                hold_start_date="2026-07-22",
                hold_end_date="2026-08-05",
            ),
        ]
    )
    accepted = store.accept_membership_snapshot(payload)
    lifecycle.record_membership_snapshot(
        payload,
        source_snapshot_id=accepted["snapshot_id"],
    )
    people = lifecycle._person_ids_by_canonical_key(
        [
            "fast@example.com",
            "ended@example.com",
            "hold@example.com",
        ]
    )
    sale_source = reporting.accept_source_event(
        {
            "source_system": "ghl",
            "source_object_type": "commercial_agreement",
            "source_event_id": "agreement-fast",
            "occurred_at": "2026-07-23T00:00:00+10:00",
            "observed_at": "2026-07-23T01:00:00+10:00",
            "confidence": "verified",
            "payload": {"contact_id": "ghl-fast"},
        }
    )
    reporting.record_sale(
        {
            "sale_id": "sale-fast",
            "source_system": "ghl",
            "source_sale_id": "agreement-fast",
            "sold_at": "2026-07-23T00:00:00+10:00",
            "sale_type": "membership",
            "qualifying_new_membership": True,
            "confidence": "verified",
            "source_event_version_id": sale_source["event_version_id"],
            "service_components": [
                {"service_type": "sgpt", "service_name": "Fast Track"},
                {
                    "service_type": "personal_training",
                    "service_name": "Fast Track",
                },
            ],
        }
    )
    backfill = lifecycle.record_historical_backfill(
        {
            "observed_at": "2026-07-30T00:00:00+00:00",
            "source_run_id": "historical-1",
            "records": [],
            "opening_cohorts": [
                {
                    "as_of_date": "2026-07-02",
                    "canonical_keys": [
                        "fast@example.com",
                        "ended@example.com",
                        "hold@example.com",
                    ],
                    "coverage_complete": True,
                    "confidence": "high",
                    "source_record_id": "opening-2026-07-02",
                    "evidence": {"source": "protected workbook reconstruction"},
                }
            ],
        }
    )
    preview = lifecycle.preview(
        "28d",
        as_of="2026-07-30T00:00:00+00:00",
    )

    assert backfill["accepted_event_versions"] == 1
    assert preview["members_joined"] == 1
    assert preview["final_membership_endings"] == 1
    assert preview["straight_cancellations"] == 1
    assert preview["downgrade_only_transitions"] == 1
    assert preview["approved_holds"] == 1
    assert preview["opening_cohort"]["unique_people"] == 3
    assert preview["attrition_rate"] == "0.3333333333333333333333333333"
    assert preview["net_unique_member_growth"] == 0


def test_ambiguous_historical_date_fails_closed(tmp_path):
    store, _reporting, lifecycle = setup_repositories(tmp_path)
    payload = membership_payload(
        [member("member@example.com", "ghl-1", services=["sgpt"])]
    )
    store.accept_membership_snapshot(payload)

    result = lifecycle.record_historical_backfill(
        {
            "observed_at": "2026-07-30T00:00:00+00:00",
            "source_run_id": "historical-ambiguous",
            "records": [
                {
                    "canonical_key": "member@example.com",
                    "event_type": "membership_ended",
                    "effective_date": "2026-07-20",
                    "ambiguous_date": True,
                    "confidence": "high",
                    "source_record_id": "legacy-row-1",
                }
            ],
            "opening_cohorts": [],
        }
    )

    assert result["accepted_event_versions"] == 0
    assert result["quarantined_event_versions"] == 1


def test_current_people_contract_is_person_keyed_and_explicit(tmp_path):
    store, _reporting, _lifecycle = setup_repositories(tmp_path)
    payload = membership_payload(
        [
            {
                **member(
                    "member@example.com",
                    "ghl-1",
                    services=["sgpt"],
                    hold_status="On Hold",
                    hold_start_date="2026-07-20",
                    hold_end_date="2026-08-10",
                ),
                "first_name": "Sam",
                "last_name": "Member",
            }
        ]
    )
    store.accept_membership_snapshot(payload)
    store.accept_active_client_cohort(
        validate_active_client_cohort(
            {
                "observed_at": "2026-07-30T00:00:00+00:00",
                "as_of_date": "2026-07-29",
                "rule_version": "test-v1",
                "source_refs": {
                    "membership_reconciliation": "membership-run-1"
                },
                "rows": [
                    {
                        "canonical_key": "member@example.com",
                        "in_legacy_cohort": True,
                        "active_signal": True,
                        "confirmed_active": True,
                        "paid_or_entitled": True,
                        "disposition": "confirmed_active",
                        "primary_reason": "accepted",
                        "decision_required": False,
                        "evidence": {
                            "source": "test",
                            "governed_roster": [
                                {
                                    "service": "PT",
                                    "status": "Active",
                                    "classification": "CLEAN_COLLECTING",
                                    "product": "PT",
                                    "assigned_trainer": "Piper Mae",
                                    "contracted_weekly_frequency": "2",
                                    "service_duration": "30 mins",
                                    "weekly_allocation": None,
                                    "allocation_currency": None,
                                    "payment_marker": "PIF",
                                    "allocation_basis": "prepaid",
                                }
                            ],
                        },
                    }
                ],
            }
        )
    )
    contract = build_current_people_contract(
        store.engine,
        period={
            "id": "28d",
            "start": "2026-07-02",
            "end": "2026-07-29",
            "timezone": "Australia/Brisbane",
            "as_of": "2026-07-29",
        },
        source_freshness=[],
        as_of=datetime(2026, 7, 30, tzinfo=UTC),
    )
    row = contract["rows"][0]

    assert row["person_id"]
    assert row["display"]["email"] == "member@example.com"
    assert row["display"]["identity_authority"] is False
    assert row["source_identities"][0]["source_record_id"] == "ghl-1"
    assert row["lifecycle"]["hold_status"] == "On Hold"
    assert row["delivery_attributes"]["complete"] is True
    roster = next(
        relationship["governed_roster_attributes"]
        for relationship in row["service_relationships"]
        if relationship["source"] == "active_client_cohort"
    )
    assert roster["attributes"]["assigned_trainer"] == "Piper Mae"
    assert roster["attributes"]["contracted_weekly_frequency"] == "2"
    assert roster["attributes"]["service_duration"] == "30 mins"
    assert roster["attributes"]["weekly_allocation"] is None
    assert roster["attributes"]["weekly_allocation_applicable"] is False
    assert roster["attributes"]["allocation_basis"] == "prepaid"
    assert roster["attributes"]["allocation_evidence_status"] == (
        "confirmed_prepaid_entitlement"
    )
    assert "approved_hold" in row["suppression_reasons"]
    assert "entitlements" in row
    assert row["entitlement_missing_reason"] is None
    assert row["entitlements"][0]["metadata"]["basis"] == (
        "governed_roster"
    )
    assert "payment_accounts" in row


def test_prepaid_pt_without_contract_frequency_remains_explicitly_incomplete():
    relationship = {
        "service_type": "personal_training",
        "service_name": "PT",
        "metadata_json": (
            '{"product":"PT","assigned_trainer":"Piper Mae",'
            '"contracted_weekly_frequency":null,'
            '"service_duration":"30 mins","weekly_allocation":null,'
            '"allocation_currency":null,"payment_marker":"PIF",'
            '"allocation_basis":"prepaid"}'
        ),
        "effective_from": None,
        "effective_to": None,
        "source": "active_client_cohort",
        "source_record_id": "roster-1",
        "source_snapshot_id": "snapshot-1",
    }

    roster = _roster_attributes(
        relationship,
        confirmed_entitlement=True,
    )

    assert roster["complete"] is False
    assert roster["missing_attributes"] == [
        "contracted_weekly_frequency"
    ]
    assert roster["attributes"]["allocation_evidence_status"] == (
        "confirmed_prepaid_entitlement"
    )
