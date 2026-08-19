from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Callable, Iterable

import requests


CURRENT_PEOPLE_PATH = "/api/v2/reporting/current-people"
PARALLEL_RESULTS_PATH = "/api/v2/reporting/parallel-results"
CUTOVER_STATUS_PATH = "/api/v2/reporting/cutover-status"
BRISBANE_TIMEZONE = "Australia/Brisbane"
ALLOWED_PERIODS = {"week", "28d", "90d"}


class HubContractError(RuntimeError):
    """Raised when a protected Hub read contract cannot be trusted."""


@dataclass(frozen=True)
class CutoverAuthority:
    metric_id: str
    definition_version: str
    promotion_authorised: bool
    effective_state: str
    rollback_active: bool
    blocked_reasons: tuple[str, ...]


def _utc_datetime(value: Any, field: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise HubContractError(f"{field} is not an ISO datetime") from exc
    if parsed.tzinfo is None:
        raise HubContractError(f"{field} must include a timezone")
    return parsed.astimezone(UTC)


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        default=str,
    )


def fingerprint(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _reporting_base_url() -> str:
    configured = os.getenv("HUB_REPORTING_BASE_URL", "").strip().rstrip("/")
    if configured:
        if configured.endswith("/api/v2/reporting"):
            return configured[: -len("/api/v2/reporting")]
        return configured
    source = os.getenv("HUB_SOURCE_BASE_URL", "").strip().rstrip("/")
    marker = "/api/v1/sources"
    if marker in source:
        return source.split(marker, 1)[0]
    ingest = os.getenv("HUB_INGEST_BASE_URL", "").strip().rstrip("/")
    marker = "/api/v1/ingest"
    if marker in ingest:
        return ingest.split(marker, 1)[0]
    raise HubContractError("Hub reporting reader is not configured")


def _secret() -> str:
    value = os.getenv("HUB_WEBHOOK_SECRET", "").strip()
    if not value:
        raise HubContractError("Hub reporting secret is not configured")
    return value


def fetch_cutover_authority(
    *,
    metric_id: str,
    definition_version: str,
    period: str = "week",
    timeout: int = 20,
    session: requests.Session | None = None,
) -> CutoverAuthority:
    client = session or requests
    response = client.get(
        f"{_reporting_base_url()}{CUTOVER_STATUS_PATH}",
        headers={"X-Hub-Secret": _secret()},
        params={"period": period},
        timeout=timeout,
    )
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict):
        raise HubContractError("Hub cutover status must be an object")
    metrics = payload.get("metrics")
    if not isinstance(metrics, list):
        raise HubContractError("Hub cutover status has no metric matrix")
    match = next(
        (
            item
            for item in metrics
            if isinstance(item, dict)
            and str(item.get("metric_id") or "") == metric_id
            and str(item.get("definition_version") or "")
            == definition_version
        ),
        None,
    )
    if match is None:
        raise HubContractError(
            "Consumer definition is not registered on the Hub cutover matrix"
        )
    state = match.get("cutover")
    if not isinstance(state, dict):
        state = match
    effective_state = str(
        state.get("effective_state") or "unavailable"
    ).strip()
    promoted = state.get("promotion_authorised") is True
    latest = state.get("latest_decision") or {}
    rollback_active = bool(
        isinstance(latest, dict) and latest.get("action") == "rollback"
    ) or effective_state == "rolled_back"
    if promoted and effective_state != "v2_accepted":
        raise HubContractError(
            "Hub cutover authority is internally inconsistent"
        )
    if rollback_active:
        promoted = False
    reasons = state.get("blocked_reasons") or []
    if not isinstance(reasons, list):
        raise HubContractError("Hub cutover blocked reasons are invalid")
    return CutoverAuthority(
        metric_id=metric_id,
        definition_version=definition_version,
        promotion_authorised=promoted,
        effective_state=effective_state,
        rollback_active=rollback_active,
        blocked_reasons=tuple(
            str(item) for item in reasons if str(item).strip()
        ),
    )


@dataclass(frozen=True)
class CurrentPeopleContract:
    schema_version: int
    contract_version: str
    mode: str
    generated_at: str
    period: dict[str, Any]
    source_freshness: tuple[dict[str, Any], ...]
    complete: bool
    blocked_reasons: tuple[str, ...]
    rows: tuple[dict[str, Any], ...]
    response_fingerprint: str

    @property
    def snapshot_id(self) -> str:
        explicit = str(
            self.period.get("snapshot_id")
            or self.period.get("contract_snapshot_id")
            or ""
        ).strip()
        return explicit or self.response_fingerprint

    def by_source_identity(
        self, source: str
    ) -> dict[str, dict[str, Any]]:
        result: dict[str, dict[str, Any]] = {}
        for row in self.rows:
            identities = row.get("source_identities") or {}
            if isinstance(identities, dict):
                values = identities.get(source) or []
            elif isinstance(identities, list):
                values = [
                    value
                    for value in identities
                    if isinstance(value, dict)
                    and str(value.get("source") or "") == source
                ]
            else:
                raise HubContractError(
                    "source identities must be a list or source-keyed object"
                )
            for value in values:
                source_id = str(
                    (
                        value.get("source_id")
                        or value.get("source_record_id")
                    )
                    if isinstance(value, dict)
                    else value
                ).strip()
                if not source_id:
                    continue
                if source_id in result:
                    raise HubContractError(
                        f"duplicate {source} source identity {source_id}"
                    )
                result[source_id] = row
        return result


def validate_current_people_contract(
    payload: Any,
    *,
    max_age_hours: int,
    expected_contract_version: str | None = None,
    require_complete: bool = True,
) -> CurrentPeopleContract:
    if not isinstance(payload, dict):
        raise HubContractError("Hub current-people response must be an object")
    try:
        schema_version = int(payload.get("schema_version"))
    except (TypeError, ValueError) as exc:
        raise HubContractError("Hub current-people schema version is invalid") from exc
    if schema_version < 1:
        raise HubContractError("Hub current-people schema version is unsupported")
    contract_version = str(payload.get("contract_version") or "").strip()
    if not contract_version:
        raise HubContractError("Hub current-people contract version is missing")
    if (
        expected_contract_version
        and contract_version != expected_contract_version
    ):
        raise HubContractError(
            "Hub current-people contract version does not match the consumer"
        )
    mode = str(payload.get("mode") or "").strip().lower()
    if mode not in {"shadow", "accepted", "live"}:
        raise HubContractError("Hub current-people mode is invalid")
    generated = _utc_datetime(payload.get("generated_at"), "generated_at")
    age_hours = (datetime.now(UTC) - generated).total_seconds() / 3600
    if age_hours < -1 or age_hours > max_age_hours:
        raise HubContractError(
            f"Hub current-people contract is outside the {max_age_hours}-hour freshness window"
        )
    period = payload.get("period")
    if not isinstance(period, dict):
        raise HubContractError("Hub current-people period is missing")
    if str(period.get("timezone") or "") != BRISBANE_TIMEZONE:
        raise HubContractError("Hub current-people period is not Brisbane-governed")
    period_id = str(
        period.get("period_id") or period.get("id") or ""
    ).strip().lower()
    if period_id not in ALLOWED_PERIODS:
        raise HubContractError("Hub current-people period id is invalid")
    source_freshness = payload.get("source_freshness")
    if not isinstance(source_freshness, (list, dict)):
        raise HubContractError("Hub current-people source freshness is missing")
    freshness_rows = (
        list(source_freshness.values())
        if isinstance(source_freshness, dict)
        else source_freshness
    )
    if any(not isinstance(row, dict) for row in freshness_rows):
        raise HubContractError("Hub current-people source freshness is invalid")
    complete = payload.get("complete") is True
    blocked = payload.get("blocked_reasons") or []
    if not isinstance(blocked, list):
        raise HubContractError("Hub current-people blocked reasons are invalid")
    blocked_reasons = tuple(
        str(item).strip() for item in blocked if str(item).strip()
    )
    if require_complete and (not complete or blocked_reasons):
        raise HubContractError(
            "Hub current-people contract is blocked or incomplete"
        )
    rows = payload.get("rows")
    if not isinstance(rows, list):
        raise HubContractError("Hub current-people rows are missing")
    person_ids: set[str] = set()
    cleaned: list[dict[str, Any]] = []
    for position, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            raise HubContractError(
                f"Hub current-people row {position} is not an object"
            )
        person_id = str(row.get("person_id") or "").strip()
        if not person_id or person_id in person_ids:
            raise HubContractError(
                f"Hub current-people row {position} has an invalid person_id"
            )
        person_ids.add(person_id)
        identities = row.get("source_identities")
        if not isinstance(identities, (dict, list)):
            raise HubContractError(
                f"Hub current-people row {position} has no source identities"
            )
        sources = (
            set(identities)
            if isinstance(identities, dict)
            else {
                str(item.get("source") or "")
                for item in identities
                if isinstance(item, dict)
            }
        )
        if sources - {"ghl", "trainerize"}:
            raise HubContractError(
                f"Hub current-people row {position} exposes an unapproved identity source"
            )
        for required in (
            "lifecycle",
            "service_relationships",
            "entitlements",
            "payment_accounts",
        ):
            if required not in row:
                raise HubContractError(
                    f"Hub current-people row {position} is missing {required}"
                )
        if not isinstance(row["lifecycle"], dict):
            raise HubContractError(
                f"Hub current-people row {position} lifecycle is invalid"
            )
        if any(
            not isinstance(row[field], list)
            for field in (
                "service_relationships",
                "entitlements",
                "payment_accounts",
            )
        ):
            raise HubContractError(
                f"Hub current-people row {position} has an invalid contract section"
            )
        cleaned.append(dict(row))
    return CurrentPeopleContract(
        schema_version=schema_version,
        contract_version=contract_version,
        mode=mode,
        generated_at=generated.isoformat(),
        period=dict(period),
        source_freshness=tuple(dict(row) for row in freshness_rows),
        complete=complete,
        blocked_reasons=blocked_reasons,
        rows=tuple(cleaned),
        response_fingerprint=fingerprint(payload),
    )


def fetch_current_people(
    *,
    period: str,
    max_age_hours: int,
    expected_contract_version: str | None = None,
    require_complete: bool = True,
    timeout: int = 20,
    session: requests.Session | None = None,
) -> CurrentPeopleContract:
    period = str(period or "").strip().lower()
    if period not in ALLOWED_PERIODS:
        raise HubContractError("period must be week, 28d or 90d")
    client = session or requests
    response = client.get(
        f"{_reporting_base_url()}{CURRENT_PEOPLE_PATH}",
        headers={"X-Hub-Secret": _secret()},
        params={"period": period},
        timeout=timeout,
    )
    response.raise_for_status()
    return validate_current_people_contract(
        response.json(),
        max_age_hours=max_age_hours,
        expected_contract_version=expected_contract_version,
        require_complete=require_complete,
    )


@dataclass(frozen=True)
class ExactParity:
    equivalent: bool
    legacy_count: int
    hub_count: int
    missing_from_hub: tuple[str, ...]
    missing_from_legacy: tuple[str, ...]
    changed: tuple[str, ...]
    legacy_fingerprint: str
    hub_fingerprint: str
    legacy_identity_fingerprint: str
    hub_identity_fingerprint: str
    legacy_classification_fingerprint: str
    hub_classification_fingerprint: str

    @property
    def unexplained_event_count(self) -> int:
        return (
            len(self.missing_from_hub)
            + len(self.missing_from_legacy)
            + len(self.changed)
        )


def exact_parity(
    legacy_rows: Iterable[Any],
    hub_rows: Iterable[Any],
    *,
    key: Callable[[Any], str],
    projection: Callable[[Any], Any],
) -> ExactParity:
    def indexed(rows: Iterable[Any], label: str) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for row in rows:
            row_key = str(key(row) or "").strip()
            if not row_key or row_key in result:
                raise HubContractError(
                    f"{label} parity rows contain a missing or duplicate key"
                )
            result[row_key] = projection(row)
        return result

    legacy = indexed(legacy_rows, "legacy")
    hub = indexed(hub_rows, "Hub")
    legacy_keys = set(legacy)
    hub_keys = set(hub)
    changed = tuple(
        sorted(
            item
            for item in legacy_keys & hub_keys
            if _canonical_json(legacy[item]) != _canonical_json(hub[item])
        )
    )
    missing_from_hub = tuple(sorted(legacy_keys - hub_keys))
    missing_from_legacy = tuple(sorted(hub_keys - legacy_keys))
    legacy_fingerprint = fingerprint(legacy)
    hub_fingerprint = fingerprint(hub)
    legacy_identity_fingerprint = fingerprint(sorted(legacy_keys))
    hub_identity_fingerprint = fingerprint(sorted(hub_keys))
    legacy_classification_fingerprint = fingerprint(legacy)
    hub_classification_fingerprint = fingerprint(hub)
    return ExactParity(
        equivalent=(
            not missing_from_hub
            and not missing_from_legacy
            and not changed
            and legacy_fingerprint == hub_fingerprint
        ),
        legacy_count=len(legacy),
        hub_count=len(hub),
        missing_from_hub=missing_from_hub,
        missing_from_legacy=missing_from_legacy,
        changed=changed,
        legacy_fingerprint=legacy_fingerprint,
        hub_fingerprint=hub_fingerprint,
        legacy_identity_fingerprint=legacy_identity_fingerprint,
        hub_identity_fingerprint=hub_identity_fingerprint,
        legacy_classification_fingerprint=(
            legacy_classification_fingerprint
        ),
        hub_classification_fingerprint=hub_classification_fingerprint,
    )


def publish_parallel_result(
    *,
    metric_id: str,
    definition_version: str,
    period_start: str,
    period_end: str,
    comparison_cycle: str,
    source_run_ids: dict[str, str],
    parity: ExactParity,
    hub_source_complete: bool = True,
    hub_source_fresh: bool = True,
    extra_evidence: dict[str, Any] | None = None,
    timeout: int = 20,
    session: requests.Session | None = None,
) -> dict[str, Any]:
    evidence = {
        "period_id": "contract",
        "comparison_cycle_id": str(comparison_cycle),
        "source_run_id": str(
            source_run_ids.get("hub_current_people")
            or next(iter(source_run_ids.values()), "")
        ),
        "classification": (
            "exact_match" if parity.equivalent else "unresolved"
        ),
        "source_run_ids": {
            str(key): str(value)
            for key, value in sorted(source_run_ids.items())
        },
        "legacy_identity_fingerprint": (
            parity.legacy_identity_fingerprint
        ),
        "hub_identity_fingerprint": parity.hub_identity_fingerprint,
        "legacy_classification_fingerprint": (
            parity.legacy_classification_fingerprint
        ),
        "hub_classification_fingerprint": (
            parity.hub_classification_fingerprint
        ),
        "legacy_only_count": len(parity.missing_from_hub),
        "hub_only_count": len(parity.missing_from_legacy),
        "missing_from_hub_count": len(parity.missing_from_hub),
        "missing_from_legacy_count": len(parity.missing_from_legacy),
        "changed_count": len(parity.changed),
        "unexplained_event_count": parity.unexplained_event_count,
        "unexplained_cents": 0,
        "hub_source_complete": bool(hub_source_complete),
        "hub_source_fresh": bool(hub_source_fresh),
        "domain_guards": {
            "fresh_complete_hub_sources": bool(
                hub_source_complete and hub_source_fresh
            ),
            "exact_identity_fingerprints": (
                parity.legacy_identity_fingerprint
                == parity.hub_identity_fingerprint
            ),
            "exact_classification_fingerprints": (
                parity.legacy_classification_fingerprint
                == parity.hub_classification_fingerprint
            ),
            "zero_set_differences": (
                not parity.missing_from_hub
                and not parity.missing_from_legacy
            ),
            "legacy_fallback_protected": True,
        },
        **(extra_evidence or {}),
    }
    client = session or requests
    response = client.post(
        f"{_reporting_base_url()}{PARALLEL_RESULTS_PATH}",
        headers={"X-Hub-Secret": _secret()},
        json={
            "metric_id": metric_id,
            "definition_version": definition_version,
            "period_start": period_start,
            "period_end": period_end,
            "legacy_value": parity.legacy_count,
            "v2_value": parity.hub_count,
            "variance_classification": (
                "exact_match" if parity.equivalent else "unresolved"
            ),
            "unexplained_event_count": parity.unexplained_event_count,
            "unexplained_cents": 0,
            "evidence": evidence,
            "request_cutover_acceptance": False,
        },
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()
