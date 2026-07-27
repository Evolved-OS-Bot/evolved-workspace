from __future__ import annotations

import logging
import threading
from collections import defaultdict
from datetime import datetime, timedelta

from .calendar_registry import build_registry
from .cohort import resolve_cohort, resolve_contact
from .config import BRISBANE_TZ, Settings
from .ghl_client import GHLReadOnlyClient
from .google_sheets import SheetsKPIWriter
from .kpi import aggregate_weekly_pt_kpi, monday_for
from .models import Appointment, Finding
from .pack_ledger import prepaid_pack_findings
from .reconciler import reconcile_contact
from .reporting import high_risk, send_report
from .source_reconciliation import (
    build_cross_system_snapshot,
    cross_system_findings,
    reconcile_primary_with_cross_system_evidence,
)
from .state_store import StateStore


log = logging.getLogger(__name__)


class ShadowAuditService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = GHLReadOnlyClient(settings.ghl_api_key, settings.ghl_location_id)
        self.store = StateStore(settings.database_path)
        self._run_lock = threading.Lock()

    def _resolve_full_cohort(self):
        """Hydrate status-sensitive contacts before applying hold/cancellation rules."""
        raw_contacts = self.client.list_contacts()
        opportunities = self.client.list_opportunities()
        cohort = resolve_cohort(raw_contacts, opportunities)

        opportunities_by_contact: dict[str, list[dict]] = defaultdict(list)
        for opportunity in opportunities:
            contact_id = opportunity.get("contactId") or (
                opportunity.get("contact") or {}
            ).get("id")
            if contact_id:
                opportunities_by_contact[str(contact_id)].append(opportunity)

        hydrated = []
        for contact in cohort:
            if contact.effective_status not in {"pt_cancellation", "pt_hold"}:
                hydrated.append(contact)
                continue
            full = resolve_contact(
                self.client.get_contact(contact.id),
                opportunities_by_contact.get(contact.id, []),
            )
            hydrated.append(full or contact)
        return hydrated

    def _registry_and_events(self):
        registry = build_registry(self.client.list_calendars())
        calendars = {item.id: item for item in registry}
        now = datetime.now(BRISBANE_TZ)
        start = now - timedelta(weeks=self.settings.history_weeks)
        end = now + timedelta(weeks=self.settings.future_read_weeks)
        events: list[Appointment] = []
        for calendar in registry:
            events.extend(self.client.list_events(calendar.id, start, end))
        by_contact: dict[str, list[Appointment]] = defaultdict(list)
        for event in events:
            by_contact[event.contact_id].append(event)
        return calendars, by_contact, events, now

    def _write_weekly_kpi(self, calendars, events, now) -> dict | None:
        if not self.settings.kpi_write_enabled:
            return None
        kpi = aggregate_weekly_pt_kpi(events, calendars, monday_for(now))
        result = SheetsKPIWriter(self.settings).write(kpi)
        self.store.record_kpi_write(kpi.week_start.isoformat(), result)
        return result

    def run_full(self, send_email: bool = True) -> tuple[str, list[Finding]]:
        if not self._run_lock.acquire(blocking=False):
            raise RuntimeError("A PT shadow audit is already running")
        run_id = self.store.start_run("full")
        try:
            calendars, by_contact, events, now = self._registry_and_events()
            cohort = self._resolve_full_cohort()
            findings = [
                reconcile_contact(
                    contact,
                    by_contact.get(contact.id, []),
                    calendars,
                    now,
                    horizon_weeks=self.settings.horizon_weeks,
                    minimum_confidence=self.settings.pattern_confidence,
                )
                for contact in cohort
            ]
            if self.settings.cross_system_reconciliation_enabled:
                try:
                    snapshot = build_cross_system_snapshot(self.settings)
                    primary_by_contact = {
                        item.contact_id: item for item in findings
                    }
                    for contact in cohort:
                        evidence = snapshot.evidence_for(contact)
                        primary_by_contact[contact.id].evidence[
                            "cross_system"
                        ] = evidence
                        has_future = any(
                            event.start >= now
                            and not event.deleted
                            and event.status
                            not in {"cancelled", "canceled", "no_show", "noshow"}
                            for event in by_contact.get(contact.id, [])
                        )
                        reconcile_primary_with_cross_system_evidence(
                            primary_by_contact[contact.id],
                            contact,
                            evidence,
                            has_future,
                        )
                        findings.extend(
                            cross_system_findings(contact, evidence, has_future)
                        )
                        findings.extend(
                            prepaid_pack_findings(
                                contact,
                                by_contact.get(contact.id, []),
                                evidence,
                                now,
                            )
                        )
                except Exception as exc:
                    log.exception("Cross-system reconciliation failed")
                    findings.append(
                        Finding(
                            contact_id="system",
                            contact_name="Cross-system reconciliation",
                            category="CROSS_SYSTEM_SOURCE_UNAVAILABLE",
                            reason=(
                                "Stripe, Trainerize or Brown & Casserly could not be "
                                f"read: {type(exc).__name__}. The GHL booking audit "
                                "continued without cross-system evidence."
                            ),
                            effective_status="system",
                        )
                    )
            self.store.complete_run(run_id, findings, len(cohort))
            try:
                result = self._write_weekly_kpi(calendars, events, now)
                if result:
                    log.info(
                        "Weekly PT KPI written: week=%s column=%s bookings=%s hours=%s",
                        result["week_start"],
                        result["column"],
                        result["kpi"]["total_bookings"],
                        result["kpi"]["total_booked_hours"],
                    )
            except Exception:
                log.exception("Weekly PT KPI write failed; shadow report will still be sent")
            if send_email:
                send_report(self.settings, findings, run_id)
            return run_id, findings
        except Exception as exc:
            self.store.fail_run(run_id, str(exc))
            raise
        finally:
            self._run_lock.release()

    def run_targeted(self, contact_id: str, alert_high_risk: bool = True):
        run_id = self.store.start_run("targeted")
        try:
            calendars, by_contact, _events, now = self._registry_and_events()
            raw = self.client.get_contact(contact_id)
            contact = resolve_contact(
                raw, self.client.list_contact_opportunities(contact_id)
            )
            findings: list[Finding] = []
            if contact:
                findings.append(
                    reconcile_contact(
                        contact,
                        by_contact.get(contact.id, []),
                        calendars,
                        now,
                        horizon_weeks=self.settings.horizon_weeks,
                        minimum_confidence=self.settings.pattern_confidence,
                    )
                )
            self.store.complete_run(run_id, findings, 1 if contact else 0)
            risky = high_risk(findings)
            if alert_high_risk and risky:
                send_report(
                    self.settings,
                    risky,
                    run_id,
                    subject_prefix="PT Booking Shadow · Immediate exception",
                )
            return run_id, findings
        except Exception as exc:
            self.store.fail_run(run_id, str(exc))
            raise

    def process_due_events(self) -> int:
        processed = 0
        for contact_id in self.store.due_contacts():
            try:
                self.run_targeted(contact_id)
            finally:
                self.store.mark_contact_events_processed(contact_id)
            processed += 1
        return processed
