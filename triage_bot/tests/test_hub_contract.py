from triage_bot.hub_contract import (
    compare_conversation_contacts,
    hub_member_flags,
)


def _row(lifecycle="active", services=("sgpt",)):
    return {
        "lifecycle": {"status": lifecycle},
        "service_relationships": [
            {"service_type": service, "status": "active"}
            for service in services
        ],
    }


def test_hub_flags_use_lifecycle_and_service_separately():
    assert hub_member_flags(_row(services=("sgpt", "personal_training"))) == {
        "is_sgpt_member": True,
        "is_pt_client": True,
        "identity_review_required": False,
    }
    assert hub_member_flags(_row(lifecycle="inactive"))[
        "is_sgpt_member"
    ] is False


def test_unresolved_or_missing_person_fails_closed():
    assert hub_member_flags(None)["identity_review_required"] is True
    flags = hub_member_flags(_row(lifecycle="review_required"))
    assert flags["is_sgpt_member"] is False
    assert flags["is_pt_client"] is False


def test_conversation_parity_is_exact_by_contact_and_flags():
    rows = [
        {
            "contact_id": "c1",
            "legacy_is_sgpt_member": True,
            "legacy_is_pt_client": False,
            "hub_is_sgpt_member": True,
            "hub_is_pt_client": False,
        }
    ]
    assert compare_conversation_contacts(rows).equivalent is True
    rows[0]["hub_is_pt_client"] = True
    assert compare_conversation_contacts(rows).changed == ("c1",)
