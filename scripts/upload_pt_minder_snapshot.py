#!/usr/bin/env python3
"""Validate and upload a manually exported PT Minder snapshot to Railway."""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from operating_data_hub.contracts import validate_pt_minder  # noqa: E402


BRISBANE = ZoneInfo("Australia/Brisbane")
COLUMN_ALIASES = {
    "source_account_id": (
        "source_account_id",
        "account id",
        "client id",
        "member id",
    ),
    "email": ("email", "email address"),
    "agreement_id": ("agreement_id", "agreement id", "debit id"),
    "product": ("product", "membership", "plan"),
    "state": ("state", "status", "payment status"),
    "amount": ("amount", "weekly amount", "debit amount"),
    "last_successful_payment": (
        "last_successful_payment",
        "last successful payment",
        "last payment date",
    ),
    "next_scheduled_payment": (
        "next_scheduled_payment",
        "next scheduled payment",
        "next payment date",
    ),
    "failed_payment_date": (
        "failed_payment_date",
        "failed payment date",
        "last failed payment",
    ),
}


def _normalise_header(value: str) -> str:
    return " ".join(str(value or "").strip().lower().split())


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError("PT Minder export has no header row")
        header_map = {
            _normalise_header(column): column for column in reader.fieldnames
        }
        resolved = {}
        for target, aliases in COLUMN_ALIASES.items():
            source = next(
                (
                    header_map[alias]
                    for alias in aliases
                    if alias in header_map
                ),
                None,
            )
            if source:
                resolved[target] = source
        required = {"source_account_id", "state"}
        missing = required - set(resolved)
        if missing:
            raise ValueError(
                "PT Minder export is missing required columns: "
                + ", ".join(sorted(missing))
            )
        return [
            {
                target: str(row.get(source) or "").strip()
                for target, source in resolved.items()
            }
            for row in reader
            if any(str(value or "").strip() for value in row.values())
        ]


def build_payload(path: Path) -> dict:
    if path.suffix.lower() == ".json":
        raw = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(raw, list):
            raw = {"rows": raw}
    elif path.suffix.lower() == ".csv":
        raw = {"rows": read_csv(path)}
    else:
        raise ValueError("Snapshot must be a .csv or .json file")
    raw.setdefault("observed_at", datetime.now(BRISBANE).isoformat())
    return validate_pt_minder(raw)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshot", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    payload = build_payload(args.snapshot)
    safe_summary = {
        "status": "validated",
        "observed_at": payload["observed_at"],
        "row_count": len(payload["rows"]),
    }
    if args.dry_run:
        print(json.dumps(safe_summary, indent=2))
        return 0

    base_url = os.environ["HUB_BASE_URL"].rstrip("/")
    secret = os.environ["HUB_WEBHOOK_SECRET"]
    response = requests.post(
        f"{base_url}/api/v1/ingest/pt-minder",
        headers={"X-Hub-Secret": secret},
        json=payload,
        timeout=60,
    )
    response.raise_for_status()
    result = response.json()
    print(
        json.dumps(
            {
                **safe_summary,
                "hub_status": result.get("status"),
                "snapshot_id": result.get("snapshot_id"),
                "fingerprint": result.get("fingerprint"),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

