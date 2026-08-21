from __future__ import annotations

import json
from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal
from typing import Any, Iterable
from zoneinfo import ZoneInfo

from sqlalchemy import select

from .reporting_v2 import (
    ReportingV2Repository,
    completed_reporting_periods,
    sale_events,
    source_events,
)
from .store import source_identities


BRISBANE_TZ = ZoneInfo("Australia/Brisbane")
LIFECYCLE_CONTRACT_VERSION = "membership-lifecycle-v1"
CURRENT_PERSON_CONTRACT_VERSION = "current-person-v1"
ACCEPTED_METRIC_CONFIDENCE = {"verified", "high"}
OPEN_HOLD_STATUSES = {
    "pending hold",
    "escalated hold",
    "on hold",
    "returning",
}
APPROVED_HOLD_STATUSES = {"on hold", "returning", "completed"}


LIFECYCLE_METRIC_DEFINITIONS = (
    {
        "metric_id": "members_joined",
        "plain_english_name": "Members joined",
        "decision_question": "How many unique people joined as members?",
        "event_grain": "unique person with a qualifying new-membership sale",
        "numerator_definition": (
            "unique canonical people with an accepted qualifying "
            "new-membership sale in the period"
        ),
        "denominator_definition": None,
        "inclusion_rules": [
            "one person once per period",
            "one Fast Track sale remains one joined member",
        ],
        "exclusion_rules": [
            "reactivations",
            "existing-member add-ons",
            "duplicate service components",
            "unresolved identities",
        ],
        "unit": "people",
    },
    {
        "metric_id": "final_membership_endings",
        "plain_english_name": "Final membership endings",
        "decision_question": (
            "How many unique people reached their evidenced final membership "
            "access date?"
        ),
        "event_grain": "unique person final membership-ending event",
        "numerator_definition": (
            "unique canonical people with an accepted membership_ended event"
        ),
        "denominator_definition": None,
        "inclusion_rules": [
            "full membership cancellation",
            "PT-only member whose complete membership ends",
        ],
        "exclusion_rules": [
            "active notice before final access",
            "PT ending while SGPT continues",
            "downgrade-only transition",
            "missing or ambiguous effective date",
        ],
        "unit": "people",
    },
    {
        "metric_id": "straight_cancellations",
        "plain_english_name": "Straight cancellations",
        "decision_question": (
            "How many final endings were full membership cancellations rather "
            "than service downgrades?"
        ),
        "event_grain": "unique person final straight-cancellation event",
        "numerator_definition": (
            "unique people with membership_ended transition_kind "
            "straight_cancellation"
        ),
        "denominator_definition": None,
        "inclusion_rules": ["complete member relationship ends"],
        "exclusion_rules": ["downgrade-only", "approved hold"],
        "unit": "people",
    },
    {
        "metric_id": "downgrade_only_transitions",
        "plain_english_name": "Downgrade-only transitions",
        "decision_question": (
            "How many people ended PT while their SGPT membership continued?"
        ),
        "event_grain": "unique person downgrade-only event",
        "numerator_definition": (
            "unique people with an accepted downgrade_only event"
        ),
        "denominator_definition": None,
        "inclusion_rules": [
            "Fast Track or SGPT-plus-PT member ends PT",
            "SGPT remains active",
        ],
        "exclusion_rules": ["final member loss"],
        "unit": "people",
    },
    {
        "metric_id": "approved_holds",
        "plain_english_name": "Approved holds",
        "decision_question": "How many unique people began an approved hold?",
        "event_grain": "unique person approved-hold start",
        "numerator_definition": (
            "unique people with an accepted hold_approved event"
        ),
        "denominator_definition": None,
        "inclusion_rules": ["On Hold, Returning or Completed with exact dates"],
        "exclusion_rules": [
            "pending or escalated request",
            "ambiguous or backwards dates",
        ],
        "unit": "people",
    },
    {
        "metric_id": "membership_attrition_rate",
        "plain_english_name": "Membership attrition rate",
        "decision_question": (
            "What proportion of the historical opening member cohort reached "
            "a final membership ending in the period?"
        ),
        "event_grain": "unique opening-cohort member",
        "numerator_definition": "unique final membership endings in the period",
        "denominator_definition": (
            "verified or high-confidence unique active members at period open"
        ),
        "inclusion_rules": ["complete historical opening cohort"],
        "exclusion_rules": [
            "downgrade-only transitions",
            "approved holds",
            "ambiguous cohort or event dates",
        ],
        "unit": "ratio",
    },
    {
        "metric_id": "net_unique_member_growth",
        "plain_english_name": "Net unique-member growth",
        "decision_question": (
            "How many unique joined members remain after final member losses?"
        ),
        "event_grain": "unique canonical person",
        "numerator_definition": (
            "unique members joined minus unique final membership endings"
        ),
        "denominator_definition": None,
        "inclusion_rules": ["one person once on each side of the equation"],
        "exclusion_rules": [
            "duplicate Fast Track components",
            "PT ending while SGPT continues",
        ],
        "unit": "people",
    },
)


def _normalise(value: Any) -> str:
    return " ".join(str(value or "").strip().lower().split())


def _local_midnight(value: date) -> datetime:
    return datetime.combine(value, time.min, tzinfo=BRISBANE_TZ)


def _date(value: Any, field: str) -> date | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return date.fromisoformat(text)
    except ValueError as exc:
        raise ValueError(f"{field} must be an ISO date") from exc


def _latest_versions(rows: Iterable[Any]) -> list[Any]:
    latest: dict[tuple[str, str, str], Any] = {}
    for row in rows:
        key = (
            str(row["source_system"]),
            str(row["source_object_type"]),
            str(row["source_event_id"]),
        )
        latest.setdefault(key, row)
    return list(latest.values())


def _service_types(row: dict[str, Any]) -> set[str]:
    return {
        _normalise(service.get("service_type"))
        for service in row.get("services") or []
        if _normalise(service.get("service_type"))
    }


def project_snapshot_row(
    row: dict[str, Any],
    *,
    person_id: str,
) -> dict[str, Any]:
    """Project only exact GHL lifecycle evidence into metric events."""
    services = _service_types(row)
    cancellation_type = _normalise(row.get("cancellation_type"))
    lifecycle_status = _normalise(row.get("lifecycle_status"))
    cancellation_status = _normalise(row.get("cancellation_status"))
    final_access = _date(row.get("final_access_date"), "final_access_date")
    notice_end = _date(row.get("notice_end_date"), "notice_end_date")
    hold_start = _date(row.get("hold_start_date"), "hold_start_date")
    hold_end = _date(row.get("hold_end_date"), "hold_end_date")
    hold_status = _normalise(row.get("hold_status"))
    hold_type = _normalise(row.get("hold_type"))

    events: list[dict[str, Any]] = []
    exceptions: list[dict[str, Any]] = []
    cancellation_present = (
        lifecycle_status in {"cancelling", "cancelled", "inactive"}
        or cancellation_status in {"notice active", "cancelling", "cancelled"}
    )
    continuing_sgpt = bool({"sgpt", "fast_track"} & services)
    if cancellation_present:
        if final_access is None:
            exceptions.append(
                {
                    "code": "missing_final_access_date",
                    "person_id": person_id,
                    "reason": (
                        "A cancellation state cannot become member loss or a "
                        "downgrade without an exact final access date."
                    ),
                }
            )
        elif cancellation_type == "membership":
            events.append(
                {
                    "event_type": "membership_ended",
                    "effective_date": final_access,
                    "transition_kind": "straight_cancellation",
                    "service_from": sorted(services),
                    "service_to": [],
                }
            )
        elif cancellation_type == "pt" and continuing_sgpt:
            events.append(
                {
                    "event_type": "downgrade_only",
                    "effective_date": final_access,
                    "transition_kind": "pt_ended_sgpt_continues",
                    "service_from": sorted(services),
                    "service_to": ["sgpt"],
                }
            )
        elif cancellation_type == "pt":
            events.append(
                {
                    "event_type": "membership_ended",
                    "effective_date": final_access,
                    "transition_kind": "pt_only_membership_ended",
                    "service_from": sorted(services),
                    "service_to": [],
                }
            )
        else:
            exceptions.append(
                {
                    "code": "ambiguous_cancellation_type",
                    "person_id": person_id,
                    "reason": (
                        "Cancellation type must be Membership or PT before an "
                        "ending can be classified."
                    ),
                }
            )

    if hold_status in APPROVED_HOLD_STATUSES:
        if hold_start is None or hold_end is None:
            exceptions.append(
                {
                    "code": "missing_hold_dates",
                    "person_id": person_id,
                    "reason": (
                        "An approved hold requires exact start and end dates."
                    ),
                }
            )
        elif hold_end <= hold_start:
            exceptions.append(
                {
                    "code": "invalid_hold_dates",
                    "person_id": person_id,
                    "reason": "Hold end must follow hold start.",
                }
            )
        else:
            events.append(
                {
                    "event_type": "hold_approved",
                    "effective_date": hold_start,
                    "transition_kind": hold_type or "membership",
                    "service_from": sorted(services),
                    "service_to": sorted(services),
                    "effective_end_date": hold_end.isoformat(),
                }
            )

    return {
        "state": {
            "person_id": person_id,
            "lifecycle_status": lifecycle_status or "review_required",
            "cancellation_status": cancellation_status or None,
            "cancellation_type": cancellation_type or None,
            "notice_end_date": notice_end.isoformat() if notice_end else None,
            "final_access_date": (
                final_access.isoformat() if final_access else None
            ),
            "hold_status": hold_status or None,
            "hold_type": hold_type or None,
            "hold_start_date": hold_start.isoformat() if hold_start else None,
            "hold_end_date": hold_end.isoformat() if hold_end else None,
            "services": sorted(services),
        },
        "events": events,
        "exceptions": exceptions,
    }


class MembershipLifecycleRepository:
    def __init__(
        self,
        engine,
        reporting_v2: ReportingV2Repository,
    ):
        self.engine = engine
        self.reporting_v2 = reporting_v2
        self._seed_definitions()

    def _seed_definitions(self) -> None:
        for item in LIFECYCLE_METRIC_DEFINITIONS:
            self.reporting_v2.register_metric_definition(
                {
                    **item,
                    "definition_version": LIFECYCLE_CONTRACT_VERSION,
                    "event_grain": item["event_grain"],
                    "source_authority": {
                        "lifecycle": (
                            "GHL through accepted membership reconciliation"
                        ),
                        "identity_and_history": "Operating Data Hub",
                        "joins": "accepted qualifying GHL agreement sale",
                    },
                    "period_semantics": (
                        "completed Brisbane-local week, rolling 28 days or "
                        "rolling 90 days"
                    ),
                    "minimum_freshness": {
                        "membership_reconciliation_hours": 14,
                        "ghl_acquisition_v2_hours": 14,
                    },
                    "owner": "Peter Brown",
                    "approval_state": "approved_shadow",
                }
            )

    def _person_ids_by_canonical_key(
        self,
        canonical_keys: Iterable[str],
    ) -> dict[str, str]:
        keys = {
            _normalise(key)
            for key in canonical_keys
            if _normalise(key)
        }
        if not keys:
            return {}
        from .store import canonical_people

        with self.engine.begin() as connection:
            rows = connection.execute(
                select(
                    canonical_people.c.canonical_key,
                    canonical_people.c.person_id,
                ).where(canonical_people.c.canonical_key.in_(keys))
            ).mappings().all()
        return {
            _normalise(row["canonical_key"]): str(row["person_id"])
            for row in rows
        }

    def record_membership_snapshot(
        self,
        payload: dict[str, Any],
        *,
        source_snapshot_id: str,
    ) -> dict[str, Any]:
        observed_at = datetime.fromisoformat(
            str(payload["observed_at"]).replace("Z", "+00:00")
        )
        person_ids = self._person_ids_by_canonical_key(
            row["canonical_key"] for row in payload["rows"]
        )
        accepted = 0
        duplicates = 0
        quarantined = 0
        exception_rows: list[dict[str, Any]] = []
        event_ids: list[str] = []
        for row in payload["rows"]:
            person_id = person_ids.get(_normalise(row["canonical_key"]))
            if not person_id:
                exception_rows.append(
                    {
                        "code": "canonical_person_missing",
                        "canonical_key": row["canonical_key"],
                    }
                )
                continue
            projection = project_snapshot_row(row, person_id=person_id)
            state_result = self.reporting_v2.accept_source_event(
                {
                    "source_system": "ghl",
                    "source_object_type": "membership_lifecycle_state",
                    "source_event_id": person_id,
                    "source_object_id": person_id,
                    "occurred_at": observed_at,
                    "observed_at": observed_at,
                    "source_run_id": payload["source_run_id"],
                    "source_snapshot_id": source_snapshot_id,
                    "confidence": "verified",
                    "payload": {
                        **projection["state"],
                        "contract_version": LIFECYCLE_CONTRACT_VERSION,
                    },
                }
            )
            accepted += state_result["status"] == "accepted"
            duplicates += state_result["status"] == "duplicate"
            event_ids.append(state_result["event_version_id"])
            for event in projection["events"]:
                event_date = event["effective_date"]
                event_result = self.reporting_v2.accept_source_event(
                    {
                        "source_system": "ghl",
                        "source_object_type": "membership_lifecycle_event",
                        "source_event_id": (
                            f"{person_id}:{event['event_type']}:"
                            f"{event_date.isoformat()}"
                        ),
                        "source_object_id": person_id,
                        "occurred_at": _local_midnight(event_date),
                        "effective_at": _local_midnight(event_date),
                        "observed_at": observed_at,
                        "source_run_id": payload["source_run_id"],
                        "source_snapshot_id": source_snapshot_id,
                        "confidence": "verified",
                        "payload": {
                            **event,
                            "effective_date": event_date.isoformat(),
                            "person_id": person_id,
                            "contract_version": LIFECYCLE_CONTRACT_VERSION,
                            "evidence": {
                                "cancellation_status": row.get(
                                    "cancellation_status"
                                ),
                                "cancellation_type": row.get(
                                    "cancellation_type"
                                ),
                                "final_access_date": row.get(
                                    "final_access_date"
                                ),
                                "hold_status": row.get("hold_status"),
                                "hold_start_date": row.get(
                                    "hold_start_date"
                                ),
                                "hold_end_date": row.get("hold_end_date"),
                            },
                        },
                    }
                )
                accepted += event_result["status"] == "accepted"
                duplicates += event_result["status"] == "duplicate"
                event_ids.append(event_result["event_version_id"])
            for exception in projection["exceptions"]:
                exception_rows.append(exception)
                result = self.reporting_v2.accept_source_event(
                    {
                        "source_system": "ghl",
                        "source_object_type": (
                            "membership_lifecycle_exception"
                        ),
                        "source_event_id": (
                            f"{person_id}:{exception['code']}:"
                            f"{payload['source_run_id']}"
                        ),
                        "source_object_id": person_id,
                        "occurred_at": observed_at,
                        "observed_at": observed_at,
                        "source_run_id": payload["source_run_id"],
                        "source_snapshot_id": source_snapshot_id,
                        "confidence": "unresolved",
                        "acceptance_state": "quarantined",
                        "rejection_reason": exception["reason"],
                        "payload": {
                            **exception,
                            "contract_version": LIFECYCLE_CONTRACT_VERSION,
                        },
                    }
                )
                quarantined += result["status"] == "accepted"
        return {
            "contract_version": LIFECYCLE_CONTRACT_VERSION,
            "mode": "shadow",
            "publication_impact": "none",
            "source_snapshot_id": source_snapshot_id,
            "accepted_event_versions": accepted,
            "duplicate_event_versions": duplicates,
            "quarantined_event_versions": quarantined,
            "event_version_ids": sorted(set(event_ids)),
            "exceptions": exception_rows,
        }

    def record_historical_backfill(
        self,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        observed_at_text = str(payload.get("observed_at") or "").strip()
        source_run_id = str(payload.get("source_run_id") or "").strip()
        if not observed_at_text or not source_run_id:
            raise ValueError("observed_at and source_run_id are required")
        observed_at = datetime.fromisoformat(
            observed_at_text.replace("Z", "+00:00")
        )
        if observed_at.tzinfo is None:
            raise ValueError("observed_at must include a timezone")
        records = payload.get("records")
        cohorts = payload.get("opening_cohorts")
        if not isinstance(records, list) or not isinstance(cohorts, list):
            raise ValueError("records and opening_cohorts must be lists")
        person_ids = self._person_ids_by_canonical_key(
            [
                row.get("canonical_key")
                for row in records
                if isinstance(row, dict)
            ]
            + [
                key
                for cohort in cohorts
                if isinstance(cohort, dict)
                for key in cohort.get("canonical_keys") or []
            ]
        )
        accepted = 0
        quarantined = 0
        event_ids: list[str] = []
        for position, record in enumerate(records, start=1):
            if not isinstance(record, dict):
                raise ValueError(f"record {position} must be an object")
            canonical_key = _normalise(record.get("canonical_key"))
            person_id = person_ids.get(canonical_key)
            if not person_id:
                raise ValueError(
                    f"record {position} canonical_key is not in the Hub"
                )
            event_type = _normalise(record.get("event_type")).replace(" ", "_")
            if event_type not in {
                "membership_ended",
                "downgrade_only",
                "hold_approved",
            }:
                raise ValueError(f"record {position} has invalid event_type")
            confidence = _normalise(record.get("confidence"))
            if confidence not in {
                "verified",
                "high",
                "medium",
                "low",
                "legacy_aggregate",
                "unresolved",
            }:
                raise ValueError(f"record {position} has invalid confidence")
            effective_date = _date(
                record.get("effective_date"),
                f"record {position} effective_date",
            )
            ambiguous = bool(record.get("ambiguous_date"))
            accepted_state = (
                "accepted"
                if effective_date
                and not ambiguous
                and confidence in ACCEPTED_METRIC_CONFIDENCE
                else "quarantined"
            )
            occurred_at = (
                _local_midnight(effective_date)
                if effective_date
                else observed_at
            )
            result = self.reporting_v2.accept_source_event(
                {
                    "source_system": "historical_backfill",
                    "source_object_type": "membership_lifecycle_event",
                    "source_event_id": str(
                        record.get("source_record_id")
                        or f"{source_run_id}:{position}"
                    ),
                    "source_object_id": person_id,
                    "occurred_at": occurred_at,
                    "effective_at": (
                        _local_midnight(effective_date)
                        if effective_date
                        else None
                    ),
                    "observed_at": observed_at,
                    "source_run_id": source_run_id,
                    "confidence": confidence,
                    "acceptance_state": accepted_state,
                    "rejection_reason": (
                        None
                        if accepted_state == "accepted"
                        else (
                            "historical effective date or evidence confidence "
                            "is insufficient"
                        )
                    ),
                    "payload": {
                        **record,
                        "person_id": person_id,
                        "event_type": event_type,
                        "effective_date": (
                            effective_date.isoformat()
                            if effective_date
                            else None
                        ),
                        "contract_version": LIFECYCLE_CONTRACT_VERSION,
                    },
                }
            )
            accepted += (
                result["status"] == "accepted"
                and accepted_state == "accepted"
            )
            quarantined += (
                result["status"] == "accepted"
                and accepted_state == "quarantined"
            )
            event_ids.append(result["event_version_id"])

        for position, cohort in enumerate(cohorts, start=1):
            if not isinstance(cohort, dict):
                raise ValueError(f"opening cohort {position} must be an object")
            cohort_date = _date(
                cohort.get("as_of_date"),
                f"opening cohort {position} as_of_date",
            )
            if cohort_date is None:
                raise ValueError(
                    f"opening cohort {position} requires as_of_date"
                )
            confidence = _normalise(cohort.get("confidence"))
            canonical_keys = [
                _normalise(key) for key in cohort.get("canonical_keys") or []
            ]
            unresolved_keys = [
                key for key in canonical_keys if key not in person_ids
            ]
            coverage_complete = bool(cohort.get("coverage_complete"))
            accepted_state = (
                "accepted"
                if coverage_complete
                and not unresolved_keys
                and confidence in ACCEPTED_METRIC_CONFIDENCE
                else "quarantined"
            )
            member_ids = sorted(
                {
                    person_ids[key]
                    for key in canonical_keys
                    if key in person_ids
                }
            )
            result = self.reporting_v2.accept_source_event(
                {
                    "source_system": "historical_backfill",
                    "source_object_type": "membership_opening_cohort",
                    "source_event_id": str(
                        cohort.get("source_record_id")
                        or f"{source_run_id}:cohort:{cohort_date.isoformat()}"
                    ),
                    "occurred_at": _local_midnight(cohort_date),
                    "effective_at": _local_midnight(cohort_date),
                    "observed_at": observed_at,
                    "source_run_id": source_run_id,
                    "confidence": confidence,
                    "acceptance_state": accepted_state,
                    "rejection_reason": (
                        None
                        if accepted_state == "accepted"
                        else (
                            "opening cohort is incomplete, unresolved or below "
                            "the accepted confidence threshold"
                        )
                    ),
                    "payload": {
                        "as_of_date": cohort_date.isoformat(),
                        "person_ids": member_ids,
                        "coverage_complete": coverage_complete,
                        "unresolved_canonical_keys": unresolved_keys,
                        "evidence": cohort.get("evidence") or {},
                        "contract_version": LIFECYCLE_CONTRACT_VERSION,
                    },
                }
            )
            accepted += (
                result["status"] == "accepted"
                and accepted_state == "accepted"
            )
            quarantined += (
                result["status"] == "accepted"
                and accepted_state == "quarantined"
            )
            event_ids.append(result["event_version_id"])
        return {
            "contract_version": LIFECYCLE_CONTRACT_VERSION,
            "mode": "shadow",
            "publication_impact": "none",
            "accepted_event_versions": accepted,
            "quarantined_event_versions": quarantined,
            "event_version_ids": sorted(set(event_ids)),
        }

    def _canonicalise_sale_people(
        self,
        sales: list[Any],
    ) -> dict[str, str]:
        source_event_ids = {
            str(row["source_event_version_id"])
            for row in sales
            if row["source_event_version_id"]
        }
        with self.engine.begin() as connection:
            event_rows = connection.execute(
                select(
                    source_events.c.event_version_id,
                    source_events.c.payload_json,
                ).where(
                    source_events.c.event_version_id.in_(source_event_ids)
                )
            ).mappings().all()
        event_payloads = {
            str(row["event_version_id"]): json.loads(row["payload_json"])
            for row in event_rows
        }
        raw_by_sale = {}
        for row in sales:
            event_payload = event_payloads.get(
                str(row["source_event_version_id"]), {}
            )
            raw_id = str(
                row["person_id"]
                or event_payload.get("person_id")
                or event_payload.get("contact_id")
                or ""
            ).strip()
            if raw_id:
                raw_by_sale[str(row["sale_id"])] = raw_id
        raw_ids = set(raw_by_sale.values())
        if not raw_ids:
            return {}
        with self.engine.begin() as connection:
            rows = connection.execute(
                select(
                    source_identities.c.source_record_id,
                    source_identities.c.person_id,
                ).where(
                    source_identities.c.source == "ghl",
                    source_identities.c.source_record_id.in_(raw_ids),
                )
            ).mappings().all()
        mapped = {
            str(row["source_record_id"]): str(row["person_id"])
            for row in rows
        }
        return {
            sale_id: mapped.get(raw_id, raw_id)
            for sale_id, raw_id in raw_by_sale.items()
        }

    def _opening_cohort(
        self,
        cohort_rows: list[Any],
        lifecycle_rows: list[Any],
        *,
        period_start: date,
    ) -> dict[str, Any]:
        eligible = []
        for row in cohort_rows:
            if row["acceptance_state"] != "accepted":
                continue
            payload = json.loads(row["payload_json"])
            cohort_date = _date(payload.get("as_of_date"), "as_of_date")
            if (
                cohort_date
                and cohort_date == period_start
                and payload.get("coverage_complete")
                and row["confidence"] in ACCEPTED_METRIC_CONFIDENCE
            ):
                eligible.append((cohort_date, row, payload))
        if not eligible:
            return {
                "available": False,
                "member_ids": set(),
                "event_version_ids": [],
                "blocked_reason": (
                    "No complete verified or high-confidence opening cohort "
                    "exists on the exact period start."
                ),
            }
        cohort_date, cohort_row, payload = max(
            eligible, key=lambda item: item[0]
        )
        member_ids = set(payload.get("person_ids") or [])
        lineage = [str(cohort_row["event_version_id"])]
        return {
            "available": True,
            "member_ids": member_ids,
            "event_version_ids": lineage,
            "source_cohort_date": cohort_date.isoformat(),
            "blocked_reason": None,
        }

    def preview(
        self,
        period_id: str,
        *,
        as_of: datetime | str | None = None,
    ) -> dict[str, Any]:
        if period_id not in {"week", "28d", "90d"}:
            raise ValueError("period must be week, 28d or 90d")
        instant = (
            datetime.fromisoformat(as_of.replace("Z", "+00:00"))
            if isinstance(as_of, str)
            else as_of
        ) or datetime.now(UTC)
        if instant.tzinfo is None:
            raise ValueError("as_of must include a timezone")
        period_start, period_end = completed_reporting_periods(instant)[
            period_id
        ]
        with self.engine.begin() as connection:
            lifecycle_rows = _latest_versions(
                connection.execute(
                    select(source_events)
                    .where(
                        source_events.c.source_object_type
                        == "membership_lifecycle_event"
                    )
                    .order_by(source_events.c.accepted_at.desc())
                ).mappings().all()
            )
            state_rows = _latest_versions(
                connection.execute(
                    select(source_events)
                    .where(
                        source_events.c.source_object_type
                        == "membership_lifecycle_state"
                    )
                    .order_by(source_events.c.accepted_at.desc())
                ).mappings().all()
            )
            cohort_rows = _latest_versions(
                connection.execute(
                    select(source_events)
                    .where(
                        source_events.c.source_object_type
                        == "membership_opening_cohort"
                    )
                    .order_by(source_events.c.accepted_at.desc())
                ).mappings().all()
            )
            sales = connection.execute(
                select(sale_events).where(
                    sale_events.c.qualifying_new_membership == 1,
                    sale_events.c.brisbane_local_date
                    >= period_start.isoformat(),
                    sale_events.c.brisbane_local_date
                    <= period_end.isoformat(),
                    sale_events.c.confidence.in_(
                        sorted(ACCEPTED_METRIC_CONFIDENCE)
                    ),
                )
            ).mappings().all()

        sale_people = self._canonicalise_sale_people(sales)
        joined_people = {
            sale_people[str(row["sale_id"])]
            for row in sales
            if str(row["sale_id"]) in sale_people
        }
        joined_lineage = {
            str(row["source_event_version_id"])
            for row in sales
            if str(row["sale_id"]) in sale_people
            and row["source_event_version_id"]
        }
        events_in_period: list[tuple[Any, dict[str, Any]]] = []
        unresolved_in_period = 0
        for row in lifecycle_rows:
            payload = json.loads(row["payload_json"])
            event_date = _date(payload.get("effective_date"), "effective_date")
            if event_date is None or not period_start <= event_date <= period_end:
                continue
            if (
                row["acceptance_state"] != "accepted"
                or row["confidence"] not in ACCEPTED_METRIC_CONFIDENCE
            ):
                unresolved_in_period += 1
                continue
            events_in_period.append((row, payload))
        ended_people = {
            str(payload["person_id"])
            for _, payload in events_in_period
            if payload.get("event_type") == "membership_ended"
        }
        straight_people = {
            str(payload["person_id"])
            for _, payload in events_in_period
            if payload.get("event_type") == "membership_ended"
            and payload.get("transition_kind") == "straight_cancellation"
        }
        downgrade_people = {
            str(payload["person_id"])
            for _, payload in events_in_period
            if payload.get("event_type") == "downgrade_only"
        }
        hold_people = {
            str(payload["person_id"])
            for _, payload in events_in_period
            if payload.get("event_type") == "hold_approved"
        }
        local_as_of = instant.astimezone(BRISBANE_TZ).date()
        active_notice_people: set[str] = set()
        active_notice_downgrades: set[str] = set()
        missing_notice_dates = 0
        active_hold_people: set[str] = set()
        for row in state_rows:
            if row["acceptance_state"] != "accepted":
                continue
            payload = json.loads(row["payload_json"])
            final_access = _date(
                payload.get("final_access_date"), "final_access_date"
            )
            notice_status = _normalise(payload.get("cancellation_status"))
            lifecycle_status = _normalise(payload.get("lifecycle_status"))
            is_notice = (
                lifecycle_status == "cancelling"
                or notice_status in {"notice active", "cancelling"}
            )
            if is_notice:
                if final_access is None:
                    missing_notice_dates += 1
                elif final_access >= local_as_of:
                    person_id = str(payload["person_id"])
                    active_notice_people.add(person_id)
                    services = set(payload.get("services") or [])
                    if (
                        _normalise(payload.get("cancellation_type")) == "pt"
                        and bool({"sgpt", "fast_track"} & services)
                    ):
                        active_notice_downgrades.add(person_id)
            hold_start = _date(payload.get("hold_start_date"), "hold_start_date")
            hold_end = _date(payload.get("hold_end_date"), "hold_end_date")
            if (
                _normalise(payload.get("hold_status")) in OPEN_HOLD_STATUSES
                and hold_start
                and hold_end
                and hold_start <= local_as_of <= hold_end
            ):
                active_hold_people.add(str(payload["person_id"]))

        opening = self._opening_cohort(
            cohort_rows,
            lifecycle_rows,
            period_start=period_start,
        )
        opening_count = len(opening["member_ids"])
        attrition_available = opening["available"] and opening_count > 0
        attrition = (
            Decimal(len(ended_people)) / Decimal(opening_count)
            if attrition_available
            else None
        )
        event_lineage_by_type: dict[str, set[str]] = {}
        for row, payload in events_in_period:
            event_lineage_by_type.setdefault(
                str(payload.get("event_type")), set()
            ).add(str(row["event_version_id"]))
        metric_values = {
            "members_joined": (len(joined_people), joined_lineage),
            "final_membership_endings": (
                len(ended_people),
                event_lineage_by_type.get("membership_ended", set()),
            ),
            "straight_cancellations": (
                len(straight_people),
                event_lineage_by_type.get("membership_ended", set()),
            ),
            "downgrade_only_transitions": (
                len(downgrade_people),
                event_lineage_by_type.get("downgrade_only", set()),
            ),
            "approved_holds": (
                len(hold_people),
                event_lineage_by_type.get("hold_approved", set()),
            ),
            "net_unique_member_growth": (
                len(joined_people) - len(ended_people),
                joined_lineage
                | event_lineage_by_type.get("membership_ended", set()),
            ),
        }
        observations: dict[str, Any] = {}
        for metric_id, (value, lineage) in metric_values.items():
            observations[metric_id] = (
                self.reporting_v2.record_metric_observation(
                    metric_id=metric_id,
                    definition_version=LIFECYCLE_CONTRACT_VERSION,
                    period_start=period_start.isoformat(),
                    period_end=period_end.isoformat(),
                    value=value,
                    numerator=value,
                    denominator=None,
                    unit="people",
                    confidence=(
                        "high" if unresolved_in_period == 0 else "medium"
                    ),
                    event_version_ids=lineage,
                    publication_state="shadow",
                )
            )
        observations["membership_attrition_rate"] = (
            self.reporting_v2.record_metric_observation(
                metric_id="membership_attrition_rate",
                definition_version=LIFECYCLE_CONTRACT_VERSION,
                period_start=period_start.isoformat(),
                period_end=period_end.isoformat(),
                value=attrition,
                numerator=len(ended_people) if attrition_available else None,
                denominator=opening_count if attrition_available else None,
                unit="ratio",
                confidence="high" if attrition_available else "unresolved",
                event_version_ids=(
                    set(opening["event_version_ids"])
                    | event_lineage_by_type.get("membership_ended", set())
                ),
                publication_state="shadow",
                unavailable_reason=(
                    None
                    if attrition_available
                    else opening["blocked_reason"]
                    or "Opening cohort is empty."
                ),
            )
        )
        blocked_reasons = []
        if not attrition_available:
            blocked_reasons.append(
                opening["blocked_reason"] or "Opening cohort is empty."
            )
        if unresolved_in_period:
            blocked_reasons.append(
                f"{unresolved_in_period} lifecycle event(s) in the period "
                "remain quarantined or below high confidence."
            )
        if missing_notice_dates:
            blocked_reasons.append(
                f"{missing_notice_dates} active notice state(s) lack an exact "
                "final access date."
            )
        return {
            "schema_version": 1,
            "contract_version": LIFECYCLE_CONTRACT_VERSION,
            "mode": "shadow",
            "publication_impact": "none",
            "period": {
                "id": period_id,
                "start": period_start.isoformat(),
                "end": period_end.isoformat(),
                "timezone": "Australia/Brisbane",
            },
            "as_of": instant.astimezone(UTC).isoformat(),
            "complete": not blocked_reasons,
            "blocked_reasons": blocked_reasons,
            "members_joined": len(joined_people),
            "final_membership_endings": len(ended_people),
            "straight_cancellations": len(straight_people),
            "downgrade_only_transitions": len(downgrade_people),
            "approved_holds": len(hold_people),
            "active_notice": {
                "unique_people": len(active_notice_people),
                "straight_cancellation": len(
                    active_notice_people - active_notice_downgrades
                ),
                "downgrade_only": len(active_notice_downgrades),
                "missing_final_access_date": missing_notice_dates,
            },
            "active_approved_holds": len(active_hold_people),
            "opening_cohort": {
                "available": opening["available"],
                "unique_people": opening_count if opening["available"] else None,
                "source_cohort_date": opening.get("source_cohort_date"),
            },
            "attrition_rate": (
                format(attrition, "f") if attrition is not None else None
            ),
            "net_unique_member_growth": (
                len(joined_people) - len(ended_people)
            ),
            "confidence": (
                "high" if not blocked_reasons else "unresolved"
            ),
            "metric_observations": observations,
            "acceptance": {
                "cutover_authorised": False,
                "legacy_reporting_unchanged": True,
                "requires_parallel_comparison": True,
            },
        }
