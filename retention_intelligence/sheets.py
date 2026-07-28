from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

from .config import Settings
from .models import RetentionAssessment


SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
RADAR_HEADERS = [
    "Member",
    "Email",
    "Service",
    "Trainer",
    "Status",
    "Urgency",
    "Data confidence",
    "Workouts 7d",
    "Workouts 28d",
    "Workouts 90d",
    "Personal baseline / week",
    "Recent rate / week",
    "Change from baseline",
    "Last workout",
    "Days since activity",
    "Engagement source",
    "Class attendance proxy 7d",
    "Class attendance proxy 28d",
    "Class attendance proxy 90d",
    "Class baseline / week",
    "Recent class rate / week",
    "Class change from baseline",
    "Last retained class booking",
    "Days since retained class booking",
    "Reason",
    "Action owner",
    "Review date",
    "Snapshot",
]
KPI_HEADERS = [
    "Week",
    "Active members in scope",
    "Adequate usage coverage",
    "Thriving",
    "Stable",
    "Drifting",
    "At risk",
    "Insufficient data",
    "Operational exceptions",
    "28-day active rate",
    "Material decline rate",
    "Classifier version",
    "Run ID",
]


def _quote(name: str) -> str:
    return "'" + name.replace("'", "''") + "'"


class RetentionSheetsWriter:
    def __init__(self, settings: Settings, service=None):
        self.settings = settings
        self.service = service or self._build_service()

    def _build_service(self):
        try:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build
        except ImportError as exc:
            raise RuntimeError("Google Sheets dependencies are required") from exc

        if self.settings.google_service_account_json:
            credentials = service_account.Credentials.from_service_account_info(
                json.loads(self.settings.google_service_account_json),
                scopes=SCOPES,
            )
        elif self.settings.google_credentials_file:
            path = Path(self.settings.google_credentials_file)
            credentials = service_account.Credentials.from_service_account_file(
                str(path), scopes=SCOPES
            )
        else:
            raise RuntimeError(
                "Set GOOGLE_SERVICE_ACCOUNT_JSON or GOOGLE_SHEETS_CREDENTIALS_FILE"
            )
        return build("sheets", "v4", credentials=credentials, cache_discovery=False)

    def _ensure_allowlisted_tabs(self) -> None:
        spreadsheet = (
            self.service.spreadsheets()
            .get(
                spreadsheetId=self.settings.google_spreadsheet_id,
                fields="sheets.properties.title",
            )
            .execute()
        )
        existing = {
            item["properties"]["title"] for item in spreadsheet.get("sheets") or []
        }
        requests = [
            {"addSheet": {"properties": {"title": title}}}
            for title in (self.settings.radar_sheet_name, self.settings.kpi_sheet_name)
            if title not in existing
        ]
        if requests:
            (
                self.service.spreadsheets()
                .batchUpdate(
                    spreadsheetId=self.settings.google_spreadsheet_id,
                    body={"requests": requests},
                )
                .execute()
            )

    @staticmethod
    def radar_values(
        assessments: list[RetentionAssessment],
        snapshot: str,
    ) -> list[list[Any]]:
        rows: list[list[Any]] = [RADAR_HEADERS]
        priority = {
            "Operational exception": 0,
            "At risk": 1,
            "Drifting": 2,
            "Insufficient data": 3,
            "Stable": 4,
            "Thriving": 5,
            "On hold": 6,
            "Excluded": 7,
        }
        for item in sorted(
            assessments,
            key=lambda row: (
                priority.get(row.status, 99),
                row.last_name.lower(),
                row.first_name.lower(),
            ),
        ):
            if not item.included_in_kpi:
                continue
            rows.append(
                [
                    f"{item.first_name} {item.last_name}".strip(),
                    item.email,
                    item.service or "",
                    item.trainer_name or "",
                    item.status,
                    item.urgency,
                    item.data_confidence,
                    item.workouts_7d,
                    item.workouts_28d,
                    item.workouts_90d,
                    item.baseline_weekly_rate,
                    item.recent_weekly_rate,
                    item.change_percent if item.change_percent is not None else "",
                    item.last_workout_date or "",
                    (
                        item.days_since_last_workout
                        if item.days_since_last_workout is not None
                        else ""
                    ),
                    item.engagement_source,
                    item.class_bookings_7d,
                    item.class_bookings_28d,
                    item.class_bookings_90d,
                    item.class_baseline_weekly_rate,
                    item.class_recent_weekly_rate,
                    (
                        item.class_change_percent
                        if item.class_change_percent is not None
                        else ""
                    ),
                    item.last_class_booking_date or "",
                    (
                        item.days_since_last_class_booking
                        if item.days_since_last_class_booking is not None
                        else ""
                    ),
                    item.reason,
                    item.action_owner,
                    item.review_date or "",
                    snapshot,
                ]
            )
        return rows

    @staticmethod
    def kpi_row(
        assessments: list[RetentionAssessment],
        *,
        week_start: date,
        run_id: str,
    ) -> list[Any]:
        included = [item for item in assessments if item.included_in_kpi]
        count = lambda status: sum(item.status == status for item in included)
        adequate = [
            item for item in included if item.data_confidence in {"High", "Medium"}
        ]
        active_28 = sum(
            (
                item.class_bookings_28d > 0
                if item.engagement_source == "retained_class_booking"
                else item.workouts_28d > 0
            )
            for item in adequate
        )
        changes = [
            (
                item.class_change_percent
                if item.engagement_source == "retained_class_booking"
                else item.change_percent
            )
            for item in adequate
        ]
        decline = sum(
            change is not None and change <= -35 for change in changes
        )
        version = assessments[0].classifier_version if assessments else ""
        return [
            week_start.isoformat(),
            len(included),
            len(adequate),
            count("Thriving"),
            count("Stable"),
            count("Drifting"),
            count("At risk"),
            count("Insufficient data"),
            count("Operational exception"),
            round(active_28 / len(adequate), 4) if adequate else "",
            round(decline / len(adequate), 4) if adequate else "",
            version,
            run_id,
        ]

    def preview(
        self,
        assessments: list[RetentionAssessment],
        *,
        snapshot: str,
        week_start: date,
        run_id: str,
    ) -> dict[str, Any]:
        radar = self.radar_values(assessments, snapshot)
        return {
            "radarRows": len(radar) - 1,
            "radarHeaders": RADAR_HEADERS,
            "kpiHeaders": KPI_HEADERS,
            "kpiRow": self.kpi_row(
                assessments, week_start=week_start, run_id=run_id
            ),
        }

    def write(
        self,
        assessments: list[RetentionAssessment],
        *,
        snapshot: str,
        week_start: date,
        run_id: str,
    ) -> dict[str, Any]:
        if not self.settings.sheets_write_enabled:
            return {
                "status": "disabled",
                **self.preview(
                    assessments,
                    snapshot=snapshot,
                    week_start=week_start,
                    run_id=run_id,
                ),
            }
        self._ensure_allowlisted_tabs()
        radar_values = self.radar_values(assessments, snapshot)
        radar_range = f"{_quote(self.settings.radar_sheet_name)}!A1:AB"
        (
            self.service.spreadsheets()
            .values()
            .clear(
                spreadsheetId=self.settings.google_spreadsheet_id,
                range=radar_range,
                body={},
            )
            .execute()
        )
        (
            self.service.spreadsheets()
            .values()
            .update(
                spreadsheetId=self.settings.google_spreadsheet_id,
                range=f"{_quote(self.settings.radar_sheet_name)}!A1",
                valueInputOption="USER_ENTERED",
                body={"values": radar_values},
            )
            .execute()
        )

        kpi_range = f"{_quote(self.settings.kpi_sheet_name)}!A:M"
        existing = (
            self.service.spreadsheets()
            .values()
            .get(
                spreadsheetId=self.settings.google_spreadsheet_id,
                range=kpi_range,
            )
            .execute()
            .get("values")
            or []
        )
        row = self.kpi_row(assessments, week_start=week_start, run_id=run_id)
        values = existing if existing and existing[0] == KPI_HEADERS else [KPI_HEADERS]
        replaced = False
        for index in range(1, len(values)):
            if values[index] and values[index][0] == week_start.isoformat():
                values[index] = row
                replaced = True
                break
        if not replaced:
            values.append(row)
        (
            self.service.spreadsheets()
            .values()
            .clear(
                spreadsheetId=self.settings.google_spreadsheet_id,
                range=kpi_range,
                body={},
            )
            .execute()
        )
        (
            self.service.spreadsheets()
            .values()
            .update(
                spreadsheetId=self.settings.google_spreadsheet_id,
                range=f"{_quote(self.settings.kpi_sheet_name)}!A1",
                valueInputOption="USER_ENTERED",
                body={"values": values},
            )
            .execute()
        )
        return {"status": "written", "radarRows": len(radar_values) - 1}
