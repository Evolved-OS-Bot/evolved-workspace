#!/usr/bin/env python3
"""Replace the protected Railway legacy-payment register without echoing its rows."""

from __future__ import annotations

import argparse
import csv
import json
import os
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CSV = (
    ROOT
    / "data"
    / "private"
    / "revenue-gap-control"
    / "legacy-payment-evidence.csv"
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True)
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    args = parser.parse_args()

    if not args.url.startswith("https://"):
        parser.error("--url must use https")
    secret = os.getenv("WEBHOOK_SHARED_SECRET", "").strip()
    if not secret:
        raise RuntimeError("WEBHOOK_SHARED_SECRET is required")

    with args.csv.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    request = urllib.request.Request(
        f"{args.url.rstrip('/')}/revenue/evidence/legacy",
        data=json.dumps({"rows": rows}).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {secret}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            result = json.load(response)
    except urllib.error.HTTPError as exc:
        message = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Register upload failed with HTTP {exc.code}: {message}") from exc
    print(
        json.dumps(
            {
                "status": result.get("status"),
                "rowCount": result.get("rowCount"),
                "sha256": result.get("sha256"),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
