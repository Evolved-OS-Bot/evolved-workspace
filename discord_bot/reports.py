"""
reports.py
Generates formatted Discord messages for daily briefs and weekly KPI reports.
"""

import re
import sys
import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

try:
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from sheets_client import read_ytd_revenue, read_appointments_this_week
except ImportError:
    def read_ytd_revenue(): return None
    def read_appointments_this_week(): return []

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


def _progress_bar(pct: float, length: int = 20) -> str:
    filled = max(0, min(length, int(pct / 100 * length)))
    return "[" + "█" * filled + "░" * (length - filled) + "]"


def format_weekly_report() -> str:
    kpi    = _parse_current_data()
    ytd    = read_ytd_revenue()
    today  = datetime.date.today()
    monday = today - datetime.timedelta(days=today.weekday())
    week_str = monday.strftime("%d %b %Y")

    if ytd is not None:
        pct      = min(ytd / GOAL * 100, 100)
        bar      = _progress_bar(pct)
        goal_str = f"{bar} {pct:.1f}%  —  ${ytd:,.0f} of ${GOAL:,.0f} YTD"
    else:
        goal_str = "YTD data unavailable"

    def v(key):
        return kpi.get(key, "—")

    return f"""**WEEKLY KPI REPORT — w/c {week_str}**

**Revenue Goal — $1M**
{goal_str}

**Members**
SGPT: {v("Active SGPT Members")}  |  PT: {v("Active PT Clients")}  |  Total: {v("Total Clients")}
Net this week: SGPT {v("SGPT Net (Gained / Lost)")}, PT {v("PT Net (Gained / Lost)")}  |  Cancels: SGPT {v("SGPT Cancels")}, PT {v("PT Cancels")}

**Revenue**
Cash Collected: {v("Cash Collected")}  |  Est. Annual Run Rate: {v("Estimated Annual Revenue")}
NCC: {v("Total New Cash Collected")}  (Organic: {v("NCC — Organic")}  |  Ads: {v("NCC via Ads")})

**Sales**
Total: {v("Sales Total")}  (SGPT: {v("SGPT Sales Total")}, PT: {v("PT Sales Total")})
Conversion: {v("Sales Conversion Rate")}  |  Show Rate: {v("Show Rate (Total)")}

**Funnel**
Leads: {v("Total Leads")}  |  Bookings: {v("Total Studio Bookings")}  |  Attended: {v("Studio Bookings Attended")}
Subscribes: {v("Total Subscribes")}

**Ad Spend**
Meta: {v("Meta Ad Spend")}  |  Google: {v("Google Ad Spend")}  |  Total: {v("Total Ad Spend")}"""


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
                if apt["showed"]:
                    extras.append(f"Show: {apt['showed']}")
                line = f"• {day_time} — {name} ({source})"
                if extras:
                    line += "  |  " + "  |  ".join(extras)
                lines.append(line)
            apt_section = "\n".join(lines)
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
