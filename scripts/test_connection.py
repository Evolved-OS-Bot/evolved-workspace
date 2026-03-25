#!/usr/bin/env python3
"""
test_connection.py
Verifies Google Sheets API credentials are working correctly.
Usage: python scripts/test_connection.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build

load_dotenv(Path(__file__).parent / ".env")

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def main():
    creds_file = os.environ.get("GOOGLE_SHEETS_CREDENTIALS_FILE")
    spreadsheet_id = os.environ.get("GOOGLE_SPREADSHEET_ID")

    if not creds_file or not Path(creds_file).exists():
        print(f"ERROR: Credentials file not found at '{creds_file}'")
        print("See scripts/SETUP.md Step 2.")
        sys.exit(1)

    try:
        creds = service_account.Credentials.from_service_account_file(
            creds_file, scopes=SCOPES
        )
        service = build("sheets", "v4", credentials=creds)
        result = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        title = result.get("properties", {}).get("title", "Unknown")
        sheets = [s["properties"]["title"] for s in result.get("sheets", [])]
        print(f"Connected successfully.")
        print(f"Spreadsheet: {title}")
        print(f"Tabs found: {', '.join(sheets)}")
    except Exception as e:
        print(f"ERROR: {e}")
        print("Check credentials and that the sheet is shared with the service account email.")
        sys.exit(1)


if __name__ == "__main__":
    main()
