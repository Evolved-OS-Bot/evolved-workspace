import json
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_membership_lifecycle_backfill import (
    build_backfill_payload,
)


def test_backfill_reuses_exact_dates_and_quarantines_ambiguity(tmp_path):
    database = tmp_path / "membership.sqlite"
    connection = sqlite3.connect(database)
    connection.executescript(
        """
        CREATE TABLE runs (
            run_id TEXT,
            started_at TEXT,
            finished_at TEXT,
            status TEXT
        );
        CREATE TABLE identity_register (
            run_id TEXT,
            identity_key TEXT,
            membership_type TEXT,
            membership_stage TEXT,
            cancellation_status TEXT,
            cancellation_type TEXT,
            notice_end_date TEXT,
            final_access_date TEXT
        );
        """
    )
    connection.execute(
        "INSERT INTO runs VALUES (?, ?, ?, ?)",
        (
            "run-1",
            "2026-07-30T00:00:00+00:00",
            "2026-07-30T01:00:00+00:00",
            "complete",
        ),
    )
    connection.executemany(
        "INSERT INTO identity_register VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        [
            (
                "run-1",
                "ended@example.com",
                "Strong",
                "Strong",
                "Cancelled",
                "Membership",
                "2026-07-24",
                "2026-07-24",
            ),
            (
                "run-1",
                "ambiguous@example.com",
                "Strong",
                "Strong",
                "Notice Active",
                "Membership",
                "2026-08-10",
                None,
            ),
            (
                "run-1",
                "fast@example.com",
                "Fast Track",
                "Fast Track",
                "Notice Active",
                "PT",
                "2026-07-25",
                "2026-07-25",
            ),
        ],
    )
    connection.commit()
    connection.close()
    cohort = tmp_path / "cohort.json"
    cohort.write_text(
        json.dumps(
            {
                "complete": True,
                "as_of_date": "2026-07-02",
                "rule_version": "cohort-v1",
                "source_refs": {"membership": "run-0"},
                "rows": [
                    {
                        "canonical_key": "ended@example.com",
                        "confirmed_active": True,
                    },
                    {
                        "canonical_key": "fast@example.com",
                        "confirmed_active": True,
                    },
                ],
            }
        )
    )

    payload = build_backfill_payload(
        membership_database=database,
        cohort_snapshots=[cohort],
        observed_at=datetime(2026, 7, 30, tzinfo=UTC),
    )

    assert payload["summary"] == {
        "records": 3,
        "accepted_exact_date_candidates": 2,
        "quarantined_ambiguous_candidates": 1,
        "opening_cohorts": 1,
    }
    by_person = {
        row["canonical_key"]: row for row in payload["records"]
    }
    assert by_person["ended@example.com"]["event_type"] == (
        "membership_ended"
    )
    assert by_person["fast@example.com"]["event_type"] == "downgrade_only"
    assert by_person["ambiguous@example.com"]["ambiguous_date"] is True
    assert payload["opening_cohorts"][0]["coverage_complete"] is True
