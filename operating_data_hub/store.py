from __future__ import annotations

import json
import uuid
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    UniqueConstraint,
    create_engine,
    func,
    inspect,
    insert,
    select,
    text,
    update,
)
from sqlalchemy.engine import make_url
from sqlalchemy.exc import IntegrityError

from .contracts import canonical_json, fingerprint
from .conversation_clearance import aggregate_cases, build_case, stable_id
from .entitlement_queue import (
    build_entitlement_exception_queue,
    service_is_covered,
)
from reporting_control.cohort import summarise_cohort_rows


metadata = MetaData()

source_snapshots = Table(
    "hub_source_snapshots",
    metadata,
    Column("snapshot_id", String(64), primary_key=True),
    Column("source", String(80), nullable=False, index=True),
    Column("observed_at", DateTime(timezone=True), nullable=False),
    Column("accepted_at", DateTime(timezone=True), nullable=False),
    Column("status", String(24), nullable=False),
    Column("complete", Integer, nullable=False),
    Column("record_count", Integer, nullable=False),
    Column("schema_version", Integer, nullable=False),
    Column("fingerprint", String(64), nullable=False),
    Column("payload_json", Text, nullable=False),
    UniqueConstraint("source", "fingerprint", name="uq_hub_source_fingerprint"),
)

job_runs = Table(
    "hub_job_runs",
    metadata,
    Column("run_id", String(64), primary_key=True),
    Column("job_id", String(120), nullable=False, index=True),
    Column("started_at", DateTime(timezone=True), nullable=False),
    Column("completed_at", DateTime(timezone=True)),
    Column("status", String(24), nullable=False),
    Column("summary_json", Text),
    Column("error", Text),
)

exceptions = Table(
    "hub_exceptions",
    metadata,
    Column("exception_id", String(64), primary_key=True),
    Column("domain", String(80), nullable=False),
    Column("code", String(120), nullable=False),
    Column("severity", String(24), nullable=False),
    Column("owner", String(160)),
    Column("status", String(24), nullable=False),
    Column("evidence_json", Text, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)

metric_snapshots = Table(
    "hub_metric_snapshots",
    metadata,
    Column("metric_snapshot_id", String(64), primary_key=True),
    Column("period_start", String(10), nullable=False),
    Column("period_end", String(10), nullable=False),
    Column("generated_at", DateTime(timezone=True), nullable=False),
    Column("source_snapshot_ids_json", Text, nullable=False),
    Column("metrics_json", Text, nullable=False),
    Column("definition_version", String(40), nullable=False),
)

canonical_people = Table(
    "hub_canonical_people",
    metadata,
    Column("person_id", String(64), primary_key=True),
    Column("canonical_key", String(320), nullable=False, unique=True),
    Column("email", String(320)),
    Column("first_name", String(160)),
    Column("last_name", String(160)),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)

source_identities = Table(
    "hub_source_identities",
    metadata,
    Column("source", String(80), primary_key=True),
    Column("source_record_id", String(200), primary_key=True),
    Column("person_id", String(64), nullable=False, index=True),
    Column("email", String(320)),
    Column("observed_at", DateTime(timezone=True), nullable=False),
    Column("source_snapshot_id", String(64), nullable=False),
)

service_relationships = Table(
    "hub_service_relationships",
    metadata,
    Column("relationship_id", String(64), primary_key=True),
    Column("person_id", String(64), nullable=False, index=True),
    Column("service_type", String(80), nullable=False),
    Column("service_name", String(240)),
    Column("status", String(40), nullable=False),
    Column("source", String(80), nullable=False),
    Column("source_record_id", String(200)),
    Column("effective_from", String(10)),
    Column("effective_to", String(10)),
    Column("observed_at", DateTime(timezone=True), nullable=False),
    Column("source_snapshot_id", String(64), nullable=False),
    Column("metadata_json", Text, nullable=False),
)

payment_accounts = Table(
    "hub_payment_accounts",
    metadata,
    Column("payment_account_id", String(64), primary_key=True),
    Column("person_id", String(64), index=True),
    Column("source", String(80), nullable=False),
    Column("source_account_id", String(200), nullable=False),
    Column("agreement_id", String(200)),
    Column("status", String(40), nullable=False),
    Column("weekly_amount", String(32)),
    Column("observed_at", DateTime(timezone=True), nullable=False),
    Column("source_snapshot_id", String(64), nullable=False),
    UniqueConstraint(
        "source",
        "source_account_id",
        name="uq_hub_payment_account_source",
    ),
)

payment_events = Table(
    "hub_payment_events",
    metadata,
    Column("payment_event_id", String(64), primary_key=True),
    Column("payment_account_id", String(64), nullable=False, index=True),
    Column("person_id", String(64), index=True),
    Column("source", String(80), nullable=False),
    Column("source_event_id", String(200), nullable=False),
    Column("occurred_on", String(10), nullable=False),
    Column("amount", String(32), nullable=False),
    Column("status", String(40), nullable=False),
    Column("service_type", String(80), nullable=False),
    Column("cadence", String(40), nullable=False),
    Column("description", Text, nullable=False),
    Column("coverage_start", String(10)),
    Column("coverage_end", String(10)),
    Column("source_snapshot_id", String(64), nullable=False),
    UniqueConstraint(
        "source",
        "source_event_id",
        name="uq_hub_payment_event_source",
    ),
)

payment_service_overrides = Table(
    "hub_payment_service_overrides",
    metadata,
    Column("override_id", String(64), primary_key=True),
    Column("source", String(80), nullable=False),
    Column("source_account_id", String(200)),
    Column("agreement_id", String(200)),
    Column("service_type", String(80), nullable=False),
    Column("cadence", String(40), nullable=False),
    Column("expected_weekly_amount", String(32)),
    Column("effective_from", String(10)),
    Column("effective_to", String(10)),
    Column("approved_by", String(160), nullable=False),
    Column("reason", Text, nullable=False),
    Column("active", Integer, nullable=False),
    Column("observed_at", DateTime(timezone=True), nullable=False),
    Column("source_snapshot_id", String(64), nullable=False),
    UniqueConstraint(
        "source",
        "source_account_id",
        "agreement_id",
        name="uq_hub_payment_service_override_target",
    ),
)

entitlements = Table(
    "hub_entitlements",
    metadata,
    Column("entitlement_id", String(64), primary_key=True),
    Column("person_id", String(64), nullable=False, index=True),
    Column("service_type", String(80), nullable=False),
    Column("quantity", String(32)),
    Column("unit", String(80)),
    Column("status", String(40), nullable=False),
    Column("effective_from", String(10)),
    Column("effective_to", String(10)),
    Column("source", String(80), nullable=False),
    Column("source_record_id", String(200)),
    Column("observed_at", DateTime(timezone=True), nullable=False),
    Column("source_snapshot_id", String(64), nullable=False),
    Column("metadata_json", Text, nullable=False),
)

lifecycle_states = Table(
    "hub_lifecycle_states",
    metadata,
    Column("person_id", String(64), primary_key=True),
    Column("status", String(40), nullable=False),
    Column("cancellation_status", String(240)),
    Column("cancellation_type", String(80)),
    Column("notice_end_date", String(10)),
    Column("final_access_date", String(10)),
    Column("hold_status", String(80)),
    Column("hold_type", String(80)),
    Column("hold_start_date", String(10)),
    Column("hold_end_date", String(10)),
    Column("classification", String(120)),
    Column("source", String(80), nullable=False),
    Column("observed_at", DateTime(timezone=True), nullable=False),
    Column("source_snapshot_id", String(64), nullable=False),
    Column("evidence_json", Text, nullable=False),
)

governed_cohort_members = Table(
    "hub_governed_cohort_members",
    metadata,
    Column("cohort_member_id", String(64), primary_key=True),
    Column("person_id", String(64), nullable=False, index=True),
    Column("canonical_key", String(320), nullable=False),
    Column("disposition", String(40), nullable=False),
    Column("confirmed_active", Integer, nullable=False),
    Column("paid_or_entitled", Integer),
    Column("decision_required", Integer, nullable=False),
    Column("primary_reason", String(240), nullable=False),
    Column("owner", String(160)),
    Column("owner_question", Text),
    Column("as_of_date", String(10), nullable=False),
    Column("rule_version", String(80), nullable=False),
    Column("current", Integer, nullable=False),
    Column("observed_at", DateTime(timezone=True), nullable=False),
    Column("source_snapshot_id", String(64), nullable=False, index=True),
    Column("evidence_json", Text, nullable=False),
)

sa_appointment_observations = Table(
    "hub_sa_appointment_observations",
    metadata,
    Column("observation_id", String(64), primary_key=True),
    Column("appointment_id", String(200), nullable=False, index=True),
    Column("contact_id", String(200), nullable=False, index=True),
    Column("calendar_id", String(200), nullable=False),
    Column("booked_at", DateTime(timezone=True)),
    Column("start_at", DateTime(timezone=True), nullable=False),
    Column("end_at", DateTime(timezone=True), nullable=False),
    Column("status", String(40), nullable=False),
    Column("assigned_user_id", String(200)),
    Column("source_updated_at", DateTime(timezone=True)),
    Column("deleted", Integer, nullable=False),
    Column("observed_at", DateTime(timezone=True), nullable=False),
    Column("source_run_id", String(120), nullable=False),
    Column("source_snapshot_id", String(64), nullable=False),
    Column("observation_fingerprint", String(64), nullable=False),
    UniqueConstraint(
        "appointment_id",
        "observation_fingerprint",
        name="uq_hub_sa_appointment_observation",
    ),
)

sa_feedback_evidence = Table(
    "hub_sa_feedback_evidence",
    metadata,
    Column("evidence_id", String(64), primary_key=True),
    Column("delivery_key", String(160), nullable=False, unique=True),
    Column("form_submission_id", String(200), nullable=False, unique=True),
    Column("contact_id", String(200), nullable=False, index=True),
    Column("submitted_at", DateTime(timezone=True), nullable=False),
    Column("sales_outcome", String(40)),
    Column("delivered_by", String(160), nullable=False),
    Column("workflow_execution_id", String(200)),
    Column("accepted_at", DateTime(timezone=True), nullable=False),
    Column("payload_json", Text, nullable=False),
)

sa_supporting_evidence = Table(
    "hub_sa_supporting_evidence",
    metadata,
    Column("evidence_id", String(64), primary_key=True),
    Column("appointment_id", String(200), index=True),
    Column("contact_id", String(200), nullable=False, index=True),
    Column("evidence_type", String(80), nullable=False),
    Column("source_record_id", String(200)),
    Column("observed_at", DateTime(timezone=True), nullable=False),
    Column("payload_json", Text, nullable=False),
    UniqueConstraint(
        "evidence_type",
        "source_record_id",
        name="uq_hub_sa_supporting_evidence",
    ),
)

sa_reconciliation_decisions = Table(
    "hub_sa_reconciliation_decisions",
    metadata,
    Column("decision_id", String(64), primary_key=True),
    Column("appointment_id", String(200), nullable=False, index=True),
    Column("contact_id", String(200), nullable=False, index=True),
    Column("canonical_status", String(40), nullable=False),
    Column("reconciliation_state", String(80), nullable=False),
    Column("proposed_status", String(40)),
    Column("rule_version", String(80), nullable=False),
    Column("decided_at", DateTime(timezone=True), nullable=False),
    Column("decision_fingerprint", String(64), nullable=False),
    Column("evidence_json", Text, nullable=False),
    UniqueConstraint(
        "appointment_id",
        "decision_fingerprint",
        name="uq_hub_sa_reconciliation_decision",
    ),
)

service_change_controls = Table(
    "hub_service_change_controls",
    metadata,
    Column("canonical_key", String(320), primary_key=True),
    Column("request_id", String(160), nullable=False, unique=True),
    Column("person_id", String(64), nullable=False, index=True),
    Column("contact_id", String(200), nullable=False, index=True),
    Column("status", String(40), nullable=False),
    Column("event_version", Integer, nullable=False),
    Column("request_date", String(10), nullable=False),
    Column("effective_date", String(10), nullable=False),
    Column("effective_at", DateTime(timezone=True)),
    Column("offer_version", String(120), nullable=False),
    Column("agreement_version", String(120), nullable=False),
    Column("signed_at", DateTime(timezone=True), nullable=False),
    Column("signature_document", Text, nullable=False),
    Column("prior_services_json", Text, nullable=False),
    Column("requested_services_json", Text, nullable=False),
    Column("surface_statuses_json", Text, nullable=False),
    Column("request_fingerprint", String(64), nullable=False),
    Column("last_error", Text),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)

service_change_events = Table(
    "hub_service_change_events",
    metadata,
    Column("event_id", String(64), primary_key=True),
    Column("request_id", String(160), nullable=False, index=True),
    Column("canonical_key", String(320), nullable=False, index=True),
    Column("person_id", String(64), nullable=False, index=True),
    Column("event_type", String(40), nullable=False),
    Column("event_version", Integer, nullable=False),
    Column("occurred_at", DateTime(timezone=True), nullable=False),
    Column("accepted_at", DateTime(timezone=True), nullable=False),
    Column("event_fingerprint", String(64), nullable=False),
    Column("payload_json", Text, nullable=False),
    UniqueConstraint(
        "request_id",
        "event_type",
        "event_version",
        name="uq_hub_service_change_event_version",
    ),
)

workflow_extension_outbox = Table(
    "hub_workflow_extension_outbox",
    metadata,
    Column("idempotency_key", String(64), primary_key=True),
    Column("workflow_key", String(120), nullable=False, index=True),
    Column("decision_id", String(200), nullable=False, index=True),
    Column("decision_version", Integer, nullable=False),
    Column("decision_fingerprint", String(64), nullable=False),
    Column("person_id", String(64), nullable=False, index=True),
    Column("contact_id", String(200)),
    Column("source_snapshot_id", String(64), nullable=False),
    Column("action_type", String(80), nullable=False),
    Column("owner_role", String(160)),
    Column("owner_user_id", String(200)),
    Column("due_at", DateTime(timezone=True)),
    Column("dedupe_scope", String(240), nullable=False),
    Column("state", String(40), nullable=False, index=True),
    Column("reason_json", Text, nullable=False),
    Column("payload_json", Text, nullable=False),
    Column("audit_json", Text, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
    Column("queued_at", DateTime(timezone=True)),
    Column("dispatched_at", DateTime(timezone=True)),
    Column("external_action_id", String(200)),
)

workflow_extension_audit = Table(
    "hub_workflow_extension_audit",
    metadata,
    Column("audit_id", String(64), primary_key=True),
    Column("idempotency_key", String(64), nullable=False, index=True),
    Column("workflow_key", String(120), nullable=False, index=True),
    Column("decision_id", String(200), nullable=False, index=True),
    Column("event_type", String(80), nullable=False),
    Column("state", String(40), nullable=False),
    Column("occurred_at", DateTime(timezone=True), nullable=False),
    Column("evidence_json", Text, nullable=False),
)

conversation_cases = Table(
    "hub_conversation_cases",
    metadata,
    Column("case_id", String(64), primary_key=True),
    Column("cycle_key", String(80), nullable=False, unique=True),
    Column("conversation_id", String(200), nullable=False, index=True),
    Column("contact_id", String(200), index=True),
    Column("person_id", String(64), index=True),
    Column("latest_inbound_message_id", String(200)),
    Column("opened_at", DateTime(timezone=True), nullable=False),
    Column("first_seen_at", DateTime(timezone=True), nullable=False),
    Column("last_seen_at", DateTime(timezone=True), nullable=False),
    Column("latest_inbound_at", DateTime(timezone=True), nullable=False),
    Column("latest_outbound_at", DateTime(timezone=True)),
    Column("category", String(80), nullable=False, index=True),
    Column("recommendation", Text, nullable=False),
    Column("owner_role", String(160), nullable=False),
    Column("owner_user_id", String(200)),
    Column("due_at", DateTime(timezone=True), nullable=False, index=True),
    Column("state", String(40), nullable=False, index=True),
    Column("breached", Integer, nullable=False),
    Column("classification_version", String(120), nullable=False),
    Column("rule_version", String(120), nullable=False),
    Column("source_run_id", String(120), nullable=False),
    Column("source_fingerprint", String(64), nullable=False),
    Column("channel", String(80), nullable=False),
    Column("current_assignment", String(200)),
    Column("excerpt", Text),
    Column("resolution_code", String(80)),
    Column("resolution_at", DateTime(timezone=True)),
    Column("disposition_json", Text, nullable=False),
)

conversation_case_events = Table(
    "hub_conversation_case_events",
    metadata,
    Column("event_id", String(64), primary_key=True),
    Column("case_id", String(64), nullable=False, index=True),
    Column("idempotency_key", String(160), nullable=False, unique=True),
    Column("event_type", String(80), nullable=False, index=True),
    Column("occurred_at", DateTime(timezone=True), nullable=False),
    Column("event_fingerprint", String(64), nullable=False),
    Column("payload_json", Text, nullable=False),
)

conversation_delivery_state = Table(
    "hub_conversation_delivery_state",
    metadata,
    Column("channel", String(80), primary_key=True),
    Column("queue_fingerprint", String(64), nullable=False),
    Column("delivered_at", DateTime(timezone=True), nullable=False),
    Column("payload_json", Text, nullable=False),
)

sa_prequalification_cases = Table(
    "hub_sa_prequalification_cases",
    metadata,
    Column("appointment_id", String(200), primary_key=True),
    Column("contact_id", String(200), nullable=False, index=True),
    Column("conversation_id", String(200), index=True),
    Column("contact_name", String(320)),
    Column("scheduled_at", DateTime(timezone=True), nullable=False, index=True),
    Column("appointment_status", String(40), nullable=False),
    Column("case_state", String(60), nullable=False, index=True),
    Column("first_incomplete_stage", String(80)),
    Column("next_action", Text),
    Column("blocked_reasons_json", Text, nullable=False),
    Column("conversation_complete", Integer, nullable=False),
    Column("conversation_fingerprint", String(64)),
    Column("latest_message_id", String(200)),
    Column("latest_message_at", DateTime(timezone=True)),
    Column("stages_json", Text, nullable=False),
    Column("facts_json", Text, nullable=False),
    Column("draft_json", Text),
    Column("review_context_json", Text),
    Column("privacy_evidence_json", Text),
    Column("rule_version", String(120), nullable=False),
    Column("model_version", String(160)),
    Column("prompt_version", String(160)),
    Column("source_run_id", String(120), nullable=False),
    Column("source_fingerprint", String(64), nullable=False),
    Column("first_seen_at", DateTime(timezone=True), nullable=False),
    Column("last_seen_at", DateTime(timezone=True), nullable=False),
)

sa_prequalification_events = Table(
    "hub_sa_prequalification_events",
    metadata,
    Column("event_id", String(64), primary_key=True),
    Column("appointment_id", String(200), nullable=False, index=True),
    Column("event_type", String(80), nullable=False, index=True),
    Column("idempotency_key", String(200), nullable=False, unique=True),
    Column("occurred_at", DateTime(timezone=True), nullable=False),
    Column("actor", String(200)),
    Column("event_fingerprint", String(64), nullable=False),
    Column("payload_json", Text, nullable=False),
)

sa_prequalification_delivery_state = Table(
    "hub_sa_prequalification_delivery_state",
    metadata,
    Column("delivery_key", String(160), primary_key=True),
    Column("queue_fingerprint", String(64), nullable=False),
    Column("delivered_at", DateTime(timezone=True), nullable=False),
    Column("payload_json", Text, nullable=False),
)

sa_prequalification_send_locks = Table(
    "hub_sa_prequalification_send_locks",
    metadata,
    Column("send_key", String(200), primary_key=True),
    Column("appointment_id", String(200), nullable=False, index=True),
    Column("draft_id", String(200), nullable=False),
    Column("reviewer", String(200), nullable=False),
    Column("wording_hash", String(64), nullable=False),
    Column("conversation_fingerprint", String(64), nullable=False),
    Column("status", String(40), nullable=False, index=True),
    Column("claimed_at", DateTime(timezone=True), nullable=False),
    Column("completed_at", DateTime(timezone=True)),
    Column("ghl_message_id", String(200)),
    Column("failure_code", String(160)),
    Column("payload_json", Text, nullable=False),
)


class HubStore:
    def __init__(self, database_url: str):
        if database_url.startswith("postgresql://"):
            database_url = database_url.replace(
                "postgresql://", "postgresql+psycopg://", 1
            )
        elif database_url.startswith("postgres://"):
            database_url = database_url.replace(
                "postgres://", "postgresql+psycopg://", 1
            )
        if database_url.startswith("sqlite"):
            sqlite_database = make_url(database_url).database
            if sqlite_database and sqlite_database != ":memory:":
                Path(sqlite_database).parent.mkdir(parents=True, exist_ok=True)
        self.engine = create_engine(
            database_url,
            pool_pre_ping=True,
            connect_args=(
                {"check_same_thread": False}
                if database_url.startswith("sqlite")
                else {}
            ),
        )
        metadata.create_all(self.engine)
        existing_columns = {
            column["name"]
            for column in inspect(self.engine).get_columns(
                "hub_payment_events"
            )
        }
        lifecycle_columns = {
            column["name"]
            for column in inspect(self.engine).get_columns(
                "hub_lifecycle_states"
            )
        }
        sa_observation_columns = {
            column["name"]
            for column in inspect(self.engine).get_columns(
                "hub_sa_appointment_observations"
            )
        }
        sa_prequalification_columns = {
            column["name"]
            for column in inspect(self.engine).get_columns(
                "hub_sa_prequalification_cases"
            )
        }
        service_change_columns = {
            column["name"]
            for column in inspect(self.engine).get_columns(
                "hub_service_change_controls"
            )
        }
        with self.engine.begin() as connection:
            if "coverage_start" not in existing_columns:
                connection.execute(
                    text(
                        "ALTER TABLE hub_payment_events "
                        "ADD COLUMN coverage_start VARCHAR(10)"
                    )
                )
            if "coverage_end" not in existing_columns:
                connection.execute(
                    text(
                        "ALTER TABLE hub_payment_events "
                        "ADD COLUMN coverage_end VARCHAR(10)"
                    )
                )
            if "cancellation_type" not in lifecycle_columns:
                connection.execute(
                    text(
                        "ALTER TABLE hub_lifecycle_states "
                        "ADD COLUMN cancellation_type VARCHAR(80)"
                    )
                )
            if "notice_end_date" not in lifecycle_columns:
                connection.execute(
                    text(
                        "ALTER TABLE hub_lifecycle_states "
                        "ADD COLUMN notice_end_date VARCHAR(10)"
                    )
                )
            for column_name, column_type in (
                ("hold_status", "VARCHAR(80)"),
                ("hold_type", "VARCHAR(80)"),
                ("hold_start_date", "VARCHAR(10)"),
                ("hold_end_date", "VARCHAR(10)"),
            ):
                if column_name not in lifecycle_columns:
                    connection.execute(
                        text(
                            "ALTER TABLE hub_lifecycle_states "
                            f"ADD COLUMN {column_name} {column_type}"
                        )
                    )
            if "booked_at" not in sa_observation_columns:
                connection.execute(
                    text(
                        "ALTER TABLE hub_sa_appointment_observations "
                        "ADD COLUMN booked_at TIMESTAMP WITH TIME ZONE"
                    )
                )
            if "review_context_json" not in sa_prequalification_columns:
                connection.execute(
                    text(
                        "ALTER TABLE hub_sa_prequalification_cases "
                        "ADD COLUMN review_context_json TEXT"
                    )
                )
            if "privacy_evidence_json" not in sa_prequalification_columns:
                connection.execute(
                    text(
                        "ALTER TABLE hub_sa_prequalification_cases "
                        "ADD COLUMN privacy_evidence_json TEXT"
                    )
                )
            if "effective_at" not in service_change_columns:
                connection.execute(
                    text(
                        "ALTER TABLE hub_service_change_controls "
                        "ADD COLUMN effective_at TIMESTAMP WITH TIME ZONE"
                    )
                )

    def accept_snapshot(self, source: str, payload: dict[str, Any]) -> dict[str, Any]:
        payload_fingerprint = fingerprint(payload)
        now = datetime.now(UTC)
        observed_at = datetime.fromisoformat(
            str(payload["observed_at"]).replace("Z", "+00:00")
        )
        record_count = len(payload.get("rows") or [])
        if not record_count:
            summary = payload.get("summary") or {}
            record_count = int(
                summary.get("record_count")
                or summary.get("memberCount")
                or summary.get("includedCount")
                or 0
            )
        with self.engine.begin() as connection:
            existing = connection.execute(
                select(source_snapshots.c.snapshot_id).where(
                    source_snapshots.c.source == source,
                    source_snapshots.c.fingerprint == payload_fingerprint,
                )
            ).scalar()
            if existing:
                return {
                    "status": "duplicate",
                    "snapshot_id": str(existing),
                    "fingerprint": payload_fingerprint,
                }
            snapshot_id = (
                now.strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
            )
            connection.execute(
                insert(source_snapshots).values(
                    snapshot_id=snapshot_id,
                    source=source,
                    observed_at=observed_at,
                    accepted_at=now,
                    status=str(payload.get("status") or "complete"),
                    complete=int(bool(payload.get("complete"))),
                    record_count=record_count,
                    schema_version=int(payload.get("schema_version") or 1),
                    fingerprint=payload_fingerprint,
                    payload_json=canonical_json(payload),
                )
            )
        return {
            "status": "accepted",
            "snapshot_id": snapshot_id,
            "record_count": record_count,
            "fingerprint": payload_fingerprint,
        }

    def latest_snapshot(self, source: str) -> dict[str, Any] | None:
        with self.engine.begin() as connection:
            row = connection.execute(
                select(source_snapshots)
                .where(
                    source_snapshots.c.source == source,
                    source_snapshots.c.complete == 1,
                )
                .order_by(
                    source_snapshots.c.observed_at.desc(),
                    source_snapshots.c.accepted_at.desc(),
                    source_snapshots.c.snapshot_id.desc(),
                )
                .limit(1)
            ).mappings().first()
        return self._snapshot(row) if row else None

    def latest_governed_snapshot(
        self, source: str
    ) -> dict[str, Any] | None:
        snapshot = self.latest_snapshot(source)
        if not snapshot or source != "pt_minder":
            return snapshot
        return self._apply_overrides_to_pt_minder_snapshot(snapshot)

    def latest_snapshots(self) -> list[dict[str, Any]]:
        ranked = (
            select(
                *source_snapshots.c,
                func.row_number()
                .over(
                    partition_by=source_snapshots.c.source,
                    order_by=(
                        source_snapshots.c.observed_at.desc(),
                        source_snapshots.c.accepted_at.desc(),
                        source_snapshots.c.snapshot_id.desc(),
                    ),
                )
                .label("position"),
            )
            .where(source_snapshots.c.complete == 1)
            .subquery()
        )
        with self.engine.begin() as connection:
            rows = connection.execute(
                select(ranked).where(ranked.c.position == 1)
            ).mappings().all()
        return [self._snapshot(row) for row in rows]

    def workflow_extension_records(
        self,
        *,
        workflow_key: str | None = None,
        person_id: str | None = None,
        limit: int = 250,
    ) -> list[dict[str, Any]]:
        query = select(workflow_extension_outbox)
        if workflow_key:
            query = query.where(
                workflow_extension_outbox.c.workflow_key == workflow_key
            )
        if person_id:
            query = query.where(
                workflow_extension_outbox.c.person_id == person_id
            )
        query = query.order_by(
            workflow_extension_outbox.c.created_at.desc()
        ).limit(max(1, min(limit, 1000)))
        with self.engine.begin() as connection:
            rows = connection.execute(query).mappings().all()
        return [
            {
                **dict(row),
                "reasons": json.loads(row["reason_json"]),
                "payload": json.loads(row["payload_json"]),
                "audit": json.loads(row["audit_json"]),
            }
            for row in rows
        ]

    def record_workflow_extension(
        self,
        plan: dict[str, Any],
    ) -> dict[str, Any]:
        outbox = plan["outbox"]
        audit = plan["audit"]
        decision = plan["decision"]
        now = datetime.now(UTC)
        due_at = (
            datetime.fromisoformat(
                str(outbox["due_at"]).replace("Z", "+00:00")
            )
            if outbox.get("due_at")
            else None
        )
        queued_at = (
            datetime.fromisoformat(
                str(outbox["queued_at"]).replace("Z", "+00:00")
            )
            if outbox.get("queued_at")
            else None
        )
        values = {
            "idempotency_key": outbox["idempotency_key"],
            "workflow_key": outbox["workflow_key"],
            "decision_id": outbox["decision_id"],
            "decision_version": outbox["decision_version"],
            "decision_fingerprint": decision["decision_fingerprint"],
            "person_id": outbox["person_id"],
            "contact_id": outbox.get("contact_id"),
            "source_snapshot_id": decision["source"]["snapshot_id"],
            "action_type": outbox["action_type"],
            "owner_role": outbox.get("owner_role"),
            "owner_user_id": outbox.get("owner_user_id"),
            "due_at": due_at,
            "dedupe_scope": outbox["dedupe_scope"],
            "state": outbox["state"],
            "reason_json": canonical_json(audit["result_reasons"]),
            "payload_json": canonical_json(outbox["payload"]),
            "audit_json": canonical_json(audit),
            "created_at": now,
            "updated_at": now,
            "queued_at": queued_at,
        }
        with self.engine.begin() as connection:
            existing = connection.execute(
                select(workflow_extension_outbox).where(
                    workflow_extension_outbox.c.idempotency_key
                    == outbox["idempotency_key"]
                )
            ).mappings().first()
            if existing:
                return {
                    "status": "duplicate",
                    "idempotency_key": outbox["idempotency_key"],
                    "state": existing["state"],
                }
            connection.execute(
                insert(workflow_extension_outbox).values(**values)
            )
            connection.execute(
                insert(workflow_extension_audit).values(
                    audit_id=uuid.uuid4().hex,
                    idempotency_key=outbox["idempotency_key"],
                    workflow_key=outbox["workflow_key"],
                    decision_id=outbox["decision_id"],
                    event_type="planned",
                    state=outbox["state"],
                    occurred_at=now,
                    evidence_json=canonical_json(audit),
                )
            )
        return {
            "status": "recorded",
            "idempotency_key": outbox["idempotency_key"],
            "state": outbox["state"],
        }

    def mark_workflow_extension_dispatched(
        self,
        idempotency_key: str,
        *,
        external_action_id: str,
        evidence: dict[str, Any],
        occurred_at: datetime | None = None,
    ) -> dict[str, Any]:
        action_id = str(external_action_id or "").strip()
        if not action_id:
            raise ValueError("external_action_id is required")
        dispatched_at = (occurred_at or datetime.now(UTC)).astimezone(UTC)
        with self.engine.begin() as connection:
            row = connection.execute(
                select(workflow_extension_outbox).where(
                    workflow_extension_outbox.c.idempotency_key
                    == idempotency_key
                )
            ).mappings().first()
            if not row:
                raise KeyError("workflow extension outbox record not found")
            if row["state"] == "dispatched":
                if row["external_action_id"] != action_id:
                    raise RuntimeError(
                        "outbox record already has a different external action"
                    )
                return {
                    "status": "duplicate",
                    "idempotency_key": idempotency_key,
                    "external_action_id": action_id,
                }
            if row["state"] != "queued":
                raise RuntimeError(
                    f"cannot dispatch outbox state: {row['state']}"
                )
            connection.execute(
                update(workflow_extension_outbox)
                .where(
                    workflow_extension_outbox.c.idempotency_key
                    == idempotency_key
                )
                .values(
                    state="dispatched",
                    dispatched_at=dispatched_at,
                    external_action_id=action_id,
                    updated_at=dispatched_at,
                )
            )
            connection.execute(
                insert(workflow_extension_audit).values(
                    audit_id=uuid.uuid4().hex,
                    idempotency_key=idempotency_key,
                    workflow_key=row["workflow_key"],
                    decision_id=row["decision_id"],
                    event_type="dispatched",
                    state="dispatched",
                    occurred_at=dispatched_at,
                    evidence_json=canonical_json(
                        {
                            "external_action_id": action_id,
                            "evidence": evidence,
                        }
                    ),
                )
            )
        return {
            "status": "dispatched",
            "idempotency_key": idempotency_key,
            "external_action_id": action_id,
        }

    @staticmethod
    def _stable_id(*parts: Any) -> str:
        value = ":".join(str(part or "").strip().lower() for part in parts)
        return uuid.uuid5(uuid.NAMESPACE_URL, value).hex

    @staticmethod
    def _override_matches_account(
        override: dict[str, Any],
        account: dict[str, Any],
    ) -> bool:
        if override["source"] != account.get("source"):
            return False
        source_account_id = str(
            override.get("source_account_id") or ""
        )
        agreement_id = str(override.get("agreement_id") or "")
        return (
            (not source_account_id or source_account_id == str(
                account.get("source_account_id") or ""
            ))
            and (
                not agreement_id
                or agreement_id == str(account.get("agreement_id") or "")
            )
        )

    @staticmethod
    def _override_applies_on(
        override: dict[str, Any],
        occurred_on: str | None,
    ) -> bool:
        if not occurred_on:
            return True
        return (
            (
                not override.get("effective_from")
                or str(override["effective_from"]) <= occurred_on
            )
            and (
                not override.get("effective_to")
                or str(override["effective_to"]) >= occurred_on
            )
        )

    @staticmethod
    def _override_amount_matches_account(
        override: dict[str, Any],
        account: dict[str, Any],
    ) -> bool:
        expected = str(
            override.get("expected_weekly_amount") or ""
        )
        return (
            not expected
            or expected == str(account.get("weekly_amount") or "")
        )

    def _active_payment_service_overrides(
        self,
        connection=None,
    ) -> list[dict[str, Any]]:
        def fetch(active_connection):
            return [
                dict(row)
                for row in active_connection.execute(
                    select(payment_service_overrides).where(
                        payment_service_overrides.c.active == 1
                    )
                ).mappings().all()
            ]

        if connection is not None:
            return fetch(connection)
        with self.engine.begin() as active_connection:
            return fetch(active_connection)

    def _apply_overrides_to_pt_minder_snapshot(
        self,
        snapshot: dict[str, Any],
    ) -> dict[str, Any]:
        projected = json.loads(canonical_json(snapshot))
        overrides = self._active_payment_service_overrides()
        applied = 0
        for account in projected["payload"].get("rows") or []:
            matching = [
                override
                for override in overrides
                if self._override_matches_account(override, {
                    **account,
                    "source": "pt_minder",
                })
                and self._override_amount_matches_account(
                    override,
                    account,
                )
            ]
            if not matching:
                continue
            matching.sort(
                key=lambda item: (
                    bool(item.get("source_account_id")),
                    bool(item.get("agreement_id")),
                    str(item.get("observed_at") or ""),
                ),
                reverse=True,
            )
            override = matching[0]
            account["governed_service_type"] = override["service_type"]
            account["governed_cadence"] = override["cadence"]
            account["service_override"] = {
                "override_id": override["override_id"],
                "approved_by": override["approved_by"],
                "reason": override["reason"],
                "source_label_preserved": True,
            }
            for transaction in account.get("transactions") or []:
                if not self._override_applies_on(
                    override,
                    transaction.get("occurred_on"),
                ):
                    continue
                transaction["raw_service_type"] = transaction[
                    "service_type"
                ]
                transaction["raw_cadence"] = transaction["cadence"]
                transaction["service_type"] = override["service_type"]
                transaction["cadence"] = override["cadence"]
                transaction["classification"] = "governed_override"
                transaction["classification_note"] = override["reason"]
                applied += 1
        projected["governance"] = {
            "payment_service_overrides_applied": applied,
            "raw_source_payload_preserved": True,
        }
        return projected

    def accept_payment_service_overrides(
        self,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        result = self.accept_snapshot(
            "payment_service_overrides",
            payload,
        )
        snapshot_id = str(result["snapshot_id"])
        observed_at = datetime.fromisoformat(
            str(payload["observed_at"]).replace("Z", "+00:00")
        )
        with self.engine.begin() as connection:
            for item in payload["rows"]:
                override_id = self._stable_id(
                    "payment-service-override",
                    item["source"],
                    item.get("source_account_id"),
                    item.get("agreement_id"),
                )
                override = {
                    "override_id": override_id,
                    "source": item["source"],
                    "source_account_id": item.get("source_account_id"),
                    "agreement_id": item.get("agreement_id"),
                    "service_type": item["service_type"],
                    "cadence": item["cadence"],
                    "expected_weekly_amount": item.get(
                        "expected_weekly_amount"
                    ),
                    "effective_from": item.get("effective_from"),
                    "effective_to": item.get("effective_to"),
                    "approved_by": item["approved_by"],
                    "reason": item["reason"],
                    "active": int(item["active"]),
                    "observed_at": observed_at,
                    "source_snapshot_id": snapshot_id,
                }
                self._replace_by_id(
                    connection,
                    payment_service_overrides,
                    payment_service_overrides.c.override_id,
                    override_id,
                    override,
                )
        return {
            **result,
            "governance": self.payment_service_override_state(),
        }

    def payment_service_override_state(self) -> dict[str, Any]:
        with self.engine.begin() as connection:
            rows = [
                dict(row)
                for row in connection.execute(
                    select(payment_service_overrides)
                ).mappings().all()
            ]
        active = [row for row in rows if row["active"]]
        return {
            "status": "ready",
            "active_overrides": len(active),
            "inactive_overrides": len(rows) - len(active),
            "sources": sorted(
                {str(row["source"]) for row in active}
            ),
            "raw_source_labels_preserved": True,
        }

    def _upsert_person(
        self,
        connection,
        *,
        canonical_key: str,
        email: str | None,
        first_name: str | None,
        last_name: str | None,
        observed_at: datetime,
    ) -> str:
        person_id = self._stable_id("person", canonical_key)
        existing = connection.execute(
            select(canonical_people.c.person_id).where(
                canonical_people.c.person_id == person_id
            )
        ).scalar()
        if existing:
            values: dict[str, Any] = {
                "email": email,
                "updated_at": observed_at,
            }
            if first_name is not None:
                values["first_name"] = first_name
            if last_name is not None:
                values["last_name"] = last_name
            connection.execute(
                update(canonical_people)
                .where(canonical_people.c.person_id == person_id)
                .values(**values)
            )
        else:
            connection.execute(
                insert(canonical_people).values(
                    person_id=person_id,
                    canonical_key=canonical_key,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    created_at=observed_at,
                    updated_at=observed_at,
                )
            )
        return person_id

    @staticmethod
    def _replace_by_id(connection, table: Table, field, value: str, row: dict[str, Any]):
        existing = connection.execute(
            select(field).where(field == value)
        ).scalar()
        if existing:
            connection.execute(
                update(table).where(field == value).values(**row)
            )
        else:
            connection.execute(insert(table).values(**row))

    def accept_membership_snapshot(
        self, payload: dict[str, Any]
    ) -> dict[str, Any]:
        result = self.accept_snapshot("membership_reconciliation", payload)
        snapshot_id = str(result["snapshot_id"])
        observed_at = datetime.fromisoformat(
            str(payload["observed_at"]).replace("Z", "+00:00")
        )
        with self.engine.begin() as connection:
            # These tables express the latest reconciled position. Preserve
            # historical rows, but retire anything not reaffirmed by this run.
            connection.execute(
                update(service_relationships)
                .where(
                    service_relationships.c.source
                    == "membership_reconciliation"
                )
                .values(
                    status="inactive",
                    observed_at=observed_at,
                    source_snapshot_id=snapshot_id,
                )
            )
            connection.execute(
                update(lifecycle_states)
                .where(
                    lifecycle_states.c.source
                    == "membership_reconciliation"
                )
                .values(
                    status="inactive",
                    observed_at=observed_at,
                    source_snapshot_id=snapshot_id,
                )
            )
            for item in payload["rows"]:
                person_id = self._upsert_person(
                    connection,
                    canonical_key=item["canonical_key"],
                    email=item.get("email"),
                    first_name=item.get("first_name"),
                    last_name=item.get("last_name"),
                    observed_at=observed_at,
                )
                for source, ids in item["source_ids"].items():
                    for source_id in ids:
                        row = {
                            "source": source,
                            "source_record_id": source_id,
                            "person_id": person_id,
                            "email": item.get("email"),
                            "observed_at": observed_at,
                            "source_snapshot_id": snapshot_id,
                        }
                        existing = connection.execute(
                            select(source_identities.c.person_id).where(
                                source_identities.c.source == source,
                                source_identities.c.source_record_id == source_id,
                            )
                        ).scalar()
                        if existing:
                            connection.execute(
                                update(source_identities)
                                .where(
                                    source_identities.c.source == source,
                                    source_identities.c.source_record_id == source_id,
                                )
                                .values(**row)
                            )
                        else:
                            connection.execute(
                                insert(source_identities).values(**row)
                            )

                for service in item["services"]:
                    relationship_id = self._stable_id(
                        "relationship",
                        person_id,
                        service["service_type"],
                        service.get("service_name"),
                        "membership_reconciliation",
                    )
                    relationship = {
                        "relationship_id": relationship_id,
                        "person_id": person_id,
                        "service_type": service["service_type"],
                        "service_name": service.get("service_name"),
                        "status": item["lifecycle_status"],
                        "source": "membership_reconciliation",
                        "source_record_id": payload["source_run_id"],
                        "effective_from": None,
                        "effective_to": item.get("final_access_date"),
                        "observed_at": observed_at,
                        "source_snapshot_id": snapshot_id,
                        "metadata_json": canonical_json(
                            {
                                "ghl_active": item["ghl_active"],
                                "stripe_entitled": item[
                                    "stripe_entitled"
                                ],
                                "trainerize_active": item[
                                    "trainerize_active"
                                ],
                            }
                        ),
                    }
                    self._replace_by_id(
                        connection,
                        service_relationships,
                        service_relationships.c.relationship_id,
                        relationship_id,
                        relationship,
                    )
                lifecycle = {
                    "person_id": person_id,
                    "status": item["lifecycle_status"],
                    "cancellation_status": item.get("cancellation_status"),
                    "cancellation_type": item.get("cancellation_type"),
                    "notice_end_date": item.get("notice_end_date"),
                    "final_access_date": item.get("final_access_date"),
                    "hold_status": item.get("hold_status"),
                    "hold_type": item.get("hold_type"),
                    "hold_start_date": item.get("hold_start_date"),
                    "hold_end_date": item.get("hold_end_date"),
                    "classification": item.get("classification"),
                    "source": "membership_reconciliation",
                    "observed_at": observed_at,
                    "source_snapshot_id": snapshot_id,
                    "evidence_json": canonical_json(
                        {
                            "source_run_id": payload["source_run_id"],
                            "ghl_active": item["ghl_active"],
                            "stripe_entitled": item["stripe_entitled"],
                            "trainerize_active": item["trainerize_active"],
                        }
                    ),
                }
                self._replace_by_id(
                    connection,
                    lifecycle_states,
                    lifecycle_states.c.person_id,
                    person_id,
                    lifecycle,
                )
        return {
            **result,
            "canonical": self.canonical_counts(),
        }

    def accept_service_change_event(
        self,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """Accept an immutable requested, accepted or exception event.

        The single current control row per canonical person prevents concurrent
        requests. Accepted events are also projected into canonical service
        relationships only after every required surface has succeeded.
        """
        now = datetime.now(UTC)
        occurred_at = datetime.fromisoformat(
            str(payload["occurred_at"]).replace("Z", "+00:00")
        )
        event_fingerprint = fingerprint(payload)
        request_core = {
            "request_id": payload["request_id"],
            "canonical_key": payload["canonical_key"],
            "contact_id": payload["contact_id"],
            "request_date": payload["request_date"],
            "effective_date": payload["effective_date"],
            "effective_at": payload["effective_at"],
            "offer_version": payload["offer_version"],
            "agreement_version": payload["agreement_version"],
            "signed_at": payload["signed_at"],
            "signature_document": payload["signature_document"],
            "prior_services": payload["prior_services"],
            "requested_services": payload["requested_services"],
        }
        request_fingerprint = fingerprint(request_core)
        event_id = self._stable_id(
            "service-change-event",
            payload["request_id"],
            payload["event_type"],
            payload["event_version"],
        )

        with self.engine.begin() as connection:
            existing_event = connection.execute(
                select(service_change_events).where(
                    service_change_events.c.event_id == event_id
                )
            ).mappings().first()
            if existing_event:
                if existing_event["event_fingerprint"] != event_fingerprint:
                    raise ValueError(
                        "service-change event key already exists with a different payload"
                    )
                return {
                    "status": "duplicate",
                    "event_id": event_id,
                    "request_id": payload["request_id"],
                    "event_type": payload["event_type"],
                }

            control = connection.execute(
                select(service_change_controls).where(
                    service_change_controls.c.canonical_key
                    == payload["canonical_key"]
                )
            ).mappings().first()

            if payload["event_type"] == "requested":
                if control and control["status"] == "requested":
                    raise ValueError(
                        "another service-change request is already pending for this person"
                    )
                if control and control["request_id"] == payload["request_id"]:
                    raise ValueError(
                        "request_id was already used with a different event payload"
                    )
                person_id = self._upsert_person(
                    connection,
                    canonical_key=payload["canonical_key"],
                    email=payload.get("email"),
                    first_name=None,
                    last_name=None,
                    observed_at=occurred_at,
                )
                control_values = {
                    "canonical_key": payload["canonical_key"],
                    "request_id": payload["request_id"],
                    "person_id": person_id,
                    "contact_id": payload["contact_id"],
                    "status": "requested",
                    "event_version": payload["event_version"],
                    "request_date": payload["request_date"],
                    "effective_date": payload["effective_date"],
                    "effective_at": datetime.fromisoformat(
                        str(payload["effective_at"]).replace("Z", "+00:00")
                    ),
                    "offer_version": payload["offer_version"],
                    "agreement_version": payload["agreement_version"],
                    "signed_at": datetime.fromisoformat(
                        str(payload["signed_at"]).replace("Z", "+00:00")
                    ),
                    "signature_document": payload["signature_document"],
                    "prior_services_json": canonical_json(
                        payload["prior_services"]
                    ),
                    "requested_services_json": canonical_json(
                        payload["requested_services"]
                    ),
                    "surface_statuses_json": canonical_json(
                        payload["surface_statuses"]
                    ),
                    "request_fingerprint": request_fingerprint,
                    "last_error": None,
                    "updated_at": now,
                }
                if control:
                    connection.execute(
                        update(service_change_controls)
                        .where(
                            service_change_controls.c.canonical_key
                            == payload["canonical_key"]
                        )
                        .values(**control_values)
                    )
                else:
                    connection.execute(
                        insert(service_change_controls).values(
                            **control_values
                        )
                    )
            else:
                if not control:
                    raise ValueError(
                        "service-change request has not been accepted by the hub"
                    )
                if control["request_id"] != payload["request_id"]:
                    raise ValueError(
                        "event does not match the active service-change request"
                    )
                if control["status"] not in {"requested", "exception"}:
                    raise ValueError(
                        "service-change request is no longer pending"
                    )
                if control["request_fingerprint"] != request_fingerprint:
                    raise ValueError(
                        "event does not match the immutable requested service change"
                    )
                if payload["event_version"] != int(control["event_version"]) + 1:
                    raise ValueError(
                        "service-change event_version must be the next version"
                    )
                person_id = str(control["person_id"])
                if payload["event_type"] == "accepted":
                    effective_at = datetime.fromisoformat(
                        str(payload["effective_at"]).replace("Z", "+00:00")
                    )
                    if occurred_at < effective_at:
                        raise ValueError(
                            "accepted event cannot precede the exact effective boundary"
                        )
                    prior_keys = {
                        (
                            item["service_type"],
                            item["service_name"].lower(),
                        )
                        for item in payload["prior_services"]
                    }
                    active_keys = {
                        (
                            str(row["service_type"]),
                            str(row["service_name"]).lower(),
                        )
                        for row in connection.execute(
                            select(
                                service_relationships.c.service_type,
                                service_relationships.c.service_name,
                            ).where(
                                service_relationships.c.person_id == person_id,
                                service_relationships.c.status == "active",
                            )
                        ).mappings()
                    }
                    if active_keys != prior_keys:
                        raise ValueError(
                            "hub current service state does not match the "
                            "immutable prior service snapshot"
                        )
                    connection.execute(
                        update(service_relationships)
                        .where(
                            service_relationships.c.person_id == person_id,
                            service_relationships.c.status == "active",
                        )
                        .values(
                            status="inactive",
                            effective_to=payload["effective_date"],
                            observed_at=occurred_at,
                            source_snapshot_id=event_id,
                        )
                    )
                    for service in payload["requested_services"]:
                        relationship_id = self._stable_id(
                            "service-change-relationship",
                            person_id,
                            service["service_type"],
                            service["service_name"],
                            payload["request_id"],
                        )
                        relationship = {
                            "relationship_id": relationship_id,
                            "person_id": person_id,
                            "service_type": service["service_type"],
                            "service_name": service["service_name"],
                            "status": "active",
                            "source": "service_change",
                            "source_record_id": payload["request_id"],
                            "effective_from": payload["effective_date"],
                            "effective_to": None,
                            "observed_at": occurred_at,
                            "source_snapshot_id": event_id,
                            "metadata_json": canonical_json(
                                {
                                    "event_id": event_id,
                                    "event_version": payload[
                                        "event_version"
                                    ],
                                    "offer_version": payload[
                                        "offer_version"
                                    ],
                                    "weekly_price_cents": service.get(
                                        "weekly_price_cents"
                                    ),
                                    "quantity": service.get("quantity"),
                                    "unit": service.get("unit"),
                                    "replaced_prior_service": (
                                        (
                                            service["service_type"],
                                            service["service_name"].lower(),
                                        )
                                        in prior_keys
                                    ),
                                }
                            ),
                        }
                        self._replace_by_id(
                            connection,
                            service_relationships,
                            service_relationships.c.relationship_id,
                            relationship_id,
                            relationship,
                        )
                    next_status = "accepted"
                    last_error = None
                else:
                    next_status = "exception"
                    last_error = payload["last_error"]
                connection.execute(
                    update(service_change_controls)
                    .where(
                        service_change_controls.c.canonical_key
                        == payload["canonical_key"]
                    )
                    .values(
                        status=next_status,
                        event_version=payload["event_version"],
                        surface_statuses_json=canonical_json(
                            payload["surface_statuses"]
                        ),
                        last_error=last_error,
                        updated_at=now,
                    )
                )

            connection.execute(
                insert(service_change_events).values(
                    event_id=event_id,
                    request_id=payload["request_id"],
                    canonical_key=payload["canonical_key"],
                    person_id=person_id,
                    event_type=payload["event_type"],
                    event_version=payload["event_version"],
                    occurred_at=occurred_at,
                    accepted_at=now,
                    event_fingerprint=event_fingerprint,
                    payload_json=canonical_json(payload),
                )
            )

        return {
            "status": "accepted",
            "event_id": event_id,
            "request_id": payload["request_id"],
            "event_type": payload["event_type"],
            "event_version": payload["event_version"],
            "canonical_projection_updated": (
                payload["event_type"] == "accepted"
            ),
        }

    def service_change_state(self, request_id: str) -> dict[str, Any] | None:
        with self.engine.begin() as connection:
            control = connection.execute(
                select(service_change_controls).where(
                    service_change_controls.c.request_id == request_id
                )
            ).mappings().first()
            if not control:
                return None
            events = connection.execute(
                select(
                    service_change_events.c.event_id,
                    service_change_events.c.event_type,
                    service_change_events.c.event_version,
                    service_change_events.c.occurred_at,
                    service_change_events.c.accepted_at,
                )
                .where(service_change_events.c.request_id == request_id)
                .order_by(service_change_events.c.event_version)
            ).mappings().all()
        return {
            "request_id": control["request_id"],
            "canonical_key": control["canonical_key"],
            "contact_id": control["contact_id"],
            "status": control["status"],
            "event_version": control["event_version"],
            "request_date": control["request_date"],
            "effective_date": control["effective_date"],
            "effective_at": (
                control["effective_at"].isoformat()
                if control["effective_at"]
                else None
            ),
            "offer_version": control["offer_version"],
            "agreement_version": control["agreement_version"],
            "surface_statuses": json.loads(
                control["surface_statuses_json"]
            ),
            "last_error": control["last_error"],
            "updated_at": control["updated_at"].isoformat(),
            "events": [
                {
                    **dict(event),
                    "occurred_at": event["occurred_at"].isoformat(),
                    "accepted_at": event["accepted_at"].isoformat(),
                }
                for event in events
            ],
        }

    def accept_pt_minder_snapshot(
        self, payload: dict[str, Any]
    ) -> dict[str, Any]:
        result = self.accept_snapshot("pt_minder", payload)
        snapshot_id = str(result["snapshot_id"])
        observed_at = datetime.fromisoformat(
            str(payload["observed_at"]).replace("Z", "+00:00")
        )
        with self.engine.begin() as connection:
            for item in payload["rows"]:
                person_id = None
                if item.get("email"):
                    person_id = self._upsert_person(
                        connection,
                        canonical_key=item["email"],
                        email=item["email"],
                        first_name=None,
                        last_name=None,
                        observed_at=observed_at,
                    )
                    identity = {
                        "source": "pt_minder",
                        "source_record_id": item["source_account_id"],
                        "person_id": person_id,
                        "email": item["email"],
                        "observed_at": observed_at,
                        "source_snapshot_id": snapshot_id,
                    }
                    existing_identity = connection.execute(
                        select(source_identities.c.person_id).where(
                            source_identities.c.source == "pt_minder",
                            source_identities.c.source_record_id
                            == item["source_account_id"],
                        )
                    ).scalar()
                    if existing_identity:
                        connection.execute(
                            update(source_identities)
                            .where(
                                source_identities.c.source == "pt_minder",
                                source_identities.c.source_record_id
                                == item["source_account_id"],
                            )
                            .values(**identity)
                        )
                    else:
                        connection.execute(
                            insert(source_identities).values(**identity)
                        )

                account_id = self._stable_id(
                    "payment-account",
                    "pt_minder",
                    item["source_account_id"],
                )
                account = {
                    "payment_account_id": account_id,
                    "person_id": person_id,
                    "source": "pt_minder",
                    "source_account_id": item["source_account_id"],
                    "agreement_id": item.get("agreement_id"),
                    "status": item["state"],
                    "weekly_amount": item.get("weekly_amount"),
                    "observed_at": observed_at,
                    "source_snapshot_id": snapshot_id,
                }
                self._replace_by_id(
                    connection,
                    payment_accounts,
                    payment_accounts.c.payment_account_id,
                    account_id,
                    account,
                )
                for transaction in item.get("transactions") or []:
                    event_id = self._stable_id(
                        "payment-event",
                        "pt_minder",
                        transaction["source_transaction_id"],
                    )
                    event = {
                        "payment_event_id": event_id,
                        "payment_account_id": account_id,
                        "person_id": person_id,
                        "source": "pt_minder",
                        "source_event_id": transaction[
                            "source_transaction_id"
                        ],
                        "occurred_on": transaction["occurred_on"],
                        "amount": transaction["amount"],
                        "status": transaction["status"],
                        "service_type": transaction["service_type"],
                        "cadence": transaction["cadence"],
                        "description": transaction["description"],
                        "coverage_start": transaction.get(
                            "coverage_start"
                        ),
                        "coverage_end": transaction.get("coverage_end"),
                        "source_snapshot_id": snapshot_id,
                    }
                    self._replace_by_id(
                        connection,
                        payment_events,
                        payment_events.c.payment_event_id,
                        event_id,
                        event,
                    )
        return {
            **result,
            "canonical": self.canonical_counts(),
        }

    def accept_active_client_cohort(
        self, payload: dict[str, Any]
    ) -> dict[str, Any]:
        result = self.accept_snapshot("active_client_cohort", payload)
        snapshot_id = str(result["snapshot_id"])
        observed_at = datetime.fromisoformat(
            str(payload["observed_at"]).replace("Z", "+00:00")
        )
        with self.engine.begin() as connection:
            connection.execute(
                update(governed_cohort_members).values(current=0)
            )
            connection.execute(
                update(service_relationships)
                .where(
                    service_relationships.c.source
                    == "active_client_cohort"
                )
                .values(
                    status="inactive",
                    observed_at=observed_at,
                    source_snapshot_id=snapshot_id,
                )
            )
            connection.execute(
                update(entitlements)
                .where(entitlements.c.source == "active_client_cohort")
                .values(
                    status="superseded",
                    observed_at=observed_at,
                    source_snapshot_id=snapshot_id,
                )
            )
            for item in payload["rows"]:
                canonical_key = item["canonical_key"]
                email = (
                    canonical_key if "@" in canonical_key else None
                )
                evidence = item["evidence"]
                person_id = self._upsert_person(
                    connection,
                    canonical_key=canonical_key,
                    email=email,
                    first_name=None,
                    last_name=None,
                    observed_at=observed_at,
                )
                cohort_member_id = self._stable_id(
                    "governed-cohort",
                    person_id,
                    snapshot_id,
                )
                cohort_member = {
                    "cohort_member_id": cohort_member_id,
                    "person_id": person_id,
                    "canonical_key": canonical_key,
                    "disposition": item["disposition"],
                    "confirmed_active": int(item["confirmed_active"]),
                    "paid_or_entitled": (
                        None
                        if item["paid_or_entitled"] is None
                        else int(item["paid_or_entitled"])
                    ),
                    "decision_required": int(item["decision_required"]),
                    "primary_reason": item["primary_reason"],
                    "owner": item.get("owner"),
                    "owner_question": item.get("owner_question"),
                    "as_of_date": payload["as_of_date"],
                    "rule_version": payload["rule_version"],
                    "current": 1,
                    "observed_at": observed_at,
                    "source_snapshot_id": snapshot_id,
                    "evidence_json": canonical_json(evidence),
                }
                self._replace_by_id(
                    connection,
                    governed_cohort_members,
                    governed_cohort_members.c.cohort_member_id,
                    cohort_member_id,
                    cohort_member,
                )
                if not item["confirmed_active"]:
                    continue
                for service in evidence.get("governed_roster") or []:
                    service_type = {
                        "SGPT": "sgpt",
                        "PT": "personal_training",
                    }[service["service"]]
                    product = service.get("product")
                    relationship_id = self._stable_id(
                        "relationship",
                        person_id,
                        service_type,
                        product,
                        "active_client_cohort",
                    )
                    relationship = {
                        "relationship_id": relationship_id,
                        "person_id": person_id,
                        "service_type": service_type,
                        "service_name": product,
                        "status": "active",
                        "source": "active_client_cohort",
                        "source_record_id": snapshot_id,
                        "effective_from": None,
                        "effective_to": service.get("effective_to"),
                        "observed_at": observed_at,
                        "source_snapshot_id": snapshot_id,
                        "metadata_json": canonical_json(service),
                    }
                    self._replace_by_id(
                        connection,
                        service_relationships,
                        service_relationships.c.relationship_id,
                        relationship_id,
                        relationship,
                    )
                    entitlement_id = self._stable_id(
                        "entitlement",
                        person_id,
                        service_type,
                        product,
                        "active_client_cohort",
                    )
                    if item["paid_or_entitled"] is True:
                        entitlement_status = "confirmed"
                    elif item["paid_or_entitled"] is False:
                        entitlement_status = "not_entitled"
                    else:
                        entitlement_status = "unverified"
                    entitlement = {
                        "entitlement_id": entitlement_id,
                        "person_id": person_id,
                        "service_type": service_type,
                        "quantity": None,
                        "unit": None,
                        "status": entitlement_status,
                        "effective_from": None,
                        "effective_to": service.get("effective_to"),
                        "source": "active_client_cohort",
                        "source_record_id": snapshot_id,
                        "observed_at": observed_at,
                        "source_snapshot_id": snapshot_id,
                        "metadata_json": canonical_json(
                            {
                                "basis": "governed_roster",
                                "service": service,
                                "paid_or_entitled": item[
                                    "paid_or_entitled"
                                ],
                            }
                        ),
                    }
                    self._replace_by_id(
                        connection,
                        entitlements,
                        entitlements.c.entitlement_id,
                        entitlement_id,
                        entitlement,
                    )
        return {
            **result,
            "canonical": self.canonical_counts(),
            "governed": self.governed_state(),
        }

    def accept_commercial_evidence(
        self, payload: dict[str, Any]
    ) -> dict[str, Any]:
        source = payload["source_system"]
        snapshot_source = f"commercial_evidence_{source}"
        result = self.accept_snapshot(snapshot_source, payload)
        snapshot_id = str(result["snapshot_id"])
        observed_at = datetime.fromisoformat(
            str(payload["observed_at"]).replace("Z", "+00:00")
        )
        with self.engine.begin() as connection:
            connection.execute(
                update(entitlements)
                .where(entitlements.c.source == source)
                .values(
                    status="superseded",
                    observed_at=observed_at,
                    source_snapshot_id=snapshot_id,
                )
            )
            for item in payload["rows"]:
                person_id = self._upsert_person(
                    connection,
                    canonical_key=item["canonical_key"],
                    email=item.get("email"),
                    first_name=None,
                    last_name=None,
                    observed_at=observed_at,
                )
                for source_id in item["source_identity_ids"]:
                    identity = {
                        "source": source,
                        "source_record_id": source_id,
                        "person_id": person_id,
                        "email": item.get("email"),
                        "observed_at": observed_at,
                        "source_snapshot_id": snapshot_id,
                    }
                    existing = connection.execute(
                        select(source_identities.c.person_id).where(
                            source_identities.c.source == source,
                            source_identities.c.source_record_id == source_id,
                        )
                    ).scalar()
                    if existing:
                        connection.execute(
                            update(source_identities)
                            .where(
                                source_identities.c.source == source,
                                source_identities.c.source_record_id
                                == source_id,
                            )
                            .values(**identity)
                        )
                    else:
                        connection.execute(
                            insert(source_identities).values(**identity)
                        )
                for item_entitlement in item["entitlements"]:
                    entitlement_id = self._stable_id(
                        "entitlement",
                        source,
                        item_entitlement["source_record_id"],
                    )
                    entitlement = {
                        "entitlement_id": entitlement_id,
                        "person_id": person_id,
                        "service_type": item_entitlement["service_type"],
                        "quantity": item_entitlement["quantity"],
                        "unit": item_entitlement["unit"],
                        "status": item_entitlement["status"],
                        "effective_from": item_entitlement[
                            "effective_from"
                        ],
                        "effective_to": item_entitlement["effective_to"],
                        "source": source,
                        "source_record_id": item_entitlement[
                            "source_record_id"
                        ],
                        "observed_at": observed_at,
                        "source_snapshot_id": snapshot_id,
                        "metadata_json": canonical_json(
                            {
                                "basis": item_entitlement["basis"],
                                "payment_reference": item_entitlement[
                                    "payment_reference"
                                ],
                                "source_run_id": payload["source_run_id"],
                            }
                        ),
                    }
                    self._replace_by_id(
                        connection,
                        entitlements,
                        entitlements.c.entitlement_id,
                        entitlement_id,
                        entitlement,
                    )
                account_ids: dict[str, str] = {}
                for item_account in item["payment_accounts"]:
                    account_id = self._stable_id(
                        "payment-account",
                        source,
                        item_account["source_account_id"],
                    )
                    account_ids[
                        item_account["source_account_id"]
                    ] = account_id
                    account = {
                        "payment_account_id": account_id,
                        "person_id": person_id,
                        "source": source,
                        "source_account_id": item_account[
                            "source_account_id"
                        ],
                        "agreement_id": item_account["agreement_id"],
                        "status": item_account["status"],
                        "weekly_amount": item_account["weekly_amount"],
                        "observed_at": observed_at,
                        "source_snapshot_id": snapshot_id,
                    }
                    self._replace_by_id(
                        connection,
                        payment_accounts,
                        payment_accounts.c.payment_account_id,
                        account_id,
                        account,
                    )
                for item_event in item["payment_events"]:
                    event_id = self._stable_id(
                        "payment-event",
                        source,
                        item_event["source_event_id"],
                    )
                    event = {
                        "payment_event_id": event_id,
                        "payment_account_id": account_ids[
                            item_event["source_account_id"]
                        ],
                        "person_id": person_id,
                        "source": source,
                        "source_event_id": item_event["source_event_id"],
                        "occurred_on": item_event["occurred_on"],
                        "amount": item_event["amount"],
                        "status": item_event["status"],
                        "service_type": item_event["service_type"],
                        "cadence": item_event["cadence"],
                        "description": item_event["description"],
                        "coverage_start": item_event.get(
                            "coverage_start"
                        ),
                        "coverage_end": item_event.get("coverage_end"),
                        "source_snapshot_id": snapshot_id,
                    }
                    self._replace_by_id(
                        connection,
                        payment_events,
                        payment_events.c.payment_event_id,
                        event_id,
                        event,
                    )
        return {
            **result,
            "canonical": self.canonical_counts(),
            "governed": self.governed_state(),
        }

    def governed_state(
        self,
        *,
        as_of: date | None = None,
    ) -> dict[str, Any] | None:
        reporting_date = as_of or datetime.now(UTC).date()
        with self.engine.begin() as connection:
            rows = connection.execute(
                select(governed_cohort_members).where(
                    governed_cohort_members.c.current == 1
                )
            ).mappings().all()
            if not rows:
                return None
            active_relationships = int(
                connection.execute(
                    select(func.count())
                    .select_from(service_relationships)
                    .where(
                        service_relationships.c.source
                        == "active_client_cohort",
                        service_relationships.c.status == "active",
                    )
                ).scalar_one()
            )
            current_entitlements = connection.execute(
                select(
                    entitlements.c.person_id,
                    entitlements.c.source,
                    entitlements.c.status,
                    entitlements.c.service_type,
                    entitlements.c.effective_from,
                    entitlements.c.effective_to,
                ).where(
                    entitlements.c.status != "superseded",
                )
            ).mappings().all()
            active_service_rows = connection.execute(
                select(
                    service_relationships.c.person_id,
                    service_relationships.c.service_type,
                    service_relationships.c.service_name,
                ).where(
                    service_relationships.c.source
                    == "active_client_cohort",
                    service_relationships.c.status == "active",
                )
            ).mappings().all()
            lifecycle_rows = connection.execute(
                select(
                    lifecycle_states.c.person_id,
                    lifecycle_states.c.status,
                    lifecycle_states.c.cancellation_status,
                    lifecycle_states.c.cancellation_type,
                    lifecycle_states.c.final_access_date,
                ).where(
                    lifecycle_states.c.source
                    == "membership_reconciliation"
                )
            ).mappings().all()
        confirmed = {
            row["person_id"] for row in rows if row["confirmed_active"]
        }
        as_of_date = str(rows[0]["as_of_date"])
        confirmed_types: dict[str, set[str]] = {}
        for row in current_entitlements:
            if (
                row["source"] == "active_client_cohort"
                or row["status"] != "confirmed"
                or (
                    row["effective_from"]
                    and str(row["effective_from"]) > as_of_date
                )
                or (
                    row["effective_to"]
                    and str(row["effective_to"]) < as_of_date
                )
            ):
                continue
            confirmed_types.setdefault(
                str(row["person_id"]), set()
            ).add(str(row["service_type"]))
        required_types: dict[str, set[str]] = {}
        for row in active_service_rows:
            person_id = str(row["person_id"])
            required_types.setdefault(person_id, set()).add(
                str(row["service_type"])
            )
        fully_covered = {
            person_id
            for person_id in confirmed
            if required_types.get(str(person_id))
            and all(
                service_is_covered(
                    service_type,
                    confirmed_types.get(str(person_id), set()),
                )
                for service_type in required_types[str(person_id)]
            )
        }
        first = rows[0]
        active_people_services = {
            str(person_id): required_types.get(str(person_id), set())
            for person_id in confirmed
        }
        for lifecycle in lifecycle_rows:
            person_id = str(lifecycle["person_id"])
            services = active_people_services.get(person_id)
            if not services:
                continue
            cancellation_type = str(
                lifecycle["cancellation_type"] or ""
            ).strip().lower()
            final_access_text = str(
                lifecycle["final_access_date"] or ""
            ).strip()
            if (
                cancellation_type == "pt"
                and final_access_text
                and date.fromisoformat(final_access_text) < reporting_date
            ):
                services.discard("personal_training")
        group_and_pt_people = {
            person_id
            for person_id, services in active_people_services.items()
            if {"sgpt", "personal_training"} <= services
        }
        # Fast Track is the governed service combination: concurrent SGPT and
        # personal training. A member remains Fast Track throughout a notice
        # period and moves to Strength & Sculpt only when the PT relationship
        # reaches its evidenced effective end date.
        fast_track_people = group_and_pt_people
        pt_only_people = {
            person_id
            for person_id, services in active_people_services.items()
            if services == {"personal_training"}
        }
        sgpt_people = {
            person_id
            for person_id, services in active_people_services.items()
            if "sgpt" in services
        }
        strength_and_sculpt_only_people = (
            sgpt_people - fast_track_people
        )
        return {
            "persisted": True,
            "snapshot_id": first["source_snapshot_id"],
            "as_of_date": first["as_of_date"],
            "rule_version": first["rule_version"],
            "union_people": len(rows),
            "confirmed_active_clients": len(confirmed),
            "active_service_relationships": active_relationships,
            "service_breakdown": {
                "strength_and_sculpt_only": len(
                    strength_and_sculpt_only_people
                ),
                "strength_and_sculpt_access": len(sgpt_people),
                "fast_track": len(fast_track_people),
                "sgpt_with_pt_add_on": 0,
                "pt_only": len(pt_only_people),
                "pt_service_clients": sum(
                    "personal_training" in services
                    for services in active_people_services.values()
                ),
            },
            "paid_or_entitled_confirmed": len(
                fully_covered
            ),
            "paid_or_entitled_unverified": len(
                confirmed - fully_covered
            ),
            "decision_required": sum(
                bool(row["decision_required"]) for row in rows
            ),
        }

    def sgpt_delivery_identity_context(self) -> dict[str, Any]:
        """Resolve Trainerize IDs through the shared identity/cohort layer."""
        with self.engine.begin() as connection:
            active_sgpt_rows = connection.execute(
                select(
                    service_relationships.c.person_id,
                    canonical_people.c.first_name,
                    canonical_people.c.last_name,
                    canonical_people.c.email,
                )
                .select_from(
                    service_relationships.join(
                        canonical_people,
                        service_relationships.c.person_id
                        == canonical_people.c.person_id,
                    )
                )
                .where(
                    service_relationships.c.source
                    == "active_client_cohort",
                    service_relationships.c.status == "active",
                    service_relationships.c.service_type == "sgpt",
                )
            ).mappings().all()
            trainerize_rows = connection.execute(
                select(
                    source_identities.c.source_record_id,
                    source_identities.c.person_id,
                ).where(source_identities.c.source == "trainerize")
            ).mappings().all()
        active_members = {
            str(row["person_id"]): {
                "person_id": str(row["person_id"]),
                "name": " ".join(
                    part
                    for part in (
                        str(row["first_name"] or "").strip(),
                        str(row["last_name"] or "").strip(),
                    )
                    if part
                )
                or None,
                "email": str(row["email"] or "").strip() or None,
            }
            for row in active_sgpt_rows
        }
        return {
            "active_member_ids": sorted(active_members),
            "active_members": active_members,
            "trainerize_to_person_id": {
                str(row["source_record_id"]): str(row["person_id"])
                for row in trainerize_rows
            },
        }

    def active_notice_periods(
        self,
        *,
        as_of: date | None = None,
    ) -> dict[str, Any]:
        today = as_of or datetime.now(UTC).date()
        with self.engine.begin() as connection:
            rows = connection.execute(
                select(
                    lifecycle_states.c.person_id,
                    lifecycle_states.c.status,
                    lifecycle_states.c.cancellation_status,
                    lifecycle_states.c.cancellation_type,
                    lifecycle_states.c.notice_end_date,
                    lifecycle_states.c.final_access_date,
                    lifecycle_states.c.observed_at,
                    canonical_people.c.first_name,
                    canonical_people.c.last_name,
                    canonical_people.c.email,
                )
                .select_from(
                    lifecycle_states.join(
                        canonical_people,
                        lifecycle_states.c.person_id
                        == canonical_people.c.person_id,
                    )
                )
                .where(
                    lifecycle_states.c.source
                    == "membership_reconciliation"
                )
            ).mappings().all()
            governed_services = connection.execute(
                select(
                    service_relationships.c.person_id,
                    service_relationships.c.service_type,
                ).where(
                    service_relationships.c.source
                    == "active_client_cohort",
                    service_relationships.c.status == "active",
                )
            ).mappings().all()
            governed_people = {
                str(person_id)
                for person_id in connection.execute(
                    select(
                        governed_cohort_members.c.person_id
                    ).where(
                        governed_cohort_members.c.current == 1,
                        governed_cohort_members.c.confirmed_active == 1,
                    )
                ).scalars().all()
            }

        services_by_person: dict[str, set[str]] = {}
        for service in governed_services:
            services_by_person.setdefault(
                str(service["person_id"]), set()
            ).add(str(service["service_type"]))

        periods: list[dict[str, Any]] = []
        missing_dates = 0
        overdue = 0
        for row in rows:
            if str(row["person_id"]) not in governed_people:
                continue
            status = str(row["status"] or "").strip().lower()
            cancellation_status = str(
                row["cancellation_status"] or ""
            ).strip().lower()
            if status != "cancelling" and cancellation_status not in {
                "notice active",
                "cancelling",
            }:
                continue
            end_text = str(
                row["final_access_date"]
                or row["notice_end_date"]
                or ""
            ).strip()
            end_date = (
                date.fromisoformat(end_text)
                if end_text
                else None
            )
            if end_date and end_date < today:
                state = "overdue"
                overdue += 1
            elif end_date:
                state = "active"
            else:
                state = "date_missing"
                missing_dates += 1
            cancellation_type = str(
                row["cancellation_type"] or ""
            ).strip().lower()
            services = services_by_person.get(
                str(row["person_id"]), set()
            )
            if (
                cancellation_type == "pt"
                and {"sgpt", "personal_training"} <= services
            ):
                transition = "Fast Track → Strength & Sculpt"
                notice_type = "Downgrade"
                current_service = (
                    "Fast Track (Strength & Sculpt + 1:1 PT)"
                )
                future_service = "Strength & Sculpt"
            elif cancellation_type == "membership":
                transition = "Membership ending"
                notice_type = "Full membership cancellation"
                if {"sgpt", "personal_training"} <= services:
                    current_service = (
                        "Fast Track (Strength & Sculpt + 1:1 PT)"
                    )
                elif "sgpt" in services:
                    current_service = "Strength & Sculpt"
                elif "personal_training" in services:
                    current_service = "1:1 PT only"
                else:
                    current_service = "Current service not classified"
                future_service = "Membership ends"
            elif cancellation_type == "pt":
                transition = "Personal training ending"
                notice_type = "PT service cancellation"
                current_service = (
                    "1:1 PT only"
                    if "personal_training" in services
                    else "Current service not classified"
                )
                future_service = "1:1 PT service ends"
            else:
                transition = "Service change in progress"
                notice_type = "Service change"
                if {"sgpt", "personal_training"} <= services:
                    current_service = (
                        "Fast Track (Strength & Sculpt + 1:1 PT)"
                    )
                elif "sgpt" in services:
                    current_service = "Strength & Sculpt"
                elif "personal_training" in services:
                    current_service = "1:1 PT only"
                else:
                    current_service = "Current service not classified"
                future_service = "New service needs confirmation"
            name = " ".join(
                value
                for value in (
                    str(row["first_name"] or "").strip(),
                    str(row["last_name"] or "").strip(),
                )
                if value
            )
            periods.append(
                {
                    "client_name": name or None,
                    "email": row["email"],
                    "transition": transition,
                    "notice_type": notice_type,
                    "current_service": current_service,
                    "future_service": future_service,
                    "cancellation_type": (
                        str(row["cancellation_type"] or "").strip()
                        or None
                    ),
                    "notice_end_date": row["notice_end_date"],
                    "final_access_date": row["final_access_date"],
                    "effective_end_date": end_text or None,
                    "state": state,
                    "days_remaining": (
                        (end_date - today).days
                        if end_date and end_date >= today
                        else None
                    ),
                    "observed_at": row["observed_at"].isoformat(),
                }
            )
        periods.sort(
            key=lambda item: (
                item["effective_end_date"] or "9999-12-31",
                item["client_name"] or item["email"] or "",
            )
        )
        return {
            "as_of_date": today.isoformat(),
            "active_count": sum(
                item["state"] == "active" for item in periods
            ),
            "full_cancellation_count": sum(
                item["notice_type"] == "Full membership cancellation"
                for item in periods
            ),
            "downgrade_count": sum(
                item["notice_type"] == "Downgrade"
                for item in periods
            ),
            "pt_cancellation_count": sum(
                item["notice_type"] == "PT service cancellation"
                for item in periods
            ),
            "other_change_count": sum(
                item["notice_type"] == "Service change"
                for item in periods
            ),
            "missing_date_count": missing_dates,
            "overdue_count": overdue,
            "periods": periods,
        }

    def attrition_preview(
        self,
        *,
        period_start: date,
        period_end: date,
    ) -> dict[str, Any]:
        with self.engine.begin() as connection:
            lifecycle = connection.execute(
                select(
                    lifecycle_states.c.person_id,
                    lifecycle_states.c.status,
                    lifecycle_states.c.cancellation_type,
                    lifecycle_states.c.final_access_date,
                ).where(
                    lifecycle_states.c.source
                    == "membership_reconciliation"
                )
            ).mappings().all()
            current_active = {
                str(person_id)
                for person_id in connection.execute(
                    select(governed_cohort_members.c.person_id).where(
                        governed_cohort_members.c.current == 1,
                        governed_cohort_members.c.confirmed_active == 1,
                    )
                ).scalars().all()
            }
        ended_members: set[str] = set()
        pt_downgrades: set[str] = set()
        for row in lifecycle:
            end_text = str(row["final_access_date"] or "").strip()
            if not end_text:
                continue
            effective_end = date.fromisoformat(end_text)
            if not period_start <= effective_end <= period_end:
                continue
            person_id = str(row["person_id"])
            cancellation_type = str(
                row["cancellation_type"] or ""
            ).strip().lower()
            if (
                cancellation_type == "membership"
                and person_id not in current_active
                and str(row["status"] or "").strip().lower()
                in {"cancelled", "inactive", "cancelling"}
            ):
                ended_members.add(person_id)
            elif cancellation_type == "pt":
                pt_downgrades.add(person_id)
        return {
            "period_start": period_start.isoformat(),
            "period_end": period_end.isoformat(),
            "members_lost": len(ended_members),
            "pt_downgrades": len(pt_downgrades),
            "attrition_rate": None,
            "complete": False,
            "confidence": "provisional",
            "coverage_note": (
                "This counts final membership endings still represented in "
                "the latest lifecycle state. A historical opening cohort and "
                "immutable lifecycle events are still required before the "
                "attrition rate or net member growth can be accepted."
            ),
        }

    def recurring_income_projection_preview(
        self,
        *,
        max_age_hours: int = 96,
    ) -> dict[str, Any]:
        with self.engine.begin() as connection:
            rows = connection.execute(
                select(source_snapshots)
                .where(
                    source_snapshots.c.source == "revenue_control",
                    source_snapshots.c.complete == 1,
                )
                .order_by(
                    source_snapshots.c.observed_at.desc(),
                    source_snapshots.c.accepted_at.desc(),
                    source_snapshots.c.snapshot_id.desc(),
                )
                .limit(50)
            ).mappings().all()
        for row in rows:
            payload = json.loads(row["payload_json"])
            summary = payload.get("summary") or {}
            bridge = summary.get("cashBridge") or {}
            if not isinstance(bridge, dict):
                continue
            scheduled = bridge.get("scheduled_run_rate")
            confirmed = bridge.get("confirmed_current_income")
            if scheduled in (None, ""):
                continue
            observed_at = row["observed_at"]
            if observed_at.tzinfo is None:
                observed_at = observed_at.replace(tzinfo=UTC)
            age_hours = max(
                0,
                (datetime.now(UTC) - observed_at).total_seconds() / 3600,
            )
            available = age_hours <= max_age_hours
            return {
                "available": available,
                "definition_version": "scheduled-run-rate-v1",
                "projected_weekly_recurring_income": str(scheduled),
                "confirmed_weekly_recurring_income": (
                    str(confirmed) if confirmed not in (None, "") else None
                ),
                "window_start": summary.get("windowStart"),
                "window_end": summary.get("windowEnd"),
                "observed_at": observed_at.isoformat(),
                "age_hours": round(age_hours, 1),
                "confidence": "high" if available else "stale",
                "coverage_note": (
                    "Normalised weekly recurring schedules. Paid-in-advance "
                    "revenue, one-off packs and speculative new sales are "
                    "not included."
                ),
                "unavailable_reason": (
                    None
                    if available
                    else "Revenue Control evidence is older than 96 hours."
                ),
            }
        return {
            "available": False,
            "definition_version": "scheduled-run-rate-v1",
            "projected_weekly_recurring_income": None,
            "confirmed_weekly_recurring_income": None,
            "window_start": None,
            "window_end": None,
            "observed_at": None,
            "age_hours": None,
            "confidence": "unavailable",
            "coverage_note": (
                "Normalised weekly recurring schedules. Paid-in-advance "
                "revenue, one-off packs and speculative new sales are not "
                "included."
            ),
            "unavailable_reason": (
                "No complete Revenue Control cash bridge is available."
            ),
        }

    def entitlement_exception_queue(
        self,
        *,
        identified: bool = False,
    ) -> dict[str, Any]:
        with self.engine.begin() as connection:
            governed_rows = [
                dict(row)
                for row in connection.execute(
                    select(governed_cohort_members).where(
                        governed_cohort_members.c.current == 1,
                        governed_cohort_members.c.confirmed_active == 1,
                    )
                ).mappings().all()
            ]
            relationships = [
                dict(row)
                for row in connection.execute(
                    select(service_relationships).where(
                        service_relationships.c.source
                        == "active_client_cohort",
                        service_relationships.c.status == "active",
                    )
                ).mappings().all()
            ]
            entitlement_rows = [
                dict(row)
                for row in connection.execute(
                    select(entitlements).where(
                        entitlements.c.status != "superseded"
                    )
                ).mappings().all()
            ]
            lifecycle_rows = [
                dict(row)
                for row in connection.execute(
                    select(lifecycle_states)
                ).mappings().all()
            ]
            people_rows = [
                dict(row)
                for row in connection.execute(
                    select(canonical_people)
                ).mappings().all()
            ]
            payment_account_rows = [
                dict(row)
                for row in connection.execute(
                    select(payment_accounts)
                ).mappings().all()
            ]
            raw_payment_event_rows = [
                dict(row)
                for row in connection.execute(
                    select(payment_events)
                ).mappings().all()
            ]
            active_overrides = self._active_payment_service_overrides(
                connection
            )
        accounts_by_id = {
            str(row["payment_account_id"]): row
            for row in payment_account_rows
        }
        payment_event_rows = []
        for raw_event in raw_payment_event_rows:
            event = dict(raw_event)
            account = accounts_by_id.get(
                str(event["payment_account_id"])
            )
            if account:
                matching = [
                    override
                    for override in active_overrides
                    if self._override_matches_account(override, account)
                    and self._override_amount_matches_account(
                        override,
                        account,
                    )
                    and self._override_applies_on(
                        override,
                        event.get("occurred_on"),
                    )
                ]
                if matching:
                    matching.sort(
                        key=lambda item: (
                            bool(item.get("source_account_id")),
                            bool(item.get("agreement_id")),
                            str(item.get("observed_at") or ""),
                        ),
                        reverse=True,
                    )
                    override = matching[0]
                    event["raw_service_type"] = event["service_type"]
                    event["raw_cadence"] = event["cadence"]
                    event["service_type"] = override["service_type"]
                    event["cadence"] = override["cadence"]
                    event["service_override_id"] = override["override_id"]
            payment_event_rows.append(event)
        return build_entitlement_exception_queue(
            governed_rows=governed_rows,
            relationships=relationships,
            entitlement_rows=entitlement_rows,
            lifecycle_rows=lifecycle_rows,
            people_rows=people_rows,
            payment_account_rows=payment_account_rows,
            payment_event_rows=payment_event_rows,
            identified=identified,
        )

    def roster_candidate_state(self) -> dict[str, Any] | None:
        snapshot = self.latest_snapshot("active_roster_candidate")
        if not snapshot:
            return None
        payload = snapshot["payload"]
        candidate = {
            str(row["canonical_key"]).strip().lower(): row
            for row in payload["rows"]
        }
        with self.engine.begin() as connection:
            governed_rows = connection.execute(
                select(
                    canonical_people.c.canonical_key,
                    canonical_people.c.first_name,
                    canonical_people.c.last_name,
                    canonical_people.c.email,
                    governed_cohort_members.c.confirmed_active,
                )
                .select_from(
                    governed_cohort_members.join(
                        canonical_people,
                        governed_cohort_members.c.person_id
                        == canonical_people.c.person_id,
                    )
                )
                .where(governed_cohort_members.c.current == 1)
            ).mappings().all()
        governed_details = {
            str(row["canonical_key"]).strip().lower(): row
            for row in governed_rows
            if row["confirmed_active"]
        }
        governed = set(governed_details)
        cohort_snapshot = self.latest_snapshot("active_client_cohort")
        governed_services: dict[str, tuple[str, ...]] = {}
        accepted_candidate_snapshot = None
        accepted_observed_at = None
        if cohort_snapshot:
            accepted_candidate_snapshot = (
                cohort_snapshot["payload"].get("source_refs") or {}
            ).get("roster_candidate_snapshot")
            accepted_observed_at = cohort_snapshot["observed_at"]
            for row in cohort_snapshot["payload"].get("rows") or []:
                if not row.get("confirmed_active"):
                    continue
                governed_services[
                    str(row["canonical_key"]).strip().lower()
                ] = tuple(
                    sorted(
                        str(service.get("service") or "")
                        for service in (
                            (row.get("evidence") or {}).get(
                                "governed_roster"
                            )
                            or []
                        )
                    )
                )
        candidate_keys = set(candidate)
        added = candidate_keys - governed
        removed = governed - candidate_keys
        changed_services = {
            key
            for key in candidate_keys & governed
            if tuple(
                sorted(
                    str(service.get("service_type") or "")
                    for service in candidate[key].get("services") or []
                )
            )
            != governed_services.get(key, ())
        }
        relationships = sum(
            len(row["services"]) for row in candidate.values()
        )
        observed_at = datetime.fromisoformat(
            str(snapshot["observed_at"]).replace("Z", "+00:00")
        )
        if observed_at.tzinfo is None:
            observed_at = observed_at.replace(tzinfo=UTC)
        age_minutes = max(
            0,
            int((datetime.now(UTC) - observed_at).total_seconds() // 60),
        )
        accepted_current_candidate = (
            accepted_candidate_snapshot == snapshot["snapshot_id"]
        )

        def client_detail(
            key: str,
            *,
            candidate_row: dict[str, Any] | None = None,
        ) -> dict[str, Any]:
            """Return an exact-identity label for the authenticated dashboard."""
            governed_row = governed_details.get(key)
            first_name = str(
                (governed_row or {}).get("first_name") or ""
            ).strip()
            last_name = str(
                (governed_row or {}).get("last_name") or ""
            ).strip()
            name = " ".join(part for part in (first_name, last_name) if part)
            email = str(
                (governed_row or {}).get("email") or key
            ).strip() or None
            candidate_services = tuple(
                sorted(
                    str(service.get("service_type") or "")
                    for service in (candidate_row or {}).get("services") or []
                )
            )
            return {
                "client_name": name or email or key,
                "email": email,
                "accepted_services": list(governed_services.get(key, ())),
                "candidate_services": list(candidate_services),
            }

        return {
            "snapshot_id": snapshot["snapshot_id"],
            "observed_at": snapshot["observed_at"],
            "age_minutes": age_minutes,
            "as_of_date": payload["as_of_date"],
            "source_run_id": payload["source_run_id"],
            "candidate_active_clients": len(candidate_keys),
            "candidate_service_relationships": relationships,
            "accepted_active_clients": len(governed),
            "unchanged_clients": len(candidate_keys & governed),
            "added_since_accepted": len(added),
            "removed_since_accepted": len(removed),
            "changed_services_since_accepted": len(changed_services),
            "added_clients": [
                client_detail(key, candidate_row=candidate[key])
                for key in sorted(added)
            ],
            "removed_clients": [
                client_detail(key) for key in sorted(removed)
            ],
            "changed_service_clients": [
                client_detail(key, candidate_row=candidate[key])
                for key in sorted(changed_services)
            ],
            "accepted_candidate_snapshot": accepted_candidate_snapshot,
            "accepted_observed_at": accepted_observed_at,
            "accepted_current_candidate": accepted_current_candidate,
            "exact_match": (
                not added and not removed and not changed_services
            ),
        }

    def promote_roster_candidate(
        self,
        *,
        expected_snapshot_id: str,
    ) -> dict[str, Any]:
        candidate_snapshot = self.latest_snapshot("active_roster_candidate")
        existing_snapshot = self.latest_snapshot("active_client_cohort")
        membership_snapshot = self.latest_snapshot(
            "membership_reconciliation"
        )
        stripe_commercial_snapshot = self.latest_snapshot(
            "commercial_evidence_stripe"
        )
        pack_commercial_snapshot = self.latest_snapshot(
            "commercial_evidence_stripe_pack"
        )
        revenue_commercial_snapshot = self.latest_snapshot(
            "commercial_evidence_revenue_control"
        )
        if not all(
            (
                candidate_snapshot,
                existing_snapshot,
                membership_snapshot,
                stripe_commercial_snapshot,
            )
        ):
            raise ValueError(
                "candidate, governed cohort, membership and Stripe evidence "
                "must all be available"
            )
        if candidate_snapshot["snapshot_id"] != expected_snapshot_id:
            raise ValueError("roster candidate snapshot changed before promotion")

        candidate_payload = candidate_snapshot["payload"]
        existing_payload = existing_snapshot["payload"]
        candidate = {
            row["canonical_key"]: row
            for row in candidate_payload["rows"]
        }
        existing = {
            row["canonical_key"]: dict(row)
            for row in existing_payload["rows"]
        }
        accepted = {
            key
            for key, row in existing.items()
            if row["confirmed_active"]
        }
        removed = accepted - set(candidate)
        if removed:
            raise ValueError(
                "roster candidate removes accepted identities; owner review "
                "is required before promotion"
            )

        membership = {
            row["canonical_key"]: row
            for row in membership_snapshot["payload"]["rows"]
        }
        commercial: dict[str, set[str]] = {}
        for commercial_snapshot in (
            stripe_commercial_snapshot,
            pack_commercial_snapshot,
            revenue_commercial_snapshot,
        ):
            if not commercial_snapshot:
                continue
            for commercial_row in commercial_snapshot["payload"]["rows"]:
                confirmed = {
                    entitlement["service_type"]
                    for entitlement in commercial_row.get(
                        "entitlements"
                    ) or []
                    if entitlement["status"] == "confirmed"
                }
                commercial.setdefault(
                    commercial_row["canonical_key"], set()
                ).update(confirmed)
        required_entitlements = {
            "SGPT": {"sgpt", "fast_track"},
            "PT": {"personal_training"},
        }
        promoted = 0
        decision_required = 0
        for canonical_key, candidate_row in candidate.items():
            roster_services = [
                {
                    "service": service["service_type"],
                    "status": service["status"],
                    "classification": service.get("classification"),
                    "product": service.get("product"),
                    "assigned_trainer": service.get("assigned_trainer"),
                    "contracted_weekly_frequency": service.get(
                        "contracted_weekly_frequency"
                    ),
                    "service_duration": service.get("service_duration"),
                    "weekly_allocation": service.get("weekly_allocation"),
                    "allocation_currency": service.get(
                        "allocation_currency"
                    ),
                    "contract_length": service.get("contract_length"),
                    "effective_to": service.get("effective_to"),
                    "payment_marker": service.get("payment_marker"),
                    "allocation_basis": service.get("allocation_basis"),
                }
                for service in candidate_row["services"]
            ]
            row = existing.get(canonical_key)
            if row and row["confirmed_active"]:
                row = dict(row)
                row["evidence"] = {
                    **row["evidence"],
                    "governed_roster": roster_services,
                    "roster_candidate_snapshot": expected_snapshot_id,
                }
                existing[canonical_key] = row
                continue

            membership_row = membership.get(canonical_key) or {}
            confirmed_entitlements = commercial.get(canonical_key) or set()
            services_supported = all(
                bool(
                    required_entitlements[service["service_type"]]
                    & confirmed_entitlements
                )
                for service in candidate_row["services"]
            )
            qualifies = bool(
                membership_row.get("ghl_active")
                and membership_row.get("lifecycle_status") == "active"
                and services_supported
            )
            base = dict(row or {})
            base.update(
                {
                    "canonical_key": canonical_key,
                    "in_legacy_cohort": bool(
                        base.get("in_legacy_cohort")
                        or membership_row.get("ghl_active")
                        or membership_row.get("stripe_entitled")
                        or membership_row.get("trainerize_active")
                    ),
                    "active_signal": bool(
                        membership_row.get("ghl_active")
                        or membership_row.get("stripe_entitled")
                        or membership_row.get("trainerize_active")
                    ),
                    "confirmed_active": qualifies,
                    "paid_or_entitled": None,
                    "disposition": (
                        "confirmed_active"
                        if qualifies
                        else "decision_required"
                    ),
                    "primary_reason": (
                        "current_roster_with_authoritative_lifecycle_and_commercial_evidence"
                        if qualifies
                        else "roster_candidate_lacks_authoritative_lifecycle_or_commercial_evidence"
                    ),
                    "decision_required": not qualifies,
                    "owner": None if qualifies else "Peter Brown",
                    "owner_question": (
                        None
                        if qualifies
                        else (
                            "Should this roster identity be accepted through "
                            "approved non-Stripe evidence, corrected in GHL, "
                            "or removed from the active roster?"
                        )
                    ),
                    "evidence": {
                        **dict(base.get("evidence") or {}),
                        "ghl_active_signal": bool(
                            membership_row.get("ghl_active")
                        ),
                        "stripe_contract_signal": bool(
                            membership_row.get("stripe_entitled")
                        ),
                        "trainerize_access_signal": bool(
                            membership_row.get("trainerize_active")
                        ),
                        "confirmed_commercial_services": sorted(
                            confirmed_entitlements
                        ),
                        "governed_roster": roster_services,
                        "roster_candidate_snapshot": expected_snapshot_id,
                    },
                }
            )
            existing[canonical_key] = base
            promoted += int(qualifies)
            decision_required += int(not qualifies)

        payload = {
            "schema_version": 1,
            "source": "active_client_cohort",
            "observed_at": datetime.now(UTC).isoformat(timespec="seconds"),
            "as_of_date": candidate_payload["as_of_date"],
            "rule_version": "active-client-cohort-v2",
            "status": "complete",
            "complete": True,
            "source_refs": {
                "previous_governed_snapshot": existing_snapshot["snapshot_id"],
                "roster_candidate_snapshot": expected_snapshot_id,
                "membership_snapshot": membership_snapshot["snapshot_id"],
                "commercial_snapshot": stripe_commercial_snapshot[
                    "snapshot_id"
                ],
                "commercial_pack_snapshot": (
                    pack_commercial_snapshot["snapshot_id"]
                    if pack_commercial_snapshot
                    else None
                ),
            },
            "rows": [existing[key] for key in sorted(existing)],
        }
        from .contracts import validate_active_client_cohort

        result = self.accept_active_client_cohort(
            validate_active_client_cohort(payload)
        )
        return {
            **result,
            "promotion": {
                "promoted_additions": promoted,
                "candidate_decisions_required": decision_required,
                "removed_identities": 0,
            },
        }

    def _append_conversation_event(
        self,
        connection,
        *,
        case_id: str,
        idempotency_key: str,
        event_type: str,
        occurred_at: datetime,
        payload: dict[str, Any],
    ) -> bool:
        event_fingerprint = fingerprint(payload)
        existing = connection.execute(
            select(conversation_case_events.c.event_id).where(
                conversation_case_events.c.idempotency_key
                == idempotency_key
            )
        ).scalar()
        if existing:
            return False
        connection.execute(
            insert(conversation_case_events).values(
                event_id=stable_id("conversation_event", idempotency_key),
                case_id=case_id,
                idempotency_key=idempotency_key,
                event_type=event_type,
                occurred_at=occurred_at,
                event_fingerprint=event_fingerprint,
                payload_json=canonical_json(payload),
            )
        )
        return True

    def accept_conversation_clearance(
        self,
        payload: dict[str, Any],
        *,
        owner_role: str = "Admin Eve",
        owner_user_id: str | None = None,
    ) -> dict[str, Any]:
        snapshot_result = self.accept_snapshot(
            "conversation_clearance", payload
        )
        if payload.get("status") == "failed":
            return {
                **snapshot_result,
                "case_status": "source_failed",
                "cases_created": 0,
                "cases_updated": 0,
                "events_appended": 0,
            }
        observed_at = datetime.fromisoformat(
            str(payload["observed_at"]).replace("Z", "+00:00")
        ).astimezone(UTC)
        source_run_id = str(payload["source_run_id"])
        created = 0
        updated = 0
        ignored_older = 0
        events = 0
        reopened = 0
        with self.engine.begin() as connection:
            for observation in payload.get("rows") or []:
                contact_id = str(observation.get("contact_id") or "").strip()
                person_id = None
                if contact_id:
                    person_id = connection.execute(
                        select(source_identities.c.person_id).where(
                            source_identities.c.source == "ghl",
                            source_identities.c.source_record_id == contact_id,
                        )
                    ).scalar()
                case = build_case(
                    observation,
                    observed_at=observed_at,
                    owner_role=owner_role,
                    owner_user_id=owner_user_id,
                    person_id=str(person_id) if person_id else None,
                )
                observation_fingerprint = fingerprint(observation)
                existing = connection.execute(
                    select(conversation_cases).where(
                        conversation_cases.c.cycle_key == case["cycle_key"]
                    )
                ).mappings().first()
                existing_last_seen = (
                    existing["last_seen_at"] if existing else None
                )
                if (
                    existing_last_seen is not None
                    and existing_last_seen.tzinfo is None
                ):
                    existing_last_seen = existing_last_seen.replace(tzinfo=UTC)
                if existing and observed_at < existing_last_seen:
                    ignored_older += 1
                    continue
                if not existing:
                    prior_open = connection.execute(
                        select(conversation_cases).where(
                            conversation_cases.c.conversation_id
                            == case["conversation_id"],
                            conversation_cases.c.state.in_(
                                ("open", "due_soon", "overdue", "blocked")
                            ),
                        )
                    ).mappings().all()
                    for prior in prior_open:
                        connection.execute(
                            update(conversation_cases)
                            .where(
                                conversation_cases.c.case_id
                                == prior["case_id"]
                            )
                            .values(
                                state="reopened",
                                last_seen_at=observed_at,
                                resolution_code="new_inbound_cycle",
                                resolution_at=observed_at,
                            )
                        )
                        events += int(
                            self._append_conversation_event(
                                connection,
                                case_id=prior["case_id"],
                                idempotency_key=(
                                    f"{prior['case_id']}:reopened:"
                                    f"{case['cycle_key']}"
                                ),
                                event_type="reopened",
                                occurred_at=observed_at,
                                payload={
                                    "new_cycle_key": case["cycle_key"],
                                    "source_run_id": source_run_id,
                                },
                            )
                        )
                        reopened += 1
                    disposition = case.pop("disposition")
                    connection.execute(
                        insert(conversation_cases).values(
                            **case,
                            first_seen_at=observed_at,
                            last_seen_at=observed_at,
                            source_run_id=source_run_id,
                            source_fingerprint=observation_fingerprint,
                            disposition_json=canonical_json(disposition),
                        )
                    )
                    created += 1
                    events += int(
                        self._append_conversation_event(
                            connection,
                            case_id=case["case_id"],
                            idempotency_key=(
                                f"{case['case_id']}:observed:{source_run_id}"
                            ),
                            event_type="observed",
                            occurred_at=observed_at,
                            payload={
                                "source_run_id": source_run_id,
                                "source_fingerprint": observation_fingerprint,
                                "state": case["state"],
                                "category": case["category"],
                            },
                        )
                    )
                    continue
                next_state = case["state"]
                next_resolution_code = case["resolution_code"]
                next_resolution_at = case["resolution_at"]
                next_disposition = case["disposition"]
                if existing["state"] in {"resolved", "disposed", "delegated"}:
                    next_state = existing["state"]
                    next_resolution_code = existing["resolution_code"]
                    next_resolution_at = existing["resolution_at"]
                    next_disposition = json.loads(
                        existing["disposition_json"] or "{}"
                    )
                values = {
                    key: value
                    for key, value in case.items()
                    if key
                    not in {
                        "case_id",
                        "cycle_key",
                        "opened_at",
                        "disposition",
                    }
                }
                values.update(
                    last_seen_at=observed_at,
                    source_run_id=source_run_id,
                    source_fingerprint=observation_fingerprint,
                    state=next_state,
                    resolution_code=next_resolution_code,
                    resolution_at=next_resolution_at,
                    disposition_json=canonical_json(next_disposition),
                )
                connection.execute(
                    update(conversation_cases)
                    .where(conversation_cases.c.case_id == existing["case_id"])
                    .values(**values)
                )
                updated += 1
                events += int(
                    self._append_conversation_event(
                        connection,
                        case_id=existing["case_id"],
                        idempotency_key=(
                            f"{existing['case_id']}:observed:{source_run_id}"
                        ),
                        event_type=(
                            "resolved"
                            if next_state == "resolved"
                            and existing["state"] != "resolved"
                            else "observed"
                        ),
                        occurred_at=observed_at,
                        payload={
                            "source_run_id": source_run_id,
                            "source_fingerprint": observation_fingerprint,
                            "previous_state": existing["state"],
                            "state": next_state,
                            "category": case["category"],
                        },
                    )
                )
        return {
            **snapshot_result,
            "case_status": (
                "complete" if payload.get("complete") else "incomplete"
            ),
            "cases_created": created,
            "cases_updated": updated,
            "cases_reopened": reopened,
            "older_observations_ignored": ignored_older,
            "events_appended": events,
        }

    def conversation_clearance_cases(
        self,
        *,
        identified: bool,
        state: str | None = None,
        limit: int = 500,
    ) -> list[dict[str, Any]]:
        query = select(conversation_cases)
        if state:
            query = query.where(conversation_cases.c.state == state)
        query = query.order_by(
            conversation_cases.c.due_at.asc(),
            conversation_cases.c.opened_at.asc(),
        ).limit(max(1, min(int(limit), 2000)))
        with self.engine.begin() as connection:
            rows = connection.execute(query).mappings().all()
        result: list[dict[str, Any]] = []
        for source in rows:
            row = dict(source)
            row["breached"] = bool(row["breached"])
            row["disposition"] = json.loads(
                row.pop("disposition_json") or "{}"
            )
            for key, value in list(row.items()):
                if isinstance(value, datetime):
                    row[key] = value.astimezone(UTC).isoformat()
            if not identified:
                for key in (
                    "conversation_id",
                    "contact_id",
                    "person_id",
                    "latest_inbound_message_id",
                    "current_assignment",
                    "owner_user_id",
                    "excerpt",
                    "disposition",
                    "source_fingerprint",
                ):
                    row.pop(key, None)
            result.append(row)
        return result

    def conversation_clearance_events(
        self,
        *,
        case_id: str,
    ) -> list[dict[str, Any]]:
        with self.engine.begin() as connection:
            rows = connection.execute(
                select(conversation_case_events)
                .where(conversation_case_events.c.case_id == case_id)
                .order_by(conversation_case_events.c.occurred_at.asc())
            ).mappings().all()
        return [
            {
                **{
                    key: (
                        value.astimezone(UTC).isoformat()
                        if isinstance(value, datetime)
                        else value
                    )
                    for key, value in dict(row).items()
                    if key != "payload_json"
                },
                "payload": json.loads(row["payload_json"]),
            }
            for row in rows
        ]

    def conversation_clearance_queue(
        self,
        *,
        identified: bool,
        limit: int = 500,
    ) -> dict[str, Any]:
        cases = self.conversation_clearance_cases(
            identified=identified,
            limit=limit,
        )
        open_cases = [
            row
            for row in cases
            if row.get("state") in {"open", "due_soon", "overdue", "blocked"}
        ]
        for row in open_cases:
            row["carried_over"] = row.get("first_seen_at") != row.get(
                "last_seen_at"
            )
        queue_basis = [
            {
                key: row.get(key)
                for key in (
                    "case_id",
                    "cycle_key",
                    "latest_inbound_at",
                    "category",
                    "recommendation",
                    "due_at",
                    "state",
                    "carried_over",
                )
            }
            for row in open_cases
        ]
        return {
            "schema_version": 1,
            "mode": "single_inbox_exception_queue",
            "secondary_task_creation": "prohibited",
            "record_count": len(open_cases),
            "queue_fingerprint": fingerprint(queue_basis),
            "cases": open_cases,
        }

    def conversation_delivery_preview(
        self,
        *,
        channel: str,
        identified: bool,
    ) -> dict[str, Any]:
        queue = self.conversation_clearance_queue(identified=identified)
        with self.engine.begin() as connection:
            previous = connection.execute(
                select(conversation_delivery_state).where(
                    conversation_delivery_state.c.channel == channel
                )
            ).mappings().first()
        return {
            **queue,
            "channel": channel,
            "changed_since_delivery": (
                previous is None
                or previous["queue_fingerprint"]
                != queue["queue_fingerprint"]
            ),
            "last_delivered_at": (
                previous["delivered_at"].replace(tzinfo=UTC).isoformat()
                if previous
                and previous["delivered_at"].tzinfo is None
                else previous["delivered_at"].astimezone(UTC).isoformat()
                if previous
                else None
            ),
        }

    def acknowledge_conversation_delivery(
        self,
        *,
        channel: str,
        queue_fingerprint: str,
        delivered_at: datetime | None = None,
    ) -> dict[str, Any]:
        current = self.conversation_clearance_queue(identified=False)
        if queue_fingerprint != current["queue_fingerprint"]:
            raise ValueError("queue changed before delivery acknowledgement")
        timestamp = (delivered_at or datetime.now(UTC)).astimezone(UTC)
        values = {
            "channel": channel,
            "queue_fingerprint": queue_fingerprint,
            "delivered_at": timestamp,
            "payload_json": canonical_json(
                {
                    "record_count": current["record_count"],
                    "queue_fingerprint": queue_fingerprint,
                }
            ),
        }
        with self.engine.begin() as connection:
            existing = connection.execute(
                select(conversation_delivery_state.c.channel).where(
                    conversation_delivery_state.c.channel == channel
                )
            ).scalar()
            if existing:
                connection.execute(
                    update(conversation_delivery_state)
                    .where(conversation_delivery_state.c.channel == channel)
                    .values(**values)
                )
            else:
                connection.execute(
                    insert(conversation_delivery_state).values(**values)
                )
        return {
            "status": "acknowledged",
            "channel": channel,
            "queue_fingerprint": queue_fingerprint,
            "delivered_at": timestamp.isoformat(),
        }

    def conversation_clearance_summary(self) -> dict[str, Any]:
        cases = self.conversation_clearance_cases(
            identified=False,
            limit=2000,
        )
        summary = aggregate_cases(cases)
        with self.engine.begin() as connection:
            latest = connection.execute(
                select(source_snapshots)
                .where(source_snapshots.c.source == "conversation_clearance")
                .order_by(
                    source_snapshots.c.observed_at.desc(),
                    source_snapshots.c.accepted_at.desc(),
                )
                .limit(1)
            ).mappings().first()
        if not latest:
            extraction = {
                "status": "not_observed",
                "complete": False,
                "observed_at": None,
                "error_code": None,
            }
        else:
            payload = json.loads(latest["payload_json"])
            extraction = {
                "status": payload.get("status"),
                "complete": bool(payload.get("complete")),
                "observed_at": str(payload.get("observed_at")),
                "pages": payload.get("pages"),
                "expected_total": payload.get("expected_total"),
                "error_code": payload.get("error_code"),
            }
        return {**summary, "extraction": extraction}

    def canonical_counts(self) -> dict[str, int]:
        with self.engine.begin() as connection:
            lifecycle_rows = connection.execute(
                select(
                    lifecycle_states.c.status,
                    lifecycle_states.c.evidence_json,
                )
            ).mappings().all()
            active_signal_people = 0
            commercial_entitlement_signal_people = 0
            for lifecycle in lifecycle_rows:
                evidence = json.loads(lifecycle["evidence_json"])
                active_signal_people += int(
                    bool(
                        evidence.get("ghl_active")
                        or evidence.get("stripe_entitled")
                        or evidence.get("trainerize_active")
                    )
                )
                commercial_entitlement_signal_people += int(
                    bool(evidence.get("stripe_entitled"))
                )
            governed_rows = connection.execute(
                select(
                    governed_cohort_members.c.person_id,
                    governed_cohort_members.c.confirmed_active,
                    governed_cohort_members.c.decision_required,
                ).where(governed_cohort_members.c.current == 1)
            ).mappings().all()
            governed_confirmed = sum(
                bool(row["confirmed_active"]) for row in governed_rows
            )
            governed_decisions = sum(
                bool(row["decision_required"]) for row in governed_rows
            )
            lifecycle_active_people = int(
                connection.execute(
                    select(func.count())
                    .select_from(lifecycle_states)
                    .where(
                        lifecycle_states.c.status.in_(
                            ("active", "paused", "cancelling")
                        )
                    )
                ).scalar_one()
            )
            projected_active_relationship_rows = int(
                connection.execute(
                    select(func.count())
                    .select_from(service_relationships)
                    .where(
                        service_relationships.c.status.in_(
                            ("active", "paused", "cancelling")
                        )
                    )
                ).scalar_one()
            )
            governed_active_relationships = int(
                connection.execute(
                    select(func.count())
                    .select_from(service_relationships)
                    .where(
                        service_relationships.c.source
                        == "active_client_cohort",
                        service_relationships.c.status == "active",
                    )
                ).scalar_one()
            )
            return {
                "people": int(
                    connection.execute(
                        select(func.count()).select_from(canonical_people)
                    ).scalar_one()
                ),
                "active_people": int(
                    governed_confirmed
                    if governed_rows
                    else lifecycle_active_people
                ),
                "legacy_lifecycle_active_people": (
                    lifecycle_active_people
                ),
                "active_source_signal_people": active_signal_people,
                "commercial_entitlement_signal_people": (
                    commercial_entitlement_signal_people
                ),
                "authoritative_active_clients": (
                    governed_confirmed if governed_rows else 0
                ),
                "decision_required_people": (
                    governed_decisions
                    if governed_rows
                    else sum(
                        row["status"] == "review_required"
                        for row in lifecycle_rows
                    )
                ),
                "source_identities": int(
                    connection.execute(
                        select(func.count()).select_from(source_identities)
                    ).scalar_one()
                ),
                "service_relationships": int(
                    connection.execute(
                        select(func.count()).select_from(
                            service_relationships
                        )
                    ).scalar_one()
                ),
                "active_service_relationships": int(
                    governed_active_relationships
                    if governed_rows
                    else projected_active_relationship_rows
                ),
                "projected_active_service_relationship_rows": (
                    projected_active_relationship_rows
                ),
                "payment_accounts": int(
                    connection.execute(
                        select(func.count()).select_from(payment_accounts)
                    ).scalar_one()
                ),
                "payment_events": int(
                    connection.execute(
                        select(func.count()).select_from(payment_events)
                    ).scalar_one()
                ),
                "entitlements": int(
                    connection.execute(
                        select(func.count()).select_from(entitlements)
                    ).scalar_one()
                ),
                "lifecycle_states": int(
                    connection.execute(
                        select(func.count()).select_from(lifecycle_states)
                    ).scalar_one()
                ),
            }

    def latest_cohort_summary(self) -> dict[str, Any] | None:
        snapshot = self.latest_snapshot("active_client_cohort")
        if not snapshot:
            return None
        payload = snapshot["payload"]
        return {
            **summarise_cohort_rows(payload["rows"]),
            "snapshot_id": snapshot["snapshot_id"],
            "observed_at": snapshot["observed_at"],
            "as_of_date": payload["as_of_date"],
            "rule_version": payload["rule_version"],
            "source_refs": payload["source_refs"],
        }

    @staticmethod
    def _snapshot(row: Any) -> dict[str, Any]:
        return {
            "snapshot_id": row["snapshot_id"],
            "source": row["source"],
            "observed_at": row["observed_at"].isoformat(),
            "accepted_at": row["accepted_at"].isoformat(),
            "status": row["status"],
            "complete": bool(row["complete"]),
            "record_count": row["record_count"],
            "schema_version": row["schema_version"],
            "fingerprint": row["fingerprint"],
            "payload": json.loads(row["payload_json"]),
        }

    def start_job(self, job_id: str) -> str:
        run_id = (
            datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
            + "-"
            + uuid.uuid4().hex[:8]
        )
        with self.engine.begin() as connection:
            connection.execute(
                insert(job_runs).values(
                    run_id=run_id,
                    job_id=job_id,
                    started_at=datetime.now(UTC),
                    status="running",
                )
            )
        return run_id

    def close_interrupted_jobs(self) -> int:
        """Close runs left open when the Railway process was replaced."""
        now = datetime.now(UTC)
        with self.engine.begin() as connection:
            result = connection.execute(
                update(job_runs)
                .where(job_runs.c.status == "running")
                .values(
                    completed_at=now,
                    status="failed",
                    error=(
                        "Railway process ended before the job recorded "
                        "completion"
                    ),
                )
            )
        return int(result.rowcount or 0)

    def finish_job(
        self,
        run_id: str,
        *,
        status: str,
        summary: dict[str, Any] | None = None,
        error: str | None = None,
    ) -> None:
        with self.engine.begin() as connection:
            connection.execute(
                update(job_runs)
                .where(job_runs.c.run_id == run_id)
                .values(
                    completed_at=datetime.now(UTC),
                    status=status,
                    summary_json=(
                        canonical_json(summary) if summary is not None else None
                    ),
                    error=(error or "")[:2000] or None,
                )
            )

    def recent_jobs(self, limit: int = 25) -> list[dict[str, Any]]:
        with self.engine.begin() as connection:
            rows = connection.execute(
                select(job_runs)
                .order_by(job_runs.c.started_at.desc())
                .limit(limit)
            ).mappings().all()
        return [
            {
                "run_id": row["run_id"],
                "job_id": row["job_id"],
                "started_at": row["started_at"].isoformat(),
                "completed_at": (
                    row["completed_at"].isoformat()
                    if row["completed_at"]
                    else None
                ),
                "status": row["status"],
                "summary": (
                    json.loads(row["summary_json"])
                    if row["summary_json"]
                    else {}
                ),
                "error": row["error"],
            }
            for row in rows
        ]

    def accept_sa_attendance_snapshot(
        self,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        if not payload.get("complete"):
            raise ValueError(
                "partial Strength Assessment attendance runs are not accepted"
            )
        accepted = self.accept_snapshot(
            "strength_assessment_attendance",
            payload,
        )
        snapshot = self.latest_snapshot("strength_assessment_attendance")
        if not snapshot:
            raise RuntimeError("attendance snapshot was not persisted")
        inserted = 0
        with self.engine.begin() as connection:
            for row in payload.get("rows") or []:
                row_fingerprint = fingerprint(
                    {
                        "appointment_id": row["appointment_id"],
                        "booked_at": row.get("booked_at"),
                        "status": row["status"],
                        "start_at": row["start_at"],
                        "end_at": row["end_at"],
                        "assigned_user_id": row.get("assigned_user_id"),
                        "updated_at": row.get("updated_at"),
                        "deleted": row.get("deleted", False),
                    }
                )
                existing = connection.execute(
                    select(sa_appointment_observations.c.observation_id).where(
                        sa_appointment_observations.c.appointment_id
                        == row["appointment_id"],
                        sa_appointment_observations.c.observation_fingerprint
                        == row_fingerprint,
                    )
                ).first()
                if existing:
                    continue
                observation_id = self._stable_id(
                    "sa-appointment",
                    row["appointment_id"],
                    row_fingerprint,
                )
                connection.execute(
                    insert(sa_appointment_observations).values(
                        observation_id=observation_id,
                        appointment_id=row["appointment_id"],
                        contact_id=row["contact_id"],
                        calendar_id=row["calendar_id"],
                        booked_at=(
                            datetime.fromisoformat(row["booked_at"])
                            if row.get("booked_at")
                            else None
                        ),
                        start_at=datetime.fromisoformat(row["start_at"]),
                        end_at=datetime.fromisoformat(row["end_at"]),
                        status=row["status"],
                        assigned_user_id=row.get("assigned_user_id"),
                        source_updated_at=(
                            datetime.fromisoformat(row["updated_at"])
                            if row.get("updated_at")
                            else None
                        ),
                        deleted=int(bool(row.get("deleted"))),
                        observed_at=datetime.fromisoformat(
                            row["observed_at"]
                        ),
                        source_run_id=payload["source_run_id"],
                        source_snapshot_id=snapshot["snapshot_id"],
                        observation_fingerprint=row_fingerprint,
                    )
                )
                inserted += 1
        return {
            **accepted,
            "observations_inserted": inserted,
            "source_snapshot_id": snapshot["snapshot_id"],
        }

    def accept_sa_feedback(
        self,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        with self.engine.begin() as connection:
            existing = connection.execute(
                select(sa_feedback_evidence.c.evidence_id).where(
                    sa_feedback_evidence.c.delivery_key
                    == payload["delivery_key"]
                )
            ).first()
            if existing:
                return {
                    "status": "duplicate",
                    "evidence_id": existing[0],
                }
            evidence_id = self._stable_id(
                "sa-feedback",
                payload["delivery_key"],
            )
            connection.execute(
                insert(sa_feedback_evidence).values(
                    evidence_id=evidence_id,
                    delivery_key=payload["delivery_key"],
                    form_submission_id=payload["form_submission_id"],
                    contact_id=payload["contact_id"],
                    submitted_at=datetime.fromisoformat(
                        payload["submitted_at"]
                    ),
                    sales_outcome=payload.get("sales_outcome"),
                    delivered_by=payload["delivered_by"],
                    workflow_execution_id=payload.get(
                        "workflow_execution_id"
                    ),
                    accepted_at=datetime.now(UTC),
                    payload_json=canonical_json(payload),
                )
            )
        return {"status": "accepted", "evidence_id": evidence_id}

    def latest_sa_events(self) -> list[dict[str, Any]]:
        with self.engine.begin() as connection:
            rows = connection.execute(
                select(sa_appointment_observations).order_by(
                    sa_appointment_observations.c.observed_at.desc(),
                    sa_appointment_observations.c.observation_id.desc(),
                )
            ).mappings().all()
        latest: dict[str, Any] = {}
        for row in rows:
            latest.setdefault(row["appointment_id"], row)
        def timestamp(value: datetime | None) -> str | None:
            if value is None:
                return None
            if value.tzinfo is None:
                value = value.replace(tzinfo=UTC)
            return value.isoformat()

        return [
            {
                "appointment_id": row["appointment_id"],
                "contact_id": row["contact_id"],
                "calendar_id": row["calendar_id"],
                "booked_at": timestamp(row["booked_at"]),
                "start_at": timestamp(row["start_at"]),
                "end_at": timestamp(row["end_at"]),
                "status": row["status"],
                "assigned_user_id": row["assigned_user_id"],
                "updated_at": (
                    timestamp(row["source_updated_at"])
                ),
                "deleted": bool(row["deleted"]),
                "observed_at": timestamp(row["observed_at"]),
                "source_run_id": row["source_run_id"],
            }
            for row in latest.values()
        ]

    def sa_feedback_rows(self) -> list[dict[str, Any]]:
        with self.engine.begin() as connection:
            rows = connection.execute(
                select(sa_feedback_evidence).order_by(
                    sa_feedback_evidence.c.submitted_at
                )
            ).mappings().all()
        def timestamp(value: datetime) -> str:
            if value.tzinfo is None:
                value = value.replace(tzinfo=UTC)
            return value.isoformat()

        return [
            {
                "evidence_id": row["evidence_id"],
                "delivery_key": row["delivery_key"],
                "form_submission_id": row["form_submission_id"],
                "contact_id": row["contact_id"],
                "submitted_at": timestamp(row["submitted_at"]),
                "sales_outcome": row["sales_outcome"],
                "delivered_by": row["delivered_by"],
                "workflow_execution_id": row["workflow_execution_id"],
            }
            for row in rows
        ]

    def record_sa_reconciliation(
        self,
        rows: list[dict[str, Any]],
        exception_rows: list[dict[str, Any]],
    ) -> dict[str, int]:
        inserted = 0
        now = datetime.now(UTC)
        open_keys: set[str] = set()
        with self.engine.begin() as connection:
            for row in rows:
                material = {
                    "canonical_status": row["canonical_status"],
                    "reconciliation_state": row["reconciliation_state"],
                    "proposed_status": row.get("proposed_status"),
                    "feedback_submission_ids": row.get(
                        "feedback_submission_ids"
                    )
                    or [],
                    "rule_version": row["rule_version"],
                }
                decision_fingerprint = fingerprint(material)
                existing = connection.execute(
                    select(sa_reconciliation_decisions.c.decision_id).where(
                        sa_reconciliation_decisions.c.appointment_id
                        == row["appointment_id"],
                        sa_reconciliation_decisions.c.decision_fingerprint
                        == decision_fingerprint,
                    )
                ).first()
                if not existing:
                    try:
                        with connection.begin_nested():
                            connection.execute(
                                insert(sa_reconciliation_decisions).values(
                                    decision_id=self._stable_id(
                                        "sa-decision",
                                        row["appointment_id"],
                                        decision_fingerprint,
                                    ),
                                    appointment_id=row["appointment_id"],
                                    contact_id=row["contact_id"],
                                    canonical_status=row[
                                        "canonical_status"
                                    ],
                                    reconciliation_state=row[
                                        "reconciliation_state"
                                    ],
                                    proposed_status=row.get(
                                        "proposed_status"
                                    ),
                                    rule_version=row["rule_version"],
                                    decided_at=now,
                                    decision_fingerprint=(
                                        decision_fingerprint
                                    ),
                                    evidence_json=canonical_json(material),
                                )
                            )
                        inserted += 1
                    except IntegrityError:
                        # Scheduled and manual refreshes can reconcile the
                        # same appointment concurrently. The stable decision
                        # ID makes that write safely idempotent.
                        pass
            for item in exception_rows:
                target = (
                    item.get("appointment_id")
                    or item.get("form_submission_id")
                    or item["contact_id"]
                )
                exception_id = self._stable_id(
                    "sa-attendance",
                    target,
                    item["code"],
                )
                open_keys.add(exception_id)
                existing = connection.execute(
                    select(exceptions.c.exception_id).where(
                        exceptions.c.exception_id == exception_id
                    )
                ).first()
                values = {
                    "domain": "strength_assessment_attendance",
                    "code": item["code"],
                    "severity": item["severity"],
                    "owner": item.get("owner") or "Admin Eve",
                    "status": "open",
                    "evidence_json": canonical_json(item),
                    "updated_at": now,
                }
                if existing:
                    connection.execute(
                        update(exceptions)
                        .where(exceptions.c.exception_id == exception_id)
                        .values(**values)
                    )
                else:
                    connection.execute(
                        insert(exceptions).values(
                            exception_id=exception_id,
                            created_at=now,
                            **values,
                        )
                    )
            current = connection.execute(
                select(exceptions.c.exception_id).where(
                    exceptions.c.domain
                    == "strength_assessment_attendance",
                    exceptions.c.status == "open",
                )
            ).all()
            for (exception_id,) in current:
                if exception_id not in open_keys:
                    connection.execute(
                        update(exceptions)
                        .where(exceptions.c.exception_id == exception_id)
                        .values(status="resolved", updated_at=now)
                    )
        return {
            "decisions_inserted": inserted,
            "open_exceptions": len(open_keys),
        }

    def sa_attendance_decisions(self) -> list[dict[str, Any]]:
        with self.engine.begin() as connection:
            rows = connection.execute(
                select(sa_reconciliation_decisions).order_by(
                    sa_reconciliation_decisions.c.decided_at.desc()
                )
            ).mappings().all()
        latest: dict[str, Any] = {}
        for row in rows:
            latest.setdefault(row["appointment_id"], row)
        return [
            {
                "appointment_id": row["appointment_id"],
                "contact_id": row["contact_id"],
                "canonical_status": row["canonical_status"],
                "reconciliation_state": row["reconciliation_state"],
                "proposed_status": row["proposed_status"],
                "rule_version": row["rule_version"],
                "decided_at": row["decided_at"].isoformat(),
                "evidence": json.loads(row["evidence_json"]),
            }
            for row in latest.values()
        ]

    def sa_attendance_exceptions(
        self,
        *,
        identified: bool,
    ) -> list[dict[str, Any]]:
        with self.engine.begin() as connection:
            rows = connection.execute(
                select(exceptions).where(
                    exceptions.c.domain
                    == "strength_assessment_attendance",
                    exceptions.c.status == "open",
                )
                .order_by(exceptions.c.severity.desc())
            ).mappings().all()
        result = []
        for row in rows:
            evidence = json.loads(row["evidence_json"])
            item = {
                "exception_id": row["exception_id"],
                "code": row["code"],
                "severity": row["severity"],
                "owner": row["owner"],
                "status": row["status"],
                "updated_at": row["updated_at"].isoformat(),
            }
            if identified:
                item["evidence"] = evidence
            result.append(item)
        return result

    def _append_sa_prequalification_event(
        self,
        connection,
        *,
        appointment_id: str,
        event_type: str,
        idempotency_key: str,
        occurred_at: datetime,
        payload: dict[str, Any],
        actor: str | None = None,
    ) -> bool:
        existing = connection.execute(
            select(sa_prequalification_events.c.event_id).where(
                sa_prequalification_events.c.idempotency_key
                == idempotency_key
            )
        ).scalar()
        if existing:
            return False
        connection.execute(
            insert(sa_prequalification_events).values(
                event_id=stable_id("sa_prequal_event", idempotency_key),
                appointment_id=appointment_id,
                event_type=event_type,
                idempotency_key=idempotency_key,
                occurred_at=occurred_at,
                actor=actor,
                event_fingerprint=fingerprint(payload),
                payload_json=canonical_json(payload),
            )
        )
        return True

    def accept_sa_prequalification_observation(
        self,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        snapshot = self.accept_snapshot(
            "strength_assessment_prequalification", payload
        )
        if payload.get("status") == "failed":
            return {
                **snapshot,
                "case_status": "source_failed",
                "cases_created": 0,
                "cases_updated": 0,
                "events_appended": 0,
            }
        observed_at = datetime.fromisoformat(
            str(payload["observed_at"]).replace("Z", "+00:00")
        ).astimezone(UTC)
        source_run_id = str(payload["source_run_id"])
        created = 0
        updated = 0
        events = 0
        with self.engine.begin() as connection:
            for row in payload.get("rows") or []:
                appointment_id = str(row["appointment_id"])
                row_fingerprint = fingerprint(row)
                existing = connection.execute(
                    select(sa_prequalification_cases).where(
                        sa_prequalification_cases.c.appointment_id
                        == appointment_id
                    )
                ).mappings().first()
                values = {
                    "contact_id": row["contact_id"],
                    "conversation_id": row.get("conversation_id"),
                    "contact_name": row.get("contact_name"),
                    "scheduled_at": datetime.fromisoformat(
                        str(row["scheduled_at"]).replace("Z", "+00:00")
                    ).astimezone(UTC),
                    "appointment_status": row["appointment_status"],
                    "case_state": row["case_state"],
                    "first_incomplete_stage": row.get(
                        "first_incomplete_stage"
                    ),
                    "next_action": row.get("next_action"),
                    "blocked_reasons_json": canonical_json(
                        row.get("blocked_reasons") or []
                    ),
                    "conversation_complete": int(
                        bool(row.get("conversation_complete"))
                    ),
                    "conversation_fingerprint": row.get(
                        "conversation_fingerprint"
                    ),
                    "latest_message_id": row.get("latest_message_id"),
                    "latest_message_at": (
                        datetime.fromisoformat(
                            str(row["latest_message_at"]).replace(
                                "Z", "+00:00"
                            )
                        ).astimezone(UTC)
                        if row.get("latest_message_at")
                        else None
                    ),
                    "stages_json": canonical_json(row["stages"]),
                    "facts_json": canonical_json(row.get("facts") or {}),
                    "draft_json": (
                        canonical_json(row["draft"])
                        if row.get("draft") is not None
                        else None
                    ),
                    "review_context_json": canonical_json(
                        row.get("review_context") or {}
                    ),
                    "privacy_evidence_json": canonical_json(
                        row.get("privacy_evidence") or {}
                    ),
                    "rule_version": row["rule_version"],
                    "model_version": row.get("model_version"),
                    "prompt_version": row.get("prompt_version"),
                    "source_run_id": source_run_id,
                    "source_fingerprint": row_fingerprint,
                    "last_seen_at": observed_at,
                }
                if existing is None:
                    connection.execute(
                        insert(sa_prequalification_cases).values(
                            appointment_id=appointment_id,
                            first_seen_at=observed_at,
                            **values,
                        )
                    )
                    created += 1
                    event_type = "case_observed"
                else:
                    connection.execute(
                        update(sa_prequalification_cases)
                        .where(
                            sa_prequalification_cases.c.appointment_id
                            == appointment_id
                        )
                        .values(**values)
                    )
                    updated += 1
                    event_type = (
                        "case_changed"
                        if existing["source_fingerprint"] != row_fingerprint
                        else "case_reobserved"
                    )
                events += int(
                    self._append_sa_prequalification_event(
                        connection,
                        appointment_id=appointment_id,
                        event_type=event_type,
                        idempotency_key=(
                            f"{appointment_id}:{event_type}:{source_run_id}"
                        ),
                        occurred_at=observed_at,
                        payload={
                            "source_run_id": source_run_id,
                            "source_fingerprint": row_fingerprint,
                            "case_state": row["case_state"],
                            "first_incomplete_stage": row.get(
                                "first_incomplete_stage"
                            ),
                            "draft_id": (row.get("draft") or {}).get(
                                "draft_id"
                            ),
                        },
                    )
                )
        return {
            **snapshot,
            "case_status": "complete" if payload.get("complete") else "partial",
            "cases_created": created,
            "cases_updated": updated,
            "events_appended": events,
        }

    def sa_prequalification_case_rows(
        self,
        *,
        appointment_id: str | None = None,
        limit: int = 500,
    ) -> list[dict[str, Any]]:
        query = select(sa_prequalification_cases)
        if appointment_id:
            query = query.where(
                sa_prequalification_cases.c.appointment_id
                == appointment_id
            )
        query = query.order_by(
            sa_prequalification_cases.c.scheduled_at.asc()
        ).limit(max(1, min(int(limit), 2000)))
        with self.engine.begin() as connection:
            rows = connection.execute(query).mappings().all()
        result = []
        for source in rows:
            row = dict(source)
            for key in (
                "blocked_reasons_json",
                "stages_json",
                "facts_json",
                "draft_json",
                "review_context_json",
                "privacy_evidence_json",
            ):
                value = row.pop(key)
                row[key.removesuffix("_json")] = (
                    json.loads(value) if value else None
                )
            row["conversation_complete"] = bool(row["conversation_complete"])
            for key, value in list(row.items()):
                if isinstance(value, datetime):
                    row[key] = value.astimezone(UTC).isoformat()
            result.append(row)
        return result

    def accept_sa_prequalification_review(
        self,
        review: dict[str, Any],
    ) -> dict[str, Any]:
        appointment_id = review["appointment_id"]
        with self.engine.begin() as connection:
            case = connection.execute(
                select(sa_prequalification_cases).where(
                    sa_prequalification_cases.c.appointment_id
                    == appointment_id
                )
            ).mappings().first()
            if case is None:
                raise ValueError("pre-qualification case was not found")
            draft = json.loads(case["draft_json"] or "{}")
            if str(draft.get("draft_id") or "") != review["draft_id"]:
                raise ValueError("review draft is stale or unknown")
            idempotency_key = (
                f"{appointment_id}:review:{review['draft_id']}:"
                f"{review['reviewer']}:{review['action']}"
            )
            inserted = self._append_sa_prequalification_event(
                connection,
                appointment_id=appointment_id,
                event_type="draft_reviewed",
                idempotency_key=idempotency_key,
                occurred_at=datetime.fromisoformat(
                    review["reviewed_at"].replace("Z", "+00:00")
                ).astimezone(UTC),
                actor=review["reviewer"],
                payload=review,
            )
        return {
            "status": "accepted" if inserted else "duplicate",
            "appointment_id": appointment_id,
            "draft_id": review["draft_id"],
            "send_authorised": False,
        }

    def claim_sa_prequalification_send(self, claim: dict[str, Any]) -> dict[str, Any]:
        now = datetime.fromisoformat(claim["claimed_at"].replace("Z", "+00:00")).astimezone(UTC)
        appointment_id = claim["appointment_id"]
        send_key = claim["send_key"]
        with self.engine.begin() as connection:
            case = connection.execute(
                select(sa_prequalification_cases).where(
                    sa_prequalification_cases.c.appointment_id == appointment_id
                )
            ).mappings().first()
            if case is None:
                raise ValueError("pre-qualification case was not found")
            draft = json.loads(case["draft_json"] or "{}")
            checks = {
                "draft_id": str(draft.get("draft_id") or "") == claim["draft_id"],
                "conversation_fingerprint": case["conversation_fingerprint"] == claim["conversation_fingerprint"],
                "latest_message_id": case["latest_message_id"] == claim["latest_message_id"],
                "scheduled_at": case["scheduled_at"].astimezone(UTC).isoformat() == claim["scheduled_at"],
                "appointment_status": case["appointment_status"] == "confirmed",
                "future": case["scheduled_at"].astimezone(UTC) > now,
                "rule_version": case["rule_version"] == claim["rule_version"],
            }
            if not all(checks.values()):
                raise ValueError("send claim is stale or appointment is no longer eligible")
            existing = connection.execute(
                select(sa_prequalification_send_locks).where(
                    sa_prequalification_send_locks.c.send_key == send_key
                )
            ).mappings().first()
            if existing:
                return {"status": existing["status"], "send_key": send_key, "duplicate": True}
            connection.execute(insert(sa_prequalification_send_locks).values(
                send_key=send_key,
                appointment_id=appointment_id,
                draft_id=claim["draft_id"],
                reviewer=claim["reviewer"],
                wording_hash=claim["wording_hash"],
                conversation_fingerprint=claim["conversation_fingerprint"],
                status="claimed",
                claimed_at=now,
                payload_json=canonical_json({**claim, "checks": checks}),
            ))
            self._append_sa_prequalification_event(
                connection,
                appointment_id=appointment_id,
                event_type="send_claimed",
                idempotency_key=f"{send_key}:claimed",
                occurred_at=now,
                actor=claim["reviewer"],
                payload={**claim, "checks": checks},
            )
        return {"status": "claimed", "send_key": send_key, "duplicate": False}

    def complete_sa_prequalification_send(self, result: dict[str, Any]) -> dict[str, Any]:
        now = datetime.fromisoformat(result["completed_at"].replace("Z", "+00:00")).astimezone(UTC)
        with self.engine.begin() as connection:
            lock = connection.execute(
                select(sa_prequalification_send_locks).where(
                    sa_prequalification_send_locks.c.send_key == result["send_key"]
                )
            ).mappings().first()
            if lock is None:
                raise ValueError("send lock was not found")
            if lock["status"] == "sent":
                return {"status": "sent", "send_key": result["send_key"], "duplicate": True}
            status = "sent" if result.get("ghl_message_id") else "failed"
            connection.execute(
                update(sa_prequalification_send_locks)
                .where(sa_prequalification_send_locks.c.send_key == result["send_key"])
                .values(
                    status=status,
                    completed_at=now,
                    ghl_message_id=result.get("ghl_message_id"),
                    failure_code=result.get("failure_code"),
                    payload_json=canonical_json(result),
                )
            )
            self._append_sa_prequalification_event(
                connection,
                appointment_id=lock["appointment_id"],
                event_type="message_sent" if status == "sent" else "send_failed",
                idempotency_key=f"{result['send_key']}:{status}",
                occurred_at=now,
                actor=lock["reviewer"],
                payload=result,
            )
        return {"status": status, "send_key": result["send_key"], "duplicate": False}

    def sa_prequalification_events_for_case(
        self,
        appointment_id: str,
    ) -> list[dict[str, Any]]:
        with self.engine.begin() as connection:
            rows = connection.execute(
                select(sa_prequalification_events)
                .where(
                    sa_prequalification_events.c.appointment_id
                    == appointment_id
                )
                .order_by(sa_prequalification_events.c.occurred_at.asc())
            ).mappings().all()
        return [
            {
                **{
                    key: (
                        value.astimezone(UTC).isoformat()
                        if isinstance(value, datetime)
                        else value
                    )
                    for key, value in dict(row).items()
                    if key != "payload_json"
                },
                "payload": json.loads(row["payload_json"]),
            }
            for row in rows
        ]

    def sa_prequalification_delivery_preview(
        self,
        *,
        delivery_key: str,
        queue_fingerprint: str,
    ) -> dict[str, Any]:
        with self.engine.begin() as connection:
            row = connection.execute(
                select(sa_prequalification_delivery_state).where(
                    sa_prequalification_delivery_state.c.delivery_key
                    == delivery_key
                )
            ).mappings().first()
        return {
            "delivery_key": delivery_key,
            "queue_fingerprint": queue_fingerprint,
            "changed_since_delivery": (
                row is None or row["queue_fingerprint"] != queue_fingerprint
            ),
            "last_delivered_at": (
                row["delivered_at"].astimezone(UTC).isoformat()
                if row is not None
                else None
            ),
        }

    def acknowledge_sa_prequalification_delivery(
        self,
        *,
        delivery_key: str,
        queue_fingerprint: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        now = datetime.now(UTC)
        with self.engine.begin() as connection:
            existing = connection.execute(
                select(sa_prequalification_delivery_state.c.delivery_key).where(
                    sa_prequalification_delivery_state.c.delivery_key
                    == delivery_key
                )
            ).scalar()
            values = {
                "queue_fingerprint": queue_fingerprint,
                "delivered_at": now,
                "payload_json": canonical_json(payload),
            }
            if existing:
                connection.execute(
                    update(sa_prequalification_delivery_state)
                    .where(
                        sa_prequalification_delivery_state.c.delivery_key
                        == delivery_key
                    )
                    .values(**values)
                )
            else:
                connection.execute(
                    insert(sa_prequalification_delivery_state).values(
                        delivery_key=delivery_key,
                        **values,
                    )
                )
        return {
            "status": "acknowledged",
            "delivery_key": delivery_key,
            "queue_fingerprint": queue_fingerprint,
            "delivered_at": now.isoformat(),
        }

    def open_exception_counts(self) -> dict[str, int]:
        with self.engine.begin() as connection:
            rows = connection.execute(
                select(exceptions.c.severity, func.count())
                .where(exceptions.c.status == "open")
                .group_by(exceptions.c.severity)
            ).all()
        return {str(severity): int(count) for severity, count in rows}
