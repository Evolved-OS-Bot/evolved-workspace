from __future__ import annotations

import json
import os
import sqlite3
from collections import defaultdict
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

import requests

from .hub_membership_client import _json_list, _services


CURRENT_SUBSCRIPTION_STATUSES = {"active", "trialing"}


def _json_object(value: Any) -> dict[str, Any]:
    try:
        parsed = json.loads(str(value or "null"))
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _date(value: Any) -> str | None:
    text = str(value or "").strip()
    return text[:10] if len(text) >= 10 else None


def _timestamp_date(value: Any) -> str | None:
    try:
        return datetime.fromtimestamp(
            int(value), tz=UTC
        ).date().isoformat()
    except (TypeError, ValueError, OSError):
        return _date(value)


def _invoice_line_coverage(
    invoice: sqlite3.Row,
) -> tuple[str | None, str | None]:
    raw = _json_object(invoice["raw_json"])
    periods = []
    for line in (raw.get("lines") or {}).get("data") or []:
        if bool(line.get("proration")):
            continue
        parent = line.get("parent") or {}
        subscription_details = (
            parent.get("subscription_item_details") or {}
        )
        if bool(subscription_details.get("proration")):
            continue
        try:
            amount = Decimal(str(line.get("amount") or "0"))
        except InvalidOperation:
            continue
        if amount <= 0:
            continue
        period = line.get("period") or {}
        start = _timestamp_date(period.get("start"))
        end = _timestamp_date(period.get("end"))
        if start and end and start <= end:
            periods.append((start, end))
    unique = sorted(set(periods))
    if not unique:
        return None, None
    end_dates = {end for _, end in unique}
    if len(end_dates) != 1:
        return None, None
    return min(start for start, _ in unique), unique[0][1]


def _is_current_subscription(row: sqlite3.Row) -> bool:
    return (
        str(row["status"] or "").strip().lower()
        in CURRENT_SUBSCRIPTION_STATUSES
        and not bool(_json_object(row["pause_collection_json"]))
    )


def _weekly_amount(subscriptions: list[sqlite3.Row]) -> str | None:
    total = Decimal("0")
    found = False
    for subscription in subscriptions:
        raw = _json_object(subscription["raw_json"])
        for item in (raw.get("items") or {}).get("data") or []:
            price = item.get("price") or {}
            unit_amount = price.get("unit_amount")
            recurring = price.get("recurring") or {}
            if unit_amount in (None, ""):
                continue
            interval_count = Decimal(
                str(recurring.get("interval_count") or 1)
            )
            amount = (
                Decimal(str(unit_amount))
                * Decimal(str(item.get("quantity") or 1))
                / Decimal("100")
            )
            interval = recurring.get("interval")
            if interval == "day":
                weekly = amount * Decimal("7") / interval_count
            elif interval == "week":
                weekly = amount / interval_count
            elif interval == "month":
                weekly = (
                    amount
                    * Decimal("12")
                    / Decimal("52")
                    / interval_count
                )
            elif interval == "year":
                weekly = amount / Decimal("52") / interval_count
            else:
                continue
            total += weekly
            found = True
    return f"{total:.2f}" if found else None


def _event_service_type(services: list[dict[str, Any]]) -> str:
    service_type = str(services[0]["service_type"] or "other")
    if service_type in {"sgpt", "personal_training"}:
        return service_type
    if service_type == "fast_track":
        return "sgpt"
    return "other"


def build_stripe_commercial_evidence(
    database: Path,
    *,
    run_id: str | None = None,
) -> dict[str, Any]:
    connection = sqlite3.connect(database)
    connection.row_factory = sqlite3.Row
    if run_id:
        run = connection.execute(
            """
            SELECT run_id, finished_at FROM runs
            WHERE run_id=? AND status='complete'
            """,
            (run_id,),
        ).fetchone()
    else:
        run = connection.execute(
            """
            SELECT run_id, finished_at FROM runs
            WHERE status='complete'
            ORDER BY finished_at DESC, started_at DESC LIMIT 1
            """
        ).fetchone()
    if not run:
        connection.close()
        raise RuntimeError("No completed reconciliation run exists")
    selected_run = str(run["run_id"])
    identities = connection.execute(
        """
        SELECT * FROM identity_register
        WHERE run_id=? AND stripe_customer_ids_json <> '[]'
        ORDER BY identity_key
        """,
        (selected_run,),
    ).fetchall()
    subscriptions = connection.execute(
        "SELECT * FROM stripe_subscriptions WHERE run_id=?",
        (selected_run,),
    ).fetchall()
    invoices = connection.execute(
        "SELECT * FROM stripe_invoices WHERE run_id=?",
        (selected_run,),
    ).fetchall()
    connection.close()

    subscriptions_by_customer: dict[str, list[sqlite3.Row]] = defaultdict(list)
    invoices_by_customer: dict[str, list[sqlite3.Row]] = defaultdict(list)
    invoices_by_subscription: dict[str, list[sqlite3.Row]] = defaultdict(list)
    for subscription in subscriptions:
        subscriptions_by_customer[
            str(subscription["customer_id"] or "")
        ].append(subscription)
    for invoice in invoices:
        invoices_by_customer[str(invoice["customer_id"] or "")].append(invoice)
        invoices_by_subscription[
            str(invoice["subscription_id"] or "")
        ].append(invoice)
    for values in invoices_by_subscription.values():
        values.sort(key=lambda row: str(row["created_at"] or ""), reverse=True)

    customer_owner: dict[str, str] = {}
    cleaned = []
    as_of_date = _date(run["finished_at"]) or datetime.now(UTC).date().isoformat()
    for identity in identities:
        canonical_key = str(identity["identity_key"]).strip().lower()
        customer_ids = _json_list(identity["stripe_customer_ids_json"])
        for customer_id in customer_ids:
            previous = customer_owner.get(customer_id)
            if previous and previous != canonical_key:
                raise RuntimeError(
                    f"Stripe customer {customer_id} has conflicting owners"
                )
            customer_owner[customer_id] = canonical_key
        services = list(
            {
                service["service_type"]: service
                for service in _services(identity)
            }.values()
        )
        identity_subscriptions = [
            subscription
            for customer_id in customer_ids
            for subscription in subscriptions_by_customer.get(
                customer_id,
                [],
            )
        ]
        current_subscriptions = [
            row for row in identity_subscriptions if _is_current_subscription(row)
        ]
        entitlements = []
        entitlement_ids: set[str] = set()
        for subscription in current_subscriptions:
            subscription_id = str(subscription["subscription_id"])
            latest_invoice = (
                invoices_by_subscription.get(subscription_id) or [None]
            )[0]
            verified_paid = bool(
                latest_invoice
                and latest_invoice["paid"]
                and str(latest_invoice["status"] or "") == "paid"
            )
            for service in services:
                source_record_id = (
                    f"{subscription_id}:{service['service_type']}"
                )
                entitlement_ids.add(source_record_id)
                entitlements.append(
                    {
                        "source_record_id": source_record_id,
                        "service_type": service["service_type"],
                        "status": "confirmed" if verified_paid else "pending",
                        "effective_from": _date(
                            subscription["current_period_start"]
                        ),
                        "effective_to": _date(
                            subscription["current_period_end"]
                        ),
                        "basis": (
                            "active_unpaused_subscription_and_paid_invoice"
                            if verified_paid
                            else "active_unpaused_subscription_without_paid_invoice"
                        ),
                    }
                )
        accounts = []
        events = []
        event_service_type = _event_service_type(services)
        for customer_id in customer_ids:
            customer_subscriptions = subscriptions_by_customer.get(
                customer_id,
                [],
            )
            customer_current = [
                row
                for row in customer_subscriptions
                if _is_current_subscription(row)
            ]
            customer_paused = any(
                bool(_json_object(row["pause_collection_json"]))
                for row in customer_subscriptions
            )
            if customer_current:
                account_status = "collecting"
            elif customer_paused:
                account_status = "paused"
            else:
                account_status = "cancelled"
            accounts.append(
                {
                    "source_account_id": customer_id,
                    "agreement_id": (
                        ",".join(
                            sorted(
                                str(row["subscription_id"])
                                for row in customer_current
                            )
                        )
                        or None
                    ),
                    "status": account_status,
                    "weekly_amount": _weekly_amount(customer_current),
                }
            )
            for invoice in invoices_by_customer.get(customer_id, []):
                raw_status = str(invoice["status"] or "").lower()
                if invoice["paid"] and raw_status == "paid":
                    status = "completed"
                elif raw_status == "open":
                    status = "pending"
                elif raw_status == "uncollectible":
                    status = "failed"
                else:
                    continue
                amount_cents = int(
                    invoice["amount_paid"]
                    if status == "completed"
                    else invoice["amount_due"]
                    or 0
                )
                if amount_cents <= 0:
                    continue
                coverage_start, coverage_end = _invoice_line_coverage(
                    invoice
                )
                events.append(
                    {
                        "source_event_id": str(invoice["invoice_id"]),
                        "source_account_id": customer_id,
                        "occurred_on": (
                            _date(invoice["created_at"])
                            or _date(invoice["period_end"])
                        ),
                        "amount": f"{Decimal(amount_cents) / 100:.2f}",
                        "status": status,
                        "service_type": event_service_type,
                        "cadence": "recurring",
                        "description": (
                            f"Stripe invoice {invoice['invoice_id']}"
                        ),
                        "coverage_start": coverage_start,
                        "coverage_end": coverage_end,
                    }
                )
                coverage_entitlement_id = (
                    f"{invoice['invoice_id']}:coverage:{event_service_type}"
                )
                if (
                    status == "completed"
                    and event_service_type in {
                        "sgpt",
                        "personal_training",
                    }
                    and coverage_start
                    and coverage_end
                    and coverage_start < coverage_end
                    and coverage_start <= as_of_date <= coverage_end
                    and coverage_entitlement_id not in entitlement_ids
                ):
                    entitlement_ids.add(coverage_entitlement_id)
                    entitlements.append(
                        {
                            "source_record_id": coverage_entitlement_id,
                            "service_type": event_service_type,
                            "status": "confirmed",
                            "effective_from": coverage_start,
                            "effective_to": coverage_end,
                            "basis": (
                                "paid_stripe_invoice_line_coverage_period"
                            ),
                        }
                    )
        cleaned.append(
            {
                "canonical_key": canonical_key,
                "email": (
                    str(identity["email"] or "").strip().lower() or None
                ),
                "source_identity_ids": customer_ids,
                "entitlements": entitlements,
                "payment_accounts": accounts,
                "payment_events": events,
            }
        )
    return {
        "schema_version": 2,
        "source_system": "stripe",
        "source_run_id": selected_run,
        "observed_at": (
            str(run["finished_at"] or "").strip()
            or datetime.now(UTC).isoformat()
        ),
        "rows": cleaned,
    }


def publish_stripe_commercial_evidence(
    database: Path,
    *,
    run_id: str | None = None,
    timeout: int = 120,
) -> dict[str, Any]:
    base_url = os.getenv("HUB_INGEST_BASE_URL", "").rstrip("/")
    secret = os.getenv("HUB_WEBHOOK_SECRET", "")
    if not base_url or not secret:
        return {"status": "not_configured"}
    payload = build_stripe_commercial_evidence(database, run_id=run_id)
    response = requests.post(
        f"{base_url}/commercial-evidence",
        headers={"X-Hub-Secret": secret},
        json=payload,
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()
