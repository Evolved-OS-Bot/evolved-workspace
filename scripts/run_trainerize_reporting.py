#!/usr/bin/env python3
"""Run the complete read-only membership reconciliation and performance report."""

from __future__ import annotations

import argparse
import json

from membership_reconciliation import run_reconciliation
from trainerize_performance_reporting import run_performance_reporting


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--include-invoices",
        action="store_true",
        help="Include the latest 90 days of Stripe invoices. Daily runs use subscription status by default.",
    )
    args = parser.parse_args()

    reconciliation = run_reconciliation(fetch_invoices=args.include_invoices)
    performance = run_performance_reporting()
    print(
        json.dumps(
            {
                "status": "complete",
                "mode": "read_only",
                "reconciliation": {
                    "run_id": reconciliation["run_id"],
                    "sources": reconciliation["sources"],
                    "identity_count": reconciliation["identity_count"],
                    "exception_count": reconciliation["exception_count"],
                    "exceptions_by_severity": reconciliation[
                        "exceptions_by_severity"
                    ],
                },
                "performance": performance,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
