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
    metrics = {
        "period": period.to_dict(),
        "members": rosters.to_dict(),
        "cash_collected": number(value("cash_collected")),
        "year_to_date_cash_collected": number(
            get_cell(rows, ROWS["cash_collected"], 2)
        ),
        "new_cash_collected": number(value("ncc_total")),
        "sales_total": number(value("sales_total"), integer=True),
        "leads_total": number(value("leads_total"), integer=True),
        "bookings_total": number(value("bookings_total"), integer=True),
        "bookings_attended": number(
            value("bookings_attended"), integer=True
        ),
        "conversion_rate": number(value("conversion_rate_total")),
        "show_rate": number(value("show_rate_total")),
        "sgpt_cancels": number(value("sgpt_cancels"), integer=True),
        "pt_cancels": number(value("pt_cancels"), integer=True),
        "sgpt_net": number(value("sgpt_net"), integer=True),
        "pt_net": number(value("pt_net"), integer=True),
        "pt_bookings": number(value("pt_bookings"), integer=True),
        "pt_booked_hours": number(value("pt_booked_hours")),
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
