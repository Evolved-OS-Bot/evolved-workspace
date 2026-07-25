#!/usr/bin/env python3
"""Refresh read-only evidence and run the weekly revenue-gap controller."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
PRIVATE_DIR = ROOT / "data" / "private" / "revenue-gap-control"
BOOKING_DATABASE = PRIVATE_DIR / "pt_booking_shadow.sqlite"
LEGACY_EVIDENCE = PRIVATE_DIR / "legacy-payment-evidence.csv"
TIMING_ITEMS = PRIVATE_DIR / "timing-items.csv"
BRISBANE = ZoneInfo("Australia/Brisbane")


def _date(value: str) -> date:
    return date.fromisoformat(value)


def default_window(today: date) -> tuple[date, date]:
    monday = today - timedelta(days=today.weekday())
    if today.weekday() == 0:
        monday -= timedelta(days=7)
    return monday, monday + timedelta(days=6)


def _load_env(path: Path, target: dict[str, str]) -> None:
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        target.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def _run(command: list[str], environment: dict[str, str] | None = None) -> None:
    subprocess.run(
        command,
        cwd=ROOT,
        env=environment,
        check=True,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--window-start", type=_date)
    parser.add_argument("--window-end", type=_date)
    parser.add_argument(
        "--skip-source-refresh",
        action="store_true",
        help="Use existing protected membership and booking snapshots.",
    )
    args = parser.parse_args(argv)

    if bool(args.window_start) != bool(args.window_end):
        parser.error("Provide both --window-start and --window-end, or neither")
    window_start, window_end = (
        (args.window_start, args.window_end)
        if args.window_start
        else default_window(datetime.now(BRISBANE).date())
    )
    if window_end < window_start:
        parser.error("--window-end must not be before --window-start")

    PRIVATE_DIR.mkdir(parents=True, exist_ok=True)
    python = str(ROOT / ".venv" / "bin" / "python")
    if not Path(python).exists():
        python = sys.executable

    if not args.skip_source_refresh:
        _run(
            [
                python,
                str(ROOT / "scripts" / "membership_reconciliation.py"),
                "--include-invoices",
            ]
        )
        booking_env = os.environ.copy()
        _load_env(ROOT / "scripts" / ".env", booking_env)
        booking_env.update(
            {
                "DATABASE_PATH": str(BOOKING_DATABASE),
                "SHADOW_MODE": "true",
                "ENABLE_SCHEDULER": "false",
                "REPORT_DRY_RUN": "true",
                "KPI_WRITE_ENABLED": "false",
                "CROSS_SYSTEM_RECONCILIATION_ENABLED": "false",
            }
        )
        _run(
            [python, "-m", "pt_booking_shadow.run_weekly"],
            environment=booking_env,
        )

    command = [
        python,
        "-m",
        "revenue_gap_control",
        "--window-start",
        window_start.isoformat(),
        "--window-end",
        window_end.isoformat(),
        "--booking-db",
        str(BOOKING_DATABASE),
    ]
    if LEGACY_EVIDENCE.exists():
        command.extend(["--legacy-evidence-csv", str(LEGACY_EVIDENCE)])
    if TIMING_ITEMS.exists():
        command.extend(["--timing-items-csv", str(TIMING_ITEMS)])
    _run(command)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
