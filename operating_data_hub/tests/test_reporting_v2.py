from datetime import UTC, datetime

import pytest
from sqlalchemy import func, select

from operating_data_hub.reporting_v2 import (
    ReportingV2Repository,
    attribute_sales_to_assessments,
    completed_reporting_periods,
    metric_lineage,
    metric_observations,
    metric_publication_decisions,
    sale_service_components,
    source_events,
    rolling_cash_goal_window,
    summarise_unique_conversion,
)
from operating_data_hub.reporting_v2_board_pack import (
    board_pack_contract,
    build_board_pack_rows,
    validate_manual_input_sheet_row,
)
from operating_data_hub.reporting_v2_migration import (
    build_raw_workbook_record,
    classify_historical_confidence,
    summarise_backfill_confidence,
)
from operating_data_hub.store import HubStore


def repository(tmp_path):
    store = HubStore(f"sqlite:///{tmp_path / 'hub.db'}")
    return ReportingV2Repository(store.engine)


def source_event(*, status="showed", observed_at=None):
    return {
        "source_system": "ghl",
        "source_object_type": "strength_assessment_appointment",
        "source_event_id": "appointment-1",
        "source_object_id": "appointment-1",
        "occurred_at": "2026-10-04T14:30:00+00:00",
        "observed_at": observed_at or "2026-10-04T15:30:00+00:00",
        "acceptance_state": "accepted",
        "confidence": "verified",
        "payload": {
            "appointment_id": "appointment-1",
            "status": status,
        },
    }


def test_source_event_is_idempotent_and_versions_material_changes(tmp_path):
    repo = repository(tmp_path)

    first = repo.accept_source_event(source_event())
    duplicate = repo.accept_source_event(source_event())
    changed = repo.accept_source_event(source_event(status="no_show"))

    assert first["status"] == "accepted"
    assert duplicate["status"] == "duplicate"
    assert changed["status"] == "accepted"
    assert changed["event_version_id"] != first["event_version_id"]
    assert changed["supersedes_event_version_id"] == first[
        "event_version_id"
    ]
    with repo.engine.begin() as connection:
        count = connection.execute(
            select(func.count()).select_from(source_events)
        ).scalar_one()
    assert count == 2


def test_source_event_uses_brisbane_date_not_sydney_daylight_rules(tmp_path):
    repo = repository(tmp_path)

    result = repo.accept_source_event(source_event())

    # 14:30 UTC is 00:30 on 5 October in Brisbane. The workbook's Sydney
    # timezone would interpret the same instant as 01:30 during DST.
    assert result["brisbane_local_date"] == "2026-10-05"


def test_completed_periods_share_one_brisbane_reporting_calendar():
    periods = completed_reporting_periods(
        "2026-07-29T01:00:00+00:00"
    )

    assert tuple(
        value.isoformat() for value in periods["week"]
    ) == ("2026-07-20", "2026-07-26")
    assert tuple(
        value.isoformat() for value in periods["28d"]
    ) == ("2026-07-01", "2026-07-28")
    assert tuple(
        value.isoformat() for value in periods["90d"]
    ) == ("2026-04-30", "2026-07-28")


def test_metric_definition_version_is_immutable(tmp_path):
    repo = repository(tmp_path)
    definition = {
        "metric_id": "test_metric",
        "definition_version": "v1",
        "plain_english_name": "Test",
        "decision_question": "Does it work?",
        "event_grain": "one event",
        "source_authority": {"source": "test"},
        "numerator_definition": "accepted events",
        "denominator_definition": None,
        "inclusion_rules": [],
        "exclusion_rules": [],
        "period_semantics": "Brisbane local day",
        "minimum_freshness": {},
        "owner": "Peter Brown",
        "approval_state": "shadow",
    }
    repo.register_metric_definition(definition)

    with pytest.raises(ValueError, match="immutable"):
        repo.register_metric_definition(
            {**definition, "plain_english_name": "Changed in place"}
        )


def test_cash_goal_definition_is_simple_and_excludes_gst(tmp_path):
    repo = repository(tmp_path)
    definition = next(
        row
        for row in repo.definitions()
        if row["metric_id"] == "cash_goal_progress"
    )

    assert definition["definition_version"] == "cash-goal-v1"
    assert "GST" in definition["exclusion_rules"]
    assert "100000000" in definition["denominator_definition"]
    assert definition["approval_state"] == "approved_shadow"
    assert "rolling 365-day" in definition["period_semantics"]


def test_cash_goal_window_rolls_without_calendar_reset():
    start, end = rolling_cash_goal_window(
        "2026-07-29T02:00:00+00:00"
    )

    assert end.isoformat() == "2026-07-29T02:00:00+00:00"
    assert start.isoformat() == "2025-07-29T02:00:00+00:00"


def test_ceo_scorecard_preview_is_gated_and_uses_one_period(tmp_path):
    repo = repository(tmp_path)
    result = repo.ceo_scorecard_preview(
        "28d", as_of="2026-07-30T00:00:00+00:00"
    )

    assert result["mode"] == "shadow"
    assert result["publication_impact"] == "none"
    assert result["period"] == {
        "id": "28d",
        "label": "Last 28 completed days",
        "start": "2026-07-02",
        "end": "2026-07-29",
        "timezone": "Australia/Brisbane",
    }
    assert result["acceptance"]["cutover_authorised"] is False
    assert result["acceptance"]["legacy_reporting_unchanged"] is True
    assert result["acceptance"]["all_metrics_ready"] is False
    assert all(
        row["blocked_reason"] for row in result["metrics"]
    )
    assert result["cash_goal"]["available"] is False


def test_ceo_scorecard_preview_rejects_arbitrary_period(tmp_path):
    repo = repository(tmp_path)
    with pytest.raises(
        ValueError, match="period must be week, 28d or 90d"
    ):
        repo.ceo_scorecard_preview("month")


def test_cash_goal_stays_unavailable_until_required_sources_are_complete(
    tmp_path,
):
    repo = repository(tmp_path)
    stripe = repo.record_cash_batch_shadow(
        {
            "source_system": "stripe",
            "source_run_id": "stripe-cash-1",
            "observed_at": "2026-07-30T12:00:00+00:00",
            "complete": True,
            "events": [
                {
                    "source_event_id": "in_1",
                    "occurred_at": "2026-07-29T01:00:00+00:00",
                    "event_type": "settled_cash",
                    "gross_amount_cents": 11000,
                    "gst_amount_cents": 1000,
                }
            ],
        }
    )

    assert stripe["cash_goal"]["available"] is False
    assert any(
        "pt_minder" in reason
        for reason in stripe["cash_goal"]["blocked_reasons"]
    )


def test_cash_goal_deduplicates_events_and_nets_refunds_excluding_gst(
    tmp_path,
):
    repo = repository(tmp_path)
    stripe_payload = {
        "source_system": "stripe",
        "source_run_id": "stripe-cash-1",
        "observed_at": "2026-07-30T12:00:00+00:00",
        "complete": True,
        "events": [
            {
                "source_event_id": "in_1",
                "occurred_at": "2026-07-29T01:00:00+00:00",
                "event_type": "settled_cash",
                "gross_amount_cents": 11000,
                "gst_amount_cents": 1000,
            },
            {
                "source_event_id": "re_1",
                "occurred_at": "2026-07-30T01:00:00+00:00",
                "event_type": "refund",
                "gross_amount_cents": 2200,
                "gst_amount_cents": 200,
            },
        ],
    }
    repo.record_cash_batch_shadow(stripe_payload)
    duplicate = repo.record_cash_batch_shadow(stripe_payload)
    result = repo.record_cash_batch_shadow(
        {
            "source_system": "pt_minder",
            "source_run_id": "ptm-cash-1",
            "observed_at": "2026-07-30T12:00:00+00:00",
            "complete": True,
            "events": [
                {
                    "source_event_id": "debit_1",
                    "occurred_at": "2026-07-28T01:00:00+00:00",
                    "event_type": "settled_cash",
                    "gross_amount_cents": 9900,
                    "gst_amount_cents": 900,
                }
            ],
        }
    )

    assert duplicate["status"] == "duplicate"
    assert result["cash_goal"]["available"] is True
    assert result["cash_goal"]["event_count"] == 3
    assert result["cash_goal"]["net_cash_ex_gst_cents"] == 17000
    period_cash = repo.cash_period_summary(
        "2026-07-28",
        "2026-07-30",
        as_of="2026-07-30T12:00:00+00:00",
    )
    assert period_cash["available"] is True
    assert period_cash["event_count"] == 3
    assert period_cash["net_cash_ex_gst_cents"] == 17000
    preview = repo.ceo_scorecard_preview(
        "28d", as_of="2026-07-30T12:00:00+00:00"
    )
    assert preview["cash_goal"]["available"] is True
    assert preview["cash_goal"]["observation"]["numerator"] == "17000"
    assert preview["cash_goal"]["observation"]["denominator"] == "100000000"


def test_cash_goal_preview_prefers_latest_fresh_observation_after_ptm_replay(
    tmp_path,
):
    repo = repository(tmp_path)
    first_observed = "2026-07-30T12:00:00+00:00"
    stripe_event = {
        "source_event_id": "pi_1:settled",
        "occurred_at": "2026-07-29T01:00:00+00:00",
        "event_type": "settled_cash",
        "gross_amount_cents": 11000,
        "gst_amount_cents": 1000,
    }
    pt_event = {
        "source_event_id": "debit_1",
        "occurred_at": "2026-07-28T01:00:00+00:00",
        "event_type": "settled_cash",
        "gross_amount_cents": 9900,
        "gst_amount_cents": 900,
    }
    pt_payload = {
        "source_system": "pt_minder",
        "source_run_id": "ptm-cash-1",
        "observed_at": first_observed,
        "complete": True,
        "events": [pt_event],
    }
    repo.record_cash_batch_shadow(pt_payload)
    repo.record_cash_batch_shadow(
        {
            "source_system": "stripe",
            "source_run_id": "stripe-cash-1",
            "observed_at": first_observed,
            "complete": True,
            "events": [stripe_event],
        }
    )

    repo.record_cash_batch_shadow(pt_payload)
    repo.record_cash_batch_shadow(
        {
            "source_system": "stripe",
            "source_run_id": "stripe-cash-2",
            "observed_at": "2026-07-30T13:00:00+00:00",
            "complete": True,
            "events": [stripe_event],
        }
    )
    preview = repo.ceo_scorecard_preview(
        "week",
        as_of="2026-07-30T13:00:00+00:00",
    )

    assert preview["cash_goal"]["available"] is True
    assert preview["cash_goal"]["observation"]["numerator"] == "19000"
    assert preview["cash_goal"]["observation"][
        "unavailable_reason"
    ] is None


def test_cash_batch_rejects_implicit_gst_and_unapproved_bank_cash(
    tmp_path,
):
    repo = repository(tmp_path)
    with pytest.raises(ValueError, match="amounts must be integer cents"):
        repo.record_cash_batch_shadow(
            {
                "source_system": "stripe",
                "source_run_id": "stripe-cash-bad",
                "observed_at": "2026-07-30T12:00:00+00:00",
                "complete": True,
                "events": [
                    {
                        "source_event_id": "in_bad",
                        "occurred_at": "2026-07-29T01:00:00+00:00",
                        "event_type": "settled_cash",
                        "gross_amount_cents": 11000,
                    }
                ],
            }
        )
    with pytest.raises(ValueError, match="requires approved_by"):
        repo.record_cash_batch_shadow(
            {
                "source_system": "bank_manual",
                "source_run_id": "bank-cash-bad",
                "observed_at": "2026-07-30T12:00:00+00:00",
                "complete": True,
                "events": [
                    {
                        "source_event_id": "bank_bad",
                        "occurred_at": "2026-07-29T01:00:00+00:00",
                        "event_type": "settled_cash",
                        "gross_amount_cents": 11000,
                        "gst_amount_cents": 1000,
                    }
                ],
            }
        )


def test_fast_track_is_one_conversion_with_two_service_components():
    result = summarise_unique_conversion(
        [
            {
                "appointment_id": "appointment-1",
                "appointment_series_id": "series-1",
                "canonical_status": "showed",
            }
        ],
        [
            {
                "sale_id": "sale-fast-track",
                "qualifying_new_membership": True,
                "appointment_series_ids": ["series-1"],
                "service_components": [
                    {
                        "service_type": "sgpt",
                        "service_name": "Strength & Sculpt",
                    },
                    {
                        "service_type": "pt",
                        "service_name": "Fast Track PT",
                    },
                ],
            }
        ],
    )

    assert result["converted_appointment_series"] == 1
    assert result["conversion_rate"] == 1
    assert result["qualifying_sales"] == 1
    assert result["service_components"] == {"pt": 1, "sgpt": 1}


def test_sale_attributes_to_most_recent_attended_assessment_within_30_days():
    result = attribute_sales_to_assessments(
        [
            {
                "appointment_id": "older",
                "appointment_series_id": "series-older",
                "contact_id": "contact-1",
                "canonical_status": "showed",
                "end_at": "2026-06-20T02:00:00+00:00",
            },
            {
                "appointment_id": "recent-rebook",
                "appointment_series_id": "series-rebook",
                "contact_id": "contact-1",
                "canonical_status": "showed",
                "end_at": "2026-07-10T02:00:00+00:00",
            },
        ],
        [
            {
                "sale_id": "sale-1",
                "contact_id": "contact-1",
                "sold_at": "2026-07-20T02:00:00+00:00",
                "qualifying_new_membership": True,
            }
        ],
    )

    sale = result["sales"][0]
    assert sale["appointment_series_ids"] == ["series-rebook"]
    assert sale["attribution_state"] == "attributed"
    assert sale["attribution_evidence"]["window_days"] == 30


def test_date_only_agreement_can_attribute_to_later_same_day_assessment():
    result = attribute_sales_to_assessments(
        [
            {
                "appointment_id": "assessment-1",
                "contact_id": "contact-1",
                "canonical_status": "showed",
                "end_at": "2026-07-20T08:00:00+00:00",
            }
        ],
        [
            {
                "sale_id": "sale-1",
                "contact_id": "contact-1",
                "sold_at": "2026-07-20T02:00:00+00:00",
                "qualifying_new_membership": True,
                "evidence": {"date_precision": "date_only"},
            }
        ],
    )

    assert result["sales"][0]["attribution_state"] == "attributed"


def test_matched_feedback_is_delivery_evidence_for_shadow_conversion():
    attendance = {
        "appointment_id": "assessment-1",
        "contact_id": "contact-1",
        "canonical_status": "confirmed",
        "reconciliation_state": "feedback_closes_confirmed",
        "proposed_status": "showed",
        "feedback_submission_ids": ["feedback-1"],
        "end_at": "2026-07-20T01:00:00+00:00",
    }
    sale = {
        "sale_id": "sale-1",
        "contact_id": "contact-1",
        "sold_at": "2026-07-20T02:00:00+00:00",
        "qualifying_new_membership": True,
    }

    attributed = attribute_sales_to_assessments([attendance], [sale])
    assert attributed["sales"][0]["attribution_state"] == "attributed"
    summary = summarise_unique_conversion(
        [attendance],
        attributed["sales"],
    )
    assert summary["converted_appointment_series"] == 1


def test_matched_feedback_is_delivery_evidence_for_shadow_show_rate(
    tmp_path,
):
    repo = repository(tmp_path)
    attendance = {
        "appointment_id": "assessment-1",
        "contact_id": "contact-1",
        "canonical_status": "confirmed",
        "status": "confirmed",
        "reconciliation_state": "feedback_closes_confirmed",
        "proposed_status": "showed",
        "feedback_submission_ids": ["feedback-1"],
        "start_at": "2026-07-20T01:00:00+00:00",
        "end_at": "2026-07-20T01:45:00+00:00",
        "show_rate_eligible": True,
        "cancellation_rate_eligible": True,
        "attendance_confidence": "high",
    }

    result = repo.record_sa_attendance_shadow(
        [attendance],
        summary={
            "definition_version": "sa-attendance-v2",
            "tracked_showed": 0,
            "tracked_no_show": 0,
            "tracked_cancelled": 0,
            "unresolved": 0,
        },
        as_of="2026-07-31T00:00:00+00:00",
    )

    observation = result["period_metrics"]["week"]
    assert observation["status"] == "accepted"
    scorecard = repo.ceo_scorecard_preview(
        "week",
        as_of="2026-07-31T00:00:00+00:00",
    )
    show_rate = next(
        row
        for row in scorecard["metrics"]
        if row["metric_id"] == "sa_show_rate"
    )
    assert show_rate["numerator"] == "1"
    assert show_rate["denominator"] == "1"
    assert show_rate["value"] == "1.0"


def test_late_sale_after_no_sale_feedback_still_converts_original_series():
    result = attribute_sales_to_assessments(
        [
            {
                "appointment_id": "assessment-1",
                "contact_id": "contact-1",
                "canonical_status": "showed",
                "sales_outcome": "No Sale",
                "end_at": "2026-07-01T02:00:00+00:00",
            }
        ],
        [
            {
                "sale_id": "late-sale",
                "contact_id": "contact-1",
                "sold_at": "2026-07-25T02:00:00+00:00",
                "qualifying_new_membership": True,
            }
        ],
    )

    assert result["sales"][0]["appointment_series_ids"] == [
        "assessment-1"
    ]


def test_returning_former_member_is_reactivation_not_conversion():
    result = attribute_sales_to_assessments(
        [
            {
                "appointment_id": "assessment-1",
                "contact_id": "contact-1",
                "canonical_status": "showed",
                "end_at": "2026-07-10T02:00:00+00:00",
            }
        ],
        [
            {
                "sale_id": "return-sale",
                "contact_id": "contact-1",
                "sold_at": "2026-07-20T02:00:00+00:00",
                "qualifying_new_membership": True,
                "returning_former_member": True,
            }
        ],
    )

    sale = result["sales"][0]
    assert sale["appointment_series_ids"] == []
    assert sale["attribution_state"] == "reactivation_excluded"


def test_existing_member_pt_add_on_is_not_acquisition_conversion():
    result = summarise_unique_conversion(
        [
            {
                "appointment_id": "appointment-1",
                "canonical_status": "showed",
            }
        ],
        [
            {
                "sale_id": "pt-add-on",
                "qualifying_new_membership": False,
                "appointment_series_ids": ["appointment-1"],
                "service_components": [{"service_type": "pt"}],
            }
        ],
    )

    assert result["converted_appointment_series"] == 0
    assert result["qualifying_sales"] == 0
    assert result["service_components"] == {}


def test_sale_store_preserves_one_sale_and_distinct_service_mix(tmp_path):
    repo = repository(tmp_path)

    accepted = repo.record_sale(
        {
            "sale_id": "sale-1",
            "source_system": "ghl",
            "source_sale_id": "agreement-1",
            "sold_at": "2026-07-29T02:00:00+00:00",
            "qualifying_new_membership": True,
            "amount_cents": 14900,
            "confidence": "verified",
            "appointment_series_ids": ["series-1"],
            "attribution_accepted": False,
            "service_components": [
                {"service_type": "sgpt", "service_name": "Strength & Sculpt"},
                {"service_type": "pt", "service_name": "Fast Track PT"},
            ],
        }
    )

    assert accepted["service_component_count"] == 2
    assert accepted["attribution_count"] == 1
    with repo.engine.begin() as connection:
        component_count = connection.execute(
            select(func.count()).select_from(sale_service_components)
        ).scalar_one()
    assert component_count == 2


def test_manual_input_needs_independent_approval(tmp_path):
    repo = repository(tmp_path)
    submitted = repo.submit_manual_input(
        {
            "input_type": "bank_cash",
            "effective_date": "2026-07-29",
            "value": "250.00",
            "unit": "AUD",
            "source_reference": "bank-statement-line-42",
            "reason": "Cash received outside connected processor",
            "submitted_by": "Admin Eve",
        }
    )
    assert submitted["accepted_for_metrics"] is False

    with pytest.raises(ValueError, match="independent"):
        repo.decide_manual_input(
            submitted["input_id"],
            decision="accepted",
            decided_by="Admin Eve",
            reason="Self approval",
        )

    accepted = repo.decide_manual_input(
        submitted["input_id"],
        decision="accepted",
        decided_by="Peter Brown",
        reason="Matched to bank evidence",
    )
    assert accepted["accepted_for_metrics"] is True


def test_metric_observation_records_event_lineage(tmp_path):
    repo = repository(tmp_path)
    event_result = repo.accept_source_event(source_event())

    metric_result = repo.record_metric_observation(
        metric_id="sa_show_rate",
        definition_version="sa-attendance-v2",
        period_start="2026-10-05",
        period_end="2026-10-05",
        value="1",
        numerator=1,
        denominator=1,
        unit="ratio",
        confidence="verified",
        event_version_ids=[event_result["event_version_id"]],
    )

    with repo.engine.begin() as connection:
        observation_count = connection.execute(
            select(func.count()).select_from(metric_observations)
        ).scalar_one()
        lineage_count = connection.execute(
            select(func.count()).select_from(metric_lineage)
        ).scalar_one()
    assert metric_result["status"] == "accepted"
    assert observation_count == 1
    assert lineage_count == 1


def test_unavailable_metric_requires_a_visible_reason(tmp_path):
    repo = repository(tmp_path)

    with pytest.raises(ValueError, match="unavailable_reason"):
        repo.record_metric_observation(
            metric_id="sa_show_rate",
            definition_version="sa-attendance-v2",
            period_start="2026-07-20",
            period_end="2026-07-26",
            value=None,
            numerator=0,
            denominator=0,
            unit="ratio",
            confidence="unresolved",
        )


def test_parallel_cutover_rejects_unexplained_difference(tmp_path):
    repo = repository(tmp_path)

    with pytest.raises(ValueError, match="unexplained variance"):
        repo.record_parallel_result(
            metric_id="sa_show_rate",
            definition_version="sa-attendance-v2",
            period_start="2026-07-20",
            period_end="2026-07-26",
            legacy_value="0.8",
            v2_value="0.75",
            variance_classification="unresolved",
            unexplained_event_count=1,
            unexplained_cents=0,
            evidence={"appointment_id": "appointment-1"},
            request_cutover_acceptance=True,
        )


def test_metric_cutover_remains_shadow_without_owner_acceptance(tmp_path):
    repo = repository(tmp_path)
    observation = {
        "value": "17",
        "confidence": "verified",
        "unavailable_reason": None,
    }
    acceptance = {
        "acceptance_record_id": "acceptance-1",
        "metric_id": "leads_created",
        "definition_version": "ghl-leads-v1",
        "acceptance_state": "ready_for_owner_acceptance",
        "technical_gates_passed": True,
        "required_distinct_scheduled_cycles": 2,
        "completed_distinct_scheduled_cycles": 2,
        "unexplained_event_count": 0,
        "unexplained_cents": 0,
        "recommendation": "Ready for Peter's metric-level decision.",
    }

    status = repo.metric_cutover_status(
        metric_id="leads_created",
        definition_version="ghl-leads-v1",
        observation=observation,
        acceptance_record=acceptance,
        legacy_fallback_available=True,
    )

    assert status["effective_state"] == "eligible_for_owner_approval"
    assert status["technical_ready"] is True
    assert status["owner_accepted"] is False
    assert status["promotion_authorised"] is False
    with pytest.raises(ValueError, match="owner acceptance"):
        repo.decide_metric_publication(
            {
                "metric_id": "leads_created",
                "definition_version": "ghl-leads-v1",
                "action": "approve",
                "decided_by": "Peter Brown",
                "reason": "Accept the governed V2 metric.",
                "legacy_fallback_available": True,
            },
            acceptance_record=acceptance,
            observation=observation,
        )


def test_metric_publication_is_immutable_and_rolls_back_in_isolation(tmp_path):
    repo = repository(tmp_path)
    observation = {
        "value": "17",
        "confidence": "verified",
        "unavailable_reason": None,
    }
    acceptance = {
        "acceptance_record_id": "acceptance-2",
        "metric_id": "leads_created",
        "definition_version": "ghl-leads-v1",
        "acceptance_state": "owner_accepted",
        "technical_gates_passed": True,
        "owner_approval_state": "accepted",
        "owner_approval_reference": "owner-decision-2026-08-02",
        "required_distinct_scheduled_cycles": 2,
        "completed_distinct_scheduled_cycles": 2,
        "unexplained_event_count": 0,
        "unexplained_cents": 0,
        "fingerprint": "acceptance-fingerprint",
    }
    approved = repo.decide_metric_publication(
        {
            "metric_id": "leads_created",
            "definition_version": "ghl-leads-v1",
            "action": "approve",
            "decided_by": "Peter Brown",
            "decided_at": "2026-08-02T01:00:00+00:00",
            "reason": "Two clean cycles and owner acceptance passed.",
            "legacy_fallback_available": True,
        },
        acceptance_record=acceptance,
        observation=observation,
    )
    accepted_status = repo.metric_cutover_status(
        metric_id="leads_created",
        definition_version="ghl-leads-v1",
        observation=observation,
        acceptance_record=acceptance,
        legacy_fallback_available=True,
    )
    failed_closed_status = repo.metric_cutover_status(
        metric_id="leads_created",
        definition_version="ghl-leads-v1",
        observation={
            **observation,
            "confidence": "unresolved",
        },
        acceptance_record=acceptance,
        legacy_fallback_available=True,
    )
    rollback = repo.decide_metric_publication(
        {
            "metric_id": "leads_created",
            "definition_version": "ghl-leads-v1",
            "action": "rollback",
            "decided_by": "Peter Brown",
            "decided_at": "2026-08-02T02:00:00+00:00",
            "reason": "Production verification found a source regression.",
            "legacy_fallback_available": True,
        },
        acceptance_record=acceptance,
        observation=observation,
    )
    rolled_back_status = repo.metric_cutover_status(
        metric_id="leads_created",
        definition_version="ghl-leads-v1",
        observation=observation,
        acceptance_record=acceptance,
        legacy_fallback_available=True,
    )

    assert approved["effective_state"] == "v2_accepted"
    assert accepted_status["promotion_authorised"] is True
    assert failed_closed_status["effective_state"] == "unavailable"
    assert failed_closed_status["promotion_authorised"] is False
    assert rollback["effective_state"] == "rolled_back"
    assert rolled_back_status["effective_state"] == "rolled_back"
    assert rolled_back_status["promotion_authorised"] is False
    with repo.engine.begin() as connection:
        decision_count = connection.execute(
            select(func.count()).select_from(
                metric_publication_decisions
            )
        ).scalar_one()
    assert decision_count == 2


def test_attendance_shadow_writes_only_shadow_metric(tmp_path):
    repo = repository(tmp_path)
    row = {
        "appointment_id": "appointment-1",
        "contact_id": "contact-1",
        "calendar_id": "calendar-1",
        "start_at": "2026-07-29T00:00:00+00:00",
        "end_at": "2026-07-29T01:00:00+00:00",
        "status": "showed",
        "canonical_status": "showed",
        "reconciliation_state": "terminal_consistent",
        "observed_at": datetime.now(UTC).isoformat(),
        "rule_version": "sa-attendance-v2",
    }

    result = repo.record_sa_attendance_shadow(
        [row],
        {
            "definition_version": "sa-attendance-v2",
            "showed": 1,
            "tracked_showed": 1,
            "no_show": 0,
            "tracked_no_show": 0,
            "tracked_cancelled": 0,
            "unresolved": 0,
        },
        as_of="2026-07-29T01:00:00+00:00",
    )

    assert result["metric"]["status"] == "accepted"
    assert result["cancellation_metric"]["status"] == "accepted"
    assert set(result["period_metrics"]) == {"week", "28d", "90d"}
    assert set(result["cancellation_period_metrics"]) == {
        "week",
        "28d",
        "90d",
    }
    assert set(result["conversion_period_metrics"]) == {
        "week",
        "28d",
        "90d",
    }
    status = repo.status()
    assert status["publication_authority"] == "none"
    assert status["legacy_reporting_unchanged"] is True
    assert status["latest_metric_observations"][0][
        "publication_state"
    ] == "shadow"
    conversion = next(
        row
        for row in status["latest_metric_observations"]
        if row["metric_id"] == "assessment_conversion_unique"
    )
    assert conversion["value"] is None
    assert "sale event bridge" in conversion["unavailable_reason"]


def test_unique_conversion_records_one_fast_track_conversion_when_complete(
    tmp_path,
):
    repo = repository(tmp_path)
    results = repo.record_unique_conversion_shadow(
        attendance_rows=[
            {
                "appointment_id": "appointment-1",
                "appointment_series_id": "series-1",
                "canonical_status": "showed",
                "start_at": "2026-07-22T01:00:00+00:00",
            }
        ],
        sales=[
            {
                "sale_id": "fast-track-sale",
                "qualifying_new_membership": True,
                "appointment_series_ids": ["series-1"],
                "service_components": [
                    {"service_type": "sgpt"},
                    {"service_type": "pt"},
                ],
            }
        ],
        commercial_source_complete=True,
        as_of="2026-07-29T01:00:00+00:00",
    )

    assert results["week"]["status"] == "accepted"
    week = next(
        row
        for row in repo.status()["latest_metric_observations"]
        if row["metric_id"] == "assessment_conversion_unique"
        and row["period_start"] == "2026-07-20"
    )
    assert week["value"] == "1.0"
    assert week["numerator"] == "1"
    assert week["denominator"] == "1"


def test_legacy_attendance_supports_conversion_with_legacy_confidence(tmp_path):
    repo = repository(tmp_path)
    repo.record_unique_conversion_shadow(
        attendance_rows=[
            {
                "appointment_id": "legacy-appointment",
                "appointment_series_id": "legacy-series",
                "canonical_status": "showed",
                "attendance_confidence": "legacy_aggregate",
                "show_rate_eligible": False,
                "start_at": "2026-07-22T01:00:00+00:00",
            }
        ],
        sales=[
            {
                "sale_id": "legacy-sale",
                "qualifying_new_membership": True,
                "appointment_series_ids": ["legacy-series"],
                "service_components": [{"service_type": "sgpt"}],
            }
        ],
        commercial_source_complete=True,
        as_of="2026-07-29T01:00:00+00:00",
    )

    week = next(
        row
        for row in repo.status()["latest_metric_observations"]
        if row["metric_id"] == "assessment_conversion_unique"
        and row["period_start"] == "2026-07-20"
    )
    assert week["value"] == "1.0"
    assert week["confidence"] == "legacy_aggregate"


def test_acquisition_and_onboarding_shadow_keeps_completion_unavailable(
    tmp_path,
):
    repo = repository(tmp_path)
    results = repo.record_acquisition_onboarding_shadow(
        lead_events=[
            {
                "source_event_id": "lead:1",
                "occurred_at": "2026-07-22T01:00:00+00:00",
            }
        ],
        prequalification_eligible_events=[
            {
                "appointment_id": "appointment-1",
                "occurred_at": "2026-07-23T01:00:00+00:00",
            }
        ],
        prequalification_events=[
            {
                "appointment_id": "appointment-1",
                "occurred_at": "2026-07-23T01:00:00+00:00",
            }
        ],
        onboarding_cases=[
            {
                "sale_id": "sale-1",
                "sold_at": "2026-07-22T01:00:00+00:00",
                "booking_days": 2,
                "completion_days": None,
            }
        ],
        as_of="2026-07-29T01:00:00+00:00",
    )

    assert results["week"]["leads"]["status"] == "accepted"
    observations = {
        row["metric_id"]: row
        for row in repo.status()["latest_metric_observations"]
        if row["period_start"] == "2026-07-20"
    }
    assert observations["leads_created"]["value"] == "1"
    assert observations["sa_bookings_unique"]["value"] == "1"
    assert observations["prequalification_completion_rate"]["value"] == "1.0"
    assert observations["onboarding_booking_speed_days"]["value"] == "2.0"
    assert observations["onboarding_completion_speed_days"]["value"] is None
    assert (
        observations["onboarding_completion_speed_days"]["confidence"]
        == "unresolved"
    )


def test_successful_first_week_rate_excludes_immature_sales(tmp_path):
    repo = repository(tmp_path)
    results = repo.record_onboarding_activation_shadow(
        activation_cases=[
            {
                "sale_id": "sale-mature",
                "sold_at": "2026-07-20T01:00:00+00:00",
                "activation_days": 8,
            },
            {
                "sale_id": "sale-immature",
                "sold_at": "2026-07-25T01:00:00+00:00",
                "activation_days": None,
            },
        ],
        source_complete=True,
        as_of="2026-07-30T01:00:00+00:00",
    )

    assert results["week"]["successful_first_week_rate"]["status"] == (
        "accepted"
    )
    observations = {
        row["metric_id"]: row
        for row in repo.status()["latest_metric_observations"]
        if row["period_start"] == "2026-07-20"
    }
    assert observations["successful_first_week_rate"]["value"] == "1.0"
    assert observations["successful_first_week_rate"]["numerator"] == "1"
    assert observations["successful_first_week_rate"]["denominator"] == "1"
    assert observations["successful_first_week_speed_days"]["value"] == "8.0"


def test_board_pack_contract_contains_no_sheet_calculation_path(tmp_path):
    repo = repository(tmp_path)
    contract = board_pack_contract()
    rows = build_board_pack_rows(
        [
            {
                "metric_id": "sa_show_rate",
                "definition_version": "sa-attendance-v2",
                "period_start": "2026-07-20",
                "period_end": "2026-07-26",
                "value": "0.8",
                "unit": "ratio",
                "numerator": "8",
                "denominator": "10",
                "confidence": "verified",
                "publication_state": "shadow",
                "unavailable_reason": None,
            }
        ],
        repo.definitions(),
    )

    assert contract["sheet_calculation_allowed"] is False
    assert contract["publication_enabled"] is False
    assert rows[1][0] == "Strength Assessment show-up rate"
    assert rows[1][4:6] == ["8", "10"]


def test_manual_input_sheet_cannot_set_its_own_approval():
    row = {
        "Input Type": "bank_cash",
        "Effective Date": "2026-07-29",
        "Value": "250",
        "Unit": "AUD",
        "Source Reference": "bank-line-42",
        "Reason": "Outside processor",
        "Submitted By": "Admin Eve",
        "Approval State": "accepted",
    }

    with pytest.raises(ValueError, match="hub-controlled"):
        validate_manual_input_sheet_row(row)


def test_historical_backfill_preserves_raw_row_and_confidence():
    raw = build_raw_workbook_record(
        workbook_id="workbook-1",
        tab_name="Appointments",
        tab_id=123,
        row_number=42,
        values=["2026-07-29", "Member"],
        formulas=["", ""],
        exported_at="2026-07-29T10:00:00+10:00",
    )
    high = classify_historical_confidence(
        {
            "exact_person_match": True,
            "compatible_timestamp": True,
            "compatible_product_or_amount": True,
        }
    )
    legacy = classify_historical_confidence(
        {"legacy_aggregate_only": True}
    )
    summary = summarise_backfill_confidence([high, legacy])

    assert raw["row_hash"]
    assert high["confidence"] == "high"
    assert legacy["confidence"] == "legacy_aggregate"
    assert summary["accepted_for_official_aggregate"] == 1
    assert summary["context_only"] == 1
