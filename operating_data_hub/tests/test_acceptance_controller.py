from datetime import UTC, datetime

import pytest

from operating_data_hub.acceptance_controller import (
    MetricAcceptanceController,
    POLICIES,
)
from operating_data_hub.store import HubStore


def controller(tmp_path):
    store = HubStore(f"sqlite:///{tmp_path / 'hub.db'}")
    return store, MetricAcceptanceController(store.engine)


def complete_job(store, job_id, started_at):
    run_id = store.start_job(job_id)
    with store.engine.begin() as connection:
        connection.exec_driver_sql(
            "UPDATE hub_job_runs SET started_at = ? WHERE run_id = ?",
            (started_at, run_id),
        )
    store.finish_job(run_id, status="complete", summary={"mode": "shadow"})


def base_payload(metric_id, definition_version):
    return {
        "metric_id": metric_id,
        "definition_version": definition_version,
        "cycle_window_start": "2026-08-01T00:00:00+00:00",
        "freshness": [
            {
                "source": "test",
                "age_hours": 1,
                "max_age_hours": 14,
                "complete": True,
            }
        ],
        "identity_sample": {
            "sampled": 10,
            "exact_matches": 10,
            "unexplained_mismatches": 0,
            "selection_method": "deterministic_hash",
            "sample_fingerprint": "sample-fingerprint",
            "entity_grain": "GHL contact",
        },
        "comparisons": [
            {
                "period_id": period_id,
                "comparison_cycle_id": f"comparison-cycle-{cycle}",
                "source_run_id": f"source-run-{cycle}",
                "classification": "exact_match",
                "unexplained_event_count": 0,
                "unexplained_cents": 0,
                "evidence_reference": f"comparison-{cycle}-{period_id}",
            }
            for cycle in (1, 2)
            for period_id in ("week", "28d", "90d")
        ],
        "domain_guards": {
            "unique_contact_deduplication": True,
            "earliest_submission_authority": True,
            "no_write_side_effects": True,
        },
    }


def test_technical_acceptance_is_separate_from_owner_authority(tmp_path):
    store, acceptance = controller(tmp_path)
    complete_job(
        store,
        "reporting-v2-website-analytics-refresh",
        "2026-08-01 20:02:00.000000",
    )
    complete_job(
        store,
        "reporting-v2-website-analytics-refresh",
        "2026-08-02 08:02:00.000000",
    )

    result = acceptance.record(
        base_payload(
            "website_subscribers_unique", "website-marketing-v1"
        ),
        as_of="2026-08-02T09:00:00+00:00",
    )

    assert result["acceptance_state"] == "ready_for_owner_acceptance"
    assert result["technical_gates_passed"] is True
    assert result["owner_approval_state"] == "pending"
    assert result["promotion_authorised"] is False
    assert result["publication_state"] == "shadow"


def test_unelapsed_bounded_observation_collects_without_blocking(tmp_path):
    store, acceptance = controller(tmp_path)
    complete_job(
        store,
        "reporting-v2-xero-accounting-refresh",
        "2026-08-01 20:24:00.000000",
    )
    payload = {
        "metric_id": "operating_expenses",
        "definition_version": "operating-expenses-v2",
        "cycle_window_start": "2026-08-01T00:00:00+00:00",
        "observation_not_before": "2026-08-02T08:24:00+00:00",
        "freshness": [
            {
                "source": "xero_accounting",
                "age_hours": 4,
                "max_age_hours": 26,
                "complete": True,
            }
        ],
        "identity_sample": {},
        "comparisons": [
            {
                "period_id": period_id,
                "comparison_cycle_id": f"comparison-cycle-{cycle}",
                "source_run_id": f"source-run-{cycle}",
                "classification": "bookkeeping_timing",
                "unexplained_event_count": 0,
                "unexplained_cents": 0,
            }
            for cycle in (1, 2)
            for period_id in ("week", "28d", "90d")
        ],
        "domain_guards": {
            "profit_and_loss_expenses_only": True,
            "transfers_and_repayments_excluded": True,
            "expense_categories_reconcile": True,
            "xero_income_excluded_from_cash": True,
            "no_kpi_or_dashboard_write": True,
        },
    }

    result = acceptance.record(
        payload, as_of="2026-08-02T00:20:00+00:00"
    )

    assert result["acceptance_state"] == "collecting"
    assert result["completed_scheduled_cycles"] == 1
    assert result["observation_not_before"] == "2026-08-02T08:24:00+00:00"
    assert result["promotion_authorised"] is False


def test_unexplained_identity_mismatch_blocks_metric(tmp_path):
    store, acceptance = controller(tmp_path)
    complete_job(
        store,
        "reporting-v2-website-analytics-refresh",
        "2026-08-01 20:02:00.000000",
    )
    complete_job(
        store,
        "reporting-v2-website-analytics-refresh",
        "2026-08-02 08:02:00.000000",
    )
    payload = base_payload(
        "website_subscribers_unique", "website-marketing-v1"
    )
    payload["identity_sample"].update(
        exact_matches=9,
        unexplained_mismatches=1,
    )

    result = acceptance.record(
        payload, as_of="2026-08-02T09:00:00+00:00"
    )

    assert result["acceptance_state"] == "blocked"
    assert result["technical_gates_passed"] is False


def test_identity_evidence_rejects_names_and_emails(tmp_path):
    _, acceptance = controller(tmp_path)
    payload = base_payload(
        "website_subscribers_unique", "website-marketing-v1"
    )
    payload["identity_sample"]["email"] = "private@example.com"

    with pytest.raises(ValueError, match="aggregate evidence only"):
        acceptance.record(
            payload, as_of=datetime(2026, 8, 2, tzinfo=UTC)
        )


def test_owner_acceptance_requires_exact_metric_and_rule(tmp_path):
    store, acceptance = controller(tmp_path)
    complete_job(
        store,
        "reporting-v2-website-analytics-refresh",
        "2026-08-01 20:02:00.000000",
    )
    complete_job(
        store,
        "reporting-v2-website-analytics-refresh",
        "2026-08-02 08:02:00.000000",
    )
    payload = base_payload(
        "website_subscribers_unique", "website-marketing-v1"
    )
    payload["owner_approval"] = {
        "approved": True,
        "approved_by": "Peter Brown",
        "metric_id": "website_subscribers_unique",
        "definition_version": "website-marketing-v1",
        "rule_reference": "owner-decision-2026-08-02",
    }

    result = acceptance.record(
        payload, as_of="2026-08-02T09:00:00+00:00"
    )

    assert result["acceptance_state"] == "owner_accepted"
    assert result["owner_approval_state"] == "approved_exact_rule"
    assert result["promotion_authorised"] is False
    assert "separate publication registry" in result["recommendation"]


def test_xero_income_is_never_promoted_as_cash(tmp_path):
    store, acceptance = controller(tmp_path)
    complete_job(
        store,
        "reporting-v2-cash-refresh",
        "2026-08-01 20:20:00.000000",
    )
    complete_job(
        store,
        "reporting-v2-cash-refresh",
        "2026-08-02 08:20:00.000000",
    )
    complete_job(
        store,
        "reporting-v2-xero-accounting-refresh",
        "2026-08-01 20:24:00.000000",
    )
    complete_job(
        store,
        "reporting-v2-xero-accounting-refresh",
        "2026-08-02 08:24:00.000000",
    )
    payload = {
        "metric_id": "cash_accounting_validation",
        "definition_version": "cash-accounting-validation-v1",
        "cycle_window_start": "2026-08-01T00:00:00+00:00",
        "freshness": [
            {
                "source": source,
                "age_hours": 1,
                "max_age_hours": maximum,
                "complete": True,
            }
            for source, maximum in (
                ("stripe", 14),
                ("pt_minder", 192),
                ("xero_accounting", 26),
            )
        ],
            "comparisons": [
                {
                    "period_id": period_id,
                    "comparison_cycle_id": f"comparison-cycle-{cycle}",
                    "source_run_id": f"source-run-{cycle}",
                    "classification": "bookkeeping_timing",
                    "unexplained_event_count": 0,
                    "unexplained_cents": 0,
                }
                for cycle in (1, 2)
                for period_id in ("week", "28d", "90d")
            ],
        "domain_guards": {
            "same_completed_period": True,
            "material_difference_classified": True,
            "xero_income_validation_only": True,
            "cash_goal_unchanged": True,
            "no_kpi_or_dashboard_write": True,
        },
    }

    result = acceptance.record(
        payload, as_of="2026-08-02T09:00:00+00:00"
    )

    latest = acceptance.latest("cash_accounting_validation")[0]
    assert result["acceptance_state"] == "ready_for_owner_acceptance"
    assert latest["acceptance_fingerprint"]
    assert latest["evidence"]["xero_income_can_be_cash"] is False
    assert latest["promotion_authorised"] is False


def test_external_railway_cycles_are_distinct_and_complete(tmp_path):
    _, acceptance = controller(tmp_path)
    payload = {
        "metric_id": "sgpt_delivery",
        "definition_version": "sgpt-delivery-v1",
        "external_cycles": [
            {
                "source": "trainerize_performance",
                "run_id": run_id,
                "complete": True,
                "status": "accepted",
            }
            for run_id in ("trainerize-run-1", "trainerize-run-2")
        ],
        "freshness": [
            {
                "source": "trainerize_performance",
                "age_hours": 1,
                "max_age_hours": 14,
                "complete": True,
            }
        ],
        "identity_sample": {
            "sampled": 20,
            "exact_matches": 20,
            "unexplained_mismatches": 0,
            "sample_fingerprint": "sgpt-sample",
        },
        "comparisons": [
            {
                "period_id": period_id,
                "comparison_cycle_id": f"comparison-cycle-{cycle}",
                "source_run_id": f"source-run-{cycle}",
                "classification": "exact_match",
                "unexplained_event_count": 0,
                "unexplained_cents": 0,
            }
            for cycle in (1, 2)
            for period_id in ("week", "28d", "90d")
        ],
        "domain_guards": {
            "complete_fresh_source": True,
            "exact_identity_set_reconciliation": True,
            "zero_outcome_inference": True,
            "timetable_assignment_coverage": True,
            "no_kpi_or_dashboard_write": True,
        },
    }

    result = acceptance.record(
        payload, as_of="2026-08-02T09:00:00+00:00"
    )

    assert result["acceptance_state"] == "ready_for_owner_acceptance"
    assert result["required_scheduled_cycles"] == 2
    assert result["completed_scheduled_cycles"] == 2


def test_consumer_contract_requires_two_exact_comparison_cycles(tmp_path):
    _, acceptance = controller(tmp_path)
    payload = {
        "metric_id": "consumer_retention_intelligence_contract",
        "definition_version": "retention-hub-read-v1",
        "freshness": [
            {
                "source": "operating_data_hub",
                "age_hours": 1,
                "max_age_hours": 14,
                "complete": True,
            }
        ],
        "comparisons": [
            {
                "period_id": "contract",
                "comparison_cycle_id": f"comparison-{cycle}",
                "source_run_id": f"source-{cycle}",
                "classification": "exact_match",
                "legacy_identity_fingerprint": "identity-fingerprint",
                "hub_identity_fingerprint": "identity-fingerprint",
                "legacy_classification_fingerprint": (
                    "classification-fingerprint"
                ),
                "hub_classification_fingerprint": (
                    "classification-fingerprint"
                ),
                "legacy_only_count": 0,
                "hub_only_count": 0,
                "unexplained_event_count": 0,
                "unexplained_cents": 0,
                "hub_source_complete": True,
                "hub_source_fresh": True,
            }
            for cycle in (1, 2)
        ],
        "domain_guards": {
            "fresh_complete_hub_sources": True,
            "exact_identity_fingerprints": True,
            "exact_classification_fingerprints": True,
            "zero_set_differences": True,
            "legacy_fallback_protected": True,
        },
    }

    result = acceptance.record(
        payload, as_of="2026-08-02T09:00:00+00:00"
    )

    assert result["acceptance_state"] == "ready_for_owner_acceptance"
    assert result["required_scheduled_cycles"] == 2
    assert result["completed_scheduled_cycles"] == 2
    assert result["gate_results"]["completed_comparison_cycles"] == 2

    payload["comparisons"][1]["source_run_id"] = "source-1"
    repeated_source = acceptance.record(
        payload, as_of="2026-08-02T09:00:00+00:00"
    )
    assert repeated_source["acceptance_state"] == "collecting"
    assert repeated_source["completed_scheduled_cycles"] == 1


def test_consumer_contract_fingerprint_difference_blocks(tmp_path):
    _, acceptance = controller(tmp_path)
    payload = {
        "metric_id": "consumer_revenue_control_contract",
        "definition_version": "revenue-control-hub-read-v1",
        "freshness": [
            {
                "source": "operating_data_hub",
                "age_hours": 1,
                "max_age_hours": 14,
                "complete": True,
            }
        ],
        "comparisons": [
            {
                "period_id": "contract",
                "comparison_cycle_id": f"comparison-{cycle}",
                "source_run_id": f"source-{cycle}",
                "classification": "exact_match",
                "legacy_identity_fingerprint": "legacy",
                "hub_identity_fingerprint": "different",
                "legacy_classification_fingerprint": "classification",
                "hub_classification_fingerprint": "classification",
                "legacy_only_count": 0,
                "hub_only_count": 0,
                "unexplained_event_count": 0,
                "unexplained_cents": 0,
                "hub_source_complete": True,
                "hub_source_fresh": True,
            }
            for cycle in (1, 2)
        ],
        "domain_guards": {
            "fresh_complete_hub_sources": True,
            "exact_identity_fingerprints": True,
            "exact_classification_fingerprints": True,
            "zero_set_differences": True,
            "legacy_fallback_protected": True,
        },
    }

    result = acceptance.record(
        payload, as_of="2026-08-02T09:00:00+00:00"
    )

    assert result["acceptance_state"] == "blocked"
    assert result["technical_gates_passed"] is False


def test_evolved_standards_uses_canonical_future_proofing_score_rule(
    tmp_path,
):
    _, acceptance = controller(tmp_path)
    required_periods = (
        "component_evidence",
        "insufficiency_cases",
        "transition_sample",
        "time_to_standard_sample",
        "future_proofing_score_sample",
        "future_proofing_score_insufficiency",
    )
    payload = {
        "metric_id": "evolved_standards",
        "definition_version": "evolved-standards-v1-shadow",
        "external_cycles": [
            {
                "source": "trainerize_performance",
                "run_id": f"trainerize-run-{cycle}",
                "complete": True,
                "status": "accepted",
            }
            for cycle in (1, 2)
        ],
        "freshness": [
            {
                "source": "trainerize_performance",
                "age_hours": 1,
                "max_age_hours": 14,
                "complete": True,
            }
        ],
        "identity_sample": {
            "sampled": 20,
            "exact_matches": 20,
            "unexplained_mismatches": 0,
            "sample_fingerprint": "standards-sample",
        },
        "comparisons": [
            {
                "period_id": period_id,
                "comparison_cycle_id": f"comparison-cycle-{cycle}",
                "source_run_id": f"trainerize-run-{cycle}",
                "classification": "exact_match",
                "unexplained_event_count": 0,
                "unexplained_cents": 0,
            }
            for cycle in (1, 2)
            for period_id in required_periods
        ],
        "domain_guards": {
            "exact_alias_only": True,
            "right_left_independent": True,
            "combined_side_fails_closed": True,
            "missing_duration_load_bodyweight_fails_closed": True,
            "unresolved_identity_or_start_fails_closed": True,
            "stale_or_incomplete_evidence_fails_closed": True,
            "component_evidence_traceable": True,
            "rankings_milestones_standards_separate": True,
            "canonical_six_standard_source_sufficiency": True,
            "all_six_standards_sufficient_for_score": True,
            "no_invented_overall_live_long_perform_label": True,
            "individual_standard_levels_preserved": True,
            "future_proofing_score_range_0_18": True,
            "future_proofing_band_canonical": True,
            "split_squat_weaker_sufficient_side_governs": True,
            "split_squat_asymmetry_retained": True,
            "missing_or_ambiguous_evidence_fails_closed": True,
            "no_kpi_or_dashboard_write": True,
        },
    }

    result = acceptance.record(
        payload, as_of="2026-08-03T09:00:00+00:00"
    )

    assert result["acceptance_state"] == "ready_for_owner_acceptance"
    assert result["gate_results"]["acceptance_rule_version"] == (
        "evolved-standards-future-proofing-score-v1"
    )
    assert "overall_requires_owner_decision" not in (
        POLICIES["evolved_standards"]["guards"]
    )

    accepted_rule_fingerprint = result["acceptance_fingerprint"]
    payload["domain_guards"][
        "all_six_standards_sufficient_for_score"
    ] = False
    incomplete = acceptance.record(
        payload, as_of="2026-08-03T09:00:00+00:00"
    )
    assert incomplete["acceptance_state"] == "blocked"
    assert incomplete["acceptance_fingerprint"] != accepted_rule_fingerprint
