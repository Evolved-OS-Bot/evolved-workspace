"""
sheets_client.py
Authenticates with Google Sheets API using a service account
and reads the KPI tab.
"""

import os
from pathlib import Path
from datetime import date, datetime, timedelta
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
            valueRenderOption="UNFORMATTED_VALUE",
        )
        .execute()
    )
    return result.get("values", [])


def serial_to_date(val):
    """Convert a Google Sheets date serial number to a Python date."""
    try:
        n = int(val)
        d = (datetime(1899, 12, 30) + timedelta(days=n)).date()
        if date(2020, 1, 1) <= d <= date(2035, 1, 1):
            return d
    except (ValueError, TypeError):
        pass
    return None


def find_current_week_col(rows):
    """
    Scans row 1 for the most recent date <= today.
    Returns (col_index, week_date).
    """
    today = date.today()
    header_row = rows[0] if rows else []
    best_col, best_date = None, None

    for i, cell in enumerate(header_row):
        d = serial_to_date(cell)
        if d and d <= today:
            if best_date is None or d > best_date:
                best_date = d
                best_col = i

    return best_col, best_date
