from __future__ import annotations

import csv
from pathlib import Path
from types import SimpleNamespace
from zoneinfo import ZoneInfo

import pytest

from revenue_gap_control.railway_runtime import RailwayRevenueRuntime


def runtime(tmp_path: Path) -> RailwayRevenueRuntime:
    result = object.__new__(RailwayRevenueRuntime)
    result.settings = SimpleNamespace(timezone=ZoneInfo("Australia/Brisbane"))
    result.legacy_evidence_path = tmp_path / "legacy-payment-evidence.csv"
    return result


def valid_row() -> dict[str, str]:
    return {
        "email": " Member@Example.com ",
        "payment_rail": "EziDebit",
        "status": "collecting",
        "weekly_amount": "99",
        "last_receipt_date": "2026-07-22",
        "next_due_date": "2026-07-29",
        "notes": "  Verified   in PTMinder. ",
    }


def test_replace_legacy_evidence_normalises_and_hashes(tmp_path):
    service = runtime(tmp_path)

    result = service.replace_legacy_evidence([valid_row()])

    assert result["status"] == "replaced"
    assert result["rowCount"] == 1
    assert len(result["sha256"]) == 64
    with service.legacy_evidence_path.open(newline="", encoding="utf-8") as handle:
        row = next(csv.DictReader(handle))
    assert row == {
        "email": "member@example.com",
        "payment_rail": "PTMinder/EziDebit",
        "status": "collecting",
        "weekly_amount": "99.00",
        "last_receipt_date": "2026-07-22",
        "next_due_date": "2026-07-29",
        "notes": "Verified in PTMinder.",
    }
    assert service.legacy_evidence_status()["rowCount"] == 1


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("email", "not-an-email"),
        ("payment_rail", "Stripe"),
        ("status", "maybe"),
        ("weekly_amount", "zero"),
        ("last_receipt_date", "22/07/2026"),
    ],
)
def test_replace_legacy_evidence_rejects_invalid_rows(tmp_path, field, value):
    service = runtime(tmp_path)
    row = valid_row()
    row[field] = value

    with pytest.raises(ValueError):
        service.replace_legacy_evidence([row])


def test_replace_legacy_evidence_rejects_duplicate_email(tmp_path):
    service = runtime(tmp_path)
    row = valid_row()

    with pytest.raises(ValueError, match="duplicate email"):
        service.replace_legacy_evidence([row, row])
