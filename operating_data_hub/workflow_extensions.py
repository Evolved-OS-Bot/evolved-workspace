from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any, Iterable

from .contracts import canonical_json, fingerprint


CONTRACT_VERSION = "hub-workflow-extension-v1"
ACCEPTED_STATE = "accepted"
INTERNAL_TASK = "internal_task"


@dataclass(frozen=True)
class WorkflowPolicy:
    workflow_key: str
    definition_version: str
    authority_state: str
    owner_rule: str
    default_owner_role: str
    cooldown_hours: int
    required_cutover_consumer: str | None = None
    minimum_distinct_parity_cycles: int = 0
    required_cutover_schema_version: int | None = None
    primary_owner_name: str | None = None
    primary_owner_user_id: str | None = None
    oversight_owner_name: str | None = None
    oversight_owner_user_id: str | None = None
    controlled_test_approval_ref: str | None = None
    allowed_action_types: tuple[str, ...] = (INTERNAL_TASK,)
    consent_rule: str = "internal_only"


WORKFLOW_POLICIES: dict[str, WorkflowPolicy] = {
    "retention_intervention_review": WorkflowPolicy(
        "retention_intervention_review",
        "retention-intervention-review-v1",
        "proposal_only",
        "accepted_policy_owner_required",
        "Member Experience",
        168,
        "retention_intelligence",
        2,
        None,
        "Alyssa Crighton (Piper Mae)",
        "WOBADTaoxWfMqNRqHmX0",
        "Megan Brown",
        "adexBwouW9iBHpmiXrnN",
    ),
    "conversation_support_routing": WorkflowPolicy(
        "conversation_support_routing",
        "conversation-support-routing-v1",
        "proposal_only",
        "admin_eve",
        "Admin Eve",
        24,
        "conversation_triage",
        2,
        None,
        "Admin Eve",
        "EtONSa9U2pTpyOpX1hX8",
        None,
        None,
        "build7-conversation-controlled-test-2026-08-03",
    ),
    "pt_booking_continuity": WorkflowPolicy(
        "pt_booking_continuity",
        "pt-booking-continuity-v1",
        "proposal_only",
        "admin_eve",
        "Admin Eve",
        72,
        "pt_booking_continuity",
        2,
    ),
    "revenue_exception_review": WorkflowPolicy(
        "revenue_exception_review",
        "revenue-exception-review-v1",
        "proposal_only",
        "admin_eve",
        "Admin Eve",
        72,
        "revenue_control",
        1,
        2,
    ),
    "onboarding_outcome_followup": WorkflowPolicy(
        "onboarding_outcome_followup",
        "onboarding-outcome-followup-v1",
        "internal_task_allowed",
        "assigned_trainer_then_admin_eve",
        "Admin Eve",
        24,
    ),
    "strength_assessment_outcome_followup": WorkflowPolicy(
        "strength_assessment_outcome_followup",
        "sa-attendance-followup-v1",
        "internal_task_allowed",
        "assigned_trainer_then_admin_eve",
        "Admin Eve",
        24,
    ),
}


class DecisionContractError(ValueError):
    pass


def _required_text(payload: dict[str, Any], field: str) -> str:
    value = str(payload.get(field) or "").strip()
    if not value:
        raise DecisionContractError(f"{field} is required")
    return value


def _parse_datetime(value: Any, field: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise DecisionContractError(
            f"{field} must be an ISO-8601 datetime"
        ) from exc
    if parsed.tzinfo is None:
        raise DecisionContractError(f"{field} must include a timezone")
    return parsed.astimezone(UTC)


def _nonnegative_int(value: Any, field: str) -> int:
    try:
        parsed = int(value or 0)
    except (TypeError, ValueError) as exc:
        raise DecisionContractError(
            f"{field} must be a non-negative integer"
        ) from exc
    if parsed < 0:
        raise DecisionContractError(
            f"{field} must be a non-negative integer"
        )
    return parsed


def validate_decision_envelope(payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("contract_version") != CONTRACT_VERSION:
        raise DecisionContractError(
            f"contract_version must be {CONTRACT_VERSION}"
        )
    workflow_key = _required_text(payload, "workflow_key")
    if workflow_key not in WORKFLOW_POLICIES:
        raise DecisionContractError(f"unknown workflow_key: {workflow_key}")
    decision_id = _required_text(payload, "decision_id")
    try:
        decision_version = int(payload.get("decision_version"))
    except (TypeError, ValueError) as exc:
        raise DecisionContractError(
            "decision_version must be a positive integer"
        ) from exc
    if decision_version < 1:
        raise DecisionContractError(
            "decision_version must be a positive integer"
        )
    subject = dict(payload.get("subject") or {})
    person_id = _required_text(subject, "person_id")
    source = dict(payload.get("source") or {})
    source_system = _required_text(source, "system")
    source_snapshot_id = _required_text(source, "snapshot_id")
    source_observed_at = _parse_datetime(
        source.get("observed_at"), "source.observed_at"
    )
    evidence = list(payload.get("evidence") or [])
    if not evidence:
        raise DecisionContractError("evidence must contain at least one item")
    for index, item in enumerate(evidence):
        if not isinstance(item, dict):
            raise DecisionContractError(
                f"evidence[{index}] must be an object"
            )
        _required_text(item, "authority")
        _required_text(item, "record_id")
        _required_text(item, "fingerprint")
    action = dict(payload.get("action") or {})
    action_type = _required_text(action, "type")
    _required_text(action, "title")
    _required_text(action, "body")
    owner = dict(action.get("owner") or {})
    owner_role = str(owner.get("role") or "").strip()
    owner_user_id = str(owner.get("user_id") or "").strip()
    escalation_owner = dict(action.get("escalation_owner") or {})
    due_at = (
        _parse_datetime(action["due_at"], "action.due_at")
        if action.get("due_at")
        else None
    )
    if action_type == INTERNAL_TASK and due_at is None:
        raise DecisionContractError(
            "action.due_at is required for an internal task"
        )
    acceptance = dict(payload.get("acceptance") or {})
    acceptance_state = _required_text(acceptance, "state")
    _required_text(acceptance, "definition_id")
    decision_authorised = (
        acceptance.get("decision_authorised", False) is True
    )
    if decision_authorised:
        _required_text(acceptance, "accepted_by")
    cutover = dict(acceptance.get("cutover") or {})
    exception = dict(payload.get("exception") or {})
    _required_text(exception, "code")
    exception_status = _required_text(exception, "status")
    _required_text(exception, "severity")
    controls = dict(payload.get("controls") or {})
    suppression_reasons = sorted(
        {
            str(reason).strip()
            for reason in controls.get("suppression_reasons") or []
            if str(reason).strip()
        }
    )
    consent = dict(controls.get("consent") or {})
    consent_state = str(consent.get("state") or "not_required").strip()
    decision_fingerprint = fingerprint(payload)
    idempotency_key = fingerprint(
        {
            "contract_version": CONTRACT_VERSION,
            "workflow_key": workflow_key,
            "decision_id": decision_id,
            "decision_version": decision_version,
            "person_id": person_id,
            "action_type": action_type,
            "dedupe_scope": str(
                controls.get("dedupe_scope") or workflow_key
            ),
        }
    )
    return {
        **payload,
        "workflow_key": workflow_key,
        "decision_id": decision_id,
        "decision_version": decision_version,
        "subject": {**subject, "person_id": person_id},
        "source": {
            **source,
            "system": source_system,
            "snapshot_id": source_snapshot_id,
            "observed_at": source_observed_at.isoformat(),
            "complete": source.get("complete") is True,
            "fresh": source.get("fresh") is True,
        },
        "exception": {**exception, "status": exception_status},
        "action": {
            **action,
            "type": action_type,
            "owner": {
                **owner,
                "role": owner_role,
                "user_id": owner_user_id,
            },
            "escalation_owner": {
                **escalation_owner,
                "name": str(
                    escalation_owner.get("name") or ""
                ).strip(),
                "user_id": str(
                    escalation_owner.get("user_id") or ""
                ).strip(),
            },
            "due_at": due_at.isoformat() if due_at else None,
        },
        "acceptance": {
            **acceptance,
            "state": acceptance_state,
            "decision_authorised": decision_authorised,
            "cutover": {
                **cutover,
                "consumer": str(cutover.get("consumer") or "").strip(),
                "authorised": cutover.get("authorised") is True,
                "promotion_authorised": (
                    cutover.get("promotion_authorised") is True
                ),
                "status_record_id": str(
                    cutover.get("status_record_id") or ""
                ).strip(),
                "status_fingerprint": str(
                    cutover.get("status_fingerprint") or ""
                ).strip(),
                "distinct_parity_cycles": _nonnegative_int(
                    cutover.get("distinct_parity_cycles"),
                    "acceptance.cutover.distinct_parity_cycles",
                ),
                "fresh_exact_parity": (
                    cutover.get("fresh_exact_parity") is True
                ),
                "contract_schema_version": _nonnegative_int(
                    cutover.get("contract_schema_version"),
                    "acceptance.cutover.contract_schema_version",
                ),
            },
        },
        "controls": {
            **controls,
            "dedupe_scope": str(
                controls.get("dedupe_scope") or workflow_key
            ),
            "suppression_reasons": suppression_reasons,
            "consent": {**consent, "state": consent_state},
        },
        "decision_fingerprint": decision_fingerprint,
        "idempotency_key": idempotency_key,
    }


def _prior_blocks(
    prior: dict[str, Any],
    *,
    decision: dict[str, Any],
    policy: WorkflowPolicy,
    now: datetime,
) -> str | None:
    if prior.get("idempotency_key") == decision["idempotency_key"]:
        return "duplicate"
    if prior.get("workflow_key") != decision["workflow_key"]:
        return None
    if prior.get("person_id") != decision["subject"]["person_id"]:
        return None
    if prior.get("dedupe_scope") != decision["controls"]["dedupe_scope"]:
        return None
    if prior.get("state") not in {"queued", "dispatched"}:
        return None
    active_at_raw = (
        prior.get("dispatched_at")
        or prior.get("queued_at")
        or prior.get("created_at")
    )
    if not active_at_raw:
        return None
    if isinstance(active_at_raw, datetime):
        active_at = active_at_raw
        if active_at.tzinfo is None:
            active_at = active_at.replace(tzinfo=UTC)
        active_at = active_at.astimezone(UTC)
    else:
        active_at = _parse_datetime(active_at_raw, "prior.active_at")
    if active_at + timedelta(hours=policy.cooldown_hours) > now:
        return "cooldown"
    return None


def plan_workflow_extension(
    payload: dict[str, Any],
    *,
    prior_records: Iterable[dict[str, Any]] = (),
    now: datetime | None = None,
) -> dict[str, Any]:
    decision = validate_decision_envelope(payload)
    policy = WORKFLOW_POLICIES[decision["workflow_key"]]
    observed_at = (now or datetime.now(UTC)).astimezone(UTC)
    reasons: list[str] = []
    preview_reasons: list[str] = []
    suppression_reasons: list[str] = []
    rejection_reasons: list[str] = []

    if decision["acceptance"]["state"] != ACCEPTED_STATE:
        preview_reasons.append("decision_not_accepted")
    if not decision["acceptance"]["decision_authorised"]:
        preview_reasons.append("workflow_decision_not_authorised")
    if not bool(decision["source"].get("complete")):
        preview_reasons.append("source_incomplete")
    if not bool(decision["source"].get("fresh")):
        preview_reasons.append("source_stale")
    test_authority = dict(
        decision["acceptance"].get("test_authority") or {}
    )
    controlled_test_authorised = bool(
        policy.controlled_test_approval_ref
        and decision["controls"].get("controlled_test") is True
        and decision["subject"].get("test_contact") is True
        and str(decision["subject"].get("email") or "")
        .strip()
        .lower()
        .endswith(".invalid")
        and test_authority.get("approval_ref")
        == policy.controlled_test_approval_ref
        and test_authority.get("approved_by") == "Peter Brown"
        and test_authority.get("reversible") is True
    )
    if (
        policy.authority_state != "internal_task_allowed"
        and not controlled_test_authorised
    ):
        preview_reasons.append("workflow_policy_not_accepted")
    if policy.required_cutover_consumer:
        cutover = decision["acceptance"]["cutover"]
        if (
            cutover["consumer"] != policy.required_cutover_consumer
            or not cutover["authorised"]
            or not cutover["promotion_authorised"]
            or not cutover["status_record_id"]
            or not cutover["status_fingerprint"]
        ):
            preview_reasons.append("consumer_cutover_not_authorised")
        if (
            not cutover["fresh_exact_parity"]
            or cutover["distinct_parity_cycles"]
            < policy.minimum_distinct_parity_cycles
        ):
            preview_reasons.append("consumer_cutover_parity_not_met")
        if (
            policy.required_cutover_schema_version is not None
            and cutover["contract_schema_version"]
            != policy.required_cutover_schema_version
        ):
            preview_reasons.append("consumer_cutover_schema_mismatch")
    if decision["action"]["type"] not in policy.allowed_action_types:
        rejection_reasons.append("side_effect_not_allowed")
    if decision["action"]["type"] != INTERNAL_TASK:
        rejection_reasons.append("client_or_source_side_effect_forbidden")
    if decision["controls"]["consent"]["state"] == "required_missing":
        suppression_reasons.append("consent_missing")
    if decision["exception"]["status"] != "open":
        suppression_reasons.append("exception_not_open")
    if decision["controls"]["suppression_reasons"]:
        suppression_reasons.extend(
            decision["controls"]["suppression_reasons"]
        )
    if (
        not decision["action"]["owner"]["role"]
        or not decision["action"]["owner"]["user_id"]
    ):
        preview_reasons.append("exact_owner_missing")
    if policy.primary_owner_user_id:
        if (
            decision["action"]["owner"]["role"]
            != policy.default_owner_role
            or decision["action"]["owner"]["user_id"]
            != policy.primary_owner_user_id
        ):
            preview_reasons.append("policy_owner_mismatch")
        if policy.oversight_owner_user_id:
            escalation = decision["action"]["escalation_owner"]
            if (
                escalation["user_id"] != policy.oversight_owner_user_id
                or escalation["name"] != policy.oversight_owner_name
            ):
                preview_reasons.append("oversight_owner_missing")
        availability = str(
            decision["controls"].get("owner_availability") or "unknown"
        ).strip().lower()
        if availability != "available":
            preview_reasons.append("primary_owner_unavailable")

    if rejection_reasons:
        state = "rejected"
        reasons.extend(rejection_reasons)
    elif preview_reasons:
        state = "preview"
        reasons.extend(preview_reasons)
    elif suppression_reasons:
        state = "suppressed"
        reasons.extend(suppression_reasons)
    else:
        state = "queued"

    if state == "queued":
        for prior in prior_records:
            blocked = _prior_blocks(
                prior,
                decision=decision,
                policy=policy,
                now=observed_at,
            )
            if blocked:
                state = blocked
                reasons.append(
                    "idempotency_key_already_recorded"
                    if blocked == "duplicate"
                    else "workflow_cooldown_active"
                )
                break

    audit = {
        "contract_version": CONTRACT_VERSION,
        "policy_version": policy.definition_version,
        "planned_at": observed_at.isoformat(),
        "decision_fingerprint": decision["decision_fingerprint"],
        "source_snapshot_id": decision["source"]["snapshot_id"],
        "acceptance_state": decision["acceptance"]["state"],
        "decision_authorised": decision["acceptance"][
            "decision_authorised"
        ],
        "cutover": decision["acceptance"]["cutover"],
        "controlled_test_authorised": controlled_test_authorised,
        "consent_state": decision["controls"]["consent"]["state"],
        "suppression_reasons": decision["controls"][
            "suppression_reasons"
        ],
        "result_state": state,
        "result_reasons": sorted(set(reasons)),
    }
    return {
        "contract_version": CONTRACT_VERSION,
        "policy": {
            "workflow_key": policy.workflow_key,
            "definition_version": policy.definition_version,
            "authority_state": policy.authority_state,
            "owner_rule": policy.owner_rule,
            "default_owner_role": policy.default_owner_role,
            "cooldown_hours": policy.cooldown_hours,
            "required_cutover_consumer": (
                policy.required_cutover_consumer
            ),
            "minimum_distinct_parity_cycles": (
                policy.minimum_distinct_parity_cycles
            ),
            "required_cutover_schema_version": (
                policy.required_cutover_schema_version
            ),
            "primary_owner_name": policy.primary_owner_name,
            "primary_owner_user_id": policy.primary_owner_user_id,
            "oversight_owner_name": policy.oversight_owner_name,
            "oversight_owner_user_id": policy.oversight_owner_user_id,
            "controlled_test_approval_ref": (
                policy.controlled_test_approval_ref
            ),
            "allowed_action_types": list(policy.allowed_action_types),
            "consent_rule": policy.consent_rule,
        },
        "decision": decision,
        "outbox": {
            "idempotency_key": decision["idempotency_key"],
            "workflow_key": decision["workflow_key"],
            "decision_id": decision["decision_id"],
            "decision_version": decision["decision_version"],
            "person_id": decision["subject"]["person_id"],
            "contact_id": decision["subject"].get("contact_id"),
            "action_type": decision["action"]["type"],
            "owner_role": decision["action"]["owner"]["role"],
            "owner_user_id": decision["action"]["owner"]["user_id"],
            "due_at": decision["action"]["due_at"],
            "dedupe_scope": decision["controls"]["dedupe_scope"],
            "state": state,
            "created_at": observed_at.isoformat(),
            "queued_at": (
                observed_at.isoformat() if state == "queued" else None
            ),
            "payload": decision["action"],
            "audit": audit,
        },
        "audit": audit,
    }


def workflow_policy_registry() -> dict[str, Any]:
    return {
        "contract_version": CONTRACT_VERSION,
        "side_effect_boundary": [INTERNAL_TASK],
        "policies": [
            {
                "workflow_key": policy.workflow_key,
                "definition_version": policy.definition_version,
                "authority_state": policy.authority_state,
                "owner_rule": policy.owner_rule,
                "default_owner_role": policy.default_owner_role,
                "cooldown_hours": policy.cooldown_hours,
                "required_cutover_consumer": (
                    policy.required_cutover_consumer
                ),
                "minimum_distinct_parity_cycles": (
                    policy.minimum_distinct_parity_cycles
                ),
                "required_cutover_schema_version": (
                    policy.required_cutover_schema_version
                ),
                "primary_owner_name": policy.primary_owner_name,
                "primary_owner_user_id": policy.primary_owner_user_id,
                "oversight_owner_name": policy.oversight_owner_name,
                "oversight_owner_user_id": (
                    policy.oversight_owner_user_id
                ),
                "controlled_test_approval_ref": (
                    policy.controlled_test_approval_ref
                ),
                "allowed_action_types": list(policy.allowed_action_types),
                "consent_rule": policy.consent_rule,
            }
            for policy in WORKFLOW_POLICIES.values()
        ],
        "canonical_fingerprint": fingerprint(
            canonical_json(
                [
                    policy.__dict__
                    for policy in WORKFLOW_POLICIES.values()
                ]
            )
        ),
    }
