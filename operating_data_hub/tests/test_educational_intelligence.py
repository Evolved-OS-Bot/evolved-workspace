from datetime import date

from operating_data_hub import educational_intelligence as surveillance


def test_discovery_is_held_and_does_not_mutate_canonical_files(
    monkeypatch, tmp_path
):
    reference = tmp_path / "reference/educational-intelligence"
    reference.mkdir(parents=True)
    (reference / "quarterly-surveillance-config.json").write_text("{}")
    (reference / "approved-studies-bank.md").write_text(
        "https://pubmed.ncbi.nlm.nih.gov/12345678/"
    )
    (reference / "emerging-science-horizon-watchlist.md").write_text(
        "NCT12345678"
    )
    monkeypatch.setattr(
        surveillance.engine,
        "load_config",
        lambda _path: {"cadence": {"lookback_days": 120}},
    )
    monkeypatch.setattr(
        surveillance.engine,
        "canonical_hashes",
        lambda: {"doctrine": "unchanged"},
    )
    monkeypatch.setattr(
        surveillance.engine,
        "fetch_live",
        lambda *_args, **_kwargs: {
            "pubmed": [{"pmid": "87654321"}],
            "trials": [],
            "horizon_refresh": [{"nct_id": "NCT12345678"}],
            "safety_flags": [],
        },
    )
    monkeypatch.setattr(
        surveillance.engine,
        "classify_candidates",
        lambda *_args: [
            {
                "candidate_id": "PMID-87654321",
                "duplicate_state": "NEW",
            }
        ],
    )

    payload = surveillance.run_discovery(
        tmp_path,
        as_of=date(2026, 8, 18),
    )

    assert payload["promotion_state"] == "HELD_HUMAN_APPRAISAL_REQUIRED"
    assert payload["publication_impact"] == "none"
    assert payload["canonical_mutation"] is False
    assert payload["counts"] == {
        "candidates": 1,
        "new": 1,
        "existing": 0,
        "safety_flags": 0,
        "horizon_refresh": 1,
    }
