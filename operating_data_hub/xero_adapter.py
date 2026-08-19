from __future__ import annotations

import json
import re
import secrets
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from typing import Any
from urllib.parse import urlencode

import requests
from cryptography.fernet import Fernet, InvalidToken
from requests.adapters import HTTPAdapter
from sqlalchemy import Column, DateTime, MetaData, String, Table, Text, insert, select, update
from urllib3.util.retry import Retry


XERO_AUTHORIZE_URL = "https://login.xero.com/identity/connect/authorize"
XERO_TOKEN_URL = "https://identity.xero.com/connect/token"
XERO_CONNECTIONS_URL = "https://api.xero.com/connections"
XERO_ACCOUNTING_URL = "https://api.xero.com/api.xro/2.0"
XERO_READ_SCOPES = (
    "openid",
    "profile",
    "email",
    "offline_access",
    "accounting.settings.read",
    "accounting.reports.banksummary.read",
    "accounting.reports.profitandloss.read",
)


xero_metadata = MetaData()
xero_connections = Table(
    "hub_xero_connections",
    xero_metadata,
    Column("connection_id", String(64), primary_key=True),
    Column("tenant_id", String(64), nullable=False),
    Column("tenant_name", String(240), nullable=False),
    Column("access_token_encrypted", Text, nullable=False),
    Column("refresh_token_encrypted", Text, nullable=False),
    Column("expires_at", DateTime(timezone=True), nullable=False),
    Column("scopes_json", Text, nullable=False),
    Column("connected_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
    Column("status", String(32), nullable=False),
)


def new_oauth_state() -> str:
    return secrets.token_urlsafe(32)


def _money(value: Any) -> Decimal | None:
    text = str(value or "").strip()
    if not text:
        return None
    negative = text.startswith("(") and text.endswith(")")
    cleaned = text.strip("()").replace(",", "").replace("$", "")
    try:
        amount = Decimal(cleaned)
    except InvalidOperation:
        return None
    return -amount if negative else amount


def _normalise_label(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(value or "").casefold()).strip()


def _report_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    reports = payload.get("Reports") or []
    if not reports:
        return []
    flattened: list[dict[str, Any]] = []

    def visit(row: dict[str, Any], section: str | None = None) -> None:
        current_section = str(row.get("Title") or section or "").strip() or None
        cells = row.get("Cells") or []
        values = [cell.get("Value") for cell in cells]
        if values or row.get("Title"):
            flattened.append(
                {
                    "row_type": row.get("RowType"),
                    "section": current_section,
                    "label": values[0] if values else row.get("Title"),
                    "values": values[1:] if len(values) > 1 else [],
                }
            )
        for child in row.get("Rows") or []:
            visit(child, current_section)

    for row in reports[0].get("Rows") or []:
        visit(row)
    return flattened


def profit_and_loss_summary(payload: dict[str, Any]) -> dict[str, Any]:
    """Return governed headline totals without exposing account-level detail."""
    aliases = {
        "income": {
            "total income",
            "total revenue",
            "total trading income",
        },
        "cost_of_sales": {
            "total cost of sales",
            "total cost of goods sold",
        },
        "operating_expenses": {
            "total operating expenses",
            "total overheads",
        },
        "total_expenses": {"total expenses"},
        "net_profit": {
            "net profit",
            "net loss",
            "net earnings",
        },
    }
    totals: dict[str, Decimal | None] = {
        key: None for key in aliases
    }
    for row in _report_rows(payload):
        label = _normalise_label(row["label"])
        amount = next(
            (
                parsed
                for parsed in (_money(value) for value in reversed(row["values"]))
                if parsed is not None
            ),
            None,
        )
        if amount is None:
            continue
        for key, labels in aliases.items():
            if label in labels:
                totals[key] = amount
                break

    explicit_expenses = totals["total_expenses"]
    if explicit_expenses is not None:
        governed_expenses = abs(explicit_expenses)
    else:
        expense_components = [
            abs(value)
            for value in (
                totals["cost_of_sales"],
                totals["operating_expenses"],
            )
            if value is not None
        ]
        governed_expenses = (
            sum(expense_components, Decimal("0"))
            if expense_components
            else None
        )
    reports = payload.get("Reports") or []
    report = reports[0] if reports else {}
    status = str(payload.get("Status") or "OK").upper()
    return {
        "complete": bool(reports) and status == "OK",
        "report_name": report.get("ReportName") or "Profit and Loss",
        "accounting_basis": "accrual",
        "currency": "AUD",
        "income": (
            format(totals["income"], "f")
            if totals["income"] is not None
            else None
        ),
        "cost_of_sales": (
            format(abs(totals["cost_of_sales"]), "f")
            if totals["cost_of_sales"] is not None
            else None
        ),
        "operating_expenses": (
            format(abs(totals["operating_expenses"]), "f")
            if totals["operating_expenses"] is not None
            else None
        ),
        "total_expenses": (
            format(governed_expenses, "f")
            if governed_expenses is not None
            else None
        ),
        "net_profit": (
            format(totals["net_profit"], "f")
            if totals["net_profit"] is not None
            else None
        ),
        "transfers_excluded": True,
        "classification": "xero_profit_and_loss",
    }


def profit_and_loss_expense_breakdown(
    payload: dict[str, Any],
    *,
    limit: int = 5,
) -> dict[str, Any]:
    """Return an explainable, compact expense view from Xero account rows."""
    expense_sections = {
        "less cost of sales",
        "cost of sales",
        "less operating expenses",
        "operating expenses",
    }
    categories = []
    for row in _report_rows(payload):
        if str(row.get("row_type") or "").casefold() != "row":
            continue
        if _normalise_label(row.get("section")) not in expense_sections:
            continue
        amount = next(
            (
                parsed
                for parsed in (
                    _money(value)
                    for value in reversed(row.get("values") or [])
                )
                if parsed is not None
            ),
            None,
        )
        label = " ".join(str(row.get("label") or "").split())
        if not label or amount is None or amount == 0:
            continue
        categories.append(
            {
                "category": label,
                "amount": format(amount, "f"),
            }
        )

    categories.sort(
        key=lambda item: abs(Decimal(item["amount"])),
        reverse=True,
    )
    shown = categories[: max(0, limit)]
    other_amount = sum(
        (Decimal(item["amount"]) for item in categories[len(shown) :]),
        Decimal("0"),
    )
    total_amount = sum(
        (Decimal(item["amount"]) for item in categories),
        Decimal("0"),
    )
    return {
        "categories": shown,
        "other_amount": format(other_amount, "f"),
        "total_amount": format(total_amount, "f"),
        "category_count": len(categories),
    }


class XeroConnectionStore:
    def __init__(self, engine, encryption_key: str) -> None:
        if not str(encryption_key or "").strip():
            raise RuntimeError("XERO_TOKEN_ENCRYPTION_KEY is required")
        try:
            self.cipher = Fernet(encryption_key.encode("ascii"))
        except (ValueError, TypeError) as exc:
            raise RuntimeError(
                "XERO_TOKEN_ENCRYPTION_KEY must be a valid Fernet key"
            ) from exc
        self.engine = engine
        xero_metadata.create_all(engine)

    def _encrypt(self, value: str) -> str:
        return self.cipher.encrypt(value.encode("utf-8")).decode("ascii")

    def _decrypt(self, value: str) -> str:
        try:
            return self.cipher.decrypt(value.encode("ascii")).decode("utf-8")
        except InvalidToken as exc:
            raise RuntimeError("Stored Xero credentials cannot be decrypted") from exc

    def save(
        self,
        *,
        tenant_id: str,
        tenant_name: str,
        token: dict[str, Any],
    ) -> None:
        now = datetime.now(UTC)
        expires_at = now + timedelta(seconds=max(60, int(token["expires_in"])))
        values = {
            "connection_id": "primary",
            "tenant_id": tenant_id,
            "tenant_name": tenant_name,
            "access_token_encrypted": self._encrypt(str(token["access_token"])),
            "refresh_token_encrypted": self._encrypt(str(token["refresh_token"])),
            "expires_at": expires_at,
            "scopes_json": json.dumps(str(token.get("scope") or "").split()),
            "connected_at": now,
            "updated_at": now,
            "status": "connected",
        }
        with self.engine.begin() as connection:
            existing = connection.execute(
                select(xero_connections.c.connection_id).where(
                    xero_connections.c.connection_id == "primary"
                )
            ).scalar()
            if existing:
                values.pop("connected_at")
                connection.execute(
                    update(xero_connections)
                    .where(xero_connections.c.connection_id == "primary")
                    .values(**values)
                )
            else:
                connection.execute(insert(xero_connections).values(**values))

    def credentials(self) -> dict[str, Any] | None:
        with self.engine.begin() as connection:
            row = connection.execute(
                select(xero_connections).where(
                    xero_connections.c.connection_id == "primary"
                )
            ).mappings().first()
        if not row:
            return None
        expires_at = row["expires_at"]
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=UTC)
        return {
            "tenant_id": row["tenant_id"],
            "tenant_name": row["tenant_name"],
            "access_token": self._decrypt(row["access_token_encrypted"]),
            "refresh_token": self._decrypt(row["refresh_token_encrypted"]),
            "expires_at": expires_at,
            "scopes": json.loads(row["scopes_json"]),
            "status": row["status"],
        }

    def status(self) -> dict[str, Any]:
        credentials = self.credentials()
        if not credentials:
            return {"connected": False, "mode": "read_only"}
        return {
            "connected": credentials["status"] == "connected",
            "mode": "read_only",
            "tenant_name": credentials["tenant_name"],
            "tenant_id": credentials["tenant_id"],
            "scopes": credentials["scopes"],
            "token_expires_at": credentials["expires_at"].isoformat(),
        }


class XeroClient:
    def __init__(
        self,
        *,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        tenant_name: str,
        store: XeroConnectionStore,
        timeout: int = 30,
    ) -> None:
        if not client_id or not client_secret or not redirect_uri:
            raise RuntimeError(
                "XERO_CLIENT_ID, XERO_CLIENT_SECRET and XERO_REDIRECT_URI are required"
            )
        if not client_secret.isascii() or "•" in client_secret:
            raise RuntimeError(
                "XERO_CLIENT_SECRET must be the revealed ASCII secret, not a masked display value"
            )
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.tenant_name = tenant_name
        self.store = store
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

    def authorization_url(self, state: str) -> str:
        return f"{XERO_AUTHORIZE_URL}?{urlencode({
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': ' '.join(XERO_READ_SCOPES),
            'state': state,
        })}"

    def _token_request(self, data: dict[str, str]) -> dict[str, Any]:
        response = self.session.post(
            XERO_TOKEN_URL,
            data=data,
            auth=(self.client_id, self.client_secret),
            timeout=self.timeout,
        )
        response.raise_for_status()
        payload = response.json()
        if not payload.get("access_token") or not payload.get("refresh_token"):
            raise RuntimeError("Xero returned an incomplete OAuth token")
        return payload

    def connect(self, code: str) -> dict[str, Any]:
        token = self._token_request(
            {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": self.redirect_uri,
            }
        )
        response = self.session.get(
            XERO_CONNECTIONS_URL,
            headers={"Authorization": f"Bearer {token['access_token']}"},
            timeout=self.timeout,
        )
        response.raise_for_status()
        connections = response.json()
        if not isinstance(connections, list) or not connections:
            raise RuntimeError("No Xero organisation was authorised")
        matches = [
            item
            for item in connections
            if str(item.get("tenantName") or "").casefold()
            == self.tenant_name.casefold()
        ]
        if len(matches) == 1:
            selected = matches[0]
        elif len(connections) == 1:
            selected = connections[0]
        else:
            raise RuntimeError(
                f"Could not uniquely select Xero organisation {self.tenant_name!r}"
            )
        self.store.save(
            tenant_id=str(selected["tenantId"]),
            tenant_name=str(selected.get("tenantName") or self.tenant_name),
            token=token,
        )
        return self.store.status()

    def _access(self) -> dict[str, Any]:
        credentials = self.store.credentials()
        if not credentials:
            raise RuntimeError("Xero is not connected")
        if credentials["expires_at"] > datetime.now(UTC) + timedelta(minutes=5):
            return credentials
        token = self._token_request(
            {
                "grant_type": "refresh_token",
                "refresh_token": credentials["refresh_token"],
            }
        )
        self.store.save(
            tenant_id=credentials["tenant_id"],
            tenant_name=credentials["tenant_name"],
            token=token,
        )
        refreshed = self.store.credentials()
        if not refreshed:
            raise RuntimeError("Xero token refresh was not persisted")
        return refreshed

    def _get(self, path: str, *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        credentials = self._access()
        response = self.session.get(
            f"{XERO_ACCOUNTING_URL}/{path.lstrip('/')}",
            headers={
                "Authorization": f"Bearer {credentials['access_token']}",
                "Accept": "application/json",
                "Xero-tenant-id": credentials["tenant_id"],
            },
            params=params,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def accounting_snapshot(
        self,
        *,
        from_date: date,
        to_date: date,
        profit_and_loss_periods: (
            dict[str, tuple[date, date]] | None
        ) = None,
    ) -> dict[str, Any]:
        observed_at = datetime.now(UTC)
        organisation = self._get("Organisation")
        accounts = self._get("Accounts")
        bank_summary = self._get(
            "Reports/BankSummary",
            params={
                "fromDate": from_date.isoformat(),
                "toDate": to_date.isoformat(),
            },
        )
        profit_and_loss = {}
        for period_id, (period_start, period_end) in (
            profit_and_loss_periods or {}
        ).items():
            report = self._get(
                "Reports/ProfitAndLoss",
                params={
                    "fromDate": period_start.isoformat(),
                    "toDate": period_end.isoformat(),
                },
            )
            profit_and_loss[period_id] = {
                "period_start": period_start.isoformat(),
                "period_end": period_end.isoformat(),
                "summary": profit_and_loss_summary(report),
                "expense_breakdown": (
                    profit_and_loss_expense_breakdown(report)
                ),
                "report": report,
            }
        bank_accounts = []
        for row in accounts.get("Accounts") or []:
            if str(row.get("Type") or "").upper() != "BANK":
                continue
            account_number = str(row.get("BankAccountNumber") or "")
            bank_accounts.append(
                {
                    "account_id": row.get("AccountID"),
                    "name": row.get("Name"),
                    "code": row.get("Code"),
                    "status": row.get("Status"),
                    "currency": row.get("CurrencyCode"),
                    "account_number_last4": account_number[-4:] if account_number else None,
                }
            )
        organisations = organisation.get("Organisations") or []
        organisation_name = (
            organisations[0].get("Name") if organisations else self.tenant_name
        )
        return {
            "schema_version": 2,
            "observed_at": observed_at.isoformat(),
            "status": "complete",
            "complete": True,
            "rows": bank_accounts,
            "summary": {
                "record_count": len(bank_accounts),
                "organisation": organisation_name,
                "period_start": from_date.isoformat(),
                "period_end": to_date.isoformat(),
                "authority": "xero_reconciled_accounting",
                "publication_impact": "none",
                "profit_and_loss_periods": sorted(profit_and_loss),
            },
            "bank_summary": bank_summary,
            "profit_and_loss": profit_and_loss,
        }
