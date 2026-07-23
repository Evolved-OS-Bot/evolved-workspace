from datetime import date
from types import SimpleNamespace

from pt_booking_shadow.config import CURRENT_TRAINERS
from pt_booking_shadow.google_sheets import (
    BOOKINGS_SECTION,
    BOOKINGS_TOTAL,
    HOURS_SECTION,
    HOURS_TOTAL,
    SheetsKPIWriter,
    column_letter,
    quote_sheet_name,
)
from pt_booking_shadow.kpi import TrainerKPI, WeeklyPTKPI


class ExecuteCall:
    def __init__(self, result):
        self.result = result

    def execute(self):
        return self.result


class FakeValues:
    def __init__(self, layout):
        self.layout = layout
        self.update = None

    def batchGet(self, **kwargs):
        return ExecuteCall(self.layout)

    def batchUpdate(self, **kwargs):
        self.update = kwargs
        return ExecuteCall({"updated": True})


class FakeSpreadsheets:
    def __init__(self, values):
        self._values = values

    def values(self):
        return self._values


class FakeService:
    def __init__(self, layout):
        self.values_api = FakeValues(layout)

    def spreadsheets(self):
        return FakeSpreadsheets(self.values_api)


def layout():
    header = [["KPI Tracker", 2025, 2026, 46223.0]]
    labels = [
        ["KPI Tracker"],
        [HOURS_SECTION],
        ["Megan Brown"],
        ["Piper Mae"],
        ["Nora Silva"],
        ["Katrina Parsons"],
        ["Leisa Smith"],
        [HOURS_TOTAL],
        [""],
        [BOOKINGS_SECTION],
        ["Megan Brown"],
        ["Piper Mae"],
        ["Nora Silva"],
        ["Katrina Parsons"],
        ["Leisa Smith"],
        [BOOKINGS_TOTAL],
    ]
    return {
        "valueRanges": [
            {"values": header},
            {"values": labels},
        ]
    }


def settings():
    return SimpleNamespace(
        google_spreadsheet_id="sheet-id",
        google_kpi_sheet_name="KPI's The Evolved",
        google_service_account_json=None,
        google_credentials_file=None,
    )


def test_column_and_sheet_helpers():
    assert column_letter(1) == "A"
    assert column_letter(27) == "AA"
    assert quote_sheet_name("KPI's The Evolved") == "'KPI''s The Evolved'"


def test_writer_updates_both_blocks_in_the_matching_week_column():
    service = FakeService(layout())
    writer = SheetsKPIWriter(settings(), service=service)
    kpi = WeeklyPTKPI(
        week_start=date(2026, 7, 20),
        trainers={
            trainer: TrainerKPI(bookings=index, booked_minutes=index * 30)
            for index, trainer in enumerate(CURRENT_TRAINERS, start=1)
        },
    )

    result = writer.write(kpi)

    assert result["column"] == "D"
    assert result["updated_cells"] == 12
    data = service.values_api.update["body"]["data"]
    ranges = {item["range"]: item["values"][0][0] for item in data}
    assert ranges["'KPI''s The Evolved'!D3"] == 0.5
    assert ranges["'KPI''s The Evolved'!D11"] == 1
    assert ranges["'KPI''s The Evolved'!D8"] == 7.5
    assert ranges["'KPI''s The Evolved'!D16"] == 15
