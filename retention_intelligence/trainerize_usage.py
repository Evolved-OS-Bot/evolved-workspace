from __future__ import annotations

import time
from collections import defaultdict
from datetime import date, datetime, timedelta
from typing import Any

from scripts.trainerize_client import TrainerizeClient

from .models import UsageMetrics


def _iso_date(value: Any) -> date | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text[:10]).date()
    except ValueError:
        return None


def tracked_workout_dates(payload: dict[str, Any]) -> list[date]:
    dates: list[date] = []
    for day in payload.get("calendar") or []:
        observed = _iso_date(day.get("date"))
        if observed is None:
            continue
        for item in day.get("items") or []:
            item_type = str(item.get("type") or "").lower()
            detail = item.get("detail") or {}
            status = str(
                item.get("status") or (detail.get("status") if isinstance(detail, dict) else "")
            ).lower()
            if item_type == "workoutregular" and status in {
                "tracked",
                "completed",
                "complete",
            }:
                dates.append(observed)
    return dates


def retained_past_class_booking_dates(
    payload: dict[str, Any],
    *,
    today: date,
) -> list[date]:
    """Return retained past group-class bookings.

    The Evolved operating rule is that trainers remove a client's booking when
    she does not attend. A retained past booking is therefore an attendance
    proxy, not a platform-verified check-in.
    """
    dates: list[date] = []
    for day in payload.get("calendar") or []:
        observed = _iso_date(day.get("date"))
        if observed is None or observed > today:
            continue
        for item in day.get("items") or []:
            if str(item.get("type") or "").lower() != "appointmentv2":
                continue
            detail = item.get("detail") or {}
            if not isinstance(detail, dict):
                continue
            is_group = detail.get("isGroupAppointment")
            category = str(detail.get("eventCategory") or "").lower()
            if is_group in {True, 1, "1"} and category == "class":
                dates.append(observed)
    return dates


class TrainerizeUsageReader:
    def __init__(self, client: TrainerizeClient | None = None, retries: int = 3):
        self.client = client or TrainerizeClient()
        self.retries = retries

    def _calendar(self, user_id: int, start: date, end: date) -> dict[str, Any]:
        error: Exception | None = None
        for attempt in range(self.retries):
            try:
                return self.client.post(
                    "/calendar/getList",
                    {
                        "userID": user_id,
                        "startDate": start.isoformat(),
                        "endDate": end.isoformat(),
                        "unitDistance": "km",
                        "unitWeight": "kg",
                    },
                )
            except Exception as exc:
                error = exc
                if attempt + 1 < self.retries:
                    time.sleep(0.5 * (2**attempt))
        raise RuntimeError(f"Trainerize calendar read failed for client {user_id}") from error

    def read_many(
        self,
        user_ids: list[int],
        *,
        today: date | None = None,
    ) -> dict[int, UsageMetrics]:
        today = today or date.today()
        start = today - timedelta(days=111)
        result: dict[int, UsageMetrics] = {}
        for user_id in user_ids:
            calendar = self._calendar(user_id, start, today)
            dates = tracked_workout_dates(calendar)
            class_dates = retained_past_class_booking_dates(
                calendar,
                today=today,
            )
            counts: dict[date, int] = defaultdict(int)
            class_counts: dict[date, int] = defaultdict(int)
            for observed in dates:
                counts[observed] += 1
            for observed in class_dates:
                class_counts[observed] += 1
            last = max(dates) if dates else None
            last_class = max(class_dates) if class_dates else None
            result[user_id] = UsageMetrics(
                workouts_7d=sum(
                    count for observed, count in counts.items()
                    if observed >= today - timedelta(days=6)
                ),
                workouts_28d=sum(
                    count for observed, count in counts.items()
                    if observed >= today - timedelta(days=27)
                ),
                workouts_90d=sum(
                    count for observed, count in counts.items()
                    if observed >= today - timedelta(days=89)
                ),
                baseline_workouts=sum(
                    count for observed, count in counts.items()
                    if today - timedelta(days=111)
                    <= observed
                    <= today - timedelta(days=28)
                ),
                baseline_weeks=12.0,
                last_workout_date=last.isoformat() if last else None,
                days_since_last_workout=(today - last).days if last else None,
                class_bookings_7d=sum(
                    count for observed, count in class_counts.items()
                    if observed >= today - timedelta(days=6)
                ),
                class_bookings_28d=sum(
                    count for observed, count in class_counts.items()
                    if observed >= today - timedelta(days=27)
                ),
                class_bookings_90d=sum(
                    count for observed, count in class_counts.items()
                    if observed >= today - timedelta(days=89)
                ),
                baseline_class_bookings=sum(
                    count for observed, count in class_counts.items()
                    if today - timedelta(days=111)
                    <= observed
                    <= today - timedelta(days=28)
                ),
                last_class_booking_date=(
                    last_class.isoformat() if last_class else None
                ),
                days_since_last_class_booking=(
                    (today - last_class).days if last_class else None
                ),
            )
        return result
