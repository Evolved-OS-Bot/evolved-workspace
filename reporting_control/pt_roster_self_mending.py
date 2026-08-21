from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from typing import Any


EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PT_PRODUCT_PATTERN = re.compile(
    r"\bpt\s*(\d+)\s*m(?:in)?\s*x\s*(\d+)\b",
    re.IGNORECASE,
)
ACTIVE_PT_COLUMNS = (
    "Personal Trainer",
    "Session Length",
    "Sessions p/wk",
    "$$$",
    "Weekly Debit",
)
SALES_COLUMNS = (
    "Product",
    "Trainer Assigned",
    "Cash Taken",
    "Added to Trainerize",
    "Debits Set Up",
)
SALES_LEDGER_START = "2025-10-01"


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    return " ".join(str(value).split())


def _email(value: Any) -> str:
    return str(value or "").strip().lower()


def _money(value: Any) -> Decimal | None:
    text = str(value or "").strip().replace("$", "").replace(",", "")
    if not text:
        return None
    try:
        return Decimal(text)
    except InvalidOperation:
        return None


def _true(value: Any) -> bool:
    return str(value or "").strip().lower() in {
        "1",
        "true",
        "yes",
        "y",
    }


def _date(value: Any) -> str | None:
    if isinstance(value, (int, float)):
        parsed = (
            datetime(1899, 12, 30) + timedelta(days=int(value))
        ).date()
        if date(2020, 1, 1) <= parsed <= date(2035, 1, 1):
            return parsed.isoformat()
    text = str(value or "").strip()
    if not text:
        return None
    if text.isdigit() and 40000 <= int(text) <= 60000:
        return (
            datetime(1899, 12, 30) + timedelta(days=int(text))
        ).date().isoformat()
    for pattern in ("%Y-%m-%d", "%d/%m/%Y", "%d/%m/%y"):
        try:
            return datetime.strptime(text[:10], pattern).date().isoformat()
        except ValueError:
            continue
    return None


def _row_hash(sheet: str, row_number: int, row: dict[str, str]) -> str:
    payload = json.dumps(
        {
            "sheet": sheet,
            "row_number": row_number,
            "row": row,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _records(
    rows: list[list[Any]],
    *,
    sheet: str,
    required: set[str],
) -> list[dict[str, Any]]:
    if not rows:
        raise ValueError(f"{sheet} is empty")
    header = [_text(value) for value in rows[0]]
    aliases = {
        "Session Cost": "$$$",
        "Session cost": "$$$",
        "Sessions per week": "Sessions p/wk",
    }
    canonical_header = [aliases.get(value, value) for value in header]
    missing = required - set(canonical_header)
    if missing:
        raise ValueError(
            f"{sheet} is missing columns: {', '.join(sorted(missing))}"
        )
    records = []
    for row_number, values in enumerate(rows[1:], start=2):
        row = {
            name: _text(values[position]) if position < len(values) else ""
            for position, name in enumerate(canonical_header)
            if name
        }
        if not any(row.values()):
            continue
        records.append(
            {
                "sheet": sheet,
                "row_number": row_number,
                "values": row,
                "precondition_sha256": _row_hash(sheet, row_number, row),
            }
        )
    return records


def _membership_by_email(snapshot: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        _email(row.get("email") or row.get("canonical_key")): row
        for row in snapshot.get("payload", {}).get("rows") or []
        if EMAIL_PATTERN.fullmatch(
            _email(row.get("email") or row.get("canonical_key"))
        )
    }


def _commercial_by_email(
    snapshots: list[dict[str, Any]],
) -> dict[str, dict[str, list[dict[str, Any]]]]:
    result: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(
        lambda: {
            "entitlements": [],
            "payment_accounts": [],
            "payment_events": [],
        }
    )
    for snapshot in snapshots:
        for row in snapshot.get("payload", {}).get("rows") or []:
            email = _email(row.get("email") or row.get("canonical_key"))
            if not EMAIL_PATTERN.fullmatch(email):
                continue
            for field in result[email]:
                result[email][field].extend(row.get(field) or [])
    return result


def _pt_minder_pt_payments_by_email(
    snapshot: dict[str, Any] | None,
) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in (snapshot or {}).get("payload", {}).get("rows") or []:
        email = _email(row.get("email") or row.get("canonical_key"))
        if not EMAIL_PATTERN.fullmatch(email):
            continue
        result[email].extend(
            transaction
            for transaction in row.get("transactions") or []
            if transaction.get("service_type") == "personal_training"
            and transaction.get("status") == "completed"
        )
    return result


def _pt_minder_payment_for_service(
    transactions: list[dict[str, Any]],
    *,
    service_start: str | None,
    as_of: str,
) -> dict[str, Any] | None:
    if not service_start:
        return None
    eligible = [
        transaction
        for transaction in transactions
        if service_start
        <= str(transaction.get("occurred_on") or "")
        <= as_of
    ]
    if not eligible:
        return None
    exact_start = [
        transaction
        for transaction in eligible
        if str(transaction.get("occurred_on") or "") == service_start
    ]
    return max(
        exact_start or eligible,
        key=lambda transaction: (
            str(transaction.get("occurred_on") or ""),
            str(transaction.get("source_transaction_id") or ""),
        ),
    )


def _current_pt_commercial(
    evidence: dict[str, list[dict[str, Any]]],
    as_of: str,
) -> dict[str, Any]:
    entitlements = [
        row
        for row in evidence["entitlements"]
        if row.get("service_type") in {"personal_training", "fast_track"}
        and row.get("status") == "confirmed"
        and (
            not row.get("effective_from")
            or str(row["effective_from"]) <= as_of
        )
        and (
            not row.get("effective_to")
            or str(row["effective_to"]) >= as_of
        )
    ]
    accounts = [
        row
        for row in evidence["payment_accounts"]
        if row.get("status") in {"active", "collecting"}
    ]
    prepaid_pack = any(
        str(row.get("unit") or "").strip().lower() == "prepaid pack"
        and row.get("status") == "confirmed"
        for row in entitlements
    )
    purchased_service_term = any(
        row.get("basis")
        == "revenue_control_governed_purchased_service_term"
        and row.get("status") == "confirmed"
        for row in entitlements
    )
    approved_hold = any(
        row.get("service_type") in {"personal_training", "fast_track"}
        and row.get("status") == "pending"
        and row.get("basis")
        == "revenue_control_assessment:APPROVED_PAUSE"
        for row in evidence["entitlements"]
    )
    events = [
        row
        for row in evidence["payment_events"]
        if row.get("service_type") in {"personal_training", "fast_track"}
        and row.get("status") == "completed"
        and (
            not row.get("coverage_start")
            or str(row["coverage_start"]) <= as_of
        )
        and (
            not row.get("coverage_end")
            or str(row["coverage_end"]) >= as_of
        )
    ]
    latest_event = max(
        events,
        key=lambda row: (
            str(row.get("occurred_on") or ""),
            str(row.get("source_event_id") or ""),
        ),
        default=None,
    )
    weekly_amounts = {
        str(row.get("weekly_amount") or "")
        for row in accounts
        if row.get("weekly_amount") not in (None, "")
    }
    return {
        "confirmed": bool(entitlements),
        "debits_set_up": bool(accounts),
        "prepaid_pack": prepaid_pack,
        "paid_in_advance": prepaid_pack or purchased_service_term,
        "approved_hold": approved_hold,
        "weekly_amount": (
            next(iter(weekly_amounts))
            if len(weekly_amounts) == 1
            else None
        ),
        "cash_taken": (
            str(latest_event.get("amount"))
            if latest_event is not None
            else None
        ),
        "payment_reference": (
            str(latest_event.get("source_event_id"))
            if latest_event is not None
            else None
        ),
        "payment_conflict": len(weekly_amounts) > 1,
    }


def _product_terms(value: Any) -> tuple[str, str] | None:
    match = PT_PRODUCT_PATTERN.search(_text(value))
    if not match:
        return None
    return f"{int(match.group(1))} mins", str(int(match.group(2)))


def _supports_pt_service(value: Any) -> bool:
    product = _text(value).lower()
    return bool(_product_terms(product)) or any(
        label in product
        for label in ("silver", "fast track")
    )


def _proposal(
    *,
    sheet: str,
    row_number: int,
    column: str,
    current: str,
    proposed: str,
    evidence: str,
    precondition_sha256: str,
    evidence_class: str = "authoritative_source",
) -> dict[str, Any]:
    approval_status = (
        "eligible_for_owner_approval"
        if evidence_class == "authoritative_source"
        else "manual_evidence_required"
    )
    return {
        "sheet": sheet,
        "row_number": row_number,
        "column": column,
        "current": current,
        "proposed": proposed,
        "evidence": evidence,
        "evidence_class": evidence_class,
        "approval_status": approval_status,
        "precondition_sha256": precondition_sha256,
        "write_enabled": False,
    }


def _strict_incomplete_repeat(
    rows: list[dict[str, Any]],
    *,
    columns: tuple[str, ...],
) -> dict[str, Any] | None:
    if len(rows) != 2:
        return None
    left, right = rows
    conflicts = [
        column
        for column in columns
        if left["values"].get(column)
        and right["values"].get(column)
        and left["values"][column] != right["values"][column]
    ]
    if conflicts:
        return None
    left_present = {
        column for column in columns if left["values"].get(column)
    }
    right_present = {
        column for column in columns if right["values"].get(column)
    }
    if left_present > right_present:
        preserve, quarantine = left, right
    elif right_present > left_present:
        preserve, quarantine = right, left
    else:
        return None
    return {
        "status": "strict_incomplete_repeat",
        "preserve_row": preserve["row_number"],
        "quarantine_row": quarantine["row_number"],
        "conflicting_columns": [],
        "write_enabled": False,
    }


def build_pt_roster_self_mending_shadow(
    *,
    sales_rows: list[list[Any]],
    active_pt_rows: list[list[Any]],
    membership_snapshot: dict[str, Any],
    commercial_snapshots: list[dict[str, Any]],
    observed_at: str,
    pt_minder_snapshot: dict[str, Any] | None = None,
) -> dict[str, Any]:
    sales = _records(
        sales_rows,
        sheet="Sales",
        required={"Date", "Email", *SALES_COLUMNS},
    )
    active = _records(
        active_pt_rows,
        sheet="Active PT",
        required={"1:1", "Email", *ACTIVE_PT_COLUMNS},
    )
    membership = _membership_by_email(membership_snapshot)
    commercial = _commercial_by_email(commercial_snapshots)
    pt_minder_pt_payments = _pt_minder_pt_payments_by_email(
        pt_minder_snapshot
    )
    as_of = observed_at[:10]

    active_by_email: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in active:
        email = _email(row["values"].get("Email"))
        if email:
            active_by_email[email].append(row)
    sales_by_email: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in sales:
        email = _email(row["values"].get("Email"))
        if email:
            sales_by_email[email].append(row)

    cases = []
    all_emails = sorted(active_by_email)
    for email in all_emails:
        active_matches = active_by_email[email]
        if len(active_matches) != 1:
            service_starts = {
                _date(row["values"].get("1:1"))
                for row in active_matches
            }
            service_start = (
                next(iter(service_starts))
                if len(service_starts) == 1
                else None
            )
            matching_sales = [
                row
                for row in sales_by_email.get(email, [])
                if (
                    service_start
                    and _date(row["values"].get("Date"))
                    == service_start
                )
            ]
            active_analysis = (
                _strict_incomplete_repeat(
                    active_matches,
                    columns=(*ACTIVE_PT_COLUMNS, "Rebook"),
                )
                if service_start
                else None
            )
            sales_analysis = _strict_incomplete_repeat(
                matching_sales,
                columns=SALES_COLUMNS,
            )
            cases.append(
                {
                    "email": email,
                    "service_start": service_start,
                    "state": "exception",
                    "reason": "duplicate_roster_rows",
                    "sales_linkage": "not_evaluated",
                    "active_pt_rows": [
                        row["row_number"] for row in active_matches
                    ],
                    "sales_rows": [
                        row["row_number"] for row in matching_sales
                    ],
                    "duplicate_analysis": {
                        "active_pt": active_analysis,
                        "sales": sales_analysis,
                        "resolution_status": (
                            "dominant_pair_identified"
                            if active_analysis and sales_analysis
                            else "manual_review_required"
                        ),
                        "write_enabled": False,
                    },
                    "proposed_patches": [],
                }
            )
            continue
        active_row = active_matches[0]
        active_values = active_row["values"]
        service_start = _date(active_values.get("1:1"))
        sales_history = sales_by_email.get(email, [])
        sales_matches = [
            row
            for row in sales_history
            if (
                not service_start
                or _date(row["values"].get("Date")) == service_start
            )
        ]
        if not sales_matches:
            if service_start and service_start > as_of:
                cases.append(
                    {
                        "email": email,
                        "service_start": service_start,
                        "state": "future_start",
                        "reason": "service_not_yet_effective",
                        "sales_linkage": "not_due",
                        "active_pt_rows": [active_row["row_number"]],
                        "sales_rows": [
                            row["row_number"] for row in sales_history
                        ],
                        "proposed_patches": [],
                    }
                )
                continue
            pt_sales_history = [
                row
                for row in sales_history
                if _supports_pt_service(row["values"].get("Product"))
            ]
            if pt_sales_history:
                selected_history = max(
                    pt_sales_history,
                    key=lambda row: (
                        _date(row["values"].get("Date")) or "",
                        row["row_number"],
                    ),
                )
                cases.append(
                    {
                        "email": email,
                        "service_start": service_start,
                        "state": "historical_sales_link",
                        "reason": "pt_sales_history_on_different_date",
                        "sales_linkage": "historical_only",
                        "active_pt_rows": [active_row["row_number"]],
                        "sales_rows": [selected_history["row_number"]],
                        "proposed_patches": [],
                    }
                )
                continue
            if (
                not sales_history
                and service_start
                and service_start < SALES_LEDGER_START
            ):
                cases.append(
                    {
                        "email": email,
                        "service_start": service_start,
                        "state": "legacy_sales_history_unavailable",
                        "reason": "service_predates_sales_ledger",
                        "sales_linkage": "legacy_not_expected",
                        "active_pt_rows": [active_row["row_number"]],
                        "sales_rows": [],
                        "proposed_patches": [],
                    }
                )
                continue
            pt_minder_payment = _pt_minder_payment_for_service(
                pt_minder_pt_payments.get(email, []),
                service_start=service_start,
                as_of=as_of,
            )
            if not sales_history and pt_minder_payment:
                cases.append(
                    {
                        "email": email,
                        "service_start": service_start,
                        "state": "pt_minder_payment_link",
                        "reason": "pt_minder_payment_without_sales_row",
                        "sales_linkage": "payment_evidence_only",
                        "active_pt_rows": [active_row["row_number"]],
                        "sales_rows": [],
                        "payment_evidence": {
                            "source": "pt_minder",
                            "transaction_id": pt_minder_payment.get(
                                "source_transaction_id"
                            ),
                            "occurred_on": pt_minder_payment.get(
                                "occurred_on"
                            ),
                            "amount": pt_minder_payment.get("amount"),
                        },
                        "proposed_patches": [],
                    }
                )
                continue
            sales_linkage = (
                "historical_only" if sales_history else "absent"
            )
            cases.append(
                {
                    "email": email,
                    "service_start": service_start,
                    "state": "exception",
                    "reason": (
                        "missing_current_sales_row_with_history"
                        if sales_history
                        else "missing_sales_history"
                    ),
                    "sales_linkage": sales_linkage,
                    "active_pt_rows": [active_row["row_number"]],
                    "sales_rows": [
                        row["row_number"] for row in sales_history
                    ],
                    "proposed_patches": [],
                }
            )
            continue
        if len(sales_matches) > 1:
            cases.append(
                {
                    "email": email,
                    "service_start": service_start,
                    "state": "exception",
                    "reason": "duplicate_roster_rows",
                    "sales_linkage": "duplicate_exact",
                    "active_pt_rows": [active_row["row_number"]],
                    "sales_rows": [
                        row["row_number"] for row in sales_matches
                    ],
                    "proposed_patches": [],
                }
            )
            continue

        sales_row = sales_matches[0]
        sales_values = sales_row["values"]
        member = membership.get(email)
        if not member:
            state = "exception"
            reason = "identity_ambiguous"
            patches: list[dict[str, Any]] = []
        elif (
            member.get("lifecycle_status") != "active"
            or (
                member.get("final_access_date")
                and str(member["final_access_date"]) < as_of
            )
        ):
            state = "exception"
            reason = "cancelled_or_final_access_ended"
            patches = []
        else:
            payment = _current_pt_commercial(
                commercial.get(email, {
                    "entitlements": [],
                    "payment_accounts": [],
                    "payment_events": [],
                }),
                as_of,
            )
            if payment["payment_conflict"]:
                state = "exception"
                reason = "payment_terms_conflict"
                patches = []
            else:
                patches = []
                active_terms = (
                    _text(active_values.get("Session Length")),
                    _text(active_values.get("Sessions p/wk")),
                )
                sales_terms = _product_terms(sales_values.get("Product"))

                if not sales_values.get("Product") and all(active_terms):
                    minutes = re.search(r"\d+", active_terms[0])
                    if minutes:
                        patches.append(
                            _proposal(
                                sheet="Sales",
                                row_number=sales_row["row_number"],
                                column="Product",
                                current="",
                                proposed=(
                                    f"PT {minutes.group()}M x "
                                    f"{active_terms[1]}"
                                ),
                                evidence=(
                                    "Matching Active PT structured terms"
                                ),
                                precondition_sha256=sales_row[
                                    "precondition_sha256"
                                ],
                                evidence_class="supporting_projection",
                            )
                        )
                ghl_trainer = _text(member.get("pt_block_trainer"))
                if not sales_values.get("Trainer Assigned") and ghl_trainer:
                    patches.append(
                        _proposal(
                            sheet="Sales",
                            row_number=sales_row["row_number"],
                            column="Trainer Assigned",
                            current="",
                            proposed=ghl_trainer,
                            evidence="GHL PT Block Trainer",
                            precondition_sha256=sales_row[
                                "precondition_sha256"
                            ],
                        )
                    )
                elif (
                    not sales_values.get("Trainer Assigned")
                    and active_values.get("Personal Trainer")
                ):
                    patches.append(
                        _proposal(
                            sheet="Sales",
                            row_number=sales_row["row_number"],
                            column="Trainer Assigned",
                            current="",
                            proposed=active_values["Personal Trainer"],
                            evidence="Matching Active PT trainer",
                            precondition_sha256=sales_row[
                                "precondition_sha256"
                            ],
                            evidence_class="supporting_projection",
                        )
                    )
                if (
                    not sales_values.get("Cash Taken")
                    and payment["cash_taken"]
                ):
                    patches.append(
                        _proposal(
                            sheet="Sales",
                            row_number=sales_row["row_number"],
                            column="Cash Taken",
                            current="",
                            proposed=f"${Decimal(payment['cash_taken']):.2f}",
                            evidence=(
                                "Current completed payment event "
                                f"{payment['payment_reference']}"
                            ),
                            precondition_sha256=sales_row[
                                "precondition_sha256"
                            ],
                        )
                    )
                if (
                    not _true(sales_values.get("Added to Trainerize"))
                    and member.get("trainerize_active")
                ):
                    patches.append(
                        _proposal(
                            sheet="Sales",
                            row_number=sales_row["row_number"],
                            column="Added to Trainerize",
                            current=sales_values.get(
                                "Added to Trainerize", ""
                            ),
                            proposed="TRUE",
                            evidence="Accepted Trainerize active identity",
                            precondition_sha256=sales_row[
                                "precondition_sha256"
                            ],
                        )
                    )
                if (
                    not _true(sales_values.get("Debits Set Up"))
                    and payment["debits_set_up"]
                ):
                    patches.append(
                        _proposal(
                            sheet="Sales",
                            row_number=sales_row["row_number"],
                            column="Debits Set Up",
                            current=sales_values.get("Debits Set Up", ""),
                            proposed="TRUE",
                            evidence="Accepted collecting payment account",
                            precondition_sha256=sales_row[
                                "precondition_sha256"
                            ],
                        )
                    )
                if (
                    not active_values.get("Personal Trainer")
                    and sales_values.get("Trainer Assigned")
                ):
                    patches.append(
                        _proposal(
                            sheet="Active PT",
                            row_number=active_row["row_number"],
                            column="Personal Trainer",
                            current="",
                            proposed=sales_values["Trainer Assigned"],
                            evidence="Matching Sales trainer assignment",
                            precondition_sha256=active_row[
                                "precondition_sha256"
                            ],
                            evidence_class="supporting_projection",
                        )
                    )
                if sales_terms:
                    for column, proposed in zip(
                        ("Session Length", "Sessions p/wk"),
                        sales_terms,
                    ):
                        if not active_values.get(column):
                            patches.append(
                                _proposal(
                                    sheet="Active PT",
                                    row_number=active_row["row_number"],
                                    column=column,
                                    current="",
                                    proposed=proposed,
                                    evidence="Matching structured Sales product",
                                    precondition_sha256=active_row[
                                        "precondition_sha256"
                                    ],
                                    evidence_class=(
                                        "supporting_projection"
                                    ),
                                )
                            )
                weekly = _money(payment["weekly_amount"])
                sessions = _money(
                    active_values.get("Sessions p/wk")
                    or (sales_terms[1] if sales_terms else "")
                )
                if (
                    not active_values.get("Weekly Debit")
                    and weekly is not None
                ):
                    patches.append(
                        _proposal(
                            sheet="Active PT",
                            row_number=active_row["row_number"],
                            column="Weekly Debit",
                            current="",
                            proposed=f"${weekly:.2f}",
                            evidence="Accepted collecting payment account",
                            precondition_sha256=active_row[
                                "precondition_sha256"
                            ],
                        )
                    )
                if (
                    not active_values.get("$$$")
                    and weekly is not None
                    and sessions
                    and sessions > 0
                ):
                    patches.append(
                        _proposal(
                            sheet="Active PT",
                            row_number=active_row["row_number"],
                            column="$$$",
                            current="",
                            proposed=f"${weekly / sessions:.2f}",
                            evidence=(
                                "Accepted weekly debit divided by structured "
                                "sessions per week"
                            ),
                            precondition_sha256=active_row[
                                "precondition_sha256"
                            ],
                        )
                    )

                required_active_columns = (
                    (
                        "Personal Trainer",
                        "Session Length",
                        "Weekly Debit",
                    )
                    if payment["prepaid_pack"]
                    else ACTIVE_PT_COLUMNS
                )
                missing_terms = [
                    column
                    for column in required_active_columns
                    if not active_values.get(column)
                    and not any(
                        patch["sheet"] == "Active PT"
                        and patch["column"] == column
                        for patch in patches
                    )
                ]
                missing_terms.extend(
                    column
                    for column in ("Product", "Trainer Assigned")
                    if not sales_values.get(column)
                    and not any(
                        patch["sheet"] == "Sales"
                        and patch["column"] == column
                        for patch in patches
                    )
                )
                if missing_terms:
                    state = "pending_terms"
                    reason = "missing_agreement_terms"
                elif payment["approved_hold"]:
                    state = "approved_hold"
                    reason = "approved_payment_hold"
                elif not payment["confirmed"]:
                    state = "pending_provisioning"
                    reason = "missing_payment_evidence"
                elif not member.get("trainerize_active"):
                    state = "pending_provisioning"
                    reason = "trainerize_not_provisioned"
                elif (
                    not sales_values.get("Cash Taken")
                    and not any(
                        patch["sheet"] == "Sales"
                        and patch["column"] == "Cash Taken"
                        for patch in patches
                    )
                ):
                    state = "pending_provisioning"
                    reason = "missing_payment_evidence"
                elif (
                    not _true(sales_values.get("Added to Trainerize"))
                    and not any(
                        patch["sheet"] == "Sales"
                        and patch["column"] == "Added to Trainerize"
                        for patch in patches
                    )
                ):
                    state = "pending_provisioning"
                    reason = "trainerize_not_provisioned"
                elif (
                    not payment["paid_in_advance"]
                    and not _true(sales_values.get("Debits Set Up"))
                    and not any(
                        patch["sheet"] == "Sales"
                        and patch["column"] == "Debits Set Up"
                        for patch in patches
                    )
                ):
                    state = "pending_provisioning"
                    reason = "missing_payment_evidence"
                elif patches:
                    state = "pending_terms"
                    reason = "worksheet_projection_incomplete"
                else:
                    state = "confirmed_current_pt"
                    reason = "complete"

        cases.append(
            {
                "email": email,
                "service_start": service_start,
                "state": state,
                "reason": reason,
                "sales_linkage": "exact",
                "active_pt_rows": [active_row["row_number"]],
                "sales_rows": [sales_row["row_number"]],
                "proposed_patches": patches,
            }
        )

    for case in cases:
        matching_active = active_by_email.get(case["email"], [])
        values = matching_active[0]["values"] if matching_active else {}
        case["client_name"] = " ".join(
            str(values.get(column) or "").strip()
            for column in ("First Name", "Last Name")
            if str(values.get(column) or "").strip()
        )

    state_counts = Counter(case["state"] for case in cases)
    reason_counts = Counter(case["reason"] for case in cases)
    sales_linkage_counts = Counter(
        case["sales_linkage"] for case in cases
    )
    proposal_count = sum(
        len(case["proposed_patches"]) for case in cases
    )
    proposal_approval_counts = Counter(
        patch["approval_status"]
        for case in cases
        for patch in case["proposed_patches"]
    )
    return {
        "schema_version": 7,
        "status": "complete",
        "mode": "read_only_shadow",
        "observed_at": observed_at,
        "source_snapshot_ids": {
            "membership_reconciliation": membership_snapshot.get(
                "snapshot_id"
            ),
            "commercial_evidence": [
                snapshot.get("snapshot_id")
                for snapshot in commercial_snapshots
            ],
            "pt_minder": (pt_minder_snapshot or {}).get("snapshot_id"),
        },
        "summary": {
            "active_pt_rows": len(active),
            "cases": len(cases),
            "confirmed_current_pt": state_counts[
                "confirmed_current_pt"
            ],
            "pending_terms": state_counts["pending_terms"],
            "pending_provisioning": state_counts[
                "pending_provisioning"
            ],
            "approved_holds": state_counts["approved_hold"],
            "exceptions": state_counts["exception"],
            "proposed_patches": proposal_count,
            "proposals_eligible_for_owner_approval": (
                proposal_approval_counts["eligible_for_owner_approval"]
            ),
            "proposals_requiring_manual_evidence": (
                proposal_approval_counts["manual_evidence_required"]
            ),
            "reason_counts": dict(sorted(reason_counts.items())),
            "sales_linkage_counts": dict(
                sorted(sales_linkage_counts.items())
            ),
            "exact_sales_links": sales_linkage_counts["exact"],
            "historical_sales_links": sales_linkage_counts[
                "historical_only"
            ],
            "legacy_sales_history_unavailable": state_counts[
                "legacy_sales_history_unavailable"
            ],
            "future_starts": state_counts["future_start"],
            "pt_minder_payment_links": state_counts[
                "pt_minder_payment_link"
            ],
            "absent_sales_history": sales_linkage_counts["absent"],
            "duplicate_active_identities": sum(
                case["reason"] == "duplicate_roster_rows"
                and len(case["active_pt_rows"]) > 1
                for case in cases
            ),
            "duplicate_dominant_pairs_identified": sum(
                case.get("duplicate_analysis", {}).get(
                    "resolution_status"
                )
                == "dominant_pair_identified"
                for case in cases
            ),
            "writes_enabled": False,
            "row_deletions_proposed": 0,
            "row_creations_proposed": 0,
        },
        "cases": cases,
    }
