import json

from operating_data_hub.entitlement_queue import (
    build_entitlement_exception_queue,
    classify_gap,
    service_is_covered,
)


def test_service_coverage_requires_every_governed_service():
    assert service_is_covered("sgpt", {"fast_track"})
    assert service_is_covered("personal_training", {"personal_training"})
    assert service_is_covered("personal_training", {"fast_track"})


def test_current_purchased_service_term_covers_roster_service():
    queue = build_entitlement_exception_queue(
        governed_rows=[
            {
                "person_id": "person-1",
                "confirmed_active": 1,
                "as_of_date": "2026-07-27",
            }
        ],
        relationships=[
            {
                "person_id": "person-1",
                "service_type": "sgpt",
                "service_name": "SGPT",
                "metadata_json": json.dumps(
                    {
                        "classification": "NO_CURRENT_PAYMENT_EVIDENCE",
                        "status": "Active",
                    }
                ),
            }
        ],
        entitlement_rows=[
            {
                "person_id": "person-1",
                "source": "revenue_control",
                "status": "confirmed",
                "service_type": "sgpt",
                "effective_from": "2026-07-20",
                "effective_to": "2026-10-20",
                "metadata_json": json.dumps(
                    {
                        "basis": (
                            "revenue_control_governed_"
                            "purchased_service_term"
                        )
                    }
                ),
            }
        ],
        lifecycle_rows=[
            {
                "person_id": "person-1",
                "status": "active",
                "evidence_json": json.dumps({"ghl_active": True}),
            }
        ],
        people_rows=[],
    )

    assert queue["summary"]["service_gaps"] == 0


def test_future_and_expired_purchased_terms_are_distinct():
    governed = [
        {
            "person_id": f"person-{number}",
            "confirmed_active": 1,
            "as_of_date": "2026-07-27",
        }
        for number in (1, 2)
    ]
    relationships = [
        {
            "person_id": f"person-{number}",
            "service_type": "sgpt",
            "service_name": "SGPT",
            "metadata_json": json.dumps(
                {
                    "classification": "NO_CURRENT_PAYMENT_EVIDENCE",
                    "status": "Active",
                }
            ),
        }
        for number in (1, 2)
    ]
    entitlements = [
        {
            "person_id": "person-1",
            "source": "revenue_control",
            "status": "confirmed",
            "service_type": "sgpt",
            "effective_from": "2026-08-03",
            "effective_to": "2026-10-20",
            "metadata_json": json.dumps(
                {
                    "basis": (
                        "revenue_control_governed_"
                        "purchased_service_term"
                    )
                }
            ),
        },
        {
            "person_id": "person-2",
            "source": "revenue_control",
            "status": "confirmed",
            "service_type": "sgpt",
            "effective_from": "2026-04-01",
            "effective_to": "2026-07-20",
            "metadata_json": json.dumps(
                {
                    "basis": (
                        "revenue_control_governed_"
                        "purchased_service_term"
                    )
                }
            ),
        },
    ]
    lifecycle = [
        {
            "person_id": f"person-{number}",
            "status": "active",
            "evidence_json": json.dumps({"ghl_active": True}),
        }
        for number in (1, 2)
    ]

    queue = build_entitlement_exception_queue(
        governed_rows=governed,
        relationships=relationships,
        entitlement_rows=entitlements,
        lifecycle_rows=lifecycle,
        people_rows=[],
    )
    buckets = {
        bucket["code"]: bucket["service_gap_count"]
        for bucket in queue["buckets"]
    }

    assert buckets == {
        "purchased_service_term_expired": 1,
        "purchased_service_term_future": 1,
    }


def test_confirmed_future_entitlement_downgrades_payment_decision():
    queue = build_entitlement_exception_queue(
        governed_rows=[
            {
                "person_id": "person-1",
                "confirmed_active": 1,
                "as_of_date": "2026-07-27",
            }
        ],
        relationships=[
            {
                "person_id": "person-1",
                "service_type": "personal_training",
                "service_name": "PT",
                "metadata_json": json.dumps(
                    {
                        "classification": (
                            "PAYMENT_UNRESOLVED_WITH_FUTURE_BOOKING"
                        ),
                        "status": "Active",
                    }
                ),
            }
        ],
        entitlement_rows=[
            {
                "person_id": "person-1",
                "source": "stripe",
                "status": "confirmed",
                "service_type": "personal_training",
                "effective_from": "2026-07-28",
                "effective_to": "2026-08-04",
                "metadata_json": "{}",
            }
        ],
        lifecycle_rows=[
            {
                "person_id": "person-1",
                "status": "active",
                "evidence_json": json.dumps({"ghl_active": True}),
            }
        ],
        people_rows=[],
    )

    assert queue["buckets"][0]["code"] == (
        "confirmed_entitlement_starts_later"
    )
    assert queue["summary"]["high_priority_service_gaps"] == 0


def test_current_pt_minder_period_outranks_stale_retry():
    queue = build_entitlement_exception_queue(
        governed_rows=[
            {
                "person_id": "person-1",
                "confirmed_active": 1,
                "as_of_date": "2026-07-27",
            }
        ],
        relationships=[
            {
                "person_id": "person-1",
                "service_type": "personal_training",
                "service_name": "PT",
                "metadata_json": json.dumps(
                    {
                        "classification": (
                            "PAYMENT_UNRESOLVED_WITH_FUTURE_BOOKING"
                        ),
                        "status": "Active",
                    }
                ),
            }
        ],
        entitlement_rows=[],
        lifecycle_rows=[
            {
                "person_id": "person-1",
                "status": "active",
                "evidence_json": json.dumps({"ghl_active": True}),
            }
        ],
        people_rows=[],
        payment_account_rows=[
            {
                "person_id": "person-1",
                "source": "pt_minder",
                "status": "collecting",
            }
        ],
        payment_event_rows=[
            {
                "person_id": "person-1",
                "source": "pt_minder",
                "source_event_id": "current",
                "occurred_on": "2026-07-16",
                "status": "completed",
                "service_type": "fast_track",
                "cadence": "recurring",
                "description": "Silver Package (Fortnightly)",
                "coverage_start": "2026-07-16",
                "coverage_end": "2026-07-29",
            },
            {
                "person_id": "person-1",
                "source": "pt_minder",
                "source_event_id": "retry",
                "occurred_on": "2026-07-24",
                "status": "failed",
                "service_type": "fast_track",
                "cadence": "recurring",
                "description": "Silver Package (Fortnightly) retry",
                "coverage_start": "2026-03-12",
                "coverage_end": "2026-03-25",
            },
        ],
    )

    assert queue["buckets"][0]["code"] == "pt_minder_shadow_collecting"


def test_governed_pt_minder_override_routes_immutable_pt_label_as_sgpt():
    queue = build_entitlement_exception_queue(
        governed_rows=[
            {
                "person_id": "nirvana",
                "confirmed_active": 1,
                "as_of_date": "2026-07-27",
            }
        ],
        relationships=[
            {
                "person_id": "nirvana",
                "service_type": "sgpt",
                "service_name": "Strength and Sculpt",
                "metadata_json": json.dumps(
                    {
                        "classification": "NO_CURRENT_PAYMENT_EVIDENCE",
                        "status": "Active",
                    }
                ),
            }
        ],
        entitlement_rows=[],
        lifecycle_rows=[
            {
                "person_id": "nirvana",
                "status": "active",
                "evidence_json": json.dumps({"ghl_active": True}),
            }
        ],
        people_rows=[],
        payment_account_rows=[
            {
                "person_id": "nirvana",
                "source": "pt_minder",
                "status": "collecting",
            }
        ],
        payment_event_rows=[
            {
                "person_id": "nirvana",
                "source": "pt_minder",
                "source_event_id": "txn-1",
                "occurred_on": "2026-07-24",
                "coverage_start": "2026-07-24",
                "coverage_end": "2026-07-30",
                "status": "completed",
                "service_type": "sgpt",
                "cadence": "recurring",
                "description": "1:1 PT Leisa (2 x 30 mins)",
                "service_override_id": "override-1",
            }
        ],
    )

    assert queue["buckets"][0]["code"] == "pt_minder_shadow_collecting"


def test_gap_classification_is_fail_closed_and_purpose_aware():
    assert (
        classify_gap(
            classification="CLEAN_COLLECTING",
            roster_status="Active",
            lifecycle_status="review_required",
            ghl_active=True,
        )
        == "lifecycle_mismatch"
    )
    assert (
        classify_gap(
            classification="APPROVED_PAUSE",
            roster_status="Active",
            lifecycle_status="active",
            ghl_active=True,
        )
        == "approved_hold"
    )
    assert (
        classify_gap(
            classification="ACTIVE_PIA",
            roster_status="Active - PIA",
            lifecycle_status="active",
            ghl_active=True,
        )
        == "prepaid_or_pack"
    )
    assert (
        classify_gap(
            classification="Active - ARREARS",
            roster_status="Active",
            lifecycle_status="active",
            ghl_active=True,
        )
        == "arrears_retry"
    )
    assert (
        classify_gap(
            classification="ACTIVE_CONTRACT_RECEIPT_UNRESOLVED",
            roster_status="Active",
            lifecycle_status="active",
            ghl_active=True,
        )
        == "active_contract_receipt_unresolved"
    )
    assert (
        classify_gap(
            classification="PAYMENT_UNRESOLVED_WITH_FUTURE_BOOKING",
            roster_status="Active",
            lifecycle_status="active",
            ghl_active=True,
        )
        == "payment_unresolved_with_future_booking"
    )
    assert (
        classify_gap(
            classification="NO_CURRENT_PAYMENT_EVIDENCE",
            roster_status="Active",
            lifecycle_status="active",
            ghl_active=True,
        )
        == "no_current_payment_evidence"
    )


def test_queue_counts_clients_and_service_gaps_separately():
    governed = [
        {"person_id": "person-1", "confirmed_active": 1},
        {"person_id": "person-2", "confirmed_active": 1},
    ]
    relationships = [
        {
            "person_id": "person-1",
            "service_type": "sgpt",
            "service_name": "Fast Track",
            "metadata_json": json.dumps(
                {
                    "classification": "CLEAN_COLLECTING",
                    "status": "Active",
                }
            ),
        },
        {
            "person_id": "person-1",
            "service_type": "personal_training",
            "service_name": "Fast Track",
            "metadata_json": json.dumps(
                {
                    "classification": "BOOKING_PAYMENT_UNRESOLVED",
                    "status": "Active",
                }
            ),
        },
        {
            "person_id": "person-2",
            "service_type": "sgpt",
            "service_name": "Bronze",
            "metadata_json": json.dumps(
                {
                    "classification": "APPROVED_PAUSE",
                    "status": "Active",
                }
            ),
        },
    ]
    commercial = [
        {
            "person_id": "person-1",
            "source": "stripe",
            "service_type": "sgpt",
            "status": "confirmed",
        }
    ]
    lifecycle = [
        {
            "person_id": "person-1",
            "status": "active",
            "evidence_json": '{"ghl_active":true}',
        },
        {
            "person_id": "person-2",
            "status": "active",
            "evidence_json": '{"ghl_active":true}',
        },
    ]
    people = [
        {
            "person_id": "person-1",
            "canonical_key": "one@example.com",
            "email": "one@example.com",
        },
        {
            "person_id": "person-2",
            "canonical_key": "two@example.com",
            "email": "two@example.com",
        },
    ]

    aggregate = build_entitlement_exception_queue(
        governed_rows=governed,
        relationships=relationships,
        entitlement_rows=commercial,
        lifecycle_rows=lifecycle,
        people_rows=people,
    )
    identified = build_entitlement_exception_queue(
        governed_rows=governed,
        relationships=relationships,
        entitlement_rows=commercial,
        lifecycle_rows=lifecycle,
        people_rows=people,
        identified=True,
    )

    assert aggregate["summary"]["clients_pending"] == 2
    assert aggregate["summary"]["service_gaps"] == 2
    assert "email" not in str(aggregate)
    assert "one@example.com" in str(identified)


def test_latest_revenue_assessment_overrides_stale_roster_bucket():
    queue = build_entitlement_exception_queue(
        governed_rows=[
            {"person_id": "person-1", "confirmed_active": True}
        ],
        relationships=[
            {
                "person_id": "person-1",
                "service_type": "sgpt",
                "service_name": "SGPT",
                "metadata_json": (
                    '{"classification":"CLEAN_COLLECTING",'
                    '"status":"Active"}'
                ),
            }
        ],
        entitlement_rows=[
            {
                "person_id": "person-1",
                "service_type": "sgpt",
                "source": "revenue_control",
                "status": "pending",
                "metadata_json": (
                    '{"basis":"revenue_control_assessment:'
                    'BOOKING_PAYMENT_UNRESOLVED"}'
                ),
            }
        ],
        lifecycle_rows=[
            {
                "person_id": "person-1",
                "status": "active",
                "evidence_json": '{"ghl_active":true}',
            }
        ],
        people_rows=[
            {
                "person_id": "person-1",
                "canonical_key": "one@example.com",
                "email": "one@example.com",
            }
        ],
    )

    assert queue["buckets"][0]["code"] == (
        "payment_booking_unresolved"
    )


def test_no_payment_bucket_routes_available_payment_evidence():
    people = [
        {
            "person_id": f"person-{position}",
            "canonical_key": f"{position}@example.com",
            "email": f"{position}@example.com",
        }
        for position in range(1, 8)
    ]
    governed = [
        {
            "person_id": row["person_id"],
            "confirmed_active": True,
            "as_of_date": "2026-08-02",
        }
        for row in people
    ]
    relationships = [
        {
            "person_id": row["person_id"],
            "service_type": "sgpt",
            "service_name": "Bronze",
            "metadata_json": (
                '{"classification":"NO_CURRENT_PAYMENT_EVIDENCE",'
                '"status":"Active"}'
            ),
        }
        for row in people
    ]
    lifecycle = [
        {
            "person_id": row["person_id"],
            "status": "active",
            "evidence_json": '{"ghl_active":true}',
        }
        for row in people
    ]
    accounts = [
        {
            "person_id": "person-1",
            "source": "pt_minder",
            "status": "collecting",
        },
        {
            "person_id": "person-2",
            "source": "pt_minder",
            "status": "collecting",
        },
        {
            "person_id": "person-3",
            "source": "stripe",
            "status": "cancelled",
        },
        {
            "person_id": "person-4",
            "source": "stripe",
            "status": "paused",
        },
        {
            "person_id": "person-5",
            "source": "pt_minder",
            "status": "collecting",
        },
        {
            "person_id": "person-6",
            "source": "stripe",
            "status": "cancelled",
        },
        {
            "person_id": "person-7",
            "source": "stripe",
            "status": "cancelled",
        },
    ]
    events = [
        {
            "person_id": "person-1",
            "source": "pt_minder",
            "source_event_id": "one",
            "occurred_on": "2026-07-25",
            "status": "pending",
            "service_type": "personal_training",
            "cadence": "recurring",
            "description": "SGPT (LIMITED 2 PER WEEK) recurring payment",
        },
        {
            "person_id": "person-2",
            "source": "pt_minder",
            "source_event_id": "two",
            "occurred_on": "2026-07-24",
            "status": "failed",
            "service_type": "other",
            "cadence": "recurring",
            "description": "Silver Package (Fortnightly) recurring payment",
        },
        {
            "person_id": "person-3",
            "source": "stripe",
            "source_event_id": "three",
            "occurred_on": "2026-07-20",
            "status": "completed",
            "service_type": "sgpt",
            "cadence": "recurring",
            "description": "Stripe invoice",
            "coverage_start": "2026-06-20",
            "coverage_end": "2026-07-20",
        },
        {
            "person_id": "person-4",
            "source": "stripe",
            "source_event_id": "four",
            "occurred_on": "2026-07-14",
            "status": "completed",
            "service_type": "sgpt",
            "cadence": "recurring",
            "description": "Stripe invoice",
        },
        {
            "person_id": "person-5",
            "source": "pt_minder",
            "source_event_id": "five",
            "occurred_on": "2026-07-24",
            "status": "pending",
            "service_type": "personal_training",
            "cadence": "recurring",
            "description": "1:1 PT Leisa recurring payment",
        },
        {
            "person_id": "person-6",
            "source": "stripe",
            "source_event_id": "six",
            "occurred_on": "2026-07-20",
            "status": "completed",
            "service_type": "sgpt",
            "cadence": "recurring",
            "description": "Stripe invoice",
        },
        {
            "person_id": "person-7",
            "source": "stripe",
            "source_event_id": "seven",
            "occurred_on": "2026-07-20",
            "status": "completed",
            "service_type": "sgpt",
            "cadence": "recurring",
            "description": "Stripe invoice",
            "coverage_start": "2026-07-20",
            "coverage_end": "2026-07-20",
        },
    ]

    queue = build_entitlement_exception_queue(
        governed_rows=governed,
        relationships=relationships,
        entitlement_rows=[],
        lifecycle_rows=lifecycle,
        people_rows=people,
        payment_account_rows=accounts,
        payment_event_rows=events,
        identified=True,
    )
    buckets = {
        bucket["code"]: bucket["client_count"]
        for bucket in queue["buckets"]
    }

    assert buckets == {
        "arrears_retry": 1,
        "payment_service_mismatch": 1,
        "payment_account_paused_roster_active": 1,
        "one_time_invoice_entitlement_term_missing": 1,
        "paid_period_expired_roster_active": 1,
        "paid_period_end_unresolved": 1,
        "pt_minder_shadow_collecting": 1,
    }
