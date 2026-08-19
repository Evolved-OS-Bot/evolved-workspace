from operating_data_hub.trainerize_attendance import (
    TrainerizeAttendanceClient,
    attach_evidence,
    corroborate_attendance,
    resolve_verified_appointments,
)


class FakeTrainerizeClient:
    def __init__(self, clients, calendars):
        self.clients = clients
        self.calendars = calendars

    def attendance_clients(self):
        return self.clients

    def calendar(self, user_id, start_date, end_date):
        return self.calendars.get(user_id, [])


def tracked(name, session_id="workout-1"):
    return [
        {
            "date": "2026-07-22",
            "items": [
                {
                    "id": session_id,
                    "name": name,
                    "status": "tracked",
                    "type": "workoutRegular",
                }
            ],
        }
    ]


def candidate(kind="onboarding"):
    return {
        "appointment_id": "appointment-1",
        "contact_id": "contact-1",
        "target_date": "2026-07-22",
        "kind": kind,
    }


def test_exact_email_and_tracked_onboarding_verify_showed():
    result = corroborate_attendance(
        FakeTrainerizeClient(
            [
                {
                    "id": 123,
                    "email": "Member@Example.com",
                    "firstName": "Different",
                    "lastName": "Name",
                }
            ],
            {123: tracked("On-boarding Session")},
        ),
        [candidate()],
        {
            "contact-1": {
                "email": "member@example.com",
                "name": "Member Name",
            }
        },
    )

    evidence = result["results"][0]
    assert evidence["decision"] == "verified_showed"
    assert evidence["identity"]["basis"] == "email"
    assert evidence["matching_sessions"][0]["session_id"] == "workout-1"


def test_exact_unique_name_is_allowed_when_email_does_not_match():
    result = corroborate_attendance(
        FakeTrainerizeClient(
            [
                {
                    "id": 123,
                    "email": "",
                    "firstName": "Member",
                    "lastName": "Name",
                }
            ],
            {123: tracked("Women's Standard Strength Assessment")},
        ),
        [candidate("strength_assessment")],
        {"contact-1": {"name": "Member Name"}},
    )

    assert result["results"][0]["decision"] == "verified_showed"
    assert result["results"][0]["identity"]["basis"] == "exact_name"


def test_deactivated_exact_identity_remains_valid_attendance_evidence():
    result = corroborate_attendance(
        FakeTrainerizeClient(
            [
                {
                    "id": 30609970,
                    "email": "indie26mia@icloud.com",
                    "firstName": "Indie",
                    "lastName": "Cevallos",
                    "attendanceAccountState": "deactivatedClient",
                }
            ],
            {
                30609970: tracked(
                    "Women's Standard Strength Assessment",
                    session_id="1145161709",
                )
            },
        ),
        [
            {
                **candidate("strength_assessment"),
                "target_date": "2026-07-22",
            }
        ],
        {
            "contact-1": {
                "email": "indie26mia@icloud.com",
                "name": "Indie Cevallos",
            }
        },
    )

    evidence = result["results"][0]
    assert evidence["decision"] == "verified_showed"
    assert evidence["identity"]["account_state"] == "deactivatedClient"


def test_attendance_roster_combines_views_and_prefers_active_duplicate():
    client = TrainerizeAttendanceClient("group", "token", 123)
    client._clients_for_view = lambda view: (
        [{"id": 1, "email": "active@example.com"}]
        if view == "activeClient"
        else [
            {"id": 1, "email": "old@example.com"},
            {"id": 2, "email": "deactivated@example.com"},
        ]
    )

    rows = {row["id"]: row for row in client.attendance_clients()}

    assert rows[1]["email"] == "active@example.com"
    assert rows[1]["attendanceAccountState"] == "activeClient"
    assert rows[2]["attendanceAccountState"] == "deactivatedClient"


def test_ambiguous_identity_fails_closed():
    clients = [
        {"id": 123, "firstName": "Member", "lastName": "Name"},
        {"id": 456, "firstName": "Member", "lastName": "Name"},
    ]
    result = corroborate_attendance(
        FakeTrainerizeClient(clients, {}),
        [candidate()],
        {"contact-1": {"name": "Member Name"}},
    )

    evidence = result["results"][0]
    assert evidence["decision"] == "unresolved"
    assert evidence["reason"] == "trainerize_identity_ambiguous"


def test_missing_or_duplicate_required_session_fails_closed():
    missing = corroborate_attendance(
        FakeTrainerizeClient(
            [{"id": 123, "email": "member@example.com"}],
            {123: tracked("Regular Workout")},
        ),
        [candidate()],
        {"contact-1": {"email": "member@example.com"}},
    )
    duplicate = corroborate_attendance(
        FakeTrainerizeClient(
            [{"id": 123, "email": "member@example.com"}],
            {
                123: [
                    {
                        "date": "2026-07-22",
                        "items": [
                            {
                                "id": "one",
                                "name": "On-boarding Session",
                                "status": "tracked",
                            },
                            {
                                "id": "two",
                                "name": "Onboarding Session",
                                "status": "tracked",
                            },
                        ],
                    }
                ]
            },
        ),
        [candidate()],
        {"contact-1": {"email": "member@example.com"}},
    )

    assert missing["results"][0]["reason"] == "required_session_not_tracked"
    assert duplicate["results"][0]["reason"] == (
        "ambiguous_matching_sessions"
    )


def test_attach_evidence_reports_tasks_remaining_after_precheck():
    plan = {
        "actions": [
            {
                "appointment_id": "appointment-1",
                "contact_id": "contact-1",
                "stage": "coach",
            },
            {
                "appointment_id": "appointment-1",
                "contact_id": "contact-1",
                "stage": "admin",
            },
            {
                "appointment_id": "appointment-2",
                "contact_id": "contact-2",
                "stage": "coach",
            },
        ],
        "counts": {"coach_due": 2, "admin_due": 1},
    }
    attached = attach_evidence(
        plan,
        {
            "source_status": "complete",
            "counts": {
                "requested": 2,
                "verified_showed": 1,
                "unresolved": 1,
            },
            "results": [
                {
                    **candidate(),
                    "decision": "verified_showed",
                    "matching_sessions": [{"session_id": "workout-1"}],
                }
            ],
        },
    )

    assert attached["counts"]["trainerize_verified"] == 1
    assert attached["counts"]["coach_due_after_precheck"] == 1
    assert attached["counts"]["admin_due_after_precheck"] == 0


class FakeGHLClient:
    def __init__(self, status="confirmed", fail_write=False):
        self.status = status
        self.fail_write = fail_write
        self.updates = []

    def get_appointment_state(self, appointment_id):
        return {
            "appointment_id": appointment_id,
            "contact_id": "contact-1",
            "start_at": "2026-07-22T00:30:00+00:00",
            "status": self.status,
        }

    def update_trainerize_verified_to_showed(
        self,
        event,
        evidence,
        *,
        idempotency_key,
    ):
        if self.fail_write:
            raise RuntimeError("write unavailable")
        self.updates.append(idempotency_key)
        self.status = "showed"
        return {}


def evidence_plan():
    return {
        "actions": [
            {
                "appointment_id": "appointment-1",
                "contact_id": "contact-1",
                "trainerize_evidence": {
                    **candidate(),
                    "decision": "verified_showed",
                    "matching_sessions": [
                        {"session_id": "workout-1"}
                    ],
                },
            }
        ]
    }


def test_verified_evidence_updates_and_verifies_ghl():
    client = FakeGHLClient()
    result = resolve_verified_appointments(client, evidence_plan())

    assert result["counts"] == {
        "verified": 1,
        "resolved": 1,
        "fallback": 0,
    }
    assert result["audit"][0]["outcome"] == "updated_to_showed"
    assert client.updates


def test_failed_ghl_write_falls_back_to_staff_task():
    result = resolve_verified_appointments(
        FakeGHLClient(fail_write=True),
        evidence_plan(),
    )

    assert result["counts"]["fallback"] == 1
    assert not result["resolved_ids"]
    assert result["audit"][0]["outcome"] == "staff_task_fallback"
