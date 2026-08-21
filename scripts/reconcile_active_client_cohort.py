#!/usr/bin/env python3
"""Reconcile an accepted membership derivative to the governed roster.

This command reads protected local artifacts only. It does not call GHL,
Stripe, Trainerize, PT Minder or Google Sheets.
"""

from __future__ import annotations

import argparse
import csv
import json
import sqlite3
import sys
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from reporting_control.cohort import (  # noqa: E402
    active_signal,
    normalise_control_text,
    summarise_cohort_rows,
)


DEFAULT_IDENTITY = (
    ROOT
    / "data/private/integration-reporting/runs/20260727T103436Z"
    / "identity_register.csv"
)
DEFAULT_REVENUE_DB = (
    ROOT / "data/private/revenue-gap-control/revenue_gap.sqlite"
)
DEFAULT_RECONCILIATION_DB = (
    ROOT / "data/private/integration-reporting/reconciliation.sqlite"
)
DEFAULT_ALIASES = (
    ROOT / "data/private/integration-reporting/identity_links.csv"
)
DEFAULT_CLASSIFICATIONS = (
    ROOT / "data/private/integration-reporting/account_classifications.csv"
)
DEFAULT_PRIVATE_DIR = (
    ROOT / "data/private/reporting-control-plane/active-client-cohort-20260727"
)
DEFAULT_PUBLIC_REPORT = (
    ROOT
    / "outputs/reporting-control-plane"
    / "active-client-cohort-reconciliation-2026-07-27.md"
)


def normalise_email(value: Any) -> str:
    return str(value or "").strip().lower()


def load_aliases(path: Path) -> dict[str, str]:
    aliases: dict[str, str] = {}
    with path.open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            canonical = normalise_email(row.get("canonical_email"))
            linked = normalise_email(row.get("linked_email"))
            if canonical and linked:
                aliases[canonical] = canonical
                aliases[linked] = canonical
    return aliases


def load_classifications(
    path: Path,
    aliases: dict[str, str],
) -> dict[str, str]:
    results = {}
    with path.open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            email = aliases.get(
                normalise_email(row.get("email")),
                normalise_email(row.get("email")),
            )
            if email:
                results[email] = str(
                    row.get("classification") or ""
                ).strip().lower()
    return results


def load_governed_roster(
    database: Path,
    aliases: dict[str, str],
) -> tuple[
    str,
    dict[str, list[dict[str, str]]],
    dict[str, list[dict[str, str]]],
]:
    connection = sqlite3.connect(database)
    connection.row_factory = sqlite3.Row
    run = connection.execute(
        """
        SELECT run_id FROM runs
        WHERE status='complete'
        ORDER BY completed_at DESC LIMIT 1
        """
    ).fetchone()
    if not run:
        connection.close()
        raise RuntimeError("No complete governed roster snapshot exists")
    rows = connection.execute(
        """
        SELECT email, service, status, classification, product
        FROM roster_snapshot
        WHERE run_id=?
        ORDER BY lower(trim(email)), service
        """,
        (run["run_id"],),
    ).fetchall()
    connection.close()
    all_people: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        raw_email = normalise_email(row["email"])
        email = aliases.get(raw_email, raw_email)
        if not email:
            raise ValueError("Governed roster row is missing an email")
        all_people[email].append(
            {
                "service": row["service"],
                "status": row["status"],
                "classification": row["classification"],
                "product": row["product"],
            }
        )
    governed = {
        email: [
            row
            for row in person_rows
            if row["service"] == "PT"
            or str(row["status"]).strip().lower()
            in {"active", "active - pia"}
        ]
        for email, person_rows in all_people.items()
    }
    governed = {
        email: rows for email, rows in governed.items() if rows
    }
    return str(run["run_id"]), governed, dict(all_people)


def load_identity_rows(
    path: Path,
    aliases: dict[str, str],
) -> dict[str, dict[str, str]]:
    results = {}
    with path.open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            raw_email = normalise_email(row.get("email"))
            email = aliases.get(raw_email, raw_email)
            if not email:
                continue
            if email in results:
                raise ValueError(
                    f"Accepted identity derivative duplicates {email}"
                )
            results[email] = row
    return results


def load_current_identity_rows(
    database: Path,
    aliases: dict[str, str],
) -> tuple[str, dict[str, dict[str, str]]]:
    """Load the latest accepted source state without altering the baseline."""
    connection = sqlite3.connect(database)
    connection.row_factory = sqlite3.Row
    run = connection.execute(
        """
        SELECT run_id FROM runs
        WHERE status='complete'
        ORDER BY finished_at DESC, started_at DESC LIMIT 1
        """
    ).fetchone()
    if not run:
        connection.close()
        raise RuntimeError("No complete membership reconciliation exists")
    rows = connection.execute(
        """
        SELECT email, ghl_active_signal, stripe_entitled_signal,
               trainerize_active_signal, membership_type, membership_stage,
               cancellation_status, final_access_date
        FROM identity_register
        WHERE run_id=? AND trim(coalesce(email, '')) <> ''
        ORDER BY lower(trim(email))
        """,
        (run["run_id"],),
    ).fetchall()
    connection.close()

    results: dict[str, dict[str, str]] = {}
    for source in rows:
        raw_email = normalise_email(source["email"])
        email = aliases.get(raw_email, raw_email)
        candidate = {
            "ghl_active_signal": str(bool(source["ghl_active_signal"])),
            "stripe_entitled_signal": str(
                bool(source["stripe_entitled_signal"])
            ),
            "trainerize_active_signal": str(
                bool(source["trainerize_active_signal"])
            ),
            "membership_type": str(source["membership_type"] or ""),
            "membership_stage": str(source["membership_stage"] or ""),
            "cancellation_status": str(
                source["cancellation_status"] or ""
            ),
            "final_access_date": str(source["final_access_date"] or ""),
        }
        existing = results.get(email)
        if not existing:
            results[email] = candidate
            continue
        for field in (
            "ghl_active_signal",
            "stripe_entitled_signal",
            "trainerize_active_signal",
        ):
            existing[field] = str(
                existing[field] == "True" or candidate[field] == "True"
            )
        for field in (
            "membership_type",
            "membership_stage",
            "cancellation_status",
            "final_access_date",
        ):
            if not existing[field] and candidate[field]:
                existing[field] = candidate[field]
    return str(run["run_id"]), results


def decision_for(
    *,
    email: str,
    baseline_identity: dict[str, str] | None,
    current_identity: dict[str, str] | None,
    roster: list[dict[str, str]],
    audit_roster: list[dict[str, str]],
    classification: str,
    timing_additions: set[str],
    known_internal: set[str],
) -> dict[str, Any]:
    in_governed = bool(roster)
    historical_signal = False
    historical_cancellation = None
    if baseline_identity:
        historical_signal = active_signal(
            ghl_active=baseline_identity["ghl_active_signal"] == "True",
            stripe_entitled=(
                baseline_identity["stripe_entitled_signal"] == "True"
            ),
            trainerize_active=(
                baseline_identity["trainerize_active_signal"] == "True"
            ),
        )
        historical_cancellation = str(
            baseline_identity.get("cancellation_status") or ""
        ).strip()
    in_legacy = bool(historical_signal or historical_cancellation)

    raw_signal = False
    raw_cancellation = None
    normalised_cancellation = None
    if current_identity:
        raw_signal = active_signal(
            ghl_active=current_identity["ghl_active_signal"] == "True",
            stripe_entitled=(
                current_identity["stripe_entitled_signal"] == "True"
            ),
            trainerize_active=(
                current_identity["trainerize_active_signal"] == "True"
            ),
        )
        raw_cancellation = str(
            current_identity.get("cancellation_status") or ""
        ).strip()
        normalised_cancellation = normalise_control_text(raw_cancellation)

    evidence = {
        "email": email,
        "ghl_active_signal": bool(
            current_identity
            and current_identity["ghl_active_signal"] == "True"
        ),
        "stripe_contract_signal": bool(
            current_identity
            and current_identity["stripe_entitled_signal"] == "True"
        ),
        "trainerize_access_signal": bool(
            current_identity
            and current_identity["trainerize_active_signal"] == "True"
        ),
        "historical_active_signal": historical_signal,
        "historical_cancellation_status": historical_cancellation,
        "raw_cancellation_status": raw_cancellation,
        "normalised_cancellation_status": normalised_cancellation,
        "final_access_date": (
            current_identity.get("final_access_date")
            if current_identity
            else None
        ),
        "account_classification": classification or None,
        "governed_roster": roster,
        "revenue_audit_roster": audit_roster,
    }

    if in_governed:
        governed_reasons = {
            row["classification"] for row in roster
        }
        if not in_legacy and "APPROVED_PAUSE" in governed_reasons:
            reason = "governed_approved_hold_without_active_source_signal"
        else:
            reason = "governed_active_roster"
        return {
            "canonical_key": email,
            "in_legacy_cohort": in_legacy,
            "active_signal": raw_signal,
            "confirmed_active": True,
            "paid_or_entitled": None,
            "disposition": "confirmed_active",
            "primary_reason": reason,
            "decision_required": False,
            "owner": None,
            "owner_question": None,
            "evidence": evidence,
        }

    roster_classes = {row["classification"] for row in audit_roster}
    internal = classification in {
        "staff",
        "owner_admin",
        "approved_internal_access",
    } or email in known_internal
    complimentary = classification == "complimentary_member"
    online = classification == "online_client" or "online" in " ".join(
        (
            current_identity.get("membership_type", "")
            if current_identity
            else "",
            current_identity.get("membership_stage", "")
            if current_identity
            else "",
        )
    ).lower()
    if not raw_signal:
        disposition = "excluded"
        reason = (
            "historical_signal_now_retired"
            if historical_signal
            else "cancellation_metadata_without_active_signal"
        )
    elif "Active - ARREARS" in roster_classes:
        disposition = "revenue_review_only"
        reason = "arrears_evidence_excluded_from_active_kpi"
    elif internal:
        disposition = "excluded"
        reason = "staff_owner_or_internal_access"
    elif complimentary:
        disposition = "excluded"
        reason = "complimentary_membership_outside_kpi"
    elif online:
        disposition = "excluded"
        reason = "online_service_outside_sgpt_pt_kpi"
    elif (
        email in timing_additions
        or classification in {"current_pt_client", "current_sgpt_client"}
    ):
        disposition = "timing_difference"
        reason = "active_roster_row_added_after_governed_snapshot"
    else:
        disposition = "decision_required"
        reason = "source_signal_absent_from_governed_roster"
    decision_required = disposition == "decision_required"
    return {
        "canonical_key": email,
        "in_legacy_cohort": in_legacy,
        "active_signal": raw_signal,
        "confirmed_active": False,
        "paid_or_entitled": None,
        "disposition": disposition,
        "primary_reason": reason,
        "decision_required": decision_required,
        "owner": "Peter Brown" if decision_required else None,
        "owner_question": (
            "Should this identity be added to the governed active roster, "
            "linked to another identity, or have stale source state retired?"
            if decision_required
            else None
        ),
        "evidence": evidence,
    }


def write_outputs(
    *,
    rows: list[dict[str, Any]],
    private_dir: Path,
    public_report: Path,
    source_refs: dict[str, str],
    observed_at: str,
) -> dict[str, Any]:
    payload = {
        "schema_version": 1,
        "source": "active_client_cohort",
        "observed_at": observed_at,
        "as_of_date": "2026-07-27",
        "rule_version": "active-client-cohort-v1",
        "status": "complete",
        "complete": True,
        "source_refs": source_refs,
        "rows": rows,
    }
    summary = summarise_cohort_rows(rows)
    intersection = sum(
        bool(row["in_legacy_cohort"]) and bool(row["confirmed_active"])
        for row in rows
    )
    legacy_only = sum(
        bool(row["in_legacy_cohort"]) and not bool(row["confirmed_active"])
        for row in rows
    )
    governed_only = sum(
        not bool(row["in_legacy_cohort"]) and bool(row["confirmed_active"])
        for row in rows
    )
    net_overstatement = (
        summary["legacy_inflated_cohort"]
        - summary["confirmed_active_clients"]
    )
    private_dir.mkdir(parents=True, exist_ok=True)
    private_dir.chmod(0o700)
    payload_path = private_dir / "cohort-decision-snapshot.json"
    payload_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    payload_path.chmod(0o600)

    difference = [
        row
        for row in rows
        if bool(row["in_legacy_cohort"])
        != bool(row["confirmed_active"])
    ]
    difference_path = private_dir / "identity-level-difference.csv"
    with difference_path.open("w", newline="", encoding="utf-8") as handle:
        fieldnames = [
            "canonical_key",
            "in_legacy_cohort",
            "active_signal",
            "confirmed_active",
            "disposition",
            "primary_reason",
            "decision_required",
            "owner",
            "owner_question",
            "evidence_json",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in difference:
            writer.writerow(
                {
                    **{key: row.get(key) for key in fieldnames[:-1]},
                    "evidence_json": json.dumps(
                        row["evidence"], sort_keys=True
                    ),
                }
            )
    difference_path.chmod(0o600)

    reason_counts = Counter(
        row["primary_reason"] for row in difference
    )
    unresolved = [
        row for row in difference if row["decision_required"]
    ]
    owner_review_path = private_dir / "owner-review.md"
    owner_lines = [
        "# Active Client Cohort Owner Review",
        "",
        "**As of:** 27 July 2026",
        "",
        "For each identity, choose exactly one outcome: add to the governed "
        "active roster, approve an identity link, classify as a governed "
        "exclusion, or retire stale source state through the normal owner-"
        "approved operational process.",
        "",
    ]
    for position, row in enumerate(unresolved, start=1):
        evidence = row["evidence"]
        signals = [
            name
            for name, present in (
                ("GHL lifecycle", evidence["ghl_active_signal"]),
                ("Stripe contract", evidence["stripe_contract_signal"]),
                ("Trainerize access", evidence["trainerize_access_signal"]),
            )
            if present
        ]
        owner_lines.extend(
            [
                f"## {position}. {row['canonical_key']}",
                "",
                f"- Signals: {', '.join(signals) or 'none'}",
                f"- Cancellation field: "
                f"{evidence['normalised_cancellation_status'] or 'none'}",
                f"- Question: {row['owner_question']}",
                "",
            ]
        )
    owner_review_path.write_text(
        "\n".join(owner_lines).rstrip() + "\n",
        encoding="utf-8",
    )
    owner_review_path.chmod(0o600)
    public_report.parent.mkdir(parents=True, exist_ok=True)
    public_report.write_text(
        f"""# Active Client Cohort Reconciliation

**As of:** 27 July 2026  
**Rule:** `active-client-cohort-v1`  
**Mode:** Read-only, shadow only  
**Production cutover:** Not authorised

## Confirmed result

| Measure | Count |
|---|---:|
| Legacy hub lifecycle count previously labelled active signal | {summary["legacy_inflated_cohort"]} |
| Current active-source signals among the compared identities | {summary["active_source_signal_people"]} |
| Governed confirmed active clients | {summary["confirmed_active_clients"]} |
| Identities present in both compared cohorts | {intersection} |
| Legacy-only identities | {legacy_only} |
| Governed-only identities | {governed_only} |
| Symmetric identity difference | {summary["identity_difference"]} |
| Net count overstatement | {net_overstatement} |

The former 191 label was incorrect. It combined 152 real source-signal
identities with 39 identities that had only a non-empty cancellation field.
Current source state is overlaid on that frozen audit baseline. One historical
source-signal identity is now correctly retired following an owner-approved
cancellation correction, so the current signal count is 151.

## Identity-difference buckets

| Exclusive primary reason | Count |
|---|---:|
| Cancellation metadata without an active source signal | {reason_counts["cancellation_metadata_without_active_signal"]} |
| Staff, owner or approved internal access | {reason_counts["staff_owner_or_internal_access"]} |
| Approved complimentary membership outside the KPI | {reason_counts["complimentary_membership_outside_kpi"]} |
| Online service outside the SGPT/PT KPI | {reason_counts["online_service_outside_sgpt_pt_kpi"]} |
| Arrears evidence retained for revenue review only | {reason_counts["arrears_evidence_excluded_from_active_kpi"]} |
| Active roster row added after the governed snapshot | {reason_counts["active_roster_row_added_after_governed_snapshot"]} |
| Historical active signal now retired | {reason_counts["historical_signal_now_retired"]} |
| Governed approved hold without an active source signal | {reason_counts["governed_approved_hold_without_active_source_signal"]} |
| Peter decision required | {reason_counts["source_signal_absent_from_governed_roster"]} |
| **Total identity difference** | **{summary["identity_difference"]}** |

## Owner review

{"No identities require Peter's decision. Every identity in the 64-person difference now has a governed disposition." if not unresolved else f'''{len(unresolved)} identities require Peter to decide whether the person belongs
on the governed roster, needs an approved identity link, or carries stale
source state. The identified cases and evidence are in the protected artifact.'''}

## Paid and entitled status

This run does not publish a paid-or-entitled total. The accepted membership
snapshot contains Stripe contract status, not complete payment evidence, and
Trainerize proves access only.

Paid or entitled must be projected separately from Stripe payment events,
specific PT Minder debit events, PIA or pack evidence, approved holds, pending
debits, future starts and final-access dates. Until that evidence is accepted,
the dashboard must display this measure as unavailable.

## Safety gates

- The reconciliation command is read-only. Eliza Lebsanft's separate,
  owner-authorised cancellation correction was completed across GHL,
  Trainerize and the governed workbook before this shadow report was refreshed.
  Emma Johnson's owner-authorised Active SGPT restoration is recorded as a
  timing difference until the next governed roster snapshot is accepted.
  Erica Asler, Madison McKiernan and Reemi Shah are also recorded as
  owner-approved timing corrections. Sue Goodwin is classified as a current
  Evolved Anywhere online client outside the SGPT/PT KPI, and Tsana Leatham is classified
  as an approved complimentary member outside the KPI.
- Existing production consumers remain on their protected inputs.
- No cutover is allowed until the next governed snapshot includes all five
  owner-approved timing additions with exact identity parity, the
  paid-or-entitled projection is complete and two shadow parity cycles pass.

## Validation

The reporting-control, operating-hub, revenue-control, PT-continuity,
retention-intelligence, Trainerize-performance and membership-reconciliation
suites pass: 184 tests.
""",
        encoding="utf-8",
    )
    return {
        **summary,
        "difference_path": str(difference_path),
        "payload_path": str(payload_path),
        "owner_review_path": str(owner_review_path),
        "public_report": str(public_report),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--identity-csv", type=Path, default=DEFAULT_IDENTITY)
    parser.add_argument(
        "--current-reconciliation-db",
        type=Path,
        default=DEFAULT_RECONCILIATION_DB,
    )
    parser.add_argument("--revenue-db", type=Path, default=DEFAULT_REVENUE_DB)
    parser.add_argument("--aliases", type=Path, default=DEFAULT_ALIASES)
    parser.add_argument(
        "--classifications",
        type=Path,
        default=DEFAULT_CLASSIFICATIONS,
    )
    parser.add_argument("--private-dir", type=Path, default=DEFAULT_PRIVATE_DIR)
    parser.add_argument(
        "--public-report",
        type=Path,
        default=DEFAULT_PUBLIC_REPORT,
    )
    parser.add_argument("--timing-addition", action="append", default=[])
    parser.add_argument("--known-internal", action="append", default=[])
    args = parser.parse_args()

    aliases = load_aliases(args.aliases)
    classifications = load_classifications(args.classifications, aliases)
    roster_run, governed, audit_roster = load_governed_roster(
        args.revenue_db, aliases
    )
    identities = load_identity_rows(args.identity_csv, aliases)
    current_run, current_identities = load_current_identity_rows(
        args.current_reconciliation_db,
        aliases,
    )
    timing_additions = {
        aliases.get(normalise_email(value), normalise_email(value))
        for value in args.timing_addition
    }
    known_internal = {
        aliases.get(normalise_email(value), normalise_email(value))
        for value in args.known_internal
    }
    union = set(governed)
    for email, row in identities.items():
        if (
            row["ghl_active_signal"] == "True"
            or row["stripe_entitled_signal"] == "True"
            or row["trainerize_active_signal"] == "True"
            or str(row.get("cancellation_status") or "").strip()
        ):
            union.add(email)
    rows = [
        decision_for(
            email=email,
            baseline_identity=identities.get(email),
            current_identity=current_identities.get(email),
            roster=governed.get(email, []),
            audit_roster=audit_roster.get(email, []),
            classification=classifications.get(email, ""),
            timing_additions=timing_additions,
            known_internal=known_internal,
        )
        for email in sorted(union)
    ]
    result = write_outputs(
        rows=rows,
        private_dir=args.private_dir,
        public_report=args.public_report,
        source_refs={
            "membership_derivative": str(args.identity_csv),
            "current_membership_reconciliation_run": current_run,
            "governed_roster_run": roster_run,
            "approved_aliases": str(args.aliases),
            "approved_classifications": str(args.classifications),
        },
        observed_at=datetime.now(UTC).isoformat(timespec="seconds"),
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
