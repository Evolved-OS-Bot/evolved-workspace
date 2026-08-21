#!/usr/bin/env python3
"""Preflight a second independent purpose-aware PT Minder capture."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from operating_data_hub.contracts import (  # noqa: E402
    fingerprint,
    validate_pt_minder,
)


def verify_capture(
    payload: dict,
    *,
    prior_observed_at: str,
    prior_fingerprint: str | None = None,
    expected_accounts: int = 27,
    account_tolerance: int = 5,
    minimum_transactions: int = 500,
) -> dict:
    validated = validate_pt_minder(payload)
    observed_at = datetime.fromisoformat(
        validated["observed_at"].replace("Z", "+00:00")
    )
    prior_observed = datetime.fromisoformat(
        prior_observed_at.replace("Z", "+00:00")
    )
    if observed_at.tzinfo is None or prior_observed.tzinfo is None:
        raise ValueError("capture observation times must include a timezone")

    capture_fingerprint = fingerprint(validated)
    account_count = len(validated["rows"])
    transaction_count = sum(
        len(row.get("transactions") or [])
        for row in validated["rows"]
    )
    failures = []
    if not validated["transaction_detail_complete"]:
        failures.append("transaction detail is incomplete")
    if observed_at <= prior_observed:
        failures.append("capture is not newer than the first parity cycle")
    if (
        prior_fingerprint
        and capture_fingerprint == prior_fingerprint.strip().lower()
    ):
        failures.append("capture fingerprint matches the prior snapshot")
    lower_accounts = max(1, expected_accounts - account_tolerance)
    upper_accounts = expected_accounts + account_tolerance
    if not lower_accounts <= account_count <= upper_accounts:
        failures.append(
            "account count moved outside the approved review tolerance"
        )
    if transaction_count < minimum_transactions:
        failures.append(
            "transaction history is below the approved completeness floor"
        )

    return {
        "status": "ready_for_upload" if not failures else "blocked",
        "ready_for_upload": not failures,
        "schema_version": validated["schema_version"],
        "observed_at": validated["observed_at"],
        "account_count": account_count,
        "transaction_count": transaction_count,
        "fingerprint": capture_fingerprint,
        "comparison": {
            "prior_observed_at": prior_observed_at,
            "expected_accounts": expected_accounts,
            "account_tolerance": account_tolerance,
            "minimum_transactions": minimum_transactions,
        },
        "failures": failures,
        "next_step": (
            "Upload to the governed hub, then run the protected revenue "
            "parity comparison. Do not promote the feed unless that "
            "comparison is exact."
            if not failures
            else "Correct or repeat the capture before any upload."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshot", type=Path)
    parser.add_argument("--prior-observed-at", required=True)
    parser.add_argument("--prior-fingerprint")
    parser.add_argument("--expected-accounts", type=int, default=27)
    parser.add_argument("--account-tolerance", type=int, default=5)
    parser.add_argument("--minimum-transactions", type=int, default=500)
    args = parser.parse_args()

    payload = json.loads(args.snapshot.read_text(encoding="utf-8"))
    result = verify_capture(
        payload,
        prior_observed_at=args.prior_observed_at,
        prior_fingerprint=args.prior_fingerprint,
        expected_accounts=args.expected_accounts,
        account_tolerance=args.account_tolerance,
        minimum_transactions=args.minimum_transactions,
    )
    print(json.dumps(result, indent=2))
    return 0 if result["ready_for_upload"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
