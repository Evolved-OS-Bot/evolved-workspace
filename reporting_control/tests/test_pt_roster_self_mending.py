from reporting_control.pt_roster_self_mending import (
    build_pt_roster_self_mending_shadow,
)


SALES_HEADER = [
    "Date",
    "First Name",
    "Last Name",
    "Mobile",
    "Email",
    "Source",
    "Product",
    "Salesperson",
    "Trainer Assigned",
    "Cash Taken",
    "Added to Trainerize",
    "Evolved Allstars",
    "Add-On Program",
    "Meal Plan Given",
    "Session Credits",
    "Onboarding Session Booked",
    "Onboarding Session Complete",
    "Debits Set Up",
]
ACTIVE_HEADER = [
    "1:1",
    "First Name",
    "Last Name",
    "Phone",
    "Email",
    "Personal Trainer",
    "Session Length",
    "Sessions p/wk",
    "$$$",
    "Weekly Debit",
    "Rebook",
]


def membership(
    *,
    lifecycle_status="active",
    trainerize_active=True,
    pt_block_trainer=None,
):
    return {
        "snapshot_id": "membership-1",
        "payload": {
            "rows": [
                {
                    "email": "erica.asler@gmail.com",
                    "lifecycle_status": lifecycle_status,
                    "final_access_date": None,
                    "trainerize_active": trainerize_active,
                    "pt_block_trainer": pt_block_trainer,
                }
            ]
        },
    }


def commercial(*, include_payment=True):
    row = {
        "email": "erica.asler@gmail.com",
        "entitlements": [],
        "payment_accounts": [],
        "payment_events": [],
    }
    if include_payment:
        row["entitlements"] = [
            {
                "service_type": "personal_training",
                "status": "confirmed",
                "effective_from": "2026-07-27",
                "effective_to": "2026-08-03",
            }
        ]
        row["payment_accounts"] = [
            {
                "status": "collecting",
                "weekly_amount": "60.00",
            }
        ]
        row["payment_events"] = [
            {
                "service_type": "personal_training",
                "status": "completed",
                "occurred_on": "2026-07-27",
                "coverage_start": "2026-07-27",
                "coverage_end": "2026-08-03",
                "amount": "60.00",
                "source_event_id": "in_erica",
            }
        ]
    return {"snapshot_id": "stripe-1", "payload": {"rows": [row]}}


def prepaid_pack_commercial():
    return {
        "snapshot_id": "stripe-pack-1",
        "payload": {
            "rows": [
                {
                    "email": "erica.asler@gmail.com",
                    "entitlements": [
                        {
                            "service_type": "personal_training",
                            "status": "confirmed",
                            "effective_from": "2026-07-11",
                            "effective_to": None,
                            "unit": "prepaid pack",
                            "basis": (
                                "approved_payment_to_contact_pack_map"
                            ),
                        }
                    ],
                    "payment_accounts": [
                        {
                            "status": "paid_in_advance",
                            "weekly_amount": None,
                        }
                    ],
                    "payment_events": [
                        {
                            "service_type": "personal_training",
                            "status": "completed",
                            "occurred_on": "2026-07-11",
                            "amount": "2400.00",
                            "source_event_id": "pi_pack",
                        }
                    ],
                }
            ]
        },
    }


def purchased_term_commercial():
    return {
        "snapshot_id": "revenue-control-1",
        "payload": {
            "rows": [
                {
                    "email": "erica.asler@gmail.com",
                    "entitlements": [
                        {
                            "service_type": "personal_training",
                            "status": "confirmed",
                            "effective_from": "2026-07-13",
                            "effective_to": "2026-08-09",
                            "quantity": "4",
                            "unit": "30-minute sessions",
                            "basis": (
                                "revenue_control_governed_"
                                "purchased_service_term"
                            ),
                        }
                    ],
                    "payment_accounts": [],
                    "payment_events": [],
                }
            ]
        },
    }


def approved_hold_commercial():
    return {
        "snapshot_id": "revenue-control-hold-1",
        "payload": {
            "rows": [
                {
                    "email": "erica.asler@gmail.com",
                    "entitlements": [
                        {
                            "service_type": "personal_training",
                            "status": "pending",
                            "basis": (
                                "revenue_control_assessment:"
                                "APPROVED_PAUSE"
                            ),
                        }
                    ],
                    "payment_accounts": [],
                    "payment_events": [],
                }
            ]
        },
    }


def sales_row(**overrides):
    values = {
        "Date": "27/7/2026",
        "First Name": "Erica",
        "Last Name": "Asler",
        "Mobile": "0468 789 281",
        "Email": "erica.asler@gmail.com",
        "Source": "Website Organic",
        "Product": "PT 30M x 1",
        "Salesperson": "Megan",
        "Trainer Assigned": "Megan",
        "Cash Taken": "$60.00",
        "Added to Trainerize": "TRUE",
        "Debits Set Up": "TRUE",
    }
    values.update(overrides)
    return [values.get(column, "") for column in SALES_HEADER]


def active_row(**overrides):
    values = {
        "1:1": "27/7/2026",
        "First Name": "Erica",
        "Last Name": "Asler",
        "Phone": "0468 789 281",
        "Email": "erica.asler@gmail.com",
        "Personal Trainer": "Megan",
        "Session Length": "30 mins",
        "Sessions p/wk": "1",
        "$$$": "$60.00",
        "Weekly Debit": "$60.00",
        "Rebook": "",
    }
    values.update(overrides)
    return [values.get(column, "") for column in ACTIVE_HEADER]


def build(
    sales,
    active,
    member=None,
    payments=None,
    pt_minder_snapshot=None,
):
    return build_pt_roster_self_mending_shadow(
        sales_rows=[SALES_HEADER, *sales],
        active_pt_rows=[ACTIVE_HEADER, *active],
        membership_snapshot=member or membership(),
        commercial_snapshots=[payments or commercial()],
        observed_at="2026-07-29T06:20:00+10:00",
        pt_minder_snapshot=pt_minder_snapshot,
    )


def test_erica_complete_pair_is_confirmed_without_patch():
    result = build([sales_row()], [active_row()])

    assert result["summary"]["confirmed_current_pt"] == 1
    assert result["summary"]["proposed_patches"] == 0
    assert result["cases"][0]["reason"] == "complete"


def test_current_prepaid_pack_does_not_require_weekly_debit_terms():
    result = build(
        [
            sales_row(
                **{
                    "Product": "PT 45M 20PK",
                    "Trainer Assigned": (
                        "Nora Silva / Piper Mae"
                    ),
                    "Cash Taken": "$1,800.00",
                    "Debits Set Up": "FALSE",
                }
            )
        ],
        [
            active_row(
                **{
                    "Personal Trainer": "Nora Silva / Piper Mae",
                    "Session Length": "60 mins",
                    "Sessions p/wk": "",
                    "$$$": "",
                    "Weekly Debit": "PIF",
                }
            )
        ],
        payments=prepaid_pack_commercial(),
    )

    assert result["summary"]["confirmed_current_pt"] == 1
    assert result["summary"]["pending_terms"] == 0
    assert result["summary"]["proposed_patches"] == 0
    assert result["cases"][0]["reason"] == "complete"


def test_governed_purchased_term_does_not_require_recurring_debit_setup():
    result = build(
        [
            sales_row(
                **{
                    "Product": "Silver",
                    "Cash Taken": "$599.00",
                    "Debits Set Up": "FALSE",
                }
            )
        ],
        [active_row(**{"Weekly Debit": "$50.00"})],
        payments=purchased_term_commercial(),
    )

    assert result["summary"]["confirmed_current_pt"] == 1
    assert result["summary"]["pending_provisioning"] == 0
    assert result["cases"][0]["reason"] == "complete"


def test_approved_pause_is_a_protected_hold_not_failed_provisioning():
    result = build(
        [sales_row()],
        [active_row()],
        payments=approved_hold_commercial(),
    )

    assert result["summary"]["pending_provisioning"] == 0
    assert result["summary"]["approved_holds"] == 1
    assert result["cases"][0]["state"] == "approved_hold"
    assert result["cases"][0]["reason"] == "approved_payment_hold"


def test_incomplete_pair_proposes_only_allowlisted_evidence_backed_cells():
    result = build(
        [
            sales_row(
                **{
                    "Product": "",
                    "Trainer Assigned": "",
                    "Cash Taken": "",
                    "Added to Trainerize": "",
                    "Debits Set Up": "",
                }
            )
        ],
        [
            active_row(
                **{
                    "Session Length": "",
                    "Sessions p/wk": "",
                    "$$$": "",
                    "Weekly Debit": "",
                }
            )
        ],
    )

    patches = {
        (patch["sheet"], patch["column"]): patch["proposed"]
        for patch in result["cases"][0]["proposed_patches"]
    }
    assert patches == {
        ("Sales", "Trainer Assigned"): "Megan",
        ("Sales", "Cash Taken"): "$60.00",
        ("Sales", "Added to Trainerize"): "TRUE",
        ("Sales", "Debits Set Up"): "TRUE",
        ("Active PT", "Weekly Debit"): "$60.00",
    }
    assert all(
        patch["write_enabled"] is False
        for patch in result["cases"][0]["proposed_patches"]
    )
    assert {
        patch["column"]: patch["approval_status"]
        for patch in result["cases"][0]["proposed_patches"]
    } == {
        "Trainer Assigned": "manual_evidence_required",
        "Cash Taken": "eligible_for_owner_approval",
        "Added to Trainerize": "eligible_for_owner_approval",
        "Debits Set Up": "eligible_for_owner_approval",
        "Weekly Debit": "eligible_for_owner_approval",
    }
    assert result["cases"][0]["state"] == "pending_terms"


def test_duplicate_active_rows_are_quarantined_without_patch():
    result = build(
        [
            sales_row(),
            sales_row(**{"Product": "", "Cash Taken": ""}),
        ],
        [
            active_row(),
            active_row(**{"Session Length": "", "Sessions p/wk": ""}),
        ],
    )

    assert result["summary"]["exceptions"] == 1
    assert result["cases"][0]["reason"] == "duplicate_roster_rows"
    assert result["cases"][0]["proposed_patches"] == []
    assert result["cases"][0]["duplicate_analysis"] == {
        "active_pt": {
            "status": "strict_incomplete_repeat",
            "preserve_row": 2,
            "quarantine_row": 3,
            "conflicting_columns": [],
            "write_enabled": False,
        },
        "sales": {
            "status": "strict_incomplete_repeat",
            "preserve_row": 2,
            "quarantine_row": 3,
            "conflicting_columns": [],
            "write_enabled": False,
        },
        "resolution_status": "dominant_pair_identified",
        "write_enabled": False,
    }
    assert result["summary"]["duplicate_dominant_pairs_identified"] == 1


def test_paid_invoice_cannot_reactivate_cancelled_lifecycle():
    result = build(
        [sales_row()],
        [active_row()],
        member=membership(lifecycle_status="cancelled"),
    )

    assert result["cases"][0]["reason"] == (
        "cancelled_or_final_access_ended"
    )
    assert result["cases"][0]["proposed_patches"] == []


def test_trainerize_access_alone_does_not_propose_cash_or_debits():
    result = build(
        [
            sales_row(
                **{
                    "Cash Taken": "",
                    "Added to Trainerize": "",
                    "Debits Set Up": "",
                }
            )
        ],
        [active_row()],
        payments=commercial(include_payment=False),
    )

    patches = result["cases"][0]["proposed_patches"]
    assert {(patch["sheet"], patch["column"]) for patch in patches} == {
        ("Sales", "Added to Trainerize")
    }
    assert result["cases"][0]["reason"] == "missing_payment_evidence"


def test_false_provisioning_flags_are_corrected_only_with_source_evidence():
    result = build(
        [
            sales_row(
                **{
                    "Added to Trainerize": "FALSE",
                    "Debits Set Up": "FALSE",
                }
            )
        ],
        [active_row()],
    )

    patches = {
        patch["column"]: (patch["current"], patch["proposed"])
        for patch in result["cases"][0]["proposed_patches"]
    }
    assert patches == {
        "Added to Trainerize": ("FALSE", "TRUE"),
        "Debits Set Up": ("FALSE", "TRUE"),
    }


def test_boolean_false_is_preserved_in_patch_audit_value():
    result = build(
        [
            sales_row(
                **{
                    "Added to Trainerize": False,
                    "Debits Set Up": False,
                }
            )
        ],
        [active_row()],
    )

    patches = {
        patch["column"]: patch["current"]
        for patch in result["cases"][0]["proposed_patches"]
    }
    assert patches == {
        "Added to Trainerize": "FALSE",
        "Debits Set Up": "FALSE",
    }


def test_ghl_pt_block_trainer_preserves_shared_assignment_for_sales_projection():
    result = build(
        [sales_row(**{"Trainer Assigned": ""})],
        [active_row(**{"Personal Trainer": "Cover Coach"})],
        member=membership(
            pt_block_trainer="Katrina Parsons / Piper Mae"
        ),
    )

    patch = result["cases"][0]["proposed_patches"][0]
    assert patch["column"] == "Trainer Assigned"
    assert patch["proposed"] == "Katrina Parsons / Piper Mae"
    assert patch["evidence"] == "GHL PT Block Trainer"
    assert patch["approval_status"] == "eligible_for_owner_approval"


def test_shadow_never_proposes_row_creation_or_deletion():
    result = build([], [active_row()])

    assert result["cases"][0]["reason"] == "missing_sales_history"
    assert result["cases"][0]["sales_linkage"] == "absent"
    assert result["summary"]["row_creations_proposed"] == 0
    assert result["summary"]["row_deletions_proposed"] == 0


def test_historical_sales_row_is_distinguished_from_absent_history():
    result = build(
        [sales_row(Date="20/7/2026")],
        [active_row()],
    )

    case = result["cases"][0]
    assert case["state"] == "historical_sales_link"
    assert case["reason"] == "pt_sales_history_on_different_date"
    assert case["sales_linkage"] == "historical_only"
    assert case["sales_rows"] == [2]
    assert result["summary"]["historical_sales_links"] == 1
    assert result["summary"]["absent_sales_history"] == 0


def test_service_before_sales_ledger_is_not_a_missing_sales_exception():
    result = build(
        [],
        [active_row(**{"1:1": "1/7/2025"})],
    )

    case = result["cases"][0]
    assert case["state"] == "legacy_sales_history_unavailable"
    assert case["reason"] == "service_predates_sales_ledger"
    assert case["sales_linkage"] == "legacy_not_expected"
    assert result["summary"]["exceptions"] == 0
    assert result["summary"]["legacy_sales_history_unavailable"] == 1
    assert result["summary"]["absent_sales_history"] == 0


def test_future_service_start_is_not_a_missing_sales_exception():
    result = build(
        [],
        [active_row(**{"1:1": "3/8/2026"})],
    )

    case = result["cases"][0]
    assert case["state"] == "future_start"
    assert case["reason"] == "service_not_yet_effective"
    assert case["sales_linkage"] == "not_due"
    assert result["summary"]["exceptions"] == 0
    assert result["summary"]["future_starts"] == 1


def test_pt_minder_pt_payment_explains_missing_sales_row():
    result = build(
        [],
        [active_row(**{"1:1": "30/6/2026"})],
        pt_minder_snapshot={
            "snapshot_id": "pt-minder-1",
            "payload": {
                "rows": [
                    {
                        "email": "erica.asler@gmail.com",
                        "transactions": [
                            {
                                "amount": "120.00",
                                "occurred_on": "2026-06-30",
                                "service_type": "personal_training",
                                "source_transaction_id": "ezi-2841886",
                                "status": "completed",
                            },
                            {
                                "amount": "60.00",
                                "occurred_on": "2026-07-22",
                                "service_type": "personal_training",
                                "source_transaction_id": "ezi-2857491",
                                "status": "completed",
                            }
                        ],
                    }
                ]
            },
        },
    )

    case = result["cases"][0]
    assert case["state"] == "pt_minder_payment_link"
    assert case["reason"] == "pt_minder_payment_without_sales_row"
    assert case["sales_linkage"] == "payment_evidence_only"
    assert case["payment_evidence"]["transaction_id"] == "ezi-2841886"
    assert result["summary"]["exceptions"] == 0
    assert result["summary"]["pt_minder_payment_links"] == 1
    assert result["summary"]["absent_sales_history"] == 0


def test_summary_separates_exact_absent_and_duplicate_linkage():
    duplicate = active_row(Email="duplicate@example.com")
    result = build(
        [sales_row()],
        [
            active_row(),
            active_row(
                Email="missing@example.com",
                **{"1:1": "1/7/2025"},
            ),
            duplicate,
            duplicate,
        ],
    )

    assert result["schema_version"] == 7
    assert result["summary"]["exact_sales_links"] == 1
    assert result["summary"]["legacy_sales_history_unavailable"] == 1
    assert result["summary"]["absent_sales_history"] == 0
    assert result["summary"]["duplicate_active_identities"] == 1


def test_summary_separates_authoritative_and_supporting_proposals():
    result = build(
        [sales_row(**{"Trainer Assigned": "", "Added to Trainerize": ""})],
        [active_row()],
    )

    assert result["summary"]["proposals_eligible_for_owner_approval"] == 1
    assert result["summary"]["proposals_requiring_manual_evidence"] == 1
