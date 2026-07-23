from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

from .config import CURRENT_TRAINER_FULL_NAMES, Settings
from .kpi import WeeklyPTKPI


SHEETS_SCOPE = "https://www.googleapis.com/auth/spreadsheets"
HOURS_SECTION = "PT Booked Hours (automated from GHL)"
HOURS_TOTAL = "PT Booked Hours Total"
BOOKINGS_SECTION = "PT Bookings (automated from GHL)"
BOOKINGS_TOTAL = "PT Bookings Total"


def quote_sheet_name(name: str) -> str:
    return f"'{name.replace(chr(39), chr(39) * 2)}'"


def column_letter(index: int) -> str:
    if index < 1:
        raise ValueError("Spreadsheet column indexes are 1-based")
    result = ""
    while index:
        index, remainder = divmod(index - 1, 26)
        result = chr(65 + remainder) + result
    return result


def _sheet_date(value: Any) -> date | None:
    if isinstance(value, (int, float)):
        return (datetime(1899, 12, 30) + timedelta(days=int(value))).date()
    text = str(value or "").strip()
    for pattern in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%-m/%-d/%Y"):
        try:
            return datetime.strptime(text, pattern).date()
        except (ValueError, TypeError):
            continue
    return None


class SheetsKPIWriter:
    def __init__(self, settings: Settings, service=None):
        self.settings = settings
        self.service = service or self._build_service()

    def _build_service(self):
        try:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build
        except ImportError as exc:
            raise RuntimeError(
                "Google Sheets dependencies are required when KPI_WRITE_ENABLED=true"
            ) from exc

        credentials = None
        if self.settings.google_service_account_json:
            try:
                info = json.loads(self.settings.google_service_account_json)
            except json.JSONDecodeError as exc:
                raise RuntimeError("GOOGLE_SERVICE_ACCOUNT_JSON is not valid JSON") from exc
            credentials = service_account.Credentials.from_service_account_info(
                info, scopes=[SHEETS_SCOPE]
            )
        elif self.settings.google_credentials_file:
            path = Path(self.settings.google_credentials_file)
            if not path.is_absolute() and not path.exists():
                workspace_candidate = Path.cwd() / "scripts" / path
                if workspace_candidate.exists():
                    path = workspace_candidate
            if not path.exists():
                raise RuntimeError(f"Google credentials file does not exist: {path}")
            credentials = service_account.Credentials.from_service_account_file(
                str(path), scopes=[SHEETS_SCOPE]
            )
        else:
            raise RuntimeError(
                "Set GOOGLE_SERVICE_ACCOUNT_JSON or GOOGLE_SHEETS_CREDENTIALS_FILE "
                "when KPI_WRITE_ENABLED=true"
            )
        return build("sheets", "v4", credentials=credentials, cache_discovery=False)

    def _read_layout(self) -> tuple[list[Any], list[str]]:
        sheet = quote_sheet_name(self.settings.google_kpi_sheet_name)
        result = (
            self.service.spreadsheets()
            .values()
            .batchGet(
                spreadsheetId=self.settings.google_spreadsheet_id,
                ranges=[f"{sheet}!1:1", f"{sheet}!A1:A250"],
                valueRenderOption="UNFORMATTED_VALUE",
            )
            .execute()
        )
        ranges = result.get("valueRanges") or []
        if len(ranges) != 2:
            raise RuntimeError("Could not read the KPI header and label column")
        header = (ranges[0].get("values") or [[]])[0]
        label_rows = ranges[1].get("values") or []
        labels = [str(row[0]).strip() if row else "" for row in label_rows]
        return header, labels

    def read_values(self, sheet_name: str, cell_range: str) -> list[list[Any]]:
        sheet = quote_sheet_name(sheet_name)
        result = (
            self.service.spreadsheets()
            .values()
            .get(
                spreadsheetId=self.settings.google_spreadsheet_id,
                range=f"{sheet}!{cell_range}",
                valueRenderOption="FORMATTED_VALUE",
            )
            .execute()
        )
        return result.get("values") or []

    @staticmethod
    def _unique_row(labels: list[str], label: str) -> int:
        matches = [index + 1 for index, value in enumerate(labels) if value == label]
        if len(matches) != 1:
            raise RuntimeError(
                f"Expected one KPI row labelled {label!r}; found {len(matches)}"
            )
        return matches[0]

    @staticmethod
    def _week_column(header: list[Any], week_start: date) -> int:
        matches = [
            index + 1
            for index, value in enumerate(header)
            if _sheet_date(value) == week_start
        ]
        if len(matches) != 1:
            raise RuntimeError(
                f"Expected one KPI column for {week_start.isoformat()}; found {len(matches)}"
            )
        return matches[0]

    def _block_rows(
        self, labels: list[str], section_label: str, total_label: str
    ) -> tuple[dict[str, int], int]:
        section_row = self._unique_row(labels, section_label)
        rows: dict[str, int] = {}
        for offset, trainer in enumerate(
            CURRENT_TRAINER_FULL_NAMES.values(), start=1
        ):
            row = section_row + offset
            actual = labels[row - 1] if row - 1 < len(labels) else ""
            if actual != trainer:
                raise RuntimeError(
                    f"Expected {trainer!r} at row {row} below {section_label!r}; "
                    f"found {actual!r}"
                )
            rows[trainer] = row
        total_row = section_row + len(CURRENT_TRAINER_FULL_NAMES) + 1
        actual_total = labels[total_row - 1] if total_row - 1 < len(labels) else ""
        if actual_total != total_label:
            raise RuntimeError(
                f"Expected {total_label!r} at row {total_row}; found {actual_total!r}"
            )
        return rows, total_row

    def write(self, kpi: WeeklyPTKPI) -> dict:
        header, labels = self._read_layout()
        column = self._week_column(header, kpi.week_start)
        column_name = column_letter(column)
        hours_rows, hours_total_row = self._block_rows(
            labels, HOURS_SECTION, HOURS_TOTAL
        )
        bookings_rows, bookings_total_row = self._block_rows(
            labels, BOOKINGS_SECTION, BOOKINGS_TOTAL
        )

        data = []
        sheet = quote_sheet_name(self.settings.google_kpi_sheet_name)
        for short_name, full_name in CURRENT_TRAINER_FULL_NAMES.items():
            item = kpi.trainers[short_name]
            data.extend(
                [
                    {
                        "range": (
                            f"{sheet}!{column_name}{hours_rows[full_name]}"
                        ),
                        "values": [[item.booked_hours]],
                    },
                    {
                        "range": (
                            f"{sheet}!{column_name}{bookings_rows[full_name]}"
                        ),
                        "values": [[item.bookings]],
                    },
                ]
            )
        data.extend(
            [
                {
                    "range": (
                        f"{sheet}!{column_name}{hours_total_row}"
                    ),
                    "values": [[kpi.total_booked_hours]],
                },
                {
                    "range": (
                        f"{sheet}!{column_name}{bookings_total_row}"
                    ),
                    "values": [[kpi.total_bookings]],
                },
            ]
        )
        (
            self.service.spreadsheets()
            .values()
            .batchUpdate(
                spreadsheetId=self.settings.google_spreadsheet_id,
                body={"valueInputOption": "USER_ENTERED", "data": data},
            )
            .execute()
        )
        return {
            "week_start": kpi.week_start.isoformat(),
            "column": column_name,
            "updated_cells": len(data),
            "kpi": kpi.to_dict(),
        }
