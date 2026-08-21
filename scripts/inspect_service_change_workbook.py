#!/usr/bin/env python3
"""Read-only header inspection for service-change workbook integration."""

from __future__ import annotations

import json
import os
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build


WORKSPACE = Path(__file__).resolve().parents[1]
ENV_FILE = WORKSPACE / "scripts" / ".env"
TARGET_TABS = (
    "Active Online",
    "Active SGPT",
    "Active PT",
    "Sales",
    "SGPT Cancellations",
    "PT Cancellations",
)


def load_env() -> None:
    for raw_line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


def main() -> int:
    load_env()
    credential_path = Path(os.environ["GOOGLE_SHEETS_CREDENTIALS_FILE"])
    if not credential_path.is_absolute():
        credential_path = ENV_FILE.parent / credential_path
    credentials = service_account.Credentials.from_service_account_file(
        credential_path,
        scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"],
    )
    sheets = build(
        "sheets",
        "v4",
        credentials=credentials,
        cache_discovery=False,
    )
    spreadsheet_id = os.environ["GOOGLE_SPREADSHEET_ID"]
    metadata = (
        sheets.spreadsheets()
        .get(
            spreadsheetId=spreadsheet_id,
            fields=(
                "spreadsheetId,properties.title,"
                "sheets(properties(sheetId,title,"
                "gridProperties(rowCount,columnCount,frozenRowCount)))"
            ),
        )
        .execute()
    )
    visible = {
        item["properties"]["title"]: item["properties"]
        for item in metadata.get("sheets", [])
    }
    output = {
        "spreadsheet_id": metadata["spreadsheetId"],
        "title": metadata["properties"]["title"],
        "tabs": {},
    }
    for title in TARGET_TABS:
        if title not in visible:
            output["tabs"][title] = {"status": "missing"}
            continue
        rows = (
            sheets.spreadsheets()
            .values()
            .get(
                spreadsheetId=spreadsheet_id,
                range=f"'{title}'!A1:Z3",
                valueRenderOption="FORMATTED_VALUE",
            )
            .execute()
            .get("values", [])
        )
        output["tabs"][title] = {
            "properties": visible[title],
            "header_candidates": [
                {"row": index, "values": row}
                for index, row in enumerate(rows, start=1)
            ],
        }
    print(json.dumps(output, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
