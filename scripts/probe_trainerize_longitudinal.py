#!/usr/bin/env python3
"""Read-only preflight for the Trainerize longitudinal strength audit.

The probe prints aggregate counts, response keys, and recording-shape summaries.
It deliberately excludes names, emails, raw member IDs, and measurement values.
"""

from __future__ import annotations

from collections import Counter
from datetime import date
from typing import Any

from trainerize_client import TrainerizeAPIError, TrainerizeClient


START_DATE = "2020-01-01"
END_DATE = date.today().isoformat()


def collect_clients(client: TrainerizeClient, view: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    start = 0
    while True:
        page = client.get_client_list(
            view=view,
            start=start,
            count=100,
            location_id=client.location_id,
        )
        batch = page.get("users") or []
        rows.extend(batch)
        start += len(batch)
        if not batch or start >= int(page.get("total") or 0):
            return rows


def response_shape(value: Any) -> Any:
    if isinstance(value, dict):
        return sorted(value.keys())
    if isinstance(value, list):
        return {"type": "list", "count": len(value)}
    return type(value).__name__


def main() -> None:
    client = TrainerizeClient(timeout=60)
    active = collect_clients(client, "activeClient")
    deactivated = collect_clients(client, "deactivatedClient")
    print({"active_clients": len(active), "deactivated_clients": len(deactivated)})

    active_ids = [int(row["id"]) for row in active if row.get("id") is not None]
    profile_response = client.post(
        "/user/getProfile",
        {"usersid": active_ids[:100], "unitBodystats": "cm"},
    )
    profiles = profile_response.get("usrProfile") or profile_response.get("users") or []
    print({"profile_response_keys": sorted(profile_response.keys())})
    if profiles:
        print({"profile_keys": sorted(profiles[0].keys())})

    candidates = sorted(
        profiles,
        key=lambda row: str(row.get("created") or row.get("dateCreated") or "9999"),
    )
    if not candidates:
        raise RuntimeError("No active profile was available for the preflight")
    sample_user_id = int(candidates[0]["id"])

    calendar_responses: list[dict[str, Any]] = []
    for year in range(int(START_DATE[:4]), date.today().year + 1):
        window_start = f"{year}-01-01"
        window_end = min(f"{year}-12-31", END_DATE)
        if window_start > END_DATE:
            break
        calendar_responses.append(
            client.post(
                "/calendar/getList",
                {
                    "userID": sample_user_id,
                    "startDate": window_start,
                    "endDate": window_end,
                    "unitDistance": "km",
                    "unitWeight": "kg",
                },
            )
        )
    item_types: Counter[str] = Counter()
    item_statuses: Counter[str] = Counter()
    detail_keys: Counter[str] = Counter()
    workout_ids: list[int] = []
    body_stat_dates: list[str] = []
    total_items = 0
    for calendar in calendar_responses:
        for day in calendar.get("calendar") or []:
            for item in day.get("items") or []:
                total_items += 1
                item_types[str(item.get("type") or "unknown")] += 1
                item_statuses[str(item.get("status") or "unknown")] += 1
                detail = item.get("detail") or {}
                if isinstance(detail, dict):
                    detail_keys.update(detail.keys())
                if item.get("id") is not None and (
                    str(item.get("type") or "").lower() == "workout"
                    or detail.get("workoutID") is not None
                ):
                    workout_ids.append(int(item["id"]))
                if str(item.get("type") or "") == "bodyStat" and day.get("date"):
                    body_stat_dates.append(str(day["date"])[:10])
    print(
        {
            "calendar_response_keys": sorted(calendar_responses[-1].keys()),
            "sample_calendar_items": total_items,
            "item_types": dict(item_types),
            "item_statuses": dict(item_statuses),
            "detail_keys": sorted(detail_keys),
            "candidate_daily_workouts": len(set(workout_ids)),
        }
    )

    if workout_ids:
        daily = client.post("/dailyWorkout/get", {"ids": list(dict.fromkeys(workout_ids))[:5]})
        rows = daily.get("dailyWorkouts") or []
        print({"daily_workout_response_keys": sorted(daily.keys()), "rows": len(rows)})
        if rows:
            print({"daily_workout_keys": sorted(rows[0].keys())})
            exercises = rows[0].get("exercises") or []
            print({"exercise_count_in_sample": len(exercises)})
            if exercises:
                exercise = exercises[0]
                definition = exercise.get("def") or {}
                statistics = exercise.get("stats") or []
                print(
                    {
                        "exercise_keys": sorted(exercise.keys()),
                        "definition_keys": sorted(definition.keys()),
                        "stat_keys": sorted(statistics[0].keys()) if statistics else [],
                    }
                )

    summary = client.post(
        "/user/getClientSummary", {"userID": sample_user_id, "unitWeight": "kg"}
    )
    print({"client_summary_keys": sorted(summary.keys())})

    if body_stat_dates:
        body = client.post(
            "/bodystats/get",
            {
                "userID": sample_user_id,
                "date": max(body_stat_dates),
                "unitBodystats": "cm",
                "unitWeight": "kg",
            },
        )
        print({"body_stats_keys": sorted(body.keys())})
        if isinstance(body.get("bodyMeasures"), dict):
            print({"body_measure_keys": sorted(body["bodyMeasures"].keys())})
        elif isinstance(body.get("bodyMeasures"), list) and body["bodyMeasures"]:
            print({"body_measure_keys": sorted(body["bodyMeasures"][0].keys())})

    optional_calls = [
        ("accomplishments", "/accomplishment/getList", {"userID": sample_user_id}),
        ("goals", "/goal/getList", {"userID": sample_user_id}),
        ("habits", "/habits/getList", {"userID": sample_user_id}),
        ("training_plans", "/trainingPlan/getList", {"userID": sample_user_id}),
    ]
    for label, endpoint, payload in optional_calls:
        try:
            response = client.post(endpoint, payload)
            print({label: response_shape(response), f"{label}_keys": sorted(response.keys())})
        except TrainerizeAPIError as exc:
            print({label: "unavailable", "http_status": exc.status_code})


if __name__ == "__main__":
    main()
