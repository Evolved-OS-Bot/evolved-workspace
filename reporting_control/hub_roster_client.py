from __future__ import annotations

import csv
import os
import re
import sqlite3
from collections import defaultdict
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any

import requests


EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
ACTIVE_SGPT_STATUSES = {"active", "active - pia"}
PREPAID_MARKERS = {"PIF", "PIA", "PAID IN ADVANCE"}


def _normalise_email(value: Any) -> str:
    return str(value or "").strip().lower()


def _text(value: Any) -> str | None:
    return " ".join(str(value or "").split()) or None


def _amount(value: Any) -> str | None:
    return str(value) if value is not None and str(value).strip() else None


def _iso_date(value: Any) -> str | None:
    text = str(value or "").strip()
    if not text:
        return None
    if text.isdigit():
        return (
            date(1899, 12, 30) + timedelta(days=int(text))
        ).isoformat()
    for pattern in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(text[:10], pattern).date().isoformat()
        except ValueError:
            continue
    return None


def _allocation_basis(row: Any) -> str:
    weekly_allocation = getattr(row, "weekly_allocation", None)
    if weekly_allocation is not None:
        return "weekly_recurring"
    marker = str(getattr(row, "payment_marker", "") or "").strip().upper()
    status = str(getattr(row, "status", "") or "").strip().lower()
    if marker in PREPAID_MARKERS or status == "active - pia":
        return "prepaid"
    return "unresolved"


def _load_aliases(path: Path | None) -> dict[str, str]:
    aliases: dict[str, str] = {}
    if path is None or not path.exists():
        return aliases
    with path.open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            canonical = _normalise_email(row.get("canonical_email"))
            linked = _normalise_email(row.get("linked_email"))
            if canonical and linked:
                aliases[canonical] = canonical
                aliases[linked] = canonical
    return aliases


def build_roster_candidate_from_records(
    roster_rows: list[Any],
    *,
    source_run_id: str,
    observed_at: str,
    identity_links_path: Path | None = None,
) -> dict[str, Any]:
    aliases = _load_aliases(identity_links_path)
    people: dict[str, list[dict[str, Any]]] = defaultdict(list)
    missing_identity: list[str] = []
    for row in roster_rows:
        service = str(row.service or "").strip().upper()
        status = " ".join(str(row.status or "").split())
        if service == "SGPT" and status.lower() not in ACTIVE_SGPT_STATUSES:
            continue
        if service not in {"SGPT", "PT"}:
            continue
        email = aliases.get(_normalise_email(row.email), _normalise_email(row.email))
        if not EMAIL_PATTERN.fullmatch(email):
            missing_identity.append(f"{service}:{row.row_number}")
            continue
        people[email].append(
            {
                "service_type": service,
                "status": status or "Active",
                "classification": None,
                "product": _text(row.product),
                "source_row": int(row.row_number),
                "assigned_trainer": _text(
                    getattr(row, "trainer", None)
                ),
                "contracted_weekly_frequency": _text(
                    getattr(row, "sessions_per_week", None)
                ),
                "service_duration": _text(
                    getattr(row, "session_length", None)
                ),
                "weekly_allocation": _amount(
                    getattr(row, "weekly_allocation", None)
                ),
                "allocation_currency": (
                    "AUD"
                    if getattr(row, "weekly_allocation", None) is not None
                    else None
                ),
                "contract_length": _text(
                    getattr(row, "contract_length", None)
                ),
                "effective_to": _iso_date(
                    getattr(row, "renewal_date", None)
                ),
                "payment_marker": _text(
                    getattr(row, "payment_marker", None)
                ),
                "allocation_basis": _allocation_basis(row),
            }
        )
    if missing_identity:
        raise ValueError(
            "Roster candidate contains rows without an exact governed "
            f"identity: {', '.join(missing_identity)}"
        )
    output_rows: list[dict[str, Any]] = []
    for email, services in sorted(people.items()):
        service_types = [item["service_type"] for item in services]
        if len(service_types) != len(set(service_types)):
            raise ValueError(
                f"Roster candidate has duplicate service rows for {email}"
            )
        output_rows.append(
            {
                "canonical_key": email,
                "services": sorted(
                    services, key=lambda item: item["service_type"]
                ),
            }
        )
    return {
        "schema_version": 2,
        "source": "active_roster_candidate",
        "source_system": "google_sheet",
        "source_run_id": source_run_id,
        "observed_at": observed_at,
        "as_of_date": observed_at[:10],
        "status": "complete",
        "complete": True,
        "rows": output_rows,
    }


def build_roster_candidate(
    database: Path,
    *,
    run_id: str | None = None,
    identity_links_path: Path | None = None,
) -> dict[str, Any]:
    """Build an exact, read-only candidate from a completed roster audit."""
    connection = sqlite3.connect(database)
    connection.row_factory = sqlite3.Row
    if run_id:
        run = connection.execute(
            """
            SELECT run_id, completed_at FROM runs
            WHERE run_id=? AND status='complete'
            """,
            (run_id,),
        ).fetchone()
    else:
        run = connection.execute(
            """
            SELECT run_id, completed_at FROM runs
            WHERE status='complete'
            ORDER BY completed_at DESC LIMIT 1
            """
        ).fetchone()
    if not run:
        connection.close()
        raise RuntimeError("No completed revenue roster snapshot exists")
    roster_rows = connection.execute(
        """
        SELECT service, source_row, email, status, classification, product,
               trainer, session_length, sessions_per_week,
               weekly_allocation, payment_marker,
               contract_length, renewal_date
        FROM roster_snapshot
        WHERE run_id=?
        ORDER BY lower(trim(email)), service, source_row
        """,
        (run["run_id"],),
    ).fetchall()
    connection.close()

    aliases = _load_aliases(identity_links_path)
    people: dict[str, list[dict[str, Any]]] = defaultdict(list)
    missing_identity: list[str] = []
    for row in roster_rows:
        service = str(row["service"] or "").strip().upper()
        status = " ".join(str(row["status"] or "").split())
        if service == "SGPT" and status.lower() not in ACTIVE_SGPT_STATUSES:
            continue
        if service not in {"SGPT", "PT"}:
            continue
        email = _normalise_email(row["email"])
        email = aliases.get(email, email)
        if not EMAIL_PATTERN.fullmatch(email):
            missing_identity.append(f"{service}:{row['source_row']}")
            continue
        people[email].append(
            {
                "service_type": service,
                "status": status or "Active",
                "classification": (
                    " ".join(str(row["classification"] or "").split()) or None
                ),
                "product": (
                    " ".join(str(row["product"] or "").split()) or None
                ),
                "source_row": int(row["source_row"]),
                "assigned_trainer": _text(row["trainer"]),
                "contracted_weekly_frequency": _text(
                    row["sessions_per_week"]
                ),
                "service_duration": _text(row["session_length"]),
                "weekly_allocation": _amount(row["weekly_allocation"]),
                "allocation_currency": (
                    "AUD" if row["weekly_allocation"] is not None else None
                ),
                "contract_length": _text(row["contract_length"]),
                "effective_to": _iso_date(row["renewal_date"]),
                "payment_marker": _text(row["payment_marker"]),
                "allocation_basis": (
                    "weekly_recurring"
                    if row["weekly_allocation"] is not None
                    else (
                        "prepaid"
                        if str(
                            row["payment_marker"] or ""
                        ).strip().upper() in PREPAID_MARKERS
                        or status.lower() == "active - pia"
                        else "unresolved"
                    )
                ),
            }
        )
    if missing_identity:
        raise ValueError(
            "Roster candidate contains rows without an exact governed "
            f"identity: {', '.join(missing_identity)}"
        )

    output_rows: list[dict[str, Any]] = []
    for email, services in sorted(people.items()):
        service_types = [item["service_type"] for item in services]
        if len(service_types) != len(set(service_types)):
            raise ValueError(
                f"Roster candidate has duplicate service rows for {email}"
            )
        output_rows.append(
            {
                "canonical_key": email,
                "services": sorted(
                    services, key=lambda item: item["service_type"]
                ),
            }
        )

    observed_at = str(run["completed_at"] or "").strip()
    if not observed_at:
        observed_at = datetime.now(UTC).isoformat(timespec="seconds")
    return {
        "schema_version": 2,
        "source": "active_roster_candidate",
        "source_system": "google_sheet",
        "source_run_id": str(run["run_id"]),
        "observed_at": observed_at,
        "as_of_date": observed_at[:10],
        "status": "complete",
        "complete": True,
        "rows": output_rows,
    }


def publish_roster_candidate(
    database: Path,
    *,
    run_id: str | None = None,
    identity_links_path: Path | None = None,
) -> dict[str, Any]:
    base_url = os.getenv("HUB_INGEST_BASE_URL", "").rstrip("/")
    secret = os.getenv("HUB_WEBHOOK_SECRET", "")
    if not base_url or not secret:
        return {"status": "not_configured"}
    payload = build_roster_candidate(
        database,
        run_id=run_id,
        identity_links_path=identity_links_path,
    )
    response = requests.post(
        f"{base_url}/active-roster-candidate",
        headers={"X-Hub-Secret": secret},
        json=payload,
        timeout=20,
    )
    response.raise_for_status()
    return response.json()


def publish_roster_candidate_payload(
    payload: dict[str, Any],
) -> dict[str, Any]:
    base_url = os.getenv("HUB_INGEST_BASE_URL", "").rstrip("/")
    secret = os.getenv("HUB_WEBHOOK_SECRET", "")
    if not base_url or not secret:
        return {"status": "not_configured"}
    response = requests.post(
        f"{base_url}/active-roster-candidate",
        headers={"X-Hub-Secret": secret},
        json=payload,
        timeout=20,
    )
    response.raise_for_status()
    return response.json()


def promote_roster_candidate_payload(
    snapshot_id: str,
) -> dict[str, Any]:
    source_base_url = os.getenv("HUB_SOURCE_BASE_URL", "").rstrip("/")
    ingest_base_url = os.getenv("HUB_INGEST_BASE_URL", "").rstrip("/")
    governance_base_url = os.getenv(
        "HUB_GOVERNANCE_BASE_URL", ""
    ).rstrip("/")
    if not governance_base_url:
        for base_url, suffix in (
            (source_base_url, "/sources"),
            (ingest_base_url, "/ingest"),
        ):
            if base_url.endswith(suffix):
                governance_base_url = (
                    base_url[: -len(suffix)] + "/governance"
                )
                break
    secret = os.getenv("HUB_WEBHOOK_SECRET", "")
    if not governance_base_url or not secret:
        return {"status": "not_configured"}
    response = requests.post(
        f"{governance_base_url}/promote-roster-candidate",
        headers={"X-Hub-Secret": secret},
        json={"expected_snapshot_id": snapshot_id},
        timeout=30,
    )
    if response.status_code == 409:
        detail = response.json()
        return {
            "status": "review_required",
            "reason": detail.get("error") or "governance review required",
        }
    response.raise_for_status()
    return response.json()
