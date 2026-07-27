#!/usr/bin/env python3
"""Read-only GHL, Stripe and Trainerize membership reconciliation.

Identified source snapshots and exception details are written only below
data/private/integration-reporting/. Aggregate, non-identifying summaries are
written below outputs/trainerize-reporting-reconciliation/.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sqlite3
from collections import defaultdict
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

try:
    from .trainerize_client import TrainerizeClient
except ImportError:  # Direct script execution.
    from trainerize_client import TrainerizeClient


ROOT = Path(__file__).resolve().parents[1]
PRIVATE_DIR = ROOT / "data" / "private" / "integration-reporting"
PUBLIC_DIR = ROOT / "outputs" / "trainerize-reporting-reconciliation"
DATABASE = PRIVATE_DIR / "reconciliation.sqlite"
IDENTITY_LINKS_FILE = PRIVATE_DIR / "identity_links.csv"
IDENTITY_RECORD_LINKS_FILE = PRIVATE_DIR / "identity_record_links.csv"
ACCOUNT_CLASSIFICATIONS_FILE = PRIVATE_DIR / "account_classifications.csv"
AUTHORITATIVE_STRIPE_CUSTOMERS_FILE = (
    PRIVATE_DIR / "authoritative_stripe_customers.csv"
)
ENV_FILE = ROOT / "scripts" / ".env"

GHL_BASE_URL = "https://services.leadconnectorhq.com"
STRIPE_BASE_URL = "https://api.stripe.com/v1"
MEMBERSHIP_PIPELINE_ID = "fkEvrFkTihYkdb3bpprd"

MEMBERSHIP_STAGES = {
    "22019d21-0efd-4604-9a5c-030b57495c8d": "Hold: Escalated",  # defensive only
    "22019d21-0efd-4604-9a83-5608c0776735": "Online Only",
    "edaf6054-486a-473d-be37-e5f9bcde0dd9": "Fit & Flexible",
    "81aab141-2d01-4cdb-9d25-ee949f36098b": "Strong, Fit & Flexible Membership",
    "a1e8d561-91ec-4d95-a8ea-98ea2e129142": "Fast Track",
    "27bf02d9-74fd-4ee2-a1e0-b515b76fba79": "Gold (legacy)",
    "58247f13-4a47-40f8-8289-35d62fc138b3": "PT Only",
    "9ce28fb1-f43b-472a-ac11-1b4c147b202b": "PT 1 p.wk",
    "01d615da-4bd4-4bf3-a5c6-54332588367d": "PT 2 p.wk",
    "edf7f617-e058-438a-978a-330fa262ef8e": "PT 3 p.wk",
}

GHL_FIELDS = {
    "membership_type": "1SgYibtlIuophn9FYAh8",
    "cancellation_status": "vqTZezcOELXVjVLRTiCR",
    "cancellation_type": "VhxR2hI4B1GfvcZJiD9j",
    "final_access_date": "3mZzBYcUk7ZAvB9Fs7lH",
    "notice_end_date": "8Thl9yA4A7kwkbF8QL1Z",
}

STRIPE_ENTITLED_STATUSES = {"active", "trialing", "past_due", "unpaid"}
STRIPE_ENDED_STATUSES = {"canceled", "incomplete_expired"}
GHL_ENDED_MEMBER_TAGS = {"old member", "oldmember"}
GHL_ENDED_PT_TAGS = {"old pt client"}
GHL_TERMINATED_TAGS = {"terminated"}
PT_MEMBERSHIP_STAGE_IDS = {
    stage_id
    for stage_id, stage_name in MEMBERSHIP_STAGES.items()
    if stage_name.startswith("PT ")
}

SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}


SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS runs (
    run_id TEXT PRIMARY KEY,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    status TEXT NOT NULL,
    counts_json TEXT,
    limitations_json TEXT
);

CREATE TABLE IF NOT EXISTS ghl_contacts (
    run_id TEXT NOT NULL,
    contact_id TEXT NOT NULL,
    email TEXT,
    first_name TEXT,
    last_name TEXT,
    assigned_to TEXT,
    tags_json TEXT NOT NULL,
    membership_type TEXT,
    cancellation_status TEXT,
    cancellation_type TEXT,
    notice_end_date TEXT,
    final_access_date TEXT,
    date_added TEXT,
    date_updated TEXT,
    raw_json TEXT NOT NULL,
    PRIMARY KEY (run_id, contact_id)
);

CREATE TABLE IF NOT EXISTS ghl_opportunities (
    run_id TEXT NOT NULL,
    opportunity_id TEXT NOT NULL,
    contact_id TEXT,
    pipeline_id TEXT,
    stage_id TEXT,
    stage_name TEXT,
    status TEXT,
    updated_at TEXT,
    raw_json TEXT NOT NULL,
    PRIMARY KEY (run_id, opportunity_id)
);

CREATE TABLE IF NOT EXISTS stripe_customers (
    run_id TEXT NOT NULL,
    customer_id TEXT NOT NULL,
    email TEXT,
    name TEXT,
    delinquent INTEGER NOT NULL,
    created_at TEXT,
    raw_json TEXT NOT NULL,
    PRIMARY KEY (run_id, customer_id)
);

CREATE TABLE IF NOT EXISTS stripe_subscriptions (
    run_id TEXT NOT NULL,
    subscription_id TEXT NOT NULL,
    customer_id TEXT,
    status TEXT,
    current_period_start TEXT,
    current_period_end TEXT,
    cancel_at TEXT,
    cancel_at_period_end INTEGER NOT NULL,
    canceled_at TEXT,
    pause_collection_json TEXT,
    product_ids_json TEXT,
    price_ids_json TEXT,
    raw_json TEXT NOT NULL,
    PRIMARY KEY (run_id, subscription_id)
);

CREATE TABLE IF NOT EXISTS stripe_invoices (
    run_id TEXT NOT NULL,
    invoice_id TEXT NOT NULL,
    customer_id TEXT,
    subscription_id TEXT,
    status TEXT,
    paid INTEGER NOT NULL,
    amount_due INTEGER,
    amount_paid INTEGER,
    period_end TEXT,
    created_at TEXT,
    raw_json TEXT NOT NULL,
    PRIMARY KEY (run_id, invoice_id)
);

CREATE TABLE IF NOT EXISTS trainerize_clients (
    run_id TEXT NOT NULL,
    trainerize_user_id INTEGER NOT NULL,
    email TEXT,
    first_name TEXT,
    last_name TEXT,
    roster_view TEXT NOT NULL,
    source_status TEXT,
    client_type TEXT,
    role TEXT,
    trainer_id INTEGER,
    latest_signed_in TEXT,
    raw_json TEXT NOT NULL,
    PRIMARY KEY (run_id, trainerize_user_id, roster_view)
);

CREATE TABLE IF NOT EXISTS identity_register (
    run_id TEXT NOT NULL,
    identity_key TEXT NOT NULL,
    email TEXT,
    ghl_contact_ids_json TEXT NOT NULL,
    stripe_customer_ids_json TEXT NOT NULL,
    stripe_subscription_ids_json TEXT NOT NULL,
    trainerize_active_ids_json TEXT NOT NULL,
    trainerize_deactivated_ids_json TEXT NOT NULL,
    ghl_active_signal INTEGER NOT NULL,
    stripe_entitled_signal INTEGER NOT NULL,
    trainerize_active_signal INTEGER NOT NULL,
    membership_type TEXT,
    membership_stage TEXT,
    cancellation_status TEXT,
    final_access_date TEXT,
    stripe_statuses_json TEXT NOT NULL,
    latest_invoice_status TEXT,
    evidence_json TEXT NOT NULL,
    PRIMARY KEY (run_id, identity_key)
);

CREATE TABLE IF NOT EXISTS exceptions (
    run_id TEXT NOT NULL,
    exception_id TEXT NOT NULL,
    identity_key TEXT NOT NULL,
    email TEXT,
    severity TEXT NOT NULL,
    exception_type TEXT NOT NULL,
    summary TEXT NOT NULL,
    evidence_json TEXT NOT NULL,
    recommended_action TEXT NOT NULL,
    owner TEXT NOT NULL,
    auto_action_allowed INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (run_id, exception_id)
);
"""


def load_env(path: Path = ENV_FILE) -> dict[str, str]:
    values = dict(os.environ)
    if path.exists():
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            values.setdefault(key.strip(), value.strip().strip('"').strip("'"))
    return values


def utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def normalise_email(value: Any) -> str:
    return str(value or "").strip().lower()


def load_identity_links(path: Path = IDENTITY_LINKS_FILE) -> dict[str, str]:
    """Load owner-confirmed email links without attempting fuzzy matching."""
    links: dict[str, str] = {}
    if not path.exists():
        return links
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            canonical = normalise_email(row.get("canonical_email"))
            linked = normalise_email(row.get("linked_email"))
            if not canonical or not linked:
                continue
            links[canonical] = canonical
            links[linked] = canonical
    return links


def load_identity_record_links(
    path: Path = IDENTITY_RECORD_LINKS_FILE,
) -> dict[tuple[str, str], str]:
    """Load owner-confirmed source-record links for records without an email."""
    links: dict[tuple[str, str], str] = {}
    if not path.exists():
        return links
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            canonical = normalise_email(row.get("canonical_email"))
            source = normalise_text(row.get("source"))
            source_id = str(row.get("source_id") or "").strip()
            if canonical and source and source_id:
                links[(source, source_id)] = canonical
    return links


def load_account_classifications(
    path: Path = ACCOUNT_CLASSIFICATIONS_FILE,
) -> dict[str, dict[str, Any]]:
    """Load owner-approved account categories and explicit access exemptions."""
    classifications: dict[str, dict[str, Any]] = {}
    if not path.exists():
        return classifications
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            email = normalise_email(row.get("email"))
            if not email:
                continue
            classifications[email] = {
                "classification": normalise_text(row.get("classification")),
                "approved_active_without_local_entitlement": normalise_text(
                    row.get("approved_active_without_local_entitlement")
                )
                in {"true", "yes", "1"},
            }
    return classifications


def load_authoritative_stripe_customers(
    path: Path = AUTHORITATIVE_STRIPE_CUSTOMERS_FILE,
) -> dict[str, str]:
    """Load reviewed email-to-Stripe-customer decisions without deleting history."""
    authoritative: dict[str, str] = {}
    if not path.exists():
        return authoritative
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            email = normalise_email(row.get("email"))
            customer_id = str(row.get("authoritative_customer_id") or "").strip()
            if email and customer_id:
                authoritative[email] = customer_id
    return authoritative


def canonicalise_control_keys(
    controls: dict[str, Any],
    identity_links: dict[str, str],
) -> dict[str, Any]:
    """Apply confirmed email aliases to owner-approved control registers."""
    return {
        identity_links.get(normalise_email(key), normalise_email(key)): value
        for key, value in controls.items()
        if normalise_email(key)
    }


def normalise_text(value: Any) -> str:
    return " ".join(str(value or "").strip().lower().split())


def as_iso_timestamp(value: Any) -> str | None:
    if value in (None, ""):
        return None
    try:
        return datetime.fromtimestamp(int(value), tz=UTC).isoformat(timespec="seconds")
    except (TypeError, ValueError, OSError):
        return str(value)


def parse_iso_date(value: Any) -> date | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        return None


def custom_field_map(contact: dict[str, Any]) -> dict[str, Any]:
    def normalise_value(value: Any) -> Any:
        if isinstance(value, list):
            cleaned = [str(item).strip() for item in value if str(item).strip()]
            return ", ".join(cleaned)
        if isinstance(value, dict):
            return json_text(value)
        return value

    return {
        str(item.get("id")): normalise_value(item.get("value"))
        for item in contact.get("customFields") or []
        if isinstance(item, dict) and item.get("id")
    }


def json_text(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def open_database(path: Path = DATABASE) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    os.chmod(path.parent, 0o700)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.executescript(SCHEMA)
    connection.commit()
    os.chmod(path, 0o600)
    return connection


class GHLReader:
    def __init__(self, api_key: str, location_id: str, timeout: int = 60) -> None:
        self.location_id = location_id
        self.timeout = timeout
        self.session = requests.Session()
        self.session.mount(
            "https://",
            HTTPAdapter(
                max_retries=Retry(
                    total=3,
                    connect=3,
                    read=3,
                    status=3,
                    backoff_factor=1,
                    # GHL intermittently returns 400 for a cursor that succeeds
                    # unchanged moments later, so cursor reads are retried here.
                    status_forcelist=(400, 429, 500, 502, 503, 504),
                    # POST /contacts/search is a read-only, idempotent query.
                    allowed_methods=frozenset({"GET", "POST"}),
                    raise_on_status=False,
                )
            ),
        )
        self.session.headers.update(
            {
                "Authorization": f"Bearer {api_key}",
                "Version": "2021-07-28",
                "Accept": "application/json",
            }
        )

    def _paginate(self, path: str, params: dict[str, Any], list_key: str) -> list[dict[str, Any]]:
        first_url = f"{GHL_BASE_URL}{path}"
        for snapshot_attempt in range(3):
            url = first_url
            rows: list[dict[str, Any]] = []
            seen_urls: set[str] = set()
            request_params: dict[str, Any] | None = params
            while url and url not in seen_urls:
                seen_urls.add(url)
                response = self.session.get(
                    url, params=request_params, timeout=self.timeout
                )
                if (
                    response.status_code == 400
                    and request_params is None
                    and snapshot_attempt < 2
                ):
                    # GHL cursors can become invalid if contacts change mid-snapshot.
                    # Discard the partial result and restart from a fresh first page.
                    break
                response.raise_for_status()
                payload = response.json()
                batch = payload.get(list_key) or []
                rows.extend(item for item in batch if isinstance(item, dict))
                next_url = (payload.get("meta") or {}).get("nextPageUrl")
                if not next_url:
                    return rows
                url = urljoin(GHL_BASE_URL, str(next_url))
                request_params = None
            else:
                return rows
        raise RuntimeError(
            f"GHL pagination remained unstable after 3 complete snapshot attempts: {path}"
        )

    def contacts(self) -> list[dict[str, Any]]:
        """Return a complete contact snapshot through the supported search API.

        HighLevel's former GET /contacts/ endpoint is deprecated and its
        startAfter cursor can expire during a full account scan. The supported
        search endpoint uses numbered pages. We still reject and restart a
        snapshot if the reported total changes, a page is empty too early, or a
        contact ID appears twice because the result order moved mid-read.
        """
        endpoint = f"{GHL_BASE_URL}/contacts/search"
        page_limit = 100
        max_snapshot_attempts = 3

        for snapshot_attempt in range(max_snapshot_attempts):
            rows: list[dict[str, Any]] = []
            seen_ids: set[str] = set()
            expected_total: int | None = None
            page = 1
            unstable = False

            while True:
                response = self.session.post(
                    endpoint,
                    json={
                        "locationId": self.location_id,
                        "page": page,
                        "pageLimit": page_limit,
                    },
                    timeout=self.timeout,
                )
                response.raise_for_status()
                payload = response.json()
                batch = [
                    item
                    for item in payload.get("contacts") or []
                    if isinstance(item, dict)
                ]
                reported_total = int(payload.get("total") or 0)

                if expected_total is None:
                    expected_total = reported_total
                elif reported_total != expected_total:
                    unstable = True
                    break

                if not batch:
                    if len(rows) == expected_total:
                        return rows
                    unstable = True
                    break

                batch_ids = [str(item.get("id") or "") for item in batch]
                if (
                    any(not contact_id for contact_id in batch_ids)
                    or len(set(batch_ids)) != len(batch_ids)
                    or seen_ids.intersection(batch_ids)
                ):
                    unstable = True
                    break

                rows.extend(batch)
                seen_ids.update(batch_ids)

                if len(rows) == expected_total:
                    return rows
                if len(rows) > expected_total or len(batch) < page_limit:
                    unstable = True
                    break
                page += 1

            if not unstable:
                return rows
            if snapshot_attempt + 1 == max_snapshot_attempts:
                break

        raise RuntimeError(
            "GHL contact search remained unstable after "
            f"{max_snapshot_attempts} complete snapshot attempts"
        )

    def opportunities(self) -> list[dict[str, Any]]:
        return self._paginate(
            "/opportunities/search",
            {"location_id": self.location_id, "limit": 100},
            "opportunities",
        )


class StripeReader:
    def __init__(self, restricted_key: str, timeout: int = 30) -> None:
        self.timeout = timeout
        self.session = requests.Session()
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
        self.session.auth = (restricted_key, "")

    def collection(
        self, resource: str, params: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        query = {"limit": 100, **(params or {})}
        while True:
            response = self.session.get(
                f"{STRIPE_BASE_URL}/{resource}",
                params=query,
                timeout=self.timeout,
            )
            response.raise_for_status()
            payload = response.json()
            batch = payload.get("data") or []
            rows.extend(item for item in batch if isinstance(item, dict))
            if not payload.get("has_more") or not batch:
                return rows
            query["starting_after"] = batch[-1]["id"]


def fetch_trainerize_view(client: TrainerizeClient, view: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    start = 0
    while True:
        page = client.get_client_list(
            view=view, start=start, count=100, verbose=True
        )
        batch = page.get("users") or []
        rows.extend(item for item in batch if isinstance(item, dict))
        total = int(page.get("total") or 0)
        if not batch or start + len(batch) >= total:
            return rows
        start += len(batch)


def latest_membership_opportunities(
    opportunities: Iterable[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    for opportunity in opportunities:
        if opportunity.get("pipelineId") != MEMBERSHIP_PIPELINE_ID:
            continue
        contact_id = str(opportunity.get("contactId") or "")
        if not contact_id:
            continue
        candidate_key = str(opportunity.get("updatedAt") or opportunity.get("createdAt") or "")
        current_key = str(
            (latest.get(contact_id) or {}).get("updatedAt")
            or (latest.get(contact_id) or {}).get("createdAt")
            or ""
        )
        if contact_id not in latest or candidate_key >= current_key:
            latest[contact_id] = opportunity
    return latest


def is_ghl_active(contact: dict[str, Any], opportunity: dict[str, Any] | None) -> bool:
    tags = {normalise_text(tag) for tag in contact.get("tags") or []}
    cancellation_status = normalise_text(
        custom_field_map(contact).get(GHL_FIELDS["cancellation_status"])
    )
    if cancellation_status == "cancelled" or tags & GHL_TERMINATED_TAGS:
        return False
    member_tag = "member" in tags and not tags & GHL_ENDED_MEMBER_TAGS
    live_stage = False
    if (
        opportunity
        and opportunity.get("pipelineStageId") in MEMBERSHIP_STAGES
        and normalise_text(opportunity.get("status")) in {"open", "won"}
    ):
        stage_id = str(opportunity.get("pipelineStageId") or "")
        if stage_id in PT_MEMBERSHIP_STAGE_IDS:
            live_stage = not bool(tags & GHL_ENDED_PT_TAGS)
        else:
            live_stage = not bool(tags & GHL_ENDED_MEMBER_TAGS)
    return member_tag or live_stage


def is_stripe_entitled(subscription: dict[str, Any]) -> bool:
    # Stripe keeps a subscription's status as `active` while invoice collection is
    # paused. Those subscriptions are contractual records, not current service
    # entitlement. The hold workflow resumes billing and access together.
    return (
        normalise_text(subscription.get("status")) in STRIPE_ENTITLED_STATUSES
        and not bool(subscription.get("pause_collection"))
    )


def build_identity_records(
    contacts: list[dict[str, Any]],
    opportunities: list[dict[str, Any]],
    customers: list[dict[str, Any]],
    subscriptions: list[dict[str, Any]],
    invoices: list[dict[str, Any]],
    trainerize_active: list[dict[str, Any]],
    trainerize_deactivated: list[dict[str, Any]],
    identity_links: dict[str, str] | None = None,
    identity_record_links: dict[tuple[str, str], str] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    identity_links = identity_links or {}
    identity_record_links = identity_record_links or {}
    contacts_by_email: dict[str, list[dict[str, Any]]] = defaultdict(list)
    customers_by_email: dict[str, list[dict[str, Any]]] = defaultdict(list)
    active_tz_by_email: dict[str, list[dict[str, Any]]] = defaultdict(list)
    deactivated_tz_by_email: dict[str, list[dict[str, Any]]] = defaultdict(list)
    subscriptions_by_customer: dict[str, list[dict[str, Any]]] = defaultdict(list)
    invoices_by_customer: dict[str, list[dict[str, Any]]] = defaultdict(list)
    missing_email: list[dict[str, Any]] = []

    def add_email(
        mapping: dict[str, list[dict[str, Any]]],
        row: dict[str, Any],
        *,
        source: str,
        id_field: str,
    ) -> None:
        source_email = normalise_email(row.get("email"))
        email = identity_links.get(source_email, source_email)
        if not email:
            email = identity_record_links.get(
                (normalise_text(source), str(row.get(id_field) or ""))
            )
        if email:
            mapping[email].append(row)
        else:
            missing_email.append(
                {
                    "source": source,
                    "source_id": row.get(id_field),
                    "record": row,
                }
            )

    for contact in contacts:
        add_email(
            contacts_by_email,
            contact,
            source="ghl",
            id_field="id",
        )
    for customer in customers:
        add_email(
            customers_by_email,
            customer,
            source="stripe",
            id_field="id",
        )
    for client in trainerize_active:
        add_email(
            active_tz_by_email,
            client,
            source="trainerize_active",
            id_field="id",
        )
    for client in trainerize_deactivated:
        add_email(
            deactivated_tz_by_email,
            client,
            source="trainerize_deactivated",
            id_field="id",
        )

    for subscription in subscriptions:
        subscriptions_by_customer[str(subscription.get("customer") or "")].append(
            subscription
        )
    for invoice in invoices:
        invoices_by_customer[str(invoice.get("customer") or "")].append(invoice)

    latest_opportunities = latest_membership_opportunities(opportunities)
    for missing in missing_email:
        if missing["source"] != "ghl":
            continue
        contact = missing["record"]
        missing["active_signal"] = is_ghl_active(
            contact,
            latest_opportunities.get(str(contact.get("id") or "")),
        )
    all_emails = sorted(
        set(contacts_by_email)
        | set(customers_by_email)
        | set(active_tz_by_email)
        | set(deactivated_tz_by_email)
    )
    identities: list[dict[str, Any]] = []

    for email in all_emails:
        email_contacts = contacts_by_email[email]
        email_customers = customers_by_email[email]
        active_clients = active_tz_by_email[email]
        deactivated_clients = deactivated_tz_by_email[email]

        contact_opportunities = [
            latest_opportunities.get(str(contact.get("id") or ""))
            for contact in email_contacts
        ]
        contact_opportunities = [row for row in contact_opportunities if row]
        selected_contact = max(
            email_contacts,
            key=lambda row: str(row.get("dateUpdated") or row.get("dateAdded") or ""),
            default={},
        )
        selected_opportunity = max(
            contact_opportunities,
            key=lambda row: str(row.get("updatedAt") or row.get("createdAt") or ""),
            default={},
        )
        fields = custom_field_map(selected_contact)

        email_subscriptions = [
            subscription
            for customer in email_customers
            for subscription in subscriptions_by_customer.get(
                str(customer.get("id") or ""), []
            )
        ]
        email_invoices = [
            invoice
            for customer in email_customers
            for invoice in invoices_by_customer.get(str(customer.get("id") or ""), [])
        ]
        latest_invoice = max(
            email_invoices,
            key=lambda row: int(row.get("created") or 0),
            default={},
        )
        stripe_statuses = sorted(
            {normalise_text(row.get("status")) for row in email_subscriptions}
        )
        stage_id = str(selected_opportunity.get("pipelineStageId") or "")

        identities.append(
            {
                "identity_key": email,
                "email": email,
                "ghl_contacts": email_contacts,
                "stripe_customers": email_customers,
                "stripe_subscriptions": email_subscriptions,
                "trainerize_active": active_clients,
                "trainerize_deactivated": deactivated_clients,
                "ghl_active_signal": any(
                    is_ghl_active(
                        contact,
                        latest_opportunities.get(str(contact.get("id") or "")),
                    )
                    for contact in email_contacts
                ),
                "stripe_entitled_signal": any(
                    is_stripe_entitled(row) for row in email_subscriptions
                ),
                "trainerize_active_signal": bool(active_clients),
                "membership_type": fields.get(GHL_FIELDS["membership_type"]),
                "membership_stage": MEMBERSHIP_STAGES.get(stage_id),
                "cancellation_status": fields.get(
                    GHL_FIELDS["cancellation_status"]
                ),
                "cancellation_type": fields.get(GHL_FIELDS["cancellation_type"]),
                "notice_end_date": fields.get(GHL_FIELDS["notice_end_date"]),
                "final_access_date": fields.get(GHL_FIELDS["final_access_date"]),
                "stripe_statuses": stripe_statuses,
                "latest_invoice_status": latest_invoice.get("status"),
                "selected_contact": selected_contact,
                "selected_opportunity": selected_opportunity,
            }
        )

    return identities, missing_email


def make_exception(
    identity: dict[str, Any],
    *,
    severity: str,
    exception_type: str,
    summary: str,
    recommended_action: str,
    owner: str = "Admin Eve",
    extra_evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    evidence = {
        "ghl_contact_count": len(identity.get("ghl_contacts") or []),
        "stripe_customer_count": len(identity.get("stripe_customers") or []),
        "stripe_subscription_statuses": identity.get("stripe_statuses") or [],
        "trainerize_active_count": len(identity.get("trainerize_active") or []),
        "trainerize_deactivated_count": len(
            identity.get("trainerize_deactivated") or []
        ),
        "ghl_active_signal": bool(identity.get("ghl_active_signal")),
        "stripe_entitled_signal": bool(identity.get("stripe_entitled_signal")),
        "trainerize_active_signal": bool(
            identity.get("trainerize_active_signal")
        ),
        "membership_type": identity.get("membership_type"),
        "membership_stage": identity.get("membership_stage"),
        "cancellation_status": identity.get("cancellation_status"),
        "final_access_date": identity.get("final_access_date"),
    }
    evidence.update(extra_evidence or {})
    digest = hashlib.sha256(
        f"{identity['identity_key']}|{exception_type}".encode()
    ).hexdigest()[:16]
    return {
        "exception_id": digest,
        "identity_key": identity["identity_key"],
        "email": identity.get("email"),
        "severity": severity,
        "exception_type": exception_type,
        "summary": summary,
        "evidence": evidence,
        "recommended_action": recommended_action,
        "owner": owner,
        "auto_action_allowed": False,
    }


def classify_exceptions(
    identities: list[dict[str, Any]],
    missing_email: list[dict[str, Any]],
    *,
    today: date | None = None,
    account_classifications: dict[str, dict[str, Any]] | None = None,
    authoritative_stripe_customers: dict[str, str] | None = None,
) -> list[dict[str, Any]]:
    today = today or date.today()
    account_classifications = account_classifications or {}
    authoritative_stripe_customers = authoritative_stripe_customers or {}
    exceptions: list[dict[str, Any]] = []

    def repeated_source_email(rows: list[dict[str, Any]]) -> bool:
        counts: dict[str, int] = defaultdict(int)
        for row in rows:
            email = normalise_email(row.get("email"))
            if email:
                counts[email] += 1
        return any(count > 1 for count in counts.values())

    for missing in missing_email:
        source = str(missing["source"])
        source_id = str(missing.get("source_id") or "unknown")
        active_signal = bool(missing.get("active_signal"))
        if source == "ghl":
            severity = "high" if active_signal else "low"
        elif source == "trainerize_active":
            severity = "high"
        elif source == "stripe":
            severity = "medium"
        else:
            severity = "low"
        identity = {
            "identity_key": f"missing:{source}:{source_id}",
            "email": None,
        }
        exceptions.append(
            make_exception(
                identity,
                severity=severity,
                exception_type="missing_email",
                summary=f"{source} record has no usable email for deterministic matching",
                recommended_action=(
                    "Verify the source record and add or correct the email. "
                    "Do not match by name."
                ),
                extra_evidence={
                    "source": source,
                    "source_id": source_id,
                    "active_signal": active_signal,
                },
            )
        )

    for identity in identities:
        ghl_count = len(identity["ghl_contacts"])
        stripe_count = len(identity["stripe_customers"])
        tz_active_count = len(identity["trainerize_active"])
        tz_deactivated_count = len(identity["trainerize_deactivated"])
        ghl_active = bool(identity["ghl_active_signal"])
        stripe_entitled = bool(identity["stripe_entitled_signal"])
        tz_active = bool(identity["trainerize_active_signal"])
        cancellation_status = normalise_text(identity.get("cancellation_status"))
        final_access = parse_iso_date(identity.get("final_access_date"))
        account_classification = account_classifications.get(
            identity["identity_key"], {}
        )
        approved_active_without_entitlement = bool(
            account_classification.get("approved_active_without_local_entitlement")
        )

        if repeated_source_email(identity["ghl_contacts"]):
            exceptions.append(
                make_exception(
                    identity,
                    severity="high" if ghl_active else "low",
                    exception_type="duplicate_ghl_email",
                    summary="Multiple GHL contacts share the same exact email",
                    recommended_action=(
                        "Review and merge only through the approved GHL duplicate "
                        "process after confirming record ownership."
                    ),
                )
            )
        if repeated_source_email(identity["stripe_customers"]):
            entitled_customer_ids = {
                str(subscription.get("customer") or "")
                for subscription in identity["stripe_subscriptions"]
                if is_stripe_entitled(subscription)
            }
            reviewed_customer_id = authoritative_stripe_customers.get(
                identity["identity_key"]
            )
            observed_customer_ids = {
                str(customer.get("id") or "")
                for customer in identity["stripe_customers"]
            }
            reviewed_duplicate_is_consistent = (
                reviewed_customer_id in observed_customer_ids
                and (
                    not entitled_customer_ids
                    or entitled_customer_ids == {reviewed_customer_id}
                )
            )
            if reviewed_duplicate_is_consistent:
                continue
            duplicate_stripe_severity = (
                "critical"
                if len(entitled_customer_ids) > 1
                else "medium"
                if entitled_customer_ids
                else "low"
            )
            exceptions.append(
                make_exception(
                    identity,
                    severity=duplicate_stripe_severity,
                    exception_type="duplicate_stripe_email",
                    summary="Multiple Stripe customers share the same exact email",
                    recommended_action=(
                        "Determine the authoritative Stripe customer and preserve "
                        "subscription history before updating identifiers."
                    ),
                )
            )
        if tz_active_count > 1:
            exceptions.append(
                make_exception(
                    identity,
                    severity="critical",
                    exception_type="duplicate_trainerize_active_email",
                    summary="Multiple active Trainerize clients share the same exact email",
                    recommended_action=(
                        "Stop automated fulfilment and resolve the duplicate accounts "
                        "with Trainerize support or the approved account procedure."
                    ),
                )
            )
        if tz_active_count and tz_deactivated_count:
            exceptions.append(
                make_exception(
                    identity,
                    severity="medium",
                    exception_type="trainerize_active_and_deactivated_duplicate",
                    summary="The same email exists on active and deactivated Trainerize rosters",
                    recommended_action=(
                        "Confirm the active account is the intended identity and retain "
                        "the deactivated record as history unless a safe merge is approved."
                    ),
                )
            )

        if stripe_entitled and not tz_active:
            exceptions.append(
                make_exception(
                    identity,
                    severity="high",
                    exception_type="paid_without_trainerize_access",
                    summary="Stripe shows an entitled subscription but Trainerize has no active client",
                    recommended_action=(
                        "Verify the GHL identity and service start date, then complete "
                        "the approved Trainerize onboarding or document the exception."
                    ),
                )
            )
        elif (
            ghl_active
            and not tz_active
            and not approved_active_without_entitlement
        ):
            exceptions.append(
                make_exception(
                    identity,
                    severity="medium",
                    exception_type="ghl_member_without_trainerize_access",
                    summary="GHL shows an active member signal but Trainerize has no active client",
                    recommended_action=(
                        "Verify whether the member is paid outside Stripe, future-dated "
                        "or incorrectly classified before provisioning access."
                    ),
                )
            )

        ended_access = (
            cancellation_status == "cancelled"
            and final_access is not None
            and final_access <= today
        )
        if tz_active and ended_access:
            exceptions.append(
                make_exception(
                    identity,
                    severity="critical",
                    exception_type="trainerize_active_after_final_access",
                    summary="Trainerize remains active after the recorded final access date",
                    recommended_action=(
                        "Verify the accepted cancellation and final service date, then "
                        "deactivate through the approved cancellation control."
                    ),
                )
            )
        elif tz_active and cancellation_status == "cancelled":
            exceptions.append(
                make_exception(
                    identity,
                    severity="medium",
                    exception_type="cancelled_but_final_access_unresolved",
                    summary="GHL shows Cancelled while Trainerize remains active",
                    recommended_action=(
                        "Confirm whether the final access date is future, missing or "
                        "incorrect before changing Trainerize."
                    ),
                )
            )

        if (
            tz_active
            and not ghl_active
            and not stripe_entitled
            and not approved_active_without_entitlement
        ):
            exceptions.append(
                make_exception(
                    identity,
                    severity="medium",
                    exception_type="trainerize_active_without_current_entitlement_signal",
                    summary="Trainerize is active without a current GHL or Stripe entitlement signal",
                    recommended_action=(
                        "Review for complimentary, staff, assessment, future, manually "
                        "paid or stale access. Do not deactivate from this report alone."
                    ),
                )
            )
        if stripe_entitled and not ghl_active:
            exceptions.append(
                make_exception(
                    identity,
                    severity="medium",
                    exception_type="stripe_entitled_without_ghl_member_signal",
                    summary="Stripe is entitled but GHL has no active member signal",
                    recommended_action=(
                        "Verify GHL membership tags, pipeline stage and contact identity."
                    ),
                )
            )
        if ghl_active and not stripe_entitled and not approved_active_without_entitlement:
            has_ended_subscription = any(
                status in STRIPE_ENDED_STATUSES
                for status in identity.get("stripe_statuses") or []
            )
            exceptions.append(
                make_exception(
                    identity,
                    severity="medium" if has_ended_subscription else "low",
                    exception_type="ghl_member_without_stripe_entitlement",
                    summary="GHL is active but Stripe has no currently entitled subscription",
                    recommended_action=(
                        "Review for non-Stripe payment, approved complimentary access, "
                        "future start, billing failure or stale GHL lifecycle state."
                    ),
                )
            )

    exceptions.sort(
        key=lambda row: (
            SEVERITY_ORDER.get(row["severity"], 99),
            row["exception_type"],
            row["identity_key"],
        )
    )
    return exceptions


def insert_snapshots(
    connection: sqlite3.Connection,
    run_id: str,
    contacts: list[dict[str, Any]],
    opportunities: list[dict[str, Any]],
    customers: list[dict[str, Any]],
    subscriptions: list[dict[str, Any]],
    invoices: list[dict[str, Any]],
    trainerize_active: list[dict[str, Any]],
    trainerize_deactivated: list[dict[str, Any]],
    identities: list[dict[str, Any]],
    exceptions: list[dict[str, Any]],
) -> None:
    latest_opportunities = latest_membership_opportunities(opportunities)
    for contact in contacts:
        fields = custom_field_map(contact)
        connection.execute(
            """
            INSERT INTO ghl_contacts VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                str(contact.get("id") or ""),
                normalise_email(contact.get("email")) or None,
                contact.get("firstName"),
                contact.get("lastName"),
                contact.get("assignedTo"),
                json_text(contact.get("tags") or []),
                fields.get(GHL_FIELDS["membership_type"]),
                fields.get(GHL_FIELDS["cancellation_status"]),
                fields.get(GHL_FIELDS["cancellation_type"]),
                fields.get(GHL_FIELDS["notice_end_date"]),
                fields.get(GHL_FIELDS["final_access_date"]),
                contact.get("dateAdded"),
                contact.get("dateUpdated"),
                json_text(contact),
            ),
        )
    for opportunity in opportunities:
        stage_id = str(opportunity.get("pipelineStageId") or "")
        connection.execute(
            """
            INSERT INTO ghl_opportunities VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                str(opportunity.get("id") or ""),
                str(opportunity.get("contactId") or ""),
                opportunity.get("pipelineId"),
                stage_id,
                MEMBERSHIP_STAGES.get(stage_id),
                opportunity.get("status"),
                opportunity.get("updatedAt"),
                json_text(opportunity),
            ),
        )
    for customer in customers:
        connection.execute(
            """
            INSERT INTO stripe_customers VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                str(customer.get("id") or ""),
                normalise_email(customer.get("email")) or None,
                customer.get("name"),
                int(bool(customer.get("delinquent"))),
                as_iso_timestamp(customer.get("created")),
                json_text(customer),
            ),
        )
    for subscription in subscriptions:
        items = (subscription.get("items") or {}).get("data") or []
        product_ids = sorted(
            {
                str((item.get("price") or {}).get("product") or "")
                for item in items
                if (item.get("price") or {}).get("product")
            }
        )
        price_ids = sorted(
            {
                str((item.get("price") or {}).get("id") or "")
                for item in items
                if (item.get("price") or {}).get("id")
            }
        )
        connection.execute(
            """
            INSERT INTO stripe_subscriptions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                str(subscription.get("id") or ""),
                str(subscription.get("customer") or ""),
                subscription.get("status"),
                as_iso_timestamp(subscription.get("current_period_start")),
                as_iso_timestamp(subscription.get("current_period_end")),
                as_iso_timestamp(subscription.get("cancel_at")),
                int(bool(subscription.get("cancel_at_period_end"))),
                as_iso_timestamp(subscription.get("canceled_at")),
                json_text(subscription.get("pause_collection")),
                json_text(product_ids),
                json_text(price_ids),
                json_text(subscription),
            ),
        )
    for invoice in invoices:
        parent = invoice.get("parent") or {}
        subscription_id = (
            invoice.get("subscription")
            or (parent.get("subscription_details") or {}).get("subscription")
        )
        connection.execute(
            """
            INSERT INTO stripe_invoices VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                str(invoice.get("id") or ""),
                str(invoice.get("customer") or ""),
                str(subscription_id or ""),
                invoice.get("status"),
                int(bool(invoice.get("paid"))),
                invoice.get("amount_due"),
                invoice.get("amount_paid"),
                as_iso_timestamp(invoice.get("period_end")),
                as_iso_timestamp(invoice.get("created")),
                json_text(invoice),
            ),
        )
    for view, clients in (
        ("active", trainerize_active),
        ("deactivated", trainerize_deactivated),
    ):
        for client in clients:
            connection.execute(
                """
                INSERT INTO trainerize_clients VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    int(client.get("id") or 0),
                    normalise_email(client.get("email")) or None,
                    client.get("firstName"),
                    client.get("lastName"),
                    view,
                    client.get("status"),
                    client.get("type"),
                    client.get("role"),
                    client.get("trainerID"),
                    client.get("latestSignedIn"),
                    json_text(client),
                ),
            )
    for identity in identities:
        evidence = {
            "ghl_contact_count": len(identity["ghl_contacts"]),
            "stripe_customer_count": len(identity["stripe_customers"]),
            "trainerize_active_count": len(identity["trainerize_active"]),
            "trainerize_deactivated_count": len(identity["trainerize_deactivated"]),
        }
        connection.execute(
            """
            INSERT INTO identity_register VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
            """,
            (
                run_id,
                identity["identity_key"],
                identity.get("email"),
                json_text([row.get("id") for row in identity["ghl_contacts"]]),
                json_text([row.get("id") for row in identity["stripe_customers"]]),
                json_text(
                    [row.get("id") for row in identity["stripe_subscriptions"]]
                ),
                json_text([row.get("id") for row in identity["trainerize_active"]]),
                json_text(
                    [row.get("id") for row in identity["trainerize_deactivated"]]
                ),
                int(identity["ghl_active_signal"]),
                int(identity["stripe_entitled_signal"]),
                int(identity["trainerize_active_signal"]),
                identity.get("membership_type"),
                identity.get("membership_stage"),
                identity.get("cancellation_status"),
                identity.get("final_access_date"),
                json_text(identity.get("stripe_statuses") or []),
                identity.get("latest_invoice_status"),
                json_text(evidence),
            ),
        )
    for exception in exceptions:
        connection.execute(
            """
            INSERT INTO exceptions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                exception["exception_id"],
                exception["identity_key"],
                exception.get("email"),
                exception["severity"],
                exception["exception_type"],
                exception["summary"],
                json_text(exception["evidence"]),
                exception["recommended_action"],
                exception["owner"],
                int(exception["auto_action_allowed"]),
            ),
        )
    connection.commit()


def write_private_csv(
    path: Path, rows: list[dict[str, Any]], fields: list[str]
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    os.chmod(path.parent, 0o700)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    os.chmod(path, 0o600)


def write_outputs(
    run_id: str,
    identities: list[dict[str, Any]],
    exceptions: list[dict[str, Any]],
    source_counts: dict[str, int],
) -> dict[str, Any]:
    run_dir = PRIVATE_DIR / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    os.chmod(run_dir, 0o700)

    identity_rows = [
        {
            "email": row.get("email"),
            "ghl_contact_count": len(row["ghl_contacts"]),
            "stripe_customer_count": len(row["stripe_customers"]),
            "stripe_subscription_count": len(row["stripe_subscriptions"]),
            "trainerize_active_count": len(row["trainerize_active"]),
            "trainerize_deactivated_count": len(row["trainerize_deactivated"]),
            "ghl_active_signal": row["ghl_active_signal"],
            "stripe_entitled_signal": row["stripe_entitled_signal"],
            "trainerize_active_signal": row["trainerize_active_signal"],
            "membership_type": row.get("membership_type"),
            "membership_stage": row.get("membership_stage"),
            "cancellation_status": row.get("cancellation_status"),
            "final_access_date": row.get("final_access_date"),
            "stripe_statuses": "|".join(row.get("stripe_statuses") or []),
            "latest_invoice_status": row.get("latest_invoice_status"),
        }
        for row in identities
    ]
    write_private_csv(
        run_dir / "identity_register.csv",
        identity_rows,
        [
            "email",
            "ghl_contact_count",
            "stripe_customer_count",
            "stripe_subscription_count",
            "trainerize_active_count",
            "trainerize_deactivated_count",
            "ghl_active_signal",
            "stripe_entitled_signal",
            "trainerize_active_signal",
            "membership_type",
            "membership_stage",
            "cancellation_status",
            "final_access_date",
            "stripe_statuses",
            "latest_invoice_status",
        ],
    )
    exception_rows = [
        {
            **{key: value for key, value in row.items() if key != "evidence"},
            "evidence": json_text(row["evidence"]),
        }
        for row in exceptions
    ]
    write_private_csv(
        run_dir / "exceptions.csv",
        exception_rows,
        [
            "exception_id",
            "identity_key",
            "email",
            "severity",
            "exception_type",
            "summary",
            "evidence",
            "recommended_action",
            "owner",
            "auto_action_allowed",
        ],
    )

    by_type: dict[str, int] = defaultdict(int)
    by_severity: dict[str, int] = defaultdict(int)
    by_severity_type: dict[tuple[str, str], int] = defaultdict(int)
    for exception in exceptions:
        by_type[exception["exception_type"]] += 1
        by_severity[exception["severity"]] += 1
        by_severity_type[
            (exception["severity"], exception["exception_type"])
        ] += 1

    summary = {
        "run_id": run_id,
        "generated_at": utc_now(),
        "mode": "read_only",
        "sources": source_counts,
        "identity_count": len(identities),
        "exception_count": len(exceptions),
        "exceptions_by_severity": dict(sorted(by_severity.items())),
        "exceptions_by_type": dict(sorted(by_type.items())),
        "limitations": [
            "Trainerize product subscriptions, Class Access add-ons and credit balances are not included because reliable API reads are not yet verified.",
            "GHL membership tags and pipeline stages contain known historical inconsistencies, so they are evidence signals rather than a standalone entitlement ledger.",
            "No automatic access, billing or lifecycle changes are permitted from this report.",
        ],
    }
    summary_path = run_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    os.chmod(summary_path, 0o600)

    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Trainerize Reporting and Reconciliation",
        "",
        f"**Run:** {run_id}  ",
        f"**Generated:** {summary['generated_at']}  ",
        "**Mode:** Read-only",
        "",
        "## Source Coverage",
        "",
        "| Source | Records |",
        "|---|---:|",
    ]
    for name, count in source_counts.items():
        lines.append(f"| {name.replace('_', ' ').title()} | {count:,} |")
    lines += [
        "",
        "## Exceptions",
        "",
        f"Total exception rows: **{len(exceptions):,}**",
        "",
        "| Severity | Count |",
        "|---|---:|",
    ]
    for severity in ("critical", "high", "medium", "low", "info"):
        if by_severity.get(severity):
            lines.append(f"| {severity.title()} | {by_severity[severity]:,} |")
    lines += [
        "",
        "## Exception Types",
        "",
        "| Severity | Type | Count |",
        "|---|---|---:|",
    ]
    for (severity, exception_type), count in sorted(
        by_severity_type.items(),
        key=lambda item: (
            SEVERITY_ORDER.get(item[0][0], 99),
            -item[1],
            item[0][1],
        ),
    ):
        lines.append(
            f"| {severity.title()} | "
            f"{exception_type.replace('_', ' ').title()} | {count:,} |"
        )
    lines += [
        "",
        "## Interpretation",
        "",
        "This is an exception-discovery report, not an instruction to change member access. Each identified case remains private and requires evidence review.",
        "",
        "Trainerize product subscriptions, Class Access add-ons and credit balances remain outside automated reconciliation until reliable API reads are verified.",
        "",
    ]
    public_path = PUBLIC_DIR / "latest-reconciliation-summary.md"
    public_path.write_text("\n".join(lines), encoding="utf-8")
    return summary


def run_reconciliation(
    *,
    database: Path = DATABASE,
    fetch_invoices: bool = False,
    identity_links: dict[str, str] | None = None,
    identity_record_links: dict[tuple[str, str], str] | None = None,
    account_classifications: dict[str, dict[str, Any]] | None = None,
    authoritative_stripe_customers: dict[str, str] | None = None,
) -> dict[str, Any]:
    env = load_env()
    required = (
        "GHL_API_KEY",
        "GHL_LOCATION_ID",
        "STRIPE_RESTRICTED_KEY",
        "TRAINERIZE_GROUP_ID",
        "TRAINERIZE_API_TOKEN",
        "TRAINERIZE_LOCATION_ID",
    )
    missing = [key for key in required if not env.get(key)]
    if missing:
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")

    run_id = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    connection = open_database(database)
    connection.execute(
        "INSERT INTO runs (run_id, started_at, status) VALUES (?, ?, 'running')",
        (run_id, utc_now()),
    )
    connection.commit()
    try:
        ghl = GHLReader(env["GHL_API_KEY"], env["GHL_LOCATION_ID"])
        stripe = StripeReader(env["STRIPE_RESTRICTED_KEY"])
        trainerize = TrainerizeClient()

        contacts = ghl.contacts()
        opportunities = ghl.opportunities()
        customers = stripe.collection("customers")
        subscriptions = stripe.collection("subscriptions", {"status": "all"})
        invoice_cutoff = int(
            (datetime.now(UTC) - timedelta(days=90)).timestamp()
        )
        invoices = (
            stripe.collection(
                "invoices",
                {"created[gte]": invoice_cutoff},
            )
            if fetch_invoices
            else []
        )
        trainerize_active = fetch_trainerize_view(trainerize, "activeClient")
        trainerize_deactivated = fetch_trainerize_view(
            trainerize, "deactivatedClient"
        )

        resolved_identity_links = (
            identity_links if identity_links is not None else load_identity_links()
        )
        resolved_account_classifications = canonicalise_control_keys(
            (
                account_classifications
                if account_classifications is not None
                else load_account_classifications()
            ),
            resolved_identity_links,
        )
        resolved_authoritative_customers = canonicalise_control_keys(
            (
                authoritative_stripe_customers
                if authoritative_stripe_customers is not None
                else load_authoritative_stripe_customers()
            ),
            resolved_identity_links,
        )

        identities, missing_email = build_identity_records(
            contacts,
            opportunities,
            customers,
            subscriptions,
            invoices,
            trainerize_active,
            trainerize_deactivated,
            resolved_identity_links,
            (
                identity_record_links
                if identity_record_links is not None
                else load_identity_record_links()
            ),
        )
        exceptions = classify_exceptions(
            identities,
            missing_email,
            account_classifications=resolved_account_classifications,
            authoritative_stripe_customers=resolved_authoritative_customers,
        )
        insert_snapshots(
            connection,
            run_id,
            contacts,
            opportunities,
            customers,
            subscriptions,
            invoices,
            trainerize_active,
            trainerize_deactivated,
            identities,
            exceptions,
        )
        source_counts = {
            "ghl_contacts": len(contacts),
            "ghl_opportunities": len(opportunities),
            "stripe_customers": len(customers),
            "stripe_subscriptions": len(subscriptions),
            "stripe_invoices": len(invoices),
            "trainerize_active": len(trainerize_active),
            "trainerize_deactivated": len(trainerize_deactivated),
        }
        summary = write_outputs(run_id, identities, exceptions, source_counts)
        connection.execute(
            """
            UPDATE runs
            SET finished_at=?, status='complete', counts_json=?, limitations_json=?
            WHERE run_id=?
            """,
            (
                utc_now(),
                json_text(source_counts),
                json_text(summary["limitations"]),
                run_id,
            ),
        )
        connection.commit()
        return summary
    except BaseException:
        connection.execute(
            "UPDATE runs SET finished_at=?, status='failed' WHERE run_id=?",
            (utc_now(), run_id),
        )
        connection.commit()
        raise
    finally:
        connection.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--database",
        type=Path,
        default=DATABASE,
        help="Private SQLite output path.",
    )
    parser.add_argument(
        "--include-invoices",
        action="store_true",
        help="Include the latest 90 days of invoices. Daily entitlement checks use subscriptions by default.",
    )
    args = parser.parse_args()
    summary = run_reconciliation(
        database=args.database,
        fetch_invoices=args.include_invoices,
    )
    safe = {
        "run_id": summary["run_id"],
        "mode": summary["mode"],
        "sources": summary["sources"],
        "identity_count": summary["identity_count"],
        "exception_count": summary["exception_count"],
        "exceptions_by_severity": summary["exceptions_by_severity"],
    }
    print(json.dumps(safe, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
