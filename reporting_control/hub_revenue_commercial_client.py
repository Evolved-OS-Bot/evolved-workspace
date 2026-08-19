from __future__ import annotations

import csv
import json
import os
import re
import sqlite3
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import requests


EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
CURRENT_SUBSCRIPTION_STATUSES = {"active", "trialing"}
CURRENT_LEGACY_STATUSES = {"collecting", "active", "paid"}
SERVICE_TYPES = {
    "SGPT": "sgpt",
    "PT": "personal_training",
}
PREPAID_CLASSIFICATIONS = {
    "ACTIVE_PIA",
    "PIF_PACK_IN_DELIVERY",
    "PACK_RENEWAL_DUE",
}
PURCHASED_TERM_STATES = {"approved", "revoked"}


def _normalise_email(value: Any) -> str:
    return str(value or "").strip().lower()


def _json_list(value: Any) -> list[Any]:
    try:
        parsed = json.loads(str(value or "[]"))
    except json.JSONDecodeError:
        return []
    return parsed if isinstance(parsed, list) else []


def _load_aliases(path: Path | None) -> dict[str, str]:
    aliases: dict[str, str] = {}
    if path is None or not path.exists():
        return aliases
    with path.open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            canonical = _normalise_email(row.get("canonical_email"))
            linked = _normalise_email(row.get("linked_email"))
            if canonical and linked:
                aliases[canonical] = canonical
                aliases[linked] = canonical
    return aliases


def _load_current_legacy_receipts(
    path: Path | None,
    *,
    as_of: date,
) -> dict[str, str]:
    current: dict[str, str] = {}
    if path is None or not path.exists():
        return current
    with path.open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            email = _normalise_email(row.get("email"))
            status = str(row.get("status") or "").strip().lower()
            receipt = str(row.get("last_receipt_date") or "").strip()[:10]
            try:
                age = (as_of - date.fromisoformat(receipt)).days
            except ValueError:
                continue
            if (
                EMAIL_PATTERN.fullmatch(email)
                and status in CURRENT_LEGACY_STATUSES
                and 0 <= age <= 14
            ):
                current[email] = receipt
    return current


def _load_current_approved_external_receipts(
    path: Path | None,
    *,
    as_of: date,
) -> dict[str, str]:
    current: dict[str, str] = {}
    if path is None or not path.exists():
        return current
    with path.open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            email = _normalise_email(row.get("email"))
            classification = str(
                row.get("classification") or ""
            ).strip().lower()
            approved = str(
                row.get("approved_active_without_local_entitlement") or ""
            ).strip().lower() in {"1", "true", "yes"}
            confirmed = str(row.get("confirmed_date") or "").strip()[:10]
            try:
                age = (as_of - date.fromisoformat(confirmed)).days
            except ValueError:
                continue
            if (
                EMAIL_PATTERN.fullmatch(email)
                and approved
                and classification == "external_payment_client"
                and 0 <= age <= 14
            ):
                current[email] = confirmed
    return current


def _load_approved_prepaid_entitlements(
    *,
    legacy_path: Path | None,
    classifications_path: Path | None,
) -> dict[str, str]:
    approved: dict[str, str] = {}
    if legacy_path is not None and legacy_path.exists():
        with legacy_path.open(
            newline="",
            encoding="utf-8-sig",
        ) as handle:
            for row in csv.DictReader(handle):
                email = _normalise_email(row.get("email"))
                status = str(row.get("status") or "").strip().lower()
                if (
                    EMAIL_PATTERN.fullmatch(email)
                    and status in {"paid_in_advance", "pif"}
                ):
                    approved[email] = (
                        "revenue_control_approved_prepaid_ledger"
                    )
    if (
        classifications_path is not None
        and classifications_path.exists()
    ):
        with classifications_path.open(
            newline="",
            encoding="utf-8-sig",
        ) as handle:
            for row in csv.DictReader(handle):
                email = _normalise_email(row.get("email"))
                classification = str(
                    row.get("classification") or ""
                ).strip().lower()
                is_approved = str(
                    row.get(
                        "approved_active_without_local_entitlement"
                    )
                    or ""
                ).strip().lower() in {"1", "true", "yes"}
                if (
                    EMAIL_PATTERN.fullmatch(email)
                    and is_approved
                    and classification == "prepaid_credit_client"
                ):
                    approved[email] = (
                        "revenue_control_owner_approved_prepaid_credit"
                    )
    return approved


def _load_purchased_service_terms(
    path: Path | None,
    *,
    aliases: dict[str, str],
) -> list[dict[str, Any]]:
    if path is None or not path.exists():
        return []
    terms: list[dict[str, Any]] = []
    seen: set[str] = set()
    with path.open(newline="", encoding="utf-8-sig") as handle:
        for position, row in enumerate(csv.DictReader(handle), start=2):
            term_id = str(row.get("term_id") or "").strip()
            invoice_id = str(row.get("stripe_invoice_id") or "").strip()
            additional_invoice_ids = [
                value.strip()
                for value in re.split(
                    r"[;,]",
                    str(
                        row.get("additional_stripe_invoice_ids") or ""
                    ),
                )
                if value.strip()
            ]
            purchaser = _normalise_email(row.get("purchaser_email"))
            beneficiary = _normalise_email(row.get("beneficiary_email"))
            beneficiary = aliases.get(beneficiary, beneficiary)
            service = str(row.get("service_type") or "").strip().lower()
            state = str(row.get("state") or "").strip().lower()
            effective_from = _iso_sheet_date(row.get("effective_from"))
            effective_to = _iso_sheet_date(row.get("effective_to"))
            approved_by = " ".join(
                str(row.get("approved_by") or "").split()
            )
            approved_on = _iso_sheet_date(row.get("approved_on"))
            if (
                not term_id
                or term_id in seen
                or not invoice_id.startswith("in_")
                or any(
                    not value.startswith("in_")
                    for value in additional_invoice_ids
                )
                or len(
                    {invoice_id, *additional_invoice_ids}
                ) != 1 + len(additional_invoice_ids)
                or not EMAIL_PATTERN.fullmatch(purchaser)
                or not EMAIL_PATTERN.fullmatch(beneficiary)
                or service not in set(SERVICE_TYPES.values())
                or state not in PURCHASED_TERM_STATES
                or not effective_from
                or not effective_to
                or effective_from > effective_to
                or not approved_by
                or not approved_on
            ):
                raise RuntimeError(
                    "Purchased-service-term register contains an invalid "
                    f"record at row {position}"
                )
            seen.add(term_id)
            quantity = str(row.get("quantity") or "").strip() or None
            unit = " ".join(str(row.get("unit") or "").split()) or None
            terms.append(
                {
                    "term_id": term_id,
                    "stripe_invoice_id": invoice_id,
                    "additional_stripe_invoice_ids": additional_invoice_ids,
                    "purchaser_email": purchaser,
                    "beneficiary_email": beneficiary,
                    "service_type": service,
                    "quantity": quantity,
                    "unit": unit,
                    "state": state,
                    "effective_from": effective_from,
                    "effective_to": effective_to,
                    "approved_by": approved_by,
                    "approved_on": approved_on,
                }
            )
    return terms


def _direct_receipt(row: sqlite3.Row | None) -> str | None:
    if row is None:
        return None
    statuses = {
        str(value or "").strip().lower()
        for value in _json_list(row["stripe_statuses_json"])
    }
    if (
        statuses & CURRENT_SUBSCRIPTION_STATUSES
        and bool(row["latest_invoice_paid"])
        and str(row["latest_invoice_status"] or "").strip().lower()
        == "paid"
        and not bool(row["pause_collection"])
    ):
        receipt = str(row["latest_receipt_date"] or "").strip()[:10]
        return receipt or None
    return None


def _has_current_contract(row: sqlite3.Row | None) -> bool:
    if row is None or bool(row["pause_collection"]):
        return False
    statuses = {
        str(value or "").strip().lower()
        for value in _json_list(row["stripe_statuses_json"])
    }
    return bool(statuses & CURRENT_SUBSCRIPTION_STATUSES)


def _pending_assessment(
    *,
    classification: str,
    service: str,
    payment: sqlite3.Row | None,
    booking: sqlite3.Row | None,
) -> str:
    if classification != "BOOKING_PAYMENT_UNRESOLVED":
        return classification
    if (
        service == "personal_training"
        and booking is not None
        and bool(booking["has_future_booking"])
    ):
        return "PAYMENT_UNRESOLVED_WITH_FUTURE_BOOKING"
    if _has_current_contract(payment):
        return "ACTIVE_CONTRACT_RECEIPT_UNRESOLVED"
    return "NO_CURRENT_PAYMENT_EVIDENCE"


def _iso_sheet_date(value: Any) -> str | None:
    text = str(value or "").strip()
    for pattern in ("%Y-%m-%d", "%d/%m/%Y", "%d/%m/%y"):
        try:
            return datetime.strptime(text, pattern).date().isoformat()
        except ValueError:
            continue
    try:
        serial = float(text)
    except ValueError:
        return None
    if not serial.is_integer():
        return None
    converted = (datetime(1899, 12, 30) + timedelta(days=int(serial))).date()
    if date(2020, 1, 1) <= converted <= date(2035, 1, 1):
        return converted.isoformat()
    return None


def build_revenue_commercial_evidence(
    database: Path,
    *,
    run_id: str | None = None,
    identity_links_path: Path | None = None,
    legacy_evidence_path: Path | None = None,
    account_classifications_path: Path | None = None,
    purchased_service_terms_path: Path | None = None,
) -> dict[str, Any]:
    connection = sqlite3.connect(database)
    connection.row_factory = sqlite3.Row
    if run_id:
        run = connection.execute(
            """
            SELECT * FROM runs
            WHERE run_id=? AND status='complete'
            """,
            (run_id,),
        ).fetchone()
    else:
        run = connection.execute(
            """
            SELECT * FROM runs
            WHERE status='complete'
            ORDER BY completed_at DESC LIMIT 1
            """
        ).fetchone()
    if not run:
        connection.close()
        raise RuntimeError("No completed revenue-control audit exists")

    limitations = [
        str(value)
        for value in _json_list(run["limitations_json"])
    ]
    if any(
        value.startswith("SOURCE:")
        or "invoice completeness was not required" in value.lower()
        for value in limitations
    ):
        connection.close()
        raise RuntimeError(
            "Revenue-control audit has source limitations and cannot "
            "promote commercial evidence"
        )

    selected_run = str(run["run_id"])
    roster = connection.execute(
        """
        SELECT * FROM roster_snapshot
        WHERE run_id=?
        ORDER BY lower(trim(email)), service, source_row
        """,
        (selected_run,),
    ).fetchall()
    payments = {
        _normalise_email(row["email"]): row
        for row in connection.execute(
            "SELECT * FROM payment_evidence WHERE run_id=?",
            (selected_run,),
        ).fetchall()
    }
    bookings = {
        _normalise_email(row["email"]): row
        for row in connection.execute(
            "SELECT * FROM booking_evidence WHERE run_id=?",
            (selected_run,),
        ).fetchall()
    }
    connection.close()

    as_of = date.fromisoformat(str(run["window_end"]))
    aliases = _load_aliases(identity_links_path)
    legacy = _load_current_legacy_receipts(
        legacy_evidence_path,
        as_of=as_of,
    )
    approved_external = _load_current_approved_external_receipts(
        account_classifications_path,
        as_of=as_of,
    )
    approved_prepaid = _load_approved_prepaid_entitlements(
        legacy_path=legacy_evidence_path,
        classifications_path=account_classifications_path,
    )
    purchased_terms = _load_purchased_service_terms(
        purchased_service_terms_path,
        aliases=aliases,
    )

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    seen_services: set[tuple[str, str]] = set()
    for row in roster:
        raw_email = _normalise_email(row["email"])
        canonical = aliases.get(raw_email, raw_email)
        service = SERVICE_TYPES.get(str(row["service"] or "").strip().upper())
        if not EMAIL_PATTERN.fullmatch(canonical) or service is None:
            raise RuntimeError(
                "CLEAN_COLLECTING row lacks an exact governed identity "
                "or service type"
            )
        key = (canonical, service)
        if key in seen_services:
            existing = next(
                item
                for item in grouped[canonical]
                if item["service_type"] == service
            )
            existing.update(
                {
                    "status": "pending",
                    "effective_from": None,
                    "basis": (
                        "revenue_control_assessment:"
                        "DUPLICATE_ROSTER_SERVICE"
                    ),
                }
            )
            continue
        seen_services.add(key)

        classification = str(row["classification"] or "").strip().upper()
        receipt = None
        if classification in PREPAID_CLASSIFICATIONS:
            basis = (
                approved_prepaid.get(raw_email)
                or approved_prepaid.get(canonical)
            )
            if basis:
                receipt = str(run["window_start"])
                status = "confirmed"
            else:
                renewal_date = _iso_sheet_date(row["renewal_date"])
                if (
                    service == "sgpt"
                    and str(row["payment_marker"] or "").strip().upper()
                    in {"PIF", "PIA"}
                    and renewal_date is not None
                    and renewal_date >= str(run["window_end"])
                ):
                    basis = (
                        "revenue_control_governed_pif_roster_"
                        "through_renewal"
                    )
                    receipt = str(run["window_start"])
                    status = "confirmed"
                else:
                    basis = (
                        f"revenue_control_assessment:{classification}"
                    )
                    status = "pending"
        elif classification == "CLEAN_COLLECTING":
            receipt = _direct_receipt(
                payments.get(raw_email) or payments.get(canonical)
            )
            if receipt:
                basis = "revenue_control_current_stripe_receipt"
            else:
                receipt = legacy.get(raw_email) or legacy.get(canonical)
                basis = "revenue_control_current_approved_legacy_receipt"
            if not receipt:
                receipt = (
                    approved_external.get(raw_email)
                    or approved_external.get(canonical)
                )
                basis = (
                    "revenue_control_current_approved_external_receipt"
                )
            if not receipt:
                raise RuntimeError(
                    "CLEAN_COLLECTING row lacks current underlying receipt "
                    f"evidence: {canonical} {service}"
                )
            status = "confirmed"
        else:
            assessment = _pending_assessment(
                classification=classification,
                service=service,
                payment=payments.get(raw_email) or payments.get(canonical),
                booking=bookings.get(raw_email) or bookings.get(canonical),
            )
            basis = f"revenue_control_assessment:{assessment}"
            status = "pending"

        grouped[canonical].append(
            {
                "source_record_id": (
                    f"{selected_run}:{row['service']}:{row['source_row']}"
                ),
                "service_type": service,
                "status": status,
                "effective_from": receipt,
                "effective_to": (
                    (
                        _iso_sheet_date(row["renewal_date"])
                        or str(run["window_end"])
                    )
                    if (
                        classification in PREPAID_CLASSIFICATIONS
                        and status == "confirmed"
                    )
                    else None
                ),
                "basis": basis,
            }
        )

    for term in purchased_terms:
        canonical = str(term["beneficiary_email"])
        grouped[canonical].append(
            {
                "source_record_id": (
                    f"purchased-service-term:{term['term_id']}"
                ),
                "service_type": term["service_type"],
                "quantity": term["quantity"],
                "unit": term["unit"],
                "status": (
                    "confirmed"
                    if term["state"] == "approved"
                    else "not_entitled"
                ),
                "effective_from": term["effective_from"],
                "effective_to": term["effective_to"],
                "basis": (
                    "revenue_control_governed_purchased_service_term"
                ),
                "payment_reference": ";".join(
                    [
                        term["stripe_invoice_id"],
                        *term["additional_stripe_invoice_ids"],
                    ]
                ),
            }
        )

    observed_at = (
        str(run["completed_at"] or "").strip()
        or datetime.now().astimezone().isoformat()
    )
    return {
        "schema_version": 1,
        "source_system": "revenue_control",
        "source_run_id": selected_run,
        "observed_at": observed_at,
        "rows": [
            {
                "canonical_key": canonical,
                "email": canonical,
                "source_identity_ids": [],
                "entitlements": entitlements,
                "payment_accounts": [],
                "payment_events": [],
            }
            for canonical, entitlements in sorted(grouped.items())
        ],
    }


def publish_revenue_commercial_evidence(
    database: Path,
    *,
    run_id: str | None = None,
    identity_links_path: Path | None = None,
    legacy_evidence_path: Path | None = None,
    account_classifications_path: Path | None = None,
    purchased_service_terms_path: Path | None = None,
    timeout: int = 120,
) -> dict[str, Any]:
    base_url = os.getenv("HUB_INGEST_BASE_URL", "").rstrip("/")
    secret = os.getenv("HUB_WEBHOOK_SECRET", "")
    if not base_url or not secret:
        return {"status": "not_configured"}
    payload = build_revenue_commercial_evidence(
        database,
        run_id=run_id,
        identity_links_path=identity_links_path,
        legacy_evidence_path=legacy_evidence_path,
        account_classifications_path=account_classifications_path,
        purchased_service_terms_path=purchased_service_terms_path,
    )
    response = requests.post(
        f"{base_url}/commercial-evidence",
        headers={"X-Hub-Secret": secret},
        json=payload,
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()
