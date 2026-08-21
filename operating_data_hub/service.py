from __future__ import annotations

import logging
from datetime import UTC, datetime, time, timedelta
from decimal import Decimal
from typing import Any

import requests

from .acceptance_controller import MetricAcceptanceController
from .cash_adapter import (
    StripeCashReader,
    build_pt_minder_cash_batch,
    build_stripe_cash_batch,
)
from .config import BRISBANE_TZ, Settings
from .contracts import validate_summary
from .current_people import build_current_people_contract
from .delivery_reporting import sgpt_delivery_preview
from .evolved_standards import (
    DEFINITION_VERSION as EVOLVED_STANDARDS_DEFINITION_VERSION,
    build_evolved_standards_projection,
)
from .ghl_reporting_v2 import (
    GHLAcquisitionReader,
    build_ghl_acquisition_snapshot,
)
from .kpi_adapter import collect_kpi_snapshot
from .membership_lifecycle import MembershipLifecycleRepository
from .onboarding_followup import (
    build_onboarding_followup_plan,
    execute_onboarding_followup_plan,
)
from .onboarding_activation import build_onboarding_activation_evidence
from .reporting_v2 import ReportingV2Repository, completed_reporting_periods
from .reporting_v2_board_pack import board_pack_contract
from .sa_attendance import (
    GHLAttendanceClient,
    parse_datetime,
    reconcile_attendance,
)
from .sa_attendance_followup import (
    build_followup_plan,
    execute_followup_plan,
)
from .sa_attendance_sheet import (
    SAAttendanceSheetPublisher,
    build_sheets_service,
)
from .sa_listed_history import build_listed_history
from .store import HubStore
from .trainerize_attendance import (
    TrainerizeAttendanceClient,
    attach_evidence,
    corroborate_attendance,
)
from .xero_adapter import (
    XeroClient,
    XeroConnectionStore,
    profit_and_loss_expense_breakdown,
)
from .website_analytics import (
    GA4WebsiteReader,
    build_website_marketing_snapshot,
    normalise_subscriber_submission,
    subscriber_assessment_booking_periods,
)
from .workflow_extensions import (
    plan_workflow_extension,
    workflow_policy_registry,
)


SOURCE_MAX_AGE_HOURS: dict[str, int | None] = {
    "google_kpi": 14,
    "retention_intelligence": 14,
    "pt_booking_continuity": 192,
    "pt_roster_self_mending": 26,
    "revenue_control": 96,
    "conversation_triage": 14,
    "strength_assessment_prequalification": 26,
    "trainerize_performance": 14,
    "pt_minder": 192,
    "membership_reconciliation": 14,
    "active_client_cohort": 14,
    "active_roster_candidate": 14,
    "commercial_evidence_stripe": 14,
    "commercial_evidence_stripe_pack": 192,
    "commercial_evidence_pt_minder": 192,
    "commercial_evidence_governed_manual": 192,
    "commercial_evidence_revenue_control": 96,
    "strength_assessment_attendance": 14,
    "ghl_acquisition_v2": 14,
    "sa_listed_history": 14,
    "xero_accounting": 26,
    "website_analytics_v2": 14,
    # Owner-approved classification rules are governed configuration, not a
    # periodically observed operational feed. Their effective dates determine
    # whether they apply, so elapsed wall-clock time must not make them stale.
    "payment_service_overrides": None,
}

log = logging.getLogger(__name__)


class HubService:
    def __init__(self, settings: Settings, store: HubStore | None = None):
        self.settings = settings
        self.store = store or HubStore(settings.database_url)
        self.store.close_interrupted_jobs()
        self.reporting_v2 = ReportingV2Repository(self.store.engine)
        self.membership_lifecycle = MembershipLifecycleRepository(
            self.store.engine,
            self.reporting_v2,
        )
        self.metric_acceptance = MetricAcceptanceController(
            self.store.engine
        )

    def xero_client(self) -> XeroClient:
        return XeroClient(
            client_id=self.settings.xero_client_id,
            client_secret=self.settings.xero_client_secret,
            redirect_uri=self.settings.xero_redirect_uri,
            tenant_name=self.settings.xero_tenant_name,
            store=XeroConnectionStore(
                self.store.engine,
                self.settings.xero_token_encryption_key,
            ),
        )

    def workflow_extension_policies(self) -> dict[str, Any]:
        return workflow_policy_registry()

    def workflow_extension_outbox(
        self,
        *,
        workflow_key: str | None = None,
        person_id: str | None = None,
        limit: int = 250,
    ) -> dict[str, Any]:
        records = self.store.workflow_extension_records(
            workflow_key=workflow_key,
            person_id=person_id,
            limit=limit,
        )
        return {
            "contract": workflow_policy_registry(),
            "records": records,
            "counts": {
                state: sum(row["state"] == state for row in records)
                for state in (
                    "preview",
                    "suppressed",
                    "rejected",
                    "duplicate",
                    "cooldown",
                    "queued",
                    "dispatched",
                )
            },
        }

    def accept_workflow_extension_decision(
        self,
        payload: dict[str, Any],
        *,
        persist: bool,
    ) -> dict[str, Any]:
        subject = dict(payload.get("subject") or {})
        prior = self.store.workflow_extension_records(
            workflow_key=str(payload.get("workflow_key") or "") or None,
            person_id=str(subject.get("person_id") or "") or None,
            limit=250,
        )
        plan = plan_workflow_extension(
            payload,
            prior_records=prior,
            now=datetime.now(UTC),
        )
        persistence = (
            self.store.record_workflow_extension(plan)
            if persist
            else {
                "status": "preview_only",
                "idempotency_key": plan["outbox"]["idempotency_key"],
                "state": plan["outbox"]["state"],
            }
        )
        return {
            "mode": "recorded" if persist else "preview",
            "publication_impact": "none",
            "source_writes": "none",
            "client_messages": "none",
            "plan": plan,
            "persistence": persistence,
        }

    def xero_status(self) -> dict[str, Any]:
        if not self.settings.xero_token_encryption_key:
            return {
                "connected": False,
                "configured": False,
                "mode": "read_only",
            }
        status = XeroConnectionStore(
            self.store.engine,
            self.settings.xero_token_encryption_key,
        ).status()
        return {
            **status,
            "configured": bool(
                self.settings.xero_client_id
                and self.settings.xero_client_secret
                and self.settings.xero_redirect_uri
            ),
        }

    def refresh_xero_accounting(self) -> dict[str, Any]:
        observed_at = datetime.now(UTC)
        reporting_periods = completed_reporting_periods(observed_at)
        snapshot = self.xero_client().accounting_snapshot(
            from_date=(observed_at - timedelta(days=365)).date(),
            to_date=observed_at.date(),
            profit_and_loss_periods=reporting_periods,
        )
        result = self.store.accept_snapshot("xero_accounting", snapshot)
        return {
            "mode": "shadow",
            "publication_impact": "none",
            "source": "xero_accounting",
            "snapshot": result,
            "summary": snapshot["summary"],
        }

    def refresh_website_analytics(self) -> dict[str, Any]:
        if (
            not self.settings.ghl_api_key
            or not self.settings.ghl_location_id
        ):
            raise RuntimeError(
                "GHL_API_KEY and GHL_LOCATION_ID are required"
            )
        observed_at = datetime.now(UTC)
        ghl_reader = GHLAcquisitionReader(
            self.settings.ghl_api_key,
            self.settings.ghl_location_id,
        )
        raw_submissions = ghl_reader.form_submissions(
            self.settings.ghl_subscriber_form_id,
            datetime.combine(
                self.settings.website_analytics_started_on,
                time.min,
                tzinfo=BRISBANE_TZ,
            ).astimezone(UTC),
            observed_at,
        )
        subscriber_submissions = [
            normalise_subscriber_submission(
                row,
                form_id=self.settings.ghl_subscriber_form_id,
            )
            for row in raw_submissions
            if row.get("id") and row.get("contactId")
        ]
        snapshot_payload = build_website_marketing_snapshot(
            reader=GA4WebsiteReader(
                self.settings.google_service_account_json or "",
                self.settings.ga4_property_id,
            ),
            subscriber_submissions=subscriber_submissions,
            analytics_started_on=(
                self.settings.website_analytics_started_on
            ),
            observed_at=observed_at,
        )
        snapshot = self.store.accept_snapshot(
            "website_analytics_v2",
            snapshot_payload,
        )
        accepted_events = 0
        for row in subscriber_submissions:
            result = self.reporting_v2.accept_source_event(
                {
                    "source_system": "ghl",
                    "source_object_type": "website_subscription",
                    "source_event_id": row["source_event_id"],
                    "source_object_id": row["source_object_id"],
                    "occurred_at": row["submitted_at"],
                    "observed_at": observed_at.isoformat(),
                    "source_snapshot_id": snapshot["snapshot_id"],
                    "confidence": "verified",
                    "payload": row,
                }
            )
            accepted_events += result["status"] == "accepted"
        return {
            "status": "complete",
            "mode": "shadow",
            "source": "website_analytics_v2",
            "source_snapshot_id": snapshot["snapshot_id"],
            "summary": snapshot_payload["summary"],
            "periods": snapshot_payload["periods"],
            "subscriber_events_accepted": accepted_events,
            "publication_impact": "none",
        }

    def run_job(self, job_id: str, function):
        run_id = self.store.start_job(job_id)
        try:
            result = function()
            self.store.finish_job(
                run_id, status="complete", summary=result
            )
            return result
        except Exception as exc:
            self.store.finish_job(
                run_id, status="failed", error=str(exc)
            )
            raise

    def refresh_kpi(self) -> dict[str, Any]:
        payload = collect_kpi_snapshot()
        return self.store.accept_snapshot("google_kpi", payload)

    def _trainerize_attendance_precheck(
        self,
        plan: dict[str, Any],
        identities: dict[str, dict[str, Any]],
        *,
        kind: str,
    ) -> dict[str, Any]:
        candidates: dict[str, dict[str, Any]] = {}
        for action in plan.get("actions") or []:
            appointment_id = str(
                action.get("appointment_id") or ""
            ).strip()
            if not appointment_id or appointment_id in candidates:
                continue
            scheduled = (
                action.get("scheduled_start")
                or action.get("start_at")
            )
            target_date = (
                parse_datetime(scheduled, "scheduled_start")
                .astimezone(BRISBANE_TZ)
                .date()
                .isoformat()
            )
            candidates[appointment_id] = {
                "appointment_id": appointment_id,
                "contact_id": str(action.get("contact_id") or ""),
                "target_date": target_date,
                "kind": kind,
            }
        if not candidates:
            return attach_evidence(
                plan,
                {
                    "source_status": "not_required",
                    "results": [],
                    "counts": {
                        "requested": 0,
                        "verified_showed": 0,
                        "unresolved": 0,
                    },
                },
            )
        if not self.settings.trainerize_attendance_enabled:
            return attach_evidence(
                plan,
                {
                    "source_status": "disabled",
                    "results": [],
                    "counts": {
                        "requested": len(candidates),
                        "verified_showed": 0,
                        "unresolved": len(candidates),
                    },
                },
            )
        try:
            if (
                not self.settings.trainerize_group_id
                or not self.settings.trainerize_api_token
                or self.settings.trainerize_location_id is None
            ):
                raise RuntimeError(
                    "Trainerize attendance credentials are incomplete"
                )
            evidence = corroborate_attendance(
                TrainerizeAttendanceClient(
                    self.settings.trainerize_group_id,
                    self.settings.trainerize_api_token,
                    self.settings.trainerize_location_id,
                ),
                candidates.values(),
                identities,
            )
        except Exception:
            log.exception("Trainerize attendance pre-check failed")
            evidence = {
                "source_status": "unavailable",
                "results": [],
                "counts": {
                    "requested": len(candidates),
                    "verified_showed": 0,
                    "unresolved": len(candidates),
                },
            }
        return attach_evidence(plan, evidence)

    def refresh_sa_attendance(self) -> dict[str, Any]:
        if not self.settings.ghl_api_key or not self.settings.ghl_location_id:
            raise RuntimeError(
                "GHL_API_KEY and GHL_LOCATION_ID are required for "
                "Strength Assessment attendance collection"
            )
        if not self.settings.sa_calendar_ids:
            raise RuntimeError("SA_ATTENDANCE_CALENDAR_IDS cannot be empty")
        now = datetime.now(UTC)
        client = GHLAttendanceClient(
            self.settings.ghl_api_key,
            self.settings.ghl_location_id,
            write_enabled=self.settings.sa_ghl_write_enabled,
        )
        raw = client.list_events(
            self.settings.sa_calendar_ids,
            now
            - timedelta(days=self.settings.sa_collection_lookback_days),
            now + timedelta(days=14),
        )
        from .contracts import validate_sa_attendance, validate_sa_feedback

        payload = validate_sa_attendance(raw)
        accepted = self.store.accept_sa_attendance_snapshot(payload)
        feedback_accepted = 0
        feedback_duplicate = 0
        feedback_rows = client.list_form_submissions(
            self.settings.sa_feedback_form_id,
            now
            - timedelta(days=self.settings.sa_collection_lookback_days),
            now,
            sales_outcome_field_id=(
                self.settings.sa_feedback_sales_outcome_field_id
            ),
        )
        for feedback in feedback_rows:
            result = self.store.accept_sa_feedback(
                validate_sa_feedback(feedback)
            )
            if result["status"] == "accepted":
                feedback_accepted += 1
            else:
                feedback_duplicate += 1
        reconciliation = self.reconcile_sa_attendance(now=now)
        sheet_publication = None
        if self.settings.sa_sheets_write_enabled:
            sheet_publication = self.publish_sa_attendance_sheet(
                reconciliation["rows"]
            )
        return {
            **accepted,
            "summary": reconciliation["summary"],
            "feedback_collection": {
                "read": len(feedback_rows),
                "accepted": feedback_accepted,
                "duplicate": feedback_duplicate,
            },
            "sheet_publication": sheet_publication,
        }

    def sa_attendance_followup(
        self,
        *,
        now: datetime | None = None,
        execute: bool = False,
    ) -> dict[str, Any]:
        observed_at = (now or datetime.now(UTC)).astimezone(UTC)
        reconciliation = self.reconcile_sa_attendance(now=observed_at)
        plan = build_followup_plan(
            reconciliation["rows"],
            now=observed_at,
            admin_user_id=self.settings.sa_task_admin_user_id,
            lookback_days=self.settings.sa_task_followup_lookback_days,
        )
        if execute and not self.settings.sa_task_write_enabled:
            raise RuntimeError("SA attendance task writes are disabled")
        client = GHLAttendanceClient(
            self.settings.ghl_api_key,
            self.settings.ghl_location_id,
            write_enabled=self.settings.sa_task_write_enabled,
        )
        contact_ids = {
            str(row.get("contact_id") or "")
            for row in plan.get("actions") or []
            if row.get("contact_id")
        }
        identities = {}
        for contact_id in contact_ids:
            try:
                identities[contact_id] = client.get_contact(contact_id)
            except Exception:
                log.exception(
                    "GHL contact identity lookup failed for Trainerize "
                    "attendance pre-check"
                )
                identities[contact_id] = {}
        plan = self._trainerize_attendance_precheck(
            plan,
            identities,
            kind="strength_assessment",
        )
        result = execute_followup_plan(
            client,
            plan,
            write_enabled=execute and self.settings.sa_task_write_enabled,
        )
        return {
            "definition_version": "sa-attendance-followup-v1",
            "writes_enabled": self.settings.sa_task_write_enabled,
            "plan": plan,
            "result": result,
        }

    def publish_sa_attendance_sheet(
        self,
        rows: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        if not self.settings.sa_sheets_write_enabled:
            raise RuntimeError("SA Attendance Sheet writes are disabled")
        if self.settings.sa_sheet_tab_id is None:
            raise RuntimeError("SA_ATTENDANCE_SHEET_TAB_ID is required")
        if rows is None:
            rows = self.reconcile_sa_attendance()["rows"]
        publisher = SAAttendanceSheetPublisher(
            build_sheets_service(
                self.settings.google_service_account_json
            ),
            self.settings.google_spreadsheet_id,
            sheet_name=self.settings.sa_sheet_tab_name,
            sheet_id=self.settings.sa_sheet_tab_id,
            write_enabled=True,
        )
        return publisher.publish(rows)

    def reconcile_sa_attendance(
        self,
        *,
        now: datetime | None = None,
    ) -> dict[str, Any]:
        result = reconcile_attendance(
            self.store.latest_sa_events(),
            self.store.sa_feedback_rows(),
            now=now,
            grace_period=timedelta(
                minutes=self.settings.sa_grace_minutes
            ),
            matching_window=timedelta(
                days=self.settings.sa_feedback_matching_days
            ),
            legacy_showed_before=datetime.combine(
                self.settings.sa_legacy_attendance_cutoff,
                time.min,
                tzinfo=BRISBANE_TZ,
            ),
        )
        persistence = self.store.record_sa_reconciliation(
            result["rows"],
            result["exceptions"],
        )
        snapshot = self.store.latest_snapshot(
            "strength_assessment_attendance"
        )
        try:
            reporting_v2 = self.reporting_v2.record_sa_attendance_shadow(
                result["rows"],
                result["summary"],
                source_snapshot_id=(
                    snapshot["snapshot_id"] if snapshot else None
                ),
            )
        except Exception as exc:
            log.exception(
                "Reporting V2 attendance shadow projection failed"
            )
            reporting_v2 = {
                "status": "failed",
                "error": str(exc),
                "publication_impact": "none",
            }
        return {
            **result,
            "persistence": persistence,
            "reporting_v2_shadow": reporting_v2,
        }

    def ingest_sa_feedback(
        self,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        accepted = self.store.accept_sa_feedback(payload)
        reconciliation = self.reconcile_sa_attendance()
        return {
            **accepted,
            "reconciliation": {
                "summary": reconciliation["summary"],
                "persistence": reconciliation["persistence"],
            },
        }

    def sa_attendance_state(self, *, identified: bool = False) -> dict[str, Any]:
        result = self.reconcile_sa_attendance()
        snapshot = self.store.latest_snapshot(
            "strength_assessment_attendance"
        )
        source = None
        if snapshot:
            source = {
                key: value
                for key, value in snapshot.items()
                if key != "payload"
            }
        state = {
            "definition_version": result["summary"]["definition_version"],
            "summary": result["summary"],
            "source": source,
            "exceptions": self.store.sa_attendance_exceptions(
                identified=identified
            ),
            "writes": {
                "ghl_enabled": self.settings.sa_ghl_write_enabled,
                "tasks_enabled": self.settings.sa_task_write_enabled,
                "sheets_enabled": self.settings.sa_sheets_write_enabled,
            },
        }
        if identified:
            state["rows"] = result["rows"]
        return state

    def reporting_v2_state(self) -> dict[str, Any]:
        return self.reporting_v2.status()

    def reporting_v2_definitions(self) -> list[dict[str, Any]]:
        return self.reporting_v2.definitions()

    def reporting_v2_cutover_status(
        self,
        period_id: str = "week",
    ) -> dict[str, Any]:
        scorecard = self.reporting_v2_ceo_scorecard(period_id)
        return {
            **scorecard["cutover"],
            "period": scorecard["period"],
            "publication_write_available": True,
            "owner_authority_required": "Peter Brown",
        }

    def decide_reporting_v2_publication(
        self,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        period_id = str(payload.get("period") or "week")
        cutover = self.reporting_v2_cutover_status(period_id)
        metric_id = str(payload.get("metric_id") or "").strip()
        definition_version = str(
            payload.get("definition_version") or ""
        ).strip()
        metric = next(
            (
                row
                for row in cutover["metrics"]
                if row["metric_id"] == metric_id
                and row["definition_version"] == definition_version
            ),
            None,
        )
        if metric is None:
            raise ValueError(
                "metric and definition version are not on the cutover matrix"
            )
        acceptance_record = next(
            (
                row
                for row in self.metric_acceptance.latest(metric_id)
                if row["definition_version"] == definition_version
            ),
            None,
        )
        confidence = (
            "high"
            if metric["cutover"]["gates"]["confidence"]["passed"]
            else "unresolved"
        )
        observation = {
            "value": metric.get("value"),
            "unit": metric.get("unit"),
            "confidence": confidence,
            "unavailable_reason": (
                metric["cutover"]["gates"]["observation"].get("reason")
            ),
        }
        decision_payload = {
            **payload,
            "legacy_fallback_available": metric["cutover"][
                "legacy_fallback_available"
            ],
        }
        return self.reporting_v2.decide_metric_publication(
            decision_payload,
            acceptance_record=acceptance_record,
            observation=observation,
        )

    def reporting_v2_board_pack_contract(self) -> dict[str, Any]:
        return board_pack_contract()

    def accept_membership_snapshot(
        self,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        accepted = self.store.accept_membership_snapshot(payload)
        lifecycle = self.membership_lifecycle.record_membership_snapshot(
            payload,
            source_snapshot_id=accepted["snapshot_id"],
        )
        return {
            **accepted,
            "membership_lifecycle_shadow": lifecycle,
        }

    def reporting_v2_membership_lifecycle(
        self,
        period_id: str,
    ) -> dict[str, Any]:
        return self.membership_lifecycle.preview(period_id)

    def reporting_v2_membership_lifecycle_backfill(
        self,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        return self.membership_lifecycle.record_historical_backfill(payload)

    def reporting_v2_current_people(
        self,
        period_id: str,
    ) -> dict[str, Any]:
        periods = completed_reporting_periods()
        if period_id not in periods:
            raise ValueError("period must be week, 28d or 90d")
        period_start, period_end = periods[period_id]
        required_sources = (
            "membership_reconciliation",
            "active_client_cohort",
            "commercial_evidence_stripe",
            "pt_minder",
        )
        snapshots = {
            row["source"]: row for row in self.store.latest_snapshots()
        }
        now = datetime.now(UTC)
        freshness = []
        for source in required_sources:
            snapshot = snapshots.get(source)
            maximum = SOURCE_MAX_AGE_HOURS.get(source, 26)
            if not snapshot:
                freshness.append(
                    {
                        "source": source,
                        "freshness": "missing",
                        "observed_at": None,
                        "source_snapshot_id": None,
                        "age_hours": None,
                        "max_age_hours": maximum,
                    }
                )
                continue
            observed_at = datetime.fromisoformat(
                snapshot["observed_at"].replace("Z", "+00:00")
            )
            if observed_at.tzinfo is None:
                observed_at = observed_at.replace(tzinfo=UTC)
            age = max(0, (now - observed_at).total_seconds() / 3600)
            freshness.append(
                {
                    "source": source,
                    "freshness": (
                        "fresh"
                        if maximum is None or age <= maximum
                        else "stale"
                    ),
                    "observed_at": snapshot["observed_at"],
                    "source_snapshot_id": snapshot["snapshot_id"],
                    "age_hours": round(age, 1),
                    "max_age_hours": maximum,
                }
            )
        return build_current_people_contract(
            self.store.engine,
            period={
                "id": period_id,
                "start": period_start.isoformat(),
                "end": period_end.isoformat(),
                "timezone": "Australia/Brisbane",
                "as_of": period_end.isoformat(),
            },
            source_freshness=freshness,
            as_of=now,
        )

    def reporting_v2_acquisition_preview(self) -> dict[str, Any]:
        snapshot = self.store.latest_snapshot("ghl_acquisition_v2") or {}
        reporting = self.reporting_v2.status()
        metric_ids = {
            "leads_created",
            "sa_bookings_unique",
            "prequalification_completion_rate",
            "assessment_conversion_unique",
            "onboarding_booking_speed_days",
            "onboarding_completion_speed_days",
        }
        return {
            "mode": "shadow",
            "publication_impact": "none",
            "observed_at": snapshot.get("observed_at"),
            "source_summary": (
                (snapshot.get("payload") or {}).get("summary") or {}
            ),
            "onboarding_completion_followup": (
                (snapshot.get("payload") or {})
                .get("completion_followup", {})
                .get("counts", {})
            ),
            "period_metrics": [
                row
                for row in reporting["latest_metric_observations"]
                if row["metric_id"] in metric_ids
            ],
        }

    def reporting_v2_ceo_scorecard(
        self, period_id: str
    ) -> dict[str, Any]:
        acceptance_records = {
            (row["metric_id"], row["definition_version"]): row
            for row in self.metric_acceptance.latest()
        }
        scorecard = self.reporting_v2.ceo_scorecard_preview(
            period_id,
            acceptance_records=acceptance_records,
        )
        acquisition = self.store.latest_snapshot("ghl_acquisition_v2") or {}
        acquisition_payload = acquisition.get("payload") or {}
        website_snapshot = (
            self.store.latest_snapshot("website_analytics_v2") or {}
        )
        website_payload = website_snapshot.get("payload") or {}
        scorecard["website_marketing"] = (
            (website_payload.get("periods") or {}).get(period_id)
            or {
                "period_start": scorecard["period"]["start"],
                "period_end": scorecard["period"]["end"],
                "analytics_started_on": (
                    self.settings.website_analytics_started_on.isoformat()
                ),
                "coverage_complete": False,
                "coverage_state": "collecting",
                "page_views": None,
                "visitors": None,
                "sessions": None,
                "new_subscribers": None,
                "visitor_to_subscriber_rate": None,
                "unavailable_reason": (
                    "The first accepted website analytics refresh has not "
                    "completed."
                ),
            }
        )
        scorecard["subscriber_booking"] = (
            (
                (acquisition_payload.get("subscriber_booking") or {}).get(
                    "periods"
                )
                or {}
            ).get(period_id)
            or {
                "period_start": scorecard["period"]["start"],
                "period_end": scorecard["period"]["end"],
                "new_subscribers": None,
                "subscribers_booking_assessment": None,
                "subscriber_to_assessment_rate": None,
                "open_booking_window": None,
                "booking_window_days": 30,
            }
        )
        scorecard["week_ahead"] = (
            acquisition_payload.get("week_ahead")
            or {
                "definition_version": "upcoming-sa-readiness-v1",
                "booked": None,
                "prequalified": None,
                "awaiting_prequalification": None,
                "prequalification_rate": None,
                "appointments": [],
                "unavailable_reason": (
                    "The next accepted GHL acquisition refresh will populate "
                    "the week-ahead assessment view."
                ),
            }
        )
        scorecard[
            "projected_income"
        ] = self.store.recurring_income_projection_preview()
        xero_snapshot = self.store.latest_snapshot("xero_accounting") or {}
        xero_payload = xero_snapshot.get("payload") or {}
        xero_period = (
            (xero_payload.get("profit_and_loss") or {}).get(period_id)
            or {}
        )
        xero_summary = xero_period.get("summary") or {}
        xero_expense_breakdown = xero_period.get("expense_breakdown") or (
            profit_and_loss_expense_breakdown(
                xero_period.get("report") or {}
            )
            if xero_period.get("report")
            else {}
        )
        expenses_amount = xero_summary.get("total_expenses")
        scorecard["expenses"] = {
            "available": bool(
                xero_summary.get("complete")
                and expenses_amount is not None
            ),
            "definition_version": "operating-expenses-v2",
            "amount": expenses_amount,
            "confidence": (
                "high"
                if xero_summary.get("complete")
                and expenses_amount is not None
                else "unresolved"
            ),
            "source": "Xero Profit and Loss",
            "accounting_basis": "accrual",
            "transfers_excluded": True,
            "period_start": xero_period.get("period_start"),
            "period_end": xero_period.get("period_end"),
            "top_categories": xero_expense_breakdown.get(
                "categories", []
            ),
            "other_amount": xero_expense_breakdown.get("other_amount"),
            "category_count": xero_expense_breakdown.get(
                "category_count", 0
            ),
            "unavailable_reason": (
                None
                if xero_summary.get("complete")
                and expenses_amount is not None
                else (
                    "The next accepted Xero refresh will populate expenses "
                    "for this completed period."
                )
            ),
        }
        period_cash = self.reporting_v2.cash_period_summary(
            scorecard["period"]["start"],
            scorecard["period"]["end"],
        )
        income_amount = xero_summary.get("income")
        comparison_available = bool(
            xero_summary.get("complete")
            and income_amount is not None
            and period_cash["available"]
        )
        cash_amount = (
            Decimal(period_cash["net_cash_ex_gst_cents"]) / Decimal(100)
            if period_cash["available"]
            else None
        )
        income_decimal = (
            Decimal(str(income_amount))
            if income_amount is not None
            else None
        )
        difference_amount = (
            cash_amount - income_decimal
            if comparison_available
            and cash_amount is not None
            and income_decimal is not None
            else None
        )
        difference_ratio = (
            abs(difference_amount) / abs(cash_amount)
            if difference_amount is not None
            and cash_amount is not None
            and cash_amount != 0
            else None
        )
        close_status = (
            "review_required"
            if difference_ratio is not None
            and difference_ratio >= Decimal("0.10")
            else (
                "directionally_aligned"
                if difference_ratio is not None
                else "unavailable"
            )
        )
        scorecard["accounting_validation"] = {
            "available": comparison_available,
            "definition_version": "cash-accounting-validation-v1",
            "confidence": "medium" if comparison_available else "unresolved",
            "cash_collected_ex_gst": (
                format(cash_amount, "f") if cash_amount is not None else None
            ),
            "xero_income_ex_gst": income_amount,
            "difference": (
                format(difference_amount, "f")
                if difference_amount is not None
                else None
            ),
            "difference_percent_of_cash": (
                format(difference_ratio * Decimal("100"), ".1f")
                if difference_ratio is not None
                else None
            ),
            "cash_event_count": period_cash["event_count"],
            "classification": close_status,
            "publication_impact": "none",
            "explanation": (
                "Actual cash comes from completed member payments. Xero "
                "income is what has currently been coded into the accounts. "
                "The difference is work for the bookkeeping close; it does "
                "not reduce collected cash or change the cash goal."
            ),
            "blocked_reasons": period_cash["blocked_reasons"],
        }
        performance = (
            self.store.latest_snapshot("trainerize_performance") or {}
        )
        summary = (performance.get("payload") or {}).get("summary") or {}
        identity_context = self.store.sgpt_delivery_identity_context()
        trainerize_to_person = identity_context[
            "trainerize_to_person_id"
        ]
        sgpt_events = []
        identity_unmatched_events = 0
        for source_event in summary.get("sgptBookingEvents") or []:
            event = dict(source_event)
            trainerize_user_id = str(
                event.get("trainerize_user_id") or ""
            ).strip()
            person_id = trainerize_to_person.get(trainerize_user_id)
            if person_id:
                event["person_id"] = person_id
            else:
                identity_unmatched_events += 1
            sgpt_events.append(event)
        scorecard["sgpt_delivery"] = sgpt_delivery_preview(
            sgpt_events,
            period_start=scorecard["period"]["start"],
            period_end=scorecard["period"]["end"],
            today=datetime.now(BRISBANE_TZ).date(),
            active_sgpt_member_ids=identity_context[
                "active_member_ids"
            ],
            identity_unmatched_events=identity_unmatched_events,
            source={
                "snapshot_id": performance.get("snapshot_id"),
                "run_id": summary.get("runId"),
                "observed_at": performance.get("observed_at"),
                "complete": performance.get("complete"),
                "status": performance.get("status"),
            },
        )
        scorecard["evolved_standards"] = (
            build_evolved_standards_projection(
                trainerize_snapshot=performance,
                membership_snapshot=self.store.latest_snapshot(
                    "membership_reconciliation"
                ),
                acquisition_snapshot=acquisition,
                as_of_date=datetime.now(BRISBANE_TZ).date(),
                acceptance_record=acceptance_records.get(
                    (
                        "evolved_standards",
                        EVOLVED_STANDARDS_DEFINITION_VERSION,
                    )
                ),
            )
        )
        lifecycle = self.membership_lifecycle.preview(period_id)
        scorecard["membership_lifecycle"] = lifecycle
        scorecard["attrition_legacy_marker"] = self.store.attrition_preview(
            period_start=datetime.fromisoformat(
                scorecard["period"]["start"]
            ).date(),
            period_end=datetime.fromisoformat(
                scorecard["period"]["end"]
            ).date(),
        )
        scorecard["attrition"] = {
            "members_lost": lifecycle["final_membership_endings"],
            "pt_downgrades": lifecycle["downgrade_only_transitions"],
            "coverage_note": (
                "A verified opening active-member cohort is required before "
                "the attrition rate can be accepted."
                if lifecycle["attrition_rate"] is None
                else (
                    "The period rate is calculated from the exact opening "
                    "active-member cohort and final membership endings."
                )
            ),
            "contract_version": lifecycle["contract_version"],
            "complete": lifecycle["complete"],
            "blocked_reasons": lifecycle["blocked_reasons"],
        }
        definitions = {
            (row["metric_id"], row["definition_version"]): row
            for row in self.reporting_v2.definitions()
        }

        def cutover_entry(
            metric_id: str,
            definition_version: str,
            observation: dict[str, Any] | None,
            *,
            legacy_fallback_available: bool,
        ) -> dict[str, Any]:
            status = self.reporting_v2.metric_cutover_status(
                metric_id=metric_id,
                definition_version=definition_version,
                observation=observation,
                acceptance_record=acceptance_records.get(
                    (metric_id, definition_version)
                ),
                legacy_fallback_available=legacy_fallback_available,
            )
            definition = definitions.get(
                (metric_id, definition_version), {}
            )
            return {
                "metric_id": metric_id,
                "definition_version": definition_version,
                "plain_english_name": definition.get(
                    "plain_english_name", metric_id
                ),
                "value": (
                    observation.get("value")
                    if observation is not None
                    else None
                ),
                "unit": (
                    observation.get("unit")
                    if observation is not None
                    else None
                ),
                "cutover": status,
                "effective_publication_state": status["effective_state"],
            }

        website = scorecard["website_marketing"]
        website_confidence = (
            "high" if website.get("coverage_complete") else "unresolved"
        )
        extra_cutover = [
            cutover_entry(
                "website_visitors",
                "website-marketing-v1",
                {
                    "value": website.get("visitors"),
                    "unit": "count",
                    "confidence": website_confidence,
                    "unavailable_reason": website.get(
                        "unavailable_reason"
                    ),
                },
                legacy_fallback_available=False,
            ),
            cutover_entry(
                "website_subscribers_unique",
                "website-marketing-v1",
                {
                    "value": website.get("new_subscribers"),
                    "unit": "count",
                    "confidence": website_confidence,
                    "unavailable_reason": website.get(
                        "unavailable_reason"
                    ),
                },
                legacy_fallback_available=True,
            ),
            cutover_entry(
                "visitor_to_subscriber_rate",
                "website-marketing-v1",
                {
                    "value": website.get("visitor_to_subscriber_rate"),
                    "unit": "ratio",
                    "confidence": website_confidence,
                    "unavailable_reason": website.get(
                        "unavailable_reason"
                    ),
                },
                legacy_fallback_available=False,
            ),
            cutover_entry(
                "cash_goal_progress",
                "cash-goal-v1",
                scorecard["cash_goal"].get("observation"),
                legacy_fallback_available=True,
            ),
            cutover_entry(
                "operating_expenses",
                "operating-expenses-v2",
                {
                    "value": scorecard["expenses"].get("amount"),
                    "unit": "AUD",
                    "confidence": scorecard["expenses"].get(
                        "confidence", "unresolved"
                    ),
                    "unavailable_reason": scorecard["expenses"].get(
                        "unavailable_reason"
                    ),
                },
                legacy_fallback_available=False,
            ),
            cutover_entry(
                "cash_accounting_validation",
                "cash-accounting-validation-v1",
                {
                    "value": scorecard["accounting_validation"].get(
                        "difference"
                    ),
                    "unit": "AUD",
                    "confidence": (
                        "high"
                        if scorecard["accounting_validation"].get(
                            "available"
                        )
                        else "unresolved"
                    ),
                    "unavailable_reason": (
                        "Complete cash and Xero observations are required."
                    ),
                },
                legacy_fallback_available=False,
            ),
            cutover_entry(
                "sgpt_delivery",
                "sgpt-delivery-v1",
                {
                    "value": (
                        1
                        if scorecard["sgpt_delivery"].get("available")
                        else None
                    ),
                    "unit": "contract",
                    "confidence": (
                        "high"
                        if scorecard["sgpt_delivery"].get("available")
                        else "unresolved"
                    ),
                    "unavailable_reason": scorecard[
                        "sgpt_delivery"
                    ].get("unavailable_reason"),
                },
                legacy_fallback_available=True,
            ),
            cutover_entry(
                "evolved_standards",
                "evolved-standards-v1-shadow",
                {
                    "value": (
                        1
                        if scorecard["evolved_standards"].get("status")
                        == "available"
                        else None
                    ),
                    "unit": "component_evidence_contract",
                    "confidence": (
                        "high"
                        if scorecard["evolved_standards"].get("status")
                        == "available"
                        else "unresolved"
                    ),
                    "unavailable_reason": scorecard[
                        "evolved_standards"
                    ].get("reason"),
                },
                legacy_fallback_available=False,
            ),
        ]
        for metric_id, definition_version in (
            (
                "consumer_retention_intelligence_contract",
                "retention-hub-read-v1",
            ),
            (
                "consumer_conversation_triage_contract",
                "conversation-triage-hub-read-v1",
            ),
            (
                "consumer_pt_booking_continuity_contract",
                "pt-booking-hub-read-v1",
            ),
            (
                "consumer_revenue_control_contract",
                "revenue-control-hub-read-v1",
            ),
        ):
            comparison = self.reporting_v2.latest_parallel_result(
                metric_id,
                definition_version,
            )
            clean = bool(
                comparison
                and comparison["acceptance_state"]
                in {"passed", "accepted_for_cutover"}
                and comparison["unexplained_event_count"] == 0
                and comparison["unexplained_cents"] == 0
            )
            extra_cutover.append(
                cutover_entry(
                    metric_id,
                    definition_version,
                    {
                        "value": (
                            comparison.get("v2_value")
                            if comparison
                            else None
                        ),
                        "unit": "classifications",
                        "confidence": "high" if clean else "unresolved",
                        "unavailable_reason": (
                            None
                            if comparison
                            else (
                                "No scheduled Hub-versus-legacy comparison "
                                "has been recorded."
                            )
                        ),
                    },
                    legacy_fallback_available=True,
                )
            )
        scorecard["cutover"] = {
            "mode": "metric_by_metric",
            "kpi_workbook_cutover_authorised": False,
            "legacy_dashboard_available": True,
            "metrics": [
                {
                    "metric_id": row["metric_id"],
                    "definition_version": row["definition_version"],
                    "plain_english_name": row["plain_english_name"],
                    "value": row["value"],
                    "unit": row["unit"],
                    "cutover": row["cutover"],
                    "effective_publication_state": row[
                        "effective_publication_state"
                    ],
                }
                for row in scorecard["metrics"]
            ]
            + extra_cutover,
        }
        scorecard["cutover"]["accepted_metric_count"] = sum(
            row["effective_publication_state"] == "v2_accepted"
            for row in scorecard["cutover"]["metrics"]
        )
        return scorecard

    def reporting_v2_sgpt_delivery(
        self,
        *,
        period: str = "week",
        identified: bool = False,
    ) -> dict[str, Any]:
        scorecard = self.reporting_v2_ceo_scorecard(period)
        result = dict(scorecard["sgpt_delivery"])
        if not identified or not result.get("available"):
            return result
        context = self.store.sgpt_delivery_identity_context()
        members = context["active_members"]
        for period_key in ("selected_period", "current_week"):
            period_result = dict(result[period_key])
            for field in (
                "active_members_with_no_booking",
                "active_members_with_no_attendance",
            ):
                period_result[field] = [
                    members[person_id]
                    for person_id in (period_result.get(field) or [])
                    if person_id in members
                ]
            result[period_key] = period_result
        return result

    def record_reporting_v2_parallel_result(
        self,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        return self.reporting_v2.record_parallel_result(
            metric_id=payload.get("metric_id"),
            definition_version=payload.get("definition_version"),
            period_start=payload.get("period_start"),
            period_end=payload.get("period_end"),
            legacy_value=payload.get("legacy_value"),
            v2_value=payload.get("v2_value"),
            variance_classification=payload.get(
                "variance_classification"
            ),
            unexplained_event_count=payload.get(
                "unexplained_event_count", 0
            ),
            unexplained_cents=payload.get("unexplained_cents", 0),
            evidence=payload.get("evidence") or {},
            request_cutover_acceptance=False,
        )

    def submit_reporting_v2_cash_batch(
        self,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        return self.reporting_v2.record_cash_batch_shadow(payload)

    def refresh_reporting_v2_cash(self) -> dict[str, Any]:
        if not self.settings.stripe_restricted_key:
            raise RuntimeError("STRIPE_RESTRICTED_KEY is required")
        observed_at = datetime.now(UTC)
        backfill_days = self.settings.reporting_v2_cash_lookback_days
        latest_stripe_run = self.reporting_v2.latest_cash_source_run(
            "stripe"
        )
        stripe_lookback_days = (
            self.settings.reporting_v2_cash_overlap_days
            if latest_stripe_run and latest_stripe_run["complete"]
            else backfill_days
        )
        pt_minder_snapshot = self.store.latest_governed_snapshot("pt_minder")
        if not pt_minder_snapshot:
            raise RuntimeError(
                "A complete accepted PT Minder snapshot is required"
            )

        pt_minder_batch = build_pt_minder_cash_batch(
            pt_minder_snapshot,
            lookback_days=backfill_days,
            as_of=observed_at,
        )
        pt_minder_result = self.reporting_v2.record_cash_batch_shadow(
            {
                key: value
                for key, value in pt_minder_batch.items()
                if key != "adapter_summary"
            }
        )

        stripe_reader = StripeCashReader(
            self.settings.stripe_restricted_key
        )
        stripe_batch = build_stripe_cash_batch(
            payment_intents=stripe_reader.payment_intents(
                created_gte=int(
                    (
                        observed_at
                        - timedelta(days=stripe_lookback_days)
                    ).timestamp()
                )
            ),
            observed_at=observed_at,
            lookback_days=stripe_lookback_days,
        )
        stripe_result = self.reporting_v2.record_cash_batch_shadow(
            {
                key: value
                for key, value in stripe_batch.items()
                if key != "adapter_summary"
            }
        )
        goal = stripe_result["cash_goal"]
        return {
            "mode": "shadow",
            "publication_impact": "none",
            "stripe": {
                **stripe_batch["adapter_summary"],
                "source_run_id": stripe_result["source_run_id"],
                "complete": stripe_batch["complete"],
            },
            "pt_minder": {
                **pt_minder_batch["adapter_summary"],
                "source_run_id": pt_minder_result["source_run_id"],
                "complete": pt_minder_batch["complete"],
            },
            "cash_goal": {
                "available": goal["available"],
                "net_cash_ex_gst_cents": goal[
                    "net_cash_ex_gst_cents"
                ],
                "event_count": goal["event_count"],
                "window_start": goal["window_start"],
                "window_end": goal["window_end"],
                "blocked_reasons": goal["blocked_reasons"],
            },
        }

    def refresh_reporting_v2_ghl_acquisition(self) -> dict[str, Any]:
        if not self.settings.ghl_api_key or not self.settings.ghl_location_id:
            raise RuntimeError(
                "GHL_API_KEY and GHL_LOCATION_ID are required"
            )
        reader = GHLAcquisitionReader(
            self.settings.ghl_api_key,
            self.settings.ghl_location_id,
        )
        observed_at = datetime.now(UTC)
        attendance_rows = self.reconcile_sa_attendance(
            now=observed_at
        )["rows"]
        contacts = reader.contacts()
        payload = build_ghl_acquisition_snapshot(
            contacts=contacts,
            opportunities=reader.opportunities(),
            attendance_rows=attendance_rows,
            observed_at=observed_at,
            onboarding_events=reader.onboarding_events(
                observed_at - timedelta(days=400),
                observed_at + timedelta(days=90),
            ),
        )
        subscriber_events = self.reporting_v2.latest_source_event_payloads(
            "ghl", "website_subscription"
        )
        subscriber_booking = subscriber_assessment_booking_periods(
            subscriber_submissions=subscriber_events,
            assessment_appointments=attendance_rows,
            observed_at=observed_at,
        )
        completion_followup = build_onboarding_followup_plan(
            payload["onboarding_cases"],
            payload["onboarding_events"],
            now=observed_at,
            admin_user_id=self.settings.sa_task_admin_user_id,
            lookback_days=(
                self.settings.onboarding_task_followup_lookback_days
            ),
        )
        identities = {
            str(row.get("id") or ""): {
                "email": row.get("email"),
                "firstName": row.get("firstName"),
                "lastName": row.get("lastName"),
                "name": row.get("name"),
            }
            for row in contacts
            if row.get("id")
        }
        try:
            if (
                not self.settings.trainerize_group_id
                or not self.settings.trainerize_api_token
                or self.settings.trainerize_location_id is None
            ):
                raise RuntimeError(
                    "Trainerize activation credentials are unavailable"
                )
            activation = build_onboarding_activation_evidence(
                trainerize_client=TrainerizeAttendanceClient(
                    self.settings.trainerize_group_id,
                    self.settings.trainerize_api_token,
                    self.settings.trainerize_location_id,
                ),
                ghl_client=GHLAttendanceClient(
                    self.settings.ghl_api_key,
                    self.settings.ghl_location_id,
                    write_enabled=False,
                ),
                onboarding_cases=payload["onboarding_cases"],
                identities=identities,
                observed_at=observed_at,
            )
        except Exception as exc:
            log.exception("Onboarding activation evidence is unavailable")
            activation = {
                "definition_version": "successful-first-week-v1",
                "observed_at": observed_at.isoformat(),
                "complete": False,
                "cases": [],
                "summary": {
                    "eligible_sales": 0,
                    "activated": 0,
                    "onboarding_attended": 0,
                    "three_training_records": 0,
                    "first_week_confirmed": 0,
                    "trainerize_identity_unresolved": 0,
                    "unavailable_reason": type(exc).__name__,
                },
            }
        completion_followup = self._trainerize_attendance_precheck(
            completion_followup,
            identities,
            kind="onboarding",
        )
        snapshot = self.store.accept_snapshot(
            "ghl_acquisition_v2",
            {
                "schema_version": payload["schema_version"],
                "source": payload["source"],
                "observed_at": payload["observed_at"],
                "status": "complete",
                "complete": True,
                "summary": payload["summary"],
                "week_ahead": payload["week_ahead"],
                "subscriber_booking": {
                    "definition_version": subscriber_booking[
                        "definition_version"
                    ],
                    "observed_at": subscriber_booking["observed_at"],
                    "periods": subscriber_booking["periods"],
                    "summary": subscriber_booking["summary"],
                },
                "completion_followup": completion_followup,
                "onboarding_activation": {
                    "definition_version": activation["definition_version"],
                    "complete": activation["complete"],
                    "summary": activation["summary"],
                },
            },
        )
        snapshot_id = snapshot["snapshot_id"]
        accepted_events = 0
        for event_type, rows in (
            ("lead", payload["lead_events"]),
            (
                "prequalification_eligible",
                payload["prequalification_eligible_events"],
            ),
            ("prequalification", payload["prequalification_events"]),
            ("onboarding_appointment", payload["onboarding_events"]),
        ):
            for row in rows:
                occurred_at = (
                    row.get("occurred_at")
                    or row.get("scheduled_start")
                )
                result = self.reporting_v2.accept_source_event(
                    {
                        "source_system": "ghl",
                        "source_object_type": event_type,
                        "source_event_id": row["source_event_id"],
                        "source_object_id": row.get("source_object_id"),
                        "occurred_at": occurred_at,
                        "observed_at": (
                            row.get("observed_at")
                            or payload["observed_at"]
                        ),
                        "source_snapshot_id": snapshot_id,
                        "confidence": (
                            "verified"
                            if event_type
                            in {"lead", "onboarding_appointment"}
                            else row.get("confidence") or "high"
                        ),
                        "payload": row,
                    }
                )
                accepted_events += result["status"] == "accepted"
        sale_results = []
        for sale in payload["sales"]:
            source_event = self.reporting_v2.accept_source_event(
                {
                    "source_system": "ghl",
                    "source_object_type": "commercial_agreement",
                    "source_event_id": sale["source_sale_id"],
                    "source_object_id": sale["source_sale_id"],
                    "occurred_at": sale["sold_at"],
                    "observed_at": payload["observed_at"],
                    "source_snapshot_id": snapshot_id,
                    "confidence": sale["confidence"],
                    "payload": sale,
                }
            )
            sale_results.append(
                self.reporting_v2.record_sale(
                    {
                        **sale,
                        "source_event_version_id": source_event[
                            "event_version_id"
                        ],
                        "attribution_accepted": (
                            sale.get("attribution_state") == "attributed"
                        ),
                    }
                )
            )
        conversion_metrics = (
            self.reporting_v2.record_unique_conversion_shadow(
                attendance_rows=attendance_rows,
                sales=payload["sales"],
                commercial_source_complete=True,
                as_of=observed_at,
                source_snapshot_ids=[snapshot_id],
            )
        )
        funnel_metrics = (
            self.reporting_v2.record_acquisition_onboarding_shadow(
                lead_events=payload["lead_events"],
                prequalification_eligible_events=payload[
                    "prequalification_eligible_events"
                ],
                prequalification_events=payload[
                    "prequalification_events"
                ],
                onboarding_cases=payload["onboarding_cases"],
                as_of=observed_at,
                source_snapshot_ids=[snapshot_id],
            )
        )
        related_snapshot_ids = [snapshot_id]
        for source_name in (
            "website_analytics_v2",
            "strength_assessment_attendance",
        ):
            related = self.store.latest_snapshot(source_name)
            if related and related.get("snapshot_id"):
                related_snapshot_ids.append(related["snapshot_id"])
        subscriber_booking_metrics = (
            self.reporting_v2.record_subscriber_booking_shadow(
                period_metrics=subscriber_booking["periods"],
                as_of=observed_at,
                source_snapshot_ids=related_snapshot_ids,
            )
        )
        activation_metrics = (
            self.reporting_v2.record_onboarding_activation_shadow(
                activation_cases=activation["cases"],
                source_complete=activation["complete"],
                as_of=observed_at,
                source_snapshot_ids=[snapshot_id],
            )
        )
        return {
            "status": "complete",
            "mode": "shadow",
            "source_snapshot_id": snapshot_id,
            "summary": payload["summary"],
            "source_events_accepted": accepted_events,
            "sales_processed": len(sale_results),
            "conversion_metrics": conversion_metrics,
            "funnel_metrics": funnel_metrics,
            "subscriber_booking_metrics": subscriber_booking_metrics,
            "subscriber_booking_summary": subscriber_booking["summary"],
            "activation_metrics": activation_metrics,
            "activation_summary": activation["summary"],
            "completion_followup": completion_followup["counts"],
            "publication_impact": "none",
        }

    def onboarding_completion_followup(
        self,
        *,
        execute: bool = False,
    ) -> dict[str, Any]:
        snapshot = self.store.latest_snapshot("ghl_acquisition_v2")
        if not snapshot:
            raise RuntimeError("GHL acquisition snapshot is unavailable")
        plan = (
            (snapshot.get("payload") or {}).get("completion_followup") or {}
        )
        if not plan:
            raise RuntimeError(
                "Onboarding completion follow-up plan is unavailable"
            )
        if execute and not self.settings.onboarding_task_write_enabled:
            raise RuntimeError("Onboarding outcome task writes are disabled")
        client = GHLAttendanceClient(
            self.settings.ghl_api_key,
            self.settings.ghl_location_id,
            write_enabled=self.settings.onboarding_task_write_enabled,
        )
        result = execute_onboarding_followup_plan(
            client,
            plan,
            write_enabled=(
                execute and self.settings.onboarding_task_write_enabled
            ),
        )
        return {
            "definition_version": "onboarding-outcome-followup-v1",
            "writes_enabled": (
                self.settings.onboarding_task_write_enabled
            ),
            "plan": plan,
            "result": result,
        }

    def refresh_sa_listed_history(self) -> dict[str, Any]:
        if not self.settings.sa_listed_history_enabled:
            raise RuntimeError("SA listed history collection is disabled")
        observed_at = datetime.now(UTC)
        sheets = build_sheets_service(
            self.settings.google_service_account_json
        )
        response = (
            sheets.spreadsheets()
            .values()
            .get(
                spreadsheetId=self.settings.google_spreadsheet_id,
                range="'Appointments'!A2:N2000",
                valueRenderOption="FORMATTED_VALUE",
            )
            .execute()
        )
        history = build_listed_history(
            response.get("values") or [],
            observed_at=observed_at,
        )
        accepted = self.store.accept_snapshot(
            "sa_listed_history",
            {
                "schema_version": history["schema_version"],
                "source": history["source"],
                "tab": history["tab"],
                "observed_at": history["observed_at"],
                "status": history["status"],
                "complete": history["complete"],
                "summary": history["summary"],
            },
        )
        projection = self.reporting_v2.record_sa_listed_history_shadow(
            history["events"],
            observed_at=history["observed_at"],
            source_snapshot_id=accepted["snapshot_id"],
        )
        return {
            **accepted,
            "summary": history["summary"],
            "reporting_v2_shadow": projection,
            "publication_impact": "none",
        }

    def submit_reporting_v2_manual_input(
        self,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        if not self.settings.reporting_v2_manual_inputs_enabled:
            raise RuntimeError(
                "Reporting V2 manual inputs are disabled"
            )
        return self.reporting_v2.submit_manual_input(payload)

    def decide_reporting_v2_manual_input(
        self,
        input_id: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        if not self.settings.reporting_v2_manual_inputs_enabled:
            raise RuntimeError(
                "Reporting V2 manual inputs are disabled"
            )
        return self.reporting_v2.decide_manual_input(
            input_id,
            decision=str(payload.get("decision") or ""),
            decided_by=str(payload.get("decided_by") or ""),
            reason=str(payload.get("reason") or ""),
        )

    def poll_compatibility_health(self) -> dict[str, Any]:
        results = {}
        endpoints = {
            "retention_intelligence": self.settings.retention_health_url,
            "pt_booking_continuity": self.settings.pt_health_url,
        }
        for source, url in endpoints.items():
            try:
                response = requests.get(url, timeout=20)
                response.raise_for_status()
                body = response.json()
                observed_at = datetime.now(UTC).isoformat()
                if source == "retention_intelligence":
                    observed_at = (
                        body.get("latestRun", {}).get("completedAt")
                        or observed_at
                    )
                if source == "pt_booking_continuity":
                    observed_at = (
                        body.get("lastSuccessfulRun")
                        or body.get("latestRevenueRun", {}).get("completedAt")
                        or observed_at
                    )
                payload = validate_summary(
                    source,
                    {
                        "observed_at": observed_at,
                        "status": (
                            "healthy"
                            if body.get("status") == "ok"
                            else "failed"
                        ),
                        "summary": body,
                    },
                )
                results[source] = self.store.accept_snapshot(source, payload)
                if source == "pt_booking_continuity":
                    revenue = body.get("latestRevenueRun") or {}
                    if revenue.get("completedAt"):
                        revenue_payload = validate_summary(
                            "revenue_control",
                            {
                                "observed_at": revenue["completedAt"],
                                "status": revenue.get("status", "failed"),
                                "summary": revenue,
                            },
                        )
                        results["revenue_control"] = self.store.accept_snapshot(
                            "revenue_control", revenue_payload
                        )
            except Exception as exc:
                results[source] = {
                    "status": "failed",
                    "error": type(exc).__name__,
                }
        return results

    def dashboard_data(self) -> dict[str, Any]:
        now = datetime.now(UTC)
        sources = []
        for snapshot in self.store.latest_snapshots():
            observed_at = datetime.fromisoformat(
                snapshot["observed_at"].replace("Z", "+00:00")
            )
            if observed_at.tzinfo is None:
                observed_at = observed_at.replace(tzinfo=UTC)
            age = (
                now - observed_at
            ).total_seconds() / 3600
            max_age = SOURCE_MAX_AGE_HOURS.get(snapshot["source"], 26)
            freshness = (
                "fresh"
                if max_age is None or age <= max_age
                else "stale"
            )
            sources.append(
                {
                    **{key: value for key, value in snapshot.items() if key != "payload"},
                    "age_hours": round(max(0, age), 1),
                    "max_age_hours": max_age,
                    "freshness": freshness,
                }
            )
        kpi = self.store.latest_snapshot("google_kpi") or {}
        metrics = dict(
            kpi.get("payload", {})
            .get("summary", {})
            .get("metrics", {})
        )
        if metrics.get("recurring_cash_collected") is None:
            total_cash = metrics.get("cash_collected")
            new_cash = metrics.get("new_cash_collected")
            if total_cash is not None and new_cash is not None:
                metrics["recurring_cash_collected"] = max(
                    0, total_cash - new_cash
                )
        if metrics.get("net_service_movement") is None:
            movement = [
                value
                for value in (
                    metrics.get("sgpt_net"),
                    metrics.get("pt_net"),
                )
                if value is not None
            ]
            metrics["net_service_movement"] = (
                sum(movement) if movement else None
            )
        performance_snapshot = (
            self.store.latest_snapshot("trainerize_performance") or {}
        )
        performance_payload = performance_snapshot.get("payload") or {}
        performance_summary = performance_payload.get("summary") or {}
        performance_source = next(
            (
                source
                for source in sources
                if source["source"] == "trainerize_performance"
            ),
            {},
        )
        trainerize_performance = {
            "available": bool(performance_snapshot),
            "status": performance_payload.get("status"),
            "freshness": performance_source.get("freshness"),
            "age_hours": performance_source.get("age_hours"),
            "observed_at": performance_snapshot.get("observed_at"),
            "run_id": performance_summary.get("runId"),
            "active_roster": performance_summary.get("activeRoster"),
            "members_with_detailed_workouts": performance_summary.get(
                "membersWithDetailedWorkouts"
            ),
            "reassessment_due": performance_summary.get(
                "reassessmentDue"
            ),
            "remarkable_candidates": performance_summary.get(
                "remarkableCandidates"
            ),
            "detailed_workout_source_through": performance_summary.get(
                "detailedWorkoutSourceThrough"
            ),
            "strength_improvement": performance_summary.get(
                "strengthImprovement"
            ),
            "top_performers": performance_summary.get("topPerformers") or [],
            "workout_milestones": performance_summary.get(
                "workoutMilestones"
            ) or [],
            "standards_milestones": performance_summary.get(
                "standardsMilestones"
            ) or [],
        }
        prequalification_snapshot = (
            self.store.latest_snapshot(
                "strength_assessment_prequalification"
            )
            or {}
        )
        prequalification_summary = (
            (prequalification_snapshot.get("payload") or {}).get("summary")
            or {}
        )
        prequalification_total = prequalification_summary.get(
            "eligibleLeads"
        )
        prequalification_completed = prequalification_summary.get(
            "completed"
        )
        prequalification_rate = prequalification_summary.get(
            "completionRate"
        )
        if (
            prequalification_rate is None
            and prequalification_total
            and prequalification_completed is not None
        ):
            prequalification_rate = (
                prequalification_completed / prequalification_total
            )
        acquisition_funnel = {
            "prequalification_available": bool(
                prequalification_snapshot
                and prequalification_rate is not None
            ),
            "prequalification_completion_rate": prequalification_rate,
            "prequalification_completed": prequalification_completed,
            "prequalification_eligible": prequalification_total,
            "onboarding_speed_available": False,
            "average_sale_to_onboarding_days": None,
            "onboarding_speed_note": (
                "Requires a governed GHL link between the sale date and the "
                "first completed KickStart or Fast Track onboarding session."
            ),
        }
        acquisition_snapshot = (
            self.store.latest_snapshot("ghl_acquisition_v2") or {}
        )
        activation_state = (
            (acquisition_snapshot.get("payload") or {})
            .get("onboarding_activation", {})
        )
        activation_summary = activation_state.get("summary") or {}
        acquisition_funnel["successful_first_week"] = {
            "available": bool(activation_state.get("complete")),
            "observed_at": acquisition_snapshot.get("observed_at"),
            "eligible_sales": activation_summary.get("eligible_sales"),
            "activated": activation_summary.get("activated"),
            "onboarding_attended": activation_summary.get(
                "onboarding_attended"
            ),
            "three_training_records": activation_summary.get(
                "three_training_records"
            ),
            "first_week_confirmed": activation_summary.get(
                "first_week_confirmed"
            ),
            "trainerize_identity_unresolved": activation_summary.get(
                "trainerize_identity_unresolved"
            ),
            "unavailable_reason": activation_summary.get(
                "unavailable_reason"
            ),
        }
        attendance_snapshot = self.store.latest_snapshot(
            "strength_assessment_attendance"
        )
        attendance = self.sa_attendance_state() if attendance_snapshot else {
            "definition_version": "sa-attendance-v2",
            "summary": {
                "booked": 0,
                "showed": 0,
                "legacy_showed": 0,
                "tracked_showed": 0,
                "no_show": 0,
                "tracked_no_show": 0,
                "cancelled": 0,
                "tracked_cancelled": 0,
                "invalid": 0,
                "unresolved": 0,
                "show_rate": None,
                "show_rate_denominator": 0,
                "cancellation_rate": None,
                "cancellation_rate_denominator": 0,
                "show_rate_provisional": True,
                "complete": False,
            },
            "source": None,
            "exceptions": [],
            "writes": {
                "ghl_enabled": self.settings.sa_ghl_write_enabled,
                "sheets_enabled": self.settings.sa_sheets_write_enabled,
            },
        }
        metrics["governed_attendance"] = attendance["summary"]
        if self.settings.sa_sheets_write_enabled:
            metrics["show_rate"] = attendance["summary"]["show_rate"]
            metrics["bookings_attended"] = attendance["summary"]["showed"]
        self_mending_snapshot = (
            self.store.latest_snapshot("pt_roster_self_mending") or {}
        )
        self_mending_payload = self_mending_snapshot.get("payload") or {}
        self_mending_summary = self_mending_payload.get("summary") or {}
        self_mending_source = next(
            (
                source
                for source in sources
                if source["source"] == "pt_roster_self_mending"
            ),
            {},
        )
        action_copy = {
            "missing_payment_evidence": {
                "issue": "Payment or account status needs review",
                "recommended_action": (
                    "Confirm whether the client is returning, staying "
                    "paused, or cancelling."
                ),
            },
            "missing_agreement_terms": {
                "issue": "Membership details are incomplete",
                "recommended_action": (
                    "Confirm the agreed service, frequency and payment terms."
                ),
            },
            "trainerize_not_provisioned": {
                "issue": "Training account setup needs review",
                "recommended_action": (
                    "Confirm the client has the correct Trainerize access."
                ),
            },
            "duplicate_roster_rows": {
                "issue": "Duplicate PT client records detected",
                "recommended_action": (
                    "Review the duplicate records before changing the roster."
                ),
            },
        }
        action_items = []
        for item in self_mending_summary.get("action_items") or []:
            wording = action_copy.get(
                str(item.get("reason") or ""),
                {
                    "issue": "Client record needs review",
                    "recommended_action": (
                        "Review the supporting payment, membership and "
                        "access evidence."
                    ),
                },
            )
            action_items.append({**item, **wording})
        pt_roster_self_mending = {
            "available": bool(self_mending_snapshot),
            "status": self_mending_payload.get("status"),
            "freshness": self_mending_source.get("freshness"),
            "age_hours": self_mending_source.get("age_hours"),
            "observed_at": self_mending_snapshot.get("observed_at"),
            "mode": self_mending_summary.get("mode"),
            "active_pt_rows": self_mending_summary.get(
                "active_pt_rows"
            ),
            "confirmed_current_pt": self_mending_summary.get(
                "confirmed_current_pt"
            ),
            "pending_terms": self_mending_summary.get("pending_terms"),
            "pending_provisioning": self_mending_summary.get(
                "pending_provisioning"
            ),
            "approved_holds": self_mending_summary.get("approved_holds"),
            "exceptions": self_mending_summary.get("exceptions"),
            "exact_sales_links": self_mending_summary.get(
                "exact_sales_links"
            ),
            "historical_sales_links": self_mending_summary.get(
                "historical_sales_links"
            ),
            "legacy_sales_history_unavailable": (
                self_mending_summary.get(
                    "legacy_sales_history_unavailable"
                )
            ),
            "future_starts": self_mending_summary.get("future_starts"),
            "pt_minder_payment_links": self_mending_summary.get(
                "pt_minder_payment_links"
            ),
            "absent_sales_history": self_mending_summary.get(
                "absent_sales_history"
            ),
            "duplicate_active_identities": self_mending_summary.get(
                "duplicate_active_identities"
            ),
            "duplicate_dominant_pairs_identified": (
                self_mending_summary.get(
                    "duplicate_dominant_pairs_identified"
                )
            ),
            "proposed_patches": self_mending_summary.get(
                "proposed_patches"
            ),
            "proposals_eligible_for_owner_approval": (
                self_mending_summary.get(
                    "proposals_eligible_for_owner_approval"
                )
            ),
            "proposals_requiring_manual_evidence": (
                self_mending_summary.get(
                    "proposals_requiring_manual_evidence"
                )
            ),
            "writes_enabled": self_mending_summary.get(
                "writes_enabled", False
            ),
            "action_items": action_items,
        }
        stale_sources = [
            source["source"]
            for source in sources
            if source["freshness"] != "fresh"
        ]
        roster_candidate_state = self.store.roster_candidate_state()
        roster_review_required = bool(
            roster_candidate_state
            and not roster_candidate_state.get("exact_match")
        )
        attendance_exception_count = len(attendance.get("exceptions") or [])
        return {
            "generated_at": now.isoformat(timespec="seconds"),
            "mode": "shadow",
            "sources": sorted(sources, key=lambda row: row["source"]),
            "metrics": metrics,
            "canonical": self.store.canonical_counts(),
            "cohort": self.store.latest_cohort_summary(),
            "governed": self.store.governed_state(),
            "active_notice_periods": self.store.active_notice_periods(),
            "payment_service_overrides": (
                self.store.payment_service_override_state()
            ),
            "entitlement_queue": (
                self.store.entitlement_exception_queue()
            ),
            "roster_candidate": roster_candidate_state,
            "trainerize_performance": trainerize_performance,
            "acquisition_funnel": acquisition_funnel,
            "strength_assessment_attendance": attendance,
            "pt_roster_self_mending": pt_roster_self_mending,
            "jobs": self.store.recent_jobs(),
            "exceptions": self.store.open_exception_counts(),
            "system_summary": {
                "all_current": not stale_sources,
                "stale_source_count": len(stale_sources),
                "stale_sources": stale_sources,
                "accepted_source_count": len(sources),
                "roster_review_required": roster_review_required,
                "decision_waiting_count": (
                    len(action_items)
                    + int(roster_review_required)
                    + attendance_exception_count
                ),
                "attendance_exception_count": attendance_exception_count,
            },
        }
