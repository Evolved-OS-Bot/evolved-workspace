#!/usr/bin/env python3
"""
update_metrics.py
Reads the current week's KPI data from the Google Sheet
and rewrites context/current-data.md.

Usage:
    python scripts/update_metrics.py            # Update current-data.md
    python scripts/update_metrics.py --dry-run  # Print without writing
"""

import csv
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).parent))
from sheets_client import read_sheet, find_current_week_col
from reporting_control import (
    ReportingPeriod,
    deduplicate_service_rosters,
    filter_roster_by_values,
)

DRY_RUN     = "--dry-run" in sys.argv
OUTPUT_PATH = ROOT / "context" / "current-data.md"
JSON_OUTPUT_PATH = ROOT / "context" / "current-data.json"
IDENTITY_LINKS_PATH = (
    ROOT / "data" / "private" / "integration-reporting" / "identity_links.csv"
)
SHEET_NAME  = os.environ.get("GOOGLE_KPI_SHEET_NAME", "KPI's The Evolved")

# Row index map — 0-based (sheet row number minus 1)
ROWS = {
    # Members
    "active_sgpt":          16,   # Row 17
    "active_pt":            24,   # Row 25
    # Ad spend
    "meta_ad_spend":        25,   # Row 26
    "google_ad_spend":      26,   # Row 27
    "total_ad_spend":       27,   # Row 28
    # Subscribes
    "subscribes_organic":   32,   # Row 33
    "subscribes_paid":      33,   # Row 34
    "subscribes_total":     34,   # Row 35
    # Leads
    "leads_organic":        37,   # Row 38
    "leads_meta":           38,   # Row 39
    "leads_google":         39,   # Row 40
    "leads_paid_total":     40,   # Row 41
    "leads_total":          41,   # Row 42
    # Studio bookings
    "bookings_total":       51,   # Row 52
    "bookings_via_ads":     52,   # Row 53
    "bookings_no_ads":      53,   # Row 54
    "bookings_attended":    59,   # Row 60
    "show_rate_ads":        60,   # Row 61
    "show_rate_no_ads":     61,   # Row 62
    "show_rate_total":      62,   # Row 63
    # SGPT sales
    "sgpt_meta":            63,   # Row 64
    "sgpt_google":          64,   # Row 65
    "sgpt_organic":         65,   # Row 66
    "sgpt_total":           69,   # Row 70
    # PT sales
    "pt_meta":              70,   # Row 71
    "pt_google":            71,   # Row 72
    "pt_organic":           72,   # Row 73
    "pt_total":             76,   # Row 77
    # Sales totals
    "sales_via_ads":        77,   # Row 78
    "sales_no_ads":         78,   # Row 79
    "sales_total":          79,   # Row 80
    "conversion_rate_total":82,   # Row 83
    # New Cash Collected
    "ncc_organic":          83,   # Row 84
    "ncc_meta":             84,   # Row 85
    "ncc_google":           85,   # Row 86
    "ncc_total":            87,   # Row 88
    "ncc_ads_total":        88,   # Row 89
    # Cancels / net
    "sgpt_cancels":         89,   # Row 90
    "pt_cancels":           90,   # Row 91
    "sgpt_net":             93,   # Row 94
    "pt_net":               94,   # Row 95
    # Suspensions
    "suspensions_active":   97,   # Row 98
    # Revenue
    "cash_collected":       105,  # Row 106
    # Automated PT utilisation
    "pt_booked_hours":      114,  # Row 115
    "pt_bookings":          122,  # Row 123
}


def get_cell(rows, row_idx, col_idx):
    try:
        return rows[row_idx][col_idx]
    except (IndexError, TypeError):
        return None


def fmt(val, prefix="", suffix="", pct=False):
    s = str(val).strip() if val is not None else ""
    if not s or s.startswith("#") or s == "—":
        return "—"
    if pct:
        try:
            return f"{float(val)*100:.1f}%"
        except (ValueError, TypeError):
            pass
    return f"{prefix}{val}{suffix}"


def fmt_currency(val):
    if val is None or str(val).strip() == "":
        return "—"
    try:
        n = float(str(val).replace("$", "").replace(",", ""))
        return f"${n:,.2f}"
    except (ValueError, TypeError):
        return str(val)


def number(val, *, integer=False):
    if val is None or str(val).strip() in {"", "—"}:
        return None
    try:
        parsed = float(str(val).replace("$", "").replace(",", ""))
        return int(parsed) if integer and parsed.is_integer() else parsed
    except (ValueError, TypeError):
        return None


def load_approved_aliases(path=IDENTITY_LINKS_PATH):
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return [
            (row.get("canonical_email", ""), row.get("linked_email", ""))
            for row in csv.DictReader(handle)
            if row.get("canonical_email") and row.get("linked_email")
        ]


def atomic_write_text(path, content):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(path)


def load_governed_attendance():
    hub_url = os.getenv("OPERATING_DATA_HUB_URL", "").rstrip("/")
    hub_secret = os.getenv("HUB_WEBHOOK_SECRET", "")
    if not hub_url or not hub_secret:
        return None
    response = requests.get(
        f"{hub_url}/api/v1/sa-attendance/summary",
        headers={"X-Hub-Secret": hub_secret},
        timeout=20,
    )
    response.raise_for_status()
    payload = response.json()
    return {
        "definition_version": payload.get("definition_version"),
        **(payload.get("summary") or {}),
        "source_observed_at": (
            (payload.get("source") or {}).get("observed_at")
        ),
    }


def main():
    print(f"Reading sheet: {SHEET_NAME}")
    rows = read_sheet(SHEET_NAME, "A1:BF140")

    col_idx, week_date = find_current_week_col(rows)
    if col_idx is None:
        print("ERROR: Could not find current week column in sheet header row.")
        sys.exit(1)

    print(f"Current week: {week_date} (col index {col_idx})")
    period = ReportingPeriod.from_kpi_posting_date(week_date)
    limitations = []
    try:
        governed_attendance = load_governed_attendance()
    except Exception as exc:
        governed_attendance = None
        limitations.append(
            "Governed Strength Assessment attendance is unavailable because "
            f"the hub summary could not be read: {type(exc).__name__}."
        )
    if governed_attendance is None:
        limitations.append(
            "Strength Assessment attendance remains in shadow setup. Sheet "
            "show-rate cells are legacy column-K outputs and are not treated "
            "as governed attendance."
        )

    def g(key):
        return get_cell(rows, ROWS[key], col_idx)

    # Stock and service-relationship metrics
    active_sgpt = g("active_sgpt")
    active_pt   = g("active_pt")
    try:
        sgpt_roster = filter_roster_by_values(
            read_sheet("Active SGPT", "A1:K500"),
            column_names=("Status",),
            accepted_values=("Active", "Active - PIA"),
        )
        roster_summary = deduplicate_service_rosters(
            {
                "SGPT": sgpt_roster,
                "PT": read_sheet("Active PT", "A1:M500"),
            },
            approved_email_aliases=load_approved_aliases(),
        )
        total_clients = roster_summary.unique_clients
    except Exception as exc:
        roster_summary = None
        total_clients = None
        limitations.append(
            "Unique active roster clients unavailable because the Active SGPT "
            f"or Active PT roster could not be read: {type(exc).__name__}."
        )

    cash = g("cash_collected")
    ytd_cash = get_cell(rows, ROWS["cash_collected"], 2)
    try:
        cash_num    = float(str(cash).replace("$", "").replace(",", ""))
        annual_est  = f"${cash_num * 52:,.0f}"
        cash_fmt    = f"${cash_num:,.2f}"
    except (ValueError, TypeError):
        cash_num, annual_est, cash_fmt = None, "—", "—"

    blended = "—"
    if cash_num and total_clients:
        blended = f"${cash_num / total_clients:.2f}"

    now_local = datetime.now().astimezone()
    now = now_local.strftime("%Y-%m-%d %H:%M %Z")
    generated_at = now_local.isoformat(timespec="seconds")
    week_str = period.label
    service_relationships = (
        roster_summary.service_relationships if roster_summary else None
    )
    overlaps = roster_summary.cross_service_overlaps if roster_summary else None

    data = {
        "schema_version": 1,
        "report_id": "current-business-metrics",
        "generated_at": generated_at,
        "mode": "read_only",
        "period": period.to_dict(),
        "source": {
            "spreadsheet": "Brown & Casserly Pty Ltd 2026",
            "kpi_sheet": SHEET_NAME,
            "posting_column_date": period.posting_date.isoformat(),
            "limitations": limitations,
        },
        "members": {
            "active_sgpt_service_relationships": number(
                active_sgpt, integer=True
            ),
            "active_pt_service_relationships": number(active_pt, integer=True),
            "unique_active_roster_clients": total_clients,
            "active_service_roster_rows": service_relationships,
            "cross_service_overlaps": overlaps,
            "active_suspensions": number(g("suspensions_active"), integer=True),
            "unique_client_definition": (
                roster_summary.to_dict()["definition"]
                if roster_summary
                else None
            ),
        },
        "revenue": {
            "cash_collected": cash_num,
            "year_to_date_cash_collected": number(ytd_cash),
            "estimated_annual_revenue": (
                cash_num * 52 if cash_num is not None else None
            ),
            "blended_weekly_revenue_per_unique_client": (
                cash_num / total_clients
                if cash_num is not None and total_clients
                else None
            ),
            "new_cash_collected": number(g("ncc_total")),
            "new_cash_via_ads": number(g("ncc_ads_total")),
            "new_cash_organic": number(g("ncc_organic")),
            "new_cash_meta": number(g("ncc_meta")),
            "new_cash_google": number(g("ncc_google")),
        },
        "acquisition": {
            "meta_ad_spend": number(g("meta_ad_spend")),
            "google_ad_spend": number(g("google_ad_spend")),
            "total_ad_spend": number(g("total_ad_spend")),
            "organic_subscribes": number(g("subscribes_organic"), integer=True),
            "paid_subscribes": number(g("subscribes_paid"), integer=True),
            "total_subscribes": number(g("subscribes_total"), integer=True),
            "organic_leads": number(g("leads_organic"), integer=True),
            "meta_leads": number(g("leads_meta"), integer=True),
            "google_leads": number(g("leads_google"), integer=True),
            "paid_leads": number(g("leads_paid_total"), integer=True),
            "total_leads": number(g("leads_total"), integer=True),
            "studio_bookings": number(g("bookings_total"), integer=True),
            "bookings_via_ads": number(g("bookings_via_ads"), integer=True),
            "bookings_without_ads": number(
                g("bookings_no_ads"), integer=True
            ),
            "studio_bookings_attended": number(
                g("bookings_attended"), integer=True
            ),
            "show_rate_ads": number(g("show_rate_ads")),
            "show_rate_no_ads": number(g("show_rate_no_ads")),
            "show_rate_total": number(g("show_rate_total")),
            "governed_attendance": governed_attendance,
            "attendance_definition_version": (
                governed_attendance.get("definition_version")
                if governed_attendance
                else "sa-attendance-v1"
            ),
            "attendance_publication_state": (
                "provisional"
                if governed_attendance
                and governed_attendance.get("show_rate_provisional")
                else (
                    "governed"
                    if governed_attendance
                    else "shadow-unavailable"
                )
            ),
            "sales_conversion_rate": number(g("conversion_rate_total")),
        },
        "sales": {
            "sgpt_meta": number(g("sgpt_meta"), integer=True),
            "sgpt_google": number(g("sgpt_google"), integer=True),
            "sgpt_organic": number(g("sgpt_organic"), integer=True),
            "sgpt_total": number(g("sgpt_total"), integer=True),
            "pt_meta": number(g("pt_meta"), integer=True),
            "pt_google": number(g("pt_google"), integer=True),
            "pt_organic": number(g("pt_organic"), integer=True),
            "pt_total": number(g("pt_total"), integer=True),
            "via_ads": number(g("sales_via_ads"), integer=True),
            "without_ads": number(g("sales_no_ads"), integer=True),
            "total": number(g("sales_total"), integer=True),
        },
        "retention": {
            "sgpt_cancels": number(g("sgpt_cancels"), integer=True),
            "pt_cancels": number(g("pt_cancels"), integer=True),
            "sgpt_net": number(g("sgpt_net"), integer=True),
            "pt_net": number(g("pt_net"), integer=True),
        },
        "pt_utilisation": {
            "bookings": number(g("pt_bookings"), integer=True),
            "booked_hours": number(g("pt_booked_hours")),
        },
    }

    content = f"""\
# Current Data

> Auto-generated by `update_metrics.py` — last updated {now}
> Completed service period: **{week_str}**. KPI posting column: **{period.posting_date.strftime("%d %b %Y")}**.
> Run `update-metrics` to refresh.

---

## How This Connects

- **business-info.md** provides organisational context
- **personal-info.md** defines what you're responsible for
- **strategy.md** outlines what you're optimising toward
- **This file** gives Claude the numbers behind the narrative

---

## Members

| Metric | Value |
|---|---|
| Active SGPT Members | {fmt(active_sgpt)} |
| Active PT Clients | {fmt(active_pt)} |
| Total Clients | {fmt(total_clients)} |
| Active Service Roster Rows | {fmt(service_relationships)} |
| Cross-Service Overlaps Removed | {fmt(overlaps)} |
| Active Suspensions | {fmt(g("suspensions_active"))} |

`Total Clients` is a deduplicated roster-person count. It uses exact email,
exact phone and owner-approved email aliases only; names are never matched.

---

## Revenue ({week_str})

| Metric | Value |
|---|---|
| Cash Collected | {cash_fmt} |
| Year-to-Date Cash Collected | {fmt_currency(ytd_cash)} |
| Estimated Annual Revenue | {annual_est} |
| Blended Weekly Revenue Per Client | {blended} |
| Total New Cash Collected | {fmt_currency(g("ncc_total"))} |
| NCC via Ads | {fmt_currency(g("ncc_ads_total"))} |
| NCC — Organic | {fmt_currency(g("ncc_organic"))} |
| NCC — Meta Ads | {fmt_currency(g("ncc_meta"))} |
| NCC — Google Ads | {fmt_currency(g("ncc_google"))} |

---

## Ad Spend

| Metric | Value |
|---|---|
| Meta Ad Spend | {fmt_currency(g("meta_ad_spend"))} |
| Google Ad Spend | {fmt_currency(g("google_ad_spend"))} |
| Total Ad Spend | {fmt_currency(g("total_ad_spend"))} |

---

## Leads & Bookings Funnel

| Metric | Value |
|---|---|
| Organic Subscribes | {fmt(g("subscribes_organic"))} |
| Paid Subscribes | {fmt(g("subscribes_paid"))} |
| Total Subscribes | {fmt(g("subscribes_total"))} |
| Organic Leads | {fmt(g("leads_organic"))} |
| Meta Leads | {fmt(g("leads_meta"))} |
| Google Leads | {fmt(g("leads_google"))} |
| Total Paid Leads | {fmt(g("leads_paid_total"))} |
| Total Leads | {fmt(g("leads_total"))} |
| Total Studio Bookings | {fmt(g("bookings_total"))} |
| Bookings via Ads | {fmt(g("bookings_via_ads"))} |
| Bookings w/o Ads | {fmt(g("bookings_no_ads"))} |
| Studio Bookings Attended | {fmt(g("bookings_attended"))} |
| Legacy Column-K Show Rate (Ads) | {fmt(g("show_rate_ads"), pct=True)} |
| Legacy Column-K Show Rate (No Ads) | {fmt(g("show_rate_no_ads"), pct=True)} |
| Legacy Column-K Show Rate (Total) | {fmt(g("show_rate_total"), pct=True)} |
| Governed Showed | {fmt(governed_attendance.get("showed") if governed_attendance else None)} |
| Governed No Show | {fmt(governed_attendance.get("no_show") if governed_attendance else None)} |
| Governed Cancelled | {fmt(governed_attendance.get("cancelled") if governed_attendance else None)} |
| Governed Unresolved | {fmt(governed_attendance.get("unresolved") if governed_attendance else None)} |
| Governed Show Rate | {fmt(governed_attendance.get("show_rate") if governed_attendance else None, pct=True)} |
| Attendance Definition | {governed_attendance.get("definition_version") if governed_attendance else "sa-attendance-v1 (shadow unavailable)"} |
| Sales Conversion Rate | {fmt(g("conversion_rate_total"), pct=True)} |

---

## Sales

| Metric | Value |
|---|---|
| SGPT Sales — Meta | {fmt(g("sgpt_meta"))} |
| SGPT Sales — Google | {fmt(g("sgpt_google"))} |
| SGPT Sales — Organic | {fmt(g("sgpt_organic"))} |
| SGPT Sales Total | {fmt(g("sgpt_total"))} |
| PT Sales — Meta | {fmt(g("pt_meta"))} |
| PT Sales — Google | {fmt(g("pt_google"))} |
| PT Sales — Organic | {fmt(g("pt_organic"))} |
| PT Sales Total | {fmt(g("pt_total"))} |
| Sales via Ads | {fmt(g("sales_via_ads"))} |
| Sales w/o Ads | {fmt(g("sales_no_ads"))} |
| Sales Total | {fmt(g("sales_total"))} |

---

## Retention

| Metric | Value |
|---|---|
| SGPT Cancels | {fmt(g("sgpt_cancels"))} |
| PT Cancels | {fmt(g("pt_cancels"))} |
| SGPT Net (Gained / Lost) | {fmt(g("sgpt_net"))} |
| PT Net (Gained / Lost) | {fmt(g("pt_net"))} |

---

## PT Utilisation

| Metric | Value |
|---|---|
| PT Bookings (week) | {fmt(g("pt_bookings"))} |
| PT Booked Hours (week) | {fmt(g("pt_booked_hours"))} |

---

## Data Sources

- Google Sheet: KPI's The Evolved tab
- Active SGPT and Active PT rosters for the unique-client control
- Raw data from GHL → aggregated via COUNTIFS formulas
- Cash Collected and Ad Spend entered manually each week
- Machine-readable contract: `context/current-data.json`
"""

    if limitations:
        content += "\n## Data Limitations\n\n" + "\n".join(
            f"- {item}" for item in limitations
        ) + "\n"

    if DRY_RUN:
        print("\n--- DRY RUN (no file written) ---\n")
        print(content)
        print("\n--- JSON CONTRACT ---\n")
        print(json.dumps(data, indent=2))
    else:
        atomic_write_text(OUTPUT_PATH, content)
        atomic_write_text(
            JSON_OUTPUT_PATH,
            json.dumps(data, indent=2, sort_keys=True) + "\n",
        )
        print(f"Written to {OUTPUT_PATH} and {JSON_OUTPUT_PATH}")


if __name__ == "__main__":
    main()
