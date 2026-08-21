from retention_intelligence.hub_contract import apply_hub_authority
from retention_intelligence.models import MemberInput, UsageMetrics
from reporting_control.current_people_client import validate_current_people_contract
from datetime import UTC, datetime


def _member():
    return MemberInput(
        trainerize_user_id=101,
        email="legacy@example.com",
        first_name="Legacy",
        last_name="Name",
        service="Silver Package",
        trainer_name=None,
        created_date="2026-01-01",
        latest_signed_in=None,
        ghl_active=True,
        stripe_entitled=True,
        trainerize_active=True,
        cancellation_status=None,
        final_access_date=None,
        account_classification=None,
        has_operational_exception=False,
        usage=UsageMetrics(),
    )


def _contract(rows):
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
            "rows": rows,
        },
        max_age_hours=1,
    )


def test_hub_authority_overlays_governed_state_but_preserves_usage_profile():
    member = _member()
    contract = _contract(
        [
            {
                "person_id": "person-1",
                "display": {
                    "email": "current@example.com",
                    "first_name": "Current",
                    "last_name": "Member",
                },
                "source_identities": {
                    "trainerize": [{"source_id": "101"}],
                    "ghl": [{"source_id": "contact-1"}],
                },
                "lifecycle": {"status": "active"},
                "service_relationships": [
                    {
                        "service_type": "sgpt",
                        "service_name": "Strength & Sculpt",
                        "status": "active",
                    }
                ],
                "entitlements": [
                    {"status": "confirmed", "current": True}
                ],
                "payment_accounts": [],
            }
        ]
    )
    projected = apply_hub_authority([member], contract)[0]
    assert projected.email == "current@example.com"
    assert projected.service == "Strength & Sculpt"
    assert projected.ghl_active is True
    assert projected.stripe_entitled is True
    assert projected.usage is member.usage


def test_missing_hub_person_fails_closed_without_dropping_delivery_row():
    projected = apply_hub_authority([_member()], _contract([]))[0]
    assert projected.ghl_active is False
    assert projected.stripe_entitled is False
    assert projected.has_operational_exception is True
