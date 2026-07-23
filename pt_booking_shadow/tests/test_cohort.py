from datetime import date

from pt_booking_shadow.config import FIELD_IDS
from pt_booking_shadow.cohort import resolve_contact


def raw_contact(tags=None, fields=None):
    return {
        "id": "c1",
        "firstName": "Test",
        "lastName": "Member",
        "tags": tags or [],
        "customFields": [
            {"id": field_id, "value": value}
            for field_id, value in (fields or {}).items()
        ],
    }


def opportunity(stage, status="open"):
    return {
        "pipelineId": "fkEvrFkTihYkdb3bpprd",
        "pipelineStageId": stage,
        "status": status,
        "updatedAt": "2026-07-23T00:00:00Z",
    }


def test_resolves_frequency_from_pipeline_stage():
    contact = resolve_contact(
        raw_contact(["personal training"]),
        [opportunity("01d615da-4bd4-4bf3-a5c6-54332588367d")],
    )
    assert contact.expected_frequency == 2
    assert contact.effective_status == "active"


def test_pt_only_uses_frequency_tag():
    contact = resolve_contact(
        raw_contact(["personal training", "1 p.wk"]),
        [opportunity("58247f13-4a47-40f8-8289-35d62fc138b3")],
    )
    assert contact.expected_frequency == 1


def test_pt_hold_precedes_former_status():
    fields = {
        FIELD_IDS["hold_type"]: "PT",
        FIELD_IDS["hold_status"]: "On Hold",
        FIELD_IDS["hold_start"]: "2026-07-20",
        FIELD_IDS["hold_end"]: "2026-08-17",
    }
    contact = resolve_contact(raw_contact(["personal training", "old pt client"], fields), [])
    assert contact.effective_status == "pt_hold"
    assert contact.hold_end == date(2026, 8, 17)


def test_pt_cancellation_precedes_hold():
    fields = {
        FIELD_IDS["hold_type"]: "PT",
        FIELD_IDS["hold_status"]: "On Hold",
        FIELD_IDS["cancellation_type"]: "PT",
        FIELD_IDS["cancellation_status"]: "Notice Active",
        FIELD_IDS["final_access"]: "2026-08-31",
    }
    contact = resolve_contact(raw_contact(["personal training"], fields), [])
    assert contact.effective_status == "pt_cancellation"
    assert contact.final_access == date(2026, 8, 31)


def test_membership_hold_does_not_pause_pt():
    fields = {
        FIELD_IDS["hold_type"]: "Membership",
        FIELD_IDS["hold_status"]: "On Hold",
    }
    contact = resolve_contact(raw_contact(["personal training"], fields), [])
    assert contact.effective_status == "active"
