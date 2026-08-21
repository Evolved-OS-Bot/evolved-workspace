from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

from google.oauth2 import service_account
from googleapiclient.discovery import build


SA_ATTENDANCE_HEADERS = (
    "Appointment ID",
    "Contact ID",
    "Scheduled Start",
    "Scheduled End",
    "Appointment Owner",
    "Delivered By",
    "Canonical Status",
    "Status Effective Time",
    "Status Source",
    "Feedback Submitted Time",
    "Conversion Evidence",
    "Reconciliation State",
    "Exception Owner",
    "Last Observed Time",
    "Rule Version",
)

SHEETS_SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def build_sheets_service(
    service_account_json: str | None = None,
) -> Any:
    credentials_json = (
        service_account_json
        or os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "").strip()
    )
    if credentials_json:
        credentials = service_account.Credentials.from_service_account_info(
            json.loads(credentials_json),
            scopes=SHEETS_SCOPES,
        )
    else:
        credentials_file = os.getenv(
            "GOOGLE_SHEETS_CREDENTIALS_FILE", ""
        ).strip()
        if not credentials_file:
            raise RuntimeError(
                "Google Sheets credentials are not configured"
            )
        credentials = service_account.Credentials.from_service_account_file(
            str(Path(credentials_file).expanduser()),
            scopes=SHEETS_SCOPES,
        )
    return build("sheets", "v4", credentials=credentials)


def row_values(row: dict[str, Any]) -> list[Any]:
    exception_owner = (
        "Admin Eve" if row.get("exception_code") else ""
    )
    return [
        row["appointment_id"],
        row["contact_id"],
        row["start_at"],
        row["end_at"],
        row.get("assigned_user_id") or "",
        row.get("delivered_by") or "",
        row.get("canonical_status") or row.get("status") or "unknown",
        row.get("updated_at") or row.get("observed_at") or "",
        "GHL appointment",
        row.get("feedback_submitted_at") or "",
        row.get("conversion_evidence") or "",
        row.get("reconciliation_state") or "",
        exception_owner,
        row.get("observed_at") or "",
        row.get("rule_version") or "",
    ]


def validate_layout(headers: Iterable[Any]) -> None:
    actual = tuple(str(value or "").strip() for value in headers)
    if actual != SA_ATTENDANCE_HEADERS:
        raise ValueError(
            "SA Attendance layout mismatch; refusing to write"
        )


def build_upsert_plan(
    existing_rows: list[list[Any]],
    attendance_rows: Iterable[dict[str, Any]],
    *,
    sheet_name: str = "SA Attendance",
) -> dict[str, Any]:
    if not existing_rows:
        raise ValueError("SA Attendance tab is empty")
    validate_layout(existing_rows[0])
    positions: dict[str, int] = {}
    for row_number, values in enumerate(existing_rows[1:], start=2):
        appointment_id = str(values[0] if values else "").strip()
        if not appointment_id:
            continue
        if appointment_id in positions:
            raise ValueError(
                f"duplicate Appointment ID in SA Attendance: {appointment_id}"
            )
        positions[appointment_id] = row_number

    updates = []
    appends = []
    seen: set[str] = set()
    for item in attendance_rows:
        appointment_id = str(item.get("appointment_id") or "").strip()
        if not appointment_id:
            raise ValueError("attendance row requires appointment_id")
        if appointment_id in seen:
            raise ValueError(
                f"duplicate attendance appointment_id: {appointment_id}"
            )
        seen.add(appointment_id)
        values = row_values(item)
        if appointment_id in positions:
            row_number = positions[appointment_id]
            current = list(existing_rows[row_number - 1])
            current.extend([""] * (len(SA_ATTENDANCE_HEADERS) - len(current)))
            current = current[: len(SA_ATTENDANCE_HEADERS)]
            if [str(value or "") for value in current] != [
                str(value or "") for value in values
            ]:
                updates.append(
                    {
                        "range": (
                            f"'{sheet_name}'!A{row_number}:O{row_number}"
                        ),
                        "values": [values],
                        "precondition": current,
                    }
                )
        else:
            appends.append(values)
    return {"updates": updates, "appends": appends}


class SAAttendanceSheetPublisher:
    def __init__(
        self,
        service: Any,
        spreadsheet_id: str,
        *,
        sheet_name: str = "SA Attendance",
        sheet_id: int | None,
        write_enabled: bool = False,
    ):
        self.service = service
        self.spreadsheet_id = spreadsheet_id
        self.sheet_name = sheet_name
        self.sheet_id = sheet_id
        self.write_enabled = write_enabled

    def _metadata(self) -> dict[str, Any]:
        return (
            self.service.spreadsheets()
            .get(
                spreadsheetId=self.spreadsheet_id,
                fields="sheets.properties",
            )
            .execute()
        )

    def resolve_sheet_id(self) -> int:
        matching = [
            item["properties"]
            for item in self._metadata().get("sheets", [])
            if item["properties"]["title"] == self.sheet_name
        ]
        if len(matching) != 1:
            raise ValueError(
                "SA Attendance tab must exist exactly once"
            )
        live_id = int(matching[0]["sheetId"])
        if self.sheet_id is not None and live_id != self.sheet_id:
            raise ValueError("SA Attendance tab ID mismatch")
        return live_id

    def read_rows(self) -> list[list[Any]]:
        response = (
            self.service.spreadsheets()
            .values()
            .get(
                spreadsheetId=self.spreadsheet_id,
                range=f"'{self.sheet_name}'!A:O",
                valueRenderOption="UNFORMATTED_VALUE",
            )
            .execute()
        )
        return response.get("values", [])

    def publish(self, rows: list[dict[str, Any]]) -> dict[str, Any]:
        if not self.write_enabled:
            raise RuntimeError("SA Attendance Sheet writes are disabled")
        self.resolve_sheet_id()
        existing = self.read_rows()
        plan = build_upsert_plan(
            existing,
            rows,
            sheet_name=self.sheet_name,
        )

        for update_row in plan["updates"]:
            current = (
                self.service.spreadsheets()
                .values()
                .get(
                    spreadsheetId=self.spreadsheet_id,
                    range=update_row["range"],
                    valueRenderOption="UNFORMATTED_VALUE",
                )
                .execute()
                .get("values", [[]])[0]
            )
            current.extend(
                [""] * (len(SA_ATTENDANCE_HEADERS) - len(current))
            )
            if current[: len(SA_ATTENDANCE_HEADERS)] != update_row[
                "precondition"
            ]:
                raise RuntimeError(
                    f"row changed during publication: {update_row['range']}"
                )
            (
                self.service.spreadsheets()
                .values()
                .update(
                    spreadsheetId=self.spreadsheet_id,
                    range=update_row["range"],
                    valueInputOption="RAW",
                    body={"values": update_row["values"]},
                )
                .execute()
            )
        if plan["appends"]:
            (
                self.service.spreadsheets()
                .values()
                .append(
                    spreadsheetId=self.spreadsheet_id,
                    range=f"'{self.sheet_name}'!A:O",
                    valueInputOption="RAW",
                    insertDataOption="INSERT_ROWS",
                    body={"values": plan["appends"]},
                )
                .execute()
            )
        return {
            "status": "published",
            "updated": len(plan["updates"]),
            "appended": len(plan["appends"]),
            "published_at": datetime.now().astimezone().isoformat(),
        }
