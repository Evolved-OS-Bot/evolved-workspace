from datetime import UTC, date, datetime

from operating_data_hub.website_analytics import (
    _metric_counts,
    build_website_marketing_snapshot,
    normalise_subscriber_submission,
    subscriber_assessment_booking_periods,
    unique_subscribers,
)


class FakeReader:
    property_id = "429372468"

    def __init__(self):
        self.calls = []

    def period_totals(self, period_start, period_end):
        self.calls.append((period_start, period_end))
        return {
            "page_views": 120,
            "visitors": 40,
            "sessions": 55,
        }


def _submission(submission_id, contact_id, submitted_at):
    return normalise_subscriber_submission(
        {
            "id": submission_id,
            "contactId": contact_id,
            "createdAt": submitted_at,
        },
        form_id="qB8xGGwhLdSGtbc3Z0EJ",
    )


def test_subscribers_are_unique_people_not_submission_count():
    rows = [
        _submission("s-2", "contact-1", "2026-08-04T10:00:00+10:00"),
        _submission("s-1", "contact-1", "2026-08-03T10:00:00+10:00"),
        _submission("s-3", "contact-2", "2026-08-05T10:00:00+10:00"),
    ]

    result = unique_subscribers(rows)

    assert [row["submission_id"] for row in result] == ["s-1", "s-3"]


def test_full_coverage_period_publishes_traffic_and_conversion():
    reader = FakeReader()
    snapshot = build_website_marketing_snapshot(
        reader=reader,
        subscriber_submissions=[
            _submission(
                "s-1",
                "contact-1",
                "2026-08-05T10:00:00+10:00",
            )
        ],
        analytics_started_on=date(2026, 8, 2),
        observed_at=datetime(2026, 8, 10, 1, tzinfo=UTC),
    )

    week = snapshot["periods"]["week"]
    assert week["coverage_complete"] is True
    assert week["page_views"] == 120
    assert week["visitors"] == 40
    assert week["new_subscribers"] == 1
    assert week["visitor_to_subscriber_rate"] == 0.025


def test_pre_connection_period_is_unavailable_not_zero():
    reader = FakeReader()
    snapshot = build_website_marketing_snapshot(
        reader=reader,
        subscriber_submissions=[],
        analytics_started_on=date(2026, 8, 2),
        observed_at=datetime(2026, 8, 2, 1, tzinfo=UTC),
    )

    for period in snapshot["periods"].values():
        assert period["coverage_state"] == "not_started"
        assert period["page_views"] is None
        assert period["visitors"] is None
        assert period["visitor_to_subscriber_rate"] is None
    assert reader.calls == []


def test_ga4_aggregate_result_row_is_not_treated_as_zero():
    assert _metric_counts(
        {
            "rows": [
                {
                    "metricValues": [
                        {"value": "652"},
                        {"value": "280"},
                        {"value": "410"},
                    ]
                }
            ]
        }
    ) == [652, 280, 410]


def test_subscriber_to_assessment_is_unique_and_time_bounded():
    result = subscriber_assessment_booking_periods(
        subscriber_submissions=[
            _submission(
                "s-1", "contact-1", "2026-08-04T09:00:00+10:00"
            ),
            _submission(
                "s-2", "contact-1", "2026-08-05T09:00:00+10:00"
            ),
            _submission(
                "s-3", "contact-2", "2026-08-04T10:00:00+10:00"
            ),
        ],
        assessment_appointments=[
            {
                "appointment_id": "a-1",
                "contact_id": "contact-1",
                "booked_at": "2026-08-05T10:00:00+10:00",
                "status": "cancelled",
                "deleted": False,
            },
            {
                "appointment_id": "a-2",
                "contact_id": "contact-1",
                "booked_at": "2026-08-06T10:00:00+10:00",
                "status": "confirmed",
                "deleted": False,
            },
            {
                "appointment_id": "a-before-subscription",
                "contact_id": "contact-2",
                "booked_at": "2026-08-03T10:00:00+10:00",
                "status": "showed",
                "deleted": False,
            },
            {
                "appointment_id": "a-invalid",
                "contact_id": "contact-2",
                "booked_at": "2026-08-05T10:00:00+10:00",
                "status": "invalid",
                "deleted": False,
            },
        ],
        observed_at="2026-08-10T01:00:00Z",
    )

    week = result["periods"]["week"]
    assert week["new_subscribers"] == 2
    assert week["subscribers_booking_assessment"] == 1
    assert week["subscriber_to_assessment_rate"] == 0.5
    assert len(result["matches"]) == 1
    assert result["matches"][0]["appointment_id"] == "a-1"


def test_deleted_and_late_assessment_bookings_do_not_convert():
    result = subscriber_assessment_booking_periods(
        subscriber_submissions=[
            _submission(
                "s-1", "contact-1", "2026-08-04T09:00:00+10:00"
            )
        ],
        assessment_appointments=[
            {
                "appointment_id": "a-deleted",
                "contact_id": "contact-1",
                "booked_at": "2026-08-05T10:00:00+10:00",
                "status": "confirmed",
                "deleted": True,
            },
            {
                "appointment_id": "a-late",
                "contact_id": "contact-1",
                "booked_at": "2026-09-10T10:00:00+10:00",
                "status": "confirmed",
                "deleted": False,
            },
        ],
        observed_at="2026-08-10T01:00:00Z",
    )

    assert result["periods"]["week"][
        "subscribers_booking_assessment"
    ] == 0
