from __future__ import annotations

from datetime import UTC, datetime, time, timedelta
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any, Iterable, Iterator
from zoneinfo import ZoneInfo

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


STRIPE_BASE_URL = "https://api.stripe.com/v1"
BRISBANE_TZ = ZoneInfo("Australia/Brisbane")
SETTLED_PT_MINDER_STATUSES = {"completed"}
REFUNDED_PT_MINDER_STATUSES = {"refunded"}


def gst_from_taxable_gross(gross_cents: int) -> int:
    """Return the GST component of a fully taxable GST-inclusive amount."""
    if gross_cents < 0:
        raise ValueError("gross_cents must not be negative")
    return int(
        (Decimal(gross_cents) / Decimal(11)).quantize(
            Decimal("1"),
            rounding=ROUND_HALF_UP,
        )
    )


def _utc_datetime(timestamp: Any, field: str) -> datetime:
    try:
        parsed = datetime.fromtimestamp(int(timestamp), UTC)
    except (TypeError, ValueError, OSError) as exc:
        raise ValueError(f"{field} must be a Unix timestamp") from exc
    return parsed


def _invoice_gst_cents(
    invoice: dict[str, Any],
    gross_cents: int,
) -> tuple[int | None, str | None, str | None]:
    total = invoice.get("total")
    total_excluding_tax = invoice.get("total_excluding_tax")
    try:
        total_cents = int(total)
        ex_tax_cents = int(total_excluding_tax)
    except (TypeError, ValueError):
        return (
            None,
            None,
            "invoice does not expose an explicit ex-GST total",
        )
    if total_cents <= 0:
        return None, None, "invoice total is not positive"
    gst_cents = total_cents - ex_tax_cents
    if gst_cents < 0 or gst_cents > total_cents:
        return None, None, "invoice GST amount is outside the invoice total"
    if total_cents != gross_cents:
        gst_cents = _proportional_gst(
            amount_cents=gross_cents,
            original_gross_cents=total_cents,
            original_gst_cents=gst_cents,
        )
        return (
            gst_cents,
            "proportional_from_stripe_invoice_tax",
            None,
        )
    return gst_cents, "stripe_invoice_total_excluding_tax", None


def _proportional_gst(
    *,
    amount_cents: int,
    original_gross_cents: int,
    original_gst_cents: int,
) -> int:
    if amount_cents <= 0 or original_gross_cents <= 0:
        raise ValueError("refund and original amounts must be positive")
    return int(
        (
            Decimal(original_gst_cents)
            * Decimal(amount_cents)
            / Decimal(original_gross_cents)
        ).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    )


class StripeCashReader:
    def __init__(self, api_key: str, timeout: int = 30) -> None:
        if not str(api_key or "").strip():
            raise RuntimeError("STRIPE_RESTRICTED_KEY is required")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.auth = (api_key, "")
        self.session.mount(
            "https://",
            HTTPAdapter(
                max_retries=Retry(
                    total=3,
                    connect=3,
                    read=3,
                    status=3,
                    backoff_factor=1,
                    status_forcelist=(429, 500, 502, 503, 504),
                    allowed_methods=frozenset({"GET"}),
                    raise_on_status=False,
                )
            ),
        )

    def payment_intents(
        self,
        *,
        created_gte: int,
    ) -> Iterator[dict[str, Any]]:
        query: dict[str, Any] = {
            "limit": 100,
            "created[gte]": created_gte,
            "expand[]": [
                "data.invoice",
                "data.latest_charge",
                "data.latest_charge.refunds",
            ],
        }
        while True:
            response = self.session.get(
                f"{STRIPE_BASE_URL}/payment_intents",
                params=query,
                timeout=self.timeout,
            )
            response.raise_for_status()
            payload = response.json()
            batch = payload.get("data") or []
            if not isinstance(batch, list):
                raise RuntimeError("Stripe returned an invalid payment page")
            for item in batch:
                if isinstance(item, dict):
                    yield item
            if not payload.get("has_more"):
                return
            if not batch or not str(batch[-1].get("id") or "").strip():
                raise RuntimeError(
                    "Stripe pagination ended without a continuation ID"
                )
            query["starting_after"] = batch[-1]["id"]


def build_stripe_cash_batch(
    *,
    payment_intents: Iterable[dict[str, Any]],
    observed_at: datetime,
    lookback_days: int = 400,
) -> dict[str, Any]:
    cutoff = observed_at - timedelta(days=lookback_days)
    events: list[dict[str, Any]] = []
    errors: list[str] = []
    seen: set[str] = set()
    source_records = 0

    for payment_intent in payment_intents:
        source_records += 1
        payment_id = str(payment_intent.get("id") or "").strip()
        if not payment_id or payment_intent.get("status") != "succeeded":
            continue
        if str(payment_intent.get("currency") or "").lower() != "aud":
            errors.append(f"{payment_id or 'payment'} is not AUD")
            continue
        charge = payment_intent.get("latest_charge")
        invoice = payment_intent.get("invoice")
        if not isinstance(charge, dict):
            errors.append(f"{payment_id} has no expanded settled charge")
            continue
        try:
            gross_cents = int(payment_intent.get("amount_received"))
        except (TypeError, ValueError):
            errors.append(f"{payment_id} has no received amount")
            continue
        if gross_cents <= 0:
            errors.append(f"{payment_id} has a non-positive received amount")
            continue
        occurred_at = _utc_datetime(
            charge.get("created"),
            f"{payment_id} charge created",
        )
        if occurred_at < cutoff:
            continue
        if isinstance(invoice, dict):
            gst_cents, gst_basis, gst_error = _invoice_gst_cents(
                invoice,
                gross_cents,
            )
            invoice_id = str(invoice.get("id") or "")
        else:
            gst_cents = gst_from_taxable_gross(gross_cents)
            gst_basis = "approved_fully_taxable_gst_inclusive_supply"
            gst_error = None
            invoice_id = ""
        if gst_error or gst_cents is None:
            errors.append(f"{payment_id}: {gst_error}")
            continue

        settled_id = f"{payment_id}:settled"
        if settled_id in seen:
            errors.append(f"{payment_id} duplicates a settled event")
            continue
        seen.add(settled_id)
        events.append(
            {
                "source_event_id": settled_id,
                "occurred_at": occurred_at.isoformat(),
                "event_type": "settled_cash",
                "currency": "AUD",
                "gross_amount_cents": gross_cents,
                "gst_amount_cents": gst_cents,
                "evidence": {
                    "payment_intent_id": payment_id,
                    "charge_id": str(charge.get("id") or ""),
                    "invoice_id": invoice_id,
                    "gst_basis": gst_basis,
                },
            }
        )

        refunds = (charge.get("refunds") or {}).get("data") or []
        if (charge.get("refunds") or {}).get("has_more"):
            errors.append(f"{payment_id} has an incomplete refund expansion")
            continue
        for refund in refunds:
            if not isinstance(refund, dict):
                errors.append(f"{payment_id} has an invalid refund record")
                continue
            refund_id = str(refund.get("id") or "").strip()
            if not refund_id or refund_id in seen:
                errors.append(f"{payment_id} has a duplicate refund")
                continue
            if str(refund.get("status") or "").lower() not in {
                "succeeded",
                "",
            }:
                continue
            try:
                refund_cents = int(refund.get("amount"))
            except (TypeError, ValueError):
                errors.append(f"{payment_id} refund has no amount")
                continue
            refund_at = _utc_datetime(
                refund.get("created"),
                f"{payment_id} refund created",
            )
            if refund_at < cutoff:
                continue
            refund_gst_cents = _proportional_gst(
                amount_cents=refund_cents,
                original_gross_cents=gross_cents,
                original_gst_cents=gst_cents,
            )
            seen.add(refund_id)
            events.append(
                {
                    "source_event_id": refund_id,
                    "occurred_at": refund_at.isoformat(),
                    "event_type": "refund",
                    "currency": "AUD",
                    "gross_amount_cents": refund_cents,
                    "gst_amount_cents": refund_gst_cents,
                    "evidence": {
                        "payment_intent_id": payment_id,
                        "charge_id": str(charge.get("id") or ""),
                        "invoice_id": invoice_id,
                        "gst_basis": (
                            "proportional_from_original_stripe_invoice"
                        ),
                    },
                }
            )

    return {
        "source_system": "stripe",
        "source_run_id": (
            "stripe-cash-"
            + observed_at.astimezone(UTC).strftime("%Y%m%dT%H%M%SZ")
        ),
        "observed_at": observed_at.astimezone(UTC).isoformat(),
        "complete": not errors,
        "events": events,
        "adapter_summary": {
            "lookback_days": lookback_days,
            "source_records": source_records,
            "accepted_events": len(events),
            "error_count": len(errors),
            "errors": errors[:20],
        },
    }


def build_pt_minder_cash_batch(
    snapshot: dict[str, Any],
    *,
    lookback_days: int = 400,
    as_of: datetime | None = None,
) -> dict[str, Any]:
    payload = snapshot.get("payload") or {}
    observed_at = datetime.fromisoformat(
        str(snapshot.get("observed_at") or "").replace("Z", "+00:00")
    ).astimezone(UTC)
    effective_as_of = (as_of or observed_at).astimezone(UTC)
    cutoff = effective_as_of - timedelta(days=lookback_days)
    errors: list[str] = []
    events: list[dict[str, Any]] = []
    seen: set[str] = set()

    if payload.get("transaction_detail_complete") is not True:
        errors.append("PT Minder transaction detail is incomplete")
    rows = payload.get("rows")
    if not isinstance(rows, list) or not rows:
        errors.append("PT Minder cash source has no account rows")
        rows = []

    for row in rows:
        for transaction in row.get("transactions") or []:
            status = str(transaction.get("status") or "").lower()
            if status not in (
                SETTLED_PT_MINDER_STATUSES
                | REFUNDED_PT_MINDER_STATUSES
            ):
                continue
            source_event_id = str(
                transaction.get("source_transaction_id") or ""
            ).strip()
            if not source_event_id or source_event_id in seen:
                errors.append("PT Minder contains a duplicate transaction")
                continue
            try:
                gross_cents = int(
                    (
                        Decimal(str(transaction.get("amount")))
                        * Decimal(100)
                    ).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
                )
            except (InvalidOperation, TypeError, ValueError):
                errors.append(
                    f"{source_event_id or 'transaction'} has no amount"
                )
                continue
            occurred_on = datetime.fromisoformat(
                str(transaction.get("occurred_on"))
            ).date()
            occurred_at = datetime.combine(
                occurred_on,
                time.min,
                tzinfo=BRISBANE_TZ,
            ).astimezone(UTC)
            if occurred_at < cutoff:
                continue
            seen.add(source_event_id)
            events.append(
                {
                    "source_event_id": source_event_id,
                    "occurred_at": occurred_at.isoformat(),
                    "event_type": (
                        "refund"
                        if status in REFUNDED_PT_MINDER_STATUSES
                        else "settled_cash"
                    ),
                    "currency": "AUD",
                    "gross_amount_cents": gross_cents,
                    "gst_amount_cents": gst_from_taxable_gross(gross_cents),
                    "evidence": {
                        "source_snapshot_id": snapshot.get("snapshot_id"),
                        "source_account_id": row.get("source_account_id"),
                        "gst_basis": (
                            "approved_fully_taxable_gst_inclusive_supply"
                        ),
                        "gst_divisor": 11,
                    },
                }
            )

    return {
        "source_system": "pt_minder",
        "source_run_id": f"ptm-cash-{snapshot.get('snapshot_id')}",
        "source_snapshot_id": snapshot.get("snapshot_id"),
        "observed_at": observed_at.isoformat(),
        "complete": not errors,
        "events": events,
        "adapter_summary": {
            "lookback_days": lookback_days,
            "source_records": len(rows),
            "accepted_events": len(events),
            "error_count": len(errors),
            "errors": errors[:20],
        },
    }
