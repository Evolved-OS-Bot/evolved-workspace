import sqlite3

from pt_booking_shadow.models import Finding
from pt_booking_shadow.reporting import build_csv, build_html
from pt_booking_shadow.state_store import StateStore


def finding(category="HEALTHY"):
    return Finding(
        contact_id="c1",
        contact_name="Test Member",
        category=category,
        reason="Evidence-led test.",
        effective_status="active",
    )


def test_store_persists_run_and_deduplicates_event(tmp_path):
    store = StateStore(str(tmp_path / "state.db"))
    run_id = store.start_run("full")
    store.complete_run(run_id, [finding()], 1)
    assert store.last_successful_run()
    assert store.enqueue_event("event-1", "c1", "AppointmentUpdate", delay_minutes=0)
    assert not store.enqueue_event("event-1", "c1", "AppointmentUpdate", delay_minutes=0)
    assert store.due_contacts() == ["c1"]
    store.mark_contact_events_processed("c1")
    assert store.due_contacts() == []


def test_report_contains_shadow_banner_and_contact_link():
    body = build_html([finding("WOULD_TOP_UP")], "location-1", "run-1")
    assert "NO GHL APPOINTMENTS WERE CHANGED" in body
    assert "/contacts/detail/c1" in body


def test_csv_contains_category_and_no_phone_or_email():
    content = build_csv([finding("HEALTHY")], "location-1", "run-1").decode()
    assert "HEALTHY" in content
    assert "phone" not in content.lower()
    assert "email" not in content.lower()
