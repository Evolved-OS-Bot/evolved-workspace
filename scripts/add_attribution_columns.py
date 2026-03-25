#!/usr/bin/env python3
"""
add_attribution_columns.py
Appends 'First Attribution Channel' and 'Referrer' columns to the
Appointments, Sales, and Subscribers sheets.
One-time run.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build

load_dotenv(Path(__file__).parent / ".env")

SCOPES         = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_ID = os.environ["GOOGLE_SPREADSHEET_ID"]

NEW_HEADERS = ["First Attribution Channel", "Referrer"]

TARGET_SHEETS = ["Appointments", "Sales", "Subscribes"]


def get_service():
    creds = service_account.Credentials.from_service_account_file(
        os.environ["GOOGLE_SHEETS_CREDENTIALS_FILE"], scopes=SCOPES
    )
    return build("sheets", "v4", credentials=creds)


def get_header_row(service, sheet_name):
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{sheet_name}'!1:1",
    ).execute()
    return result.get("values", [[]])[0]


def col_letter(n):
    """Convert 1-based column index to letter(s)."""
    s = ""
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def main():
    service = get_service()

    # Verify sheet names exist
    meta = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    sheet_names = [s["properties"]["title"] for s in meta["sheets"]]

    for sheet in TARGET_SHEETS:
        if sheet not in sheet_names:
            # Try case-insensitive match
            match = next((s for s in sheet_names if s.lower() == sheet.lower()), None)
            if not match:
                print(f"WARNING: Sheet '{sheet}' not found. Available: {sheet_names}")
                continue
            sheet = match

        headers = get_header_row(service, sheet)
        next_col = len(headers) + 1

        # Check if already added
        if "First Attribution Channel" in headers:
            print(f"{sheet}: columns already present, skipping.")
            continue

        col_start = col_letter(next_col)
        col_end   = col_letter(next_col + len(NEW_HEADERS) - 1)
        range_str = f"'{sheet}'!{col_start}1:{col_end}1"

        service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=range_str,
            valueInputOption="RAW",
            body={"values": [NEW_HEADERS]},
        ).execute()

        print(f"{sheet}: added '{NEW_HEADERS[0]}' ({col_start}) and '{NEW_HEADERS[1]}' ({col_letter(next_col + 1)}) — was {len(headers)} columns, now {len(headers) + 2}")


if __name__ == "__main__":
    main()
