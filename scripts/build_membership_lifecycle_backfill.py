#!/usr/bin/env python3
"""Build a protected lifecycle backfill from existing governed evidence.

This does not call GHL, Stripe, Trainerize or Google Sheets. It reuses the
membership-reconciliation database and accepted cohort snapshots already
produced by the governed control plane.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any


def _text(value: Any) -> str:
    return " ".join(str(value or "").strip().lower().split())


def _date(value: Any) -> str | None:
    text = str(value or "").strip()[:10]
    if not text:
        return None
    try:
        return date.fromisoformat(text).isoformat()
    except ValueError:
        return None


def _source_record_id(*parts: Any) -> str:
    material = "|".join(str(part or "") for part in parts)
    return "historical-lifecycle:" + hashlib.sha256(
        material.encode("utf-8")
    ).hexdigest()


def _event_type(row: sqlite3.Row) -> tuple[str | None, str | None]:
    cancellation_type = _text(row["cancellation_type"])
    service = " ".join(
        (
            _text(row["membership_type"]),
            _text(row["membership_stage"]),
        )
    )
    if cancellation_type == "membership":
        return "membership_ended", "straight_cancellation"
    if cancellation_type == "pt":
        if any(
            token in service
            for token in (
                "fast track",
                "strong",
                "sgpt",
                "bronze",
                "silver",
                "gold",
            )
        ):
            return "downgrade_only", "pt_ended_sgpt_continues"
        if any(
            token in service
            for token in ("pt only", "pt 1", "pt 2", "pt 3")
        ):
            return "membership_ended", "pt_only_membership_ended"
    return None, None


def build_backfill_payload(
    *,
    membership_database: Path,
    cohort_snapshots: list[Path],
    observed_at: datetime | None = None,
) -> dict[str, Any]:
    connection = sqlite3.connect(membership_database)
    connection.row_factory = sqlite3.Row
    run = connection.execute(
        """
        SELECT run_id, finished_at
        FROM runs
        WHERE status='complete'
        ORDER BY started_at DESC
        LIMIT 1
        """
    ).fetchone()
    if not run:
        connection.close()
        raise RuntimeError("No complete membership reconciliation exists")
    rows = connection.execute(
        """
        SELECT *
        FROM identity_register
        WHERE run_id=?
          AND (
            TRIM(COALESCE(cancellation_type, '')) <> ''
            OR TRIM(COALESCE(cancellation_status, '')) <> ''
          )
        ORDER BY identity_key
        """,
        (run["run_id"],),
    ).fetchall()
    connection.close()

    records = []
    for row in rows:
        event_type, transition_kind = _event_type(row)
        final_access = _date(row["final_access_date"])
        if event_type and final_access:
            confidence = "high"
            ambiguous = False
        else:
            confidence = "unresolved"
            ambiguous = True
        records.append(
            {
                "canonical_key": str(row["identity_key"]).strip().lower(),
                "event_type": event_type or "membership_ended",
                "effective_date": final_access,
                "ambiguous_date": ambiguous,
                "confidence": confidence,
                "transition_kind": transition_kind,
                "source_record_id": _source_record_id(
                    run["run_id"],
                    row["identity_key"],
                    row["cancellation_type"],
                    row["final_access_date"],
                ),
                "evidence": {
                    "source": "existing membership reconciliation",
                    "source_run_id": run["run_id"],
                    "cancellation_status": row["cancellation_status"],
                    "cancellation_type": row["cancellation_type"],
                    "notice_end_date": _date(row["notice_end_date"]),
                    "date_rule": (
                        "exact GHL final-access date"
                        if final_access
                        else "date unavailable; quarantined"
                    ),
                },
            }
        )

    opening_cohorts = []
    for path in cohort_snapshots:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError(f"{path} must contain an object")
        as_of_date = _date(payload.get("as_of_date"))
        confirmed = sorted(
            {
                str(row.get("canonical_key") or "").strip().lower()
                for row in payload.get("rows") or []
                if row.get("confirmed_active")
                and str(row.get("canonical_key") or "").strip()
            }
        )
        complete = bool(payload.get("complete")) and bool(as_of_date)
        opening_cohorts.append(
            {
                "as_of_date": as_of_date,
                "canonical_keys": confirmed,
                "coverage_complete": complete,
                "confidence": "high" if complete else "unresolved",
                "source_record_id": _source_record_id(
                    path.name,
                    as_of_date,
                    payload.get("rule_version"),
                ),
                "evidence": {
                    "source": "accepted active-client cohort snapshot",
                    "source_file": path.name,
                    "rule_version": payload.get("rule_version"),
                    "source_refs": payload.get("source_refs") or {},
                },
            }
        )
    instant = observed_at or datetime.now(UTC)
    if instant.tzinfo is None:
        raise ValueError("observed_at must include a timezone")
    return {
        "schema_version": 1,
        "source_run_id": f"membership-lifecycle-backfill-{run['run_id']}",
        "observed_at": instant.astimezone(UTC).isoformat(),
        "records": records,
        "opening_cohorts": opening_cohorts,
        "summary": {
            "records": len(records),
            "accepted_exact_date_candidates": sum(
                row["confidence"] == "high" and not row["ambiguous_date"]
                for row in records
            ),
            "quarantined_ambiguous_candidates": sum(
                row["ambiguous_date"] for row in records
            ),
            "opening_cohorts": len(opening_cohorts),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("membership_database", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument(
        "--cohort-snapshot",
        action="append",
        type=Path,
        default=[],
    )
    args = parser.parse_args()
    payload = build_backfill_payload(
        membership_database=args.membership_database,
        cohort_snapshots=args.cohort_snapshot,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.chmod(args.output, 0o600)
    print(json.dumps(payload["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
