from datetime import date

from operating_data_hub.evolved_standards import (
    build_evolved_standards_projection,
    canonical_exercise,
    classify_assessment_components,
    classify_future_proofing_standards,
)


def observation(
    identifier,
    name,
    *,
    side=None,
    reps=None,
    weight=None,
    seconds=None,
    target=None,
    record_type=None,
):
    return {
        "sourceObservationId": identifier,
        "exerciseName": name,
        "side": side,
        "reps": reps,
        "weightKg": weight,
        "timeSeconds": seconds,
        "target": target,
        "recordType": record_type,
    }


def assessment(
    identifier,
    observed_on,
    observations,
    *,
    user_id=7,
    bodyweight=60,
):
    return {
        "sourceAssessmentId": identifier,
        "trainerizeUserId": user_id,
        "assessmentDate": observed_on,
        "assessmentStatus": "tracked",
        "sourceSchemaVersion": "current_independent_v2",
        "bodyWeight": (
            {
                "kg": bodyweight,
                "measurementDate": observed_on,
                "dayOffset": 0,
                "timingQuality": "Same day",
                "selectionMethod": "exact_body_stat",
            }
            if bodyweight is not None
            else None
        ),
        "observations": observations,
    }


def components_by_id(value):
    return {row["component_id"]: row for row in value}


def test_alias_normalisation_is_exact_and_does_not_fuzzy_match():
    assert canonical_exercise("Farmer's Carry") == "farmer_walk"
    assert canonical_exercise(" strict toes-to-bar ") == "toes_to_bar"
    assert canonical_exercise("ATG Split Squat") == "atg_split_squat"
    assert canonical_exercise("ATG Split Squat Elevated") is None
    assert canonical_exercise("Hanging Leg Raise") is None
    assert canonical_exercise("5km Run") == "run_5km"
    assert canonical_exercise("Generic Running") is None


def test_four_components_are_scored_independently_from_complete_evidence():
    value = components_by_id(
        classify_assessment_components(
            assessment(
                "assessment-1",
                "2026-07-20",
                [
                    observation(
                        "right",
                        "ATG Split Squat",
                        side="right",
                        reps=10,
                        weight=60,
                    ),
                    observation(
                        "left",
                        "ATG Split Squat",
                        side="left",
                        reps=10,
                        weight=30,
                    ),
                    observation(
                        "carry",
                        "Farmer Walk",
                        weight=60,
                        seconds=60,
                    ),
                    observation(
                        "plank",
                        "High Plank",
                        seconds=120,
                    ),
                    observation(
                        "side-right",
                        "Side Plank",
                        side="right",
                        seconds=120,
                    ),
                    observation(
                        "side-left",
                        "Side Plank",
                        side="left",
                        seconds=120,
                    ),
                    observation(
                        "toes",
                        "Strict Toes to Bar",
                        reps=10,
                    ),
                ],
            )
        )
    )

    assert value["single_leg_right"]["level"] == "Perform"
    assert value["single_leg_left"]["level"] == "Long"
    assert value["grip_endurance"]["level"] == "Long"
    assert value["spinal_control"]["level"] == "Perform"


def test_combined_split_squat_and_incomplete_farmer_evidence_fail_closed():
    value = components_by_id(
        classify_assessment_components(
            assessment(
                "legacy",
                "2026-07-20",
                [
                    observation(
                        "combined",
                        "ATG Split Squat",
                        reps=10,
                        weight=0,
                    ),
                    observation(
                        "carry",
                        "Farmer Walk",
                        weight=45,
                    ),
                ],
            )
        )
    )

    assert value["single_leg_right"]["sufficient"] is False
    assert value["single_leg_left"]["sufficient"] is False
    assert value["single_leg_right"]["reason"] == (
        "split_squat_side_missing_or_ambiguous"
    )
    assert value["grip_endurance"]["sufficient"] is False
    assert value["grip_endurance"]["reason"] == (
        "verified_duration_or_load_missing"
    )


def test_bodyweight_missing_allows_live_split_but_blocks_loaded_grip():
    value = components_by_id(
        classify_assessment_components(
            assessment(
                "missing-weight",
                "2026-07-20",
                [
                    observation(
                        "right",
                        "ATG Split Squat",
                        side="right",
                        reps=10,
                        weight=0,
                    ),
                    observation(
                        "carry",
                        "Farmer Walk",
                        weight=45,
                        seconds=60,
                    ),
                ],
                bodyweight=None,
            )
        )
    )

    assert value["single_leg_right"]["level"] == "Live"
    assert value["single_leg_right"]["next_level"] == "Long"
    assert value["grip_endurance"]["sufficient"] is False
    assert value["grip_endurance"]["reason"] == "bodyweight_missing"


def test_spinal_long_requires_live_and_both_independent_sides():
    value = components_by_id(
        classify_assessment_components(
            assessment(
                "spinal",
                "2026-07-20",
                [
                    observation("plank", "High Plank", seconds=120),
                    observation(
                        "side",
                        "Side Plank",
                        seconds=120,
                    ),
                    observation(
                        "toes",
                        "Toes to Bar",
                        reps=10,
                    ),
                ],
            )
        )
    )

    assert value["spinal_control"]["level"] == "Live"
    assert value["spinal_control"]["reason"] == (
        "side_plank_side_missing_or_ambiguous"
    )


def test_projection_resolves_identity_transitions_and_effective_start():
    first = assessment(
        "first",
        "2026-07-10",
        [
            observation(
                "r-first",
                "ATG Split Squat",
                side="right",
                reps=10,
                weight=0,
            )
        ],
    )
    second = assessment(
        "second",
        "2026-07-25",
        [
            observation(
                "r-second",
                "ATG Split Squat",
                side="right",
                reps=10,
                weight=30,
            )
        ],
    )
    trainerize = {
        "payload": {
            "summary": {
                "standardsEvidenceSchemaVersion": 1,
                "standardsEvidence": [first, second],
                "standardsEvidenceCoverage": {
                    "status": "complete",
                    "assessments": 2,
                },
            }
        }
    }
    membership = {
        "payload": {
            "rows": [
                {
                    "canonical_key": "member@example.com",
                    "first_name": "Ava",
                    "last_name": "Example",
                    "source_ids": {
                        "trainerize": ["7"],
                        "ghl": ["contact-7"],
                    },
                }
            ]
        }
    }
    acquisition = {
        "payload": {
            "sales": [
                {
                    "sale_id": "membership-sale-7",
                    "contact_id": "contact-7",
                    "sold_at": "2026-07-01T00:00:00+10:00",
                }
            ]
        }
    }

    value = build_evolved_standards_projection(
        trainerize_snapshot=trainerize,
        membership_snapshot=membership,
        acquisition_snapshot=acquisition,
        as_of_date=date(2026, 8, 2),
        acceptance_record={
            "acceptance_record_id": "acceptance-1",
            "acceptance_fingerprint": "fingerprint-1",
            "acceptance_state": "ready_for_owner_acceptance",
            "technical_gates_passed": True,
            "owner_approval_state": "pending",
            "promotion_authorised": False,
        },
    )

    assert value["status"] == "available"
    assert value["component_results"][0]["level"] == "Long"
    assert value["newly_achieved"][0]["level"] == "Long"
    live = next(
        row
        for row in value["time_to_standard"][
            "component_achievements"
        ]
        if row["level"] == "Live"
    )
    long = next(
        row
        for row in value["time_to_standard"][
            "component_achievements"
        ]
        if row["level"] == "Long"
    )
    assert live["days_from_effective_start"] == 9
    assert long["days_from_effective_start"] == 24
    assert value["overall"]["status"] == "unavailable"
    assert value["overall"]["classification"] is None
    assert value["overall"]["label"] is None
    assert value["future_proofing_score_summary"] == {
        "members_with_complete_score": 0,
        "members_with_incomplete_score": 1,
        "bands": {},
    }
    assert value["acceptance"] == {
        "acceptance_record_id": "acceptance-1",
        "acceptance_fingerprint": "fingerprint-1",
        "acceptance_state": "ready_for_owner_acceptance",
        "technical_gates_passed": True,
        "owner_approval_state": "pending",
        "promotion_authorised": False,
    }


def test_projection_does_not_classify_unresolved_identity():
    value = build_evolved_standards_projection(
        trainerize_snapshot={
            "payload": {
                "summary": {
                    "standardsEvidenceSchemaVersion": 1,
                    "standardsEvidence": [
                        assessment(
                            "one",
                            "2026-07-20",
                            [
                                observation(
                                    "right",
                                    "ATG Split Squat",
                                    side="right",
                                    reps=10,
                                )
                            ],
                        )
                    ],
                    "standardsEvidenceCoverage": {
                        "status": "complete"
                    },
                }
            }
        },
        membership_snapshot={"payload": {"rows": []}},
        acquisition_snapshot={"payload": {"sales": []}},
        as_of_date=date(2026, 8, 2),
    )

    assert value["status"] == "unavailable"
    assert value["component_results"] == []
    assert value["exceptions"] == [
        {
            "code": "trainerize_identity_unresolved",
            "trainerize_user_id": "7",
        }
    ]


def test_projection_fails_closed_when_source_coverage_is_incomplete():
    value = build_evolved_standards_projection(
        trainerize_snapshot={
            "payload": {
                "summary": {
                    "standardsEvidenceSchemaVersion": 1,
                    "standardsEvidence": [
                        assessment("one", "2026-08-02", [])
                    ],
                    "standardsEvidenceCoverage": {
                        "status": "unavailable",
                        "reason": "refresh incomplete",
                    },
                }
            }
        },
        membership_snapshot={"payload": {"rows": []}},
        acquisition_snapshot={"payload": {"sales": []}},
        as_of_date=date(2026, 8, 3),
    )

    assert value["status"] == "unavailable"
    assert value["reason"] == (
        "trainerize_standards_evidence_incomplete"
    )
    assert value["future_proofing_scores"] == []
    assert value["overall"]["status"] == "unavailable"


def test_future_proofing_score_requires_all_six_primary_standards():
    standards = {
        row["standard_id"]: row
        for row in classify_future_proofing_standards(
            assessment(
                "complete-six",
                "2026-08-02",
                [
                    observation(
                        "deadlift",
                        "Barbell Deadlift",
                        reps=1,
                        weight=75,
                    ),
                    observation(
                        "split-right",
                        "ATG Split Squat",
                        side="right",
                        reps=10,
                        weight=60,
                    ),
                    observation(
                        "split-left",
                        "ATG Split Squat",
                        side="left",
                        reps=10,
                        weight=30,
                    ),
                    observation(
                        "farmer",
                        "DB Farmer Walk",
                        weight=60,
                        seconds=60,
                    ),
                    observation(
                        "plank",
                        "Full Plank",
                        seconds=120,
                    ),
                    observation(
                        "side-right",
                        "Side Plank",
                        side="right",
                        seconds=60,
                    ),
                    observation(
                        "side-left",
                        "Side Plank",
                        side="left",
                        seconds=60,
                    ),
                    observation(
                        "run",
                        "5km Run",
                        seconds=29 * 60,
                    ),
                    observation(
                        "push-ups",
                        "Full Push Ups",
                        reps=15,
                        target="Chest to ground",
                    ),
                ],
            )
        )
    }

    assert standards["deadlift"]["score"] == 2
    assert standards["atg_split_squat"]["score"] == 2
    assert standards["atg_split_squat"]["raw_result"][
        "right_score"
    ] == 3
    assert standards["atg_split_squat"]["raw_result"][
        "asymmetry_levels"
    ] == 1
    assert standards["farmer_walk"]["score"] == 2
    assert standards["core_progression"]["score"] == 2
    assert standards["work_capacity"]["score"] == 1
    assert standards["push_ups"]["score"] == 2


def test_future_proofing_score_is_not_extrapolated_from_four_tests():
    component_only = classify_future_proofing_standards(
        assessment(
            "four-tests",
            "2026-08-02",
            [
                observation(
                    "split-right",
                    "ATG Split Squat",
                    side="right",
                    reps=10,
                ),
                observation(
                    "split-left",
                    "ATG Split Squat",
                    side="left",
                    reps=10,
                ),
                observation(
                    "farmer",
                    "DB Farmer Walk",
                    weight=60,
                    seconds=60,
                ),
                observation("plank", "Full Plank", seconds=120),
            ],
        )
    )

    assert len(component_only) == 6
    assert {
        row["standard_id"]
        for row in component_only
        if not row["sufficient"]
    } >= {"deadlift", "work_capacity", "push_ups"}


def test_projection_publishes_only_complete_future_proofing_score_and_band():
    complete = assessment(
        "complete-six",
        "2026-08-02",
        [
            observation(
                "deadlift",
                "Barbell Deadlift",
                reps=1,
                weight=75,
            ),
            observation(
                "split-right",
                "ATG Split Squat",
                side="right",
                reps=10,
                weight=60,
            ),
            observation(
                "split-left",
                "ATG Split Squat",
                side="left",
                reps=10,
                weight=30,
            ),
            observation(
                "farmer",
                "DB Farmer Walk",
                weight=60,
                seconds=60,
            ),
            observation("plank", "Full Plank", seconds=120),
            observation(
                "side-right",
                "Side Plank",
                side="right",
                seconds=60,
            ),
            observation(
                "side-left",
                "Side Plank",
                side="left",
                seconds=60,
            ),
            observation("run", "5km Run", seconds=29 * 60),
            observation(
                "push-ups",
                "Full Push Ups",
                reps=15,
                target="Chest to ground",
            ),
        ],
    )
    value = build_evolved_standards_projection(
        trainerize_snapshot={
            "payload": {
                "summary": {
                    "standardsEvidenceSchemaVersion": 1,
                    "standardsEvidence": [complete],
                    "standardsEvidenceCoverage": {
                        "status": "complete"
                    },
                }
            }
        },
        membership_snapshot={
            "payload": {
                "rows": [
                    {
                        "canonical_key": "member@example.com",
                        "first_name": "Ava",
                        "last_name": "Example",
                        "source_ids": {
                            "trainerize": ["7"],
                            "ghl": ["contact-7"],
                        },
                    }
                ]
            }
        },
        acquisition_snapshot={"payload": {"sales": []}},
        as_of_date=date(2026, 8, 3),
    )

    score = value["future_proofing_scores"][0]
    assert score["status"] == "available"
    assert score["score"] == 11
    assert score["maximum_score"] == 18
    assert score["band"] == "Solid base / approaching Long across most"
    assert value["overall"]["classification"] is None
    assert value["overall"]["label"] is None
    assert value["future_proofing_score_summary"] == {
        "members_with_complete_score": 1,
        "members_with_incomplete_score": 0,
        "bands": {
            "Solid base / approaching Long across most": 1
        },
    }
