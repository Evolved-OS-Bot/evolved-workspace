# Plan: Live Metrics Update Script (V1)

**Created:** 2026-03-22
**Updated:** 2026-03-23
**Status:** Step 1 Complete — Awaiting fresh sheet setup before Step 2
**Request:** Automate the Google Sheet KPI tracker so GHL data flows in without manual entry (except revenue and ad spend), then build a Python script that reads the sheet and writes context/current-data.md. Trigger: `update-metrics` shell alias.

---

## Overview

### What This Plan Accomplishes

Three connected layers:
1. **Google Sheet formulas** — replace manual metric entry in the KPI tab with `COUNTIFS` formulas that roll up raw GHL row data from the Appointments, Sales, Subscribes, and Cancellations tabs automatically
2. **One new GHL workflow** — when an opportunity is won, automatically append the new member to the Active Members sheet (currently manual)
3. **Python script** — reads the current week's column from the KPI tab and rewrites `context/current-data.md` with live data

### Why This Matters

Peter currently spends time each week manually copying numbers from GHL into the KPI sheet. The sheet already has the raw data from GHL — it just isn't being aggregated automatically. This plan closes that gap, making the only required manual input the total Cash Collected (revenue) and ad spend, which have no automatable source.

---

## Architecture

```
GHL (raw events) ──► Google Sheets raw tabs (already working)
                          │
                          ▼
               COUNTIFS formulas in KPI tab  ◄── Manual: Cash Collected, Ad Spend
                          │
                          ▼
              update_metrics.py (reads KPI tab)
                          │
                          ▼
              context/current-data.md (read by /prime)
```

**What stays manual (no automatable source):**
- Cash Collected / Total Revenue (row 105) — EziDebit + Stripe, Xero lags 1–2 days
- NCC by source (rows 83–86) — revenue attribution across payment channels
- Meta Ad Spend / Google Ad Spend (rows 26–27) — need separate Meta/Google Ads API (V3 scope)

---

## Current State

### Google Sheet Structure

**Spreadsheet ID:** `1aeD8c2mY9rwltmVnTl86rx_rYXpSsAq3HTamk-hEs3c`

**KPI Tab (gid=479564089):**
- Row 1: Week-start dates (Mondays) as column headers
- Col A: Metric row labels
- Col B: 2025 full-year total
- Col C: 2026 YTD total
- Col D: Last 6 weeks total
- Col E: Targets
- Col F onwards: Weekly data columns (Oct 2025 → Sep 2026)
- 113 rows, 57 columns

**Raw data tabs (GHL pushes row data into these):**

| Tab | GID | Key Columns |
|-----|-----|-------------|
| Appointments | 1425512753 | A=Date Booked, G=Source, H=Appt Date, J=Convert? |
| Sales | 312470558 | A=Date, F=Source, G=Product, I=Cash Taken |
| Subscribes | 826098082 | A=Date, D=Source |
| Membership Cancels (NEW) | 1824108454 | A=Date Submitted, N=Membership Tier |
| PT Cancellations | 1789559013 | A=Date |
| SGPT Cancellations | 227347788 | A=First Name (no date col — see note) |
| Active Members The Evolved | 1988437564 | A=Date Joined, F=Trainer, G=Product/Tier, J=Status |

### Gaps Being Addressed

- KPI tab rows 33–94 are manually entered each week despite the raw data existing in other tabs
- Active Members sheet is manually updated after each sale
- No formula layer exists between raw GHL data and the KPI summary
- `context/current-data.md` is a static, weeks-old snapshot

---

## Proposed Changes

### Summary

- Add `COUNTIFS` formulas to KPI tab for all automatable rows (see full list below)
- Create one new GHL workflow: Opportunity Won → append row to Active Members sheet
- Create `scripts/update_metrics.py` — reads KPI tab via Google Sheets API, writes `current-data.md`
- Create `scripts/sheets_client.py` — Google Sheets API authentication and read helper
- Create `scripts/requirements.txt`, `scripts/.env.example`, `scripts/SETUP.md`
- Update `scripts/.env` with Google Sheets credentials variables
- Update `shell-aliases.md` with `update-metrics` alias
- Update `CLAUDE.md` with script documentation

### New Files

| File | Purpose |
|---|---|
| `scripts/update_metrics.py` | Main script — reads Sheet, writes current-data.md |
| `scripts/sheets_client.py` | Google Sheets API auth + read helper |
| `scripts/requirements.txt` | Python dependencies |
| `scripts/.env.example` | Credentials template |
| `scripts/SETUP.md` | One-time setup guide |

### Files to Modify

| File | Changes |
|---|---|
| `scripts/.env` | Add Google Sheets service account variables |
| `context/current-data.md` | Add auto-generated header; script owns this file |
| `shell-aliases.md` | Add `update-metrics` alias |
| `CLAUDE.md` | Add Scripts section and update structure table |
| Google Sheet (KPI tab) | Add COUNTIFS formulas to rows 17, 19–25, 33–35, 38–42, 46–55, 57–59, 62–69, 70–79, 89–90, 93–94 |

---

## Design Decisions

1. **Google Sheets as sole script data source**: The sheet is already Peter's KPI system of record. The script reads one tab rather than calling multiple APIs. Simpler auth, simpler code, more reliable.

2. **Xero removed from scope**: Xero bank feeds lag 1–2 days. Cash Collected is entered manually anyway — Xero adds no value for real-time metrics.

3. **GHL API removed from script**: GHL data is already flowing into the Sheet. No need to call GHL directly — the Sheet is the aggregation layer.

4. **COUNTIFS date range approach**: Each formula in the KPI tab uses the column header date (row 1) as the week start. Pattern: `=COUNTIFS(Tab!$A:$A,">="&KPIs!F$1,Tab!$A:$A,"<"&KPIs!F$1+7,...)`  This makes every past and future column self-populating — no weekly column management needed.

5. **Service account for Sheets API**: Server-to-server auth via a Google Cloud service account JSON key. No browser OAuth flow. Peter shares the sheet with the service account email once.

6. **One GHL workflow for Active Members**: GHL's native Google Sheets workflow action appends a row when an opportunity is won. This is the only new GHL automation needed.

7. **SGPT Cancels tab**: Renamed from "Membership Cancels (NEW)" to "SGPT Cancels". All entries in this tab are SGPT cancellations — no tier filter needed, simple date-range COUNTIFS. PT Cancellations tab is unchanged.

8. **Show rate tracking**: Appointments tab now has col K = Show? (Y/N, manually toggled per row) and col L = Convert? (auto-populated on sale). Show rate formula uses col K = "Y". Convert rate uses col L = "Y".

9. **Source format**: `paid | {utmSource}` and `organic | {utmSource}`. Prefix hardcoded in each GHL workflow (already split). COUNTIFS wildcard: `"paid |*"`, `"organic |*"`, `"paid |*facebook*"`, `"paid |*google*"` etc.

10. **Product → member type mapping**: Bronze → SGPT member only. Silver → SGPT member + PT client (counted in both). PT packages → PT client only. SGPT member count: Bronze + Silver. PT client count: PT* + Silver. Total new members (headcount): all rows = 1 person regardless of product.

11. **Fresh sheets required before formulas**: Old Appointments and Sales data has inconsistent source values. Archive old data, create fresh tabs before writing COUNTIFS formulas.

### Open Questions — RESOLVED

1. **Source values**: GHL writes `{{contact.lastAttributionSource.utmSource}}`. Values are messy on old data. **Resolution:** Archive old sheets, start fresh. New source format: `paid | {utmSource}` or `organic | {utmSource}` — prefix hardcoded per workflow (already split into Organic/Paid workflows in GHL).
2. **Source values in Sales tab**: Same as above — same fix applies.
3. **Product values in Sales tab (col G)**: Bronze = SGPT only, Silver = SGPT + 1x PT, PT 30M/45M packages = PT only.
4. **Column structure in Appointments**: A=Date Booked, G=Source, J=Goals?, K=Show? (Y/N, manually toggled), L=Convert? (auto Y/N on sale). Original plan had Convert? at col J — now col L.
5. **Membership Cancels (NEW)**: Col N (Membership Tier) was blank — GHL now wired to populate it. Simpler fix: rename tab to "SGPT Cancels" — all entries are SGPT, no tier filter needed. PT Cancellations tab handles PT.
6. **GHL Opportunity Won fields**: Still to confirm — column mapping for Active Members sheet append (Step 3).

### Source Breakdown Scope Decision

Assessment booking and studio booking rows (38–55) will **not** be broken down by source. The strength assessment workflow is a single workflow regardless of lead source — organic/paid split is not reliable at this stage. Source breakdown is tracked at:
- **Subscribes** (rows 33–35): organic vs paid — clean, already split in GHL workflows
- **Sales** (rows 63–79): organic vs paid — contact's stored attribution carries through correctly

---

## Step-by-Step Tasks

### Step 1: Verify source string values in raw tabs

Before writing any formulas, Peter needs to check the actual values GHL is writing.

**Actions:**
- Open Appointments tab → Column G (Source) → note the exact values present (e.g. "Meta Ads", "Google Ads", "Organic", "Website", "Referral", "Social Media")
- Open Sales tab → Column F (Source) → note exact values
- Open Sales tab → Column G (Product) → note exact values (to distinguish SGPT from PT)
- Open Appointments tab → Column J (Convert?) → note what values appear (Yes/No? Showed/No-Show?)
- Open Membership Cancels (NEW) → Column N (Membership Tier) → confirm SGPT cancels appear here with a date

**Report findings** before proceeding to Step 2.

**Files affected:** None — research only

---

### Step 2: Add COUNTIFS formulas to KPI tab

Using the source string values confirmed in Step 1, add formulas to the KPI tab. All formulas use the column's row 1 date as the week anchor.

**Formula pattern (weekly date range):**
```
=COUNTIFS(SheetName!$A:$A,">="&'KPI''s The Evolved'!F$1,SheetName!$A:$A,"<"&'KPI''s The Evolved'!F$1+7[,additional criteria...])
```

**Rows to update with formulas:**

| Row | Metric | Source Tab | Filter Criteria |
|-----|--------|------------|-----------------|
| 17 | Active SGPT Members | Active Members The Evolved | Col G = "Bronze" OR "Silver", Col J = "Active" — SUM of two COUNTIFs |
| 19 | Leisa Smith (PT) | Active Members The Evolved | Col F = "Leisa Smith", Col J = "Active" |
| 20 | Bethany Fry (PT) | Active Members The Evolved | Col F = "Bethany Fry", Col J = "Active" |
| 21 | Piper Mae (PT) | Active Members The Evolved | Col F = "Piper Mae", Col J = "Active" |
| 22 | Marnie Chapple (PT) | Active Members The Evolved | Col F = "Marnie Chapple", Col J = "Active" |
| 23 | Hannah Altmann (PT) | Active Members The Evolved | Col F = "Hannah Altmann", Col J = "Active" |
| 24 | Megan Brown (PT) | Active Members The Evolved | Col F = "Megan Brown", Col J = "Active" |
| 25 | Active PT Clients | Active Members The Evolved | Col G = "PT*" OR "Silver", Col J = "Active" — SUM of two COUNTIFs |
| 33 | Organic Subscribes | Subscribes | Col D = "organic |*" wildcard |
| 34 | Paid Subscribes | Subscribes | Col D = "paid |*" wildcard |
| 35 | Total Subscribes | Subscribes | Date range only |
| 38–42 | Leads (total only) | Appointments | Date range only — source breakdown removed (single assessment workflow) |
| 46–55 | Studio Bookings (total only) | Appointments | Date range only — source breakdown removed |
| 57 | Studio Bookings Attended | Appointments | Col K (Show?) = "Y", date range |
| 62 | Show Rate | Calculated | = Row 57 / Row 52 |
| 63 | SGPT Sales Via Paid Social | Sales | Col G = "Bronze" OR "Silver", Col F = "paid |*facebook*" — SUM pattern |
| 64 | SGPT Sales Via Google Ads | Sales | Col G = "Bronze" OR "Silver", Col F = "paid |*google*" — SUM pattern |
| 65 | SGPT Sales Via Organic | Sales | Col G = "Bronze" OR "Silver", Col F = "organic |*" — SUM pattern |
| 68 | SGPT Sales Total | Sales | Col G = "Bronze" OR "Silver" — SUM of two COUNTIFs, date range |
| 70 | PT Sales Via Paid Social | Sales | Col G = "PT*" OR "Silver", Col F = "paid |*facebook*" — SUM pattern |
| 71 | PT Sales Via Google Ads | Sales | Col G = "PT*" OR "Silver", Col F = "paid |*google*" — SUM pattern |
| 72 | PT Sales Via Organic | Sales | Col G = "PT*" OR "Silver", Col F = "organic |*" — SUM pattern |
| 75 | PT Sales Total | Sales | Col G = "PT*" OR "Silver" — SUM of two COUNTIFs, date range |
| 77 | Sales Via Paid | Sales | Col F = "paid |*" |
| 78 | Sales Via Organic | Sales | Col F = "organic |*" |
| 79 | Sales Total | Sales | Date range only (1 row = 1 person regardless of product) |
| 89 | SGPT Cancels | SGPT Cancels | Date range on Col A only — tab is exclusively SGPT, no filter needed |
| 90 | PT Cancels | PT Cancellations | Date range on Col A |
| 93 | SGPT Members Gained/Lost | Calculated | = SGPT Sales Total (row 68) - SGPT Cancels (row 89) |
| 94 | PT Members Gained/Lost | Calculated | = PT Sales Total (row 75) - PT Cancels (row 90) |

**Note on rows 17/19–25 (Active Members):** These are cumulative counts (total active), not weekly additions. The formula should NOT use a date range — it should count all rows where Status = "Active" (and applicable trainer/product filter). This means these cells will show the same value across all weekly columns, which is correct.

**Note on rows 19–24 (individual trainers):** These appear to be PT client counts per trainer based on the tab context. Confirm with Peter whether these are PT client counts or SGPT session counts per trainer.

**Files affected:** Google Sheet — KPI tab, rows listed above

---

### Step 3: Set up GHL workflow — Active Members auto-update

Create a GHL workflow that fires when an opportunity is won and appends a new row to the Active Members The Evolved sheet.

**Actions:**
- In GHL → Automations → Create New Workflow
- Trigger: **Opportunity Status Changed** → Status = Won
- Action: **Google Sheets — Append Row** to spreadsheet `1aeD8c2mY9rwltmVnTl86rx_rYXpSsAq3HTamk-hEs3c`, tab "Active Members The Evolved"
- Map fields:
  - Col A (Date Joined): `{{opportunity.created_at}}`
  - Col B (First Name): `{{contact.first_name}}`
  - Col C (Last Name): `{{contact.last_name}}`
  - Col D (Mobile): `{{contact.phone}}`
  - Col E (Email): `{{contact.email}}`
  - Col F (Trainer): `{{opportunity.assigned_user}}` or custom field if trainer is tracked separately
  - Col G (Product/Tier): `{{opportunity.pipeline_stage}}` or product custom field
  - Col J (Status): `Active`
  - Col K ($$$): `{{opportunity.monetary_value}}` or membership fee custom field
- Name the workflow: "New Member → Active Members Sheet"
- Publish the workflow

**Note:** Field mapping depends on how GHL stores trainer assignment and product type on the opportunity. Peter to confirm which GHL fields hold these values.

**Files affected:** GHL (external) — no local files

---

### Step 4: Create Google Sheets credentials template and update .env

**Actions:**
- Create `scripts/.env.example`:

```
# Google Sheets API — Service Account
# Setup instructions: see scripts/SETUP.md
GOOGLE_SHEETS_CREDENTIALS_FILE=scripts/google_credentials.json
GOOGLE_SPREADSHEET_ID=1aeD8c2mY9rwltmVnTl86rx_rYXpSsAq3HTamk-hEs3c
GOOGLE_KPI_SHEET_NAME=KPI's The Evolved
```

- Update `scripts/.env` — replace existing Xero/GHL content with:

```
# Google Sheets API — Service Account
# Setup instructions: see scripts/SETUP.md
GOOGLE_SHEETS_CREDENTIALS_FILE=scripts/google_credentials.json
GOOGLE_SPREADSHEET_ID=1aeD8c2mY9rwltmVnTl86rx_rYXpSsAq3HTamk-hEs3c
GOOGLE_KPI_SHEET_NAME=KPI's The Evolved
```

**Files affected:**
- `scripts/.env.example` (create)
- `scripts/.env` (modify)

---

### Step 5: Create Python requirements file

**Actions:**
- Create `scripts/requirements.txt`:

```
google-auth==2.29.0
google-auth-oauthlib==1.2.0
google-api-python-client==2.126.0
python-dotenv==1.0.0
```

**Files affected:**
- `scripts/requirements.txt` (create)

---

### Step 6: Create Google Sheets client module

**Actions:**
- Create `scripts/sheets_client.py`:

```python
"""
sheets_client.py
Authenticates with Google Sheets API using a service account
and reads a named range or full sheet.
"""

import os
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


def get_sheets_service():
    creds_file = os.environ["GOOGLE_SHEETS_CREDENTIALS_FILE"]
    creds = service_account.Credentials.from_service_account_file(
        creds_file, scopes=SCOPES
    )
    return build("sheets", "v4", credentials=creds)


def read_sheet(sheet_name, cell_range):
    """
    Reads a range from the spreadsheet.
    e.g. read_sheet("KPI's The Evolved", "A1:BF113")
    Returns list of rows (each row is a list of cell values).
    """
    service = get_sheets_service()
    spreadsheet_id = os.environ["GOOGLE_SPREADSHEET_ID"]
    result = (
        service.spreadsheets()
        .values()
        .get(
            spreadsheetId=spreadsheet_id,
            range=f"'{sheet_name}'!{cell_range}",
        )
        .execute()
    )
    return result.get("values", [])


def find_current_week_col(rows):
    """
    Scans row 1 (index 0) for the most recent Monday date
    that is <= today. Returns the 0-based column index.
    Row 1 format: dates as strings like "2/16/2026" or "3/23/2026".
    """
    from datetime import date, datetime

    today = date.today()
    header_row = rows[0] if rows else []
    best_col = None
    best_date = None

    for i, cell in enumerate(header_row):
        try:
            d = datetime.strptime(str(cell).strip(), "%m/%d/%Y").date()
            if d <= today:
                if best_date is None or d > best_date:
                    best_date = d
                    best_col = i
        except ValueError:
            continue

    return best_col, best_date
```

**Files affected:**
- `scripts/sheets_client.py` (create)

---

### Step 7: Create main orchestration script

**Actions:**
- Create `scripts/update_metrics.py`:

```python
#!/usr/bin/env python3
"""
update_metrics.py
Reads the current week's KPI data from the Google Sheet
and rewrites context/current-data.md.

Usage:
    python scripts/update_metrics.py            # Update current-data.md
    python scripts/update_metrics.py --dry-run  # Print without writing
"""

import sys
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")

# Add scripts/ to path for local imports
sys.path.insert(0, str(Path(__file__).parent))
from sheets_client import read_sheet, find_current_week_col

DRY_RUN = "--dry-run" in sys.argv
OUTPUT_PATH = Path(__file__).parent.parent / "context" / "current-data.md"

# Row index mapping (0-based, row 1 in Sheet = index 0)
# These match the KPI tab structure confirmed during planning.
ROWS = {
    "active_sgpt_members":        16,   # Row 17
    "active_pt_clients":          24,   # Row 25
    "total_ad_spend":             27,   # Row 28
    "total_subscribes":           34,   # Row 35
    "total_leads":                41,   # Row 42
    "total_studio_bookings":      51,   # Row 52
    "studio_bookings_attended":   58,   # Row 59
    "studio_booking_show_rate":   61,   # Row 62
    "sgpt_sales_total":           68,   # Row 69
    "pt_sales_total":             75,   # Row 76
    "sales_total":                78,   # Row 79
    "conversion_rate":            81,   # Row 82
    "ncc_organic":                82,   # Row 83
    "ncc_meta":                   83,   # Row 84
    "ncc_google":                 84,   # Row 85
    "ncc_bark":                   85,   # Row 86
    "total_ncc":                  86,   # Row 87
    "sgpt_cancels":               88,   # Row 89
    "pt_cancels":                 89,   # Row 90
    "suspensions_active":         96,   # Row 97
    "cash_collected":             104,  # Row 105
    "pt_sessions":                112,  # Row 113
}


def get_cell(rows, row_idx, col_idx):
    """Safely get a cell value, return None if out of bounds."""
    try:
        return rows[row_idx][col_idx]
    except (IndexError, TypeError):
        return None


def fmt(val, prefix="", suffix=""):
    if val is None or str(val).strip() in ("", "#DIV/0!", "#VALUE!", "#REF!"):
        return "—"
    return f"{prefix}{val}{suffix}"


def main():
    sheet_name = os.environ.get("GOOGLE_KPI_SHEET_NAME", "KPI's The Evolved")

    print(f"Reading sheet: {sheet_name}")
    rows = read_sheet(sheet_name, "A1:BF113")

    col_idx, week_date = find_current_week_col(rows)
    if col_idx is None:
        print("ERROR: Could not find current week column in sheet header row.")
        sys.exit(1)

    print(f"Current week column: index {col_idx} (week of {week_date})")

    def g(row_key):
        return get_cell(rows, ROWS[row_key], col_idx)

    # Pull all metrics
    active_sgpt   = g("active_sgpt_members")
    active_pt     = g("active_pt_clients")
    total_clients_val = None
    try:
        total_clients_val = int(str(active_sgpt).replace(",","")) + int(str(active_pt).replace(",",""))
    except (ValueError, TypeError):
        pass

    ft_val = None  # Fast Track not a separate row — derived from Active Members if tagged
    ft_pct = "—"  # Manual until Active Members tab distinguishes Fast Track

    weekly_rev    = g("cash_collected")
    annual_est    = None
    try:
        wr = float(str(weekly_rev).replace("$","").replace(",",""))
        annual_est = f"${wr * 52:,.0f}"
        weekly_rev = f"${wr:,.2f}"
    except (ValueError, TypeError):
        pass

    blended = "—"
    try:
        wr_num = float(str(g("cash_collected")).replace("$","").replace(",",""))
        if total_clients_val:
            blended = f"${wr_num / total_clients_val:.2f}"
    except (ValueError, TypeError):
        pass

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    week_str = week_date.strftime("%Y-%m-%d") if week_date else "unknown"

    content = f"""## Current Data

> Auto-generated by `update_metrics.py` — last updated {now} (week of {week_str})

---

## How This Connects

- **business-info.md** provides organizational context
- **personal-info.md** defines what you're responsible for
- **strategy.md** outlines what you're optimizing toward
- **This file** gives Claude the numbers behind the narrative

---

## Key Metrics

| Metric | Current Value | Notes |
| ------ | ------------- | ----- |
| Active SGPT Members | {fmt(active_sgpt)} | |
| Active PT Clients | {fmt(active_pt)} | |
| Total Clients (est.) | {fmt(total_clients_val)} | SGPT + PT combined |
| Total Weekly Revenue | {fmt(weekly_rev)} | Manually entered — Cash Collected row |
| Estimated Annual Revenue | {fmt(annual_est)} | Weekly × 52 |
| Blended Weekly Revenue Per Client | {blended} | |
| Total Studio Bookings (week) | {fmt(g("total_studio_bookings"))} | |
| Studio Booking Show Rate | {fmt(g("studio_booking_show_rate"))} | |
| Total Leads (week) | {fmt(g("total_leads"))} | |
| Total Subscribes (week) | {fmt(g("total_subscribes"))} | |
| SGPT Sales Total (week) | {fmt(g("sgpt_sales_total"))} | |
| PT Sales Total (week) | {fmt(g("pt_sales_total"))} | |
| Sales Total (week) | {fmt(g("sales_total"))} | |
| Sales Conversion Rate | {fmt(g("conversion_rate"))} | |
| SGPT Cancels (week) | {fmt(g("sgpt_cancels"))} | |
| PT Cancels (week) | {fmt(g("pt_cancels"))} | |
| Active Suspensions | {fmt(g("suspensions_active"))} | |
| PT Sessions (week) | {fmt(g("pt_sessions"))} | |
| Total New Cash Collected | {fmt(g("total_ncc"))} | |
| Total AD Spend | {fmt(g("total_ad_spend"))} | |

---

## Data Sources

- Google Sheet: Brown & Casserly Pty Ltd 2026 (KPI's The Evolved tab)
- Raw data from GHL → aggregated via COUNTIFS formulas
- Cash Collected manually entered weekly

---

## Automation Note

_Run `update-metrics` to refresh this file. See `scripts/SETUP.md` for credentials setup._
"""

    if DRY_RUN:
        print("\n--- DRY RUN ---")
        print(content)
        print("--- END DRY RUN --- No files written.")
    else:
        OUTPUT_PATH.write_text(content)
        print(f"Done. Written to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
```

**Files affected:**
- `scripts/update_metrics.py` (create)

---

### Step 8: Create setup guide

**Actions:**
- Create `scripts/SETUP.md`:

```markdown
# Metrics Script Setup

One-time setup. Takes approximately 10 minutes.

---

## 1. Install Python dependencies

From the workspace root:

```bash
pip install -r scripts/requirements.txt
```

---

## 2. Create a Google Cloud service account

1. Go to https://console.cloud.google.com/
2. Create a new project (or use an existing one) — name it "Evolved Metrics"
3. Enable the **Google Sheets API**: APIs & Services → Enable APIs → search "Google Sheets API" → Enable
4. Create a service account: APIs & Services → Credentials → Create Credentials → Service Account
   - Name: "evolved-metrics"
   - Skip optional fields → Done
5. Click the service account → Keys tab → Add Key → JSON → download the file
6. Rename the downloaded file to `google_credentials.json` and move it to `scripts/google_credentials.json`
7. Copy the service account email address (looks like `evolved-metrics@your-project.iam.gserviceaccount.com`)

---

## 3. Share the Google Sheet with the service account

1. Open the Brown & Casserly KPI spreadsheet
2. Click Share
3. Paste the service account email address
4. Set permission to **Viewer**
5. Click Send

---

## 4. Verify credentials file is in place

```bash
ls scripts/google_credentials.json
```

---

## 5. Test the connection

```bash
python scripts/update_metrics.py --dry-run
```

If metrics appear, you're connected. Run without `--dry-run` to write to `current-data.md`.

---

## 6. Add the shell alias

Add to your `~/.zshrc`:

```bash
alias update-metrics='cd ~/Downloads/claude-workspace-evolved && python scripts/update_metrics.py'
```

Then: `source ~/.zshrc`

---

## Troubleshooting

- **"File not found: google_credentials.json"** — check the file is at `scripts/google_credentials.json`
- **"403 Forbidden"** — sheet not shared with service account email; repeat Step 3
- **"Current week column not found"** — sheet date format may differ; check row 1 of KPI tab
```

**Files affected:**
- `scripts/SETUP.md` (create)

---

### Step 9: Update `scripts/.env`

**Actions:**
- Read current `scripts/.env`
- Replace all Xero and GHL content with Google Sheets variables:

```
# Google Sheets API — Service Account
# Setup instructions: see scripts/SETUP.md
GOOGLE_SHEETS_CREDENTIALS_FILE=scripts/google_credentials.json
GOOGLE_SPREADSHEET_ID=1aeD8c2mY9rwltmVnTl86rx_rYXpSsAq3HTamk-hEs3c
GOOGLE_KPI_SHEET_NAME=KPI's The Evolved
```

**Files affected:**
- `scripts/.env` (modify)

---

### Step 10: Update `shell-aliases.md`

**Actions:**
- Add `update-metrics` section after the existing `cr` alias:

```markdown
### `update-metrics` — Refresh Live Business Data

```bash
alias update-metrics='cd ~/Downloads/claude-workspace-evolved && python scripts/update_metrics.py'
```

Reads the current week's column from the Google Sheet KPI tracker and rewrites `context/current-data.md`. Run this before starting a session to ensure Claude has current numbers during `/prime`.

**Dry run (prints output, does not write file):**
```bash
python scripts/update_metrics.py --dry-run
```
```

**Files affected:**
- `shell-aliases.md` (modify)

---

### Step 11: Update `CLAUDE.md`

**Actions:**
- Add `scripts/` row to the Workspace Structure table:
  `scripts/ | update_metrics.py reads live KPI data from Google Sheet and writes current-data.md`
- Add a **Scripts** subsection to the Commands section:

```markdown
### update-metrics (shell alias)

**Purpose:** Pull live KPI data from the Google Sheet and refresh `context/current-data.md`.

Run before `/prime` when you need current numbers. Requires one-time setup in `scripts/SETUP.md`.

```bash
update-metrics
# or for a test run:
python scripts/update_metrics.py --dry-run
```
```

**Files affected:**
- `CLAUDE.md` (modify)

---

### Step 12: Validate

**Actions:**
- Confirm all files exist in `scripts/`
- Run `python scripts/update_metrics.py --dry-run` after credentials setup
- Confirm output matches expected KPI tab values for current week
- Confirm `current-data.md` is rewritten correctly after a live run
- Spot-check 3 formula cells in the KPI tab against manually counted raw tab data

**Files affected:** None — validation only

---

## Connections & Dependencies

- `context/current-data.md` — owned and rewritten by the script
- `shell-aliases.md` — updated with new alias
- `CLAUDE.md` — updated with script documentation
- Google Sheet — KPI tab formulas updated; GHL workflow added
- `scripts/.env` — updated with Sheets credentials

---

## Validation Checklist

- [ ] Step 1 source string values confirmed before formulas written
- [ ] COUNTIFS formulas added to all rows listed in Step 2
- [ ] Formulas produce correct values for past weeks (spot-check 2–3 weeks)
- [ ] GHL workflow "New Member → Active Members Sheet" created and tested with a dummy opportunity
- [ ] `scripts/google_credentials.json` in place
- [ ] `scripts/.env` updated with Sheets variables
- [ ] `python scripts/update_metrics.py --dry-run` runs without errors
- [ ] `current-data.md` rewritten correctly after live run
- [ ] `shell-aliases.md` updated
- [ ] `CLAUDE.md` updated

---

## Success Criteria

1. The only manual inputs to the KPI sheet each week are Cash Collected, NCC by source, and Ad Spend
2. Running `update-metrics` rewrites `context/current-data.md` with current-week data in under 10 seconds
3. `/prime` loads current metrics without any manual data entry beyond the three items above

---

## Notes

- **Fast Track penetration** (currently 10% of clients) is not a distinct row in the KPI tab. Once the Active Members tab is updated by the GHL workflow (Step 3), a formula can count members where Product/Tier contains "Fast Track" — add this as a row to the KPI tab if desired.
- **V2 additions**: PT utilisation (hours booked vs available), Trainerize adherence metrics. PT utilisation could come from a new GHL workflow counting PT calendar appointments per week into a new Sheet tab.
- **Ad spend automation (V3)**: Meta Ads API + Google Ads API to eliminate those last two manual entries. Significant additional scope.
- **SGPT Cancellations tab** has no date column — cannot use for weekly COUNTIFS. If the Membership Cancels (NEW) tab does not reliably capture SGPT cancels, a date column needs to be added to the SGPT Cancellations tab.
