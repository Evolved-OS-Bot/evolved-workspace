from datetime import UTC, datetime, timedelta

from scripts.backfill_sa_attendance import build_backfill, classify_match


AT = datetime(2026, 7, 1, 2, 0, tzinfo=UTC)


def event(event_id, *, minutes=0, email="prospect@example.com"):
    return {
        "appointment_id": event_id,
        "contact_id": f"contact-{event_id}",
        "start_at": AT + timedelta(minutes=minutes),
        "email": email,
        "phone": "0400 000 000",
        "first_name": "Test",
        "last_name": "Prospect",
    }


def legacy(**overrides):
    return {
        "row_number": 2,
        "appointment_at": AT,
        "email": "prospect@example.com",
        "phone": "0400 000 000",
        "first_name": "Test",
        "last_name": "Prospect",
        "legacy_show": "Y",
        "legacy_convert": "N",
        **overrides,
    }


def test_exact_event_id_wins():
    match = classify_match(
        legacy(appointment_id="event-2"),
        [event("event-1"), event("event-2")],
    )
    assert match["classification"] == "exact"
    assert match["event"]["appointment_id"] == "event-2"


def test_unique_identity_and_exact_time_is_corroborated():
    match = classify_match(legacy(), [event("event-1")])
    assert match["classification"] == "corroborated"


def test_multiple_near_events_are_ambiguous():
    match = classify_match(
        legacy(email="", phone="", first_name="Test", last_name="Prospect"),
        [event("event-1", minutes=-5), event("event-2", minutes=5)],
    )
    assert match["classification"] == "ambiguous"


def test_k_alone_does_not_make_unmatched_history_promotion_eligible():
    result = build_backfill(
        [legacy(email="", phone="", first_name="", last_name="")],
        [],
    )
    assert result["summary"]["unmatched"] == 1
    assert result["details"][0]["promotion_eligible"] is False
    assert result["summary"]["historical_kpi_restatement_performed"] is False
