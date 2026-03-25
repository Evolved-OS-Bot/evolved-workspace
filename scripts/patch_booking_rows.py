#!/usr/bin/env python3
"""
patch_booking_rows.py
Adds source-breakdown formulas to studio booking rows 46-48 and 53-54,
and hides unused rows 49-51 and 55.
One-time run.
"""

import os
import sys
from pathlib import Path
from datetime import date, datetime
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build

load_dotenv(Path(__file__).parent / ".env")

SCOPES         = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_ID = os.environ.get("GOOGLE_SPREADSHEET_ID")
KPI_SHEET_NAME = os.environ.get("GOOGLE_KPI_SHEET_NAME", "KPI's The Evolved")


def get_service():
    creds = service_account.Credentials.from_service_account_file(
        os.environ["GOOGLE_SHEETS_CREDENTIALS_FILE"], scopes=SCOPES
    )
    return build("sheets", "v4", credentials=creds)


def get_kpi_sheet_id(service):
    result = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    for sheet in result["sheets"]:
        if sheet["properties"]["title"] == KPI_SHEET_NAME:
            return sheet["properties"]["sheetId"]
    print(f"ERROR: Tab '{KPI_SHEET_NAME}' not found.")
    sys.exit(1)


def serial_to_date(val):
    """Convert a Google Sheets date serial number to a Python date."""
    from datetime import timedelta
    try:
        n = int(val)
        return (datetime(1899, 12, 30) + timedelta(days=n)).date()
    except (ValueError, TypeError):
        return None


def get_current_week_col(service):
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{KPI_SHEET_NAME}'!1:1",
        valueRenderOption="UNFORMATTED_VALUE",
    ).execute()
    header = result.get("values", [[]])[0]
    today = date.today()
    best_col, best_date = None, None
    for i, cell in enumerate(header):
        d = serial_to_date(cell)
        if d and d <= today and (best_date is None or d > best_date):
            best_date, best_col = d, i
    s, n = "", best_col + 1
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    print(f"Current week: {best_date} → column {s}")
    return best_col, s


def get_all_weekly_cols(service):
    """Returns sorted list of (col_idx, col_letter, col_date) for all weekly columns up to today."""
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{KPI_SHEET_NAME}'!1:1",
        valueRenderOption="UNFORMATTED_VALUE",
    ).execute()
    header = result.get("values", [[]])[0]
    today = date.today()
    cols = []
    for i, cell in enumerate(header):
        d = serial_to_date(cell)
        if d and date(2020, 1, 1) <= d <= today:
            s, n = "", i + 1
            while n:
                n, r = divmod(n - 1, 26)
                s = chr(65 + r) + s
            cols.append((i, s, d))
    return sorted(cols, key=lambda x: x[2])


def build_formulas(C):
    """Return the formulas dict for a given column letter C."""
    return {
        # Row 84: New Cash Collected — Organic
        84: (
            "=SUMIFS(Sales!$J:$J,Sales!$A:$A,\">=\"&" + C + "$1-7,Sales!$A:$A,\"<\"&" + C + "$1,Sales!$F:$F,\"Organic\")"
        ),
        # Row 85: NCC Meta Ads
        85: (
            "=SUMIFS(Sales!$J:$J,Sales!$A:$A,\">=\"&" + C + "$1-7,Sales!$A:$A,\"<\"&" + C + "$1,Sales!$F:$F,\"Paid Social - Meta\")"
        ),
        # Row 86: NCC Google Ads
        86: (
            "=SUMIFS(Sales!$J:$J,Sales!$A:$A,\">=\"&" + C + "$1-7,Sales!$A:$A,\"<\"&" + C + "$1,Sales!$F:$F,\"Paid Search - Google\")"
        ),
        # Row 88: Total New Cash Collected
        88: (
            "=SUMIFS(Sales!$J:$J,Sales!$A:$A,\">=\"&" + C + "$1-7,Sales!$A:$A,\"<\"&" + C + "$1)"
        ),
        # Row 89: Total NCC via Ads
        89: (
            "=SUMIFS(Sales!$J:$J,Sales!$A:$A,\">=\"&" + C + "$1-7,Sales!$A:$A,\"<\"&" + C + "$1,Sales!$F:$F,\"Paid*\")"
        ),

        # Row 57: Studio Bookings Attended via Meta Ads
        57: (
            "=COUNTIFS(Appointments!$H:$H,\">=\"&" + C + "$1-7,Appointments!$H:$H,\"<\"&" + C + "$1,Appointments!$K:$K,\"Y\",Appointments!$G:$G,\"Paid Social - Meta\")"
        ),
        # Row 58: Studio Bookings Attended via Google Ads
        58: (
            "=COUNTIFS(Appointments!$H:$H,\">=\"&" + C + "$1-7,Appointments!$H:$H,\"<\"&" + C + "$1,Appointments!$K:$K,\"Y\",Appointments!$G:$G,\"Paid Search - Google\")"
        ),
        # Row 59: Studio Bookings Attended via Organic
        59: (
            "=COUNTIFS(Appointments!$H:$H,\">=\"&" + C + "$1-7,Appointments!$H:$H,\"<\"&" + C + "$1,Appointments!$K:$K,\"Y\",Appointments!$G:$G,\"Organic\")"
        ),

        # Row 38: Leads via Organic
        38: (
            "=COUNTIFS(Appointments!$A:$A,\">=\"&" + C + "$1-7,Appointments!$A:$A,\"<\"&" + C + "$1,Appointments!$G:$G,\"Organic\")"
        ),
        # Row 39: Leads via Meta Ads
        39: (
            "=COUNTIFS(Appointments!$A:$A,\">=\"&" + C + "$1-7,Appointments!$A:$A,\"<\"&" + C + "$1,Appointments!$G:$G,\"Paid Social - Meta\")"
        ),
        # Row 40: Leads via Google Ads
        40: (
            "=COUNTIFS(Appointments!$A:$A,\">=\"&" + C + "$1-7,Appointments!$A:$A,\"<\"&" + C + "$1,Appointments!$G:$G,\"Paid Search - Google\")"
        ),

        # Studio booking source formulas — all filter on col H (Appointment Date)
        # Row 46: Studio Bookings via Meta Ads
        46: (
            "=COUNTIFS(Appointments!$H:$H,\">=\"&" + C + "$1-7,Appointments!$H:$H,\"<\"&" + C + "$1,Appointments!$G:$G,\"Paid Social - Meta\")"
        ),
        # Row 47: Studio Bookings via Google Ads
        47: (
            "=COUNTIFS(Appointments!$H:$H,\">=\"&" + C + "$1-7,Appointments!$H:$H,\"<\"&" + C + "$1,Appointments!$G:$G,\"Paid Search - Google\")"
        ),
        # Row 48: Studio Bookings via Website (organic)
        48: (
            "=COUNTIFS(Appointments!$H:$H,\">=\"&" + C + "$1-7,Appointments!$H:$H,\"<\"&" + C + "$1,Appointments!$G:$G,\"Organic\")"
        ),
        # Row 53: Studio Bookings Made Via ADS
        53: (
            "=COUNTIFS(Appointments!$H:$H,\">=\"&" + C + "$1-7,Appointments!$H:$H,\"<\"&" + C + "$1,Appointments!$G:$G,\"Paid*\")"
        ),
        # Row 54: Studio Bookings Made w/o ADS
        54: (
            "=COUNTIFS(Appointments!$H:$H,\">=\"&" + C + "$1-7,Appointments!$H:$H,\"<\"&" + C + "$1,Appointments!$G:$G,\"Organic\")"
        ),
    }


PROTECTED_ROWS = {53, 54, 88, 89}


def build_requests_for_col(sheet_id, col_idx, C):
    requests = []
    for row_1based, formula in build_formulas(C).items():
        if row_1based in PROTECTED_ROWS:
            continue
        requests.append({
            "updateCells": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": row_1based - 1,
                    "endRowIndex": row_1based,
                    "startColumnIndex": col_idx,
                    "endColumnIndex": col_idx + 1,
                },
                "rows": [{"values": [{"userEnteredValue": {"formulaValue": formula}}]}],
                "fields": "userEnteredValue",
            }
        })
    return requests


def main():
    ALL      = "--all" in sys.argv
    service  = get_service()
    sheet_id = get_kpi_sheet_id(service)

    if ALL:
        cols = get_all_weekly_cols(service)
        print(f"Writing formulas to {len(cols)} columns ({cols[0][2]} → {cols[-1][2]})...")
        all_requests = []
        for col_idx, C, col_date in cols:
            all_requests.extend(build_requests_for_col(sheet_id, col_idx, C))
        CHUNK = 1000
        for i in range(0, len(all_requests), CHUNK):
            service.spreadsheets().batchUpdate(
                spreadsheetId=SPREADSHEET_ID,
                body={"requests": all_requests[i:i + CHUNK]},
            ).execute()
        print(f"Done. All {len(cols)} weekly columns populated.")
    else:
        all_cols = get_all_weekly_cols(service)
        col_idx, C, col_date = all_cols[-1]
        print(f"Current week: {col_date} → column {C}")
        requests = build_requests_for_col(sheet_id, col_idx, C)
        service.spreadsheets().batchUpdate(
            spreadsheetId=SPREADSHEET_ID, body={"requests": requests}
        ).execute()
        print("Formulas written:")
        print("  NCC SUMIFS (Sales col J - Cash Taken): rows 84 (Organic), 85 (Meta Ads), 86 (Google Ads), 87 (Bark), 88 (Total), 89 (ADS total)")
        print("  Studio Bookings Attended (Appt Date + col K=Y): rows 57 (Meta Ads), 58 (Google Ads), 59 (Organic)")
        print("  Leads (Date Booked): rows 38 (Meta Ads), 39 (Google Ads), 40 (Organic)")
        print("  Studio Bookings (Appt Date): rows 46 (Meta Ads), 47 (Google Ads), 48 (Organic), 53 (Paid total), 54 (Organic total)")


if __name__ == "__main__":
    main()
