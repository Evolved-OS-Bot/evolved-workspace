"""Protected Hub adapter for quarterly Educational Intelligence discovery.

This module may discover and persist a held appraisal queue. It has no write
path to the approved bank, Horizon Watchlist, doctrine or downstream systems.
"""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any

from scripts import run_quarterly_evidence_surveillance as engine

from .config import BRISBANE_TZ


SOURCE = "educational_intelligence_quarterly_surveillance"


def run_discovery(root: Path | None = None, as_of: date | None = None) -> dict[str, Any]:
    workspace_root = root or Path(__file__).resolve().parents[1]
    config_path = (
        workspace_root
        / "reference/educational-intelligence/quarterly-surveillance-config.json"
    )
    bank_path = (
        workspace_root
        / "reference/educational-intelligence/approved-studies-bank.md"
    )
    horizon_path = (
        workspace_root
        / "reference/educational-intelligence/emerging-science-horizon-watchlist.md"
    )
    config = engine.load_config(config_path)
    observed_date = as_of or datetime.now(BRISBANE_TZ).date()
    window_start = observed_date - timedelta(
        days=int(config["cadence"]["lookback_days"])
    )
    known = engine.parse_known_identities(
        bank_path.read_text(encoding="utf-8"),
        horizon_path.read_text(encoding="utf-8"),
    )
    guard_before = engine.canonical_hashes()
    raw = engine.fetch_live(
        config,
        known,
        window_start,
        observed_date,
        refresh_horizon=True,
    )
    candidates = engine.classify_candidates(raw, known)
    guard_after = engine.canonical_hashes()
    if guard_before != guard_after:
        raise engine.EngineError(
            "Canonical Educational Intelligence files changed during discovery"
        )

    counts = {
        "candidates": len(candidates),
        "new": sum(row["duplicate_state"] == "NEW" for row in candidates),
        "existing": sum(
            row["duplicate_state"] != "NEW" for row in candidates
        ),
        "safety_flags": len(raw["safety_flags"]),
        "horizon_refresh": len(raw["horizon_refresh"]),
    }
    return {
        "schema_version": 1,
        "status": "complete",
        "complete": True,
        "observed_at": datetime.now(UTC).isoformat(),
        "as_of": observed_date.isoformat(),
        "window_start": window_start.isoformat(),
        "mode": "live_discovery_shadow",
        "promotion_state": "HELD_HUMAN_APPRAISAL_REQUIRED",
        "publication_impact": "none",
        "canonical_mutation": False,
        "live_system_mutation": False,
        "counts": counts,
        "summary": {"record_count": len(candidates), **counts},
        "rows": candidates,
        "protected_raw": raw,
        "canonical_hashes_before": guard_before,
        "canonical_hashes_after": guard_after,
    }
