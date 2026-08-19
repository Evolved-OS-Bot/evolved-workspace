from datetime import UTC, datetime

from operating_data_hub.staff_bonus import (
    bonus_report_csv,
    build_monthly_bonus_report,
    normalise_sales_sheet,
    validate_eligibility,
)


HEADERS = [
    "Date",
    "First Name",
    "Last Name",
    "Mobile",
    "Email",
    "Source",
    "Product",
    "Salesperson",
]


def contact():
    return {
        "id": "contact-1",
        "firstName": "Client",
        "lastName": "One",
        "email": "client@example.com",
        "phone": "+61400111222",
    }


def showed(day="2026-08-05T02:00:00+00:00"):
    return {
        "appointment_id": "appointment-1",
        "appointment_series_id": "series-1",
        "contact_id": "contact-1",
        "canonical_status": "showed",
        "start_at": day,
    }


def test_sales_sheet_accepts_only_same_day_showed_package_sales():
    result = normalise_sales_sheet(
        [
            HEADERS,
            [
                "05/08/2026",
                "Client",
                "One",
                "0400 111 222",
                "client@example.com",
                "Organic",
                "Bronze",
                "Nora",
            ],
            [
                "05/08/2026",
                "Client",
                "One",
                "0400 111 222",
                "client@example.com",
                "Organic",
                "PT 30M x 2",
                "Nora",
            ],
            [
                "06/08/2026",
                "Client",
                "One",
                "0400 111 222",
                "client@example.com",
                "Organic",
                "Silver",
                "Nora",
            ],
        ],
        contacts=[contact()],
        attendance_rows=[showed()],
        observed_at=datetime(2026, 8, 9, tzinfo=UTC),
    )

    assert result["events"][0]["state"] == "accepted"
    assert result["events"][0]["sold_by"] == "Nora Silva"
    assert result["events"][0]["package_price_cents"] == 39_900
    assert result["events"][1]["state"] == "excluded"
    assert result["events"][1]["issue_codes"] == [
        "personal_training_sale_excluded"
    ]
    assert result["events"][2]["state"] == "review"
    assert result["events"][2]["issue_codes"] == [
        "no_showed_assessment_same_day"
    ]


def test_duplicate_package_rows_fail_closed():
    row = [
        "05/08/2026",
        "Client",
        "One",
        "0400 111 222",
        "client@example.com",
        "Organic",
        "Bronze",
        "Nora",
    ]
    result = normalise_sales_sheet(
        [HEADERS, row, row],
        contacts=[contact()],
        attendance_rows=[showed()],
        observed_at=datetime(2026, 8, 9, tzinfo=UTC),
    )

    assert [event["state"] for event in result["events"]] == [
        "review",
        "review",
    ]
    assert all(
        "duplicate_sales_rows" in event["issue_codes"]
        for event in result["events"]
    )


def test_monthly_report_applies_signed_eligibility_after_evidence():
    report = build_monthly_bonus_report(
        "2026-08",
        prequalification_events=[
            {
                "source_event_id": "prequalification-completed:opp-1",
                "event_version_id": "version-1",
                "occurred_at": "2026-08-04T23:00:00+00:00",
                "completed_by": "Nora Silva",
                "contact_name": "Client One",
            },
            {
                "source_event_id": "prequalification-completed:opp-2",
                "event_version_id": "version-2",
                "occurred_at": "2026-08-05T00:00:00+00:00",
                "completed_by": "Peter Brown",
                "contact_name": "Client Two",
            },
        ],
        prequalification_reviews=[],
        sale_events=[
            {
                "source_event_id": "staff-bonus-sales-row:2",
                "event_version_id": "sale-version-1",
                "occurred_at": "2026-08-05T02:00:00+00:00",
                "sale_date": "2026-08-05",
                "state": "accepted",
                "issue_codes": [],
                "sold_by": "Nora Silva",
                "customer_name": "Client One",
                "product": "Bronze",
            }
        ],
        sale_unallocated_reviews=[],
        eligibility_records=[
            {
                "staff_name": "Nora Silva",
                "effective_from": "2026-08-01",
                "effective_to": None,
            }
        ],
        generated_at=datetime(2026, 9, 1, tzinfo=UTC),
        source_status={
            "prequalification": {"available": True},
            "sales": {"available": True},
        },
    )

    assert report["available"] is True
    assert report["totals"]["payable_amount_cents"] == 7_000
    nora = next(
        row for row in report["staff_summary"] if row["staff_member"] == "Nora Silva"
    )
    assert nora["prequalification_count"] == 1
    assert nora["sales_count"] == 1
    peter = next(
        row for row in report["lines"] if row["staff_member"] == "Peter Brown"
    )
    assert peter["policy_eligibility"] == "owner_excluded"
    assert peter["payable_amount_cents"] == 0
    assert "governed_event_id" in bonus_report_csv(report)


def test_eligibility_requires_owner_approval_and_rejects_owner_bonus():
    valid = validate_eligibility(
        {
            "staff_name": "Piper Mae",
            "effective_from": "2026-08-01",
            "agreement_reference": "signed-document-1",
            "approved_by": "Peter Brown",
        }
    )
    assert valid["staff_name"] == "Piper Mae"

    try:
        validate_eligibility(
            {
                "staff_name": "Peter Brown",
                "effective_from": "2026-08-01",
                "agreement_reference": "not-applicable",
                "approved_by": "Peter Brown",
            }
        )
    except ValueError as exc:
        assert "excluded" in str(exc)
    else:
        raise AssertionError("Peter Brown must not become bonus eligible")
