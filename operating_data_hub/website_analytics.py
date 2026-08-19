from __future__ import annotations

import json
from datetime import UTC, date, datetime, timedelta
from typing import Any

from google.oauth2 import service_account
from googleapiclient.discovery import build

from .config import BRISBANE_TZ
from .reporting_v2 import completed_reporting_periods


ANALYTICS_SCOPE = "https://www.googleapis.com/auth/analytics.readonly"
OWNED_WEBSITE_HOST = "theevolvedgym.com.au"
SUBSCRIBER_BOOKING_WINDOW_DAYS = 30
CUTOVER_CHECKPOINT_DAYS = (7, 14, 28)
BOOKING_EVIDENCE_STATUSES = {
    "confirmed",
    "showed",
    "no_show",
    "cancelled",
}


def website_v2_cutover_periods(
    reporting_start: date | None,
    observed_at: datetime | str,
) -> dict[str, tuple[date, date]]:
    """Return only exact cutover windows that have fully completed.

    ``reporting_start`` is the first full Brisbane calendar date after the
    approved root cutover. Leaving it unset keeps normal reporting unchanged.
    """
    if reporting_start is None:
        return {}
    observed = _iso_datetime(observed_at, "observed_at")
    completed_through = (
        observed.astimezone(BRISBANE_TZ).date() - timedelta(days=1)
    )
    periods: dict[str, tuple[date, date]] = {}
    for days in CUTOVER_CHECKPOINT_DAYS:
        period_end = reporting_start + timedelta(days=days - 1)
        if period_end <= completed_through:
            periods[f"website_v2_{days}d"] = (
                reporting_start,
                period_end,
            )
    return periods


def _reporting_periods(
    observed_at: datetime,
    additional_periods: dict[str, tuple[date, date]] | None,
) -> dict[str, tuple[date, date]]:
    periods = dict(completed_reporting_periods(observed_at))
    for period_id, bounds in (additional_periods or {}).items():
        if period_id in periods:
            raise ValueError(f"duplicate reporting period: {period_id}")
        period_start, period_end = bounds
        if period_start > period_end:
            raise ValueError(f"invalid reporting period: {period_id}")
        periods[period_id] = bounds
    return periods


def _metric_counts(response: dict[str, Any]) -> list[int]:
    totals = response.get("totals") or []
    rows = response.get("rows") or []
    values = []
    if totals:
        values = totals[0].get("metricValues") or []
    elif rows:
        # A no-dimension GA4 report can return its aggregate as the
        # single result row even when a totals row is omitted.
        values = rows[0].get("metricValues") or []
    parsed = [
        int(float(str(row.get("value") or "0")))
        for row in values
    ]
    parsed.extend([0] * (3 - len(parsed)))
    return parsed


def _iso_datetime(value: Any, field: str) -> datetime:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{field} is required")
    parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=BRISBANE_TZ)
    return parsed.astimezone(UTC)


def normalise_subscriber_submission(
    raw: dict[str, Any],
    *,
    form_id: str,
) -> dict[str, Any]:
    submission_id = str(raw.get("id") or "").strip()
    contact_id = str(raw.get("contactId") or "").strip()
    if not submission_id or not contact_id:
        raise ValueError("subscriber submission identity is incomplete")
    submitted_at = _iso_datetime(
        raw.get("createdAt")
        or raw.get("submittedAt")
        or raw.get("dateAdded"),
        "subscriber submitted_at",
    )
    return {
        "source_event_id": f"website-subscriber:{form_id}:{submission_id}",
        "source_object_id": submission_id,
        "submission_id": submission_id,
        "form_id": form_id,
        "contact_id": contact_id,
        "submitted_at": submitted_at.isoformat(),
        "brisbane_local_date": (
            submitted_at.astimezone(BRISBANE_TZ).date().isoformat()
        ),
    }


def unique_subscribers(
    submissions: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    first_by_contact: dict[str, dict[str, Any]] = {}
    for row in submissions:
        contact_id = str(row.get("contact_id") or "").strip()
        if not contact_id:
            continue
        current = first_by_contact.get(contact_id)
        if current is None or str(row["submitted_at"]) < str(
            current["submitted_at"]
        ):
            first_by_contact[contact_id] = row
    return sorted(
        first_by_contact.values(),
        key=lambda row: (
            row["submitted_at"],
            row["contact_id"],
        ),
    )


def subscriber_assessment_booking_periods(
    *,
    subscriber_submissions: list[dict[str, Any]],
    assessment_appointments: list[dict[str, Any]],
    observed_at: datetime | str,
    additional_periods: dict[str, tuple[date, date]] | None = None,
) -> dict[str, Any]:
    observed = _iso_datetime(observed_at, "observed_at")
    subscribers = unique_subscribers(subscriber_submissions)
    appointments_by_contact: dict[str, list[dict[str, Any]]] = {}
    missing_booking_timestamp = 0
    for appointment in assessment_appointments:
        contact_id = str(appointment.get("contact_id") or "").strip()
        appointment_id = str(
            appointment.get("appointment_id") or ""
        ).strip()
        status = str(appointment.get("status") or "").strip().lower()
        if (
            not contact_id
            or not appointment_id
            or bool(appointment.get("deleted"))
            or status not in BOOKING_EVIDENCE_STATUSES
        ):
            continue
        booked_at = appointment.get("booked_at")
        if not booked_at:
            missing_booking_timestamp += 1
            continue
        appointments_by_contact.setdefault(contact_id, []).append(
            {
                "appointment_id": appointment_id,
                "booked_at": _iso_datetime(
                    booked_at, "assessment booked_at"
                ),
                "status": status,
            }
        )
    for rows in appointments_by_contact.values():
        rows.sort(key=lambda row: (row["booked_at"], row["appointment_id"]))

    matched_by_contact: dict[str, dict[str, Any]] = {}
    for subscriber in subscribers:
        contact_id = subscriber["contact_id"]
        submitted_at = _iso_datetime(
            subscriber["submitted_at"], "subscriber submitted_at"
        )
        booking_deadline = submitted_at + timedelta(
            days=SUBSCRIBER_BOOKING_WINDOW_DAYS
        )
        qualifying = [
            appointment
            for appointment in appointments_by_contact.get(contact_id, [])
            if submitted_at
            <= appointment["booked_at"]
            <= booking_deadline
        ]
        if qualifying:
            matched_by_contact[contact_id] = {
                "contact_id": contact_id,
                "submission_id": subscriber["submission_id"],
                "submitted_at": subscriber["submitted_at"],
                "appointment_id": qualifying[0]["appointment_id"],
                "booked_at": qualifying[0]["booked_at"].isoformat(),
                "days_to_booking": (
                    qualifying[0]["booked_at"] - submitted_at
                ).total_seconds()
                / 86400,
            }

    periods: dict[str, dict[str, Any]] = {}
    for period_id, (period_start, period_end) in _reporting_periods(
        observed, additional_periods
    ).items():
        selected = [
            subscriber
            for subscriber in subscribers
            if period_start
            <= date.fromisoformat(subscriber["brisbane_local_date"])
            <= period_end
        ]
        matched = [
            subscriber
            for subscriber in selected
            if subscriber["contact_id"] in matched_by_contact
        ]
        open_window = sum(
            _iso_datetime(
                subscriber["submitted_at"], "subscriber submitted_at"
            )
            + timedelta(days=SUBSCRIBER_BOOKING_WINDOW_DAYS)
            > observed
            for subscriber in selected
        )
        periods[period_id] = {
            "period_start": period_start.isoformat(),
            "period_end": period_end.isoformat(),
            "new_subscribers": len(selected),
            "subscribers_booking_assessment": len(matched),
            "subscriber_to_assessment_rate": (
                len(matched) / len(selected) if selected else None
            ),
            "open_booking_window": open_window,
            "booking_window_days": SUBSCRIBER_BOOKING_WINDOW_DAYS,
        }
    return {
        "definition_version": "ghl-subscriber-sa-booking-v1",
        "observed_at": observed.isoformat(),
        "periods": periods,
        "summary": {
            "unique_subscribers": len(subscribers),
            "matched_subscribers": len(matched_by_contact),
            "appointments_missing_booking_timestamp": (
                missing_booking_timestamp
            ),
        },
        "matches": sorted(
            matched_by_contact.values(),
            key=lambda row: (row["submitted_at"], row["contact_id"]),
        ),
    }


class GA4WebsiteReader:
    def __init__(
        self,
        service_account_json: str,
        property_id: str,
    ):
        if not service_account_json.strip():
            raise RuntimeError(
                "GOOGLE_SERVICE_ACCOUNT_JSON is required for website analytics"
            )
        if not property_id.strip().isdigit():
            raise RuntimeError("GA4_PROPERTY_ID must be a numeric property ID")
        credentials = service_account.Credentials.from_service_account_info(
            json.loads(service_account_json),
            scopes=[ANALYTICS_SCOPE],
        )
        self.property_id = property_id.strip()
        self.client = build(
            "analyticsdata",
            "v1beta",
            credentials=credentials,
            cache_discovery=False,
        )

    def period_totals(
        self,
        period_start: date,
        period_end: date,
    ) -> dict[str, int]:
        response = (
            self.client.properties()
            .runReport(
                property=f"properties/{self.property_id}",
                body={
                    "dateRanges": [
                        {
                            "startDate": period_start.isoformat(),
                            "endDate": period_end.isoformat(),
                        }
                    ],
                    "metrics": [
                        {"name": "screenPageViews"},
                        {"name": "activeUsers"},
                        {"name": "sessions"},
                    ],
                    "metricAggregations": ["TOTAL"],
                    "dimensionFilter": {
                        "filter": {
                            "fieldName": "hostName",
                            "stringFilter": {
                                "matchType": "EXACT",
                                "value": OWNED_WEBSITE_HOST,
                                "caseSensitive": False,
                            },
                        }
                    },
                    "keepEmptyRows": True,
                },
            )
            .execute()
        )
        parsed = _metric_counts(response)
        return {
            "page_views": parsed[0],
            "visitors": parsed[1],
            "sessions": parsed[2],
        }


def build_website_marketing_snapshot(
    *,
    reader: GA4WebsiteReader,
    subscriber_submissions: list[dict[str, Any]],
    analytics_started_on: date,
    observed_at: datetime | str,
    additional_periods: dict[str, tuple[date, date]] | None = None,
) -> dict[str, Any]:
    observed = _iso_datetime(observed_at, "observed_at")
    subscribers = unique_subscribers(subscriber_submissions)
    periods: dict[str, dict[str, Any]] = {}
    for period_id, (period_start, period_end) in _reporting_periods(
        observed, additional_periods
    ).items():
        selected_subscribers = [
            row
            for row in subscribers
            if period_start
            <= date.fromisoformat(row["brisbane_local_date"])
            <= period_end
        ]
        coverage_complete = period_start >= analytics_started_on
        coverage_started = period_end >= analytics_started_on
        if coverage_started:
            query_start = max(period_start, analytics_started_on)
            traffic = reader.period_totals(query_start, period_end)
        else:
            traffic = {
                "page_views": None,
                "visitors": None,
                "sessions": None,
            }
        visitors = traffic["visitors"]
        periods[period_id] = {
            "period_start": period_start.isoformat(),
            "period_end": period_end.isoformat(),
            "analytics_started_on": analytics_started_on.isoformat(),
            "coverage_complete": coverage_complete,
            "coverage_state": (
                "complete"
                if coverage_complete
                else "partial"
                if coverage_started
                else "not_started"
            ),
            "page_views": (
                traffic["page_views"] if coverage_complete else None
            ),
            "visitors": visitors if coverage_complete else None,
            "sessions": (
                traffic["sessions"] if coverage_complete else None
            ),
            "new_subscribers": len(selected_subscribers),
            "visitor_to_subscriber_rate": (
                len(selected_subscribers) / visitors
                if coverage_complete and visitors
                else None
            ),
            "unavailable_reason": (
                None
                if coverage_complete
                else (
                    "Owned website analytics began on "
                    f"{analytics_started_on.strftime('%-d %b %Y')}; "
                    "this completed period does not have full coverage."
                )
            ),
        }
    return {
        "schema_version": 1,
        "source": "website_analytics_v2",
        "observed_at": observed.isoformat(),
        "status": "complete",
        "complete": True,
        "property_id": reader.property_id,
        "host_name": OWNED_WEBSITE_HOST,
        "analytics_started_on": analytics_started_on.isoformat(),
        "subscriber_definition": {
            "grain": "unique GHL contact",
            "deduplication": "earliest accepted submission per contact",
        },
        "periods": periods,
        "summary": {
            "subscriber_submissions": len(subscriber_submissions),
            "unique_subscribers": len(subscribers),
        },
    }
