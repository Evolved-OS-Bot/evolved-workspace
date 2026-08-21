from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime, time, timedelta
from typing import Any, Iterable
from zoneinfo import ZoneInfo

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    UniqueConstraint,
    insert,
    select,
)

from .contracts import canonical_json, fingerprint
from .store import job_runs


BRISBANE_TZ = ZoneInfo("Australia/Brisbane")
GATE_VERSION = "metric-acceptance-v1"
EXPLAINABLE_DIFFERENCES = {
    "exact_match",
    "legacy_defect",
    "timing",
    "bookkeeping_timing",
    "approved_definition_change",
}
ACCEPTANCE_STATES = {
    "collecting",
    "blocked",
    "ready_for_owner_acceptance",
    "owner_accepted",
}

acceptance_metadata = MetaData()

metric_acceptance_evidence = Table(
    "hub_metric_acceptance_evidence",
    acceptance_metadata,
    Column("acceptance_record_id", String(64), primary_key=True),
    Column("metric_id", String(120), nullable=False, index=True),
    Column("definition_version", String(80), nullable=False),
    Column("gate_version", String(80), nullable=False),
    Column("acceptance_state", String(40), nullable=False),
    Column("technical_gates_passed", Integer, nullable=False),
    Column("owner_approval_state", String(40), nullable=False),
    Column("owner_approval_reference", Text),
    Column("publication_state", String(40), nullable=False),
    Column("promotion_authorised", Integer, nullable=False),
    Column("required_scheduled_cycles", Integer, nullable=False),
    Column("completed_scheduled_cycles", Integer, nullable=False),
    Column("observation_not_before", DateTime(timezone=True)),
    Column("recommendation", Text, nullable=False),
    Column("gate_results_json", Text, nullable=False),
    Column("evidence_json", Text, nullable=False),
    Column("acceptance_fingerprint", String(64), nullable=False),
    Column("recorded_at", DateTime(timezone=True), nullable=False),
    UniqueConstraint(
        "metric_id",
        "definition_version",
        "acceptance_fingerprint",
        name="uq_hub_metric_acceptance_evidence",
    ),
)


POLICIES: dict[str, dict[str, Any]] = {
    "website_visitors": {
        "definition_version": "website-marketing-v1",
        "cycle_requirements": [
            {
                "job_id": "reporting-v2-website-analytics-refresh",
                "times": ("06:02", "18:02"),
                "required": 2,
            }
        ],
        "required_periods": ("week", "28d", "90d"),
        "required_sample": 0,
        "guards": (
            "canonical_ga4_property",
            "exact_owned_host",
            "no_write_side_effects",
        ),
    },
    "website_subscribers_unique": {
        "definition_version": "website-marketing-v1",
        "cycle_requirements": [
            {
                "job_id": "reporting-v2-website-analytics-refresh",
                "times": ("06:02", "18:02"),
                "required": 2,
            }
        ],
        "required_periods": ("week", "28d", "90d"),
        "required_sample": 10,
        "guards": (
            "unique_contact_deduplication",
            "earliest_submission_authority",
            "no_write_side_effects",
        ),
    },
    "visitor_to_subscriber_rate": {
        "definition_version": "website-marketing-v1",
        "cycle_requirements": [
            {
                "job_id": "reporting-v2-website-analytics-refresh",
                "times": ("06:02", "18:02"),
                "required": 2,
            }
        ],
        "required_periods": ("week", "28d", "90d"),
        "required_sample": 10,
        "guards": (
            "canonical_ga4_property",
            "exact_owned_host",
            "unique_contact_deduplication",
            "no_write_side_effects",
        ),
    },
    "subscriber_to_sa_booking_rate": {
        "definition_version": "ghl-subscriber-sa-booking-v1",
        "cycle_requirements": [
            {
                "job_id": "reporting-v2-website-analytics-refresh",
                "times": ("06:02", "18:02"),
                "required": 2,
            },
            {
                "job_id": "reporting-v2-ghl-acquisition-refresh",
                "times": ("06:18", "18:18"),
                "required": 2,
            },
        ],
        "required_periods": ("week", "28d", "90d"),
        "required_sample": 10,
        "guards": (
            "unique_contact_deduplication",
            "earliest_submission_authority",
            "appointment_date_added_authority",
            "bounded_30_day_booking_window",
            "no_write_side_effects",
        ),
    },
    "sa_show_rate": {
        "definition_version": "sa-attendance-v2",
        "cycle_requirements": [
            {
                "job_id": "sa-attendance-refresh",
                "times": ("06:10", "18:10"),
                "required": 2,
            }
        ],
        "required_periods": ("week", "28d", "90d"),
        "required_sample": 20,
        "guards": (
            "exact_appointment_series_identity",
            "zero_outcome_inference",
            "cancelled_excluded_from_show_rate",
            "no_ghl_or_kpi_write",
        ),
    },
    "assessment_conversion_unique": {
        "definition_version": "assessment-conversion-v1",
        "cycle_requirements": [
            {
                "job_id": "sa-attendance-refresh",
                "times": ("06:10", "18:10"),
                "required": 2,
            },
            {
                "job_id": "reporting-v2-ghl-acquisition-refresh",
                "times": ("06:18", "18:18"),
                "required": 2,
            },
        ],
        "required_periods": ("week", "28d", "90d"),
        "required_sample": 20,
        "guards": (
            "exact_appointment_series_identity",
            "zero_outcome_inference",
            "one_sale_per_assessment_series",
            "fast_track_not_double_counted",
            "no_ghl_or_kpi_write",
        ),
    },
    "cash_goal_progress": {
        "definition_version": "cash-goal-v1",
        "cycle_requirements": [
            {
                "job_id": "reporting-v2-cash-refresh",
                "times": ("06:20", "18:20"),
                "required": 2,
            }
        ],
        "required_periods": ("rolling_365d",),
        "required_sample": 20,
        "guards": (
            "settled_cash_and_refunds_only",
            "processor_event_identity_exact",
            "gst_excluded",
            "xero_income_excluded_from_cash",
            "no_kpi_or_dashboard_write",
        ),
    },
    "operating_expenses": {
        "definition_version": "operating-expenses-v2",
        "cycle_requirements": [
            {
                "job_id": "reporting-v2-xero-accounting-refresh",
                "times": ("06:24", "18:24"),
                "required": 2,
            }
        ],
        "required_periods": ("week", "28d", "90d"),
        "required_sample": 0,
        "guards": (
            "profit_and_loss_expenses_only",
            "transfers_and_repayments_excluded",
            "expense_categories_reconcile",
            "xero_income_excluded_from_cash",
            "no_kpi_or_dashboard_write",
        ),
    },
    "cash_accounting_validation": {
        "definition_version": "cash-accounting-validation-v1",
        "cycle_requirements": [
            {
                "job_id": "reporting-v2-cash-refresh",
                "times": ("06:20", "18:20"),
                "required": 2,
            },
            {
                "job_id": "reporting-v2-xero-accounting-refresh",
                "times": ("06:24", "18:24"),
                "required": 2,
            },
        ],
        "required_periods": ("week", "28d", "90d"),
        "required_sample": 0,
        "guards": (
            "same_completed_period",
            "material_difference_classified",
            "xero_income_validation_only",
            "cash_goal_unchanged",
            "no_kpi_or_dashboard_write",
        ),
    },
    "sgpt_delivery": {
        "definition_version": "sgpt-delivery-v1",
        "cycle_requirements": [],
        "external_cycle_requirements": [
            {"source": "trainerize_performance", "required": 2}
        ],
        "required_periods": ("week", "28d", "90d"),
        "required_sample": 20,
        "guards": (
            "complete_fresh_source",
            "exact_identity_set_reconciliation",
            "zero_outcome_inference",
            "timetable_assignment_coverage",
            "no_kpi_or_dashboard_write",
        ),
    },
    "evolved_standards": {
        "definition_version": "evolved-standards-v1-shadow",
        "acceptance_rule_version": (
            "evolved-standards-future-proofing-score-v1"
        ),
        "cycle_requirements": [],
        "external_cycle_requirements": [
            {"source": "trainerize_performance", "required": 2}
        ],
        "required_periods": (
            "component_evidence",
            "insufficiency_cases",
            "transition_sample",
            "time_to_standard_sample",
            "future_proofing_score_sample",
            "future_proofing_score_insufficiency",
        ),
        "required_sample": 20,
        "guards": (
            "exact_alias_only",
            "right_left_independent",
            "combined_side_fails_closed",
            "missing_duration_load_bodyweight_fails_closed",
            "unresolved_identity_or_start_fails_closed",
            "stale_or_incomplete_evidence_fails_closed",
            "component_evidence_traceable",
            "rankings_milestones_standards_separate",
            "canonical_six_standard_source_sufficiency",
            "all_six_standards_sufficient_for_score",
            "no_invented_overall_live_long_perform_label",
            "individual_standard_levels_preserved",
            "future_proofing_score_range_0_18",
            "future_proofing_band_canonical",
            "split_squat_weaker_sufficient_side_governs",
            "split_squat_asymmetry_retained",
            "missing_or_ambiguous_evidence_fails_closed",
            "no_kpi_or_dashboard_write",
        ),
    },
    "consumer_retention_intelligence_contract": {
        "definition_version": "retention-hub-read-v1",
        "cycle_requirements": [],
        "required_periods": ("contract",),
        "required_sample": 0,
        "required_comparison_cycles": 2,
        "exact_consumer_contract": True,
        "guards": (
            "fresh_complete_hub_sources",
            "exact_identity_fingerprints",
            "exact_classification_fingerprints",
            "zero_set_differences",
            "legacy_fallback_protected",
        ),
    },
    "consumer_conversation_triage_contract": {
        "definition_version": "conversation-triage-hub-read-v1",
        "cycle_requirements": [],
        "required_periods": ("contract",),
        "required_sample": 0,
        "required_comparison_cycles": 2,
        "exact_consumer_contract": True,
        "guards": (
            "fresh_complete_hub_sources",
            "exact_identity_fingerprints",
            "exact_classification_fingerprints",
            "zero_set_differences",
            "legacy_fallback_protected",
        ),
    },
    "consumer_pt_booking_continuity_contract": {
        "definition_version": "pt-booking-hub-read-v1",
        "cycle_requirements": [],
        "required_periods": ("contract",),
        "required_sample": 0,
        "required_comparison_cycles": 2,
        "exact_consumer_contract": True,
        "guards": (
            "fresh_complete_hub_sources",
            "exact_identity_fingerprints",
            "exact_classification_fingerprints",
            "zero_set_differences",
            "legacy_fallback_protected",
        ),
    },
    "consumer_revenue_control_contract": {
        "definition_version": "revenue-control-hub-read-v1",
        "cycle_requirements": [],
        "required_periods": ("contract",),
        "required_sample": 0,
        "required_comparison_cycles": 2,
        "exact_consumer_contract": True,
        "guards": (
            "fresh_complete_hub_sources",
            "exact_identity_fingerprints",
            "exact_classification_fingerprints",
            "zero_set_differences",
            "legacy_fallback_protected",
        ),
    },
}

for _policy in POLICIES.values():
    _policy.setdefault("external_cycle_requirements", [])
    _policy.setdefault("required_comparison_cycles", 2)
    _policy.setdefault("exact_consumer_contract", False)


def _datetime(value: datetime | str | None, field: str) -> datetime | None:
    if value is None:
        return None
    parsed = value
    if isinstance(value, str):
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if not isinstance(parsed, datetime) or parsed.tzinfo is None:
        raise ValueError(f"{field} must include a timezone")
    return parsed.astimezone(UTC)


def _scheduled_time(value: str) -> time:
    hour, minute = str(value).split(":", 1)
    return time(int(hour), int(minute), tzinfo=BRISBANE_TZ)


def _near_scheduled_time(started_at: datetime, values: Iterable[str]) -> bool:
    if started_at.tzinfo is None:
        started_at = started_at.replace(tzinfo=UTC)
    local = started_at.astimezone(BRISBANE_TZ)
    for value in values:
        scheduled = datetime.combine(
            local.date(), _scheduled_time(value)
        )
        if timedelta(0) <= local - scheduled <= timedelta(minutes=10):
            return True
    return False


def _safe_sample(sample: dict[str, Any], required: int) -> dict[str, Any]:
    allowed = {
        "sampled",
        "exact_matches",
        "unexplained_mismatches",
        "selection_method",
        "sample_fingerprint",
        "entity_grain",
    }
    unexpected = set(sample) - allowed
    if unexpected:
        raise ValueError(
            "identity sample must contain aggregate evidence only; "
            f"remove {', '.join(sorted(unexpected))}"
        )
    sampled = int(sample.get("sampled") or 0)
    exact_matches = int(sample.get("exact_matches") or 0)
    mismatches = int(sample.get("unexplained_mismatches") or 0)
    if sampled < 0 or exact_matches < 0 or mismatches < 0:
        raise ValueError("identity sample counts cannot be negative")
    if exact_matches + mismatches > sampled:
        raise ValueError("identity sample counts exceed sampled cases")
    sample_fingerprint = str(sample.get("sample_fingerprint") or "").strip()
    if sampled and not sample_fingerprint:
        raise ValueError(
            "sample_fingerprint is required without retaining identities"
        )
    return {
        "required": required,
        "sampled": sampled,
        "exact_matches": exact_matches,
        "unexplained_mismatches": mismatches,
        "selection_method": str(
            sample.get("selection_method") or "deterministic_hash"
        ),
        "sample_fingerprint": sample_fingerprint or None,
        "entity_grain": str(sample.get("entity_grain") or "source identity"),
        "passed": bool(
            sampled >= required
            and exact_matches == sampled
            and mismatches == 0
        ),
    }


class MetricAcceptanceController:
    def __init__(self, engine):
        self.engine = engine
        acceptance_metadata.create_all(engine)

    def _scheduled_cycles(
        self,
        requirement: dict[str, Any],
        *,
        window_start: datetime,
        as_of: datetime,
    ) -> dict[str, Any]:
        with self.engine.begin() as connection:
            rows = connection.execute(
                select(job_runs)
                .where(
                    job_runs.c.job_id == requirement["job_id"],
                    job_runs.c.started_at >= window_start,
                    job_runs.c.started_at <= as_of,
                )
                .order_by(job_runs.c.started_at.desc())
            ).mappings().all()
        matched = [
            row
            for row in rows
            if row["status"] == "complete"
            and row["completed_at"] is not None
            and _near_scheduled_time(
                row["started_at"], requirement["times"]
            )
        ]
        distinct = []
        seen_slots = set()
        for row in matched:
            started_at = row["started_at"]
            if started_at.tzinfo is None:
                started_at = started_at.replace(tzinfo=UTC)
            local = started_at.astimezone(BRISBANE_TZ)
            slot = min(
                requirement["times"],
                key=lambda value: abs(
                    (
                        local
                        - datetime.combine(
                            local.date(), _scheduled_time(value)
                        )
                    ).total_seconds()
                ),
            )
            slot_key = f"{local.date().isoformat()}T{slot}"
            if slot_key in seen_slots:
                continue
            seen_slots.add(slot_key)
            distinct.append(
                {
                    "run_id": row["run_id"],
                    "slot": slot_key,
                    "started_at": started_at.isoformat(),
                    "completed_at": (
                        row["completed_at"].replace(tzinfo=UTC).isoformat()
                        if row["completed_at"].tzinfo is None
                        else row["completed_at"].isoformat()
                    ),
                }
            )
        required = int(requirement["required"])
        return {
            "job_id": requirement["job_id"],
            "required": required,
            "completed": len(distinct),
            "passed": len(distinct) >= required,
            "cycles": distinct[:required],
        }

    def record(
        self,
        payload: dict[str, Any],
        *,
        as_of: datetime | str | None = None,
    ) -> dict[str, Any]:
        metric_id = str(payload.get("metric_id") or "").strip()
        policy = POLICIES.get(metric_id)
        if not policy:
            raise ValueError("metric does not have an acceptance policy")
        definition_version = str(
            payload.get("definition_version") or ""
        ).strip()
        if definition_version != policy["definition_version"]:
            raise ValueError(
                "definition_version does not match the acceptance policy"
            )
        evaluated_at = _datetime(as_of or datetime.now(UTC), "as_of")
        assert evaluated_at is not None
        window_start = _datetime(
            payload.get("cycle_window_start"), "cycle_window_start"
        ) or evaluated_at - timedelta(days=8)
        observation_not_before = _datetime(
            payload.get("observation_not_before"),
            "observation_not_before",
        )

        cycle_results = [
            self._scheduled_cycles(
                requirement,
                window_start=window_start,
                as_of=evaluated_at,
            )
            for requirement in policy["cycle_requirements"]
        ]
        external_cycles = payload.get("external_cycles") or []
        external_cycle_results = []
        for requirement in policy["external_cycle_requirements"]:
            rows = [
                row
                for row in external_cycles
                if str(row.get("source") or "") == requirement["source"]
                and bool(row.get("complete"))
                and str(row.get("status") or "").lower()
                in {"complete", "accepted"}
                and str(row.get("run_id") or "").strip()
            ]
            distinct_run_ids = sorted(
                {str(row["run_id"]).strip() for row in rows}
            )
            required = int(requirement["required"])
            external_cycle_results.append(
                {
                    "source": requirement["source"],
                    "required": required,
                    "completed": len(distinct_run_ids),
                    "passed": len(distinct_run_ids) >= required,
                    "run_ids": distinct_run_ids[:required],
                }
            )
        required_cycles = sum(
            int(row["required"]) for row in cycle_results
        ) + sum(int(row["required"]) for row in external_cycle_results)
        completed_cycles = sum(
            min(int(row["completed"]), int(row["required"]))
            for row in cycle_results
        ) + sum(
            min(int(row["completed"]), int(row["required"]))
            for row in external_cycle_results
        )
        cycles_passed = all(
            row["passed"]
            for row in cycle_results + external_cycle_results
        )

        freshness = []
        for row in payload.get("freshness") or []:
            age_hours = float(row.get("age_hours"))
            max_age_hours = float(row.get("max_age_hours"))
            complete = bool(row.get("complete"))
            freshness.append(
                {
                    "source": str(row.get("source") or "").strip(),
                    "age_hours": age_hours,
                    "max_age_hours": max_age_hours,
                    "complete": complete,
                    "passed": complete and age_hours <= max_age_hours,
                }
            )
        freshness_passed = bool(freshness) and all(
            row["passed"] for row in freshness
        )

        sample = _safe_sample(
            payload.get("identity_sample") or {},
            int(policy["required_sample"]),
        )
        comparisons = payload.get("comparisons") or []
        required_periods = set(policy["required_periods"])
        required_comparison_cycles = int(
            policy["required_comparison_cycles"]
        )
        comparison_cycle_ids_by_period: dict[str, set[str]] = {
            period_id: set() for period_id in required_periods
        }
        comparison_source_run_ids_by_period: dict[str, set[str]] = {
            period_id: set() for period_id in required_periods
        }
        comparison_rows_valid = True
        comparison_contract_valid = True
        for row in comparisons:
            period_id = str(row.get("period_id") or "")
            if period_id not in required_periods:
                continue
            comparison_cycle_id = str(
                row.get("comparison_cycle_id") or ""
            ).strip()
            source_run_id = str(row.get("source_run_id") or "").strip()
            if not comparison_cycle_id or not source_run_id:
                comparison_rows_valid = False
            else:
                comparison_cycle_ids_by_period[period_id].add(
                    comparison_cycle_id
                )
                comparison_source_run_ids_by_period[period_id].add(
                    source_run_id
                )
            comparison_rows_valid = bool(
                comparison_rows_valid
                and row.get("classification") in EXPLAINABLE_DIFFERENCES
                and int(row.get("unexplained_event_count") or 0) == 0
                and int(row.get("unexplained_cents") or 0) == 0
            )
            if policy["exact_consumer_contract"]:
                legacy_identity = str(
                    row.get("legacy_identity_fingerprint") or ""
                ).strip()
                hub_identity = str(
                    row.get("hub_identity_fingerprint") or ""
                ).strip()
                legacy_classification = str(
                    row.get("legacy_classification_fingerprint") or ""
                ).strip()
                hub_classification = str(
                    row.get("hub_classification_fingerprint") or ""
                ).strip()
                comparison_contract_valid = bool(
                    comparison_contract_valid
                    and legacy_identity
                    and legacy_identity == hub_identity
                    and legacy_classification
                    and legacy_classification == hub_classification
                    and int(row.get("legacy_only_count") or 0) == 0
                    and int(row.get("hub_only_count") or 0) == 0
                    and bool(row.get("hub_source_complete"))
                    and bool(row.get("hub_source_fresh"))
                )
        comparison_periods = {
            period_id
            for period_id, cycle_ids in comparison_cycle_ids_by_period.items()
            if cycle_ids
        }
        completed_comparison_cycles = min(
            (
                min(
                    len(comparison_cycle_ids_by_period[period_id]),
                    len(comparison_source_run_ids_by_period[period_id]),
                )
                for period_id in required_periods
            ),
            default=0,
        )
        comparisons_passed = bool(
            comparisons
            and comparison_rows_valid
            and comparison_contract_valid
            and completed_comparison_cycles
            >= required_comparison_cycles
        )
        if not cycle_results and not external_cycle_results:
            required_cycles = required_comparison_cycles
            completed_cycles = min(
                completed_comparison_cycles,
                required_comparison_cycles,
            )
            cycles_passed = comparisons_passed
        unexplained_events = sum(
            int(row.get("unexplained_event_count") or 0)
            for row in comparisons
        )
        unexplained_cents = sum(
            int(row.get("unexplained_cents") or 0)
            for row in comparisons
        )

        supplied_guards = payload.get("domain_guards") or {}
        guard_results = {
            name: bool(supplied_guards.get(name))
            for name in policy["guards"]
        }
        guards_passed = all(guard_results.values())
        observation_elapsed = bool(
            observation_not_before is None
            or evaluated_at >= observation_not_before
        )
        technical_passed = bool(
            cycles_passed
            and freshness_passed
            and sample["passed"]
            and comparisons_passed
            and guards_passed
            and observation_elapsed
        )

        owner = payload.get("owner_approval") or {}
        owner_approved = bool(
            owner.get("approved") is True
            and str(owner.get("approved_by") or "").strip().lower()
            == "peter brown"
            and str(owner.get("metric_id") or "").strip() == metric_id
            and str(owner.get("definition_version") or "").strip()
            == definition_version
            and str(owner.get("rule_reference") or "").strip()
        )
        owner_state = "approved_exact_rule" if owner_approved else "pending"
        owner_reference = (
            str(owner.get("rule_reference")).strip()
            if owner_approved
            else None
        )

        hard_failure = bool(
            sample["unexplained_mismatches"]
            or unexplained_events
            or unexplained_cents
            or (
                policy["exact_consumer_contract"]
                and comparisons
                and not comparison_contract_valid
            )
            or any(value is False for value in guard_results.values())
            or any(
                row.get("classification") not in EXPLAINABLE_DIFFERENCES
                for row in comparisons
            )
        )
        if hard_failure:
            state = "blocked"
            recommendation = (
                "Keep this metric in shadow. Resolve the exact failed gate "
                "or unexplained difference, then record a new evidence run."
            )
        elif not technical_passed:
            state = "collecting"
            recommendation = (
                "Keep this metric in shadow until the bounded scheduled "
                "observation, freshness, sample and comparison gates finish."
            )
        elif not owner_approved:
            state = "ready_for_owner_acceptance"
            recommendation = (
                "Technical gates pass. Peter may accept this exact metric "
                "definition; promotion remains a separate controlled action."
            )
        else:
            state = "owner_accepted"
            recommendation = (
                "Peter accepted this exact metric definition. It is eligible "
                "for the separate publication registry, but this evidence "
                "record does not publish or change legacy reporting."
            )
        assert state in ACCEPTANCE_STATES

        gate_results = {
            "scheduled_cycles": cycle_results,
            "external_cycles": external_cycle_results,
            "freshness": freshness,
            "freshness_passed": freshness_passed,
            "identity_sample": sample,
            "required_periods": sorted(required_periods),
            "comparison_periods": sorted(comparison_periods),
            "required_comparison_cycles": required_comparison_cycles,
            "completed_comparison_cycles": completed_comparison_cycles,
            "exact_consumer_contract": bool(
                policy["exact_consumer_contract"]
            ),
            "comparisons_passed": comparisons_passed,
            "unexplained_event_count": unexplained_events,
            "unexplained_cents": unexplained_cents,
            "domain_guards": guard_results,
            "observation_elapsed": observation_elapsed,
        }
        acceptance_rule_version = policy.get("acceptance_rule_version")
        if acceptance_rule_version:
            gate_results["acceptance_rule_version"] = str(
                acceptance_rule_version
            )
        evidence = {
            "cycle_window_start": window_start.isoformat(),
            "comparison_evidence": [
                {
                    "period_id": str(row.get("period_id") or ""),
                    "comparison_cycle_id": str(
                        row.get("comparison_cycle_id") or ""
                    )
                    or None,
                    "source_run_id": str(row.get("source_run_id") or "")
                    or None,
                    "classification": row.get("classification"),
                    "unexplained_event_count": int(
                        row.get("unexplained_event_count") or 0
                    ),
                    "unexplained_cents": int(
                        row.get("unexplained_cents") or 0
                    ),
                    "evidence_reference": str(
                        row.get("evidence_reference") or ""
                    )
                    or None,
                    "legacy_identity_fingerprint": str(
                        row.get("legacy_identity_fingerprint") or ""
                    )
                    or None,
                    "hub_identity_fingerprint": str(
                        row.get("hub_identity_fingerprint") or ""
                    )
                    or None,
                    "legacy_classification_fingerprint": str(
                        row.get("legacy_classification_fingerprint") or ""
                    )
                    or None,
                    "hub_classification_fingerprint": str(
                        row.get("hub_classification_fingerprint") or ""
                    )
                    or None,
                    "legacy_only_count": int(
                        row.get("legacy_only_count") or 0
                    ),
                    "hub_only_count": int(row.get("hub_only_count") or 0),
                }
                for row in comparisons
            ],
            "publication_impact": "none",
            "legacy_reporting_unchanged": True,
            "xero_income_can_be_cash": False,
        }
        material = {
            "metric_id": metric_id,
            "definition_version": definition_version,
            "gate_version": GATE_VERSION,
            "acceptance_state": state,
            "owner_approval_state": owner_state,
            "owner_approval_reference": owner_reference,
            "observation_not_before": (
                observation_not_before.isoformat()
                if observation_not_before
                else None
            ),
            "gate_results": gate_results,
            "evidence": evidence,
        }
        record_fingerprint = fingerprint(material)
        record_id = uuid.uuid5(
            uuid.NAMESPACE_URL,
            f"metric-acceptance:{metric_id}:{definition_version}:"
            f"{record_fingerprint}",
        ).hex
        values = {
            "acceptance_record_id": record_id,
            "metric_id": metric_id,
            "definition_version": definition_version,
            "gate_version": GATE_VERSION,
            "acceptance_state": state,
            "technical_gates_passed": int(technical_passed),
            "owner_approval_state": owner_state,
            "owner_approval_reference": owner_reference,
            "publication_state": "shadow",
            "promotion_authorised": 0,
            "required_scheduled_cycles": required_cycles,
            "completed_scheduled_cycles": completed_cycles,
            "observation_not_before": observation_not_before,
            "recommendation": recommendation,
            "gate_results_json": canonical_json(gate_results),
            "evidence_json": canonical_json(evidence),
            "acceptance_fingerprint": record_fingerprint,
            "recorded_at": evaluated_at,
        }
        with self.engine.begin() as connection:
            existing = connection.execute(
                select(
                    metric_acceptance_evidence.c.acceptance_record_id
                ).where(
                    metric_acceptance_evidence.c.acceptance_record_id
                    == record_id
                )
            ).scalar()
            if not existing:
                connection.execute(
                    insert(metric_acceptance_evidence).values(**values)
                )
        return {
            "status": "duplicate" if existing else "recorded",
            "acceptance_record_id": record_id,
            "acceptance_fingerprint": record_fingerprint,
            "metric_id": metric_id,
            "definition_version": definition_version,
            "acceptance_state": state,
            "technical_gates_passed": technical_passed,
            "owner_approval_state": owner_state,
            "publication_state": "shadow",
            "promotion_authorised": False,
            "required_scheduled_cycles": required_cycles,
            "completed_scheduled_cycles": completed_cycles,
            "observation_not_before": (
                observation_not_before.isoformat()
                if observation_not_before
                else None
            ),
            "recommendation": recommendation,
            "gate_results": gate_results,
        }

    def latest(self, metric_id: str | None = None) -> list[dict[str, Any]]:
        query = select(metric_acceptance_evidence)
        if metric_id:
            query = query.where(
                metric_acceptance_evidence.c.metric_id == metric_id
            )
        query = query.order_by(
            metric_acceptance_evidence.c.recorded_at.desc()
        )
        with self.engine.begin() as connection:
            rows = connection.execute(query).mappings().all()
        latest_by_metric: dict[str, Any] = {}
        for row in rows:
            latest_by_metric.setdefault(str(row["metric_id"]), row)
        return [
            {
                "acceptance_record_id": row["acceptance_record_id"],
                "acceptance_fingerprint": row[
                    "acceptance_fingerprint"
                ],
                "metric_id": row["metric_id"],
                "definition_version": row["definition_version"],
                "gate_version": row["gate_version"],
                "acceptance_state": row["acceptance_state"],
                "technical_gates_passed": bool(
                    row["technical_gates_passed"]
                ),
                "owner_approval_state": row["owner_approval_state"],
                "owner_approval_reference": row[
                    "owner_approval_reference"
                ],
                "publication_state": row["publication_state"],
                "promotion_authorised": bool(
                    row["promotion_authorised"]
                ),
                "required_scheduled_cycles": row[
                    "required_scheduled_cycles"
                ],
                "completed_scheduled_cycles": row[
                    "completed_scheduled_cycles"
                ],
                "observation_not_before": (
                    row["observation_not_before"].isoformat()
                    if row["observation_not_before"]
                    else None
                ),
                "recommendation": row["recommendation"],
                "gate_results": json.loads(row["gate_results_json"]),
                "evidence": json.loads(row["evidence_json"]),
                "recorded_at": row["recorded_at"].isoformat(),
            }
            for row in latest_by_metric.values()
        ]
