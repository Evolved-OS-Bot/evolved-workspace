from datetime import datetime

from operating_data_hub.ghl_reporting_v2 import (
    MEMBERSHIP_AGREEMENT_DATE_FIELD_ID,
    MEMBERSHIP_TYPE_FIELD_ID,
    ONBOARDING_CALENDARS,
    PREQUAL_COMPLETED_AT_FIELD_ID,
    PREQUAL_COMPLETED_BY_FIELD_ID,
    PREQUAL_SUMMARY_FIELD_ID,
    PREQUAL_WAIVED_AT_FIELD_ID,
    PREQUAL_WAIVED_BY_FIELD_ID,
    PREQUAL_WAIVER_REASON_FIELD_ID,
    PT_AGREEMENT_DATE_FIELD_ID,
    WARM_PIPELINE_ID,
    WARM_STAGE_PREQUALIFIED,
    build_ghl_acquisition_snapshot,
    build_prequalification_parity_sample,
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
                    field(PREQUAL_SUMMARY_FIELD_ID, "Complete handoff"),
                    field(PREQUAL_COMPLETED_BY_FIELD_ID, "Peter Brown"),
                    field(
                        PREQUAL_COMPLETED_AT_FIELD_ID,
                        "2026-07-09T18:10:29+10:00",
                    ),
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
    assert snapshot["summary"]["prequalification_completion_rate"] is None
    assert snapshot["prequalification_events"][0]["occurred_at"] == (
        "2026-07-09T08:10:29+00:00"
    )
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
            "customFields": [
                field(PREQUAL_SUMMARY_FIELD_ID, "Complete handoff"),
                field(PREQUAL_COMPLETED_BY_FIELD_ID, "Piper Mae"),
                field(
                    PREQUAL_COMPLETED_AT_FIELD_ID,
                    "2026-08-01T09:00:00+10:00",
                ),
            ],
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


def test_prequalification_requires_all_four_controls_and_queues_exception():
    snapshot = build_ghl_acquisition_snapshot(
        contacts=[
            {
                "id": "contact-1",
                "customFields": [
                    field(PREQUAL_SUMMARY_FIELD_ID, "Complete handoff"),
                    field(PREQUAL_COMPLETED_BY_FIELD_ID, "Admin Eve"),
                    field(PREQUAL_COMPLETED_AT_FIELD_ID, "2026-08-01T09:00:00"),
                ],
            }
        ],
        opportunities=[
            {
                "id": "opportunity-1",
                "contactId": "contact-1",
                "pipelineId": WARM_PIPELINE_ID,
                "pipelineStageId": WARM_STAGE_PREQUALIFIED,
            }
        ],
        attendance_rows=[attendance()],
        observed_at="2026-08-02T00:00:00Z",
    )

    assert snapshot["prequalification_events"] == []
    assert snapshot["summary"]["prequalification_exceptions"] == 1
    assert snapshot["prequalification_exceptions"][0]["issue_codes"] == [
        "shared_role_completer",
        "brisbane_completion_timestamp_invalid",
    ]


def test_prequalification_corrections_keep_one_stable_event_identity():
    def snapshot(completer, completed_at):
        return build_ghl_acquisition_snapshot(
            contacts=[
                {
                    "id": "contact-1",
                    "name": "Client One",
                    "customFields": [
                        field(PREQUAL_SUMMARY_FIELD_ID, "Complete handoff"),
                        field(PREQUAL_COMPLETED_BY_FIELD_ID, completer),
                        field(PREQUAL_COMPLETED_AT_FIELD_ID, completed_at),
                    ],
                }
            ],
            opportunities=[
                {
                    "id": "opportunity-1",
                    "contactId": "contact-1",
                    "pipelineId": WARM_PIPELINE_ID,
                    "pipelineStageId": WARM_STAGE_PREQUALIFIED,
                }
            ],
            attendance_rows=[],
            observed_at="2026-08-09T00:00:00Z",
        )

    first = snapshot("Nora Silva", "2026-08-08T09:00:00+10:00")
    corrected = snapshot("Piper Mae", "2026-08-08T09:05:00+10:00")
    assert first["prequalification_events"][0]["source_event_id"] == (
        corrected["prequalification_events"][0]["source_event_id"]
    )
    assert first["prequalification_events"][0]["source_event_id"] == (
        "prequalification-completed:opportunity-1"
    )


def test_prequalification_waiver_is_explicit_and_needs_no_warm_stage():
    snapshot = build_ghl_acquisition_snapshot(
        contacts=[
            {
                "id": "contact-1",
                "customFields": [
                    field(PREQUAL_WAIVED_BY_FIELD_ID, "Megan Brown"),
                    field(
                        PREQUAL_WAIVED_AT_FIELD_ID,
                        "2026-08-09T09:00:00+10:00",
                    ),
                    field(
                        PREQUAL_WAIVER_REASON_FIELD_ID,
                        "Direct assessment booking",
                    ),
                ],
            }
        ],
        opportunities=[],
        attendance_rows=[],
        observed_at="2026-08-09T00:00:00Z",
    )

    assert snapshot["prequalification_events"] == []
    assert len(snapshot["prequalification_waiver_events"]) == 1
    assert snapshot["summary"]["prequalification_waived"] == 1
    assert snapshot["summary"]["prequalification_waiver_state"] == (
        "explicit_governed_event"
    )


def test_prequalification_parity_sample_is_aggregate_only_and_exact():
    contacts = [
        {
            "id": "contact-complete",
            "customFields": [
                field(PREQUAL_SUMMARY_FIELD_ID, "Complete handoff"),
                field(PREQUAL_COMPLETED_BY_FIELD_ID, "Piper Mae"),
                field(
                    PREQUAL_COMPLETED_AT_FIELD_ID,
                    "2026-08-08T09:00:00+10:00",
                ),
            ],
        },
        {
            "id": "contact-exception",
            "customFields": [
                field(PREQUAL_SUMMARY_FIELD_ID, "Incomplete handoff"),
            ],
        },
    ]
    opportunities = [
        {
            "id": "opportunity-complete",
            "contactId": "contact-complete",
            "pipelineId": WARM_PIPELINE_ID,
            "pipelineStageId": WARM_STAGE_PREQUALIFIED,
        },
        {
            "id": "opportunity-exception",
            "contactId": "contact-exception",
            "pipelineId": WARM_PIPELINE_ID,
            "pipelineStageId": WARM_STAGE_PREQUALIFIED,
        },
    ]
    snapshot = build_ghl_acquisition_snapshot(
        contacts=contacts,
        opportunities=opportunities,
        attendance_rows=[],
        observed_at="2026-08-09T00:00:00Z",
    )
    result = build_prequalification_parity_sample(
        contacts=contacts,
        opportunities=opportunities,
        persisted_event_refs=[
            {
                "contact_id": row["contact_id"],
                "source_event_id": row["source_event_id"],
            }
            for row in snapshot["prequalification_events"]
        ],
        persisted_review_queue=snapshot["prequalification_exceptions"],
        observed_at="2026-08-09T00:00:00Z",
    )

    assert result["sample_size"] == 2
    assert result["exact"] == 2
    assert result["mismatches"] == 0
    assert result["state_counts"] == {
        "expected_completed": 1,
        "expected_exception": 1,
        "persisted_completed": 1,
        "persisted_exception": 1,
    }
    assert "contact-complete" not in str(result)
    assert "contact-exception" not in str(result)


def test_prequalification_rejects_unknown_human_and_ambiguous_opportunities():
    snapshot = build_ghl_acquisition_snapshot(
        contacts=[
            {
                "id": "contact-1",
                "customFields": [
                    field(PREQUAL_SUMMARY_FIELD_ID, "Complete handoff"),
                    field(PREQUAL_COMPLETED_BY_FIELD_ID, "Unknown Person"),
                    field(
                        PREQUAL_COMPLETED_AT_FIELD_ID,
                        "2026-08-08T09:00:00+10:00",
                    ),
                ],
            }
        ],
        opportunities=[
            {
                "id": opportunity_id,
                "contactId": "contact-1",
                "pipelineId": WARM_PIPELINE_ID,
                "pipelineStageId": WARM_STAGE_PREQUALIFIED,
            }
            for opportunity_id in ("opportunity-1", "opportunity-2")
        ],
        attendance_rows=[],
        observed_at="2026-08-09T00:00:00Z",
    )

    assert snapshot["prequalification_events"] == []
    assert snapshot["prequalification_exceptions"][0]["issue_codes"] == [
        "eligible_warm_opportunity_ambiguous",
        "human_completer_unrecognised",
    ]


def test_historical_stage_without_new_completion_fields_is_not_an_exception():
    snapshot = build_ghl_acquisition_snapshot(
        contacts=[{"id": "contact-1", "customFields": []}],
        opportunities=[
            {
                "id": "historical-opportunity",
                "contactId": "contact-1",
                "pipelineId": WARM_PIPELINE_ID,
                "pipelineStageId": WARM_STAGE_PREQUALIFIED,
            }
        ],
        attendance_rows=[],
        observed_at="2026-08-09T00:00:00Z",
    )

    assert snapshot["prequalification_events"] == []
    assert snapshot["prequalification_exceptions"] == []


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
