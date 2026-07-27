from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Iterable


def normalise_email(value: Any) -> str:
    return str(value or "").strip().lower()


def normalise_phone(value: Any) -> str:
    digits = re.sub(r"\D", "", str(value or ""))
    if digits.startswith("61") and len(digits) >= 11:
        return "0" + digits[2:]
    return digits


class _IdentityGraph:
    def __init__(self) -> None:
        self.parent: dict[str, str] = {}

    def add(self, value: str) -> None:
        if value:
            self.parent.setdefault(value, value)

    def find(self, value: str) -> str:
        self.add(value)
        parent = self.parent[value]
        if parent != value:
            self.parent[value] = self.find(parent)
        return self.parent[value]

    def union(self, left: str, right: str) -> None:
        if not left or not right:
            return
        left_root = self.find(left)
        right_root = self.find(right)
        if left_root == right_root:
            return
        canonical = min(left_root, right_root)
        other = right_root if canonical == left_root else left_root
        self.parent[other] = canonical


@dataclass(frozen=True)
class UniqueClientSummary:
    unique_clients: int
    service_relationships: int
    cross_service_overlaps: int
    missing_identity_rows: int
    service_rows: dict[str, int]

    def to_dict(self) -> dict[str, Any]:
        return {
            "unique_clients": self.unique_clients,
            "service_relationships": self.service_relationships,
            "cross_service_overlaps": self.cross_service_overlaps,
            "missing_identity_rows": self.missing_identity_rows,
            "service_rows": dict(sorted(self.service_rows.items())),
            "definition": (
                "Unique people on the supplied active service rosters, matched "
                "only by exact normalised email, exact normalised phone or an "
                "owner-approved email alias. Names are never used."
            ),
        }


def _header_index(header: list[Any], candidates: Iterable[str]) -> int | None:
    cleaned = [str(value or "").strip().lower() for value in header]
    for candidate in candidates:
        candidate = candidate.lower()
        if candidate in cleaned:
            return cleaned.index(candidate)
    return None


def filter_roster_by_values(
    rows: list[list[Any]],
    *,
    column_names: Iterable[str],
    accepted_values: Iterable[str],
) -> list[list[Any]]:
    """Retain a header and only rows with an allowlisted control value."""
    if not rows:
        return []
    index = _header_index(rows[0], column_names)
    if index is None:
        raise ValueError(
            "Roster has no control column matching "
            f"{sorted(str(value) for value in column_names)}"
        )
    accepted = {
        str(value or "").strip().lower() for value in accepted_values
    }
    return [
        rows[0],
        *[
            row
            for row in rows[1:]
            if index < len(row)
            and str(row[index] or "").strip().lower() in accepted
        ],
    ]


def _roster_identities(
    rows: list[list[Any]],
    service: str,
) -> list[tuple[str, str, str]]:
    if not rows:
        return []
    email_index = _header_index(rows[0], ("Email", "Email Address"))
    phone_index = _header_index(rows[0], ("Phone", "Phone Number"))
    if email_index is None and phone_index is None:
        raise ValueError(f"{service} roster has no email or phone column")

    results: list[tuple[str, str, str]] = []
    for row_number, row in enumerate(rows[1:], start=2):
        email = (
            normalise_email(row[email_index])
            if email_index is not None and email_index < len(row)
            else ""
        )
        phone = (
            normalise_phone(row[phone_index])
            if phone_index is not None and phone_index < len(row)
            else ""
        )
        if not email and not phone:
            if not any(str(value or "").strip() for value in row):
                continue
            results.append((service, "", f"anonymous:{service}:{row_number}"))
            continue
        results.append(
            (
                service,
                f"email:{email}" if email else "",
                f"phone:{phone}" if phone else "",
            )
        )
    return results


def deduplicate_service_rosters(
    rosters: dict[str, list[list[Any]]],
    *,
    approved_email_aliases: Iterable[tuple[str, str]] = (),
) -> UniqueClientSummary:
    graph = _IdentityGraph()
    identities: list[tuple[str, tuple[str, ...]]] = []

    for canonical, linked in approved_email_aliases:
        canonical_key = f"email:{normalise_email(canonical)}"
        linked_key = f"email:{normalise_email(linked)}"
        graph.union(canonical_key, linked_key)

    service_rows: dict[str, int] = {}
    missing_identity_rows = 0
    for service, rows in rosters.items():
        parsed = _roster_identities(rows, service)
        service_rows[service] = len(parsed)
        for parsed_service, email_key, phone_key in parsed:
            keys = tuple(key for key in (email_key, phone_key) if key)
            if len(keys) == 2:
                graph.union(keys[0], keys[1])
            if not keys or keys[0].startswith("anonymous:"):
                missing_identity_rows += 1
            identities.append((parsed_service, keys))

    people: dict[str, set[str]] = {}
    for position, (service, keys) in enumerate(identities):
        if keys:
            person_key = graph.find(keys[0])
        else:
            person_key = f"anonymous-row:{position}"
        people.setdefault(person_key, set()).add(service)

    cross_service_overlaps = sum(
        max(0, len(services) - 1) for services in people.values()
    )
    return UniqueClientSummary(
        unique_clients=len(people),
        service_relationships=len(identities),
        cross_service_overlaps=cross_service_overlaps,
        missing_identity_rows=missing_identity_rows,
        service_rows=service_rows,
    )
