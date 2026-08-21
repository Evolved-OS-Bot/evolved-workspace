from datetime import UTC, datetime

from pt_booking_shadow.hub_contract import (
    compare_pt_cohort,
    hub_pt_projection,
)
from pt_booking_shadow.models import PTContact
from reporting_control.current_people_client import validate_current_people_contract


def _contact(status="active"):
    return PTContact(
        id="contact-1",
        name="Member",
        tags=set(),
        custom_fields={},
        email="member@example.com",
        phone="",
        stage_id=None,
        expected_frequency=1,
        effective_status=status,
        status_reason="test",
    )


def _contract(lifecycle="active"):
    return validate_current_people_contract(
        {
            "schema_version": 1,
            "contract_version": "current-person-v1",
            "mode": "shadow",
            "generated_at": datetime.now(UTC).isoformat(),
            "period": {
                "id": "week",
                "start": "2026-07-20",
                "end": "2026-07-26",
                "timezone": "Australia/Brisbane",
            },
            "source_freshness": {"membership": {"status": "fresh"}},
            "complete": True,
            "blocked_reasons": [],
            "rows": [
                {
                    "person_id": "person-1",
                    "source_identities": {
                        "ghl": [{"source_id": "contact-1"}],
                        "trainerize": [],
                    },
                    "lifecycle": {"status": lifecycle},
                    "service_relationships": [
                        {
                            "service_type": "personal_training",
                            "status": "active",
                        }
                    ],
                    "entitlements": [
                        {
                            "service_type": "personal_training",
                            "status": "confirmed",
                            "current": True,
                        }
                    ],
                    "payment_accounts": [],
                }
            ],
        },
        max_age_hours=1,
    )


def test_pt_projection_keeps_lifecycle_and_commercial_separate():
    projection = hub_pt_projection(_contract().rows[0])
    assert projection == {
        "current_pt": True,
        "suppression": "none",
        "commercial_supported": True,
    }


def test_pt_cohort_parity_uses_exact_contact_and_suppression():
    assert compare_pt_cohort([_contact()], _contract()).equivalent is True
    result = compare_pt_cohort([_contact("pt_hold")], _contract())
    assert result.changed == ("contact-1",)
