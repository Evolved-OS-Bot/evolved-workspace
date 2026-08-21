import json
import sqlite3

from reporting_control.current_people_client import CurrentPeopleContract
from revenue_gap_control.hub_contract import (
    _legacy_allocation_state,
    build_hub_audit_sources,
    compare_revenue_run,
    hub_revenue_projection,
    revenue_roster_contract_complete,
)


def test_revenue_projection_keeps_lifecycle_service_entitlement_and_payment_separate():
    projection = hub_revenue_projection(
        {
            "lifecycle": {"status": "active"},
            "service_relationships": [
                {"service_type": "sgpt", "status": "active"},
                {
                    "service_type": "personal_training",
                    "status": "active",
                },
            ],
            "entitlements": [
                {
                    "service_type": "sgpt",
                    "status": "confirmed",
                    "current": True,
                }
            ],
            "payment_accounts": [
                {"current_evidence_state": "collecting"}
            ],
        }
    )
    assert projection == {
        "lifecycle_status": "active",
        "service_types": ["personal_training", "sgpt"],
        "entitlement_services": ["sgpt"],
        "payment_states": ["collecting"],
        "roster_relationships": [],
        "roster_attributes_complete": False,
        "decision_required": False,
    }


def test_unresolved_lifecycle_fails_closed_even_with_payment():
    projection = hub_revenue_projection(
        {
            "lifecycle": {
                "status": "review_required",
                "missing_reason": "GHL conflict",
            },
            "service_relationships": [],
            "entitlements": [],
            "payment_accounts": [{"status": "active"}],
        }
    )
    assert projection["decision_required"] is True
    assert projection["service_types"] == []


def _contract(
    *,
    complete: bool = True,
    prepaid: bool = False,
) -> CurrentPeopleContract:
    missing = [] if complete else ["allocation_evidence"]
    return CurrentPeopleContract(
        schema_version=1,
        contract_version="current-person-v1",
        mode="shadow",
        generated_at="2026-08-02T00:00:00+00:00",
        period={
            "period_id": "week",
            "start": "2026-07-20",
            "end": "2026-07-26",
            "timezone": "Australia/Brisbane",
        },
        source_freshness=(),
        complete=True,
        blocked_reasons=(),
        rows=(
            {
                "person_id": "person-1",
                "display": {
                    "email": "member@example.com",
                    "first_name": "Eve",
                    "last_name": "Member",
                },
                "source_identities": [
                    {
                        "source": "ghl",
                        "source_record_id": "contact-1",
                    },
                    {
                        "source": "trainerize",
                        "source_record_id": "trainerize-1",
                    },
                ],
                "lifecycle": {"status": "active"},
                "service_relationships": [
                    {
                        "service_type": "personal_training",
                        "service_name": "PT",
                        "status": "active",
                        "source": "active_client_cohort",
                        "governed_roster_attributes": {
                            "complete": complete,
                            "attributes": {
                                "product": "PT",
                                "assigned_trainer": "Piper",
                                "contracted_weekly_frequency": "2",
                                "service_duration": "30 min",
                                "weekly_allocation": (
                                    None
                                    if prepaid
                                    else ("100" if complete else None)
                                ),
                                "allocation_currency": (
                                    None if prepaid else "AUD"
                                ),
                                "allocation_basis": (
                                    "prepaid"
                                    if prepaid
                                    else "weekly_recurring"
                                ),
                                "allocation_evidence_status": (
                                    "confirmed_prepaid_entitlement"
                                    if prepaid
                                    else (
                                        "confirmed_weekly_amount"
                                        if complete
                                        else "unresolved"
                                    )
                                ),
                                "weekly_allocation_applicable": (
                                    not prepaid
                                ),
                                "payment_marker": (
                                    "PIF" if prepaid else "100"
                                ),
                                "contract_length": "20 weeks",
                            },
                            "missing_attributes": missing,
                            "effective_from": "2026-07-01",
                            "effective_to": "2026-12-01",
                            "source_snapshot_id": "roster-v2-1",
                        },
                    }
                ],
                "entitlements": [
                    {
                        "service_type": "personal_training",
                        "status": "confirmed",
                    }
                ],
                "payment_accounts": [
                    {
                        "status": "active",
                        "latest_event_evidence": [
                            {
                                "status": "completed",
                                "occurred_on": "2026-07-25",
                            }
                        ],
                    }
                ],
                "governed_cohort": {"confirmed_active": True},
            },
        ),
        response_fingerprint="f" * 64,
    )


def test_schema_v2_roster_attributes_build_person_keyed_audit_inputs():
    contract = _contract()

    assert revenue_roster_contract_complete(contract) is True
    sources = build_hub_audit_sources(contract)

    assert sources.source_run_id == "f" * 64
    assert sources.contact_to_email == {
        "contact-1": "member@example.com"
    }
    assert len(sources.roster) == 1
    roster = sources.roster[0]
    assert roster.service == "PT"
    assert roster.weekly_allocation == 100
    assert roster.session_cost == 50
    assert roster.trainer == "Piper"
    assert sources.evidence_by_email[
        "member@example.com"
    ].latest_invoice_paid is True
    assert sources.evidence_by_email[
        "member@example.com"
    ].raw["hub_person_id"] == "person-1"


def test_incomplete_roster_attributes_fail_closed():
    contract = _contract(complete=False)

    assert revenue_roster_contract_complete(contract) is False
    try:
        build_hub_audit_sources(contract)
    except ValueError as exc:
        assert "incomplete" in str(exc)
    else:
        raise AssertionError("incomplete Hub roster must fail closed")


def test_confirmed_prepaid_entitlement_is_complete_without_weekly_amount():
    contract = _contract(prepaid=True)

    projection = hub_revenue_projection(contract.rows[0])
    relationship = projection["roster_relationships"][0]
    assert projection["roster_attributes_complete"] is True
    assert relationship["allocation_basis"] == "prepaid"
    assert (
        relationship["allocation_evidence_status"]
        == "confirmed_prepaid_entitlement"
    )
    assert relationship["weekly_allocation"] == ""
    assert relationship["weekly_allocation_applicable"] is False

    sources = build_hub_audit_sources(contract)
    roster = sources.roster[0]
    assert roster.weekly_allocation is None
    assert roster.payment_marker == "PIF"
    assert roster.session_cost is None


def test_legacy_pt_prepaid_requires_commercial_classification():
    marker_only = _legacy_allocation_state(
        service="personal_training",
        status="Active",
        payment_marker="PIF",
        weekly_allocation=None,
        renewal_date=None,
        commercial_classification="",
    )
    classified = _legacy_allocation_state(
        service="personal_training",
        status="Active",
        payment_marker="PIF",
        weekly_allocation=None,
        renewal_date=None,
        commercial_classification="PIF_PACK_IN_DELIVERY",
    )

    assert marker_only == (
        "prepaid",
        "prepaid_marker_without_confirmed_entitlement",
        False,
    )
    assert classified == (
        "prepaid",
        "confirmed_prepaid_entitlement",
        False,
    )


def test_legacy_alias_rows_are_aggregated_by_hub_person_id(tmp_path):
    database = tmp_path / "revenue.sqlite"
    connection = sqlite3.connect(database)
    connection.executescript(
        """
        CREATE TABLE client_identity (
            run_id TEXT, email TEXT, ghl_contact_ids_json TEXT
        );
        CREATE TABLE lifecycle_evidence (
            run_id TEXT, email TEXT, cancellation_status TEXT,
            final_access_date TEXT
        );
        CREATE TABLE payment_evidence (
            run_id TEXT, email TEXT, stripe_statuses_json TEXT,
            latest_invoice_paid INTEGER
        );
        CREATE TABLE roster_snapshot (
            run_id TEXT, email TEXT, service TEXT, product TEXT,
            status TEXT, payment_marker TEXT,
            classification TEXT,
            trainer TEXT, sessions_per_week TEXT, session_length TEXT,
            weekly_allocation TEXT, contract_length TEXT,
            renewal_date TEXT
        );
        """
    )
    for email in ("member@example.com", "alias@example.com"):
        connection.execute(
            "INSERT INTO client_identity VALUES (?, ?, ?)",
            ("run-1", email, json.dumps(["contact-1"])),
        )
        connection.execute(
            "INSERT INTO lifecycle_evidence VALUES (?, ?, ?, ?)",
            ("run-1", email, "", ""),
        )
        connection.execute(
            "INSERT INTO payment_evidence VALUES (?, ?, ?, ?)",
            ("run-1", email, json.dumps(["active"]), 1),
        )
    connection.execute(
        "INSERT INTO roster_snapshot VALUES "
        "(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            "run-1",
            "member@example.com",
            "PT",
            "PT",
            "Active",
            "100",
            "CLEAN_COLLECTING",
            "Piper",
            "2",
            "30 min",
            "100",
            "20 weeks",
            "2026-12-01",
        ),
    )
    connection.commit()
    connection.close()

    parity = compare_revenue_run(
        database,
        run_id="run-1",
        contract=_contract(),
    )

    assert parity.legacy_count == 1
    assert parity.hub_count == 1


def test_non_roster_source_identities_are_excluded_from_revenue_parity(
    tmp_path,
):
    database = tmp_path / "revenue.sqlite"
    connection = sqlite3.connect(database)
    connection.executescript(
        """
        CREATE TABLE client_identity (
            run_id TEXT, email TEXT, ghl_contact_ids_json TEXT
        );
        CREATE TABLE lifecycle_evidence (
            run_id TEXT, email TEXT, cancellation_status TEXT,
            final_access_date TEXT
        );
        CREATE TABLE payment_evidence (
            run_id TEXT, email TEXT, stripe_statuses_json TEXT,
            latest_invoice_paid INTEGER
        );
        CREATE TABLE roster_snapshot (
            run_id TEXT, email TEXT, service TEXT, product TEXT,
            status TEXT, payment_marker TEXT,
            classification TEXT,
            trainer TEXT, sessions_per_week TEXT, session_length TEXT,
            weekly_allocation TEXT, contract_length TEXT,
            renewal_date TEXT
        );
        """
    )
    connection.execute(
        "INSERT INTO client_identity VALUES (?, ?, ?)",
        ("run-1", "member@example.com", json.dumps(["contact-1"])),
    )
    connection.execute(
        "INSERT INTO client_identity VALUES (?, ?, ?)",
        ("run-1", "lead@example.com", json.dumps(["contact-2"])),
    )
    connection.execute(
        "INSERT INTO lifecycle_evidence VALUES (?, ?, ?, ?)",
        ("run-1", "member@example.com", "", ""),
    )
    connection.execute(
        "INSERT INTO payment_evidence VALUES (?, ?, ?, ?)",
        ("run-1", "member@example.com", json.dumps(["active"]), 1),
    )
    connection.execute(
        "INSERT INTO roster_snapshot VALUES "
        "(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            "run-1",
            "member@example.com",
            "PT",
            "PT",
            "Active",
            "100",
            "CLEAN_COLLECTING",
            "Piper",
            "2",
            "30 min",
            "100",
            "20 weeks",
            "2026-12-01",
        ),
    )
    connection.commit()
    connection.close()

    parity = compare_revenue_run(
        database,
        run_id="run-1",
        contract=_contract(),
    )

    assert parity.legacy_count == 1
    assert parity.hub_count == 1
    assert not parity.missing_from_hub
    assert not parity.missing_from_legacy
