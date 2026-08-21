import sqlite3
from pathlib import Path
from types import SimpleNamespace

import pytest

from reporting_control.hub_roster_client import (
    build_roster_candidate,
    build_roster_candidate_from_records,
    promote_roster_candidate_payload,
)


def make_database(path: Path) -> None:
    connection = sqlite3.connect(path)
    connection.executescript(
        """
        CREATE TABLE runs (
            run_id TEXT PRIMARY KEY,
            status TEXT NOT NULL,
            completed_at TEXT
        );
        CREATE TABLE roster_snapshot (
            run_id TEXT NOT NULL,
            service TEXT NOT NULL,
            source_row INTEGER NOT NULL,
            email TEXT,
            status TEXT,
            classification TEXT,
            product TEXT,
            trainer TEXT,
            session_length TEXT,
            sessions_per_week TEXT,
            weekly_allocation TEXT,
            payment_marker TEXT,
            contract_length TEXT,
            renewal_date TEXT
        );
        INSERT INTO runs VALUES (
            'run-1', 'complete', '2026-07-28T10:00:00+00:00'
        );
        INSERT INTO roster_snapshot VALUES
            ('run-1', 'SGPT', 2, 'member@example.com',
             'Active', 'CLEAN_COLLECTING', 'Strong',
             NULL, NULL, NULL, '99', '99', '12 months', '2027-07-28'),
            ('run-1', 'PT', 3, 'member@example.com',
             'Active', 'CLEAN_COLLECTING', 'PT',
             'Piper Mae', '30 mins', '2', '120', '120', NULL, NULL),
            ('run-1', 'SGPT', 4, 'arrears@example.com',
             'Active - ARREARS', 'ARREARS', 'Strong',
             NULL, NULL, NULL, '99', '99', NULL, NULL);
        """
    )
    connection.commit()
    connection.close()


def test_build_roster_candidate_is_exact_and_excludes_arrears(tmp_path):
    database = tmp_path / "revenue.sqlite"
    make_database(database)

    payload = build_roster_candidate(database)

    assert payload["source_run_id"] == "run-1"
    assert len(payload["rows"]) == 1
    assert payload["rows"][0]["canonical_key"] == "member@example.com"
    assert [
        service["service_type"]
        for service in payload["rows"][0]["services"]
    ] == ["PT", "SGPT"]


def test_build_roster_candidate_fails_closed_without_identity(tmp_path):
    database = tmp_path / "revenue.sqlite"
    make_database(database)
    connection = sqlite3.connect(database)
    connection.execute(
        """
        INSERT INTO roster_snapshot VALUES
        ('run-1', 'PT', 5, '', 'Active', 'CLEAN_COLLECTING', 'PT',
         'Piper Mae', '30 mins', '2', '120', '120', NULL, NULL)
        """
    )
    connection.commit()
    connection.close()

    with pytest.raises(ValueError, match="exact governed identity"):
        build_roster_candidate(database)


def test_build_roster_candidate_from_live_records_applies_alias(tmp_path):
    aliases = tmp_path / "identity-links.csv"
    aliases.write_text(
        "canonical_email,linked_email\n"
        "member@example.com,old@example.com\n",
        encoding="utf-8",
    )
    roster = [
        SimpleNamespace(
            service="SGPT",
            status="Active",
            email="old@example.com",
            row_number=2,
            product="Strong",
            weekly_allocation=99,
            payment_marker="99",
        ),
        SimpleNamespace(
            service="PT",
            status="Active",
            email="member@example.com",
            row_number=3,
            product="PT",
            trainer="Piper Mae",
            session_length="30 mins",
            sessions_per_week="2",
            weekly_allocation=120,
            payment_marker="120",
        ),
    ]

    payload = build_roster_candidate_from_records(
        roster,
        source_run_id="live-1",
        observed_at="2026-07-28T10:00:00+10:00",
        identity_links_path=aliases,
    )

    assert len(payload["rows"]) == 1
    assert payload["rows"][0]["canonical_key"] == "member@example.com"
    assert len(payload["rows"][0]["services"]) == 2
    pt = next(
        item
        for item in payload["rows"][0]["services"]
        if item["service_type"] == "PT"
    )
    assert pt["assigned_trainer"] == "Piper Mae"
    assert pt["contracted_weekly_frequency"] == "2"
    assert pt["service_duration"] == "30 mins"
    assert pt["weekly_allocation"] == "120"
    assert pt["allocation_basis"] == "weekly_recurring"


def test_prepaid_roster_relationship_retains_non_numeric_allocation_basis():
    roster = [
        SimpleNamespace(
            service="PT",
            status="Active",
            email="member@example.com",
            row_number=2,
            product="PT",
            trainer="Piper Mae",
            session_length="30 mins",
            sessions_per_week="2",
            weekly_allocation=None,
            payment_marker="PIF",
        )
    ]

    payload = build_roster_candidate_from_records(
        roster,
        source_run_id="live-prepaid-1",
        observed_at="2026-08-02T12:00:00+10:00",
    )
    service = payload["rows"][0]["services"][0]

    assert service["weekly_allocation"] is None
    assert service["allocation_currency"] is None
    assert service["payment_marker"] == "PIF"
    assert service["allocation_basis"] == "prepaid"


class Response:
    status_code = 200

    def raise_for_status(self):
        return None

    def json(self):
        return {"status": "accepted"}


def test_promote_roster_candidate_derives_governance_endpoint(monkeypatch):
    monkeypatch.setenv(
        "HUB_SOURCE_BASE_URL", "https://hub/api/v1/sources"
    )
    monkeypatch.setenv("HUB_WEBHOOK_SECRET", "secret")
    captured = {}

    def post(url, headers, json, timeout):
        captured.update(
            url=url, headers=headers, json=json, timeout=timeout
        )
        return Response()

    monkeypatch.setattr(
        "reporting_control.hub_roster_client.requests.post", post
    )

    result = promote_roster_candidate_payload("candidate-1")

    assert result == {"status": "accepted"}
    assert captured["url"] == (
        "https://hub/api/v1/governance/promote-roster-candidate"
    )
    assert captured["json"] == {
        "expected_snapshot_id": "candidate-1"
    }
