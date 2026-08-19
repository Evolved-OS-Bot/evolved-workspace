from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from typing import Any


RULE_VERSION = "sa-prequalification-state-v1-observer"
STAGE_STATES = {"not_asked", "asked_awaiting_reply", "complete"}
STAGE_KEYS = (
    "acknowledge_anchor",
    "goals_motivation",
    "medical",
    "injury",
    "exercise_history",
    "support_preference",
    "relevant_social_proof",
    "obstacles_readiness",
    "assessment_preframe",
    "trainer_handoff",
)
REVIEW_ACTIONS = {"approved_unchanged", "approved_edited", "rejected"}


def _iso(value: Any, field: str) -> str:
    try:
        parsed = datetime.fromisoformat(str(value or "").replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field} must be an ISO datetime") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"{field} must include a timezone")
    return parsed.astimezone(UTC).isoformat()


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        default=str,
    )


def stable_id(prefix: str, *parts: Any) -> str:
    digest = hashlib.sha256(
        "|".join(str(part or "") for part in parts).encode("utf-8")
    ).hexdigest()
    return f"{prefix}_{digest[:40]}"


def validate_stage(stage: Any, *, label: str) -> dict[str, Any]:
    if not isinstance(stage, dict):
        raise ValueError(f"{label} must be an object")
    state = str(stage.get("state") or "").strip().lower()
    if state not in STAGE_STATES:
        raise ValueError(f"{label}.state is invalid")
    evidence_ids = [
        str(value).strip()
        for value in stage.get("evidence_message_ids") or []
        if str(value).strip()
    ]
    return {
        "state": state,
        "applicability": str(
            stage.get("applicability") or "applicable"
        ).strip(),
        "value": stage.get("value"),
        "evidence_message_ids": evidence_ids,
        "outstanding_question_fingerprint": str(
            stage.get("outstanding_question_fingerprint") or ""
        ).strip()
        or None,
        "confidence": str(stage.get("confidence") or "unavailable").strip(),
        "reason": str(stage.get("reason") or "").strip() or None,
    }


def validate_observation_run(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("payload must be an object")
    source_run_id = str(payload.get("source_run_id") or "").strip()
    if not source_run_id:
        raise ValueError("source_run_id is required")
    status = str(payload.get("status") or "").strip().lower()
    if status not in {"complete", "partial", "failed"}:
        raise ValueError("status must be complete, partial or failed")
    complete = bool(payload.get("complete"))
    if complete != (status == "complete"):
        raise ValueError("complete must match status")
    observed_at = _iso(payload.get("observed_at"), "observed_at")
    rows = payload.get("rows") or []
    if not isinstance(rows, list):
        raise ValueError("rows must be an array")
    if status == "failed" and rows:
        raise ValueError("failed observation cannot contain rows")
    cleaned = []
    seen: set[str] = set()
    for index, source in enumerate(rows):
        if not isinstance(source, dict):
            raise ValueError(f"rows[{index}] must be an object")
        appointment_id = str(source.get("appointment_id") or "").strip()
        contact_id = str(source.get("contact_id") or "").strip()
        if not appointment_id or not contact_id:
            raise ValueError(f"rows[{index}] requires appointment and contact IDs")
        if appointment_id in seen:
            raise ValueError("appointment_id must be unique within a run")
        seen.add(appointment_id)
        stages_source = source.get("stages") or {}
        if not isinstance(stages_source, dict):
            raise ValueError(f"rows[{index}].stages must be an object")
        stages = {
            key: validate_stage(
                stages_source.get(key) or {"state": "not_asked"},
                label=f"rows[{index}].stages.{key}",
            )
            for key in STAGE_KEYS
        }
        draft = source.get("draft")
        if draft is not None and not isinstance(draft, dict):
            raise ValueError(f"rows[{index}].draft must be an object")
        cleaned.append(
            {
                "appointment_id": appointment_id,
                "contact_id": contact_id,
                "conversation_id": str(
                    source.get("conversation_id") or ""
                ).strip()
                or None,
                "contact_name": str(source.get("contact_name") or "").strip()
                or None,
                "scheduled_at": _iso(
                    source.get("scheduled_at"),
                    f"rows[{index}].scheduled_at",
                ),
                "appointment_status": str(
                    source.get("appointment_status") or "confirmed"
                ).strip().lower(),
                "case_state": str(
                    source.get("case_state") or "observer"
                ).strip().lower(),
                "first_incomplete_stage": str(
                    source.get("first_incomplete_stage") or ""
                ).strip()
                or None,
                "next_action": str(source.get("next_action") or "").strip()
                or None,
                "blocked_reasons": [
                    str(value).strip()
                    for value in source.get("blocked_reasons") or []
                    if str(value).strip()
                ],
                "conversation_complete": bool(
                    source.get("conversation_complete")
                ),
                "conversation_fingerprint": str(
                    source.get("conversation_fingerprint") or ""
                ).strip()
                or None,
                "latest_message_id": str(
                    source.get("latest_message_id") or ""
                ).strip()
                or None,
                "latest_message_at": (
                    _iso(
                        source.get("latest_message_at"),
                        f"rows[{index}].latest_message_at",
                    )
                    if source.get("latest_message_at")
                    else None
                ),
                "stages": stages,
                "facts": source.get("facts") or {},
                "draft": draft,
                "review_context": source.get("review_context") or {},
                "privacy_evidence": source.get("privacy_evidence") or {},
                "rule_version": str(
                    source.get("rule_version") or RULE_VERSION
                ).strip(),
                "model_version": str(
                    source.get("model_version") or ""
                ).strip()
                or None,
                "prompt_version": str(
                    source.get("prompt_version") or ""
                ).strip()
                or None,
            }
        )
    return {
        "schema_version": 1,
        "source": "sa_prequalification_observer",
        "source_run_id": source_run_id,
        "observed_at": observed_at,
        "status": status,
        "complete": complete,
        "cohort_fingerprint": str(
            payload.get("cohort_fingerprint") or ""
        ).strip()
        or None,
        "error_code": str(payload.get("error_code") or "").strip() or None,
        "rows": cleaned,
    }


def validate_review(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("payload must be an object")
    appointment_id = str(payload.get("appointment_id") or "").strip()
    draft_id = str(payload.get("draft_id") or "").strip()
    reviewer = str(payload.get("reviewer") or "").strip()
    action = str(payload.get("action") or "").strip().lower()
    if not appointment_id or not draft_id or not reviewer:
        raise ValueError("appointment_id, draft_id and reviewer are required")
    if action not in REVIEW_ACTIONS:
        raise ValueError("review action is invalid")
    final_wording = str(payload.get("final_wording") or "").strip() or None
    if action == "approved_edited" and not final_wording:
        raise ValueError("edited approval requires final_wording")
    return {
        "appointment_id": appointment_id,
        "draft_id": draft_id,
        "reviewer": reviewer,
        "action": action,
        "final_wording": final_wording,
        "reason_codes": sorted(
            {
                str(value).strip()
                for value in payload.get("reason_codes") or []
                if str(value).strip()
            }
        ),
        "note": str(payload.get("note") or "").strip() or None,
        "reviewed_at": _iso(payload.get("reviewed_at"), "reviewed_at"),
        "send_authorised": False,
    }


def validate_send_claim(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("payload must be an object")
    required = (
        "send_key", "appointment_id", "draft_id", "reviewer", "wording_hash",
        "conversation_fingerprint", "latest_message_id", "scheduled_at", "rule_version",
    )
    cleaned = {key: str(payload.get(key) or "").strip() for key in required}
    if any(not value for value in cleaned.values()):
        raise ValueError("send claim is incomplete")
    cleaned["claimed_at"] = _iso(payload.get("claimed_at"), "claimed_at")
    return cleaned


def validate_send_result(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("payload must be an object")
    send_key = str(payload.get("send_key") or "").strip()
    ghl_message_id = str(payload.get("ghl_message_id") or "").strip() or None
    failure_code = str(payload.get("failure_code") or "").strip() or None
    if not send_key or bool(ghl_message_id) == bool(failure_code):
        raise ValueError("send result requires one of ghl_message_id or failure_code")
    return {
        "send_key": send_key,
        "ghl_message_id": ghl_message_id,
        "failure_code": failure_code,
        "channel": str(payload.get("channel") or "SMS").strip(),
        "completed_at": _iso(payload.get("completed_at"), "completed_at"),
    }


__all__ = [
    "REVIEW_ACTIONS",
    "RULE_VERSION",
    "STAGE_KEYS",
    "STAGE_STATES",
    "canonical_json",
    "stable_id",
    "validate_observation_run",
    "validate_review",
    "validate_send_claim",
    "validate_send_result",
]
