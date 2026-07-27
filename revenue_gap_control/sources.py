from __future__ import annotations

import csv
import json
import sqlite3
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Iterable

from .models import (
    LegacyPaymentEvidence,
    RosterRecord,
    SourceEvidence,
    TimingItem,
)
from .normalise import decimal_value, normalise_email, normalise_phone


HOLD_STATUS_FIELD_ID = "huVhp3xNLYJDtPA9JdFA"


class SourceError(RuntimeError):
    pass


def _cell(row: list[Any], index: dict[str, int], name: str) -> str:
    position = index[name]
    return str(row[position]).strip() if position < len(row) else ""


def _header_index(
    header: list[Any], required: Iterable[str], aliases: dict[str, str] | None = None
) -> dict[str, int]:
    aliases = aliases or {}
    cleaned = [str(item).strip() for item in header]
    result: dict[str, int] = {}
    for canonical in required:
        candidates = [canonical] + [
            raw for raw, target in aliases.items() if target == canonical
        ]
        found = next((name for name in candidates if name in cleaned), None)
        if found is None:
            raise SourceError(f"Workbook is missing required column: {canonical}")
        result[canonical] = cleaned.index(found)
    return result


def parse_active_sgpt(rows: list[list[Any]]) -> list[RosterRecord]:
    if not rows:
        raise SourceError("Active SGPT is empty")
    required = [
        "First Name",
        "Last Name",
        "Phone",
        "Email",
        "Membership Tier",
        "Status",
        "Weekly Debit",
    ]
    index = _header_index(
        rows[0],
        required,
        aliases={"Status ": "Status", "Membership": "Membership Tier"},
    )
    records: list[RosterRecord] = []
    for row_number, row in enumerate(rows[1:], start=2):
        first = _cell(row, index, "First Name")
        last = _cell(row, index, "Last Name")
        email = normalise_email(_cell(row, index, "Email"))
        phone = normalise_phone(_cell(row, index, "Phone"))
        if not first and not last and not email and not phone:
            continue
        raw_debit = _cell(row, index, "Weekly Debit")
        records.append(
            RosterRecord(
                service="SGPT",
                row_number=row_number,
                first_name=first,
                last_name=last,
                email=email,
                phone=phone,
                status=_cell(row, index, "Status"),
                weekly_allocation=decimal_value(raw_debit),
                payment_marker=raw_debit.upper(),
                product=_cell(row, index, "Membership Tier"),
            )
        )
    return records


def parse_active_pt(rows: list[list[Any]]) -> list[RosterRecord]:
    if not rows:
        raise SourceError("Active PT is empty")
    required = [
        "First Name",
        "Last Name",
        "Phone",
        "Email",
        "Personal Trainer",
        "Session Length",
        "Sessions p/wk",
        "Session Cost",
        "Weekly Debit",
        "Notes",
    ]
    index = _header_index(
        rows[0],
        required,
        aliases={
            "$$$": "Session Cost",
            "Rebook": "Notes",
            "Session cost": "Session Cost",
        },
    )
    records: list[RosterRecord] = []
    for row_number, row in enumerate(rows[1:], start=2):
        first = _cell(row, index, "First Name")
        last = _cell(row, index, "Last Name")
        email = normalise_email(_cell(row, index, "Email"))
        phone = normalise_phone(_cell(row, index, "Phone"))
        if not first and not last and not email and not phone:
            continue
        raw_debit = _cell(row, index, "Weekly Debit")
        records.append(
            RosterRecord(
                service="PT",
                row_number=row_number,
                first_name=first,
                last_name=last,
                email=email,
                phone=phone,
                status="Active",
                weekly_allocation=decimal_value(raw_debit),
                payment_marker=raw_debit.upper(),
                product="Fast Track" if "fast track" in _cell(row, index, "Notes").lower() else "PT",
                trainer=_cell(row, index, "Personal Trainer"),
                session_length=_cell(row, index, "Session Length"),
                sessions_per_week=_cell(row, index, "Sessions p/wk"),
                session_cost=decimal_value(_cell(row, index, "Session Cost")),
                notes=_cell(row, index, "Notes"),
            )
        )
    return records


def load_live_roster(
    read_sheet: Callable[[str, str], list[list[Any]]]
) -> list[RosterRecord]:
    sgpt = read_sheet("Active SGPT", "A1:K500")
    pt = read_sheet("Active PT", "A1:K500")
    return parse_active_sgpt(sgpt) + parse_active_pt(pt)


def _serial_date(value: Any) -> date | None:
    if isinstance(value, (int, float)):
        parsed = (datetime(1899, 12, 30) + timedelta(days=int(value))).date()
        return parsed
    text = str(value or "").strip()
    for pattern in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(text, pattern).date()
        except ValueError:
            continue
    return None


def _column_letter(index: int) -> str:
    result = ""
    value = index + 1
    while value:
        value, remainder = divmod(value - 1, 26)
        result = chr(65 + remainder) + result
    return result


def read_kpi_cash(
    read_sheet: Callable[[str, str], list[list[Any]]],
    column_date: date,
) -> tuple[Decimal, str]:
    rows = read_sheet("KPI's The Evolved", "A1:BI106")
    if len(rows) < 106:
        raise SourceError("KPI sheet does not contain cash row 106")
    header = rows[0]
    column = next(
        (
            index
            for index, value in enumerate(header)
            if _serial_date(value) == column_date
        ),
        None,
    )
    if column is None:
        raise SourceError(
            f"KPI column dated {column_date.isoformat()} was not found"
        )
    cash_row = rows[105]
    value = cash_row[column] if column < len(cash_row) else None
    cash = decimal_value(value)
    if cash is None:
        raise SourceError(
            f"KPI {_column_letter(column)}106 has no confirmed cash value"
        )
    return cash, f"KPI {_column_letter(column)}106 dated {column_date.isoformat()}"


def load_roster_csv(path: Path, service: str) -> list[RosterRecord]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.reader(handle))
    return parse_active_sgpt(rows) if service == "SGPT" else parse_active_pt(rows)


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)
    except ValueError:
        return None


def _latest_membership_run(
    connection: sqlite3.Connection,
    max_age_hours: int,
    require_invoices: bool,
) -> sqlite3.Row:
    rows = connection.execute(
        """
        SELECT run_id, started_at, finished_at, counts_json, limitations_json
        FROM runs
        WHERE status='complete'
        ORDER BY started_at DESC
        """
    ).fetchall()
    for row in rows:
        counts = json.loads(row["counts_json"] or "{}")
        required = (
            int(counts.get("ghl_contacts") or 0) > 0
            and int(counts.get("stripe_subscriptions") or 0) > 0
            and int(counts.get("trainerize_active") or 0) > 0
        )
        if require_invoices:
            required = required and int(counts.get("stripe_invoices") or 0) > 0
        if not required:
            continue
        finished = _parse_iso(row["finished_at"])
        if finished and datetime.now(UTC) - finished > timedelta(hours=max_age_hours):
            raise SourceError(
                f"Latest usable membership snapshot is stale: {row['finished_at']}"
            )
        return row
    raise SourceError("No complete membership snapshot contains the required sources")


def _custom_field_value(raw_json: str, field_id: str) -> str:
    try:
        raw = json.loads(raw_json or "{}")
    except json.JSONDecodeError:
        return ""
    fields = raw.get("customFields") or raw.get("customField") or []
    if isinstance(fields, dict):
        value = fields.get(field_id)
        return str(value or "").strip()
    for item in fields:
        if not isinstance(item, dict):
            continue
        if str(item.get("id") or item.get("key") or "") == field_id:
            return str(item.get("value") or item.get("fieldValue") or "").strip()
    return ""


def _contact_phone(raw_json: str) -> str:
    try:
        raw = json.loads(raw_json or "{}")
    except json.JSONDecodeError:
        return ""
    return normalise_phone(raw.get("phone"))


def load_membership_evidence(
    database: Path,
    max_age_hours: int = 48,
    require_invoices: bool = True,
    identity_links_path: Path | None = None,
) -> tuple[dict[str, SourceEvidence], dict[str, str], list[str], str]:
    if not database.exists():
        raise SourceError(f"Membership database not found: {database}")
    connection = sqlite3.connect(database)
    connection.row_factory = sqlite3.Row
    with connection:
        run = _latest_membership_run(connection, max_age_hours, require_invoices)
        run_id = str(run["run_id"])
        limitations = json.loads(run["limitations_json"] or "[]")
        identities = connection.execute(
            "SELECT * FROM identity_register WHERE run_id=?", (run_id,)
        ).fetchall()
        customers = connection.execute(
            "SELECT customer_id, email FROM stripe_customers WHERE run_id=?",
            (run_id,),
        ).fetchall()
        customer_email = {
            str(row["customer_id"]): normalise_email(row["email"])
            for row in customers
            if normalise_email(row["email"])
        }
        subscriptions = connection.execute(
            """
            SELECT customer_id, status, pause_collection_json, current_period_end
            FROM stripe_subscriptions
            WHERE run_id=?
            ORDER BY current_period_end
            """,
            (run_id,),
        ).fetchall()
        invoices = connection.execute(
            """
            SELECT customer_id, status, paid, created_at
            FROM stripe_invoices
            WHERE run_id=?
            ORDER BY created_at
            """,
            (run_id,),
        ).fetchall()
        contacts = connection.execute(
            "SELECT contact_id, raw_json FROM ghl_contacts WHERE run_id=?",
            (run_id,),
        ).fetchall()

    statuses: dict[str, list[str]] = {}
    pauses: dict[str, bool] = {}
    for row in subscriptions:
        email = customer_email.get(str(row["customer_id"]))
        if not email:
            continue
        status = str(row["status"] or "").strip().lower()
        if status:
            statuses.setdefault(email, []).append(status)
        pauses[email] = pauses.get(email, False) or bool(
            str(row["pause_collection_json"] or "").strip()
            not in {"", "null", "None", "{}"}
        )

    latest_invoice: dict[str, sqlite3.Row] = {}
    for row in invoices:
        email = customer_email.get(str(row["customer_id"]))
        if email:
            latest_invoice[email] = row

    contact_raw = {str(row["contact_id"]): str(row["raw_json"]) for row in contacts}
    evidence: dict[str, SourceEvidence] = {}
    contact_to_email: dict[str, str] = {}
    for row in identities:
        email = normalise_email(row["email"])
        if not email:
            continue
        contact_ids = json.loads(row["ghl_contact_ids_json"] or "[]")
        for contact_id in contact_ids:
            contact_to_email[str(contact_id)] = email
        invoice = latest_invoice.get(email)
        hold = next(
            (
                _custom_field_value(contact_raw.get(str(contact_id), ""), HOLD_STATUS_FIELD_ID)
                for contact_id in contact_ids
                if _custom_field_value(
                    contact_raw.get(str(contact_id), ""), HOLD_STATUS_FIELD_ID
                )
            ),
            "",
        )
        trainerize_ids = json.loads(row["trainerize_active_ids_json"] or "[]")
        evidence[email] = SourceEvidence(
            email=email,
            ghl_contact_ids=[str(item) for item in contact_ids],
            stripe_statuses=sorted(set(statuses.get(email, []))),
            latest_invoice_status=str(invoice["status"] or "") if invoice else "",
            latest_invoice_paid=bool(invoice["paid"]) if invoice else False,
            latest_receipt_date=str(invoice["created_at"] or "") if invoice else "",
            pause_collection=pauses.get(email, False),
            trainerize_active=bool(trainerize_ids),
            membership_type=str(row["membership_type"] or ""),
            membership_stage=str(row["membership_stage"] or ""),
            cancellation_status=str(row["cancellation_status"] or ""),
            final_access_date=str(row["final_access_date"] or ""),
            hold_status=hold,
            source_run_id=run_id,
            raw={
                "verified_phones": sorted(
                    {
                        phone
                        for contact_id in contact_ids
                        if (
                            phone := _contact_phone(
                                contact_raw.get(str(contact_id), "")
                            )
                        )
                    }
                )
            },
        )
    if identity_links_path and identity_links_path.exists():
        with identity_links_path.open(newline="", encoding="utf-8-sig") as handle:
            for row in csv.DictReader(handle):
                canonical = normalise_email(row.get("canonical_email"))
                linked = normalise_email(row.get("linked_email"))
                source = evidence.get(canonical) or evidence.get(linked)
                if source is None:
                    continue
                if canonical:
                    evidence.setdefault(canonical, source)
                if linked:
                    evidence.setdefault(linked, source)
    return evidence, contact_to_email, [str(item) for item in limitations], run_id


def apply_verified_phone_fallback(
    roster: list[RosterRecord],
    evidence_by_email: dict[str, SourceEvidence],
) -> None:
    phone_owners: dict[str, set[str]] = {}
    for email, evidence in evidence_by_email.items():
        for phone in evidence.raw.get("verified_phones", []):
            normalised = normalise_phone(phone)
            if normalised:
                phone_owners.setdefault(normalised, set()).add(email)
    for record in roster:
        if not record.email or record.email in evidence_by_email or not record.phone:
            continue
        owners = phone_owners.get(normalise_phone(record.phone), set())
        if len(owners) == 1:
            evidence_by_email[record.email] = evidence_by_email[next(iter(owners))]


BOOKING_AUXILIARY_CATEGORIES = {
    "COMMERCIAL_EVIDENCE_REVIEW_REQUIRED",
    "STRIPE_PREPAID_PAYMENT_REVIEW_REQUIRED",
    "TRAINERIZE_ACCESS_REVIEW_REQUIRED",
    "WORKBOOK_PT_RECORD_MISSING",
    "CROSS_SYSTEM_IDENTITY_REVIEW",
    "CROSS_SYSTEM_SOURCE_UNAVAILABLE",
}


def load_booking_evidence(
    database: Path,
    evidence_by_email: dict[str, SourceEvidence],
    contact_to_email: dict[str, str],
    max_age_hours: int = 192,
) -> tuple[list[str], str]:
    if not database.exists():
        return [f"SOURCE: PT booking snapshot not found: {database}"], ""
    connection = sqlite3.connect(database)
    connection.row_factory = sqlite3.Row
    with connection:
        run = connection.execute(
            """
            SELECT id, completed_at
            FROM audit_runs
            WHERE run_type='full' AND status='completed'
            ORDER BY started_at DESC
            LIMIT 1
            """
        ).fetchone()
        if not run:
            return ["SOURCE: No completed PT booking snapshot exists"], ""
        completed = _parse_iso(run["completed_at"])
        limitations: list[str] = []
        if completed and datetime.now(UTC) - completed > timedelta(hours=max_age_hours):
            limitations.append(
                f"SOURCE: PT booking snapshot is stale: {run['completed_at']}"
            )
        rows = connection.execute(
            "SELECT contact_id, category, payload_json FROM findings WHERE run_id=?",
            (run["id"],),
        ).fetchall()
    for row in rows:
        category = str(row["category"])
        if category in BOOKING_AUXILIARY_CATEGORIES:
            continue
        email = contact_to_email.get(str(row["contact_id"]))
        if not email or email not in evidence_by_email:
            continue
        try:
            payload = json.loads(row["payload_json"])
        except json.JSONDecodeError:
            continue
        item = evidence_by_email[email]
        item.booking_category = category
        item.booked_through = str(payload.get("booked_through") or "")
        item.last_completed = str(payload.get("last_completed") or "")
        item.last_future = str(payload.get("last_future") or "")
        item.has_future_booking = category not in {
            "NO_FUTURE_BOOKINGS",
            "FORMER_PT",
        } and bool(item.last_future or item.booked_through)
        item.raw["booking"] = payload
    return limitations, str(run["id"])


def load_legacy_payment_csv(path: Path | None) -> dict[str, LegacyPaymentEvidence]:
    if path is None or not path.exists():
        return {}
    result: dict[str, LegacyPaymentEvidence] = {}
    with path.open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            email = normalise_email(row.get("email"))
            if not email:
                continue
            result[email] = LegacyPaymentEvidence(
                email=email,
                rail=str(row.get("payment_rail") or row.get("rail") or "").strip(),
                status=str(row.get("status") or "").strip(),
                weekly_amount=decimal_value(row.get("weekly_amount")),
                last_receipt_date=str(row.get("last_receipt_date") or "").strip(),
                next_due_date=str(row.get("next_due_date") or "").strip(),
                notes=str(row.get("notes") or "").strip(),
            )
    return result


def load_approved_account_classifications(
    path: Path | None,
) -> dict[str, LegacyPaymentEvidence]:
    if path is None or not path.exists():
        return {}
    approved_classes = {
        "prepaid_credit_client",
        "external_payment_client",
    }
    result: dict[str, LegacyPaymentEvidence] = {}
    with path.open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            email = normalise_email(row.get("email"))
            classification = str(row.get("classification") or "").strip().lower()
            approved = str(
                row.get("approved_active_without_local_entitlement") or ""
            ).strip().lower() in {"1", "true", "yes"}
            if not email or not approved or classification not in approved_classes:
                continue
            status = (
                "paid_in_advance"
                if classification == "prepaid_credit_client"
                else "collecting"
            )
            result[email] = LegacyPaymentEvidence(
                email=email,
                rail="owner-approved prepaid evidence",
                status=status,
                last_receipt_date=str(row.get("confirmed_date") or "").strip(),
                notes=str(row.get("note") or "").strip(),
            )
    return result


def load_timing_items_csv(path: Path | None) -> list[TimingItem]:
    if path is None or not path.exists():
        return []
    result: list[TimingItem] = []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            amount = decimal_value(row.get("amount"))
            if amount is None:
                continue
            result.append(
                TimingItem(
                    label=str(row.get("label") or "").strip(),
                    amount=amount,
                    email=normalise_email(row.get("email")),
                    category=str(row.get("category") or "").strip(),
                    receipt_date=str(row.get("receipt_date") or "").strip(),
                    service_week=str(row.get("service_week") or "").strip(),
                    owner=str(row.get("owner") or "").strip(),
                    next_action=str(row.get("next_action") or "").strip(),
                    due_date=str(row.get("due_date") or "").strip(),
                )
            )
    return result
