"""
sheets_client.py
Authenticates with Google Sheets API using a service account
and reads the KPI tab.
"""

import os
import json
import time
from pathlib import Path
from datetime import date, datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


SCRIPTS_DIR = Path(__file__).parent


def get_sheets_service():
    credentials_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "").strip()
    if credentials_json:
        creds = service_account.Credentials.from_service_account_info(
            json.loads(credentials_json), scopes=SCOPES
        )
    else:
        creds_file = os.environ["GOOGLE_SHEETS_CREDENTIALS_FILE"]
        creds_path = (
            Path(creds_file)
            if Path(creds_file).is_absolute()
            else SCRIPTS_DIR / creds_file
        )
        creds = service_account.Credentials.from_service_account_file(
            str(creds_path), scopes=SCOPES
        )
    return build("sheets", "v4", credentials=creds)


def read_sheet(sheet_name, cell_range, formatted=False):
    """
    Reads a range from the spreadsheet.
    Returns list of rows (each row is a list of cell values).
    Pass formatted=True to get display strings instead of raw values.
    """
    service = get_sheets_service()
    spreadsheet_id = os.environ["GOOGLE_SPREADSHEET_ID"]
    render_option = "FORMATTED_VALUE" if formatted else "UNFORMATTED_VALUE"
    request = (
        service.spreadsheets()
        .values()
        .get(
            spreadsheetId=spreadsheet_id,
            range=f"'{sheet_name}'!{cell_range}",
            valueRenderOption=render_option,
        )
    )
    for attempt in range(3):
        try:
            result = request.execute()
            break
        except Exception:
            if attempt == 2:
                raise
            time.sleep(2**attempt)
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


def read_ytd_revenue():
    """Read the YTD cash total from cell C106 of the KPI sheet."""
    rows = read_sheet("KPI's The Evolved", "C106:C106")
    try:
        val = rows[0][0]
        return float(str(val).replace("$", "").replace(",", ""))
    except (IndexError, ValueError, TypeError):
        return None


def read_appointments_this_week():
    """
    Read this week's appointments from the Appointments tab.
    Returns a list of dicts sorted by appointment datetime.
    Week runs Monday to Sunday.
    """
    today  = date.today()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)

    rows = read_sheet("Appointments", "A2:K500", formatted=True)
    appointments = []
    for row in rows:
        if len(row) < 8:
            continue
        apt_date_str = str(row[7]).strip()
        if not apt_date_str:
            continue
        try:
            apt_dt = datetime.strptime(apt_date_str, "%A, %B %d, %Y %H:%M")
            if monday <= apt_dt.date() <= sunday:
                appointments.append({
                    "first_name":   str(row[1]).strip() if len(row) > 1 else "",
                    "last_name":    str(row[2]).strip() if len(row) > 2 else "",
                    "source":       str(row[6]).strip() if len(row) > 6 else "",
                    "datetime":     apt_dt,
                    "sales_person": str(row[8]).strip() if len(row) > 8 else "",
                    "pre_qual":     str(row[9]).strip() if len(row) > 9 else "",
                    "showed":       str(row[10]).strip() if len(row) > 10 else "",
                })
        except (ValueError, IndexError):
            continue

    return sorted(appointments, key=lambda x: x["datetime"])


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
