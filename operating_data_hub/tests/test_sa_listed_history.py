from datetime import UTC, datetime

from operating_data_hub.reporting_v2 import ReportingV2Repository
from operating_data_hub.sa_listed_history import build_listed_history
from operating_data_hub.store import HubStore


def sheet_row(
    appointment_at: str,
    *,
    showed: str,
    converted: str,
) -> list[str]:
    return [
        "date booked",
        "First",
        "Last",
        "lead magnet",
        "0400000000",
        "member@example.com",
        "Organic",
        appointment_at,
        "Peter",
        "Y",
        showed,
        converted,
        "Organic",
        "",
    ]


def test_listed_history_uses_separate_show_and_conversion_boundaries():
    result = build_listed_history(
        [
            sheet_row(
                "Friday, September 19, 2025 17:00",
                showed="Y",
                converted="Y",
            ),
            sheet_row(
                "Wednesday, March 11, 2026 17:00",
                showed="Y",
                converted="N",
            ),
            sheet_row(
                "Thursday, March 12, 2026 17:00",
                showed="N",
                converted="N",
            ),
            sheet_row(
                "Friday, March 13, 2026 17:00",
                showed="Y",
                converted="Y",
            ),
        ],
        observed_at=datetime(2026, 7, 30, tzinfo=UTC),
    )

    events = result["events"]
    assert events[0]["show_rate_eligible"] is False
    assert events[0]["conversion_denominator_eligible"] is True
    assert events[1]["legacy_attended"] is True
    assert events[2]["show_rate_eligible"] is True
    assert events[2]["conversion_denominator_eligible"] is False
    assert events[3]["show_rate_eligible"] is True
    assert events[3]["conversion_numerator_eligible"] is True


def test_conversion_y_without_attendance_is_retained_and_flagged():
    result = build_listed_history(
        [
            sheet_row(
                "Thursday, March 12, 2026 17:00",
                showed="N",
                converted="Y",
            )
        ],
        observed_at=datetime(2026, 7, 30, tzinfo=UTC),
    )

    assert result["events"][0]["attendance_mismatch"] is True
    assert result["events"][0]["conversion_numerator_eligible"] is True
    assert result["summary"]["attendance_mismatches"] == 1


def test_repository_records_listed_history_without_relabelling_n():
    store = HubStore("sqlite:///:memory:")
    repo = ReportingV2Repository(store.engine)
    history = build_listed_history(
        [
            sheet_row(
                "Friday, September 19, 2025 17:00",
                showed="Y",
                converted="Y",
            ),
            sheet_row(
                "Thursday, March 12, 2026 17:00",
                showed="N",
                converted="N",
            ),
            sheet_row(
                "Friday, March 13, 2026 17:00",
                showed="Y",
                converted="N",
            ),
        ],
        observed_at=datetime(2026, 7, 30, tzinfo=UTC),
    )

    result = repo.record_sa_listed_history_shadow(
        history["events"],
        observed_at=history["observed_at"],
    )

    assert result["show_metrics"]["history"]["status"] == "accepted"
    observations = repo.status()["latest_metric_observations"]
    listed_show = next(
        row
        for row in observations
        if row["metric_id"] == "sa_listed_show_rate"
        and row["period_start"] == "2026-03-12"
    )
    listed_conversion = next(
        row
        for row in observations
        if row["metric_id"] == "sa_listed_conversion_rate"
        and row["period_start"] == "2025-09-19"
    )
    assert listed_show["numerator"] == "1"
    assert listed_show["denominator"] == "2"
    assert listed_conversion["numerator"] == "1"
    assert listed_conversion["denominator"] == "2"
    definitions = {
        row["metric_id"]: row for row in repo.definitions()
    }
    assert definitions["sa_listed_show_rate"]["effective_from"] == (
        "2026-03-12"
    )
    assert definitions[
        "sa_listed_conversion_rate"
    ]["effective_from"] == "2025-09-19"


def test_parallel_run_explains_blank_workbook_show_denominator():
    store = HubStore("sqlite:///:memory:")
    repo = ReportingV2Repository(store.engine)
    history = build_listed_history(
        [
            sheet_row(
                "Monday, July 20, 2026 17:00",
                showed="Y",
                converted="Y",
            ),
            sheet_row(
                "Tuesday, July 21, 2026 17:00",
                showed="Y",
                converted="Y",
            ),
            sheet_row(
                "Wednesday, July 22, 2026 17:00",
                showed="N",
                converted="N",
            ),
            sheet_row(
                "Thursday, July 23, 2026 17:00",
                showed="N",
                converted="N",
            ),
            sheet_row(
                "Friday, July 24, 2026 17:00",
                showed="",
                converted="N",
            ),
        ],
        observed_at=datetime(2026, 7, 30, tzinfo=UTC),
    )

    result = repo.record_sa_listed_history_shadow(
        history["events"],
        observed_at=history["observed_at"],
    )

    week = result["parallel_results"]["week"]
    assert week["show_rate"]["status"] == "passed"
    assert week["show_rate"]["variance"] == "0.1"
    assert week["conversion_rate"]["variance"] == "0.0"
    comparison = next(
        row
        for row in repo.status()["latest_parallel_results"]
        if row["metric_id"] == "sa_listed_show_rate"
        and row["period_start"] == "2026-07-20"
    )
    assert comparison["variance_classification"] == "legacy_defect"
    assert comparison["evidence"]["blank_attendance_rows"] == 1
    assert comparison["unexplained_event_count"] == 0
