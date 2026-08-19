from operating_data_hub.config import Settings
from operating_data_hub.ghl_reporting_v2 import (
    PREQUAL_COMPLETED_AT_FIELD_ID,
    PREQUAL_COMPLETED_BY_FIELD_ID,
    PREQUAL_SUMMARY_FIELD_ID,
    WARM_PIPELINE_ID,
    WARM_STAGE_PREQUALIFIED,
)
from operating_data_hub.service import HubService


def test_parity_uses_exact_completion_state_refs(monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'hub.db'}")
    service = HubService(Settings.from_env(require_runtime=False))
    service.store.accept_snapshot(
        "prequalification_completion_state",
        {
            "observed_at": "2026-08-09T00:00:00+00:00",
            "complete": True,
            "event_refs": [
                {
                    "source_event_id": (
                        "prequalification-completed:opportunity-1"
                    ),
                    "event_version_id": "immutable-version-1",
                    "contact_id": "contact-1",
                }
            ],
            "review_queue": [],
        },
    )

    class Reader:
        def __init__(self, *_args, **_kwargs):
            pass

        def contacts(self):
            return [
                {
                    "id": "contact-1",
                    "customFields": [
                        {
                            "id": PREQUAL_SUMMARY_FIELD_ID,
                            "value": "Complete handoff",
                        },
                        {
                            "id": PREQUAL_COMPLETED_BY_FIELD_ID,
                            "value": "Nora Silva",
                        },
                        {
                            "id": PREQUAL_COMPLETED_AT_FIELD_ID,
                            "value": "2026-08-09T09:00:00+10:00",
                        },
                    ],
                }
            ]

        def opportunities(self):
            return [
                {
                    "id": "opportunity-1",
                    "contactId": "contact-1",
                    "pipelineId": WARM_PIPELINE_ID,
                    "pipelineStageId": WARM_STAGE_PREQUALIFIED,
                }
            ]

    monkeypatch.setattr(
        "operating_data_hub.service.GHLAcquisitionReader",
        Reader,
    )
    monkeypatch.setattr(
        service.reporting_v2,
        "latest_source_event_payloads",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("parity must use the governed state references")
        ),
    )

    result = service.audit_prequalification_completion_parity()

    assert result["complete"] is True
    assert result["sample_size"] == 1
    assert result["exact"] == 1
    assert result["mismatches"] == 0
