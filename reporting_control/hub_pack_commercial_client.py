from __future__ import annotations

import os
from collections import defaultdict
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any, Iterable

import requests


def _normalise_email(value: Any) -> str:
    return str(value or "").strip().lower()


def _contact_value(contact: Any, field: str) -> Any:
    if isinstance(contact, dict):
        return contact.get(field)
    return getattr(contact, field, None)


def build_stripe_pack_commercial_evidence(
    contacts: Iterable[Any],
    pack_payments_by_contact_id: dict[str, list[Any]],
    *,
    source_run_id: str,
    observed_at: str | None = None,
) -> dict[str, Any]:
    """Build fail-closed commercial evidence from explicitly mapped PT packs."""
    contacts_by_id = {
        str(_contact_value(contact, "id")): contact
        for contact in contacts
        if str(_contact_value(contact, "id") or "").strip()
    }
    grouped: dict[str, dict[str, Any]] = {}
    seen_payment_ids: set[str] = set()
    for contact_id, payments in pack_payments_by_contact_id.items():
        contact = contacts_by_id.get(str(contact_id))
        email = _normalise_email(_contact_value(contact, "email"))
        if contact is None or not email:
            continue
        row = grouped.setdefault(
            email,
            {
                "canonical_key": email,
                "email": email,
                "source_identity_ids": [],
                "entitlements": [],
                "payment_accounts": [],
                "payment_events": [],
            },
        )
        account_id = f"pack-beneficiary:{contact_id}"
        row["source_identity_ids"].append(str(contact_id))
        row["payment_accounts"].append(
            {
                "source_account_id": account_id,
                "agreement_id": None,
                "status": "paid_in_advance",
                "weekly_amount": None,
            }
        )
        for payment in payments:
            payment_id = str(payment.payment_intent_id).strip()
            if not payment_id or payment_id in seen_payment_ids:
                continue
            seen_payment_ids.add(payment_id)
            paid_on = datetime.fromtimestamp(
                int(payment.created), tz=UTC
            ).date().isoformat()
            amount = Decimal(int(payment.amount_received)) / Decimal("100")
            row["source_identity_ids"].append(payment_id)
            row["entitlements"].append(
                {
                    "source_record_id": (
                        f"{payment_id}:personal_training"
                    ),
                    "service_type": "personal_training",
                    "quantity": None,
                    "unit": "prepaid pack",
                    "status": "confirmed",
                    "effective_from": paid_on,
                    "effective_to": None,
                    "basis": "approved_payment_to_contact_pack_map",
                }
            )
            row["payment_events"].append(
                {
                    "source_event_id": payment_id,
                    "source_account_id": account_id,
                    "occurred_on": paid_on,
                    "amount": f"{amount:.2f}",
                    "status": "completed",
                    "service_type": "personal_training",
                    "cadence": "ad_hoc",
                    "description": (
                        "Stripe prepaid PT pack with approved beneficiary map"
                    ),
                }
            )

    cleaned = []
    for row in grouped.values():
        if not row["entitlements"]:
            continue
        row["source_identity_ids"] = sorted(
            set(row["source_identity_ids"])
        )
        unique_accounts = {
            account["source_account_id"]: account
            for account in row["payment_accounts"]
        }
        row["payment_accounts"] = list(unique_accounts.values())
        cleaned.append(row)
    return {
        "schema_version": 1,
        "source_system": "stripe_pack",
        "source_run_id": source_run_id,
        "observed_at": observed_at or datetime.now(UTC).isoformat(),
        "rows": sorted(cleaned, key=lambda row: row["canonical_key"]),
    }


def publish_stripe_pack_commercial_evidence(
    contacts: Iterable[Any],
    pack_payments_by_contact_id: dict[str, list[Any]],
    *,
    source_run_id: str,
    observed_at: str | None = None,
    timeout: int = 60,
) -> dict[str, Any]:
    base_url = os.getenv("HUB_INGEST_BASE_URL", "").rstrip("/")
    secret = os.getenv("HUB_WEBHOOK_SECRET", "")
    if not base_url or not secret:
        return {"status": "not_configured"}
    payload = build_stripe_pack_commercial_evidence(
        contacts,
        pack_payments_by_contact_id,
        source_run_id=source_run_id,
        observed_at=observed_at,
    )
    response = requests.post(
        f"{base_url}/commercial-evidence",
        headers={"X-Hub-Secret": secret},
        json=payload,
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()
