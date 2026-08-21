#!/usr/bin/env python3
"""Read-only discovery of approved Stripe prices for service-change setup."""

from __future__ import annotations

import json
import os
from pathlib import Path

import requests


WORKSPACE = Path(__file__).resolve().parents[1]
ENV_FILE = WORKSPACE / "scripts" / ".env"
API_BASE = "https://api.stripe.com/v1"
TARGET_NAMES = {"Evolved Anywhere", "Online Only"}


def load_env() -> None:
    for raw_line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


def stripe_get(path: str, **params) -> dict:
    response = requests.get(
        f"{API_BASE}{path}",
        auth=(os.environ["STRIPE_RESTRICTED_KEY"], ""),
        params=params,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def main() -> int:
    load_env()
    products = stripe_get("/products", limit=100).get("data", [])
    matches = []
    for product in products:
        if product.get("name") not in TARGET_NAMES:
            continue
        prices = stripe_get(
            "/prices",
            product=product["id"],
            type="recurring",
            limit=100,
        ).get("data", [])
        for price in prices:
            recurring = price.get("recurring") or {}
            if (
                price.get("currency") == "aud"
                and recurring.get("interval") == "week"
                and int(recurring.get("interval_count") or 1) == 1
            ):
                matches.append(
                    {
                        "service_name": product["name"],
                        "product_active": bool(product.get("active")),
                        "product_id": product["id"],
                        "price_active": bool(price.get("active")),
                        "tax_behavior": price.get("tax_behavior"),
                        "price_id": price["id"],
                        "weekly_price_cents": price.get("unit_amount"),
                    }
                )
    print(json.dumps(matches, indent=2, sort_keys=True))
    return 0 if {item["service_name"] for item in matches} == TARGET_NAMES else 1


if __name__ == "__main__":
    raise SystemExit(main())
