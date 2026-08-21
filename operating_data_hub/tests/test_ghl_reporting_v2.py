from datetime import datetime

from operating_data_hub.ghl_reporting_v2 import (
    MEMBERSHIP_AGREEMENT_DATE_FIELD_ID,
    MEMBERSHIP_TYPE_FIELD_ID,
    ONBOARDING_CALENDARS,
    PT_AGREEMENT_DATE_FIELD_ID,
    WARM_PIPELINE_ID,
    WARM_STAGE_PREQUALIFIED,
    build_ghl_acquisition_snapshot,
    link_sales_to_onboarding,
    normalise_onboarding_event,
    summarise_onboarding_cases,
)


def field(field_id, value):
    return {"id": field_id, "value": value}


def attendance(contact_id="contact-1"):
    return {
        "appointment_id": "appointment-1",
        "appointment_series_id": "series-1",
        "contact_id": contact_id,
        "canonical_status": "showed",
        "start_at": "2026-07-10T01:00:00+00:00",
        "end_at": "2026-07-10T02:00:00+00:00",
    }


def test_snapshot_builds_lead_prequalification_and_fast_track_sale():
    snapshot = build_ghl_acquisition_snapshot(
        contacts=[
            {
                "id": "contact-1",
                "dateAdded": "2026-07-01T00:00:00Z",
                "source": "Paid Social - Meta",
                "customFields": [
                    field(
                        MEMBERSHIP_AGREEMENT_DATE_FIELD_ID,
                        "2026-07-20",
                    ),
                    field(MEMBERSHIP_TYPE_FIELD_ID, "Fast Track Package"),
                ],
                "tags": [],
            }
        ],
        opportunities=[
            {
                "id": "opportunity-1",
                "contactId": "contact-1",
                "pipelineId": WARM_PIPELINE_ID,
                "pipelineStageId": WARM_STAGE_PREQUALIFIED,
                "status": "won",
                "updatedAt": "2026-07-09T00:00:00Z",
            }
        ],
        attendance_rows=[attendance()],
        observed_at="2026-07-30T00:00:00Z",
    )

    assert snapshot["summary"]["leads"] == 1
    assert snapshot["summary"]["prequalification_eligible"] == 1
    assert snapshot["summary"]["prequalified"] == 1
    assert snapshot["summary"]["prequalification_completion_rate"] == 1
    assert snapshot["summary"]["sales"] == 1
    assert snapshot["summary"]["attributed_sales"] == 1
    sale = snapshot["sales"][0]
    assert sale["appointment_series_ids"] == ["series-1"]
    assert [
        item["service_type"] for item in sale["service_components"]
    ] == ["sgpt", "pt"]


def test_old_member_agreement_is_reactivation():
    snapshot = build_ghl_acquisition_snapshot(
        contacts=[
            {
                "id": "contact-1",
                "dateAdded": "2025-01-01T00:00:00Z",
                "customFields": [
                    field(
                        MEMBERSHIP_AGREEMENT_DATE_FIELD_ID,
                        "2026-07-20",
                    ),
                    field(MEMBERSHIP_TYPE_FIELD_ID, "Fast Track Package"),
                ],
                "tags": ["old member"],
            }
        ],
        opportunities=[],
        attendance_rows=[attendance()],
        observed_at="2026-07-30T00:00:00Z",
    )

    assert snapshot["summary"]["reactivations"] == 1
    assert snapshot["summary"]["attributed_sales"] == 0
    assert snapshot["sales"][0]["qualifying_new_membership"] is False


def test_week_ahead_counts_future_assessments_and_prequalification():
    contacts = [
        {
            "id": "contact-1",
            "name": "Ready Member",
            "customFields": [],
        },
        {
            "id": "contact-2",
            "firstName": "Needs",
            "lastName": "Prequalification",
            "customFields": [],
        },
    ]
    snapshot = build_ghl_acquisition_snapshot(
        contacts=contacts,
        opportunities=[
            {
                "id": "opportunity-1",
                "contactId": "contact-1",
                "pipelineId": WARM_PIPELINE_ID,
                "pipelineStageId": WARM_STAGE_PREQUALIFIED,
            }
        ],
        attendance_rows=[
            {
                "appointment_id": "future-ready",
                "contact_id": "contact-1",
                "canonical_status": "confirmed",
                "start_at": "2026-08-03T01:00:00+00:00",
                "end_at": "2026-08-03T02:00:00+00:00",
                "assigned_user_id": "coach-1",
            },
            {
                "appointment_id": "future-awaiting",
                "contact_id": "contact-2",
                "canonical_status": "confirmed",
                "start_at": "2026-08-04T01:00:00+00:00",
                "end_at": "2026-08-04T02:00:00+00:00",
            },
            {
                "appointment_id": "future-cancelled",
                "contact_id": "contact-2",
                "canonical_status": "cancelled",
                "start_at": "2026-08-05T01:00:00+00:00",
                "end_at": "2026-08-05T02:00:00+00:00",
            },
            attendance("contact-1"),
        ],
        observed_at="2026-08-01T00:00:00Z",
    )

    ahead = snapshot["week_ahead"]
    assert ahead["booked"] == 2
    assert ahead["prequalified"] == 1
    assert ahead["awaiting_prequalification"] == 1
    assert ahead["prequalification_rate"] == 0.5
    assert [
        (row["client_name"], row["prequalified"])
        for row in ahead["appointments"]
    ] == [
        ("Ready Member", True),
        ("Needs Prequalification", False),
    ]


def test_pt_agreement_is_not_duplicated_when_membership_agreement_exists():
    snapshot = build_ghl_acquisition_snapshot(
        contacts=[
            {
                "id": "contact-1",
                "dateAdded": "2026-07-01T00:00:00Z",
                "customFields": [
                    field(
                        MEMBERSHIP_AGREEMENT_DATE_FIELD_ID,
                        "2026-07-20",
                    ),
                    field(PT_AGREEMENT_DATE_FIELD_ID, "2026-07-20"),
                    field(MEMBERSHIP_TYPE_FIELD_ID, "Fast Track Package"),
                ],
            }
        ],
        opportunities=[],
        attendance_rows=[attendance()],
        observed_at="2026-07-30T00:00:00Z",
    )

    assert len(snapshot["sales"]) == 1
    assert snapshot["sales"][0]["sale_id"].startswith("ghl-membership:")


def test_unparseable_agreement_date_is_not_invented():
    snapshot = build_ghl_acquisition_snapshot(
        contacts=[
            {
                "id": "contact-1",
                "dateAdded": "2026-07-01T00:00:00Z",
                "customFields": [
                    field(
                        MEMBERSHIP_AGREEMENT_DATE_FIELD_ID,
                        "not-a-date",
                    )
                ],
            }
        ],
        opportunities=[],
        attendance_rows=[],
        observed_at="2026-07-30T00:00:00Z",
    )

    assert snapshot["sales"] == []


def test_onboarding_booking_is_linked_but_elapsed_confirmed_is_not_completed():
    calendar_id = next(iter(ONBOARDING_CALENDARS))
    raw = {
        "id": "onboarding-1",
        "contactId": "contact-1",
        "calendarId": calendar_id,
        "startTime": "2026-07-22T00:00:00Z",
        "endTime": "2026-07-22T00:30:00Z",
        "dateAdded": "2026-07-20T02:00:00Z",
        "appointmentStatus": "confirmed",
        "assignedUserId": "coach-1",
    }
    event = normalise_onboarding_event(raw)
    sales = [
        {
            "sale_id": "sale-1",
            "contact_id": "contact-1",
            "sold_at": "2026-07-20T02:00:00Z",
            "sale_type": "membership",
            "qualifying_new_membership": True,
            "evidence": {"membership_type": "Strong, Fit & Flexible"},
        }
    ]
    cases = link_sales_to_onboarding(
        sales,
        [event],
        observed_at=datetime.fromisoformat("2026-07-30T00:00:00+00:00"),
    )
    assert cases[0]["booking_days"] == 2
    assert cases[0]["completion_days"] is None
    assert cases[0]["completion_state"] == "elapsed_unverified"
    summary = summarise_onboarding_cases(cases)
    assert summary["average_sale_to_booking_days"] == 2
    assert summary["completion_tracking_available"] is False


def test_fit_and_flexible_is_excluded_from_onboarding_denominator():
    cases = link_sales_to_onboarding(
        [
            {
                "sale_id": "sale-1",
                "contact_id": "contact-1",
                "sold_at": "2026-07-20T02:00:00Z",
                "sale_type": "membership",
                "qualifying_new_membership": True,
                "evidence": {"membership_type": "Fit & Flexible"},
            }
        ],
        [],
        observed_at=datetime.fromisoformat("2026-07-30T00:00:00+00:00"),
    )
    assert cases == []


def test_fast_track_first_pt_session_is_a_valid_onboarding_booking():
    pt_calendar_id = next(
        calendar_id
        for calendar_id, appointment_type in ONBOARDING_CALENDARS.items()
        if appointment_type == "pt_session"
    )
    event = normalise_onboarding_event(
        {
            "id": "pt-1",
            "contactId": "contact-1",
            "calendarId": pt_calendar_id,
            "startTime": "2026-07-29T07:00:00Z",
            "endTime": "2026-07-29T07:30:00Z",
            "dateAdded": "2026-07-28T00:30:00Z",
            "appointmentStatus": "confirmed",
            "assignedUserId": "coach-1",
        }
    )
    cases = link_sales_to_onboarding(
        [
            {
                "sale_id": "sale-1",
                "contact_id": "contact-1",
                "sold_at": "2026-07-28T00:00:00Z",
                "sale_type": "membership",
                "qualifying_new_membership": True,
                "evidence": {"membership_type": "Fast Track Package"},
            }
        ],
        [event],
        observed_at=datetime.fromisoformat("2026-07-30T00:00:00+00:00"),
    )
    assert cases[0]["first_onboarding_appointment_id"] == "pt-1"
    assert cases[0]["booking_days"] == 1
    assert cases[0]["completion_state"] == "elapsed_unverified"


def test_kickstart_does_not_treat_an_unrelated_pt_session_as_onboarding():
    pt_calendar_id = next(
        calendar_id
        for calendar_id, appointment_type in ONBOARDING_CALENDARS.items()
        if appointment_type == "pt_session"
    )
    event = normalise_onboarding_event(
        {
            "id": "pt-1",
            "contactId": "contact-1",
            "calendarId": pt_calendar_id,
            "startTime": "2026-07-29T07:00:00Z",
            "endTime": "2026-07-29T07:30:00Z",
            "appointmentStatus": "confirmed",
        }
    )
    cases = link_sales_to_onboarding(
        [
            {
                "sale_id": "sale-1",
                "contact_id": "contact-1",
                "sold_at": "2026-07-28T00:00:00Z",
                "sale_type": "membership",
                "qualifying_new_membership": True,
                "evidence": {"membership_type": "Strong, Fit & Flexible"},
            }
        ],
        [event],
        observed_at=datetime.fromisoformat("2026-07-30T00:00:00+00:00"),
    )
    assert cases[0]["completion_state"] == "unbooked"


def test_duplicate_same_slot_pt_events_count_as_one_elapsed_appointment():
    pt_calendar_id = next(
        calendar_id
        for calendar_id, appointment_type in ONBOARDING_CALENDARS.items()
        if appointment_type == "pt_session"
    )
    events = [
        normalise_onboarding_event(
            {
                "id": event_id,
                "contactId": "contact-1",
                "calendarId": pt_calendar_id,
                "startTime": "2026-07-29T07:00:00Z",
                "endTime": "2026-07-29T07:30:00Z",
                "dateAdded": booked_at,
                "appointmentStatus": "confirmed",
                "assignedUserId": "coach-1",
            }
        )
        for event_id, booked_at in (
            ("pt-1", "2026-07-28T00:30:00Z"),
            ("pt-duplicate", "2026-07-28T00:45:00Z"),
        )
    ]
    cases = link_sales_to_onboarding(
        [
            {
                "sale_id": "sale-1",
                "contact_id": "contact-1",
                "sold_at": "2026-07-28T00:00:00Z",
                "sale_type": "membership",
                "qualifying_new_membership": True,
                "evidence": {"membership_type": "Fast Track Package"},
            }
        ],
        events,
        observed_at=datetime.fromisoformat("2026-07-30T00:00:00+00:00"),
    )
    assert cases[0]["first_onboarding_appointment_id"] == "pt-1"
    assert cases[0]["elapsed_confirmed_appointments"] == 1
