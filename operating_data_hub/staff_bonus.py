from __future__ import annotations

import csv
import io
import re
from datetime import UTC, date, datetime, time
from typing import Any, Iterable

from .config import BRISBANE_TZ


PREQUAL_BONUS_CENTS = 1_000
SALE_BONUS_CENTS = 6_000
PACKAGE_PRODUCTS = {
    "bronze": {"product": "Bronze", "package_price_cents": 39_900},
    "silver": {"product": "Silver", "package_price_cents": 59_900},
}
HUMAN_NAMES = {
    "peter": "Peter Brown",
    "peter brown": "Peter Brown",
    "megan": "Megan Brown",
    "megan brown": "Megan Brown",
    "nora": "Nora Silva",
    "nora silva": "Nora Silva",
    "piper": "Piper Mae",
    "piper mae": "Piper Mae",
    "katrina": "Katrina Parsons",
    "katrina parsons": "Katrina Parsons",
    "leisa": "Leisa Smith",
    "leisa smith": "Leisa Smith",
    "jo": "Jo McDonald",
    "jo mcdonald": "Jo McDonald",
}
OWNER_EXCLUSIONS = {"Peter Brown"}
REQUIRED_SALES_HEADERS = {
    "Date",
    "First Name",
    "Last Name",
    "Mobile",
    "Email",
    "Product",
    "Salesperson",
}


def _normalise_email(value: Any) -> str:
    return str(value or "").strip().lower()


def _normalise_phone(value: Any) -> str:
    digits = re.sub(r"\D", "", str(value or ""))
    return digits[-9:] if len(digits) >= 9 else digits


def _normalise_name(value: Any) -> str:
    return " ".join(str(value or "").lower().split())


def _parse_sheet_date(value: Any) -> date | None:
    text = str(value or "").strip()
    for pattern in ("%d/%m/%Y", "%Y-%m-%d", "%d/%m/%y"):
        try:
            return datetime.strptime(text, pattern).date()
        except ValueError:
            continue
    return None


def _brisbane_noon(day: date) -> datetime:
    return datetime.combine(day, time(hour=12), tzinfo=BRISBANE_TZ)


def _identity_indexes(
    contacts: Iterable[dict[str, Any]],
) -> tuple[dict[str, set[str]], dict[str, set[str]], dict[str, set[str]]]:
    emails: dict[str, set[str]] = {}
    phones: dict[str, set[str]] = {}
    names: dict[str, set[str]] = {}
    for contact in contacts:
        contact_id = str(contact.get("id") or "").strip()
        if not contact_id:
            continue
        email = _normalise_email(contact.get("email"))
        phone = _normalise_phone(contact.get("phone"))
        name = _normalise_name(
            contact.get("name")
            or " ".join(
                part
                for part in (
                    str(contact.get("firstName") or "").strip(),
                    str(contact.get("lastName") or "").strip(),
                )
                if part
            )
        )
        if email:
            emails.setdefault(email, set()).add(contact_id)
        if phone:
            phones.setdefault(phone, set()).add(contact_id)
        if name:
            names.setdefault(name, set()).add(contact_id)
    return emails, phones, names


def _resolve_contact_id(
    *,
    email: str,
    phone: str,
    customer_name: str,
    indexes: tuple[dict[str, set[str]], dict[str, set[str]], dict[str, set[str]]],
) -> tuple[str | None, str | None]:
    emails, phones, names = indexes
    evidence_sets = []
    if email and email in emails:
        evidence_sets.append(emails[email])
    if phone and phone in phones:
        evidence_sets.append(phones[phone])
    normalised_name = _normalise_name(customer_name)
    if normalised_name and normalised_name in names:
        evidence_sets.append(names[normalised_name])
    if not evidence_sets:
        return None, "sales_contact_unresolved"
    candidates = set.intersection(*evidence_sets)
    if len(candidates) == 1:
        return next(iter(candidates)), None
    return None, "sales_contact_ambiguous"


def normalise_sales_sheet(
    rows: list[list[Any]],
    *,
    contacts: Iterable[dict[str, Any]],
    attendance_rows: Iterable[dict[str, Any]],
    observed_at: datetime,
) -> dict[str, Any]:
    if not rows:
        raise ValueError("Sales tab is empty")
    headers = [str(value or "").strip() for value in rows[0]]
    missing = REQUIRED_SALES_HEADERS - set(headers)
    if missing:
        raise ValueError("Sales tab missing headers: " + ", ".join(sorted(missing)))
    columns = {name: headers.index(name) for name in REQUIRED_SALES_HEADERS}
    indexes = _identity_indexes(contacts)
    showed_by_contact_day: dict[tuple[str, date], list[dict[str, Any]]] = {}
    for attendance in attendance_rows:
        status = str(
            attendance.get("canonical_status") or attendance.get("status") or ""
        ).strip().lower()
        contact_id = str(attendance.get("contact_id") or "").strip()
        start_at = str(attendance.get("start_at") or "").strip()
        if status != "showed" or not contact_id or not start_at:
            continue
        try:
            start = datetime.fromisoformat(start_at.replace("Z", "+00:00"))
        except ValueError:
            continue
        showed_by_contact_day.setdefault(
            (contact_id, start.astimezone(BRISBANE_TZ).date()), []
        ).append(attendance)

    events: list[dict[str, Any]] = []
    unallocated_reviews: list[dict[str, Any]] = []
    for row_number, values in enumerate(rows[1:], start=2):
        def cell(name: str) -> str:
            index = columns[name]
            return str(values[index] if index < len(values) else "").strip()

        if not any(str(value or "").strip() for value in values):
            continue
        sale_day = _parse_sheet_date(cell("Date"))
        product_raw = " ".join(cell("Product").split())
        product_key = product_raw.lower()
        package = PACKAGE_PRODUCTS.get(product_key)
        customer_name = " ".join(
            value for value in (cell("First Name"), cell("Last Name")) if value
        ).strip()
        seller_raw = " ".join(cell("Salesperson").split())
        sold_by = HUMAN_NAMES.get(seller_raw.lower())
        base = {
            "source_event_id": f"staff-bonus-sales-row:{row_number}",
            "source_object_id": str(row_number),
            "sheet": "Sales",
            "sheet_row": row_number,
            "customer_name": customer_name or "Unnamed customer",
            "product_raw": product_raw,
            "sold_by_raw": seller_raw or None,
        }
        if sale_day is None:
            if package:
                unallocated_reviews.append(
                    {**base, "state": "review", "issue_codes": ["sale_date_invalid"]}
                )
            continue
        occurred_at = _brisbane_noon(sale_day).astimezone(UTC)
        if not package:
            events.append(
                {
                    **base,
                    "occurred_at": occurred_at.isoformat(),
                    "sale_date": sale_day.isoformat(),
                    "state": "excluded",
                    "issue_codes": [
                        "personal_training_sale_excluded"
                        if product_key.startswith("pt")
                        else "package_not_399_or_599"
                    ],
                }
            )
            continue

        email = _normalise_email(cell("Email"))
        phone = _normalise_phone(cell("Mobile"))
        contact_id, identity_issue = _resolve_contact_id(
            email=email,
            phone=phone,
            customer_name=customer_name,
            indexes=indexes,
        )
        issue_codes: list[str] = []
        if not sold_by:
            issue_codes.append("salesperson_unrecognised")
        if identity_issue:
            issue_codes.append(identity_issue)
        assessments = (
            showed_by_contact_day.get((contact_id, sale_day), []) if contact_id else []
        )
        series_ids = {
            str(row.get("appointment_series_id") or row.get("appointment_id") or "")
            for row in assessments
        }
        series_ids.discard("")
        if contact_id and not assessments:
            issue_codes.append("no_showed_assessment_same_day")
        elif len(series_ids) > 1:
            issue_codes.append("multiple_showed_assessments_same_day")
        selected = assessments[0] if len(series_ids) == 1 else None
        events.append(
            {
                **base,
                "occurred_at": occurred_at.isoformat(),
                "sale_date": sale_day.isoformat(),
                "state": "review" if issue_codes else "accepted",
                "issue_codes": issue_codes,
                "contact_id": contact_id,
                "sold_by": sold_by,
                "product": package["product"],
                "package_price_cents": package["package_price_cents"],
                "assessment_appointment_id": (
                    str(selected.get("appointment_id") or "") if selected else None
                ),
                "appointment_series_id": (
                    next(iter(series_ids)) if len(series_ids) == 1 else None
                ),
                "attribution_rule": "showed Strength Assessment on sale date",
            }
        )

    duplicate_groups: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for event in events:
        if event.get("product") and event.get("sale_date"):
            identity = str(event.get("contact_id") or event.get("customer_name") or "")
            duplicate_groups.setdefault(
                (identity, str(event["sale_date"]), str(event["product"])), []
            ).append(event)
    for group in duplicate_groups.values():
        if len(group) < 2:
            continue
        for event in group:
            if "duplicate_sales_rows" not in event["issue_codes"]:
                event["issue_codes"].append("duplicate_sales_rows")
            event["state"] = "review"

    return {
        "schema_version": 1,
        "source": "staff_bonus_sales_sheet",
        "observed_at": observed_at.isoformat(),
        "complete": True,
        "events": events,
        "unallocated_reviews": unallocated_reviews,
        "summary": {
            "record_count": len(events) + len(unallocated_reviews),
            "accepted": sum(row["state"] == "accepted" for row in events),
            "review": sum(row["state"] == "review" for row in events)
            + len(unallocated_reviews),
            "excluded": sum(row["state"] == "excluded" for row in events),
        },
    }


def validate_eligibility(payload: dict[str, Any]) -> dict[str, Any]:
    staff_name = HUMAN_NAMES.get(_normalise_name(payload.get("staff_name")))
    if not staff_name:
        raise ValueError("staff_name is not a recognised human staff name")
    if staff_name in OWNER_EXCLUSIONS:
        raise ValueError("Peter Brown is excluded from staff bonuses")
    try:
        effective_from = date.fromisoformat(str(payload.get("effective_from") or ""))
    except ValueError as exc:
        raise ValueError("effective_from must be YYYY-MM-DD") from exc
    effective_to_raw = str(payload.get("effective_to") or "").strip()
    try:
        effective_to = date.fromisoformat(effective_to_raw) if effective_to_raw else None
    except ValueError as exc:
        raise ValueError("effective_to must be YYYY-MM-DD") from exc
    if effective_to and effective_to < effective_from:
        raise ValueError("effective_to cannot precede effective_from")
    agreement_reference = str(payload.get("agreement_reference") or "").strip()
    if not agreement_reference:
        raise ValueError("agreement_reference is required")
    approved_by = " ".join(str(payload.get("approved_by") or "").split())
    if approved_by != "Peter Brown":
        raise ValueError("approved_by must be Peter Brown")
    return {
        "staff_name": staff_name,
        "effective_from": effective_from.isoformat(),
        "effective_to": effective_to.isoformat() if effective_to else None,
        "agreement_reference": agreement_reference,
        "approved_by": approved_by,
        "state": "eligible",
    }


def _eligibility_state(
    staff_name: str | None,
    event_day: date,
    eligibility_by_staff: dict[str, dict[str, Any]],
) -> str:
    if not staff_name:
        return "staff_unresolved"
    if staff_name in OWNER_EXCLUSIONS:
        return "owner_excluded"
    record = eligibility_by_staff.get(staff_name)
    if not record:
        return "agreement_not_recorded"
    start = date.fromisoformat(record["effective_from"])
    end = date.fromisoformat(record["effective_to"]) if record.get("effective_to") else None
    return "eligible" if start <= event_day and (end is None or event_day <= end) else "agreement_not_effective"


def build_monthly_bonus_report(
    month: str,
    *,
    prequalification_events: Iterable[dict[str, Any]],
    prequalification_reviews: Iterable[dict[str, Any]],
    sale_events: Iterable[dict[str, Any]],
    sale_unallocated_reviews: Iterable[dict[str, Any]],
    eligibility_records: Iterable[dict[str, Any]],
    generated_at: datetime,
    source_status: dict[str, Any],
) -> dict[str, Any]:
    if not re.fullmatch(r"\d{4}-\d{2}", month):
        raise ValueError("month must be YYYY-MM")
    try:
        date.fromisoformat(month + "-01")
    except ValueError as exc:
        raise ValueError("month must be a valid YYYY-MM") from exc
    eligibility_by_staff = {
        str(row.get("staff_name")): row for row in eligibility_records
    }
    lines: list[dict[str, Any]] = []
    review_queue = list(prequalification_reviews) + list(sale_unallocated_reviews)

    for event in prequalification_events:
        occurred = datetime.fromisoformat(str(event["occurred_at"]).replace("Z", "+00:00"))
        local_day = occurred.astimezone(BRISBANE_TZ).date()
        if local_day.strftime("%Y-%m") != month:
            continue
        staff_name = str(event.get("completed_by") or "").strip() or None
        policy = _eligibility_state(staff_name, local_day, eligibility_by_staff)
        lines.append(
            {
                "bonus_month": month,
                "staff_member": staff_name,
                "customer_name": event.get("contact_name"),
                "category": "prequalification",
                "governed_event_id": event.get("source_event_id"),
                "event_version_id": event.get("event_version_id"),
                "event_time": occurred.isoformat(),
                "evidence_status": "accepted",
                "policy_eligibility": policy,
                "unit_amount_cents": PREQUAL_BONUS_CENTS,
                "payable_amount_cents": PREQUAL_BONUS_CENTS if policy == "eligible" else 0,
                "review_reason": None,
            }
        )

    for event in sale_events:
        if event.get("state") == "excluded":
            continue
        sale_day = date.fromisoformat(str(event["sale_date"]))
        if sale_day.strftime("%Y-%m") != month:
            continue
        staff_name = str(event.get("sold_by") or "").strip() or None
        policy = _eligibility_state(staff_name, sale_day, eligibility_by_staff)
        evidence_status = str(event.get("state") or "review")
        issue_codes = list(event.get("issue_codes") or [])
        payable = (
            SALE_BONUS_CENTS
            if evidence_status == "accepted" and policy == "eligible"
            else 0
        )
        lines.append(
            {
                "bonus_month": month,
                "staff_member": staff_name or event.get("sold_by_raw"),
                "customer_name": event.get("customer_name"),
                "category": "sale",
                "product": event.get("product"),
                "governed_event_id": event.get("source_event_id"),
                "event_version_id": event.get("event_version_id"),
                "event_time": event.get("occurred_at"),
                "evidence_status": evidence_status,
                "policy_eligibility": policy,
                "unit_amount_cents": SALE_BONUS_CENTS,
                "payable_amount_cents": payable,
                "review_reason": ", ".join(issue_codes) if issue_codes else None,
            }
        )

    staff_summary: dict[str, dict[str, Any]] = {}
    for line in lines:
        staff = str(line.get("staff_member") or "Unresolved")
        summary = staff_summary.setdefault(
            staff,
            {
                "staff_member": staff,
                "prequalification_count": 0,
                "sales_count": 0,
                "prequalification_evidence_count": 0,
                "sales_evidence_count": 0,
                "review_count": 0,
                "policy_excluded_count": 0,
                "payable_amount_cents": 0,
            },
        )
        if line["evidence_status"] != "accepted":
            summary["review_count"] += 1
        else:
            evidence_key = (
                "prequalification_evidence_count"
                if line["category"] == "prequalification"
                else "sales_evidence_count"
            )
            summary[evidence_key] += 1
            if int(line["payable_amount_cents"]) > 0:
                payable_key = (
                    "prequalification_count"
                    if line["category"] == "prequalification"
                    else "sales_count"
                )
                summary[payable_key] += 1
            elif line["policy_eligibility"] != "eligible":
                summary["policy_excluded_count"] += 1
        summary["payable_amount_cents"] += int(line["payable_amount_cents"])

    return {
        "schema_version": 1,
        "report_id": "monthly-staff-bonus",
        "month": month,
        "timezone": "Australia/Brisbane",
        "generated_at": generated_at.astimezone(UTC).isoformat(),
        "source_status": source_status,
        "available": all(bool(value.get("available")) for value in source_status.values()),
        "lines": sorted(
            lines,
            key=lambda row: (
                str(row.get("staff_member") or ""),
                str(row.get("category") or ""),
                str(row.get("event_time") or ""),
            ),
        ),
        "review_queue": review_queue,
        "staff_summary": sorted(staff_summary.values(), key=lambda row: row["staff_member"]),
        "totals": {
            "prequalification_lines": sum(row["category"] == "prequalification" for row in lines),
            "sales_lines": sum(row["category"] == "sale" for row in lines),
            "review_lines": sum(row["evidence_status"] != "accepted" for row in lines)
            + len(review_queue),
            "payable_amount_cents": sum(int(row["payable_amount_cents"]) for row in lines),
        },
    }


def bonus_report_csv(report: dict[str, Any]) -> str:
    columns = [
        "bonus_month",
        "staff_member",
        "customer_name",
        "category",
        "product",
        "governed_event_id",
        "event_version_id",
        "event_time",
        "evidence_status",
        "policy_eligibility",
        "unit_amount_cents",
        "payable_amount_cents",
        "review_reason",
    ]
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=columns, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(report.get("lines") or [])
    return output.getvalue()
