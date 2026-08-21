#!/usr/bin/env python3
"""Prepare and reconcile logged Trainerize account-state audit batches."""

from __future__ import annotations

import argparse
import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRIVATE_DIR = ROOT / "data" / "private" / "trainerize-longitudinal-audit"
DATABASE = PRIVATE_DIR / "trainerize_longitudinal.sqlite"
CANDIDATES = PRIVATE_DIR / "reactivation_candidates.json"
PRIORITY_CANDIDATES = PRIVATE_DIR / "reactivation_priority_longitudinal.json"


def now() -> str:
    return datetime.now(UTC).isoformat()


def build_priority(connection: sqlite3.Connection, output_path: Path) -> None:
    """Write former members with unrecovered detail and >=120 days of history."""
    rows = connection.execute(
        """
        WITH workout_coverage AS (
            SELECT
                c.trainerize_user_id,
                c.first_name,
                c.last_name,
                c.email,
                c.created_at,
                COUNT(*) AS tracked_workouts,
                COUNT(DISTINCT ci.calendar_date) AS workout_days,
                MIN(ci.calendar_date) AS first_workout_date,
                MAX(ci.calendar_date) AS last_workout_date,
                CAST(
                    julianday(MAX(ci.calendar_date)) -
                    julianday(MIN(ci.calendar_date)) AS INT
                ) AS span_days
            FROM clients c
            JOIN calendar_items ci
              ON ci.trainerize_user_id=c.trainerize_user_id
            WHERE c.status='deactivated'
              AND c.is_test_client=0
              AND ci.item_type='workoutRegular'
              AND ci.status='tracked'
              AND NOT EXISTS (
                  SELECT 1 FROM daily_workouts dw
                  WHERE dw.trainerize_user_id=c.trainerize_user_id
              )
            GROUP BY c.trainerize_user_id
        )
        SELECT *,
            CASE
                WHEN span_days >= 600 THEN '24-month potential'
                WHEN span_days >= 300 THEN '12-month potential'
                ELSE '6-month potential'
            END AS priority_tier
        FROM workout_coverage
        WHERE span_days >= 120
        ORDER BY
            CASE
                WHEN span_days >= 600 THEN 1
                WHEN span_days >= 300 THEN 2
                ELSE 3
            END,
            tracked_workouts DESC,
            trainerize_user_id
        """
    ).fetchall()
    candidates = [dict(row) for row in rows]
    payload = {
        "generated_at": now(),
        "definition": (
            "Deactivated non-test clients with tracked workout history spanning "
            "at least 120 days and no recovered detailed workouts."
        ),
        "candidate_count": len(candidates),
        "candidates": candidates,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    output_path.chmod(0o600)
    tiers: dict[str, int] = {}
    for candidate in candidates:
        tier = str(candidate["priority_tier"])
        tiers[tier] = tiers.get(tier, 0) + 1
    print(json.dumps({"prepared_candidates": len(candidates), "tiers": tiers, "file": str(output_path)}))


def prepare(
    connection: sqlite3.Connection,
    start: int,
    count: int,
    source_results: Path | None = None,
    candidates_path: Path = CANDIDATES,
) -> None:
    all_candidates = json.loads(candidates_path.read_text())["candidates"]
    if source_results:
        selected_ids = {
            int(row["trainerize_user_id"])
            for row in json.loads(source_results.read_text())["results"]
            if row.get("success", True)
        }
        candidates = [
            row for row in all_candidates
            if int(row["trainerize_user_id"]) in selected_ids
        ]
    else:
        candidates = all_candidates[start : start + count]
    if not candidates:
        raise SystemExit("No candidates selected")
    unrestored = connection.execute(
        "SELECT COUNT(*) FROM account_state_changes WHERE restored_at IS NULL"
    ).fetchone()[0]
    if unrestored:
        raise SystemExit("Refusing to prepare a new batch while an earlier change is unrestored")
    suffix = f"retry_{datetime.now(UTC).strftime('%Y%m%dT%H%M%S')}" if source_results else f"{start:03d}_{start + len(candidates) - 1:03d}"
    batch_path = PRIVATE_DIR / f"reactivation_batch_{suffix}.json"
    batch_path.write_text(json.dumps({"candidates": candidates}, indent=2) + "\n")
    timestamp = now()
    for candidate in candidates:
        connection.execute(
            """
            INSERT INTO account_state_changes (
                trainerize_user_id, original_status, temporary_status,
                changed_at, verification_status, notes
            ) VALUES (?, 'deactivated', 'basic', ?, 'prepared_not_changed', ?)
            """,
            (
                int(candidate["trainerize_user_id"]),
                timestamp,
                f"Batch {batch_path.name}; temporary historical audit access",
            ),
        )
    connection.commit()
    print(json.dumps({"prepared": len(candidates), "batch": str(batch_path)}))


def apply_results(connection: sqlite3.Connection, results_path: Path, stage: str) -> None:
    items = json.loads(results_path.read_text())["results"]
    timestamp = now()
    successes = 0
    failures = 0
    for item in items:
        user_id = int(item["trainerize_user_id"])
        success = bool(item.get("success"))
        detail = str(item.get("detail") or "")[:300]
        if stage == "reactivated":
            verified_unchanged = (not success) and "Still deactivated" in detail
            verification = (
                "reactivated_basic_verified"
                if success
                else "not_changed_deactivated_verified"
                if verified_unchanged
                else "reactivation_failed"
            )
            connection.execute(
                """
                UPDATE account_state_changes
                SET changed_at=?,
                    restored_at=CASE WHEN ? THEN ? ELSE restored_at END,
                    verification_status=?, notes=notes || ?
                WHERE id=(
                    SELECT id FROM account_state_changes
                    WHERE trainerize_user_id=? AND restored_at IS NULL
                    ORDER BY id DESC LIMIT 1
                )
                """,
                (
                    timestamp,
                    verified_unchanged,
                    timestamp,
                    verification,
                    f"; {detail}",
                    user_id,
                ),
            )
            if success:
                connection.execute(
                    "UPDATE clients SET status='basic', updated_at=? WHERE trainerize_user_id=?",
                    (timestamp, user_id),
                )
        else:
            verification = "restored_deactivated_verified" if success else "restoration_failed"
            connection.execute(
                """
                UPDATE account_state_changes
                SET restored_at=CASE WHEN ? THEN ? ELSE restored_at END,
                    verification_status=?, notes=notes || ?
                WHERE id=(
                    SELECT id FROM account_state_changes
                    WHERE trainerize_user_id=? AND restored_at IS NULL
                    ORDER BY id DESC LIMIT 1
                )
                """,
                (success, timestamp, verification, f"; {detail}", user_id),
            )
            if success:
                connection.execute(
                    "UPDATE clients SET status='deactivated', updated_at=? WHERE trainerize_user_id=?",
                    (timestamp, user_id),
                )
        successes += int(success)
        failures += int(not success)
    connection.commit()
    print(json.dumps({"stage": stage, "successes": successes, "failures": failures}))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("build-priority", "prepare", "apply-results"))
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--count", type=int, default=10)
    parser.add_argument("--results", type=Path)
    parser.add_argument("--stage", choices=("reactivated", "restored"))
    parser.add_argument("--candidates-file", type=Path, default=CANDIDATES)
    parser.add_argument("--output", type=Path, default=PRIORITY_CANDIDATES)
    args = parser.parse_args()
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    try:
        if args.action == "build-priority":
            build_priority(connection, args.output)
        elif args.action == "prepare":
            prepare(
                connection,
                args.start,
                args.count,
                args.results,
                candidates_path=args.candidates_file,
            )
        else:
            if not args.results or not args.stage:
                parser.error("apply-results requires --results and --stage")
            apply_results(connection, args.results, args.stage)
    finally:
        connection.close()


if __name__ == "__main__":
    main()
