#!/usr/bin/env python3
"""Match the confirmed Strength Assessment roster to Trainerize accounts."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from trainerize_client import TrainerizeClient


WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ROSTER = (
    WORKSPACE_ROOT
    / "data/private/strength-assessments/master-completed-assessment-emails.csv"
)
DEFAULT_OUTPUT = (
    WORKSPACE_ROOT
    / "data/private/strength-assessments/trainerize-roster-reconciliation.csv"
)


def normalize_email(value: object) -> str:
    return str(value or "").strip().lower()


def fetch_view(client: TrainerizeClient, view: str) -> list[dict]:
    users: list[dict] = []
    start = 0
    while True:
        page = client.get_client_list(view=view, start=start, count=100, verbose=True)
        batch = page.get("users") or []
        users.extend(batch)
        total = int(page.get("total") or 0)
        if not batch or start + len(batch) >= total:
            return users
        start += len(batch)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--roster", type=Path, default=DEFAULT_ROSTER)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    with args.roster.open(newline="", encoding="utf-8") as handle:
        roster = list(csv.DictReader(handle))

    client = TrainerizeClient()
    users = fetch_view(client, "activeClient") + fetch_view(client, "deactivatedClient")

    by_email: dict[str, list[dict]] = {}
    for user in users:
        email = normalize_email(user.get("email"))
        if email:
            by_email.setdefault(email, []).append(user)

    fields = [
        "source_year",
        "appointment_date",
        "first_name",
        "last_name",
        "email",
        "trainerize_user_id",
        "trainerize_status",
        "trainerize_role",
        "match_status",
    ]
    output_rows: list[dict[str, object]] = []
    for person in roster:
        matches = by_email.get(normalize_email(person.get("email")), [])
        if not matches:
            output_rows.append({**person, "match_status": "not_found"})
            continue
        for match in matches:
            output_rows.append(
                {
                    **person,
                    "trainerize_user_id": match.get("id", ""),
                    "trainerize_status": match.get("status", ""),
                    "trainerize_role": match.get("role", ""),
                    "match_status": "matched" if len(matches) == 1 else "duplicate_email",
                }
            )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(output_rows)

    matched_emails = {
        normalize_email(row.get("email"))
        for row in output_rows
        if row.get("match_status") != "not_found"
    }
    deactivated = sum(
        1
        for row in output_rows
        if str(row.get("trainerize_status", "")).lower() == "deactivated"
    )
    active = sum(
        1
        for row in output_rows
        if str(row.get("trainerize_status", "")).lower() == "active"
    )
    print(
        f"Roster emails: {len(roster)}; matched: {len(matched_emails)}; "
        f"not found: {len(roster) - len(matched_emails)}; "
        f"active matches: {active}; deactivated matches: {deactivated}"
    )
    print(args.output)


if __name__ == "__main__":
    main()
