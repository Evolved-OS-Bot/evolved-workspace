from __future__ import annotations

import json
import uuid
from collections import Counter
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal, InvalidOperation
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
    update,
)

from .contracts import canonical_json, fingerprint


BRISBANE_TZ = ZoneInfo("Australia/Brisbane")
REPORTING_V2_SCHEMA_VERSION = 1
REPORTING_V2_MODE = "shadow"
ASSESSMENT_ATTRIBUTION_DAYS = 30

CONFIDENCE_LEVELS = {
    "verified",
    "high",
    "medium",
    "low",
    "legacy_aggregate",
    "unresolved",
}
ACCEPTANCE_STATES = {"accepted", "rejected", "quarantined"}
MANUAL_INPUT_STATES = {
    "pending",
    "accepted",
    "rejected",
    "superseded",
}
PARITY_STATES = {
    "collecting",
    "passed",
    "failed",
    "accepted_for_cutover",
}
PUBLICATION_STATES = {"shadow", "accepted", "legacy", "rejected"}
CASH_SOURCE_SYSTEMS = {"stripe", "pt_minder", "bank_manual"}
CASH_EVENT_TYPES = {"settled_cash", "refund"}
CASH_REQUIRED_SOURCE_HOURS = {
    "stripe": 14,
    "pt_minder": 192,
}


v2_metadata = MetaData()

source_events = Table(
    "hub_v2_source_events",
    v2_metadata,
    Column("event_version_id", String(64), primary_key=True),
    Column("source_system", String(80), nullable=False, index=True),
    Column("source_object_type", String(80), nullable=False),
    Column("source_event_id", String(240), nullable=False, index=True),
    Column("source_object_id", String(240)),
    Column("source_version", String(160)),
    Column("occurred_at", DateTime(timezone=True), nullable=False),
    Column("effective_at", DateTime(timezone=True)),
    Column("observed_at", DateTime(timezone=True), nullable=False),
    Column("accepted_at", DateTime(timezone=True), nullable=False),
    Column("brisbane_local_date", String(10), nullable=False, index=True),
    Column("source_run_id", String(160)),
    Column("source_snapshot_id", String(64)),
    Column("payload_hash", String(64), nullable=False),
    Column("schema_version", Integer, nullable=False),
    Column("supersedes_event_version_id", String(64)),
    Column("acceptance_state", String(24), nullable=False),
    Column("rejection_reason", Text),
    Column("confidence", String(24), nullable=False),
    Column("payload_json", Text, nullable=False),
    UniqueConstraint(
        "source_system",
        "source_object_type",
        "source_event_id",
        "payload_hash",
        name="uq_v2_source_event_version",
    ),
)

cash_source_runs = Table(
    "hub_v2_cash_source_runs",
    v2_metadata,
    Column("source_system", String(80), primary_key=True),
    Column("source_run_id", String(160), primary_key=True),
    Column("observed_at", DateTime(timezone=True), nullable=False),
    Column("complete", Integer, nullable=False),
    Column("event_count", Integer, nullable=False),
    Column("payload_hash", String(64), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
)

metric_definitions = Table(
    "hub_v2_metric_definitions",
    v2_metadata,
    Column("metric_id", String(120), primary_key=True),
    Column("definition_version", String(80), primary_key=True),
    Column("plain_english_name", String(240), nullable=False),
    Column("decision_question", Text, nullable=False),
    Column("event_grain", String(240), nullable=False),
    Column("source_authority_json", Text, nullable=False),
    Column("numerator_definition", Text),
    Column("denominator_definition", Text),
    Column("inclusion_rules_json", Text, nullable=False),
    Column("exclusion_rules_json", Text, nullable=False),
    Column("period_semantics", String(240), nullable=False),
    Column("minimum_freshness_json", Text, nullable=False),
    Column("owner", String(160), nullable=False),
    Column("approval_state", String(40), nullable=False),
    Column("effective_from", String(10)),
    Column("effective_to", String(10)),
    Column("definition_hash", String(64), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
)

metric_runs = Table(
    "hub_v2_metric_runs",
    v2_metadata,
    Column("metric_run_id", String(64), primary_key=True),
    Column("started_at", DateTime(timezone=True), nullable=False),
    Column("completed_at", DateTime(timezone=True), nullable=False),
    Column("status", String(24), nullable=False),
    Column("event_set_fingerprint", String(64), nullable=False),
    Column("source_freshness_json", Text, nullable=False),
    Column("error", Text),
)

metric_observations = Table(
    "hub_v2_metric_observations",
    v2_metadata,
    Column("metric_observation_id", String(64), primary_key=True),
    Column("metric_id", String(120), nullable=False, index=True),
    Column("definition_version", String(80), nullable=False),
    Column("metric_run_id", String(64), nullable=False, index=True),
    Column("period_start", String(10), nullable=False),
    Column("period_end", String(10), nullable=False),
    Column("as_of_at", DateTime(timezone=True)),
    Column("value", String(80)),
    Column("numerator", String(80)),
    Column("denominator", String(80)),
    Column("unit", String(40), nullable=False),
    Column("confidence", String(24), nullable=False),
    Column("publication_state", String(40), nullable=False),
    Column("unavailable_reason", Text),
    Column("created_at", DateTime(timezone=True), nullable=False),
    UniqueConstraint(
        "metric_id",
        "definition_version",
        "period_start",
        "period_end",
        "metric_run_id",
        name="uq_v2_metric_observation",
    ),
)

metric_lineage = Table(
    "hub_v2_metric_lineage",
    v2_metadata,
    Column("lineage_id", String(64), primary_key=True),
    Column("metric_observation_id", String(64), nullable=False, index=True),
    Column("event_version_id", String(64), index=True),
    Column("source_snapshot_id", String(64)),
    Column("lineage_role", String(40), nullable=False),
    UniqueConstraint(
        "metric_observation_id",
        "event_version_id",
        "source_snapshot_id",
        "lineage_role",
        name="uq_v2_metric_lineage",
    ),
)

appointment_series_links = Table(
    "hub_v2_appointment_series_links",
    v2_metadata,
    Column("link_id", String(64), primary_key=True),
    Column("appointment_id", String(240), nullable=False, unique=True),
    Column("appointment_series_id", String(240), nullable=False, index=True),
    Column("relation_type", String(40), nullable=False),
    Column("superseded", Integer, nullable=False),
    Column("confidence", String(24), nullable=False),
    Column("evidence_json", Text, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
)

sale_events = Table(
    "hub_v2_sale_events",
    v2_metadata,
    Column("sale_id", String(240), primary_key=True),
    Column("person_id", String(64)),
    Column("source_system", String(80), nullable=False),
    Column("source_sale_id", String(240), nullable=False),
    Column("sold_at", DateTime(timezone=True), nullable=False),
    Column("brisbane_local_date", String(10), nullable=False),
    Column("sale_type", String(80), nullable=False),
    Column("qualifying_new_membership", Integer, nullable=False),
    Column("amount_cents", Integer),
    Column("currency", String(8), nullable=False),
    Column("confidence", String(24), nullable=False),
    Column("source_event_version_id", String(64)),
    Column("evidence_json", Text, nullable=False),
    UniqueConstraint(
        "source_system",
        "source_sale_id",
        name="uq_v2_sale_source",
    ),
)

sale_service_components = Table(
    "hub_v2_sale_service_components",
    v2_metadata,
    Column("component_id", String(64), primary_key=True),
    Column("sale_id", String(240), nullable=False, index=True),
    Column("service_type", String(80), nullable=False),
    Column("service_name", String(240)),
    Column("quantity", String(40)),
    Column("unit", String(40)),
    Column("effective_from", String(10)),
    Column("effective_to", String(10)),
    UniqueConstraint(
        "sale_id",
        "service_type",
        "service_name",
        name="uq_v2_sale_service",
    ),
)

sale_attributions = Table(
    "hub_v2_sale_attributions",
    v2_metadata,
    Column("attribution_id", String(64), primary_key=True),
    Column("sale_id", String(240), nullable=False, index=True),
    Column("appointment_series_id", String(240), nullable=False, index=True),
    Column("attribution_rule_version", String(80), nullable=False),
    Column("confidence", String(24), nullable=False),
    Column("accepted", Integer, nullable=False),
    Column("evidence_json", Text, nullable=False),
    UniqueConstraint(
        "sale_id",
        "appointment_series_id",
        "attribution_rule_version",
        name="uq_v2_sale_attribution",
    ),
)

manual_input_events = Table(
    "hub_v2_manual_input_events",
    v2_metadata,
    Column("input_id", String(64), primary_key=True),
    Column("input_type", String(80), nullable=False, index=True),
    Column("effective_date", String(10), nullable=False),
    Column("value", String(160), nullable=False),
    Column("unit", String(40), nullable=False),
    Column("source_reference", Text, nullable=False),
    Column("reason", Text, nullable=False),
    Column("submitted_by", String(160), nullable=False),
    Column("submitted_at", DateTime(timezone=True), nullable=False),
    Column("approval_state", String(24), nullable=False),
    Column("supersedes_input_id", String(64)),
    Column("payload_hash", String(64), nullable=False),
)

manual_input_decisions = Table(
    "hub_v2_manual_input_decisions",
    v2_metadata,
    Column("decision_id", String(64), primary_key=True),
    Column("input_id", String(64), nullable=False, index=True),
    Column("decision", String(24), nullable=False),
    Column("decided_by", String(160), nullable=False),
    Column("decided_at", DateTime(timezone=True), nullable=False),
    Column("reason", Text, nullable=False),
    UniqueConstraint(
        "input_id",
        "decision",
        "decided_at",
        name="uq_v2_manual_decision",
    ),
)

parallel_run_results = Table(
    "hub_v2_parallel_run_results",
    v2_metadata,
    Column("comparison_id", String(64), primary_key=True),
    Column("metric_id", String(120), nullable=False, index=True),
    Column("definition_version", String(80), nullable=False),
    Column("period_start", String(10), nullable=False),
    Column("period_end", String(10), nullable=False),
    Column("legacy_value", String(80)),
    Column("v2_value", String(80)),
    Column("variance", String(80)),
    Column("variance_classification", String(80), nullable=False),
    Column("unexplained_event_count", Integer, nullable=False),
    Column("unexplained_cents", Integer, nullable=False),
    Column("acceptance_state", String(40), nullable=False),
    Column("evidence_json", Text, nullable=False),
    Column("comparison_fingerprint", String(64), nullable=False),
    Column("recorded_at", DateTime(timezone=True), nullable=False),
    UniqueConstraint(
        "metric_id",
        "definition_version",
        "period_start",
        "period_end",
        "comparison_fingerprint",
        name="uq_v2_parallel_attempt",
    ),
)

metric_publication_decisions = Table(
    "hub_v2_metric_publication_decisions",
    v2_metadata,
    Column("decision_id", String(64), primary_key=True),
    Column("metric_id", String(120), nullable=False, index=True),
    Column("definition_version", String(80), nullable=False),
    Column("action", String(24), nullable=False),
    Column("decided_by", String(160), nullable=False),
    Column("decided_at", DateTime(timezone=True), nullable=False),
    Column("reason", Text, nullable=False),
    Column("acceptance_record_id", String(64)),
    Column("acceptance_fingerprint", String(64)),
    Column("fallback_state", String(24), nullable=False),
    Column("evidence_json", Text, nullable=False),
    Column("decision_fingerprint", String(64), nullable=False),
    UniqueConstraint(
        "metric_id",
        "definition_version",
        "decision_fingerprint",
        name="uq_v2_metric_publication_decision",
    ),
)

CORE_METRIC_DEFINITIONS = (
    {
        "metric_id": "website_visitors",
        "definition_version": "website-marketing-v1",
        "plain_english_name": "Website visitors",
        "decision_question": (
            "How many distinct website users visited the owned root host?"
        ),
        "event_grain": "GA4 user on the exact owned root host",
        "source_authority": {
            "traffic": "canonical business-owned GA4 property",
        },
        "numerator_definition": (
            "GA4 total users filtered to theevolvedgym.com.au"
        ),
        "denominator_definition": None,
        "inclusion_rules": [
            "exact root host",
            "completed Brisbane-local reporting period",
        ],
        "exclusion_rules": [
            "other hosts",
            "periods before exact-host history begins",
        ],
        "period_semantics": "selected completed Brisbane-local period",
        "minimum_freshness": {"website_analytics_hours": 14},
        "owner": "Peter Brown",
        "approval_state": "approved_shadow",
    },
    {
        "metric_id": "website_subscribers_unique",
        "definition_version": "website-marketing-v1",
        "plain_english_name": "New subscribers",
        "decision_question": (
            "How many unique people first subscribed in the period?"
        ),
        "event_grain": "unique GHL contact's earliest accepted subscription",
        "source_authority": {
            "subscriber": "GHL 30-day email form submission",
        },
        "numerator_definition": (
            "unique contacts whose earliest accepted subscription is in "
            "the period"
        ),
        "denominator_definition": None,
        "inclusion_rules": ["one earliest subscription per GHL contact"],
        "exclusion_rules": ["repeat submissions", "missing contact identity"],
        "period_semantics": "selected completed Brisbane-local period",
        "minimum_freshness": {"website_subscription_hours": 14},
        "owner": "Peter Brown",
        "approval_state": "approved_shadow",
    },
    {
        "metric_id": "visitor_to_subscriber_rate",
        "definition_version": "website-marketing-v1",
        "plain_english_name": "Visitors becoming subscribers",
        "decision_question": (
            "What proportion of website visitors became unique subscribers?"
        ),
        "event_grain": "completed website reporting period",
        "source_authority": {
            "visitor": "canonical business-owned GA4 property",
            "subscriber": "GHL 30-day email form submission",
        },
        "numerator_definition": "unique new subscribers in the period",
        "denominator_definition": "GA4 visitors on the exact owned root host",
        "inclusion_rules": [
            "same completed Brisbane-local period",
            "unique subscriber contacts",
        ],
        "exclusion_rules": ["repeat forms", "traffic on other hosts"],
        "period_semantics": "selected completed Brisbane-local period",
        "minimum_freshness": {
            "website_analytics_hours": 14,
            "website_subscription_hours": 14,
        },
        "owner": "Peter Brown",
        "approval_state": "approved_shadow",
    },
    {
        "metric_id": "sa_show_rate",
        "definition_version": "sa-attendance-v2",
        "plain_english_name": "Strength Assessment show-up rate",
        "decision_question": (
            "Of the assessments with a verified attended or no-show outcome, "
            "what proportion attended?"
        ),
        "event_grain": "unique terminal Strength Assessment appointment series",
        "source_authority": {
            "appointment": "GHL",
            "delivery_evidence": "Consultant Feedback",
        },
        "numerator_definition": "unique terminal appointment series marked showed",
        "denominator_definition": (
            "unique terminal appointment series marked showed or no_show"
        ),
        "inclusion_rules": ["showed", "no_show"],
        "exclusion_rules": [
            "cancelled",
            "invalid",
            "superseded",
            "unresolved",
            "legacy appointments from the incomplete deleted-outcome cohort",
        ],
        "period_semantics": (
            "assessment scheduled start in completed Brisbane-local period"
        ),
        "minimum_freshness": {"strength_assessment_attendance_hours": 14},
        "owner": "Peter Brown",
        "approval_state": "shadow",
    },
    {
        "metric_id": "sa_cancellation_rate",
        "definition_version": "sa-attendance-v2",
        "plain_english_name": "Strength Assessment cancellation rate",
        "decision_question": (
            "Of assessments with a governed attended, no-show or cancelled "
            "outcome in the complete tracking cohort, what proportion "
            "cancelled?"
        ),
        "event_grain": "unique terminal Strength Assessment appointment series",
        "source_authority": {
            "appointment": "GHL",
            "outcome": "explicit governed appointment status",
        },
        "numerator_definition": (
            "unique tracked appointment series marked cancelled"
        ),
        "denominator_definition": (
            "unique tracked appointment series marked showed, no_show or "
            "cancelled"
        ),
        "inclusion_rules": ["showed", "no_show", "cancelled"],
        "exclusion_rules": [
            "invalid",
            "superseded",
            "unresolved",
            "legacy appointments from the incomplete deleted-outcome cohort",
        ],
        "period_semantics": (
            "assessment scheduled start in completed Brisbane-local period"
        ),
        "minimum_freshness": {"strength_assessment_attendance_hours": 14},
        "owner": "Peter Brown",
        "approval_state": "approved_shadow",
    },
    {
        "metric_id": "sa_listed_show_rate",
        "definition_version": "sa-listed-show-v1",
        "plain_english_name": "Listed Strength Assessment show-up rate",
        "decision_question": (
            "Since complete list tracking began, what proportion of "
            "assessments explicitly listed Y or N were listed Y?"
        ),
        "event_grain": "one row in the Appointments list",
        "source_authority": {
            "historical_list": "Google Sheets Appointments column K",
        },
        "numerator_definition": (
            "Appointments rows dated on or after 2026-03-12 with Show? = Y"
        ),
        "denominator_definition": (
            "Appointments rows dated on or after 2026-03-12 with Show? = Y or N"
        ),
        "inclusion_rules": [
            "appointment date on or after 2026-03-12",
            "explicit Y or N only",
        ],
        "exclusion_rules": [
            "blank outcomes",
            "rows before complete list tracking began",
            "no inference that N means cancellation",
        ],
        "period_semantics": (
            "assessment scheduled start in completed Brisbane-local period"
        ),
        "minimum_freshness": {"google_sheet_hours": 14},
        "owner": "Peter Brown",
        "approval_state": "approved_shadow",
        "effective_from": "2026-03-12",
    },
    {
        "metric_id": "sa_listed_conversion_rate",
        "definition_version": "sa-listed-conversion-v1",
        "plain_english_name": "Listed Strength Assessment conversion rate",
        "decision_question": (
            "What proportion of attended assessments in the historical "
            "Appointments list were marked converted?"
        ),
        "event_grain": "one attended row in the Appointments list",
        "source_authority": {
            "historical_list": (
                "Google Sheets Appointments columns K and L"
            ),
        },
        "numerator_definition": (
            "attended Appointments rows with Convert? = Y"
        ),
        "denominator_definition": (
            "surviving legacy rows from 2025-09-19 to 2026-03-11, plus "
            "rows on or after 2026-03-12 with Show? = Y"
        ),
        "inclusion_rules": [
            "conversion history begins 2025-09-19",
            "pre-2026-03-12 surviving rows are legacy attended",
            "from 2026-03-12 attendance requires Show? = Y",
            "all Convert? = Y rows remain in the listed numerator",
        ],
        "exclusion_rules": [
            "post-2026-03-12 rows with Show? = N or blank",
            "blank or N conversion outcomes from the numerator",
        ],
        "period_semantics": (
            "assessment scheduled start in completed Brisbane-local period"
        ),
        "minimum_freshness": {"google_sheet_hours": 14},
        "owner": "Peter Brown",
        "approval_state": "approved_shadow",
        "effective_from": "2025-09-19",
    },
    {
        "metric_id": "subscriber_to_sa_booking_rate",
        "definition_version": "ghl-subscriber-sa-booking-v1",
        "plain_english_name": (
            "Subscribers booking a Strength Assessment"
        ),
        "decision_question": (
            "What proportion of new website subscribers booked a Strength "
            "Assessment within 30 days?"
        ),
        "event_grain": "unique GHL contact subscriber cohort",
        "source_authority": {
            "subscriber": "GHL 30DNNC form submission",
            "booking": "GHL Strength Assessment appointment dateAdded",
        },
        "numerator_definition": (
            "unique subscriber contacts with a qualifying assessment "
            "appointment created within 30 days after first subscription"
        ),
        "denominator_definition": (
            "unique contacts whose first accepted subscription occurred in "
            "the selected completed period"
        ),
        "inclusion_rules": [
            "one earliest accepted subscription per GHL contact",
            "confirmed, showed, no-show or cancelled booking evidence",
            "booking created at or after subscription and within 30 days",
        ],
        "exclusion_rules": [
            "repeat form submissions",
            "multiple or rescheduled appointments for the same contact",
            "invalid, deleted, unknown or pre-subscription appointments",
            "SGPT and PT service components",
        ],
        "period_semantics": (
            "first subscription date in Brisbane-local completed period; "
            "recent cohorts remain an as-of-now view during their 30-day "
            "booking window"
        ),
        "minimum_freshness": {
            "website_subscription_hours": 14,
            "strength_assessment_appointment_hours": 14,
        },
        "owner": "Peter Brown",
        "approval_state": "approved_shadow",
    },
    {
        "metric_id": "leads_created",
        "definition_version": "ghl-leads-v1",
        "plain_english_name": "New leads",
        "decision_question": "How many unique contacts became leads?",
        "event_grain": "unique GHL contact creation event",
        "source_authority": {"lead": "GHL contact creation"},
        "numerator_definition": "unique accepted lead-created events",
        "denominator_definition": None,
        "inclusion_rules": ["one lead-created event per GHL contact"],
        "exclusion_rules": ["duplicate contact-event versions"],
        "period_semantics": "contact creation in Brisbane-local period",
        "minimum_freshness": {"ghl_hours": 14},
        "owner": "Peter Brown",
        "approval_state": "approved_shadow",
    },
    {
        "metric_id": "sa_bookings_unique",
        "definition_version": "ghl-sa-bookings-v1",
        "plain_english_name": "Strength Assessment bookings",
        "decision_question": (
            "How many unique eligible Strength Assessment appointments "
            "were scheduled?"
        ),
        "event_grain": "unique GHL Strength Assessment appointment",
        "source_authority": {"appointment": "GHL calendar event"},
        "numerator_definition": "unique eligible assessment appointments",
        "denominator_definition": None,
        "inclusion_rules": ["confirmed, showed or no-show appointments"],
        "exclusion_rules": ["cancelled and invalid appointments"],
        "period_semantics": "scheduled start in Brisbane-local period",
        "minimum_freshness": {"ghl_hours": 14},
        "owner": "Peter Brown",
        "approval_state": "approved_shadow",
    },
    {
        "metric_id": "prequalification_completion_rate",
        "definition_version": "ghl-prequalification-v1",
        "plain_english_name": "Prequalification completion rate",
        "decision_question": (
            "What proportion of eligible Strength Assessment bookings "
            "have completed prequalification evidence?"
        ),
        "event_grain": "unique eligible Strength Assessment appointment",
        "source_authority": {
            "appointment": "GHL calendar event",
            "completion": "GHL prequalification state",
        },
        "numerator_definition": (
            "eligible appointment with accepted prequalification evidence"
        ),
        "denominator_definition": "eligible assessment appointments",
        "inclusion_rules": [
            "current WARM prequalified-or-later stage",
            "non-empty governed Pre-qual Summary",
        ],
        "exclusion_rules": [
            "cancelled or invalid appointment",
            "missing completion evidence",
        ],
        "period_semantics": "assessment start in Brisbane-local period",
        "minimum_freshness": {"ghl_hours": 14},
        "owner": "Peter Brown",
        "approval_state": "approved_shadow",
    },
    {
        "metric_id": "assessment_conversion_unique",
        "definition_version": "assessment-conversion-v1",
        "plain_english_name": "Strength Assessment conversion rate",
        "decision_question": (
            "What proportion of attended assessment series produced at least "
            "one qualifying new-membership sale?"
        ),
        "event_grain": "unique attended Strength Assessment appointment series",
        "source_authority": {
            "attendance": "Reporting V2 accepted assessment delivery",
            "sale": "accepted GHL agreement or commercial sale event",
        },
        "numerator_definition": (
            "unique attended appointment series with an accepted qualifying "
            "new-membership sale attribution"
        ),
        "denominator_definition": "unique attended appointment series",
        "inclusion_rules": [
            "one conversion per appointment series",
            "multi-service sale remains one sale",
        ],
        "exclusion_rules": [
            "existing-member PT add-on",
            "upgrade",
            "downgrade",
            "unresolved attribution",
        ],
        "period_semantics": (
            "assessment scheduled start in completed Brisbane-local period"
        ),
        "minimum_freshness": {
            "strength_assessment_attendance_hours": 14,
            "commercial_sale_hours": 14,
        },
        "owner": "Peter Brown",
        "approval_state": "approved_shadow",
    },
    {
        "metric_id": "onboarding_booking_speed_days",
        "definition_version": "ghl-onboarding-booking-v1",
        "plain_english_name": "Average days from sale to onboarding booking",
        "decision_question": (
            "How quickly is the first required onboarding appointment "
            "scheduled after sale?"
        ),
        "event_grain": "qualifying new sale requiring onboarding",
        "source_authority": {
            "sale": "accepted GHL agreement",
            "booking": "GHL onboarding or Intro appointment",
        },
        "numerator_definition": (
            "sum of Brisbane calendar days from sale to first valid "
            "scheduled onboarding appointment"
        ),
        "denominator_definition": (
            "qualifying sales with a linked onboarding booking"
        ),
        "inclusion_rules": [
            "Strong one-session onboarding",
            "Fast Track four-session onboarding",
            "new PT-only intro",
        ],
        "exclusion_rules": [
            "Fit & Flexible with no onboarding entitlement",
            "cancelled, no-show or invalid appointments",
            "reactivations and existing-member add-ons",
        ],
        "period_semantics": "sale date in Brisbane-local period",
        "minimum_freshness": {"ghl_hours": 14},
        "owner": "Peter Brown",
        "approval_state": "approved_shadow",
    },
    {
        "metric_id": "onboarding_completion_speed_days",
        "definition_version": "ghl-onboarding-completion-v1",
        "plain_english_name": "Average days from sale to completed onboarding",
        "decision_question": (
            "How quickly is the first required onboarding session actually "
            "completed after sale?"
        ),
        "event_grain": "qualifying new sale requiring onboarding",
        "source_authority": {
            "sale": "accepted GHL agreement",
            "completion": "terminal GHL Showed onboarding appointment",
        },
        "numerator_definition": (
            "sum of Brisbane calendar days from sale to first Showed "
            "onboarding appointment"
        ),
        "denominator_definition": (
            "qualifying sales with a verified completed onboarding session"
        ),
        "inclusion_rules": ["first terminal Showed onboarding session"],
        "exclusion_rules": [
            "elapsed Confirmed appointments",
            "cancelled, no-show or invalid appointments",
            "Fit & Flexible with no onboarding entitlement",
        ],
        "period_semantics": "sale date in Brisbane-local period",
        "minimum_freshness": {"ghl_hours": 14},
        "owner": "Peter Brown",
        "approval_state": "approved_shadow",
    },
    {
        "metric_id": "successful_first_week_rate",
        "definition_version": "successful-first-week-v1",
        "plain_english_name": "New members completing a successful first week",
        "decision_question": (
            "What proportion of new members attended onboarding, completed "
            "three Trainerize training records and received a verified "
            "positive first-week check-in?"
        ),
        "event_grain": "qualifying new sale requiring onboarding",
        "source_authority": {
            "sale": "accepted GHL agreement",
            "onboarding": "terminal GHL Showed appointment",
            "training": "tracked Trainerize training records",
            "confirmation": (
                "completed GHL positive-reply verification or controlled "
                "staff-call confirmation task"
            ),
        },
        "numerator_definition": (
            "unique qualifying sales satisfying all three activation "
            "requirements"
        ),
        "denominator_definition": (
            "qualifying new sales old enough to complete the first-week "
            "activation journey"
        ),
        "inclusion_rules": [
            "attended first 1:1 onboarding appointment",
            "at least three distinct tracked Trainerize training records",
            "verified positive reply or staff-call confirmation",
        ],
        "exclusion_rules": [
            "Fit & Flexible with no onboarding entitlement",
            "reactivations",
            "existing-member add-ons",
            "sales fewer than nine days old remain pending",
        ],
        "period_semantics": "sale date in Brisbane-local period",
        "minimum_freshness": {
            "ghl_hours": 14,
            "trainerize_hours": 14,
        },
        "owner": "Peter Brown",
        "approval_state": "approved_shadow",
    },
    {
        "metric_id": "successful_first_week_speed_days",
        "definition_version": "successful-first-week-v1",
        "plain_english_name": "Average days from sale to a successful first week",
        "decision_question": (
            "How long does it take a new member to satisfy the complete "
            "first-week activation standard?"
        ),
        "event_grain": "successfully activated qualifying new sale",
        "source_authority": {
            "sale": "accepted GHL agreement",
            "activation": (
                "latest of onboarding attendance, third tracked training "
                "record and verified first-week confirmation"
            ),
        },
        "numerator_definition": (
            "sum of Brisbane calendar days from sale to final qualifying "
            "activation event"
        ),
        "denominator_definition": "successfully activated qualifying sales",
        "inclusion_rules": ["all successful-first-week requirements satisfied"],
        "exclusion_rules": ["incomplete or unresolved activation cases"],
        "period_semantics": "sale date in Brisbane-local period",
        "minimum_freshness": {
            "ghl_hours": 14,
            "trainerize_hours": 14,
        },
        "owner": "Peter Brown",
        "approval_state": "approved_shadow",
    },
    {
        "metric_id": "service_components_sold",
        "definition_version": "service-components-v1",
        "plain_english_name": "Services sold by type",
        "decision_question": (
            "Which services were included in accepted commercial sales?"
        ),
        "event_grain": "service component within one accepted sale",
        "source_authority": {"sale": "accepted commercial sale event"},
        "numerator_definition": "count of accepted service components by type",
        "denominator_definition": None,
        "inclusion_rules": ["each distinct service component"],
        "exclusion_rules": ["duplicate source service component"],
        "period_semantics": "sale occurred in completed Brisbane-local period",
        "minimum_freshness": {"commercial_sale_hours": 14},
        "owner": "Peter Brown",
        "approval_state": "shadow",
    },
    {
        "metric_id": "sgpt_delivery",
        "definition_version": "sgpt-delivery-v1",
        "plain_english_name": "Small-group training delivery",
        "decision_question": (
            "Are active small-group members receiving the booked and "
            "attended delivery the timetable promises?"
        ),
        "event_grain": (
            "Trainerize class booking/outcome joined to one active SGPT person"
        ),
        "source_authority": {
            "booking_and_outcome": "Trainerize",
            "planned_delivery": "governed timetable",
            "active_roster": "Operating Data Hub",
        },
        "numerator_definition": (
            "booked or explicitly attended member-class events by view"
        ),
        "denominator_definition": (
            "scheduled class capacity or active SGPT roster by view"
        ),
        "inclusion_rules": [
            "complete fresh source run",
            "exact active-person identity",
            "explicit outcome evidence only",
        ],
        "exclusion_rules": [
            "inferred attendance",
            "elapsed session inferred as no-show",
            "ambiguous identity",
        ],
        "period_semantics": "selected completed Brisbane-local period",
        "minimum_freshness": {"trainerize_performance_hours": 14},
        "owner": "Peter Brown",
        "approval_state": "approved_shadow",
    },
    {
        "metric_id": "evolved_standards",
        "definition_version": "evolved-standards-v1-shadow",
        "plain_english_name": "Evolved Standards evidence",
        "decision_question": (
            "Which component standards are evidenced, and how long did they "
            "take from the governed membership start?"
        ),
        "event_grain": (
            "one governed person, assessment component and achieved level"
        ),
        "source_authority": {
            "assessment_evidence": "Trainerize",
            "effective_start": "Operating Data Hub membership lifecycle",
            "component_rules": "Evolved Standards governed projection",
        },
        "numerator_definition": (
            "component achievements supported by complete exact evidence"
        ),
        "denominator_definition": (
            "eligible governed members with resolvable effective starts"
        ),
        "inclusion_rules": [
            "complete fresh source observations",
            "exact governed identity",
            "exact component evidence",
            "resolvable effective membership start",
        ],
        "exclusion_rules": [
            "ambiguous or missing identity",
            "partial or stale evidence",
            "missing effective membership start",
            "overall classification before owner policy approval",
        ],
        "period_semantics": "as-of selected completed Brisbane-local period",
        "minimum_freshness": {
            "trainerize_performance_hours": 14,
            "membership_reconciliation_hours": 14,
        },
        "owner": "Peter Brown",
        "approval_state": "approved_shadow",
    },
    {
        "metric_id": "consumer_retention_intelligence_contract",
        "definition_version": "retention-hub-read-v1",
        "plain_english_name": "Retention Intelligence Hub read",
        "decision_question": (
            "Does Retention Intelligence reproduce the Hub person and "
            "lifecycle classifications exactly?"
        ),
        "event_grain": "one versioned Hub person/lifecycle classification",
        "source_authority": {"contract": "Operating Data Hub"},
        "numerator_definition": "exact matched classifications",
        "denominator_definition": "all compared classifications",
        "inclusion_rules": ["fresh complete Hub contract", "exact identities"],
        "exclusion_rules": ["unexplained identity or classification difference"],
        "period_semantics": "scheduled shadow comparison cycle",
        "minimum_freshness": {"retention_intelligence_hours": 14},
        "owner": "Peter Brown",
        "approval_state": "approved_shadow",
    },
    {
        "metric_id": "consumer_conversation_triage_contract",
        "definition_version": "conversation-triage-hub-read-v1",
        "plain_english_name": "Conversation Triage Hub read",
        "decision_question": (
            "Does Conversation Triage reproduce the Hub person and lifecycle "
            "classifications exactly?"
        ),
        "event_grain": "one versioned Hub person/lifecycle classification",
        "source_authority": {"contract": "Operating Data Hub"},
        "numerator_definition": "exact matched classifications",
        "denominator_definition": "all compared classifications",
        "inclusion_rules": ["fresh complete Hub contract", "exact identities"],
        "exclusion_rules": ["unexplained identity or classification difference"],
        "period_semantics": "scheduled shadow comparison cycle",
        "minimum_freshness": {"conversation_triage_hours": 14},
        "owner": "Peter Brown",
        "approval_state": "approved_shadow",
    },
    {
        "metric_id": "consumer_pt_booking_continuity_contract",
        "definition_version": "pt-booking-hub-read-v1",
        "plain_english_name": "PT Booking Continuity Hub read",
        "decision_question": (
            "Does PT Booking Continuity reproduce Hub person, service and "
            "entitlement classifications exactly?"
        ),
        "event_grain": "one versioned Hub person/service classification",
        "source_authority": {"contract": "Operating Data Hub"},
        "numerator_definition": "exact matched classifications",
        "denominator_definition": "all compared classifications",
        "inclusion_rules": ["fresh complete Hub contract", "exact identities"],
        "exclusion_rules": ["unexplained identity or classification difference"],
        "period_semantics": "scheduled shadow comparison cycle",
        "minimum_freshness": {"pt_booking_continuity_hours": 192},
        "owner": "Peter Brown",
        "approval_state": "approved_shadow",
    },
    {
        "metric_id": "consumer_revenue_control_contract",
        "definition_version": "revenue-control-hub-read-v1",
        "plain_english_name": "Revenue Control Hub read",
        "decision_question": (
            "Does Revenue Control reproduce Hub person, service, entitlement "
            "and payment classifications exactly?"
        ),
        "event_grain": "one versioned Hub commercial classification",
        "source_authority": {"contract": "Operating Data Hub"},
        "numerator_definition": "exact matched classifications",
        "denominator_definition": "all compared classifications",
        "inclusion_rules": ["fresh complete Hub contract", "exact identities"],
        "exclusion_rules": ["unexplained identity or classification difference"],
        "period_semantics": "scheduled shadow comparison cycle",
        "minimum_freshness": {"revenue_control_hours": 96},
        "owner": "Peter Brown",
        "approval_state": "approved_shadow",
    },
    {
        "metric_id": "operating_expenses",
        "definition_version": "operating-expenses-v2",
        "plain_english_name": "Expenses",
        "decision_question": (
            "What expenses did the business recognise in the selected "
            "completed period?"
        ),
        "event_grain": "Xero Profit and Loss period",
        "source_authority": {
            "expenses": "Xero Profit and Loss report",
        },
        "numerator_definition": (
            "cost of sales plus operating expenses recognised by Xero"
        ),
        "denominator_definition": None,
        "inclusion_rules": [
            "completed Brisbane-local reporting period",
            "Xero cost of sales",
            "Xero operating expenses",
        ],
        "exclusion_rules": [
            "bank transfers",
            "credit-card repayments",
            "Stripe clearing movements",
            "unreconciled raw bank cash",
        ],
        "period_semantics": "selected completed Brisbane-local period",
        "minimum_freshness": {"xero_hours": 26},
        "owner": "Peter Brown",
        "approval_state": "approved_shadow",
    },
    {
        "metric_id": "cash_accounting_validation",
        "definition_version": "cash-accounting-validation-v1",
        "plain_english_name": "Cash compared with Xero income",
        "decision_question": (
            "Does collected processor cash reconcile directionally with "
            "income recognised in Xero?"
        ),
        "event_grain": "completed reporting period",
        "source_authority": {
            "cash": "accepted Stripe and PT Minder cash events",
            "income": "Xero Profit and Loss report",
        },
        "numerator_definition": (
            "accepted cash excluding GST minus Xero income excluding GST"
        ),
        "denominator_definition": None,
        "inclusion_rules": [
            "same completed Brisbane-local period",
            "fresh complete cash source runs",
            "complete Xero Profit and Loss report",
        ],
        "exclusion_rules": [
            "raw Bank Summary cash received",
            "internal transfers",
            "automatic KPI or cash-goal replacement",
        ],
        "period_semantics": "selected completed Brisbane-local period",
        "minimum_freshness": {
            "stripe_hours": 14,
            "pt_minder_hours": 192,
            "xero_hours": 26,
        },
        "owner": "Peter Brown",
        "approval_state": "shadow",
    },
    {
        "metric_id": "cash_goal_progress",
        "definition_version": "cash-goal-v1",
        "plain_english_name": "Progress to $1 million",
        "decision_question": (
            "How much accepted cash excluding GST has been collected "
            "against the $1 million goal?"
        ),
        "event_grain": "accepted settled cash, refund or approved bank event",
        "source_authority": {
            "stripe": "settled payment and refund events",
            "pt_minder": "successful payment events only",
            "bank": "independently approved manual cash events",
        },
        "numerator_definition": (
            "accepted net cash collected excluding GST inside the goal period"
        ),
        "denominator_definition": "100000000 AUD cents",
        "inclusion_rules": [
            "settled cash",
            "approved bank cash",
            "refunds as negative cash on refund date",
        ],
        "exclusion_rules": [
            "GST",
            "pending payments",
            "failed payments",
            "internal transfers",
            "duplicate processor records",
            "PT Minder Charge or displayed balance",
        ],
        "period_semantics": (
            "continuously rolling 365-day window ending at the latest "
            "accepted refresh; no calendar or financial-year reset"
        ),
        "minimum_freshness": {
            "stripe_hours": 14,
            "pt_minder_hours": 192,
        },
        "owner": "Peter Brown",
        "approval_state": "approved_shadow",
    },
)

CEO_SCORECARD_METRIC_ORDER = (
    "subscriber_to_sa_booking_rate",
    "leads_created",
    "sa_bookings_unique",
    "prequalification_completion_rate",
    "sa_show_rate",
    "assessment_conversion_unique",
    "onboarding_booking_speed_days",
    "onboarding_completion_speed_days",
    "successful_first_week_rate",
    "successful_first_week_speed_days",
)

CEO_SCORECARD_PERIOD_LABELS = {
    "week": "Previous completed week",
    "28d": "Last 28 completed days",
    "90d": "Last 90 completed days",
}

CEO_LEGACY_FALLBACK_METRICS = {
    "leads_created",
    "sa_bookings_unique",
    "prequalification_completion_rate",
    "sa_show_rate",
    "assessment_conversion_unique",
}


def _stable_id(*parts: Any) -> str:
    value = ":".join(str(part or "").strip().lower() for part in parts)
    return uuid.uuid5(uuid.NAMESPACE_URL, value).hex


def _datetime(value: datetime | str | None, field: str) -> datetime | None:
    if value is None:
        return None
    parsed = value
    if isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError(f"{field} must be an ISO datetime") from exc
    if not isinstance(parsed, datetime) or parsed.tzinfo is None:
        raise ValueError(f"{field} must include a timezone")
    return parsed.astimezone(UTC)


def _decimal_text(value: Any, field: str) -> str | None:
    if value is None:
        return None
    try:
        return format(Decimal(str(value)), "f")
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{field} must be numeric") from exc


def _confidence(value: str) -> str:
    cleaned = str(value or "").strip().lower()
    if cleaned not in CONFIDENCE_LEVELS:
        raise ValueError(
            "confidence must be verified, high, medium, low, "
            "legacy_aggregate or unresolved"
        )
    return cleaned


def _attendance_is_delivered(row: dict[str, Any]) -> bool:
    status = str(
        row.get("canonical_status") or row.get("status") or ""
    ).lower()
    return status == "showed" or (
        str(row.get("reconciliation_state") or "")
        == "feedback_closes_confirmed"
        and str(row.get("proposed_status") or "") == "showed"
        and bool(row.get("feedback_submission_ids"))
    )


def summarise_unique_conversion(
    attendance_rows: Iterable[dict[str, Any]],
    sales: Iterable[dict[str, Any]],
) -> dict[str, Any]:
    attended_series = {
        str(
            row.get("appointment_series_id")
            or row.get("appointment_id")
            or ""
        ).strip()
        for row in attendance_rows
        if _attendance_is_delivered(row)
        and not row.get("superseded")
    }
    attended_series.discard("")

    converted_series: set[str] = set()
    accepted_sale_ids: set[str] = set()
    service_mix: Counter[str] = Counter()
    unattributed_sales: list[str] = []

    for sale in sales:
        sale_id = str(sale.get("sale_id") or "").strip()
        if not sale_id or sale_id in accepted_sale_ids:
            continue
        if not bool(sale.get("qualifying_new_membership")):
            continue
        accepted_sale_ids.add(sale_id)

        components_seen: set[tuple[str, str]] = set()
        for component in sale.get("service_components") or []:
            service_type = str(
                component.get("service_type") or ""
            ).strip().lower()
            service_name = str(
                component.get("service_name") or ""
            ).strip().lower()
            key = (service_type, service_name)
            if service_type and key not in components_seen:
                components_seen.add(key)
                service_mix[service_type] += 1

        attributed = {
            str(item).strip()
            for item in (
                sale.get("appointment_series_ids")
                or [
                    sale.get("appointment_series_id")
                    or sale.get("appointment_id")
                ]
            )
            if str(item or "").strip()
        }
        qualifying = attributed & attended_series
        if qualifying:
            converted_series.update(qualifying)
        else:
            unattributed_sales.append(sale_id)

    denominator = len(attended_series)
    numerator = len(converted_series)
    return {
        "attended_appointment_series": denominator,
        "converted_appointment_series": numerator,
        "conversion_rate": (
            numerator / denominator if denominator else None
        ),
        "qualifying_sales": len(accepted_sale_ids),
        "service_components": dict(sorted(service_mix.items())),
        "unattributed_sale_ids": sorted(unattributed_sales),
    }


def attribute_sales_to_assessments(
    attendance_rows: Iterable[dict[str, Any]],
    sales: Iterable[dict[str, Any]],
    *,
    attribution_days: int = ASSESSMENT_ATTRIBUTION_DAYS,
) -> dict[str, Any]:
    if attribution_days < 1:
        raise ValueError("attribution_days must be positive")
    attended_by_person: dict[str, list[dict[str, Any]]] = {}
    for row in attendance_rows:
        if not _attendance_is_delivered(row):
            continue
        person_key = str(
            row.get("person_id")
            or row.get("contact_id")
            or ""
        ).strip()
        if not person_key:
            continue
        delivered_at = _datetime(
            row.get("end_at") or row.get("start_at"),
            "assessment delivered_at",
        )
        if delivered_at is None:
            continue
        attended_by_person.setdefault(person_key, []).append(
            {
                **row,
                "_delivered_at": delivered_at,
                "_series_id": str(
                    row.get("appointment_series_id")
                    or row.get("appointment_id")
                    or ""
                ).strip(),
            }
        )
    for rows in attended_by_person.values():
        rows.sort(key=lambda item: item["_delivered_at"], reverse=True)

    attributed_sales = []
    exceptions = []
    for raw_sale in sales:
        sale = dict(raw_sale)
        sale_id = str(sale.get("sale_id") or "").strip()
        if not sale_id:
            raise ValueError("sale_id is required")
        if (
            not bool(sale.get("qualifying_new_membership"))
            or bool(sale.get("returning_former_member"))
            or str(sale.get("sale_type") or "").lower()
            == "reactivation"
        ):
            sale["appointment_series_ids"] = []
            sale["attribution_state"] = (
                "reactivation_excluded"
                if bool(sale.get("returning_former_member"))
                or str(sale.get("sale_type") or "").lower()
                == "reactivation"
                else "non_acquisition_sale"
            )
            attributed_sales.append(sale)
            continue
        person_key = str(
            sale.get("person_id") or sale.get("contact_id") or ""
        ).strip()
        sold_at = _datetime(sale.get("sold_at"), "sold_at")
        if not person_key or sold_at is None:
            sale["appointment_series_ids"] = []
            sale["attribution_state"] = "missing_identity_or_time"
            attributed_sales.append(sale)
            exceptions.append(
                {
                    "sale_id": sale_id,
                    "code": "missing_identity_or_time",
                }
            )
            continue
        date_only = (
            str((sale.get("evidence") or {}).get("date_precision") or "")
            == "date_only"
        )
        if date_only:
            sold_day = sold_at.astimezone(BRISBANE_TZ).date()
            candidates = [
                row
                for row in attended_by_person.get(person_key, [])
                if row["_delivered_at"].astimezone(BRISBANE_TZ).date()
                <= sold_day
                and sold_day
                - row["_delivered_at"].astimezone(BRISBANE_TZ).date()
                <= timedelta(days=attribution_days)
            ]
        else:
            candidates = [
                row
                for row in attended_by_person.get(person_key, [])
                if row["_delivered_at"] <= sold_at
                and sold_at - row["_delivered_at"]
                <= timedelta(days=attribution_days)
            ]
        if not candidates:
            sale["appointment_series_ids"] = []
            sale["attribution_state"] = "no_attended_assessment_in_window"
            attributed_sales.append(sale)
            exceptions.append(
                {
                    "sale_id": sale_id,
                    "code": "no_attended_assessment_in_window",
                }
            )
            continue
        selected = candidates[0]
        sale["appointment_series_ids"] = [selected["_series_id"]]
        sale["attribution_state"] = "attributed"
        sale["attribution_rule_version"] = "assessment-conversion-v1"
        sale["attribution_evidence"] = {
            "assessment_appointment_id": selected.get("appointment_id"),
            "appointment_series_id": selected["_series_id"],
            "assessment_delivered_at": selected[
                "_delivered_at"
            ].isoformat(),
            "sale_at": sold_at.isoformat(),
            "window_days": attribution_days,
            "late_sale_after_no_sale_allowed": True,
        }
        attributed_sales.append(sale)
    return {
        "rule_version": "assessment-conversion-v1",
        "attribution_days": attribution_days,
        "sales": attributed_sales,
        "exceptions": exceptions,
    }


def completed_reporting_periods(
    as_of: datetime | str | None = None,
) -> dict[str, tuple[date, date]]:
    instant = _datetime(as_of or datetime.now(UTC), "as_of")
    if instant is None:
        raise ValueError("as_of is required")
    local_today = instant.astimezone(BRISBANE_TZ).date()
    yesterday = local_today - timedelta(days=1)
    current_week_monday = local_today - timedelta(
        days=local_today.weekday()
    )
    previous_week_end = current_week_monday - timedelta(days=1)
    previous_week_start = previous_week_end - timedelta(days=6)
    return {
        "week": (previous_week_start, previous_week_end),
        "28d": (yesterday - timedelta(days=27), yesterday),
        "90d": (yesterday - timedelta(days=89), yesterday),
    }


def rolling_cash_goal_window(
    as_of: datetime | str | None = None,
) -> tuple[datetime, datetime]:
    instant = _datetime(as_of or datetime.now(UTC), "as_of")
    if instant is None:
        raise ValueError("as_of is required")
    return instant - timedelta(days=365), instant


class ReportingV2Repository:
    def __init__(self, engine):
        self.engine = engine
        v2_metadata.create_all(self.engine)
        self.seed_core_metric_definitions()

    def seed_core_metric_definitions(self) -> None:
        for definition in CORE_METRIC_DEFINITIONS:
            self.register_metric_definition(definition)

    def register_metric_definition(
        self,
        definition: dict[str, Any],
    ) -> dict[str, Any]:
        required = (
            "metric_id",
            "definition_version",
            "plain_english_name",
            "decision_question",
            "event_grain",
            "period_semantics",
            "owner",
            "approval_state",
        )
        missing = [
            field for field in required if not str(definition.get(field) or "").strip()
        ]
        if missing:
            raise ValueError(
                "metric definition missing: " + ", ".join(missing)
            )
        material = {
            key: definition.get(key)
            for key in (
                "metric_id",
                "definition_version",
                "plain_english_name",
                "decision_question",
                "event_grain",
                "source_authority",
                "numerator_definition",
                "denominator_definition",
                "inclusion_rules",
                "exclusion_rules",
                "period_semantics",
                "minimum_freshness",
                "owner",
                "approval_state",
                "effective_from",
                "effective_to",
            )
        }
        definition_hash = fingerprint(material)
        values = {
            "metric_id": str(definition["metric_id"]).strip(),
            "definition_version": str(
                definition["definition_version"]
            ).strip(),
            "plain_english_name": str(
                definition["plain_english_name"]
            ).strip(),
            "decision_question": str(
                definition["decision_question"]
            ).strip(),
            "event_grain": str(definition["event_grain"]).strip(),
            "source_authority_json": canonical_json(
                definition.get("source_authority") or {}
            ),
            "numerator_definition": (
                str(definition.get("numerator_definition")).strip()
                if definition.get("numerator_definition") is not None
                else None
            ),
            "denominator_definition": (
                str(definition.get("denominator_definition")).strip()
                if definition.get("denominator_definition") is not None
                else None
            ),
            "inclusion_rules_json": canonical_json(
                definition.get("inclusion_rules") or []
            ),
            "exclusion_rules_json": canonical_json(
                definition.get("exclusion_rules") or []
            ),
            "period_semantics": str(
                definition["period_semantics"]
            ).strip(),
            "minimum_freshness_json": canonical_json(
                definition.get("minimum_freshness") or {}
            ),
            "owner": str(definition["owner"]).strip(),
            "approval_state": str(
                definition["approval_state"]
            ).strip(),
            "effective_from": definition.get("effective_from"),
            "effective_to": definition.get("effective_to"),
            "definition_hash": definition_hash,
            "created_at": datetime.now(UTC),
        }
        with self.engine.begin() as connection:
            existing = connection.execute(
                select(metric_definitions).where(
                    metric_definitions.c.metric_id == values["metric_id"],
                    metric_definitions.c.definition_version
                    == values["definition_version"],
                )
            ).mappings().first()
            if existing:
                if existing["definition_hash"] != definition_hash:
                    raise ValueError(
                        "metric definition versions are immutable; "
                        "create a new definition_version"
                    )
                return {
                    "status": "duplicate",
                    "metric_id": values["metric_id"],
                    "definition_version": values["definition_version"],
                }
            connection.execute(insert(metric_definitions).values(**values))
        return {
            "status": "accepted",
            "metric_id": values["metric_id"],
            "definition_version": values["definition_version"],
        }

    def accept_source_event(
        self,
        event: dict[str, Any],
    ) -> dict[str, Any]:
        source_system = str(event.get("source_system") or "").strip().lower()
        object_type = str(
            event.get("source_object_type") or ""
        ).strip().lower()
        source_event_id = str(
            event.get("source_event_id") or ""
        ).strip()
        if not source_system or not object_type or not source_event_id:
            raise ValueError(
                "source_system, source_object_type and source_event_id "
                "are required"
            )
        occurred_at = _datetime(event.get("occurred_at"), "occurred_at")
        observed_at = _datetime(event.get("observed_at"), "observed_at")
        effective_at = _datetime(event.get("effective_at"), "effective_at")
        if occurred_at is None or observed_at is None:
            raise ValueError("occurred_at and observed_at are required")
        acceptance_state = str(
            event.get("acceptance_state") or "accepted"
        ).strip().lower()
        if acceptance_state not in ACCEPTANCE_STATES:
            raise ValueError("invalid acceptance_state")
        confidence = _confidence(str(event.get("confidence") or "verified"))
        payload = event.get("payload")
        if not isinstance(payload, dict):
            raise ValueError("payload must be an object")
        payload_hash = fingerprint(payload)
        event_version_id = _stable_id(
            "v2-source-event",
            source_system,
            object_type,
            source_event_id,
            payload_hash,
        )
        values = {
            "event_version_id": event_version_id,
            "source_system": source_system,
            "source_object_type": object_type,
            "source_event_id": source_event_id,
            "source_object_id": str(
                event.get("source_object_id") or ""
            ).strip()
            or None,
            "source_version": str(
                event.get("source_version") or payload_hash
            ).strip(),
            "occurred_at": occurred_at,
            "effective_at": effective_at,
            "observed_at": observed_at,
            "accepted_at": datetime.now(UTC),
            "brisbane_local_date": occurred_at.astimezone(
                BRISBANE_TZ
            ).date().isoformat(),
            "source_run_id": str(event.get("source_run_id") or "").strip()
            or None,
            "source_snapshot_id": str(
                event.get("source_snapshot_id") or ""
            ).strip()
            or None,
            "payload_hash": payload_hash,
            "schema_version": int(
                event.get("schema_version")
                or REPORTING_V2_SCHEMA_VERSION
            ),
            "supersedes_event_version_id": str(
                event.get("supersedes_event_version_id") or ""
            ).strip()
            or None,
            "acceptance_state": acceptance_state,
            "rejection_reason": str(
                event.get("rejection_reason") or ""
            ).strip()
            or None,
            "confidence": confidence,
            "payload_json": canonical_json(payload),
        }
        if (
            acceptance_state != "accepted"
            and not values["rejection_reason"]
        ):
            raise ValueError(
                "rejection_reason is required for rejected or quarantined "
                "events"
            )
        with self.engine.begin() as connection:
            existing = connection.execute(
                select(source_events.c.event_version_id).where(
                    source_events.c.event_version_id == event_version_id
                )
            ).scalar()
            if existing:
                return {
                    "status": "duplicate",
                    "event_version_id": event_version_id,
                    "payload_hash": payload_hash,
                }
            if not values["supersedes_event_version_id"]:
                prior = connection.execute(
                    select(source_events.c.event_version_id)
                    .where(
                        source_events.c.source_system == source_system,
                        source_events.c.source_object_type == object_type,
                        source_events.c.source_event_id == source_event_id,
                    )
                    .order_by(source_events.c.accepted_at.desc())
                    .limit(1)
                ).scalar()
                values["supersedes_event_version_id"] = prior
            connection.execute(insert(source_events).values(**values))
        return {
            "status": "accepted",
            "event_version_id": event_version_id,
            "payload_hash": payload_hash,
            "brisbane_local_date": values["brisbane_local_date"],
            "supersedes_event_version_id": values[
                "supersedes_event_version_id"
            ],
        }

    def latest_source_event_payloads(
        self,
        source_system: str,
        source_object_type: str,
    ) -> list[dict[str, Any]]:
        source_system = str(source_system or "").strip().lower()
        source_object_type = str(source_object_type or "").strip().lower()
        if not source_system or not source_object_type:
            raise ValueError(
                "source_system and source_object_type are required"
            )
        with self.engine.begin() as connection:
            rows = connection.execute(
                select(source_events)
                .where(
                    source_events.c.source_system == source_system,
                    source_events.c.source_object_type
                    == source_object_type,
                    source_events.c.acceptance_state == "accepted",
                )
                .order_by(
                    source_events.c.observed_at.desc(),
                    source_events.c.accepted_at.desc(),
                    source_events.c.event_version_id.desc(),
                )
            ).mappings().all()
        latest: dict[str, dict[str, Any]] = {}
        for row in rows:
            latest.setdefault(str(row["source_event_id"]), row)
        return [
            {
                **json.loads(row["payload_json"]),
                "event_version_id": row["event_version_id"],
                "source_snapshot_id": row["source_snapshot_id"],
            }
            for row in latest.values()
        ]

    def record_cash_batch_shadow(
        self,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        if not isinstance(payload, dict):
            raise ValueError("payload must be an object")
        source_system = str(
            payload.get("source_system") or ""
        ).strip().lower()
        if source_system not in CASH_SOURCE_SYSTEMS:
            raise ValueError("cash source_system is not registered")
        source_run_id = str(
            payload.get("source_run_id") or ""
        ).strip()
        if not source_run_id:
            raise ValueError("source_run_id is required")
        observed_at = _datetime(
            payload.get("observed_at"),
            "observed_at",
        )
        if observed_at is None:
            raise ValueError("observed_at is required")
        complete = payload.get("complete")
        if not isinstance(complete, bool):
            raise ValueError("complete must be true or false")
        raw_events = payload.get("events")
        if not isinstance(raw_events, list) or len(raw_events) > 20000:
            raise ValueError(
                "events must be a list with at most 20000 entries"
            )

        cleaned_events = []
        seen_event_ids: set[str] = set()
        for position, raw in enumerate(raw_events, start=1):
            label = f"cash event {position}"
            if not isinstance(raw, dict):
                raise ValueError(f"{label} must be an object")
            source_event_id = str(
                raw.get("source_event_id") or ""
            ).strip()
            if (
                not source_event_id
                or source_event_id in seen_event_ids
            ):
                raise ValueError(
                    f"{label} requires a unique source_event_id"
                )
            seen_event_ids.add(source_event_id)
            event_type = str(
                raw.get("event_type") or ""
            ).strip().lower()
            if event_type not in CASH_EVENT_TYPES:
                raise ValueError(f"{label} has an invalid event_type")
            occurred_at = _datetime(
                raw.get("occurred_at"),
                f"{label} occurred_at",
            )
            if occurred_at is None:
                raise ValueError(f"{label} occurred_at is required")
            currency = str(
                raw.get("currency") or "AUD"
            ).strip().upper()
            if currency != "AUD":
                raise ValueError(
                    "Reporting V2 currently accepts AUD cash only"
                )
            try:
                gross_cents = int(raw.get("gross_amount_cents"))
                gst_cents = int(raw.get("gst_amount_cents"))
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"{label} amounts must be integer cents"
                ) from exc
            if gross_cents <= 0 or gross_cents > 100_000_000:
                raise ValueError(
                    f"{label} gross_amount_cents is out of range"
                )
            if gst_cents < 0 or gst_cents > gross_cents:
                raise ValueError(
                    f"{label} gst_amount_cents is out of range"
                )
            if (
                source_system == "bank_manual"
                and not str(raw.get("approved_by") or "").strip()
            ):
                raise ValueError(
                    f"{label} requires approved_by for bank cash"
                )
            sign = -1 if event_type == "refund" else 1
            cleaned_events.append(
                {
                    "source_event_id": source_event_id,
                    "occurred_at": occurred_at,
                    "event_type": event_type,
                    "currency": currency,
                    "gross_amount_cents": gross_cents,
                    "gst_amount_cents": gst_cents,
                    "net_amount_ex_gst_cents": sign
                    * (gross_cents - gst_cents),
                    "approved_by": (
                        str(raw.get("approved_by") or "").strip()
                        or None
                    ),
                    "evidence": raw.get("evidence") or {},
                }
            )

        batch_hash = fingerprint(
            {
                "source_system": source_system,
                "source_run_id": source_run_id,
                "observed_at": observed_at.isoformat(),
                "complete": complete,
                "events": [
                    {
                        **item,
                        "occurred_at": item[
                            "occurred_at"
                        ].isoformat(),
                    }
                    for item in cleaned_events
                ],
            }
        )
        with self.engine.begin() as connection:
            existing = connection.execute(
                select(cash_source_runs).where(
                    cash_source_runs.c.source_system == source_system,
                    cash_source_runs.c.source_run_id == source_run_id,
                )
            ).mappings().first()
            if existing and existing["payload_hash"] != batch_hash:
                raise ValueError(
                    "cash source runs are immutable; use a new "
                    "source_run_id"
                )
            if not existing:
                connection.execute(
                    insert(cash_source_runs).values(
                        source_system=source_system,
                        source_run_id=source_run_id,
                        observed_at=observed_at,
                        complete=int(complete),
                        event_count=len(cleaned_events),
                        payload_hash=batch_hash,
                        created_at=datetime.now(UTC),
                    )
                )

        event_results = []
        cash_event_values = []
        for item in cleaned_events:
            event_payload = {
                key: value
                for key, value in item.items()
                if key != "occurred_at"
            }
            payload_hash = fingerprint(event_payload)
            cash_event_values.append(
                {
                    "event_version_id": _stable_id(
                        "v2-source-event",
                        source_system,
                        "cash_event",
                        item["source_event_id"],
                        payload_hash,
                    ),
                    "source_system": source_system,
                    "source_object_type": "cash_event",
                    "source_event_id": item["source_event_id"],
                    "source_object_id": None,
                    "source_version": payload_hash,
                    "occurred_at": item["occurred_at"],
                    "effective_at": None,
                    "observed_at": observed_at,
                    "accepted_at": datetime.now(UTC),
                    "brisbane_local_date": item[
                        "occurred_at"
                    ].astimezone(BRISBANE_TZ).date().isoformat(),
                    "source_run_id": source_run_id,
                    "source_snapshot_id": str(
                        payload.get("source_snapshot_id") or ""
                    ).strip()
                    or None,
                    "payload_hash": payload_hash,
                    "schema_version": REPORTING_V2_SCHEMA_VERSION,
                    "supersedes_event_version_id": None,
                    "acceptance_state": "accepted",
                    "rejection_reason": None,
                    "confidence": (
                        "high"
                        if source_system == "bank_manual"
                        else "verified"
                    ),
                    "payload_json": canonical_json(event_payload),
                }
            )

        if cash_event_values:
            version_ids = [
                row["event_version_id"] for row in cash_event_values
            ]
            source_event_ids = [
                row["source_event_id"] for row in cash_event_values
            ]
            with self.engine.begin() as connection:
                existing_ids = set(
                    connection.execute(
                        select(source_events.c.event_version_id).where(
                            source_events.c.event_version_id.in_(
                                version_ids
                            )
                        )
                    ).scalars()
                )
                prior_rows = connection.execute(
                    select(
                        source_events.c.source_event_id,
                        source_events.c.event_version_id,
                    )
                    .where(
                        source_events.c.source_system == source_system,
                        source_events.c.source_object_type == "cash_event",
                        source_events.c.source_event_id.in_(
                            source_event_ids
                        ),
                    )
                    .order_by(source_events.c.accepted_at.desc())
                ).all()
                prior_by_event: dict[str, str] = {}
                for prior_event_id, prior_version_id in prior_rows:
                    prior_by_event.setdefault(
                        str(prior_event_id),
                        str(prior_version_id),
                    )
                new_values = []
                for row in cash_event_values:
                    if row["event_version_id"] in existing_ids:
                        event_results.append(
                            {
                                "status": "duplicate",
                                "event_version_id": row[
                                    "event_version_id"
                                ],
                                "payload_hash": row["payload_hash"],
                            }
                        )
                        continue
                    row["supersedes_event_version_id"] = (
                        prior_by_event.get(row["source_event_id"])
                    )
                    new_values.append(row)
                    event_results.append(
                        {
                            "status": "accepted",
                            "event_version_id": row[
                                "event_version_id"
                            ],
                            "payload_hash": row["payload_hash"],
                            "brisbane_local_date": row[
                                "brisbane_local_date"
                            ],
                            "supersedes_event_version_id": row[
                                "supersedes_event_version_id"
                            ],
                        }
                    )
                if new_values:
                    connection.execute(insert(source_events), new_values)
        goal = self.refresh_cash_goal_shadow(as_of=observed_at)
        return {
            "status": "duplicate" if existing else "accepted",
            "mode": "shadow",
            "publication_impact": "none",
            "source_system": source_system,
            "source_run_id": source_run_id,
            "event_count": len(cleaned_events),
            "event_results": event_results,
            "cash_goal": goal,
        }

    def latest_cash_source_run(
        self,
        source_system: str,
    ) -> dict[str, Any] | None:
        with self.engine.begin() as connection:
            row = connection.execute(
                select(cash_source_runs)
                .where(
                    cash_source_runs.c.source_system == source_system
                )
                .order_by(
                    cash_source_runs.c.observed_at.desc(),
                    cash_source_runs.c.created_at.desc(),
                )
                .limit(1)
            ).mappings().first()
        if row is None:
            return None
        return {
            "source_system": row["source_system"],
            "source_run_id": row["source_run_id"],
            "observed_at": row["observed_at"].isoformat(),
            "complete": bool(row["complete"]),
            "event_count": int(row["event_count"]),
        }

    def cash_period_summary(
        self,
        period_start: date | str,
        period_end: date | str,
        *,
        as_of: datetime | str | None = None,
    ) -> dict[str, Any]:
        start = (
            period_start
            if isinstance(period_start, date)
            else date.fromisoformat(str(period_start))
        )
        end = (
            period_end
            if isinstance(period_end, date)
            else date.fromisoformat(str(period_end))
        )
        observed_at = _datetime(as_of, "as_of") or datetime.now(UTC)
        with self.engine.begin() as connection:
            run_rows = connection.execute(
                select(cash_source_runs).order_by(
                    cash_source_runs.c.observed_at.desc()
                )
            ).mappings().all()
            event_rows = connection.execute(
                select(source_events)
                .where(
                    source_events.c.source_object_type == "cash_event"
                )
                .order_by(source_events.c.accepted_at.desc())
            ).mappings().all()
        latest_runs: dict[str, Any] = {}
        for row in run_rows:
            latest_runs.setdefault(str(row["source_system"]), row)
        blocked_reasons = []
        for source, maximum_hours in CASH_REQUIRED_SOURCE_HOURS.items():
            run = latest_runs.get(source)
            if run is None or not bool(run["complete"]):
                blocked_reasons.append(
                    f"{source} has no complete cash source run"
                )
                continue
            age_hours = (
                observed_at - run["observed_at"].astimezone(UTC)
            ).total_seconds() / 3600
            if age_hours < 0 or age_hours > maximum_hours:
                blocked_reasons.append(
                    f"{source} cash evidence is outside its freshness gate"
                )
        latest_events: dict[tuple[str, str], Any] = {}
        for row in event_rows:
            latest_events.setdefault(
                (
                    str(row["source_system"]),
                    str(row["source_event_id"]),
                ),
                row,
            )
        accepted = [
            row
            for row in latest_events.values()
            if row["acceptance_state"] == "accepted"
            and start.isoformat()
            <= str(row["brisbane_local_date"])
            <= end.isoformat()
        ]
        net_cents = sum(
            int(
                json.loads(row["payload_json"])[
                    "net_amount_ex_gst_cents"
                ]
            )
            for row in accepted
        )
        return {
            "available": not blocked_reasons,
            "period_start": start.isoformat(),
            "period_end": end.isoformat(),
            "net_cash_ex_gst_cents": (
                net_cents if not blocked_reasons else None
            ),
            "event_count": len(accepted),
            "blocked_reasons": blocked_reasons,
            "definition_version": "cash-period-v1",
        }

    def refresh_cash_goal_shadow(
        self,
        *,
        as_of: datetime | str | None = None,
    ) -> dict[str, Any]:
        goal_start, goal_end = rolling_cash_goal_window(as_of)
        with self.engine.begin() as connection:
            run_rows = connection.execute(
                select(cash_source_runs).order_by(
                    cash_source_runs.c.observed_at.desc()
                )
            ).mappings().all()
            event_rows = connection.execute(
                select(source_events)
                .where(
                    source_events.c.source_object_type
                    == "cash_event"
                )
                .order_by(source_events.c.accepted_at.desc())
            ).mappings().all()

        latest_runs: dict[str, Any] = {}
        for row in run_rows:
            latest_runs.setdefault(str(row["source_system"]), row)
        failures = []
        freshness = {}
        for source, maximum_hours in CASH_REQUIRED_SOURCE_HOURS.items():
            row = latest_runs.get(source)
            if row is None:
                failures.append(
                    f"{source} has no complete cash source run"
                )
                continue
            age_hours = (
                goal_end - row["observed_at"].astimezone(UTC)
            ).total_seconds() / 3600
            freshness[source] = {
                "source_run_id": row["source_run_id"],
                "observed_at": row["observed_at"].isoformat(),
                "age_hours": round(age_hours, 2),
                "complete": bool(row["complete"]),
            }
            if not bool(row["complete"]):
                failures.append(
                    f"{source} latest cash source run is incomplete"
                )
            elif age_hours < 0 or age_hours > maximum_hours:
                failures.append(
                    f"{source} cash evidence is outside its freshness gate"
                )

        latest_events: dict[tuple[str, str], Any] = {}
        for row in event_rows:
            latest_events.setdefault(
                (
                    str(row["source_system"]),
                    str(row["source_event_id"]),
                ),
                row,
            )
        accepted_rows = [
            row
            for row in latest_events.values()
            if row["acceptance_state"] == "accepted"
            and goal_start < row["occurred_at"].astimezone(UTC)
            <= goal_end
        ]
        net_cents = sum(
            int(
                json.loads(row["payload_json"])[
                    "net_amount_ex_gst_cents"
                ]
            )
            for row in accepted_rows
        )
        event_version_ids = [
            str(row["event_version_id"]) for row in accepted_rows
        ]
        unavailable_reason = "; ".join(failures) or None
        observation = self.record_metric_observation(
            metric_id="cash_goal_progress",
            definition_version="cash-goal-v1",
            period_start=goal_start.date().isoformat(),
            period_end=goal_end.date().isoformat(),
            value=(
                Decimal(net_cents) / Decimal(100_000_000)
                if not failures
                else None
            ),
            numerator=net_cents if not failures else None,
            denominator=100_000_000,
            unit="ratio",
            confidence="high" if not failures else "unresolved",
            event_version_ids=event_version_ids,
            source_freshness=freshness,
            publication_state="shadow",
            unavailable_reason=unavailable_reason,
            as_of_at=goal_end,
        )
        return {
            "mode": "shadow",
            "publication_impact": "none",
            "available": not failures,
            "net_cash_ex_gst_cents": (
                net_cents if not failures else None
            ),
            "event_count": len(accepted_rows),
            "window_start": goal_start.isoformat(),
            "window_end": goal_end.isoformat(),
            "source_freshness": freshness,
            "blocked_reasons": failures,
            "observation": observation,
        }

    def record_metric_observation(
        self,
        *,
        metric_id: str,
        definition_version: str,
        period_start: str,
        period_end: str,
        value: Any,
        numerator: Any,
        denominator: Any,
        unit: str,
        confidence: str,
        event_version_ids: Iterable[str] = (),
        source_snapshot_ids: Iterable[str] = (),
        source_freshness: dict[str, Any] | None = None,
        publication_state: str = "shadow",
        unavailable_reason: str | None = None,
        as_of_at: datetime | str | None = None,
    ) -> dict[str, Any]:
        confidence = _confidence(confidence)
        try:
            parsed_period_start = date.fromisoformat(period_start)
            parsed_period_end = date.fromisoformat(period_end)
        except ValueError as exc:
            raise ValueError(
                "period_start and period_end must be ISO dates"
            ) from exc
        if parsed_period_end < parsed_period_start:
            raise ValueError("period_end must not precede period_start")
        publication_state = str(publication_state).strip().lower()
        if publication_state not in PUBLICATION_STATES:
            raise ValueError("invalid publication_state")
        value_text = _decimal_text(value, "value")
        numerator_text = _decimal_text(numerator, "numerator")
        denominator_text = _decimal_text(denominator, "denominator")
        if value_text is None and not str(
            unavailable_reason or ""
        ).strip():
            raise ValueError(
                "unavailable_reason is required when value is unavailable"
            )
        if (
            str(unit).strip().lower() == "ratio"
            and value_text is not None
            and (
                denominator_text is None
                or Decimal(denominator_text) <= 0
            )
        ):
            raise ValueError(
                "a ratio value requires a positive denominator"
            )
        if publication_state == "accepted" and confidence not in {
            "verified",
            "high",
        }:
            raise ValueError(
                "accepted publication requires verified or high confidence"
            )
        event_ids = sorted({str(item) for item in event_version_ids if item})
        snapshot_ids = sorted(
            {str(item) for item in source_snapshot_ids if item}
        )
        parsed_as_of_at = _datetime(as_of_at, "as_of_at")
        material = {
            "metric_id": metric_id,
            "definition_version": definition_version,
            "period_start": period_start,
            "period_end": period_end,
            "value": value_text,
            "numerator": numerator_text,
            "denominator": denominator_text,
            "unit": unit,
            "confidence": confidence,
            "event_version_ids": event_ids,
            "source_snapshot_ids": snapshot_ids,
            "source_freshness": source_freshness or {},
            "publication_state": publication_state,
            "unavailable_reason": unavailable_reason,
            "as_of_at": (
                parsed_as_of_at.isoformat()
                if parsed_as_of_at is not None
                else None
            ),
        }
        event_set_fingerprint = fingerprint(
            {
                "event_version_ids": event_ids,
                "source_snapshot_ids": snapshot_ids,
            }
        )
        metric_run_id = _stable_id(
            "v2-metric-run",
            metric_id,
            definition_version,
            period_start,
            period_end,
            event_set_fingerprint,
            fingerprint(material),
        )
        observation_id = _stable_id(
            "v2-metric-observation",
            metric_run_id,
            metric_id,
            definition_version,
            period_start,
            period_end,
        )
        now = datetime.now(UTC)
        with self.engine.begin() as connection:
            definition = connection.execute(
                select(metric_definitions.c.definition_hash).where(
                    metric_definitions.c.metric_id == metric_id,
                    metric_definitions.c.definition_version
                    == definition_version,
                )
            ).scalar()
            if not definition:
                raise ValueError("metric definition is not registered")
            existing = connection.execute(
                select(
                    metric_observations.c.metric_observation_id
                ).where(
                    metric_observations.c.metric_observation_id
                    == observation_id
                )
            ).scalar()
            if existing:
                return {
                    "status": "duplicate",
                    "metric_observation_id": observation_id,
                    "metric_run_id": metric_run_id,
                }
            connection.execute(
                insert(metric_runs).values(
                    metric_run_id=metric_run_id,
                    started_at=now,
                    completed_at=now,
                    status="complete",
                    event_set_fingerprint=event_set_fingerprint,
                    source_freshness_json=canonical_json(
                        source_freshness or {}
                    ),
                    error=None,
                )
            )
            connection.execute(
                insert(metric_observations).values(
                    metric_observation_id=observation_id,
                    metric_id=metric_id,
                    definition_version=definition_version,
                    metric_run_id=metric_run_id,
                    period_start=period_start,
                    period_end=period_end,
                    as_of_at=parsed_as_of_at,
                    value=material["value"],
                    numerator=material["numerator"],
                    denominator=material["denominator"],
                    unit=str(unit).strip(),
                    confidence=confidence,
                    publication_state=publication_state,
                    unavailable_reason=unavailable_reason,
                    created_at=now,
                )
            )
            lineage_values = [
                {
                    "lineage_id": _stable_id(
                        "v2-lineage",
                        observation_id,
                        "event",
                        event_id,
                    ),
                    "metric_observation_id": observation_id,
                    "event_version_id": event_id,
                    "source_snapshot_id": None,
                    "lineage_role": "input_event",
                }
                for event_id in event_ids
            ]
            lineage_values.extend(
                {
                    "lineage_id": _stable_id(
                        "v2-lineage",
                        observation_id,
                        "snapshot",
                        snapshot_id,
                    ),
                    "metric_observation_id": observation_id,
                    "event_version_id": None,
                    "source_snapshot_id": snapshot_id,
                    "lineage_role": "source_snapshot",
                }
                for snapshot_id in snapshot_ids
            )
            if lineage_values:
                connection.execute(insert(metric_lineage), lineage_values)
        return {
            "status": "accepted",
            "metric_observation_id": observation_id,
            "metric_run_id": metric_run_id,
            "event_set_fingerprint": event_set_fingerprint,
        }

    def record_sa_attendance_shadow(
        self,
        rows: list[dict[str, Any]],
        summary: dict[str, Any],
        *,
        source_snapshot_id: str | None = None,
        as_of: datetime | str | None = None,
    ) -> dict[str, Any]:
        accepted_event_ids = []
        event_ids_by_appointment: dict[str, str] = {}
        for row in rows:
            reconciliation_state = str(
                row.get("reconciliation_state") or ""
            )
            confidence = str(
                row.get("attendance_confidence")
                or (
                    "verified"
                    if reconciliation_state == "terminal_consistent"
                    else "high"
                    if reconciliation_state == "feedback_closes_confirmed"
                    else "legacy_aggregate"
                    if reconciliation_state == "legacy_attended"
                    else "unresolved"
                    if reconciliation_state
                    in {"terminal_conflict", "elapsed_confirmed"}
                    else "medium"
                )
            )
            result = self.accept_source_event(
                {
                    "source_system": "ghl",
                    "source_object_type": "strength_assessment_appointment",
                    "source_event_id": row["appointment_id"],
                    "source_object_id": row["appointment_id"],
                    "occurred_at": row["start_at"],
                    "effective_at": row.get("status_effective_at")
                    or row.get("start_at"),
                    "observed_at": row.get("last_observed_at")
                    or row.get("observed_at")
                    or datetime.now(UTC),
                    "source_snapshot_id": source_snapshot_id,
                    "confidence": confidence,
                    "acceptance_state": (
                        "quarantined"
                        if confidence == "unresolved"
                        else "accepted"
                    ),
                    "rejection_reason": (
                        reconciliation_state
                        if confidence == "unresolved"
                        else None
                    ),
                    "payload": row,
                }
            )
            if confidence != "unresolved":
                accepted_event_ids.append(result["event_version_id"])
                event_ids_by_appointment[
                    str(row["appointment_id"])
                ] = result["event_version_id"]

        local_dates = sorted(
            {
                _datetime(row["start_at"], "start_at")
                .astimezone(BRISBANE_TZ)
                .date()
                .isoformat()
                for row in rows
            }
        )
        period_start = local_dates[0] if local_dates else "0001-01-01"
        period_end = local_dates[-1] if local_dates else "0001-01-01"
        showed = int(
            summary.get("tracked_showed", summary.get("showed")) or 0
        )
        no_show = int(
            summary.get("tracked_no_show", summary.get("no_show")) or 0
        )
        cancelled = int(summary.get("tracked_cancelled") or 0)
        denominator = showed + no_show
        cancellation_denominator = showed + no_show + cancelled
        unresolved = int(summary.get("unresolved") or 0)
        metric = self.record_metric_observation(
            metric_id="sa_show_rate",
            definition_version=str(
                summary.get("definition_version") or "sa-attendance-v2"
            ),
            period_start=period_start,
            period_end=period_end,
            value=(showed / denominator) if denominator else None,
            numerator=showed,
            denominator=denominator,
            unit="ratio",
            confidence="high" if unresolved == 0 else "unresolved",
            event_version_ids=accepted_event_ids,
            source_snapshot_ids=(
                [source_snapshot_id] if source_snapshot_id else []
            ),
            source_freshness={
                "strength_assessment_attendance": (
                    "accepted" if source_snapshot_id else "not_linked"
                )
            },
            publication_state="shadow",
            unavailable_reason=(
                "No showed or no-show outcomes"
                if denominator == 0
                else "Elapsed appointments remain unresolved"
                if unresolved
                else None
            ),
        )
        cancellation_metric = self.record_metric_observation(
            metric_id="sa_cancellation_rate",
            definition_version=str(
                summary.get("definition_version") or "sa-attendance-v2"
            ),
            period_start=period_start,
            period_end=period_end,
            value=(
                cancelled / cancellation_denominator
                if cancellation_denominator
                else None
            ),
            numerator=cancelled,
            denominator=cancellation_denominator,
            unit="ratio",
            confidence="high" if unresolved == 0 else "unresolved",
            event_version_ids=accepted_event_ids,
            source_snapshot_ids=(
                [source_snapshot_id] if source_snapshot_id else []
            ),
            source_freshness={
                "strength_assessment_attendance": (
                    "accepted" if source_snapshot_id else "not_linked"
                )
            },
            publication_state="shadow",
            unavailable_reason=(
                "No tracked terminal outcomes"
                if cancellation_denominator == 0
                else "Elapsed appointments remain unresolved"
                if unresolved
                else None
            ),
        )
        period_metrics: dict[str, dict[str, Any]] = {}
        cancellation_period_metrics: dict[str, dict[str, Any]] = {}
        for period_id, (start_date, end_date) in (
            completed_reporting_periods(as_of).items()
        ):
            selected = [
                row
                for row in rows
                if start_date
                <= _datetime(row["start_at"], "start_at")
                .astimezone(BRISBANE_TZ)
                .date()
                <= end_date
            ]
            showed_period = sum(
                _attendance_is_delivered(row)
                and row.get("show_rate_eligible", True)
                for row in selected
            )
            no_show_period = sum(
                str(
                    row.get("canonical_status")
                    or row.get("status")
                    or ""
                )
                == "no_show"
                and row.get("show_rate_eligible", True)
                for row in selected
            )
            cancelled_period = sum(
                str(
                    row.get("canonical_status")
                    or row.get("status")
                    or ""
                )
                == "cancelled"
                and row.get("cancellation_rate_eligible", True)
                for row in selected
            )
            unresolved_period = sum(
                str(row.get("reconciliation_state") or "")
                in {"elapsed_confirmed", "terminal_conflict"}
                for row in selected
            )
            denominator_period = showed_period + no_show_period
            cancellation_denominator_period = (
                showed_period + no_show_period + cancelled_period
            )
            period_event_ids = [
                event_ids_by_appointment[str(row["appointment_id"])]
                for row in selected
                if str(row["appointment_id"])
                in event_ids_by_appointment
            ]
            period_metrics[period_id] = self.record_metric_observation(
                metric_id="sa_show_rate",
                definition_version=str(
                    summary.get("definition_version")
                    or "sa-attendance-v2"
                ),
                period_start=start_date.isoformat(),
                period_end=end_date.isoformat(),
                value=(
                    showed_period / denominator_period
                    if denominator_period
                    else None
                ),
                numerator=showed_period,
                denominator=denominator_period,
                unit="ratio",
                confidence=(
                    "high"
                    if unresolved_period == 0
                    else "unresolved"
                ),
                event_version_ids=period_event_ids,
                source_snapshot_ids=(
                    [source_snapshot_id] if source_snapshot_id else []
                ),
                source_freshness={
                    "strength_assessment_attendance": (
                        "accepted" if source_snapshot_id else "not_linked"
                    )
                },
                publication_state="shadow",
                unavailable_reason=(
                    "No showed or no-show outcomes"
                    if denominator_period == 0
                    else "Elapsed appointments remain unresolved"
                    if unresolved_period
                    else None
                ),
                as_of_at=as_of,
            )
            cancellation_period_metrics[
                period_id
            ] = self.record_metric_observation(
                metric_id="sa_cancellation_rate",
                definition_version=str(
                    summary.get("definition_version")
                    or "sa-attendance-v2"
                ),
                period_start=start_date.isoformat(),
                period_end=end_date.isoformat(),
                value=(
                    cancelled_period / cancellation_denominator_period
                    if cancellation_denominator_period
                    else None
                ),
                numerator=cancelled_period,
                denominator=cancellation_denominator_period,
                unit="ratio",
                confidence=(
                    "high"
                    if unresolved_period == 0
                    else "unresolved"
                ),
                event_version_ids=period_event_ids,
                source_snapshot_ids=(
                    [source_snapshot_id] if source_snapshot_id else []
                ),
                source_freshness={
                    "strength_assessment_attendance": (
                        "accepted" if source_snapshot_id else "not_linked"
                    )
                },
                publication_state="shadow",
                unavailable_reason=(
                    "No tracked terminal outcomes"
                    if cancellation_denominator_period == 0
                    else "Elapsed appointments remain unresolved"
                    if unresolved_period
                    else None
                ),
                as_of_at=as_of,
            )
        conversion_period_metrics = (
            self.record_unique_conversion_shadow(
                attendance_rows=rows,
                sales=[],
                commercial_source_complete=False,
                as_of=as_of,
                source_snapshot_ids=(
                    [source_snapshot_id] if source_snapshot_id else []
                ),
            )
        )
        return {
            "source_events": len(accepted_event_ids),
            "quarantined_events": unresolved,
            "metric": metric,
            "cancellation_metric": cancellation_metric,
            "period_metrics": period_metrics,
            "cancellation_period_metrics": cancellation_period_metrics,
            "conversion_period_metrics": conversion_period_metrics,
        }

    def record_sa_listed_history_shadow(
        self,
        events: list[dict[str, Any]],
        *,
        observed_at: datetime | str,
        source_snapshot_id: str | None = None,
    ) -> dict[str, Any]:
        observed = _datetime(observed_at, "observed_at")
        if observed is None:
            raise ValueError("observed_at is required")
        accepted_event_ids: dict[str, str] = {}
        attendance_mismatches = 0
        for row in events:
            attendance_mismatch = bool(row.get("attendance_mismatch"))
            attendance_mismatches += attendance_mismatch
            result = self.accept_source_event(
                {
                    "source_system": "google_sheets",
                    "source_object_type": (
                        "listed_strength_assessment_history"
                    ),
                    "source_event_id": row["source_event_id"],
                    "source_object_id": (
                        f"Appointments:{row.get('row_number')}"
                    ),
                    "occurred_at": row["appointment_at"],
                    "observed_at": observed,
                    "source_snapshot_id": source_snapshot_id,
                    "confidence": "legacy_aggregate",
                    "acceptance_state": "accepted",
                    "payload": row,
                }
            )
            accepted_event_ids[
                str(row["source_event_id"])
            ] = result["event_version_id"]

        periods = {
            "history": (
                date(2025, 9, 19),
                observed.astimezone(BRISBANE_TZ).date(),
            ),
            **completed_reporting_periods(observed),
        }
        show_metrics: dict[str, dict[str, Any]] = {}
        conversion_metrics: dict[str, dict[str, Any]] = {}
        parallel_results: dict[str, dict[str, dict[str, Any]]] = {}
        for period_id, (start_date, end_date) in periods.items():
            show_period_start = max(start_date, date(2026, 3, 12))
            selected = [
                row
                for row in events
                if start_date
                <= date.fromisoformat(str(row["local_date"]))
                <= end_date
            ]
            eligible_show = [
                row for row in selected if row["show_rate_eligible"]
            ]
            legacy_show_population = [
                row
                for row in selected
                if date.fromisoformat(str(row["local_date"]))
                >= show_period_start
            ]
            showed = sum(
                row["listed_show"] == "Y" for row in eligible_show
            )
            attended = [
                row
                for row in selected
                if row["conversion_denominator_eligible"]
            ]
            converted = sum(
                row["conversion_numerator_eligible"] for row in selected
            )
            show_event_ids = [
                accepted_event_ids[row["source_event_id"]]
                for row in eligible_show
                if row["source_event_id"] in accepted_event_ids
            ]
            conversion_event_ids = [
                accepted_event_ids[row["source_event_id"]]
                for row in selected
                if (
                    row["conversion_denominator_eligible"]
                    or row["conversion_numerator_eligible"]
                )
                if row["source_event_id"] in accepted_event_ids
            ]
            common = {
                "period_start": start_date.isoformat(),
                "period_end": end_date.isoformat(),
                "unit": "ratio",
                "confidence": "legacy_aggregate",
                "source_snapshot_ids": (
                    [source_snapshot_id] if source_snapshot_id else []
                ),
                "source_freshness": {
                    "google_sheets_appointments": "accepted"
                },
                "publication_state": "shadow",
                "as_of_at": observed,
            }
            show_metrics[period_id] = self.record_metric_observation(
                metric_id="sa_listed_show_rate",
                definition_version="sa-listed-show-v1",
                period_start=show_period_start.isoformat(),
                value=(
                    showed / len(eligible_show)
                    if eligible_show
                    else None
                ),
                numerator=showed,
                denominator=len(eligible_show),
                event_version_ids=show_event_ids,
                unavailable_reason=(
                    None
                    if eligible_show
                    else "No explicit listed Y or N outcomes in the period"
                ),
                **{
                    key: value
                    for key, value in common.items()
                    if key != "period_start"
                },
            )
            conversion_metrics[
                period_id
            ] = self.record_metric_observation(
                metric_id="sa_listed_conversion_rate",
                definition_version="sa-listed-conversion-v1",
                value=converted / len(attended) if attended else None,
                numerator=converted,
                denominator=len(attended),
                event_version_ids=conversion_event_ids,
                unavailable_reason=(
                    None
                    if attended
                    else "No eligible attended assessments in the period"
                ),
                **common,
            )
            blank_show_outcomes = (
                len(legacy_show_population) - len(eligible_show)
            )
            legacy_show_value = (
                showed / len(legacy_show_population)
                if legacy_show_population
                else None
            )
            governed_show_value = (
                showed / len(eligible_show)
                if eligible_show
                else None
            )
            conversion_value = (
                converted / len(attended) if attended else None
            )
            parallel_results[period_id] = {
                "show_rate": self.record_parallel_result(
                    metric_id="sa_listed_show_rate",
                    definition_version="sa-listed-show-v1",
                    period_start=show_period_start.isoformat(),
                    period_end=end_date.isoformat(),
                    legacy_value=legacy_show_value,
                    v2_value=governed_show_value,
                    variance_classification=(
                        "exact_match"
                        if blank_show_outcomes == 0
                        else "legacy_defect"
                    ),
                    unexplained_event_count=0,
                    unexplained_cents=0,
                    evidence={
                        "legacy_denominator": len(
                            legacy_show_population
                        ),
                        "governed_denominator": len(eligible_show),
                        "showed": showed,
                        "blank_attendance_rows": blank_show_outcomes,
                        "explanation": (
                            "The workbook includes blank attendance rows in "
                            "the show-rate denominator; Reporting V2 uses "
                            "only explicit Y or N outcomes."
                            if blank_show_outcomes
                            else "The workbook and Reporting V2 match."
                        ),
                    },
                ),
                "conversion_rate": self.record_parallel_result(
                    metric_id="sa_listed_conversion_rate",
                    definition_version="sa-listed-conversion-v1",
                    period_start=start_date.isoformat(),
                    period_end=end_date.isoformat(),
                    legacy_value=conversion_value,
                    v2_value=conversion_value,
                    variance_classification="exact_match",
                    unexplained_event_count=0,
                    unexplained_cents=0,
                    evidence={
                        "legacy_denominator": len(attended),
                        "governed_denominator": len(attended),
                        "converted": converted,
                        "attendance_mismatches": sum(
                            bool(row.get("attendance_mismatch"))
                            for row in selected
                        ),
                    },
                ),
            }
        return {
            "source_events": len(accepted_event_ids),
            "quarantined_events": 0,
            "attendance_mismatches": attendance_mismatches,
            "show_metrics": show_metrics,
            "conversion_metrics": conversion_metrics,
            "parallel_results": parallel_results,
            "publication_impact": "none",
        }

    def record_acquisition_onboarding_shadow(
        self,
        *,
        lead_events: list[dict[str, Any]],
        prequalification_eligible_events: list[dict[str, Any]],
        prequalification_events: list[dict[str, Any]],
        onboarding_cases: list[dict[str, Any]],
        as_of: datetime | str | None = None,
        source_snapshot_ids: Iterable[str] = (),
    ) -> dict[str, dict[str, dict[str, Any]]]:
        results: dict[str, dict[str, dict[str, Any]]] = {}
        completed_appointments = {
            str(row.get("appointment_id") or "")
            for row in prequalification_events
            if row.get("appointment_id")
        }
        for period_id, (start_date, end_date) in (
            completed_reporting_periods(as_of).items()
        ):
            leads = {
                str(row.get("source_event_id") or "")
                for row in lead_events
                if start_date
                <= _datetime(row["occurred_at"], "occurred_at")
                .astimezone(BRISBANE_TZ)
                .date()
                <= end_date
            }
            leads.discard("")
            eligible = {
                str(row.get("appointment_id") or "")
                for row in prequalification_eligible_events
                if start_date
                <= _datetime(row["occurred_at"], "occurred_at")
                .astimezone(BRISBANE_TZ)
                .date()
                <= end_date
            }
            eligible.discard("")
            completed = eligible & completed_appointments
            selected_cases = [
                row
                for row in onboarding_cases
                if start_date
                <= _datetime(row["sold_at"], "sold_at")
                .astimezone(BRISBANE_TZ)
                .date()
                <= end_date
            ]
            booking_days = [
                int(row["booking_days"])
                for row in selected_cases
                if row.get("booking_days") is not None
            ]
            completion_days = [
                int(row["completion_days"])
                for row in selected_cases
                if row.get("completion_days") is not None
            ]
            results[period_id] = {
                "leads": self.record_metric_observation(
                    metric_id="leads_created",
                    definition_version="ghl-leads-v1",
                    period_start=start_date.isoformat(),
                    period_end=end_date.isoformat(),
                    value=len(leads),
                    numerator=len(leads),
                    denominator=None,
                    unit="count",
                    confidence="verified",
                    source_snapshot_ids=source_snapshot_ids,
                    publication_state="shadow",
                    as_of_at=as_of,
                ),
                "bookings": self.record_metric_observation(
                    metric_id="sa_bookings_unique",
                    definition_version="ghl-sa-bookings-v1",
                    period_start=start_date.isoformat(),
                    period_end=end_date.isoformat(),
                    value=len(eligible),
                    numerator=len(eligible),
                    denominator=None,
                    unit="count",
                    confidence="verified",
                    source_snapshot_ids=source_snapshot_ids,
                    publication_state="shadow",
                    as_of_at=as_of,
                ),
                "prequalification": self.record_metric_observation(
                    metric_id="prequalification_completion_rate",
                    definition_version="ghl-prequalification-v1",
                    period_start=start_date.isoformat(),
                    period_end=end_date.isoformat(),
                    value=(
                        len(completed) / len(eligible)
                        if eligible
                        else None
                    ),
                    numerator=len(completed),
                    denominator=len(eligible),
                    unit="ratio",
                    confidence="high",
                    source_snapshot_ids=source_snapshot_ids,
                    publication_state="shadow",
                    unavailable_reason=(
                        None
                        if eligible
                        else "No eligible Strength Assessment bookings"
                    ),
                    as_of_at=as_of,
                ),
                "onboarding_booking_speed": self.record_metric_observation(
                    metric_id="onboarding_booking_speed_days",
                    definition_version="ghl-onboarding-booking-v1",
                    period_start=start_date.isoformat(),
                    period_end=end_date.isoformat(),
                    value=(
                        sum(booking_days) / len(booking_days)
                        if booking_days
                        else None
                    ),
                    numerator=sum(booking_days) if booking_days else None,
                    denominator=len(booking_days),
                    unit="days",
                    confidence="high",
                    source_snapshot_ids=source_snapshot_ids,
                    publication_state="shadow",
                    unavailable_reason=(
                        None
                        if booking_days
                        else "No qualifying sales with an onboarding booking"
                    ),
                    as_of_at=as_of,
                ),
                "onboarding_completion_speed": (
                    self.record_metric_observation(
                        metric_id="onboarding_completion_speed_days",
                        definition_version="ghl-onboarding-completion-v1",
                        period_start=start_date.isoformat(),
                        period_end=end_date.isoformat(),
                        value=(
                            sum(completion_days) / len(completion_days)
                            if completion_days
                            else None
                        ),
                        numerator=(
                            sum(completion_days)
                            if completion_days
                            else None
                        ),
                        denominator=len(completion_days),
                        unit="days",
                        confidence=(
                            "verified" if completion_days else "unresolved"
                        ),
                        source_snapshot_ids=source_snapshot_ids,
                        publication_state="shadow",
                        unavailable_reason=(
                            None
                            if completion_days
                            else "GHL onboarding completion statuses are not "
                            "being recorded"
                        ),
                        as_of_at=as_of,
                    )
                ),
            }
        return results

    def record_subscriber_booking_shadow(
        self,
        *,
        period_metrics: dict[str, dict[str, Any]],
        as_of: datetime | str | None = None,
        source_snapshot_ids: Iterable[str] = (),
    ) -> dict[str, dict[str, Any]]:
        results: dict[str, dict[str, Any]] = {}
        for period_id, period in period_metrics.items():
            denominator = int(period.get("new_subscribers") or 0)
            numerator = int(
                period.get("subscribers_booking_assessment") or 0
            )
            results[period_id] = self.record_metric_observation(
                metric_id="subscriber_to_sa_booking_rate",
                definition_version="ghl-subscriber-sa-booking-v1",
                period_start=str(period["period_start"]),
                period_end=str(period["period_end"]),
                value=(numerator / denominator if denominator else None),
                numerator=numerator,
                denominator=denominator,
                unit="ratio",
                confidence="high",
                source_snapshot_ids=source_snapshot_ids,
                publication_state="shadow",
                unavailable_reason=(
                    None
                    if denominator
                    else "No new website subscribers in this period"
                ),
                as_of_at=as_of,
            )
        return results

    def record_onboarding_activation_shadow(
        self,
        *,
        activation_cases: list[dict[str, Any]],
        source_complete: bool,
        as_of: datetime | str | None = None,
        source_snapshot_ids: Iterable[str] = (),
    ) -> dict[str, dict[str, dict[str, Any]]]:
        results: dict[str, dict[str, dict[str, Any]]] = {}
        observed_at = _datetime(
            as_of or datetime.now(UTC), "as_of"
        )
        for period_id, (start_date, end_date) in (
            completed_reporting_periods(observed_at).items()
        ):
            selected = [
                row
                for row in activation_cases
                if start_date
                <= _datetime(row["sold_at"], "sold_at")
                .astimezone(BRISBANE_TZ)
                .date()
                <= end_date
            ]
            mature = [
                row
                for row in selected
                if (
                    observed_at.astimezone(BRISBANE_TZ).date()
                    - _datetime(row["sold_at"], "sold_at")
                    .astimezone(BRISBANE_TZ)
                    .date()
                ).days
                >= 9
            ]
            activated = [
                row
                for row in mature
                if row.get("activation_days") is not None
            ]
            activation_days = [
                int(row["activation_days"]) for row in activated
            ]
            available = bool(source_complete and mature)
            confidence = "high" if source_complete else "unresolved"
            results[period_id] = {
                "successful_first_week_rate": (
                    self.record_metric_observation(
                        metric_id="successful_first_week_rate",
                        definition_version="successful-first-week-v1",
                        period_start=start_date.isoformat(),
                        period_end=end_date.isoformat(),
                        value=(
                            len(activated) / len(mature)
                            if available
                            else None
                        ),
                        numerator=len(activated) if available else None,
                        denominator=len(mature),
                        unit="ratio",
                        confidence=confidence,
                        source_snapshot_ids=source_snapshot_ids,
                        publication_state="shadow",
                        unavailable_reason=(
                            None
                            if available
                            else (
                                "The GHL or Trainerize activation source is "
                                "incomplete"
                                if not source_complete
                                else "No qualifying sales are at least nine "
                                "days old in this period"
                            )
                        ),
                        as_of_at=observed_at,
                    )
                ),
                "successful_first_week_speed": (
                    self.record_metric_observation(
                        metric_id="successful_first_week_speed_days",
                        definition_version="successful-first-week-v1",
                        period_start=start_date.isoformat(),
                        period_end=end_date.isoformat(),
                        value=(
                            sum(activation_days) / len(activation_days)
                            if activation_days and source_complete
                            else None
                        ),
                        numerator=(
                            sum(activation_days)
                            if activation_days and source_complete
                            else None
                        ),
                        denominator=len(activation_days),
                        unit="days",
                        confidence=confidence,
                        source_snapshot_ids=source_snapshot_ids,
                        publication_state="shadow",
                        unavailable_reason=(
                            None
                            if activation_days and source_complete
                            else (
                                "The GHL or Trainerize activation source is "
                                "incomplete"
                                if not source_complete
                                else "No new members completed every "
                                "successful-first-week requirement"
                            )
                        ),
                        as_of_at=observed_at,
                    )
                ),
            }
        return results

    def record_unique_conversion_shadow(
        self,
        *,
        attendance_rows: list[dict[str, Any]],
        sales: list[dict[str, Any]],
        commercial_source_complete: bool,
        as_of: datetime | str | None = None,
        source_snapshot_ids: Iterable[str] = (),
    ) -> dict[str, dict[str, Any]]:
        results: dict[str, dict[str, Any]] = {}
        for period_id, (start_date, end_date) in (
            completed_reporting_periods(as_of).items()
        ):
            selected_attendance = [
                row
                for row in attendance_rows
                if start_date
                <= _datetime(row["start_at"], "start_at")
                .astimezone(BRISBANE_TZ)
                .date()
                <= end_date
            ]
            summary = summarise_unique_conversion(
                selected_attendance,
                sales if commercial_source_complete else [],
            )
            attended = summary["attended_appointment_series"]
            contains_legacy_attendance = any(
                str(
                    row.get("canonical_status")
                    or row.get("status")
                    or ""
                ).lower()
                == "showed"
                and str(row.get("attendance_confidence") or "").lower()
                == "legacy_aggregate"
                for row in selected_attendance
            )
            if commercial_source_complete:
                value = summary["conversion_rate"]
                numerator = summary["converted_appointment_series"]
                unavailable_reason = (
                    "No attended Strength Assessments in the period"
                    if attended == 0
                    else None
                )
                confidence = (
                    "legacy_aggregate"
                    if contains_legacy_attendance
                    else "high"
                )
            else:
                value = None
                numerator = None
                unavailable_reason = (
                    "The governed commercial sale event bridge is not "
                    "complete"
                )
                confidence = "unresolved"
            results[period_id] = self.record_metric_observation(
                metric_id="assessment_conversion_unique",
                definition_version="assessment-conversion-v1",
                period_start=start_date.isoformat(),
                period_end=end_date.isoformat(),
                value=value,
                numerator=numerator,
                denominator=attended,
                unit="ratio",
                confidence=confidence,
                source_snapshot_ids=source_snapshot_ids,
                publication_state="shadow",
                unavailable_reason=unavailable_reason,
                as_of_at=as_of,
            )
        return results

    def link_appointment_series(
        self,
        *,
        appointment_id: str,
        appointment_series_id: str,
        relation_type: str,
        superseded: bool,
        confidence: str,
        evidence: dict[str, Any],
    ) -> dict[str, Any]:
        if relation_type not in {
            "root",
            "reschedule",
            "duplicate_correction",
            "repeat_assessment",
        }:
            raise ValueError("invalid appointment-series relation_type")
        confidence = _confidence(confidence)
        link_id = _stable_id("v2-appointment-series", appointment_id)
        values = {
            "link_id": link_id,
            "appointment_id": appointment_id,
            "appointment_series_id": appointment_series_id,
            "relation_type": relation_type,
            "superseded": int(bool(superseded)),
            "confidence": confidence,
            "evidence_json": canonical_json(evidence),
            "created_at": datetime.now(UTC),
        }
        with self.engine.begin() as connection:
            existing = connection.execute(
                select(appointment_series_links).where(
                    appointment_series_links.c.appointment_id
                    == appointment_id
                )
            ).mappings().first()
            if existing:
                same = (
                    existing["appointment_series_id"]
                    == appointment_series_id
                    and existing["relation_type"] == relation_type
                    and existing["superseded"] == int(bool(superseded))
                    and existing["confidence"] == confidence
                    and existing["evidence_json"]
                    == canonical_json(evidence)
                )
                if not same:
                    raise ValueError(
                        "appointment-series links are immutable; "
                        "record a governed correction"
                    )
                return {"status": "duplicate", "link_id": link_id}
            connection.execute(
                insert(appointment_series_links).values(**values)
            )
        return {"status": "accepted", "link_id": link_id}

    def record_sale(self, sale: dict[str, Any]) -> dict[str, Any]:
        sale_id = str(sale.get("sale_id") or "").strip()
        source_system = str(
            sale.get("source_system") or ""
        ).strip().lower()
        source_sale_id = str(
            sale.get("source_sale_id") or sale_id
        ).strip()
        if not sale_id or not source_system or not source_sale_id:
            raise ValueError(
                "sale_id, source_system and source_sale_id are required"
            )
        sold_at = _datetime(sale.get("sold_at"), "sold_at")
        if sold_at is None:
            raise ValueError("sold_at is required")
        confidence = _confidence(str(sale.get("confidence") or "verified"))
        currency = str(sale.get("currency") or "AUD").strip().upper()
        if currency != "AUD":
            raise ValueError("Reporting V2 currently accepts AUD sales only")
        amount_cents = sale.get("amount_cents")
        if amount_cents is not None:
            amount_cents = int(amount_cents)
        components = sale.get("service_components") or []
        if not isinstance(components, list) or not components:
            raise ValueError("sale requires at least one service component")
        attributions = sale.get("appointment_series_ids") or []
        if not isinstance(attributions, list):
            raise ValueError("appointment_series_ids must be a list")
        values = {
            "sale_id": sale_id,
            "person_id": str(sale.get("person_id") or "").strip() or None,
            "source_system": source_system,
            "source_sale_id": source_sale_id,
            "sold_at": sold_at,
            "brisbane_local_date": sold_at.astimezone(
                BRISBANE_TZ
            ).date().isoformat(),
            "sale_type": str(
                sale.get("sale_type") or "membership"
            ).strip(),
            "qualifying_new_membership": int(
                bool(sale.get("qualifying_new_membership"))
            ),
            "amount_cents": amount_cents,
            "currency": currency,
            "confidence": confidence,
            "source_event_version_id": str(
                sale.get("source_event_version_id") or ""
            ).strip()
            or None,
            "evidence_json": canonical_json(sale.get("evidence") or {}),
        }
        with self.engine.begin() as connection:
            existing = connection.execute(
                select(sale_events.c.sale_id).where(
                    sale_events.c.sale_id == sale_id
                )
            ).scalar()
            if existing:
                return {"status": "duplicate", "sale_id": sale_id}
            connection.execute(insert(sale_events).values(**values))
            seen_components: set[tuple[str, str]] = set()
            for component in components:
                service_type = str(
                    component.get("service_type") or ""
                ).strip().lower()
                service_name = str(
                    component.get("service_name") or ""
                ).strip()
                if not service_type:
                    raise ValueError(
                        "service component requires service_type"
                    )
                key = (service_type, service_name.lower())
                if key in seen_components:
                    continue
                seen_components.add(key)
                connection.execute(
                    insert(sale_service_components).values(
                        component_id=_stable_id(
                            "v2-sale-component",
                            sale_id,
                            service_type,
                            service_name,
                        ),
                        sale_id=sale_id,
                        service_type=service_type,
                        service_name=service_name or None,
                        quantity=(
                            str(component.get("quantity"))
                            if component.get("quantity") is not None
                            else None
                        ),
                        unit=str(component.get("unit") or "").strip()
                        or None,
                        effective_from=component.get("effective_from"),
                        effective_to=component.get("effective_to"),
                    )
                )
            for series_id in sorted(
                {str(item).strip() for item in attributions if str(item).strip()}
            ):
                connection.execute(
                    insert(sale_attributions).values(
                        attribution_id=_stable_id(
                            "v2-sale-attribution",
                            sale_id,
                            series_id,
                            sale.get(
                                "attribution_rule_version",
                                "assessment-conversion-v1",
                            ),
                        ),
                        sale_id=sale_id,
                        appointment_series_id=series_id,
                        attribution_rule_version=str(
                            sale.get(
                                "attribution_rule_version",
                                "assessment-conversion-v1",
                            )
                        ),
                        confidence=confidence,
                        accepted=int(bool(sale.get("attribution_accepted", False))),
                        evidence_json=canonical_json(
                            sale.get("attribution_evidence") or {}
                        ),
                    )
                )
        return {
            "status": "accepted",
            "sale_id": sale_id,
            "service_component_count": len(seen_components),
            "attribution_count": len(
                {str(item).strip() for item in attributions if str(item).strip()}
            ),
        }

    def submit_manual_input(
        self,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        required = (
            "input_type",
            "effective_date",
            "value",
            "unit",
            "source_reference",
            "reason",
            "submitted_by",
        )
        missing = [
            field
            for field in required
            if payload.get(field) is None
            or not str(payload.get(field)).strip()
        ]
        if missing:
            raise ValueError(
                "manual input missing: " + ", ".join(missing)
            )
        material = {key: payload.get(key) for key in required}
        try:
            date.fromisoformat(str(payload["effective_date"]).strip())
        except ValueError as exc:
            raise ValueError(
                "effective_date must be an ISO date"
            ) from exc
        material["supersedes_input_id"] = payload.get(
            "supersedes_input_id"
        )
        submitted_at = _datetime(
            payload.get("submitted_at") or datetime.now(UTC),
            "submitted_at",
        )
        payload_hash = fingerprint(material)
        input_id = str(payload.get("input_id") or "").strip() or _stable_id(
            "v2-manual-input",
            payload_hash,
            submitted_at.isoformat(),
        )
        values = {
            "input_id": input_id,
            "input_type": str(payload["input_type"]).strip().lower(),
            "effective_date": str(payload["effective_date"]).strip(),
            "value": str(payload["value"]).strip(),
            "unit": str(payload["unit"]).strip(),
            "source_reference": str(
                payload["source_reference"]
            ).strip(),
            "reason": str(payload["reason"]).strip(),
            "submitted_by": str(payload["submitted_by"]).strip(),
            "submitted_at": submitted_at,
            "approval_state": "pending",
            "supersedes_input_id": str(
                payload.get("supersedes_input_id") or ""
            ).strip()
            or None,
            "payload_hash": payload_hash,
        }
        with self.engine.begin() as connection:
            existing = connection.execute(
                select(manual_input_events.c.input_id).where(
                    manual_input_events.c.input_id == input_id
                )
            ).scalar()
            if existing:
                return {"status": "duplicate", "input_id": input_id}
            connection.execute(insert(manual_input_events).values(**values))
        return {
            "status": "pending",
            "input_id": input_id,
            "accepted_for_metrics": False,
        }

    def decide_manual_input(
        self,
        input_id: str,
        *,
        decision: str,
        decided_by: str,
        reason: str,
    ) -> dict[str, Any]:
        decision = str(decision).strip().lower()
        if decision not in {"accepted", "rejected"}:
            raise ValueError("decision must be accepted or rejected")
        if not decided_by.strip() or not reason.strip():
            raise ValueError("decided_by and reason are required")
        now = datetime.now(UTC)
        decision_id = _stable_id(
            "v2-manual-decision",
            input_id,
            decision,
            now.isoformat(),
        )
        with self.engine.begin() as connection:
            row = connection.execute(
                select(manual_input_events).where(
                    manual_input_events.c.input_id == input_id
                )
            ).mappings().first()
            if not row:
                raise ValueError("manual input was not found")
            if row["approval_state"] != "pending":
                raise ValueError("manual input has already been decided")
            if row["submitted_by"].strip().lower() == decided_by.strip().lower():
                raise ValueError(
                    "manual input requires independent approval"
                )
            connection.execute(
                insert(manual_input_decisions).values(
                    decision_id=decision_id,
                    input_id=input_id,
                    decision=decision,
                    decided_by=decided_by.strip(),
                    decided_at=now,
                    reason=reason.strip(),
                )
            )
            connection.execute(
                update(manual_input_events)
                .where(manual_input_events.c.input_id == input_id)
                .values(approval_state=decision)
            )
        return {
            "status": decision,
            "input_id": input_id,
            "accepted_for_metrics": decision == "accepted",
        }

    def record_parallel_result(
        self,
        *,
        metric_id: str,
        definition_version: str,
        period_start: str,
        period_end: str,
        legacy_value: Any,
        v2_value: Any,
        variance_classification: str,
        unexplained_event_count: int,
        unexplained_cents: int,
        evidence: dict[str, Any],
        request_cutover_acceptance: bool = False,
    ) -> dict[str, Any]:
        allowed_classifications = {
            "exact_match",
            "v2_defect",
            "legacy_defect",
            "timing",
            "approved_definition_change",
            "unresolved",
        }
        if variance_classification not in allowed_classifications:
            raise ValueError("invalid variance_classification")
        legacy = _decimal_text(legacy_value, "legacy_value")
        v2 = _decimal_text(v2_value, "v2_value")
        variance = (
            format(Decimal(v2) - Decimal(legacy), "f")
            if legacy is not None and v2 is not None
            else None
        )
        unexplained_event_count = int(unexplained_event_count)
        unexplained_cents = int(unexplained_cents)
        can_pass = (
            unexplained_event_count == 0
            and unexplained_cents == 0
            and variance_classification
            in {
                "exact_match",
                "legacy_defect",
                "approved_definition_change",
                "timing",
            }
        )
        if request_cutover_acceptance and not can_pass:
            raise ValueError(
                "cutover cannot be accepted with unexplained variance"
            )
        state = (
            "accepted_for_cutover"
            if request_cutover_acceptance
            else "passed"
            if can_pass
            else "failed"
        )
        comparison_material = {
            "legacy_value": legacy,
            "v2_value": v2,
            "variance": variance,
            "variance_classification": variance_classification,
            "unexplained_event_count": unexplained_event_count,
            "unexplained_cents": unexplained_cents,
            "acceptance_state": state,
            "evidence": evidence,
        }
        comparison_fingerprint = fingerprint(comparison_material)
        comparison_id = _stable_id(
            "v2-parallel",
            metric_id,
            definition_version,
            period_start,
            period_end,
            comparison_fingerprint,
        )
        values = {
            "comparison_id": comparison_id,
            "metric_id": metric_id,
            "definition_version": definition_version,
            "period_start": period_start,
            "period_end": period_end,
            "legacy_value": legacy,
            "v2_value": v2,
            "variance": variance,
            "variance_classification": variance_classification,
            "unexplained_event_count": unexplained_event_count,
            "unexplained_cents": unexplained_cents,
            "acceptance_state": state,
            "evidence_json": canonical_json(evidence),
            "comparison_fingerprint": comparison_fingerprint,
            "recorded_at": datetime.now(UTC),
        }
        with self.engine.begin() as connection:
            existing = connection.execute(
                select(parallel_run_results.c.comparison_id).where(
                    parallel_run_results.c.comparison_id == comparison_id
                )
            ).scalar()
            if existing:
                return {
                    "status": "duplicate",
                    "comparison_id": comparison_id,
                    "variance": variance,
                    "acceptance_state": state,
                }
            else:
                connection.execute(
                    insert(parallel_run_results).values(**values)
                )
        return {
            "status": state,
            "comparison_id": comparison_id,
            "variance": variance,
        }

    def latest_parallel_result(
        self,
        metric_id: str,
        definition_version: str,
    ) -> dict[str, Any] | None:
        with self.engine.begin() as connection:
            row = connection.execute(
                select(parallel_run_results)
                .where(
                    parallel_run_results.c.metric_id
                    == str(metric_id).strip(),
                    parallel_run_results.c.definition_version
                    == str(definition_version).strip(),
                )
                .order_by(
                    parallel_run_results.c.recorded_at.desc(),
                    parallel_run_results.c.comparison_id.desc(),
                )
                .limit(1)
            ).mappings().first()
        if row is None:
            return None
        return {
            "comparison_id": row["comparison_id"],
            "metric_id": row["metric_id"],
            "definition_version": row["definition_version"],
            "period_start": row["period_start"],
            "period_end": row["period_end"],
            "legacy_value": row["legacy_value"],
            "v2_value": row["v2_value"],
            "variance": row["variance"],
            "variance_classification": row[
                "variance_classification"
            ],
            "unexplained_event_count": row[
                "unexplained_event_count"
            ],
            "unexplained_cents": row["unexplained_cents"],
            "acceptance_state": row["acceptance_state"],
            "evidence": json.loads(row["evidence_json"]),
            "recorded_at": row["recorded_at"].isoformat(),
        }

    def latest_publication_decision(
        self,
        metric_id: str,
        definition_version: str,
    ) -> dict[str, Any] | None:
        with self.engine.begin() as connection:
            row = connection.execute(
                select(metric_publication_decisions)
                .where(
                    metric_publication_decisions.c.metric_id
                    == str(metric_id).strip(),
                    metric_publication_decisions.c.definition_version
                    == str(definition_version).strip(),
                )
                .order_by(
                    metric_publication_decisions.c.decided_at.desc(),
                    metric_publication_decisions.c.decision_id.desc(),
                )
                .limit(1)
            ).mappings().first()
        if row is None:
            return None
        return {
            "decision_id": row["decision_id"],
            "metric_id": row["metric_id"],
            "definition_version": row["definition_version"],
            "action": row["action"],
            "decided_by": row["decided_by"],
            "decided_at": row["decided_at"].isoformat(),
            "reason": row["reason"],
            "acceptance_record_id": row["acceptance_record_id"],
            "acceptance_fingerprint": row["acceptance_fingerprint"],
            "fallback_state": row["fallback_state"],
            "evidence": json.loads(row["evidence_json"]),
        }

    def metric_cutover_status(
        self,
        *,
        metric_id: str,
        definition_version: str,
        observation: dict[str, Any] | None,
        acceptance_record: dict[str, Any] | None,
        legacy_fallback_available: bool = False,
    ) -> dict[str, Any]:
        metric_id = str(metric_id or "").strip()
        definition_version = str(definition_version or "").strip()
        definitions = {
            (row["metric_id"], row["definition_version"]): row
            for row in self.definitions()
        }
        definition = definitions.get((metric_id, definition_version))
        gates: dict[str, dict[str, Any]] = {}

        gates["definition"] = {
            "passed": definition is not None,
            "reason": (
                None
                if definition is not None
                else "The exact metric definition version is not registered."
            ),
        }
        has_value = bool(
            observation is not None
            and observation.get("value") is not None
        )
        gates["observation"] = {
            "passed": has_value,
            "reason": (
                None
                if has_value
                else (
                    (observation or {}).get("unavailable_reason")
                    or "No governed value exists for the selected period."
                )
            ),
        }
        confidence = str(
            (observation or {}).get("confidence") or ""
        ).strip().lower()
        gates["confidence"] = {
            "passed": confidence in {"verified", "high"},
            "reason": (
                None
                if confidence in {"verified", "high"}
                else "Verified or high-confidence evidence is required."
            ),
        }

        record = acceptance_record or {}
        record_matches = bool(
            record
            and str(record.get("metric_id") or "") == metric_id
            and str(record.get("definition_version") or "")
            == definition_version
        )
        technical_state = str(
            record.get("acceptance_state") or "collecting"
        ).strip().lower()
        required_cycles = int(
            record.get("required_distinct_scheduled_cycles")
            or record.get("required_scheduled_cycles")
            or record.get("required_cycles")
            or 2
        )
        completed_cycles = int(
            record.get("completed_distinct_scheduled_cycles")
            or record.get("completed_scheduled_cycles")
            or record.get("completed_cycles")
            or 0
        )
        technical_passed = bool(
            record_matches
            and record.get("technical_gates_passed")
            and technical_state
            in {"ready_for_owner_acceptance", "owner_accepted"}
        )
        gates["technical_acceptance"] = {
            "passed": technical_passed,
            "reason": (
                None
                if technical_passed
                else (
                    record.get("recommendation")
                    if record_matches
                    else None
                )
                or "Build 4 technical acceptance has not passed."
            ),
        }
        gates["scheduled_cycles"] = {
            "passed": completed_cycles >= required_cycles,
            "reason": (
                None
                if completed_cycles >= required_cycles
                else (
                    f"{completed_cycles} of {required_cycles} distinct "
                    "scheduled comparison cycles are complete."
                )
            ),
            "completed": completed_cycles,
            "required": required_cycles,
        }
        gate_results = record.get("gate_results") or {}
        unexplained_events = int(
            record.get("unexplained_event_count")
            or record.get("unexplained_events_total")
            or gate_results.get("unexplained_event_count")
            or 0
        )
        unexplained_cents = int(
            record.get("unexplained_cents")
            or record.get("unexplained_cents_total")
            or gate_results.get("unexplained_cents")
            or 0
        )
        parity_clean = bool(
            record_matches
            and unexplained_events == 0
            and unexplained_cents == 0
            and technical_passed
        )
        gates["parity"] = {
            "passed": parity_clean,
            "reason": (
                None
                if parity_clean
                else (
                    f"{unexplained_events} unexplained events and "
                    f"{unexplained_cents} unexplained cents remain."
                    if record_matches
                    else "No matching Build 4 parity record exists."
                )
            ),
        }
        owner_state = str(
            record.get("owner_approval_state") or ""
        ).strip().lower()
        owner_reference = str(
            record.get("owner_approval_reference") or ""
        ).strip()
        owner_accepted = bool(
            record_matches
            and technical_state == "owner_accepted"
            and owner_state
            in {
                "accepted",
                "approved",
                "owner_accepted",
                "approved_exact_rule",
            }
            and owner_reference
        )
        gates["owner_authority"] = {
            "passed": owner_accepted,
            "reason": (
                None
                if owner_accepted
                else "Peter's metric-level acceptance reference is required."
            ),
        }

        technical_gate_names = (
            "definition",
            "observation",
            "confidence",
            "technical_acceptance",
            "scheduled_cycles",
            "parity",
        )
        technical_ready = all(
            gates[name]["passed"] for name in technical_gate_names
        )
        decision = self.latest_publication_decision(
            metric_id,
            definition_version,
        )
        approved = bool(
            decision is not None
            and decision["action"] == "approve"
            and owner_accepted
            and technical_ready
        )
        approved_but_gate_failed = bool(
            decision is not None
            and decision["action"] == "approve"
            and not approved
        )
        rolled_back = bool(
            decision is not None and decision["action"] == "rollback"
        )

        if approved:
            effective_state = "v2_accepted"
        elif approved_but_gate_failed:
            effective_state = "unavailable"
        elif rolled_back:
            effective_state = "rolled_back"
        elif technical_ready:
            effective_state = "eligible_for_owner_approval"
        elif has_value:
            effective_state = "shadow"
        elif legacy_fallback_available:
            effective_state = "legacy"
        else:
            effective_state = "unavailable"

        blocked_reasons = [
            gate["reason"]
            for gate in gates.values()
            if not gate["passed"] and gate.get("reason")
        ]
        return {
            "metric_id": metric_id,
            "definition_version": definition_version,
            "effective_state": effective_state,
            "technical_ready": technical_ready,
            "owner_accepted": owner_accepted,
            "promotion_authorised": approved,
            "legacy_fallback_available": bool(
                legacy_fallback_available
            ),
            "rollback_available": approved,
            "gates": gates,
            "blocked_reasons": blocked_reasons,
            "latest_decision": decision,
            "acceptance_record_id": (
                record.get("acceptance_record_id")
                if record_matches
                else None
            ),
        }

    def decide_metric_publication(
        self,
        payload: dict[str, Any],
        *,
        acceptance_record: dict[str, Any] | None = None,
        observation: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        metric_id = str(payload.get("metric_id") or "").strip()
        definition_version = str(
            payload.get("definition_version") or ""
        ).strip()
        action = str(payload.get("action") or "").strip().lower()
        decided_by = str(payload.get("decided_by") or "").strip()
        reason = str(payload.get("reason") or "").strip()
        if not metric_id or not definition_version:
            raise ValueError(
                "metric_id and definition_version are required"
            )
        if action not in {"approve", "rollback"}:
            raise ValueError("action must be approve or rollback")
        if decided_by != "Peter Brown":
            raise ValueError(
                "metric publication requires Peter Brown owner authority"
            )
        if not reason:
            raise ValueError("reason is required")

        current = self.metric_cutover_status(
            metric_id=metric_id,
            definition_version=definition_version,
            observation=observation,
            acceptance_record=acceptance_record,
            legacy_fallback_available=bool(
                payload.get("legacy_fallback_available")
            ),
        )
        if action == "approve" and not (
            current["technical_ready"] and current["owner_accepted"]
        ):
            raise ValueError(
                "metric cannot be promoted until technical gates and "
                "metric-level owner acceptance pass"
            )
        if action == "rollback":
            latest = current["latest_decision"]
            if latest is None or latest["action"] != "approve":
                raise ValueError(
                    "only a currently approved metric can be rolled back"
                )

        decided_at = _datetime(
            payload.get("decided_at") or datetime.now(UTC),
            "decided_at",
        )
        acceptance_record = acceptance_record or {}
        evidence = {
            "cutover_status": current,
            "owner_reference": acceptance_record.get(
                "owner_approval_reference"
            ),
            "request_evidence": payload.get("evidence") or {},
        }
        material = {
            "metric_id": metric_id,
            "definition_version": definition_version,
            "action": action,
            "decided_by": decided_by,
            "decided_at": decided_at.isoformat(),
            "reason": reason,
            "acceptance_record_id": acceptance_record.get(
                "acceptance_record_id"
            ),
            "acceptance_fingerprint": (
                acceptance_record.get("acceptance_fingerprint")
                or acceptance_record.get("fingerprint")
            ),
            "fallback_state": (
                "legacy"
                if payload.get("legacy_fallback_available")
                else "unavailable"
            ),
            "evidence": evidence,
        }
        decision_fingerprint = fingerprint(material)
        decision_id = _stable_id(
            "v2-publication-decision",
            decision_fingerprint,
        )
        values = {
            **{
                key: material[key]
                for key in (
                    "metric_id",
                    "definition_version",
                    "action",
                    "decided_by",
                    "reason",
                    "acceptance_record_id",
                    "acceptance_fingerprint",
                    "fallback_state",
                )
            },
            "decision_id": decision_id,
            "decided_at": decided_at,
            "evidence_json": canonical_json(evidence),
            "decision_fingerprint": decision_fingerprint,
        }
        with self.engine.begin() as connection:
            existing = connection.execute(
                select(metric_publication_decisions.c.decision_id).where(
                    metric_publication_decisions.c.decision_id
                    == decision_id
                )
            ).scalar()
            if existing:
                return {
                    "status": "duplicate",
                    "decision_id": decision_id,
                    "effective_state": (
                        "v2_accepted"
                        if action == "approve"
                        else "rolled_back"
                    ),
                }
            connection.execute(
                insert(metric_publication_decisions).values(**values)
            )
        return {
            "status": "accepted",
            "decision_id": decision_id,
            "metric_id": metric_id,
            "definition_version": definition_version,
            "effective_state": (
                "v2_accepted" if action == "approve" else "rolled_back"
            ),
        }

    def ceo_scorecard_preview(
        self,
        period_id: str,
        *,
        as_of: datetime | str | None = None,
        acceptance_records: dict[
            tuple[str, str], dict[str, Any]
        ] | None = None,
    ) -> dict[str, Any]:
        period_id = str(period_id or "week").strip().lower()
        periods = completed_reporting_periods(as_of)
        if period_id not in periods:
            raise ValueError("period must be week, 28d or 90d")
        period_start, period_end = periods[period_id]

        with self.engine.begin() as connection:
            observations = connection.execute(
                select(metric_observations)
                .where(
                    metric_observations.c.period_start
                    == period_start.isoformat(),
                    metric_observations.c.period_end
                    == period_end.isoformat(),
                )
                .order_by(metric_observations.c.created_at.desc())
            ).mappings().all()
            parallel = connection.execute(
                select(parallel_run_results)
                .where(
                    parallel_run_results.c.period_start
                    == period_start.isoformat(),
                    parallel_run_results.c.period_end
                    == period_end.isoformat(),
                )
                .order_by(parallel_run_results.c.recorded_at.desc())
            ).mappings().all()
            goal_observation = connection.execute(
                select(metric_observations)
                .where(
                    metric_observations.c.metric_id
                    == "cash_goal_progress"
                )
                .order_by(metric_observations.c.created_at.desc())
                .limit(1)
            ).mappings().first()

        latest_observation: dict[str, Any] = {}
        for row in observations:
            latest_observation.setdefault(str(row["metric_id"]), row)
        latest_parallel: dict[str, Any] = {}
        for row in parallel:
            latest_parallel.setdefault(str(row["metric_id"]), row)
        definitions = {
            str(row["metric_id"]): row for row in self.definitions()
        }

        metrics = []
        ready_for_owner_acceptance = 0
        accepted_metric_count = 0
        for metric_id in CEO_SCORECARD_METRIC_ORDER:
            definition = definitions.get(metric_id) or {}
            observation = latest_observation.get(metric_id)
            comparison = latest_parallel.get(metric_id)
            comparison_state = (
                str(comparison["acceptance_state"])
                if comparison is not None
                else "not_run"
            )
            confidence = (
                str(observation["confidence"])
                if observation is not None
                else None
            )
            has_value = bool(
                observation is not None
                and observation["value"] is not None
            )
            definition_version = (
                observation["definition_version"]
                if observation is not None
                else definition.get("definition_version")
            )
            observation_payload = (
                dict(observation) if observation is not None else None
            )
            acceptance_record = (
                (acceptance_records or {}).get(
                    (metric_id, str(definition_version or ""))
                )
            )
            cutover = self.metric_cutover_status(
                metric_id=metric_id,
                definition_version=str(definition_version or ""),
                observation=observation_payload,
                acceptance_record=acceptance_record,
                legacy_fallback_available=(
                    metric_id in CEO_LEGACY_FALLBACK_METRICS
                ),
            )
            acceptance_ready = cutover["technical_ready"]
            ready_for_owner_acceptance += acceptance_ready
            accepted_metric_count += (
                cutover["effective_state"] == "v2_accepted"
            )
            if observation is None:
                blocked_reason = (
                    "No governed observation has been recorded for this "
                    "completed period."
                )
            elif not has_value:
                blocked_reason = (
                    observation["unavailable_reason"]
                    or "The governed value is unavailable."
                )
            elif confidence not in {"verified", "high"}:
                blocked_reason = (
                    "The observation still contains unresolved or "
                    "confidence-labelled evidence."
                )
            elif comparison_state == "not_run":
                blocked_reason = (
                    "The legacy-versus-V2 comparison has not been run for "
                    "this period."
                )
            elif comparison_state not in {
                "passed",
                "accepted_for_cutover",
            }:
                blocked_reason = (
                    "The parallel comparison contains an unexplained "
                    "difference."
                )
            else:
                blocked_reason = None
            metrics.append(
                {
                    "metric_id": metric_id,
                    "plain_english_name": definition.get(
                        "plain_english_name", metric_id
                    ),
                    "definition_version": (
                        definition_version
                    ),
                    "value": (
                        observation["value"]
                        if observation is not None
                        else None
                    ),
                    "numerator": (
                        observation["numerator"]
                        if observation is not None
                        else None
                    ),
                    "denominator": (
                        observation["denominator"]
                        if observation is not None
                        else None
                    ),
                    "unit": (
                        observation["unit"]
                        if observation is not None
                        else None
                    ),
                    "confidence": confidence,
                    "publication_state": (
                        observation["publication_state"]
                        if observation is not None
                        else "not_recorded"
                    ),
                    "parallel_state": comparison_state,
                    "acceptance_ready": acceptance_ready,
                    "blocked_reason": blocked_reason,
                    "cutover": cutover,
                    "effective_publication_state": cutover[
                        "effective_state"
                    ],
                    "metric_observation_id": (
                        observation["metric_observation_id"]
                        if observation is not None
                        else None
                    ),
                }
            )

        goal_start, goal_end = rolling_cash_goal_window(as_of)
        goal_payload = (
            {
                "metric_observation_id": goal_observation[
                    "metric_observation_id"
                ],
                "definition_version": goal_observation[
                    "definition_version"
                ],
                "period_start": goal_observation["period_start"],
                "period_end": goal_observation["period_end"],
                "value": goal_observation["value"],
                "numerator": goal_observation["numerator"],
                "denominator": goal_observation["denominator"],
                "unit": goal_observation["unit"],
                "confidence": goal_observation["confidence"],
                "publication_state": goal_observation[
                    "publication_state"
                ],
                "unavailable_reason": goal_observation[
                    "unavailable_reason"
                ],
            }
            if goal_observation is not None
            else None
        )
        goal_available = bool(
            goal_payload is not None
            and goal_payload["value"] is not None
            and goal_payload["numerator"] is not None
        )
        goal_cutover = self.metric_cutover_status(
            metric_id="cash_goal_progress",
            definition_version=(
                str(goal_payload["definition_version"])
                if goal_payload is not None
                else "cash-goal-v1"
            ),
            observation=goal_payload,
            acceptance_record=(acceptance_records or {}).get(
                (
                    "cash_goal_progress",
                    (
                        str(goal_payload["definition_version"])
                        if goal_payload is not None
                        else "cash-goal-v1"
                    ),
                )
            ),
            legacy_fallback_available=True,
        )
        return {
            "schema_version": 1,
            "mode": "shadow",
            "publication_impact": "none",
            "period": {
                "id": period_id,
                "label": CEO_SCORECARD_PERIOD_LABELS[period_id],
                "start": period_start.isoformat(),
                "end": period_end.isoformat(),
                "timezone": "Australia/Brisbane",
            },
            "acceptance": {
                "required_metrics": len(CEO_SCORECARD_METRIC_ORDER),
                "ready_for_owner_acceptance": (
                    ready_for_owner_acceptance
                ),
                "accepted_metrics": accepted_metric_count,
                "all_metrics_ready": (
                    ready_for_owner_acceptance
                    == len(CEO_SCORECARD_METRIC_ORDER)
                ),
                "cutover_authorised": accepted_metric_count > 0,
                "mode": "metric_by_metric",
                "legacy_reporting_unchanged": True,
            },
            "metrics": metrics,
            "cash_goal": {
                "metric_id": "cash_goal_progress",
                "target_cents": 100_000_000,
                "window_start": goal_start.isoformat(),
                "window_end": goal_end.isoformat(),
                "observation": goal_payload,
                "available": goal_available,
                "cutover": goal_cutover,
                "blocked_reason": (
                    None
                    if goal_available
                    else (
                        (
                            goal_payload["unavailable_reason"]
                            if goal_payload is not None
                            else None
                        )
                        or
                        "The accepted event-level cash adapter has not "
                        "completed its first rolling-365-day observation."
                    )
                ),
            },
        }

    def definitions(self) -> list[dict[str, Any]]:
        with self.engine.begin() as connection:
            rows = connection.execute(
                select(metric_definitions).order_by(
                    metric_definitions.c.metric_id,
                    metric_definitions.c.definition_version,
                )
            ).mappings().all()
        return [
            {
                "metric_id": row["metric_id"],
                "definition_version": row["definition_version"],
                "plain_english_name": row["plain_english_name"],
                "decision_question": row["decision_question"],
                "event_grain": row["event_grain"],
                "source_authority": json.loads(
                    row["source_authority_json"]
                ),
                "numerator_definition": row["numerator_definition"],
                "denominator_definition": row["denominator_definition"],
                "inclusion_rules": json.loads(
                    row["inclusion_rules_json"]
                ),
                "exclusion_rules": json.loads(
                    row["exclusion_rules_json"]
                ),
                "period_semantics": row["period_semantics"],
                "minimum_freshness": json.loads(
                    row["minimum_freshness_json"]
                ),
                "owner": row["owner"],
                "approval_state": row["approval_state"],
                "effective_from": row["effective_from"],
                "effective_to": row["effective_to"],
            }
            for row in rows
        ]

    def status(self) -> dict[str, Any]:
        with self.engine.begin() as connection:
            counts = {
                "source_event_versions": connection.execute(
                    select(source_events.c.event_version_id)
                ).all(),
                "metric_definitions": connection.execute(
                    select(metric_definitions.c.metric_id)
                ).all(),
                "metric_observations": connection.execute(
                    select(
                        metric_observations.c.metric_observation_id
                    )
                ).all(),
                "pending_manual_inputs": connection.execute(
                    select(manual_input_events.c.input_id).where(
                        manual_input_events.c.approval_state == "pending"
                    )
                ).all(),
                "parallel_periods": connection.execute(
                    select(parallel_run_results.c.comparison_id)
                ).all(),
            }
            latest = connection.execute(
                select(metric_observations)
                .order_by(metric_observations.c.created_at.desc())
                .limit(20)
            ).mappings().all()
            latest_parallel = connection.execute(
                select(parallel_run_results)
                .order_by(parallel_run_results.c.recorded_at.desc())
                .limit(20)
            ).mappings().all()
        return {
            "schema_version": REPORTING_V2_SCHEMA_VERSION,
            "mode": REPORTING_V2_MODE,
            "publication_authority": "none",
            "legacy_reporting_unchanged": True,
            "counts": {
                key: len(value) for key, value in counts.items()
            },
            "latest_metric_observations": [
                {
                    "metric_observation_id": row[
                        "metric_observation_id"
                    ],
                    "metric_id": row["metric_id"],
                    "definition_version": row["definition_version"],
                    "period_start": row["period_start"],
                    "period_end": row["period_end"],
                    "value": row["value"],
                    "numerator": row["numerator"],
                    "denominator": row["denominator"],
                    "unit": row["unit"],
                    "confidence": row["confidence"],
                    "publication_state": row["publication_state"],
                    "unavailable_reason": row["unavailable_reason"],
                    "created_at": row["created_at"].isoformat(),
                }
                for row in latest
            ],
            "latest_parallel_results": [
                {
                    "comparison_id": row["comparison_id"],
                    "metric_id": row["metric_id"],
                    "definition_version": row["definition_version"],
                    "period_start": row["period_start"],
                    "period_end": row["period_end"],
                    "legacy_value": row["legacy_value"],
                    "v2_value": row["v2_value"],
                    "variance": row["variance"],
                    "variance_classification": row[
                        "variance_classification"
                    ],
                    "unexplained_event_count": row[
                        "unexplained_event_count"
                    ],
                    "acceptance_state": row["acceptance_state"],
                    "evidence": json.loads(row["evidence_json"]),
                    "recorded_at": row["recorded_at"].isoformat(),
                }
                for row in latest_parallel
            ],
        }
