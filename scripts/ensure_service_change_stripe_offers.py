#!/usr/bin/env python3
"""Idempotently ensure the approved Stripe service-change offer catalogue."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import requests


WORKSPACE = Path(__file__).resolve().parents[1]
ENV_FILE = WORKSPACE / "scripts" / ".env"
API_BASE = "https://api.stripe.com/v1"
ONLINE_ONLY = {
    "service_name": "Online Only",
    "weekly_price_cents": 2700,
    "currency": "aud",
    "offer_version": "online-only-service-change-v1",
}
STRONG_COMMITMENT = {
    "service_name": "Strong, Fit & Flexible Membership",
    "discounted_weekly_price_cents": 8900,
    "original_weekly_price_cents": 9900,
    "currency": "aud",
    "offer_version": "strong-12-month-commitment-v1",
}


def load_env() -> None:
    for raw_line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


def stripe_request(method: str, path: str, *, data=None, params=None, key=None):
    response = requests.request(
        method,
        f"{API_BASE}{path}",
        auth=(os.environ["STRIPE_RESTRICTED_KEY"], ""),
        data=data,
        params=params,
        headers={"Idempotency-Key": key} if key else None,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def matching_prices(
    product_id: str,
    *,
    amount: int = ONLINE_ONLY["weekly_price_cents"],
    currency: str = ONLINE_ONLY["currency"],
) -> list[dict]:
    prices = stripe_request(
        "GET",
        "/prices",
        params={"product": product_id, "type": "recurring", "limit": 100},
    ).get("data", [])
    return [
        price
        for price in prices
        if price.get("active")
        and price.get("currency") == currency
        and price.get("unit_amount") == amount
        and (price.get("recurring") or {}).get("interval") == "week"
        and int((price.get("recurring") or {}).get("interval_count") or 1) == 1
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    load_env()

    products = stripe_request(
        "GET",
        "/products",
        params={"limit": 100},
    ).get("data", [])
    exact_products = [
        product
        for product in products
        if product.get("name") == ONLINE_ONLY["service_name"]
    ]
    online_matches = [
        (product, price)
        for product in exact_products
        for price in matching_prices(product["id"])
    ]
    if len(online_matches) > 1:
        raise RuntimeError("Multiple active Online Only A$27 weekly prices exist")
    online_product = None
    online_price = None
    if online_matches:
        online_product, online_price = online_matches[0]
    elif args.apply:
        active_products = [
            product for product in exact_products if product.get("active")
        ]
        if len(active_products) > 1:
            raise RuntimeError("Multiple active Online Only products exist")
        online_product = (
            active_products[0]
            if active_products
            else stripe_request(
                "POST",
                "/products",
                data={
                    "name": ONLINE_ONLY["service_name"],
                    "description": (
                        "Standard Trainerize programming and app access. "
                        "No routine facility, SGPT or PT access."
                    ),
                    "metadata[offer_version]": ONLINE_ONLY["offer_version"],
                },
                key="evolved-online-only-service-change-product-v1",
            )
        )
        online_price = stripe_request(
            "POST",
            "/prices",
            data={
                "product": online_product["id"],
                "currency": ONLINE_ONLY["currency"],
                "unit_amount": ONLINE_ONLY["weekly_price_cents"],
                "recurring[interval]": "week",
                "recurring[interval_count]": 1,
                "lookup_key": "evolved_online_only_weekly_aud_v1",
                "metadata[offer_version]": ONLINE_ONLY["offer_version"],
            },
            key="evolved-online-only-service-change-price-v1",
        )

    strong_candidates = [
        product
        for product in products
        if product.get("active")
        and str(product.get("name") or "").strip().lower()
        in {
            "strong, fit & flexible membership",
            "sculpt & strength",
        }
    ]
    strong_pairs = []
    for product in strong_candidates:
        original = matching_prices(
            product["id"],
            amount=STRONG_COMMITMENT["original_weekly_price_cents"],
        )
        discounted = matching_prices(
            product["id"],
            amount=STRONG_COMMITMENT["discounted_weekly_price_cents"],
        )
        if len(original) == 1 and len(discounted) <= 1:
            strong_pairs.append((product, original[0], discounted))
    if len(strong_pairs) != 1:
        raise RuntimeError(
            "Expected exactly one active Strong product with one A$99 weekly price"
        )
    strong_product, original_price, discounted_prices = strong_pairs[0]
    if discounted_prices:
        discounted_price = discounted_prices[0]
    elif args.apply:
        discounted_price = stripe_request(
            "POST",
            "/prices",
            data={
                "product": strong_product["id"],
                "currency": STRONG_COMMITMENT["currency"],
                "unit_amount": STRONG_COMMITMENT[
                    "discounted_weekly_price_cents"
                ],
                "recurring[interval]": "week",
                "recurring[interval_count]": 1,
                "lookup_key": "evolved_strong_commitment_weekly_aud_v1",
                "metadata[offer_version]": STRONG_COMMITMENT[
                    "offer_version"
                ],
            },
            key="evolved-strong-commitment-price-v1",
        )
    else:
        discounted_price = None

    print(
        json.dumps(
            {
                "status": (
                    "ready"
                    if online_price and discounted_price
                    else "missing"
                ),
                "online_only": {
                    "product_id": online_product["id"] if online_product else None,
                    "price_id": online_price["id"] if online_price else None,
                },
                "strong_12_month_commitment": {
                    "product_id": strong_product["id"],
                    "price_id": (
                        discounted_price["id"] if discounted_price else None
                    ),
                    "original_price_id": original_price["id"],
                },
            },
            indent=2,
        )
    )
    return 0 if online_price and discounted_price else 2


if __name__ == "__main__":
    raise SystemExit(main())
