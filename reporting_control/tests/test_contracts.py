from datetime import date
import json
from pathlib import Path

import pytest

from reporting_control.executive_brief import build_executive_brief
from reporting_control.identity import deduplicate_service_rosters
from reporting_control.identity import filter_roster_by_values
from reporting_control.periods import ReportingPeriod
from reporting_control.registry import load_registry


def test_kpi_posting_monday_maps_to_completed_service_week():
    period = ReportingPeriod.from_kpi_posting_date(date(2026, 7, 27))

    assert period.service_start == date(2026, 7, 20)
    assert period.service_end == date(2026, 7, 26)
    assert period.stock_as_of == date(2026, 7, 27)
    assert period.label == "20–26 Jul 2026"


def test_kpi_posting_date_must_be_monday():
    with pytest.raises(ValueError, match="Monday"):
        ReportingPeriod.from_kpi_posting_date(date(2026, 7, 26))


def test_fast_track_overlap_counts_one_unique_person():
    summary = deduplicate_service_rosters(
        {
            "SGPT": [
                ["First Name", "Email", "Phone"],
                ["Alice", "alice@example.com", "0400 111 222"],
                ["Beth", "beth@example.com", "0400 333 444"],
            ],
            "PT": [
                ["First Name", "Email", "Phone"],
                ["Alice", "ALICE@example.com", "+61 400 111 222"],
            ],
        }
    )

    assert summary.service_relationships == 3
    assert summary.unique_clients == 2
    assert summary.cross_service_overlaps == 1


def test_owner_approved_email_alias_deduplicates_without_name_matching():
    summary = deduplicate_service_rosters(
        {
            "SGPT": [
                ["Name", "Email", "Phone"],
                ["Different Display Name", "member@example.com", ""],
            ],
            "PT": [
                ["Name", "Email", "Phone"],
                ["Another Name", "payer@example.com", ""],
            ],
        },
        approved_email_aliases=[
            ("member@example.com", "payer@example.com")
        ],
    )

    assert summary.unique_clients == 1
    assert summary.cross_service_overlaps == 1


def test_roster_filter_excludes_arrears_and_preserves_header():
    rows = [
        ["Email", "Status "],
        ["active@example.com", "Active"],
        ["pia@example.com", "Active - PIA"],
        ["arrears@example.com", "Active - ARREARS"],
    ]
    filtered = filter_roster_by_values(
        rows,
        column_names=("Status",),
        accepted_values=("Active", "Active - PIA"),
    )
    assert filtered == [rows[0], rows[1], rows[2]]


def test_report_registry_is_complete_and_dependency_safe():
    root = Path(__file__).resolve().parents[2]
    registry = load_registry(root / "reporting_control" / "report_registry.json")

    assert len(registry["reports"]) == 9
    assert {report["id"] for report in registry["reports"]} >= {
        "current-business-metrics",
        "retention-intelligence",
        "pt-booking-continuity",
        "revenue-control",
        "conversation-triage",
        "trainerize-performance",
        "sgpt-delivery-v2",
        "strength-assessment-attendance",
    }


def test_executive_brief_is_aggregate_and_contains_no_identity_fields():
    root = Path(__file__).resolve().parents[2]
    brief = build_executive_brief(
        root=root,
        registry_path=root / "reporting_control" / "report_registry.json",
    )
    serialised = json.dumps(brief).lower()

    assert brief["privacy"] == "aggregate-share-safe"
    assert '"email"' not in serialised
    assert '"phone"' not in serialised
    assert '"first_name"' not in serialised
