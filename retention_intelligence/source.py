from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from scripts import membership_reconciliation as reconciliation

from .config import Settings
from .models import MemberInput, UsageMetrics


def _normalise_email(value: Any) -> str:
    return str(value or "").strip().lower()


def local_or_configured_controls(settings: Settings) -> dict[str, Any]:
    identity_links = (
        settings.identity_links
        if settings.identity_links
        else reconciliation.load_identity_links()
    )
    return {
        "identity_links": identity_links,
        "identity_record_links": (
            settings.identity_record_links
            if settings.identity_record_links
            else reconciliation.load_identity_record_links()
        ),
        "account_classifications": reconciliation.canonicalise_control_keys(
            (
                settings.account_classifications
                if settings.account_classifications
                else reconciliation.load_account_classifications()
            ),
            identity_links,
        ),
        "authoritative_stripe_customers": reconciliation.canonicalise_control_keys(
            (
                settings.authoritative_stripe_customers
                if settings.authoritative_stripe_customers
                else reconciliation.load_authoritative_stripe_customers()
            ),
            identity_links,
        ),
    }


def run_source_reconciliation(settings: Settings) -> dict[str, Any]:
    path = Path(settings.reconciliation_database)
    path.parent.mkdir(parents=True, exist_ok=True)
    controls = local_or_configured_controls(settings)
    summary = reconciliation.run_reconciliation(
        database=path,
        fetch_invoices=False,
        **controls,
    )
    summary["account_classifications"] = controls["account_classifications"]
    return summary


def load_active_members(
    settings: Settings,
    usage: dict[int, UsageMetrics],
    account_classifications: dict[str, dict[str, Any]],
) -> tuple[str, list[MemberInput]]:
    connection = sqlite3.connect(settings.reconciliation_database)
    connection.row_factory = sqlite3.Row
    run_row = connection.execute(
        "SELECT run_id FROM runs WHERE status='complete' ORDER BY started_at DESC LIMIT 1"
    ).fetchone()
    if not run_row:
        connection.close()
        raise RuntimeError("No completed reconciliation run exists")
    run_id = str(run_row["run_id"])
    identity_rows = connection.execute(
        "SELECT * FROM identity_register WHERE run_id=?",
        (run_id,),
    ).fetchall()
    identities_by_trainerize_id: dict[int, sqlite3.Row] = {}
    for row in identity_rows:
        for raw_id in json.loads(row["trainerize_active_ids_json"] or "[]"):
            identities_by_trainerize_id[int(raw_id)] = row
    exception_ids = {
        str(row["identity_key"])
        for row in connection.execute(
            """
            SELECT identity_key FROM exceptions
            WHERE run_id=? AND severity IN ('critical', 'high', 'medium')
            """,
            (run_id,),
        ).fetchall()
    }
    roster = connection.execute(
        """
        SELECT * FROM trainerize_clients
        WHERE run_id=? AND roster_view='active'
        ORDER BY trainerize_user_id
        """,
        (run_id,),
    ).fetchall()
    connection.close()

    members: list[MemberInput] = []
    for row in roster:
        user_id = int(row["trainerize_user_id"])
        identity = identities_by_trainerize_id.get(user_id)
        raw = json.loads(row["raw_json"] or "{}")
        email = _normalise_email(row["email"])
        classification = account_classifications.get(
            str(identity["identity_key"]) if identity else email,
            account_classifications.get(email, {}),
        )
        service = None
        if identity:
            service = identity["membership_stage"] or identity["membership_type"]
        members.append(
            MemberInput(
                trainerize_user_id=user_id,
                email=email,
                first_name=str(row["first_name"] or ""),
                last_name=str(row["last_name"] or ""),
                service=str(service) if service else None,
                trainer_name=(
                    str(raw.get("trainerName") or raw.get("assignedTrainerName") or "")
                    or None
                ),
                created_date=str(raw.get("created") or raw.get("dateCreated") or "")
                or None,
                latest_signed_in=str(row["latest_signed_in"] or "") or None,
                ghl_active=bool(identity["ghl_active_signal"]) if identity else False,
                stripe_entitled=(
                    bool(identity["stripe_entitled_signal"]) if identity else False
                ),
                trainerize_active=True,
                cancellation_status=(
                    str(identity["cancellation_status"] or "") or None
                    if identity
                    else None
                ),
                final_access_date=(
                    str(identity["final_access_date"] or "") or None
                    if identity
                    else None
                ),
                account_classification=classification.get("classification"),
                has_operational_exception=(
                    str(identity["identity_key"]) in exception_ids
                    if identity
                    else True
                ),
                usage=usage.get(user_id, UsageMetrics()),
            )
        )
    return run_id, members


def active_user_ids(settings: Settings) -> list[int]:
    connection = sqlite3.connect(settings.reconciliation_database)
    row = connection.execute(
        "SELECT run_id FROM runs WHERE status='complete' ORDER BY started_at DESC LIMIT 1"
    ).fetchone()
    if not row:
        connection.close()
        raise RuntimeError("No completed reconciliation run exists")
    ids = [
        int(item[0])
        for item in connection.execute(
            """
            SELECT trainerize_user_id FROM trainerize_clients
            WHERE run_id=? AND roster_view='active'
            ORDER BY trainerize_user_id
            """,
            (str(row[0]),),
        ).fetchall()
    ]
    connection.close()
    return ids
