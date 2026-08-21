#!/usr/bin/env python3
"""Read-only historical Strength Assessment attendance matcher.

The script never changes GHL, Google Sheets or hub records. It writes
identified detail only to the protected local data area and prints a
privacy-safe aggregate summary for owner review.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pt_booking_shadow.ghl_client import GHLReadOnlyClient
from scripts.sheets_client import read_sheet


load_dotenv(Path(__file__).parent / ".env")

DEFAULT_DETAIL_PATH = (
    ROOT
    / "data"
    / "private"
    / "integration-reporting"
    / "sa-attendance-backfill-detail.json"
)
BRISBANE_TZ = ZoneInfo("Australia/Brisbane")


def canonical_email(value: Any) -> str:
    return str(value or "").strip().lower()


def canonical_phone(value: Any) -> str:
    digits = re.sub(r"\D", "", str(value or ""))
    if digits.startswith("61"):
        digits = "0" + digits[2:]
    return digits


def canonical_name(first: Any, last: Any) -> str:
    return " ".join(
        " ".join(f"{first or ''} {last or ''}".lower().split()).split()
    )


def parse_sheet_datetime(value: Any) -> datetime | None:
    text = str(value or "").strip()
    for fmt in (
        "%A, %B %d, %Y %H:%M",
        "%d/%m/%Y %H:%M",
        "%Y-%m-%dT%H:%M:%S%z",
    ):
        try:
            parsed = datetime.strptime(text, fmt)
            return (
                parsed.replace(tzinfo=BRISBANE_TZ)
                if parsed.tzinfo is None
                else parsed
            ).astimezone(UTC)
        except ValueError:
            continue
    return None


def classify_match(
    legacy: dict[str, Any],
    events: list[dict[str, Any]],
    *,
    tolerance: timedelta = timedelta(minutes=15),
) -> dict[str, Any]:
    legacy_event_id = str(legacy.get("appointment_id") or "").strip()
    if legacy_event_id:
        exact = [
            row for row in events if row["appointment_id"] == legacy_event_id
        ]
        if len(exact) == 1:
            return {"classification": "exact", "event": exact[0]}
    appointment_at = legacy.get("appointment_at")
    if not isinstance(appointment_at, datetime):
        return {"classification": "unmatched", "event": None}

    contact_id = str(legacy.get("contact_id") or "").strip()
    if contact_id:
        exact = [
            row
            for row in events
            if row.get("contact_id") == contact_id
            and row["start_at"] == appointment_at
        ]
        if len(exact) == 1:
            return {"classification": "exact", "event": exact[0]}

    email = canonical_email(legacy.get("email"))
    phone = canonical_phone(legacy.get("phone"))
    name = canonical_name(
        legacy.get("first_name"),
        legacy.get("last_name"),
    )
    exact_identity = []
    for row in events:
        event_identity = (
            email
            and email == canonical_email(row.get("email"))
        ) or (
            phone
            and phone == canonical_phone(row.get("phone"))
        )
        if event_identity and row["start_at"] == appointment_at:
            exact_identity.append(row)
    if len(exact_identity) == 1:
        return {
            "classification": "corroborated",
            "event": exact_identity[0],
        }

    near = []
    for row in events:
        identity_match = (
            (email and email == canonical_email(row.get("email")))
            or (phone and phone == canonical_phone(row.get("phone")))
            or (
                name
                and name
                == canonical_name(
                    row.get("first_name"),
                    row.get("last_name"),
                )
            )
        )
        if identity_match and abs(row["start_at"] - appointment_at) <= tolerance:
            near.append(row)
    if len(near) == 1:
        return {"classification": "corroborated", "event": near[0]}
    if len(near) > 1 or len(exact_identity) > 1:
        return {
            "classification": "ambiguous",
            "event": None,
            "candidate_ids": [
                row["appointment_id"] for row in (near or exact_identity)
            ],
        }
    return {"classification": "unmatched", "event": None}


def build_backfill(
    legacy_rows: list[dict[str, Any]],
    event_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    details = []
    for legacy in legacy_rows:
        match = classify_match(legacy, event_rows)
        event = match.get("event")
        evidence = {
            "legacy_show": legacy.get("legacy_show"),
            "legacy_convert": legacy.get("legacy_convert"),
            "feedback": bool(event and event.get("feedback")),
            "agreement": bool(event and event.get("agreement")),
            "trainerize": bool(event and event.get("trainerize")),
            "routing": bool(event and event.get("routing")),
        }
        details.append(
            {
                "classification": match["classification"],
                "legacy_row": legacy.get("row_number"),
                "appointment_id": (
                    event.get("appointment_id") if event else None
                ),
                "candidate_ids": match.get("candidate_ids") or [],
                "evidence": evidence,
                "promotion_eligible": (
                    match["classification"] == "exact"
                    or (
                        match["classification"] == "corroborated"
                        and sum(
                            bool(evidence[key])
                            for key in (
                                "feedback",
                                "agreement",
                                "trainerize",
                                "routing",
                            )
                        )
                        >= 1
                    )
                ),
            }
        )
    classifications = Counter(row["classification"] for row in details)
    return {
        "schema_version": 1,
        "generated_at": datetime.now(UTC).isoformat(),
        "mode": "read_only",
        "summary": {
            "legacy_rows": len(legacy_rows),
            "event_rows": len(event_rows),
            "exact": classifications["exact"],
            "corroborated": classifications["corroborated"],
            "ambiguous": classifications["ambiguous"],
            "unmatched": classifications["unmatched"],
            "promotion_eligible": sum(
                row["promotion_eligible"] for row in details
            ),
            "historical_kpi_restatement_performed": False,
        },
        "details": details,
    }


def collect_live(days: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    api_key = os.environ["GHL_API_KEY"]
    location_id = os.environ["GHL_LOCATION_ID"]
    calendar_ids = [
        value.strip()
        for value in os.getenv(
            "SA_ATTENDANCE_CALENDAR_IDS",
            "HSVEzfJH4nice96IxHem",
        ).split(",")
        if value.strip()
    ]
    client = GHLReadOnlyClient(api_key, location_id)
    now = datetime.now(UTC)
    events = []
    contacts: dict[str, dict[str, Any]] = {}
    for calendar_id in calendar_ids:
        for item in client.list_events(
            calendar_id,
            now - timedelta(days=days),
            now + timedelta(days=14),
        ):
            if item.contact_id not in contacts:
                contacts[item.contact_id] = client.get_contact(
                    item.contact_id
                )
            contact = contacts[item.contact_id]
            events.append(
                {
                    "appointment_id": item.id,
                    "contact_id": item.contact_id,
                    "start_at": item.start.astimezone(UTC),
                    "status": item.status,
                    "email": contact.get("email"),
                    "phone": contact.get("phone"),
                    "first_name": contact.get("firstName"),
                    "last_name": contact.get("lastName"),
                }
            )
    sheet_rows = read_sheet("Appointments", "A2:N1000", formatted=True)
    legacy = []
    for row_number, row in enumerate(sheet_rows, start=2):
        appointment_at = parse_sheet_datetime(row[7] if len(row) > 7 else "")
        if not appointment_at:
            continue
        legacy.append(
            {
                "row_number": row_number,
                "first_name": row[1] if len(row) > 1 else "",
                "last_name": row[2] if len(row) > 2 else "",
                "phone": row[4] if len(row) > 4 else "",
                "email": row[5] if len(row) > 5 else "",
                "appointment_at": appointment_at,
                "legacy_show": row[10] if len(row) > 10 else "",
                "legacy_convert": row[11] if len(row) > 11 else "",
            }
        )
    return legacy, events


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=365)
    parser.add_argument(
        "--detail-output",
        type=Path,
        default=DEFAULT_DETAIL_PATH,
    )
    args = parser.parse_args()
    legacy, events = collect_live(max(30, args.days))
    result = build_backfill(legacy, events)
    args.detail_output.parent.mkdir(parents=True, exist_ok=True)
    args.detail_output.write_text(
        json.dumps(result, indent=2, default=str) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result["summary"], indent=2))
    print(f"Identified detail: {args.detail_output}")


if __name__ == "__main__":
    main()
