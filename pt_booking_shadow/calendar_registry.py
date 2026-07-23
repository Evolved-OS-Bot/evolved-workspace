from __future__ import annotations

import re
from collections import Counter
from typing import Any

from .config import CURRENT_TRAINERS
from .models import CalendarRecord


PT_NAME = re.compile(
    r"^(?P<duration>30|45|60)\s+Min(?:ute)?\s+1:1(?:\s+PT)?\s+-\s+"
    r"(?P<trainer>Megan|Piper|Nora|Katrina|Leisa)$",
    re.IGNORECASE,
)


def build_registry(calendars: list[dict[str, Any]]) -> list[CalendarRecord]:
    records: list[CalendarRecord] = []
    for raw in calendars:
        match = PT_NAME.match(str(raw.get("name", "")).strip())
        if not match or not raw.get("isActive", True):
            continue
        trainer = match.group("trainer").title()
        duration = int(match.group("duration"))
        team_members = raw.get("teamMembers") or []
        user_id = team_members[0].get("userId") if team_members else None
        records.append(
            CalendarRecord(
                id=str(raw["id"]),
                name=str(raw["name"]),
                trainer=trainer,
                duration_minutes=duration,
                user_id=user_id,
                active=True,
            )
        )

    validate_registry(records)
    return sorted(records, key=lambda item: (item.trainer, item.duration_minutes))


def validate_registry(records: list[CalendarRecord]) -> None:
    expected = {(trainer, duration) for trainer in CURRENT_TRAINERS for duration in (30, 45, 60)}
    actual = {(item.trainer, item.duration_minutes) for item in records}
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    duplicate_counts = Counter((item.trainer, item.duration_minutes) for item in records)
    duplicates = sorted(key for key, count in duplicate_counts.items() if count > 1)
    if missing or extra or duplicates or len(records) != 15:
        raise RuntimeError(
            "Invalid live PT calendar registry: "
            f"count={len(records)} missing={missing} extra={extra} duplicates={duplicates}"
        )
