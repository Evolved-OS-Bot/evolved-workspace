from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from urllib.parse import parse_qs, urlparse

from cryptography.fernet import Fernet
import pytest
from sqlalchemy import create_engine

from operating_data_hub.xero_adapter import (
    XERO_READ_SCOPES,
    XeroClient,
    XeroConnectionStore,
    profit_and_loss_expense_breakdown,
    profit_and_loss_summary,
)


def token() -> dict[str, object]:
    return {
        "access_token": "access-token",
        "refresh_token": "refresh-token",
        "expires_in": 1800,
        "scope": " ".join(XERO_READ_SCOPES),
    }


def test_xero_credentials_are_encrypted_and_status_is_read_only(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'xero.db'}")
    store = XeroConnectionStore(
        engine,
        Fernet.generate_key().decode("ascii"),
    )
    store.save(
        tenant_id="tenant-1",
        tenant_name="Brown Casserly Pty Ltd",
        token=token(),
    )

    credentials = store.credentials()
    assert credentials is not None
    assert credentials["access_token"] == "access-token"
    assert credentials["refresh_token"] == "refresh-token"
    status = store.status()
    assert status["connected"] is True
    assert status["mode"] == "read_only"
    assert status["tenant_name"] == "Brown Casserly Pty Ltd"


def test_xero_authorisation_url_requests_only_read_scopes(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'xero.db'}")
    store = XeroConnectionStore(
        engine,
        Fernet.generate_key().decode("ascii"),
    )
    client = XeroClient(
        client_id="client-id",
        client_secret="client-secret",
        redirect_uri="https://hub.example/api/v1/xero/callback",
        tenant_name="Brown Casserly Pty Ltd",
        store=store,
    )

    query = parse_qs(urlparse(client.authorization_url("state-1")).query)
    assert query["state"] == ["state-1"]
    assert query["redirect_uri"] == [
        "https://hub.example/api/v1/xero/callback"
    ]
    assert set(query["scope"][0].split()) == set(XERO_READ_SCOPES)
    assert not any(
        scope.endswith(".transactions")
        or scope in {"accounting.settings", "accounting.contacts"}
        for scope in query["scope"][0].split()
    )


def test_xero_client_rejects_a_masked_secret(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'xero.db'}")
    store = XeroConnectionStore(
        engine,
        Fernet.generate_key().decode("ascii"),
    )
    with pytest.raises(RuntimeError, match="masked display value"):
        XeroClient(
            client_id="client-id",
            client_secret="0N••••••Ba",
            redirect_uri="https://hub.example/api/v1/xero/callback",
            tenant_name="Brown Casserly Pty Ltd",
            store=store,
        )


def test_xero_snapshot_masks_bank_accounts_and_remains_shadow_ready(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'xero.db'}")
    store = XeroConnectionStore(
        engine,
        Fernet.generate_key().decode("ascii"),
    )
    store.save(
        tenant_id="tenant-1",
        tenant_name="Brown Casserly Pty Ltd",
        token={**token(), "expires_in": 3600},
    )
    client = XeroClient(
        client_id="client-id",
        client_secret="client-secret",
        redirect_uri="https://hub.example/api/v1/xero/callback",
        tenant_name="Brown Casserly Pty Ltd",
        store=store,
    )

    def fake_get(path, *, params=None):
        if path == "Organisation":
            return {"Organisations": [{"Name": "Brown Casserly Pty Ltd"}]}
        if path == "Accounts":
            return {
                "Accounts": [
                    {
                        "AccountID": "bank-1",
                        "Name": "Business One",
                        "Code": "090",
                        "Type": "BANK",
                        "Status": "ACTIVE",
                        "CurrencyCode": "AUD",
                        "BankAccountNumber": "032646565904",
                    },
                    {"AccountID": "income-1", "Type": "REVENUE"},
                ]
            }
        assert path == "Reports/BankSummary"
        assert params == {"fromDate": "2025-08-01", "toDate": "2026-08-01"}
        return {"Reports": [{"ReportName": "Bank Summary", "Rows": []}]}

    client._get = fake_get
    snapshot = client.accounting_snapshot(
        from_date=date(2025, 8, 1),
        to_date=date(2026, 8, 1),
    )
    assert snapshot["complete"] is True
    assert snapshot["summary"]["authority"] == "xero_reconciled_accounting"
    assert snapshot["summary"]["publication_impact"] == "none"
    assert snapshot["rows"] == [
        {
            "account_id": "bank-1",
            "name": "Business One",
            "code": "090",
            "status": "ACTIVE",
            "currency": "AUD",
            "account_number_last4": "5904",
        }
    ]
    assert "032646565904" not in str(snapshot)


def test_profit_and_loss_summary_excludes_transfers_and_combines_expenses():
    summary = profit_and_loss_summary(
        {
            "Status": "OK",
            "Reports": [
                {
                    "ReportName": "Profit and Loss",
                    "Rows": [
                        {
                            "RowType": "Section",
                            "Title": "Income",
                            "Rows": [
                                {
                                    "RowType": "SummaryRow",
                                    "Cells": [
                                        {"Value": "Total Income"},
                                        {"Value": "20,000.00"},
                                    ],
                                }
                            ],
                        },
                        {
                            "RowType": "Section",
                            "Title": "Less Cost of Sales",
                            "Rows": [
                                {
                                    "RowType": "SummaryRow",
                                    "Cells": [
                                        {"Value": "Total Cost of Sales"},
                                        {"Value": "2,500.00"},
                                    ],
                                }
                            ],
                        },
                        {
                            "RowType": "Section",
                            "Title": "Less Operating Expenses",
                            "Rows": [
                                {
                                    "RowType": "SummaryRow",
                                    "Cells": [
                                        {"Value": "Total Operating Expenses"},
                                        {"Value": "7,250.00"},
                                    ],
                                }
                            ],
                        },
                        {
                            "RowType": "Section",
                            "Rows": [
                                {
                                    "RowType": "Row",
                                    "Cells": [
                                        {"Value": "Net Profit"},
                                        {"Value": "10,250.00"},
                                    ],
                                }
                            ],
                        },
                    ],
                }
            ],
        }
    )

    assert summary["complete"] is True
    assert summary["income"] == "20000.00"
    assert summary["total_expenses"] == "9750.00"
    assert summary["net_profit"] == "10250.00"
    assert summary["transfers_excluded"] is True
    assert summary["accounting_basis"] == "accrual"


def test_profit_and_loss_expense_breakdown_is_compact_and_reconciles():
    breakdown = profit_and_loss_expense_breakdown(
        {
            "Status": "OK",
            "Reports": [
                {
                    "Rows": [
                        {
                            "RowType": "Section",
                            "Title": "Less Cost of Sales",
                            "Rows": [
                                {
                                    "RowType": "Row",
                                    "Cells": [
                                        {"Value": "Stripe Fees"},
                                        {"Value": "250.00"},
                                    ],
                                },
                                {
                                    "RowType": "SummaryRow",
                                    "Cells": [
                                        {"Value": "Total Cost of Sales"},
                                        {"Value": "250.00"},
                                    ],
                                },
                            ],
                        },
                        {
                            "RowType": "Section",
                            "Title": "Less Operating Expenses",
                            "Rows": [
                                {
                                    "RowType": "Row",
                                    "Cells": [
                                        {"Value": "Wages"},
                                        {"Value": "5,000.00"},
                                    ],
                                },
                                {
                                    "RowType": "Row",
                                    "Cells": [
                                        {"Value": "Foreign Currency Gain"},
                                        {"Value": "-10.00"},
                                    ],
                                },
                            ],
                        },
                        {
                            "RowType": "Section",
                            "Title": "Income",
                            "Rows": [
                                {
                                    "RowType": "Row",
                                    "Cells": [
                                        {"Value": "Membership Income"},
                                        {"Value": "20,000.00"},
                                    ],
                                }
                            ],
                        },
                    ]
                }
            ],
        },
        limit=2,
    )

    assert breakdown["categories"] == [
        {"category": "Wages", "amount": "5000.00"},
        {"category": "Stripe Fees", "amount": "250.00"},
    ]
    assert breakdown["other_amount"] == "-10.00"
    assert breakdown["total_amount"] == "5240.00"
    assert breakdown["category_count"] == 3


def test_xero_snapshot_collects_completed_period_profit_and_loss(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'xero-periods.db'}")
    store = XeroConnectionStore(
        engine,
        Fernet.generate_key().decode("ascii"),
    )
    store.save(
        tenant_id="tenant-1",
        tenant_name="Brown Casserly Pty Ltd",
        token={**token(), "expires_in": 3600},
    )
    client = XeroClient(
        client_id="client-id",
        client_secret="client-secret",
        redirect_uri="https://hub.example/api/v1/xero/callback",
        tenant_name="Brown Casserly Pty Ltd",
        store=store,
    )

    def fake_get(path, *, params=None):
        if path == "Organisation":
            return {"Organisations": [{"Name": "Brown Casserly Pty Ltd"}]}
        if path == "Accounts":
            return {"Accounts": []}
        if path == "Reports/BankSummary":
            return {"Status": "OK", "Reports": [{"Rows": []}]}
        assert path == "Reports/ProfitAndLoss"
        assert params == {
            "fromDate": "2026-07-20",
            "toDate": "2026-07-26",
        }
        return {
            "Status": "OK",
            "Reports": [
                {
                    "ReportName": "Profit and Loss",
                    "Rows": [
                        {
                            "RowType": "SummaryRow",
                            "Cells": [
                                {"Value": "Total Expenses"},
                                {"Value": "5000.00"},
                            ],
                        }
                    ],
                }
            ],
        }

    client._get = fake_get
    snapshot = client.accounting_snapshot(
        from_date=date(2025, 8, 1),
        to_date=date(2026, 8, 1),
        profit_and_loss_periods={
            "week": (date(2026, 7, 20), date(2026, 7, 26))
        },
    )

    assert snapshot["schema_version"] == 2
    assert snapshot["summary"]["profit_and_loss_periods"] == ["week"]
    assert (
        snapshot["profit_and_loss"]["week"]["summary"]["total_expenses"]
        == "5000.00"
    )
