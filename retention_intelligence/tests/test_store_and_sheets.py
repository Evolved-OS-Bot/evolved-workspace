from datetime import date

from retention_intelligence.classification import classify_member
from retention_intelligence.models import MemberInput, UsageMetrics
from retention_intelligence.sheets import RetentionSheetsWriter
from retention_intelligence import store as store_module
from retention_intelligence.store import RetentionStore


def assessment():
    return classify_member(
        MemberInput(
            trainerize_user_id=7,
            email="member@example.com",
            first_name="Jane",
            last_name="Member",
            service="Strong, Fit & Flexible Membership",
            trainer_name="Piper",
            created_date="2025-01-01",
            latest_signed_in="2026-07-25",
            ghl_active=True,
            stripe_entitled=True,
            trainerize_active=True,
            cancellation_status=None,
            final_access_date=None,
            account_classification=None,
            has_operational_exception=False,
            usage=UsageMetrics(
                workouts_7d=2,
                workouts_28d=9,
                workouts_90d=28,
                baseline_workouts=24,
                last_workout_date="2026-07-25",
                days_since_last_workout=1,
            ),
        ),
        today=date(2026, 7, 26),
    )


def test_store_retains_completed_snapshot(tmp_path):
    store = RetentionStore(f"sqlite:///{tmp_path / 'retention.db'}")
    run_id = store.start_run()
    summary = store.complete_run(run_id, "source-run", [assessment()])
    assert summary["member_count"] == 1
    assert store.latest_summary()["status"] == "complete"
    assert store.latest_radar()[0]["email"] == "member@example.com"


def test_sheet_payload_has_current_member_and_kpi():
    item = assessment()
    radar = RetentionSheetsWriter.radar_values([item], "snapshot")
    assert radar[1][0] == "Jane Member"
    kpi = RetentionSheetsWriter.kpi_row(
        [item], week_start=date(2026, 7, 20), run_id="run"
    )
    assert kpi[0] == "2026-07-20"
    assert kpi[1] == 1


def test_store_uses_psycopg3_for_railway_postgres(monkeypatch):
    captured = {}

    class FakeEngine:
        pass

    def fake_create_engine(url, **kwargs):
        captured["url"] = url
        return FakeEngine()

    monkeypatch.setattr(store_module, "create_engine", fake_create_engine)
    monkeypatch.setattr(store_module.metadata, "create_all", lambda engine: None)

    RetentionStore("postgresql://user:secret@host:5432/database")

    assert captured["url"].startswith("postgresql+psycopg://")
