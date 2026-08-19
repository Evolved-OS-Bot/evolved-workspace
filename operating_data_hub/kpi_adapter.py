from __future__ import annotations

from datetime import datetime
from typing import Any

from reporting_control import (
    ReportingPeriod,
    deduplicate_service_rosters,
    filter_roster_by_values,
)
from scripts.sheets_client import find_current_week_col, read_sheet
from scripts.update_metrics import ROWS, get_cell, number


def collect_kpi_snapshot() -> dict[str, Any]:
    rows = read_sheet("KPI's The Evolved", "A1:BF140")
    column, posting_date = find_current_week_col(rows)
    if column is None or posting_date is None:
        raise RuntimeError("No current KPI posting column found")
    period = ReportingPeriod.from_kpi_posting_date(posting_date)

    def value(key: str):
        return get_cell(rows, ROWS[key], column)

    def labelled_row(label: str, *, after: str | None = None):
        start = 0
        if after:
            section_matches = [
                index
                for index, row in enumerate(rows)
                if str(get_cell(rows, index, 0) or "").strip() == after
            ]
            if section_matches:
                start = section_matches[0] + 1
        for index in range(start, len(rows)):
            if str(get_cell(rows, index, 0) or "").strip() == label:
                return index
        return None

    cash_collected = number(value("cash_collected"))
    new_cash_collected = number(value("ncc_total"))
    recurring_cash_collected = (
        max(0, cash_collected - new_cash_collected)
        if cash_collected is not None and new_cash_collected is not None
        else None
    )
    trainer_names = (
        "Megan Brown",
        "Piper Mae",
        "Nora Silva",
        "Katrina Parsons",
        "Leisa Smith",
    )
    trainer_breakdown = {}
    for trainer_name in trainer_names:
        hours_row = labelled_row(
            trainer_name,
            after="PT Booked Hours (automated from GHL)",
        )
        bookings_row = labelled_row(
            trainer_name,
            after="PT Bookings (automated from GHL)",
        )
        trainer_breakdown[trainer_name] = {
            "booked_hours": (
                number(get_cell(rows, hours_row, column))
                if hours_row is not None
                else None
            ),
            "bookings": (
                number(get_cell(rows, bookings_row, column), integer=True)
                if bookings_row is not None
                else None
            ),
        }

    sgpt_roster = filter_roster_by_values(
        read_sheet("Active SGPT", "A1:K500"),
        column_names=("Status",),
        accepted_values=("Active", "Active - PIA"),
    )
    rosters = deduplicate_service_rosters(
        {
            "SGPT": sgpt_roster,
            "PT": read_sheet("Active PT", "A1:M500"),
        }
    )
    sgpt_net = number(value("sgpt_net"), integer=True)
    pt_net = number(value("pt_net"), integer=True)
    movement_values = [
        item for item in (sgpt_net, pt_net) if item is not None
    ]
    metrics = {
        "period": period.to_dict(),
        "members": rosters.to_dict(),
        "cash_collected": cash_collected,
        "recurring_cash_collected": recurring_cash_collected,
        "year_to_date_cash_collected": number(
            get_cell(rows, ROWS["cash_collected"], 2)
        ),
        "new_cash_collected": new_cash_collected,
        "sales_total": number(value("sales_total"), integer=True),
        "leads_total": number(value("leads_total"), integer=True),
        "bookings_total": number(value("bookings_total"), integer=True),
        "bookings_attended": number(
            value("bookings_attended"), integer=True
        ),
        "conversion_rate": number(value("conversion_rate_total")),
        "show_rate": number(value("show_rate_total")),
        "legacy_sheet_show_rate": number(value("show_rate_total")),
        "show_rate_authority": "legacy_google_kpi_shadow_only",
        "sgpt_cancels": number(value("sgpt_cancels"), integer=True),
        "pt_cancels": number(value("pt_cancels"), integer=True),
        "sgpt_net": sgpt_net,
        "pt_net": pt_net,
        "net_service_movement": (
            sum(movement_values) if movement_values else None
        ),
        "pt_bookings": number(value("pt_bookings"), integer=True),
        "pt_booked_hours": number(value("pt_booked_hours")),
        "pt_trainer_breakdown": trainer_breakdown,
    }
    return {
        "schema_version": 1,
        "source": "google_kpi",
        "observed_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": "complete",
        "complete": True,
        "summary": {
            "record_count": rosters.service_relationships,
            "metrics": metrics,
        },
    }
