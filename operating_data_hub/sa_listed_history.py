from __future__ import annotations

from datetime import UTC, date, datetime
from typing import Any
from zoneinfo import ZoneInfo

from .contracts import fingerprint


BRISBANE_TZ = ZoneInfo("Australia/Brisbane")
LISTED_SHOW_RATE_START = date(2026, 3, 12)
LISTED_CONVERSION_START = date(2025, 9, 19)


def parse_appointment_datetime(value: Any) -> datetime | None:
    text = str(value or "").strip()
    for fmt in (
        "%A, %B %d, %Y %H:%M",
        "%d/%m/%Y %H:%M",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%d %H:%M:%S",
    ):
        try:
            parsed = datetime.strptime(text, fmt)
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=BRISBANE_TZ)
            return parsed.astimezone(UTC)
        except ValueError:
            continue
    return None


def _listed_flag(value: Any) -> str | None:
    flag = str(value or "").strip().upper()
    return flag if flag in {"Y", "N"} else None


def build_listed_history(
    rows: list[list[Any]],
    *,
    observed_at: datetime | None = None,
) -> dict[str, Any]:
    observed_at = observed_at or datetime.now(UTC)
    events: list[dict[str, Any]] = []
    skipped = 0
    for row_number, row in enumerate(rows, start=2):
        appointment_at = parse_appointment_datetime(
            row[7] if len(row) > 7 else None
        )
        if appointment_at is None:
            skipped += 1
            continue
        local_date = appointment_at.astimezone(BRISBANE_TZ).date()
        listed_show = _listed_flag(row[10] if len(row) > 10 else None)
        listed_convert = _listed_flag(row[11] if len(row) > 11 else None)
        identity_fingerprint = fingerprint(
            {
                "first_name": str(row[1] if len(row) > 1 else "")
                .strip()
                .lower(),
                "last_name": str(row[2] if len(row) > 2 else "")
                .strip()
                .lower(),
                "email": str(row[5] if len(row) > 5 else "")
                .strip()
                .lower(),
                "mobile": str(row[4] if len(row) > 4 else "").strip(),
            }
        )
        show_rate_eligible = (
            local_date >= LISTED_SHOW_RATE_START
            and listed_show in {"Y", "N"}
        )
        legacy_attended = (
            LISTED_CONVERSION_START
            <= local_date
            < LISTED_SHOW_RATE_START
        )
        conversion_denominator_eligible = (
            local_date >= LISTED_CONVERSION_START
            and (
                legacy_attended
                or (
                    local_date >= LISTED_SHOW_RATE_START
                    and listed_show == "Y"
                )
            )
        )
        conversion_numerator_eligible = (
            local_date >= LISTED_CONVERSION_START
            and listed_convert == "Y"
        )
        attendance_mismatch = (
            conversion_numerator_eligible
            and not conversion_denominator_eligible
        )
        source_event_id = fingerprint(
            {
                "tab": "Appointments",
                "appointment_at": appointment_at.isoformat(),
                "identity": identity_fingerprint,
            }
        )
        events.append(
            {
                "source_event_id": source_event_id,
                "row_number": row_number,
                "appointment_at": appointment_at.isoformat(),
                "local_date": local_date.isoformat(),
                "listed_show": listed_show,
                "listed_convert": listed_convert,
                "show_rate_eligible": show_rate_eligible,
                "conversion_denominator_eligible": (
                    conversion_denominator_eligible
                ),
                "conversion_numerator_eligible": (
                    conversion_numerator_eligible
                ),
                "legacy_attended": legacy_attended,
                "attendance_mismatch": attendance_mismatch,
            }
        )
    return {
        "schema_version": 1,
        "source": "google_sheets",
        "tab": "Appointments",
        "observed_at": observed_at.isoformat(),
        "status": "complete",
        "complete": True,
        "events": events,
        "summary": {
            "record_count": len(events),
            "skipped_rows": skipped,
            "show_rate_start": LISTED_SHOW_RATE_START.isoformat(),
            "conversion_start": LISTED_CONVERSION_START.isoformat(),
            "show_rate_eligible": sum(
                event["show_rate_eligible"] for event in events
            ),
            "conversion_denominator_eligible": sum(
                event["conversion_denominator_eligible"]
                for event in events
            ),
            "conversion_numerator_eligible": sum(
                event["conversion_numerator_eligible"]
                for event in events
            ),
            "attendance_mismatches": sum(
                event["attendance_mismatch"] for event in events
            ),
        },
    }
