from __future__ import annotations

import re
import time
from collections import defaultdict
from datetime import date
from typing import Any, Iterable

import requests


TRACKED_STATUSES = {"tracked", "completed", "complete"}
SESSION_NAMES = {
    "onboarding": {
        "on boarding session",
        "onboarding session",
    },
    "strength_assessment": {
        "women s standard strength assessment",
    },
}


def normalise_text(value: Any) -> str:
    return " ".join(
        re.sub(r"[^a-z0-9]+", " ", str(value or "").lower()).split()
    )


def _full_name(row: dict[str, Any]) -> str:
    return " ".join(
        value
        for value in (
            str(row.get("firstName") or "").strip(),
            str(row.get("lastName") or "").strip(),
        )
        if value
    )


class TrainerizeAttendanceClient:
    base_url = "https://api.trainerize.com/v03"

    def __init__(
        self,
        group_id: str,
        api_token: str,
        location_id: int,
        *,
        timeout: int = 60,
    ):
        if not group_id or not api_token or not location_id:
            raise ValueError("Trainerize attendance credentials are incomplete")
        self.location_id = location_id
        self.timeout = timeout
        self.session = requests.Session()
        self.session.auth = (group_id, api_token)
        self.session.headers.update(
            {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "The-Evolved-Operating-Hub/1.0",
            }
        )

    def post(
        self,
        endpoint: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        last_error: Exception | None = None
        for attempt in range(4):
            try:
                response = self.session.post(
                    f"{self.base_url}{endpoint}",
                    json=payload,
                    timeout=self.timeout,
                )
                if response.status_code == 429 or response.status_code >= 500:
                    time.sleep(min(8, 2**attempt))
                    continue
                response.raise_for_status()
                result = response.json()
                if not isinstance(result, dict):
                    raise RuntimeError(
                        "Trainerize returned an unexpected response"
                    )
                return result
            except (requests.RequestException, ValueError) as exc:
                last_error = exc
                if (
                    isinstance(exc, requests.HTTPError)
                    and exc.response is not None
                    and 400 <= exc.response.status_code < 500
                    and exc.response.status_code != 429
                ):
                    break
                if attempt < 3:
                    time.sleep(min(8, 2**attempt))
        raise RuntimeError(
            f"Trainerize request failed for {endpoint}: {last_error}"
        ) from last_error

    def _clients_for_view(self, view: str) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        start = 0
        while True:
            response = self.post(
                "/user/getClientList",
                {
                    "view": view,
                    "sort": "name",
                    "start": start,
                    "count": 100,
                    "verbose": False,
                    "locationID": self.location_id,
                },
            )
            batch = response.get("users") or []
            rows.extend(batch)
            start += len(batch)
            if not batch or start >= int(response.get("total") or 0):
                break
        return rows

    def attendance_clients(self) -> list[dict[str, Any]]:
        by_id: dict[int, dict[str, Any]] = {}
        for view in ("activeClient", "deactivatedClient"):
            for source in self._clients_for_view(view):
                row = {**source, "attendanceAccountState": view}
                user_id = int(row["id"])
                if user_id not in by_id or view == "activeClient":
                    by_id[user_id] = row
        return list(by_id.values())

    def calendar(
        self,
        user_id: int,
        start_date: date,
        end_date: date,
    ) -> list[dict[str, Any]]:
        response = self.post(
            "/calendar/getList",
            {
                "userID": user_id,
                "startDate": start_date.isoformat(),
                "endDate": end_date.isoformat(),
                "unitDistance": "km",
                "unitWeight": "kg",
            },
        )
        return list(response.get("calendar") or [])


def _identity_candidates(
    identity: dict[str, Any],
    clients: Iterable[dict[str, Any]],
) -> tuple[list[dict[str, Any]], str | None]:
    rows = list(clients)
    email = normalise_text(identity.get("email")).replace(" ", "")
    if email:
        matches = [
            row
            for row in rows
            if normalise_text(row.get("email")).replace(" ", "") == email
        ]
        if matches:
            return matches, "email"
    name = normalise_text(
        identity.get("name")
        or " ".join(
            [
                str(identity.get("firstName") or ""),
                str(identity.get("lastName") or ""),
            ]
        )
    )
    if not name:
        return [], None
    return (
        [row for row in rows if normalise_text(_full_name(row)) == name],
        "exact_name",
    )


def _tracked_items(
    calendar: Iterable[dict[str, Any]],
    target_date: str,
) -> list[dict[str, Any]]:
    results = []
    for day in calendar:
        if str(day.get("date") or "")[:10] != target_date:
            continue
        for item in day.get("items") or []:
            status = normalise_text(item.get("status")).replace(" ", "_")
            if status not in TRACKED_STATUSES:
                continue
            results.append(
                {
                    "session_id": str(item.get("id") or ""),
                    "session_name": str(
                        item.get("name")
                        or item.get("title")
                        or item.get("workoutName")
                        or item.get("description")
                        or ""
                    ).strip(),
                    "session_status": status,
                    "session_type": str(item.get("type") or "").strip(),
                }
            )
    return results


def corroborate_attendance(
    client: TrainerizeAttendanceClient,
    candidates: Iterable[dict[str, Any]],
    identities: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    requested = [dict(row) for row in candidates]
    clients = client.attendance_clients()
    matched_users: dict[str, dict[str, Any]] = {}
    identity_results: dict[str, dict[str, Any]] = {}

    for contact_id in {
        str(row.get("contact_id") or "") for row in requested
    }:
        matches, basis = _identity_candidates(
            identities.get(contact_id) or {},
            clients,
        )
        if len(matches) == 1:
            matched_users[contact_id] = matches[0]
            identity_results[contact_id] = {
                "state": "matched",
                "basis": basis,
            }
        else:
            identity_results[contact_id] = {
                "state": "missing" if not matches else "ambiguous",
                "basis": basis,
                "candidate_count": len(matches),
            }

    ranges: dict[int, list[date]] = defaultdict(list)
    for row in requested:
        contact_id = str(row.get("contact_id") or "")
        user = matched_users.get(contact_id)
        if user and row.get("target_date"):
            ranges[int(user["id"])].append(
                date.fromisoformat(str(row["target_date"]))
            )
    calendars = {
        user_id: client.calendar(user_id, min(days), max(days))
        for user_id, days in ranges.items()
    }

    results: list[dict[str, Any]] = []
    for row in requested:
        appointment_id = str(row.get("appointment_id") or "")
        contact_id = str(row.get("contact_id") or "")
        target_date = str(row.get("target_date") or "")
        kind = str(row.get("kind") or "")
        identity_result = identity_results.get(contact_id) or {
            "state": "missing",
            "basis": None,
            "candidate_count": 0,
        }
        user = matched_users.get(contact_id)
        if not user:
            results.append(
                {
                    **row,
                    "decision": "unresolved",
                    "reason": (
                        "trainerize_identity_"
                        + str(identity_result["state"])
                    ),
                    "identity": identity_result,
                    "matching_sessions": [],
                }
            )
            continue
        tracked = _tracked_items(
            calendars.get(int(user["id"])) or [],
            target_date,
        )
        accepted_names = SESSION_NAMES.get(kind) or set()
        matching = [
            item
            for item in tracked
            if normalise_text(item["session_name"]) in accepted_names
        ]
        decision = "verified_showed" if len(matching) == 1 else "unresolved"
        reason = (
            "exact_date_tracked_session"
            if decision == "verified_showed"
            else "required_session_not_tracked"
            if not matching
            else "ambiguous_matching_sessions"
        )
        results.append(
            {
                **row,
                "decision": decision,
                "reason": reason,
                "identity": {
                    **identity_result,
                    "trainerize_user_id": int(user["id"]),
                    "account_state": user.get(
                        "attendanceAccountState"
                    ),
                },
                "matching_sessions": matching,
            }
        )
    return {
        "source_status": "complete",
        "client_count": len(clients),
        "results": results,
        "counts": {
            "requested": len(requested),
            "verified_showed": sum(
                row["decision"] == "verified_showed" for row in results
            ),
            "unresolved": sum(
                row["decision"] != "verified_showed" for row in results
            ),
        },
    }


def attach_evidence(
    plan: dict[str, Any],
    evidence: dict[str, Any],
) -> dict[str, Any]:
    results = {
        row["appointment_id"]: row
        for row in evidence.get("results") or []
        if row.get("appointment_id")
    }
    actions = []
    for source in plan.get("actions") or []:
        action = dict(source)
        result = results.get(action["appointment_id"])
        if result:
            action["trainerize_evidence"] = result
        actions.append(action)
    plan = {
        **plan,
        "actions": actions,
        "trainerize_precheck": {
            "source_status": evidence.get("source_status") or "unavailable",
            "counts": evidence.get("counts") or {},
        },
    }
    verified = {
        row["appointment_id"]
        for row in actions
        if (row.get("trainerize_evidence") or {}).get("decision")
        == "verified_showed"
    }
    plan["counts"] = {
        **(plan.get("counts") or {}),
        "trainerize_verified": len(verified),
        "coach_due_after_precheck": sum(
            row.get("stage") == "coach"
            and row["appointment_id"] not in verified
            for row in actions
        ),
        "admin_due_after_precheck": sum(
            row.get("stage") == "admin"
            and row["appointment_id"] not in verified
            for row in actions
        ),
    }
    return plan


def resolve_verified_appointments(
    ghl_client: Any,
    plan: dict[str, Any],
) -> dict[str, Any]:
    candidates: dict[str, dict[str, Any]] = {}
    for action in plan.get("actions") or []:
        evidence = action.get("trainerize_evidence") or {}
        if evidence.get("decision") == "verified_showed":
            candidates.setdefault(action["appointment_id"], evidence)

    resolved: list[dict[str, str]] = []
    audit: list[dict[str, Any]] = []
    for appointment_id, evidence in candidates.items():
        contact_id = str(evidence.get("contact_id") or "")
        session = (evidence.get("matching_sessions") or [{}])[0]
        try:
            current = ghl_client.get_appointment_state(appointment_id)
            if current["status"] == "confirmed":
                ghl_client.update_trainerize_verified_to_showed(
                    current,
                    evidence,
                    idempotency_key=(
                        "trainerize-attendance-"
                        f"{appointment_id}-"
                        f"{session.get('session_id')}-v1"
                    ),
                )
                verified = ghl_client.get_appointment_state(appointment_id)
                if verified["status"] != "showed":
                    raise RuntimeError(
                        "GHL did not retain the Showed appointment status"
                    )
                outcome = "updated_to_showed"
            elif current["status"] in {
                "showed",
                "no_show",
                "cancelled",
                "invalid",
            }:
                outcome = f"already_{current['status']}"
            else:
                raise RuntimeError(
                    "GHL appointment is not in a resolvable state"
                )
            resolved.append(
                {
                    "appointment_id": appointment_id,
                    "contact_id": contact_id,
                }
            )
            audit.append(
                {
                    "appointment_id": appointment_id,
                    "contact_id": contact_id,
                    "trainerize_session_id": session.get("session_id"),
                    "outcome": outcome,
                }
            )
        except Exception as exc:
            audit.append(
                {
                    "appointment_id": appointment_id,
                    "contact_id": contact_id,
                    "trainerize_session_id": session.get("session_id"),
                    "outcome": "staff_task_fallback",
                    "error": str(exc),
                }
            )
    return {
        "resolved": resolved,
        "resolved_ids": {
            row["appointment_id"] for row in resolved
        },
        "audit": audit,
        "counts": {
            "verified": len(candidates),
            "resolved": len(resolved),
            "fallback": len(candidates) - len(resolved),
        },
    }
