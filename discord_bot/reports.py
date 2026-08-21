"""
reports.py
Generates formatted Discord messages for daily briefs and weekly KPI reports.
"""

import json
import re
import sys
import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

try:
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from sheets_client import (
        read_ytd_revenue,
        read_appointments_this_week,
        read_sa_attendance_this_week,
    )
except ImportError:
    def read_ytd_revenue(): return None
    def read_appointments_this_week(): return []
    def read_sa_attendance_this_week(): return []

BRISBANE_TZ = ZoneInfo("Australia/Brisbane")
GOAL        = 1_000_000


def _parse_current_data() -> dict:
    """Parse context/current-data.md into a key→value dict."""
    data_file = Path(__file__).parent.parent / "context" / "current-data.md"
    result = {}
    if not data_file.exists():
        return result
    for line in data_file.read_text().splitlines():
        if not line.startswith("|"):
            continue
        parts = [p.strip() for p in line.strip("|").split("|")]
        if len(parts) == 2 and parts[0] and parts[0] not in ("Metric", "") and not parts[0].startswith("-"):
            result[parts[0]] = parts[1]
    return result


def _load_current_contract() -> dict:
    """Load the governed machine-readable KPI contract when available."""
    data_file = Path(__file__).parent.parent / "context" / "current-data.json"
    if not data_file.exists():
        return {}
    try:
        payload = json.loads(data_file.read_text())
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if payload.get("schema_version") == 1 else {}


def _currency(value, *, whole=False) -> str:
    if value is None:
        return "—"
    return f"${value:,.0f}" if whole else f"${value:,.2f}"


def _percent(value) -> str:
    return "—" if value is None else f"{value * 100:.1f}%"


def _progress_bar(pct: float, length: int = 20) -> str:
    filled = max(0, min(length, int(pct / 100 * length)))
    return "[" + "█" * filled + "░" * (length - filled) + "]"


def format_weekly_report() -> str:
    contract = _load_current_contract()
    kpi = _parse_current_data()
    ytd = contract.get("revenue", {}).get("year_to_date_cash_collected")
    if ytd is None:
        try:
            ytd = read_ytd_revenue()
        except Exception:
            ytd = None
    period = contract.get("period", {})
    week_str = period.get("label")
    if not week_str:
        today = datetime.date.today()
        monday = today - datetime.timedelta(days=today.weekday() + 7)
        week_str = (
            f"{monday.strftime('%d %b')}–"
            f"{(monday + datetime.timedelta(days=6)).strftime('%d %b %Y')}"
        )

    if ytd is not None:
        pct      = min(ytd / GOAL * 100, 100)
        bar      = _progress_bar(pct)
        goal_str = f"{bar} {pct:.1f}%  —  ${ytd:,.0f} of ${GOAL:,.0f} YTD"
    else:
        goal_str = "YTD data unavailable"

    def v(key):
        return kpi.get(key, "—")

    members = contract.get("members", {})
    revenue = contract.get("revenue", {})
    sales = contract.get("sales", {})
    acquisition = contract.get("acquisition", {})
    retention = contract.get("retention", {})

    if contract:
        values = {
            "sgpt": members.get("active_sgpt_service_relationships"),
            "pt": members.get("active_pt_service_relationships"),
            "total": members.get("unique_active_roster_clients"),
            "overlaps": members.get("cross_service_overlaps"),
            "sgpt_net": retention.get("sgpt_net"),
            "pt_net": retention.get("pt_net"),
            "sgpt_cancels": retention.get("sgpt_cancels"),
            "pt_cancels": retention.get("pt_cancels"),
            "cash": _currency(revenue.get("cash_collected")),
            "annual": _currency(
                revenue.get("estimated_annual_revenue"), whole=True
            ),
            "ncc": _currency(revenue.get("new_cash_collected")),
            "ncc_organic": _currency(revenue.get("new_cash_organic")),
            "ncc_ads": _currency(revenue.get("new_cash_via_ads")),
            "sales": sales.get("total"),
            "sgpt_sales": sales.get("sgpt_total"),
            "pt_sales": sales.get("pt_total"),
            "conversion": _percent(acquisition.get("sales_conversion_rate")),
            "show": _percent(acquisition.get("show_rate_total")),
            "leads": acquisition.get("total_leads"),
            "bookings": acquisition.get("studio_bookings"),
            "attended": acquisition.get("studio_bookings_attended"),
            "subscribes": acquisition.get("total_subscribes"),
            "meta_spend": _currency(acquisition.get("meta_ad_spend")),
            "google_spend": _currency(acquisition.get("google_ad_spend")),
            "total_spend": _currency(acquisition.get("total_ad_spend")),
        }
    else:
        values = {
            "sgpt": v("Active SGPT Members"),
            "pt": v("Active PT Clients"),
            "total": v("Total Clients"),
            "overlaps": "—",
            "sgpt_net": v("SGPT Net (Gained / Lost)"),
            "pt_net": v("PT Net (Gained / Lost)"),
            "sgpt_cancels": v("SGPT Cancels"),
            "pt_cancels": v("PT Cancels"),
            "cash": v("Cash Collected"),
            "annual": v("Estimated Annual Revenue"),
            "ncc": v("Total New Cash Collected"),
            "ncc_organic": v("NCC — Organic"),
            "ncc_ads": v("NCC via Ads"),
            "sales": v("Sales Total"),
            "sgpt_sales": v("SGPT Sales Total"),
            "pt_sales": v("PT Sales Total"),
            "conversion": v("Sales Conversion Rate"),
            "show": v("Show Rate (Total)"),
            "leads": v("Total Leads"),
            "bookings": v("Total Studio Bookings"),
            "attended": v("Studio Bookings Attended"),
            "subscribes": v("Total Subscribes"),
            "meta_spend": v("Meta Ad Spend"),
            "google_spend": v("Google Ad Spend"),
            "total_spend": v("Total Ad Spend"),
        }

    return f"""**WEEKLY KPI REPORT — completed period {week_str}**

**Revenue Goal — $1M**
{goal_str}

**Members**
SGPT relationships: {values["sgpt"]}  |  PT relationships: {values["pt"]}  |  Unique clients: {values["total"]}
Cross-service overlaps removed: {values["overlaps"]}
Net this period: SGPT {values["sgpt_net"]}, PT {values["pt_net"]}  |  Cancels: SGPT {values["sgpt_cancels"]}, PT {values["pt_cancels"]}

**Revenue**
Cash Collected: {values["cash"]}  |  Est. Annual Run Rate: {values["annual"]}
NCC: {values["ncc"]}  (Organic: {values["ncc_organic"]}  |  Ads: {values["ncc_ads"]})

**Sales**
Total: {values["sales"]}  (SGPT: {values["sgpt_sales"]}, PT: {values["pt_sales"]})
Conversion: {values["conversion"]}  |  Show Rate: {values["show"]}

**Funnel**
Leads: {values["leads"]}  |  Bookings: {values["bookings"]}  |  Attended: {values["attended"]}
Subscribes: {values["subscribes"]}

**Ad Spend**
Meta: {values["meta_spend"]}  |  Google: {values["google_spend"]}  |  Total: {values["total_spend"]}"""


def format_daily_brief() -> str:
    now     = datetime.datetime.now(BRISBANE_TZ)
    day_str = now.strftime("%A, %d %B %Y")

    # Appointments this week
    try:
        appointments = read_appointments_this_week()
        if not appointments:
            apt_section = "No assessments booked this week."
        else:
            lines = []
            for apt in appointments:
                day_time = apt["datetime"].strftime("%a %d %b, %I:%M %p")
                name     = f"{apt['first_name']} {apt['last_name']}".strip()
                source   = apt["source"] or "Unknown"
                extras   = []
                if apt["pre_qual"]:
                    extras.append(f"Pre-qual: {apt['pre_qual']}")
                line = f"• {day_time} — {name} ({source})"
                if extras:
                    line += "  |  " + "  |  ".join(extras)
                lines.append(line)
            attendance = read_sa_attendance_this_week()
            if attendance:
                counts = {}
                for event in attendance:
                    status = event["status"] or "unknown"
                    counts[status] = counts.get(status, 0) + 1
                unresolved = sum(event["unresolved"] for event in attendance)
                control = (
                    "Governed attendance: "
                    f"{counts.get('showed', 0)} Showed, "
                    f"{counts.get('no_show', 0)} No show, "
                    f"{counts.get('cancelled', 0)} Cancelled, "
                    f"{unresolved} unresolved."
                )
            else:
                control = (
                    "Governed attendance is in shadow setup; legacy column K "
                    "is not shown as an attendance result."
                )
            apt_section = "\n".join(lines + ["", control])
    except Exception as e:
        apt_section = f"Could not load appointments: {e}"

    # Pull priority names from strategy.md
    strategy_file = Path(__file__).parent.parent / "context" / "strategy.md"
    focus_lines = [
        "1. Increase revenue per client — Fast Track penetration + PT utilisation",
        "2. Fill unused PT capacity across trainers",
        "3. Strengthen marketing and sales systems",
    ]
    if strategy_file.exists():
        found = re.findall(r"\d+\.\s+\*\*(.+?)\*\*", strategy_file.read_text())
        if found:
            focus_lines = [f"{i + 1}. {p}" for i, p in enumerate(found[:3])]

    focus_str = "\n".join(focus_lines)

    return f"""Good morning, Peter. {day_str}.

**Strength Assessments This Week**
{apt_section}

**Current Priorities**
{focus_str}"""
