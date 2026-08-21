from __future__ import annotations

import json
import os
import sqlite3
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

import requests

from reporting_control.cohort import (
    active_signal,
    authoritative_lifecycle_status,
    normalise_control_text,
)


def _json_list(value: Any) -> list[str]:
    try:
        parsed = json.loads(str(value or "[]"))
    except json.JSONDecodeError:
        return []
    if not isinstance(parsed, list):
        return []
    return sorted(
        {str(item).strip() for item in parsed if str(item).strip()}
    )


def _json_object(value: Any) -> dict[str, Any]:
    try:
        parsed = json.loads(str(value or "{}"))
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _service_type(name: Any) -> str:
    value = str(name or "").strip().lower()
    if "fast track" in value:
        return "fast_track"
    if value.startswith("pt ") or "personal training" in value:
        return "personal_training"
    if "online" in value:
        return "online"
    if value:
        return "sgpt"
    return "other"


def _lifecycle_status(
    row: sqlite3.Row,
    *,
    as_of: date | None = None,
) -> str:
    return authoritative_lifecycle_status(
        ghl_active=bool(row["ghl_active_signal"]),
        stripe_entitled=bool(row["stripe_entitled_signal"]),
        trainerize_active=bool(row["trainerize_active_signal"]),
        cancellation_status=row["cancellation_status"],
        final_access_date=row["final_access_date"],
        as_of=as_of or datetime.now(UTC).date(),
    )


def _iso_date(value: Any) -> str | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return date.fromisoformat(text[:10]).isoformat()
    except ValueError:
        return None


def _services(row: sqlite3.Row) -> list[dict[str, str]]:
    names = [
        str(row["membership_type"] or "").strip(),
        str(row["membership_stage"] or "").strip(),
    ]
    services = []
    seen: set[tuple[str, str]] = set()
    for name in names:
        if not name:
            continue
        service_type = _service_type(name)
        semantic_name = name.lower().replace(" package", "").strip()
        key = (service_type, semantic_name)
        if key in seen:
            continue
        seen.add(key)
        services.append(
            {
                "service_type": service_type,
                "service_name": name,
            }
        )
    return services or [{"service_type": "other", "service_name": "Other"}]


def _ghl_contact_names(
    connection: sqlite3.Connection,
    *,
    run_id: str,
) -> dict[str, dict[str, str | None]]:
    table_exists = connection.execute(
        """
        SELECT 1 FROM sqlite_master
        WHERE type='table' AND name='ghl_contacts'
        """
    ).fetchone()
    if not table_exists:
        return {}
    rows = connection.execute(
        """
        SELECT contact_id, first_name, last_name, date_updated
        FROM ghl_contacts
        WHERE run_id=?
        ORDER BY COALESCE(date_updated, ''), contact_id
        """,
        (run_id,),
    ).fetchall()
    return {
        str(row["contact_id"]): {
            "first_name": (
                str(row["first_name"] or "").strip() or None
            ),
            "last_name": (
                str(row["last_name"] or "").strip() or None
            ),
            "date_updated": (
                str(row["date_updated"] or "").strip() or None
            ),
        }
        for row in rows
    }


def build_membership_snapshot(
    database: Path,
    *,
    run_id: str | None = None,
) -> dict[str, Any]:
    connection = sqlite3.connect(database)
    connection.row_factory = sqlite3.Row
    if run_id is None:
        run = connection.execute(
            """
            SELECT run_id, finished_at FROM runs
            WHERE status='complete'
            ORDER BY started_at DESC LIMIT 1
            """
        ).fetchone()
    else:
        run = connection.execute(
            """
            SELECT run_id, finished_at FROM runs
            WHERE status='complete' AND run_id=?
            """,
            (run_id,),
        ).fetchone()
    if not run:
        connection.close()
        raise RuntimeError("No completed membership reconciliation exists")

    rows = connection.execute(
        """
        SELECT * FROM identity_register
        WHERE run_id=?
        ORDER BY identity_key
        """,
        (str(run["run_id"]),),
    ).fetchall()
    ghl_names = _ghl_contact_names(
        connection,
        run_id=str(run["run_id"]),
    )
    connection.close()
    cleaned = []
    as_of = date.fromisoformat(str(run["finished_at"])[:10])
    for row in rows:
        services = _services(row)
        ghl_contact_ids = _json_list(row["ghl_contact_ids_json"])
        named_contacts = [
            ghl_names[contact_id]
            for contact_id in ghl_contact_ids
            if contact_id in ghl_names
        ]
        selected_name = max(
            named_contacts,
            key=lambda item: str(item.get("date_updated") or ""),
            default={},
        )
        evidence = (
            _json_object(row["evidence_json"])
            if "evidence_json" in row.keys()
            else {}
        )
        raw_active_signal = active_signal(
            ghl_active=bool(row["ghl_active_signal"]),
            stripe_entitled=bool(row["stripe_entitled_signal"]),
            trainerize_active=bool(row["trainerize_active_signal"]),
        )
        cleaned.append(
            {
                "canonical_key": str(row["identity_key"]).strip().lower(),
                "email": str(row["email"] or "").strip().lower() or None,
                "first_name": selected_name.get("first_name"),
                "last_name": selected_name.get("last_name"),
                "source_ids": {
                    "ghl": ghl_contact_ids,
                    "stripe": _json_list(row["stripe_customer_ids_json"]),
                    "trainerize": _json_list(
                        row["trainerize_active_ids_json"]
                    )
                    + _json_list(row["trainerize_deactivated_ids_json"]),
                },
                "service_type": services[0]["service_type"],
                "service_name": services[0]["service_name"],
                "services": services,
                "lifecycle_status": _lifecycle_status(row, as_of=as_of),
                "active_signal": raw_active_signal,
                "ghl_active": bool(row["ghl_active_signal"]),
                "stripe_entitled": bool(row["stripe_entitled_signal"]),
                "trainerize_active": bool(row["trainerize_active_signal"]),
                "pt_block_trainer": (
                    str(evidence.get("pt_block_trainer") or "").strip()
                    or None
                ),
                "cancellation_status": normalise_control_text(
                    row["cancellation_status"]
                ),
                "cancellation_type": normalise_control_text(
                    row["cancellation_type"]
                ),
                "notice_end_date": _iso_date(row["notice_end_date"]),
                "final_access_date": _iso_date(row["final_access_date"]),
                "hold_status": (
                    str(evidence.get("hold_status") or "").strip() or None
                ),
                "hold_type": (
                    str(evidence.get("hold_type") or "").strip() or None
                ),
                "hold_start_date": _iso_date(
                    evidence.get("hold_start_date")
                ),
                "hold_end_date": _iso_date(
                    evidence.get("hold_end_date")
                ),
            }
        )
    observed_at = (
        str(run["finished_at"] or "").strip()
        or datetime.now(UTC).isoformat()
    )
    return {
        "schema_version": 5,
        "source_run_id": str(run["run_id"]),
        "observed_at": observed_at,
        "rows": cleaned,
    }


def publish_membership_snapshot(
    database: Path,
    *,
    run_id: str | None = None,
    timeout: int = 60,
) -> dict[str, Any]:
    base_url = os.getenv("HUB_INGEST_BASE_URL", "").rstrip("/")
    secret = os.getenv("HUB_WEBHOOK_SECRET", "")
    if not base_url or not secret:
        return {"status": "not_configured"}
    payload = build_membership_snapshot(database, run_id=run_id)
    response = requests.post(
        f"{base_url}/membership-reconciliation",
        headers={"X-Hub-Secret": secret},
        json=payload,
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()
