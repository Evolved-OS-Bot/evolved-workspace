#!/usr/bin/env python3
"""
insert_formulas.py
One-time script: writes all COUNTIFS formulas into the KPI tab.
Safe to re-run — only overwrites the designated formula cells.

Usage: python scripts/insert_formulas.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build

load_dotenv(Path(__file__).parent / ".env")

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_ID = os.environ.get("GOOGLE_SPREADSHEET_ID")
KPI_SHEET_NAME = os.environ.get("GOOGLE_KPI_SHEET_NAME", "KPI's The Evolved")

# Column F is index 5 (0-based). Formulas use F$1 as the week anchor.
# When entered in col F and dragged right, $1 stays fixed (row) but
# the column shifts — giving each weekly column its own date anchor.

# All formulas reference col F — enter in F{row} and drag across.
# Row numbers are 1-based as they appear in the sheet.

SGPT = "'Active SGPT'"   # SGPT members tab — G=Tier, H=Status
PT   = "'Active PT'"    # PT clients tab — F=Personal Trainer, no Status col (all active)

FORMULAS = {
    # ── Active Members (waterfall: baseline + cumulative sales - cumulative cancels) ──
    # Baseline values are in col E (E17 for SGPT, E25 for PT) — set once, never change.
    # Formulas count ALL sales/cancels up to (but not including) this column's date,
    # so each column shows the historically correct active count at that point in time.
    17: (
        "=$E$17"
        "+COUNTIFS(Sales!$A:$A,\"<\"&F$1,Sales!$G:$G,\"Bronze\")"
        "+COUNTIFS(Sales!$A:$A,\"<\"&F$1,Sales!$G:$G,\"Silver\")"
        "+COUNTIFS(Sales!$A:$A,\"<\"&F$1,Sales!$G:$G,\"LIMITED*\")"
        "-COUNTIFS('SGPT Cancellations'!$A:$A,\"<\"&F$1)"
    ),
    # Per-trainer PT client counts — live count from Active PT tab (current snapshot).
    # Historical per-trainer tracking requires a Trainer column in PT Cancellations — add later.
    19: f"=COUNTIF({PT}!$F:$F,\"Leisa Smith\")",
    20: f"=COUNTIF({PT}!$F:$F,\"Beth Fry\")",
    21: f"=COUNTIF({PT}!$F:$F,\"Piper Mae\")",
    22: f"=COUNTIF({PT}!$F:$F,\"Marnie Chapple\")",
    23: f"=COUNTIF({PT}!$F:$F,\"Hannah Altmann\")",
    24: f"=COUNTIF({PT}!$F:$F,\"Megan Brown\")",
    # Total active PT clients — waterfall: baseline + cumulative PT sales - cumulative PT cancels
    25: (
        "=$E$25"
        "+COUNTIFS(Sales!$A:$A,\"<\"&F$1,Sales!$G:$G,\"PT*\")"
        "+COUNTIFS(Sales!$A:$A,\"<\"&F$1,Sales!$G:$G,\"Silver\")"
        "-COUNTIFS('PT Cancellations'!$A:$A,\"<\"&F$1)"
    ),

    # ── Subscribes ───────────────────────────────────────────────────────
    33: "=COUNTIFS(Subscribes!$A:$A,\">=\"&F$1-7,Subscribes!$A:$A,\"<\"&F$1,Subscribes!$D:$D,\"Organic\")",
    34: "=COUNTIFS(Subscribes!$A:$A,\">=\"&F$1-7,Subscribes!$A:$A,\"<\"&F$1,Subscribes!$D:$D,\"Paid*\")",
    35: "=COUNTIFS(Subscribes!$A:$A,\">=\"&F$1-7,Subscribes!$A:$A,\"<\"&F$1)",

    # ── Leads — counted by Date Booked (col A) ───────────────────────────
    41: "=COUNTIFS(Appointments!$A:$A,\">=\"&F$1-7,Appointments!$A:$A,\"<\"&F$1,Appointments!$G:$G,\"Paid*\")",
    42: "=COUNTIFS(Appointments!$A:$A,\">=\"&F$1-7,Appointments!$A:$A,\"<\"&F$1)",

    # ── Studio Bookings — counted by Appointment Date (col H) ────────────
    52: "=COUNTIFS(Appointments!$H:$H,\">=\"&F$1-7,Appointments!$H:$H,\"<\"&F$1)",
    55: "=F53+F54",
    # Rows 57-59 (Attended by source) are owned by patch_booking_rows.py
    60: "=COUNTIFS(Appointments!$H:$H,\">=\"&F$1-7,Appointments!$H:$H,\"<\"&F$1,Appointments!$K:$K,\"Y\")",
    61: "=IFERROR((F57+F58)/F53,\"—\")",
    62: "=IFERROR(F59/F54,\"—\")",
    63: "=IFERROR(F60/F52,\"—\")",

    # ── SGPT Sales (rows 64–70) ───────────────────────────────────────────
    # Row 64: SGPT Via Meta Ads
    64: (
        "=COUNTIFS(Sales!$A:$A,\">=\"&F$1-7,Sales!$A:$A,\"<\"&F$1,Sales!$G:$G,\"Bronze\",Sales!$F:$F,\"Paid Social - Meta\")"
        "+COUNTIFS(Sales!$A:$A,\">=\"&F$1-7,Sales!$A:$A,\"<\"&F$1,Sales!$G:$G,\"Silver\",Sales!$F:$F,\"Paid Social - Meta\")"
    ),
    # Row 65: SGPT Via Google Ads
    65: (
        "=COUNTIFS(Sales!$A:$A,\">=\"&F$1-7,Sales!$A:$A,\"<\"&F$1,Sales!$G:$G,\"Bronze\",Sales!$F:$F,\"Paid Search - Google\")"
        "+COUNTIFS(Sales!$A:$A,\">=\"&F$1-7,Sales!$A:$A,\"<\"&F$1,Sales!$G:$G,\"Silver\",Sales!$F:$F,\"Paid Search - Google\")"
    ),
    # Row 66: SGPT Via Website (organic)
    66: (
        "=COUNTIFS(Sales!$A:$A,\">=\"&F$1-7,Sales!$A:$A,\"<\"&F$1,Sales!$G:$G,\"Bronze\",Sales!$F:$F,\"Organic\")"
        "+COUNTIFS(Sales!$A:$A,\">=\"&F$1-7,Sales!$A:$A,\"<\"&F$1,Sales!$G:$G,\"Silver\",Sales!$F:$F,\"Organic\")"
    ),
    # Row 70: SGPT Sales Total
    70: (
        "=COUNTIFS(Sales!$A:$A,\">=\"&F$1-7,Sales!$A:$A,\"<\"&F$1,Sales!$G:$G,\"Bronze\")"
        "+COUNTIFS(Sales!$A:$A,\">=\"&F$1-7,Sales!$A:$A,\"<\"&F$1,Sales!$G:$G,\"Silver\")"
    ),

    # ── PT Sales (rows 71–77) ─────────────────────────────────────────────
    # Row 71: PT Via Meta Ads
    71: (
        "=COUNTIFS(Sales!$A:$A,\">=\"&F$1-7,Sales!$A:$A,\"<\"&F$1,Sales!$G:$G,\"PT*\",Sales!$F:$F,\"Paid Social - Meta\")"
        "+COUNTIFS(Sales!$A:$A,\">=\"&F$1-7,Sales!$A:$A,\"<\"&F$1,Sales!$G:$G,\"Silver\",Sales!$F:$F,\"Paid Social - Meta\")"
    ),
    # Row 72: PT Via Google Ads
    72: (
        "=COUNTIFS(Sales!$A:$A,\">=\"&F$1-7,Sales!$A:$A,\"<\"&F$1,Sales!$G:$G,\"PT*\",Sales!$F:$F,\"Paid Search - Google\")"
        "+COUNTIFS(Sales!$A:$A,\">=\"&F$1-7,Sales!$A:$A,\"<\"&F$1,Sales!$G:$G,\"Silver\",Sales!$F:$F,\"Paid Search - Google\")"
    ),
    # Row 73: PT Via Website (organic)
    73: (
        "=COUNTIFS(Sales!$A:$A,\">=\"&F$1-7,Sales!$A:$A,\"<\"&F$1,Sales!$G:$G,\"PT*\",Sales!$F:$F,\"Organic\")"
        "+COUNTIFS(Sales!$A:$A,\">=\"&F$1-7,Sales!$A:$A,\"<\"&F$1,Sales!$G:$G,\"Silver\",Sales!$F:$F,\"Organic\")"
    ),
    # Row 77: PT Sales Total
    77: (
        "=COUNTIFS(Sales!$A:$A,\">=\"&F$1-7,Sales!$A:$A,\"<\"&F$1,Sales!$G:$G,\"PT*\")"
        "+COUNTIFS(Sales!$A:$A,\">=\"&F$1-7,Sales!$A:$A,\"<\"&F$1,Sales!$G:$G,\"Silver\")"
    ),

    # ── Sales totals ──────────────────────────────────────────────────────
    78: "=COUNTIFS(Sales!$A:$A,\">=\"&F$1-7,Sales!$A:$A,\"<\"&F$1,Sales!$F:$F,\"Paid*\")",
    79: "=COUNTIFS(Sales!$A:$A,\">=\"&F$1-7,Sales!$A:$A,\"<\"&F$1,Sales!$F:$F,\"Organic\")",
    80: "=COUNTIFS(Sales!$A:$A,\">=\"&F$1-7,Sales!$A:$A,\"<\"&F$1)",

    # ── Cancels ───────────────────────────────────────────────────────────
    89: "=COUNTIFS('SGPT Cancellations'!$A:$A,\">=\"&F$1-7,'SGPT Cancellations'!$A:$A,\"<\"&F$1)",
    90: "=COUNTIFS('PT Cancellations'!$A:$A,\">=\"&F$1-7,'PT Cancellations'!$A:$A,\"<\"&F$1)",

    # ── Gained / Lost ─────────────────────────────────────────────────────
    93: "=F70-F89",
    94: "=F77-F90",
}


def get_service():
    creds_file = os.environ.get("GOOGLE_SHEETS_CREDENTIALS_FILE")
    if not creds_file or not Path(creds_file).exists():
        print(f"ERROR: Credentials file not found at '{creds_file}'")
        print("Run scripts/SETUP.md steps 1-3 first.")
        sys.exit(1)
    creds = service_account.Credentials.from_service_account_file(
        creds_file, scopes=SCOPES
    )
    return build("sheets", "v4", credentials=creds)


def get_kpi_sheet_id(service):
    result = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    for sheet in result.get("sheets", []):
        if sheet["properties"]["title"] == KPI_SHEET_NAME:
            return sheet["properties"]["sheetId"]
    print(f"ERROR: Tab '{KPI_SHEET_NAME}' not found.")
    print("Available tabs:", [s["properties"]["title"] for s in result.get("sheets", [])])
    sys.exit(1)


def col_idx_to_letter(col_idx):
    s, n = "", col_idx + 1
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def parse_header_date(cell):
    """Parse a cell value as a date — handles Google Sheets serials and common string formats."""
    from datetime import datetime, timedelta, date
    # Serial number (Google Sheets stores dates as integers)
    try:
        d = (datetime(1899, 12, 30) + timedelta(days=int(cell))).date()
        if date(2020, 1, 1) <= d <= date(2035, 1, 1):  # sanity check
            return d
    except (ValueError, TypeError):
        pass
    # String formats
    for fmt in ("%m/%d/%Y", "%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(str(cell).strip(), fmt).date()
        except ValueError:
            continue
    return None


def get_all_weekly_cols(service):
    """Returns list of (col_idx, col_letter, col_date) for all weekly columns up to today."""
    from datetime import date
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{KPI_SHEET_NAME}'!1:1",
        valueRenderOption="UNFORMATTED_VALUE",
    ).execute()
    header = result.get("values", [[]])[0]
    today = date.today()
    cols = []
    for i, cell in enumerate(header):
        d = parse_header_date(cell)
        if d and d <= today:
            cols.append((i, col_idx_to_letter(i), d))
    return sorted(cols, key=lambda x: x[2])


# Rows protected in the sheet — skip to avoid 400 errors
PROTECTED_ROWS = {17, 25, 35, 41, 42, 52, 55, 60, 61, 62, 63, 70, 77, 78, 79, 80, 89, 93, 94}


def build_requests_for_col(sheet_id, col_idx):
    """Generate all formula update requests for a single weekly column."""
    col_letter = col_idx_to_letter(col_idx)
    requests = []
    for row_1based, formula in FORMULAS.items():
        if row_1based in PROTECTED_ROWS:
            continue
        f = (formula
             .replace("F$1",  f"{col_letter}$1")
             .replace("F52",  f"{col_letter}52")
             .replace("F53",  f"{col_letter}53")
             .replace("F54",  f"{col_letter}54")
             .replace("F55",  f"{col_letter}55")
             .replace("F57",  f"{col_letter}57")
             .replace("F58",  f"{col_letter}58")
             .replace("F59",  f"{col_letter}59")
             .replace("F60",  f"{col_letter}60")
             .replace("F70",  f"{col_letter}70")
             .replace("F77",  f"{col_letter}77")
             .replace("F89",  f"{col_letter}89")
             .replace("F90",  f"{col_letter}90"))
        requests.append({
            "updateCells": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": row_1based - 1,
                    "endRowIndex": row_1based,
                    "startColumnIndex": col_idx,
                    "endColumnIndex": col_idx + 1,
                },
                "rows": [{"values": [{"userEnteredValue": {"formulaValue": f}}]}],
                "fields": "userEnteredValue",
            }
        })
    # Clear rows that had wrong formulas or are now hidden/unused
    for row_1based in [r for r in [63, 67, 68, 69, 74, 75, 76] if r not in PROTECTED_ROWS]:
        requests.append({
            "updateCells": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": row_1based - 1,
                    "endRowIndex": row_1based,
                    "startColumnIndex": col_idx,
                    "endColumnIndex": col_idx + 1,
                },
                "rows": [{"values": [{"userEnteredValue": {"stringValue": ""}}]}],
                "fields": "userEnteredValue",
            }
        })
    return requests


def hide_rows_requests(sheet_id):
    """Requests to hide obsolete breakdown rows (Email, Referrals, Social Media)."""
    requests = []
    for start, end in [(66, 69), (73, 76)]:  # rows 67-69 and 74-76 (0-based)
        requests.append({
            "updateDimensionProperties": {
                "range": {"sheetId": sheet_id, "dimension": "ROWS",
                          "startIndex": start, "endIndex": end},
                "properties": {"hiddenByUser": True},
                "fields": "hiddenByUser",
            }
        })
    return requests


def send_requests(service, requests):
    """Send batchUpdate requests in chunks to avoid API limits."""
    CHUNK = 1000
    for i in range(0, len(requests), CHUNK):
        service.spreadsheets().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body={"requests": requests[i:i + CHUNK]},
        ).execute()


def main():
    ALL = "--all" in sys.argv
    service = get_service()
    sheet_id = get_kpi_sheet_id(service)

    if ALL:
        cols = get_all_weekly_cols(service)
        if not cols:
            print("ERROR: No weekly columns found.")
            sys.exit(1)
        print(f"Writing formulas to {len(cols)} columns ({cols[0][2]} → {cols[-1][2]})...")
        all_requests = []
        for col_idx, col_letter, col_date in cols:
            all_requests.extend(build_requests_for_col(sheet_id, col_idx))
        send_requests(service, all_requests)
        print(f"Done. All {len(cols)} weekly columns populated.")
    else:
        cols = get_all_weekly_cols(service)
        if not cols:
            print("ERROR: No weekly columns found.")
            sys.exit(1)
        col_idx, col_letter, col_date = cols[-1]  # most recent
        print(f"Current week: {col_date} → column {col_letter} (index {col_idx})")
        requests = build_requests_for_col(sheet_id, col_idx)
        print(f"Writing {len(requests)} formulas to '{KPI_SHEET_NAME}' column {col_letter}...")
        send_requests(service, requests)
        print(f"Done. Open the KPI tab, select the formula cells in column {col_letter}, and drag right for future weeks.")




if __name__ == "__main__":
    main()
