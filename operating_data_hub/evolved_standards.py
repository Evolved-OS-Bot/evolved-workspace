from __future__ import annotations

import re
import statistics
import unicodedata
from collections import defaultdict
from datetime import date, datetime, timedelta
from typing import Any


DEFINITION_VERSION = "evolved-standards-v1-shadow"
EVIDENCE_SCHEMA_VERSION = 1
APPROACHING_RATIO = 0.90
NEWLY_ACHIEVED_DAYS = 30

LEVEL_NAMES = {
    0: "Below Live",
    1: "Live",
    2: "Long",
    3: "Perform",
}
COMPONENT_NAMES = {
    "single_leg_right": "Single-Leg Capacity Right",
    "single_leg_left": "Single-Leg Capacity Left",
    "grip_endurance": "Grip Endurance",
    "spinal_control": "Spinal Control",
}
ALL_COMPONENTS = (
    "single_leg_right",
    "single_leg_left",
    "grip_endurance",
    "spinal_control",
)
FUTURE_PROOFING_STANDARD_NAMES = {
    "deadlift": "Deadlift",
    "atg_split_squat": "ATG Split Squat (average of left and right)",
    "farmer_walk": "DB Farmer Walk",
    "core_progression": "Core (plank progression)",
    "work_capacity": "Running or Rowing",
    "push_ups": "Push Ups",
}
FUTURE_PROOFING_STANDARD_IDS = tuple(
    FUTURE_PROOFING_STANDARD_NAMES
)
FUTURE_PROOFING_MAX_SCORE = 18

EXERCISE_ALIASES = {
    "atg_split_squat": {
        "ATG Split Squat",
        "ATG Split Squat Right",
        "ATG Split Squat Left",
        "Right ATG Split Squat",
        "Left ATG Split Squat",
    },
    "farmer_walk": {
        "Farmer Walk",
        "Farmer Walks",
        "Farmer's Walk",
        "Farmers Walk",
        "Farmer Carry",
        "Farmer's Carry",
        "Farmers Carry",
        "DB Farmer Walk",
        "Dumbbell Farmer Walk",
    },
    "high_plank": {
        "High Plank",
        "Full Plank",
        "Plank",
    },
    "side_plank": {
        "Side Plank",
        "Side Plank Right",
        "Side Plank Left",
        "Right Side Plank",
        "Left Side Plank",
    },
    "toes_to_bar": {
        "Toes to Bar",
        "Strict Toes to Bar",
    },
    "deadlift": {
        "Deadlift",
        "Barbell Deadlift",
        "Conventional Deadlift",
    },
    "push_ups": {
        "Push Up",
        "Push Ups",
        "Push-Up",
        "Push-Ups",
        "Full Push Up",
        "Full Push Ups",
    },
    "run_5km": {
        "5km Run",
        "5 km Run",
        "Run 5km",
        "Run 5 km",
    },
    "run_10km": {
        "10km Run",
        "10 km Run",
        "Run 10km",
        "Run 10 km",
    },
    "run_21km": {
        "21km Run",
        "21 km Run",
        "Run 21km",
        "Run 21 km",
        "Half Marathon Run",
    },
    "row_1000m": {
        "1000m Row",
        "1000 m Row",
        "1km Row",
        "1 km Row",
        "Row 1000m",
        "Row 1000 m",
    },
}


def _key(value: Any) -> str:
    text = unicodedata.normalize("NFKC", str(value or "")).lower()
    text = text.replace("’", "'")
    text = re.sub(r"['`]", "", text)
    return " ".join(re.sub(r"[^a-z0-9]+", " ", text).split())


ALIAS_INDEX = {
    _key(alias): canonical
    for canonical, aliases in EXERCISE_ALIASES.items()
    for alias in aliases
}


def canonical_exercise(value: Any) -> str | None:
    """Return an exact governed alias match; never fuzzy-match an exercise."""
    return ALIAS_INDEX.get(_key(value))


def _number(value: Any) -> float | None:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if result >= 0 else None


def _date(value: Any) -> date | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        return None


def _snapshot_payload(snapshot: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(snapshot, dict):
        return {}
    payload = snapshot.get("payload")
    return payload if isinstance(payload, dict) else snapshot


def _summary(snapshot: dict[str, Any] | None) -> dict[str, Any]:
    payload = _snapshot_payload(snapshot)
    summary = payload.get("summary")
    return summary if isinstance(summary, dict) else {}


def _side(value: Any, exercise_name: Any) -> str | None:
    side = _key(value)
    if side in {"r", "right"}:
        return "right"
    if side in {"l", "left"}:
        return "left"
    name = _key(exercise_name)
    if re.search(r"\bright\b", name):
        return "right"
    if re.search(r"\bleft\b", name):
        return "left"
    return None


def _body_weight(
    assessment: dict[str, Any],
) -> tuple[float | None, dict[str, Any]]:
    raw = assessment.get("bodyWeight")
    if not isinstance(raw, dict):
        return None, {
            "sufficient": False,
            "reason": "bodyweight_missing",
        }
    kg = _number(raw.get("kg"))
    raw_day_offset = _number(raw.get("dayOffset"))
    day_offset = (
        abs(raw_day_offset)
        if raw_day_offset is not None
        else None
    )
    quality = str(raw.get("timingQuality") or "").strip()
    unsuitable = _key(quality) in {
        "not available",
        "not suitable",
    }
    if kg is None or kg <= 0 or unsuitable:
        return None, {
            "sufficient": False,
            "reason": "bodyweight_missing_or_unsuitable",
            "timing_quality": quality or None,
            "day_offset": day_offset,
        }
    if day_offset is not None and day_offset > 30:
        return None, {
            "sufficient": False,
            "reason": "bodyweight_more_than_30_days_from_assessment",
            "timing_quality": quality or None,
            "day_offset": day_offset,
        }
    return kg, {
        "sufficient": True,
        "reason": None,
        "timing_quality": quality or None,
        "day_offset": day_offset,
    }


def _result(
    *,
    component: str,
    attempted: bool,
    level: int | None,
    assessment: dict[str, Any],
    source_ids: list[str],
    reason: str | None,
    confidence: str,
    next_level: int | None = None,
    progress_to_next: float | None = None,
    approaching: bool = False,
    raw_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    observed = _date(assessment.get("assessmentDate"))
    return {
        "component_id": component,
        "component": COMPONENT_NAMES[component],
        "assessment_date": observed.isoformat() if observed else None,
        "source_assessment_id": assessment.get("sourceAssessmentId"),
        "source_observation_ids": source_ids,
        "attempted": attempted,
        "sufficient": level is not None,
        "level_number": level,
        "level": LEVEL_NAMES.get(level) if level is not None else None,
        "reason": reason,
        "confidence": confidence,
        "next_level": LEVEL_NAMES.get(next_level),
        "progress_to_next": (
            round(progress_to_next, 3)
            if progress_to_next is not None
            else None
        ),
        "approaching": approaching,
        "raw_result": raw_result or {},
    }


def _split_component(
    assessment: dict[str, Any],
    observations: list[dict[str, Any]],
    *,
    wanted_side: str,
) -> dict[str, Any]:
    component = f"single_leg_{wanted_side}"
    exact = [
        row
        for row in observations
        if canonical_exercise(row.get("exerciseName")) == "atg_split_squat"
    ]
    matching = [
        row
        for row in exact
        if _side(row.get("side"), row.get("exerciseName")) == wanted_side
    ]
    relevant = bool(
        matching
        or any(
            _side(row.get("side"), row.get("exerciseName")) is None
            for row in exact
        )
    )
    if not matching:
        return _result(
            component=component,
            attempted=relevant,
            level=None,
            assessment=assessment,
            source_ids=[
                str(row.get("sourceObservationId") or "")
                for row in exact
                if row.get("sourceObservationId")
            ],
            reason=(
                "split_squat_side_missing_or_ambiguous"
                if relevant
                else "not_tested"
            ),
            confidence="insufficient",
        )
    candidates = []
    for row in matching:
        reps = _number(row.get("reps"))
        if reps is None:
            continue
        candidates.append((reps, _number(row.get("weightKg")) or 0.0, row))
    if not candidates:
        return _result(
            component=component,
            attempted=True,
            level=None,
            assessment=assessment,
            source_ids=[
                str(row.get("sourceObservationId") or "")
                for row in matching
                if row.get("sourceObservationId")
            ],
            reason="split_squat_reps_missing",
            confidence="insufficient",
        )
    reps, load, best = max(candidates, key=lambda item: (item[0], item[1]))
    bodyweight, weight_quality = _body_weight(assessment)
    ratio = load / bodyweight if bodyweight and load > 0 else None
    level = 0
    next_level = 1
    progress = min(1.0, reps / 10.0)
    if reps >= 10:
        level = 1
        next_level = 2
        progress = ratio / 0.50 if ratio is not None else None
        if ratio is not None and ratio >= 0.50:
            level = 2
            next_level = 3
            progress = ratio / 1.00
        if ratio is not None and ratio >= 1.00:
            level = 3
            next_level = None
            progress = None
    approaching = bool(
        next_level is not None
        and progress is not None
        and APPROACHING_RATIO <= progress < 1
    )
    return _result(
        component=component,
        attempted=True,
        level=level,
        assessment=assessment,
        source_ids=[str(best.get("sourceObservationId") or "")],
        reason=None,
        confidence="high",
        next_level=next_level,
        progress_to_next=progress,
        approaching=approaching,
        raw_result={
            "reps": reps,
            "external_load_kg": load,
            "bodyweight_kg": bodyweight,
            "load_to_bodyweight_ratio": (
                round(ratio, 4) if ratio is not None else None
            ),
            "bodyweight_evidence": weight_quality,
        },
    )


def _grip_component(
    assessment: dict[str, Any],
    observations: list[dict[str, Any]],
) -> dict[str, Any]:
    matching = [
        row
        for row in observations
        if canonical_exercise(row.get("exerciseName")) == "farmer_walk"
    ]
    if not matching:
        return _result(
            component="grip_endurance",
            attempted=False,
            level=None,
            assessment=assessment,
            source_ids=[],
            reason="not_tested",
            confidence="insufficient",
        )
    bodyweight, weight_quality = _body_weight(assessment)
    candidates = []
    for row in matching:
        duration = _number(row.get("timeSeconds"))
        load = _number(row.get("weightKg"))
        if duration is not None and load is not None:
            candidates.append((duration, load, row))
    if not candidates:
        return _result(
            component="grip_endurance",
            attempted=True,
            level=None,
            assessment=assessment,
            source_ids=[
                str(row.get("sourceObservationId") or "")
                for row in matching
                if row.get("sourceObservationId")
            ],
            reason="verified_duration_or_load_missing",
            confidence="insufficient",
        )
    if bodyweight is None:
        return _result(
            component="grip_endurance",
            attempted=True,
            level=None,
            assessment=assessment,
            source_ids=[
                str(row.get("sourceObservationId") or "")
                for row in matching
                if row.get("sourceObservationId")
            ],
            reason=str(weight_quality["reason"]),
            confidence="insufficient",
        )
    duration, load, best = max(
        candidates,
        key=lambda item: (
            min(item[0], 60) * (item[1] / bodyweight),
            item[0],
        ),
    )
    ratio = load / bodyweight
    level = 0
    next_level = 1
    if duration >= 60 and ratio >= 0.75:
        level = 1
        next_level = 2
    if duration >= 60 and ratio >= 1.00:
        level = 2
        next_level = 3
    if duration >= 60 and ratio >= 1.50:
        level = 3
        next_level = None
    target_ratio = {1: 0.75, 2: 1.00, 3: 1.50}.get(next_level)
    progress = (
        min(duration / 60.0, ratio / target_ratio)
        if target_ratio is not None
        else None
    )
    approaching = bool(
        next_level is not None
        and progress is not None
        and APPROACHING_RATIO <= progress < 1
    )
    return _result(
        component="grip_endurance",
        attempted=True,
        level=level,
        assessment=assessment,
        source_ids=[str(best.get("sourceObservationId") or "")],
        reason=None,
        confidence="high",
        next_level=next_level,
        progress_to_next=progress,
        approaching=approaching,
        raw_result={
            "duration_seconds": duration,
            "total_load_kg": load,
            "bodyweight_kg": bodyweight,
            "load_to_bodyweight_ratio": round(ratio, 4),
            "bodyweight_evidence": weight_quality,
        },
    )


def _spinal_component(
    assessment: dict[str, Any],
    observations: list[dict[str, Any]],
) -> dict[str, Any]:
    canonical = [
        (canonical_exercise(row.get("exerciseName")), row)
        for row in observations
    ]
    matching = [
        (exercise, row)
        for exercise, row in canonical
        if exercise in {"high_plank", "side_plank", "toes_to_bar"}
    ]
    if not matching:
        return _result(
            component="spinal_control",
            attempted=False,
            level=None,
            assessment=assessment,
            source_ids=[],
            reason="not_tested",
            confidence="insufficient",
        )
    high = [
        (_number(row.get("timeSeconds")), row)
        for exercise, row in matching
        if exercise == "high_plank"
        and _number(row.get("timeSeconds")) is not None
    ]
    toes = [
        (_number(row.get("reps")), row)
        for exercise, row in matching
        if exercise == "toes_to_bar"
        and _number(row.get("reps")) is not None
    ]
    side_by_side: dict[str, list[tuple[float, dict[str, Any]]]] = defaultdict(
        list
    )
    ambiguous_side = False
    for exercise, row in matching:
        if exercise != "side_plank":
            continue
        duration = _number(row.get("timeSeconds"))
        side = _side(row.get("side"), row.get("exerciseName"))
        if duration is None:
            continue
        if side is None:
            ambiguous_side = True
        else:
            side_by_side[side].append((duration, row))
    best_high = max(high, default=(None, None), key=lambda item: item[0])
    best_toes = max(toes, default=(None, None), key=lambda item: item[0])
    right = max(
        side_by_side.get("right", []),
        default=(None, None),
        key=lambda item: item[0],
    )
    left = max(
        side_by_side.get("left", []),
        default=(None, None),
        key=lambda item: item[0],
    )
    high_seconds = best_high[0]
    toes_reps = best_toes[0]
    level = 0
    next_level = 1
    source_rows = []
    progress = (
        high_seconds / 120.0 if high_seconds is not None else None
    )
    if high_seconds is not None:
        source_rows.append(best_high[1])
    if high_seconds is not None and high_seconds >= 120:
        level = 1
        next_level = 2
        if right[0] is not None and left[0] is not None:
            progress = min(right[0], left[0]) / 120.0
            source_rows.extend([right[1], left[1]])
        else:
            progress = None
    if (
        high_seconds is not None
        and high_seconds >= 120
        and right[0] is not None
        and left[0] is not None
        and right[0] >= 120
        and left[0] >= 120
    ):
        level = 2
        next_level = 3
        progress = toes_reps / 10.0 if toes_reps is not None else None
    if toes_reps is not None:
        source_rows.append(best_toes[1])
    if level >= 2 and toes_reps is not None and toes_reps >= 10:
        level = 3
        next_level = None
        progress = None
    if level == 0 and high_seconds is None:
        return _result(
            component="spinal_control",
            attempted=True,
            level=None,
            assessment=assessment,
            source_ids=[
                str(row.get("sourceObservationId") or "")
                for _, row in matching
                if row.get("sourceObservationId")
            ],
            reason="spinal_progression_result_missing",
            confidence="insufficient",
        )
    approaching = bool(
        next_level is not None
        and progress is not None
        and APPROACHING_RATIO <= progress < 1
    )
    reason = (
        "side_plank_side_missing_or_ambiguous"
        if level == 1 and ambiguous_side and progress is None
        else None
    )
    return _result(
        component="spinal_control",
        attempted=True,
        level=level,
        assessment=assessment,
        source_ids=sorted(
            {
                str(row.get("sourceObservationId") or "")
                for row in source_rows
                if row and row.get("sourceObservationId")
            }
        ),
        reason=reason,
        confidence="high" if reason is None else "qualified",
        next_level=next_level,
        progress_to_next=progress,
        approaching=approaching,
        raw_result={
            "high_plank_seconds": high_seconds,
            "side_plank_right_seconds": right[0],
            "side_plank_left_seconds": left[0],
            "toes_to_bar_reps": toes_reps,
        },
    )


def classify_assessment_components(
    assessment: dict[str, Any],
) -> list[dict[str, Any]]:
    observations = assessment.get("observations")
    if not isinstance(observations, list):
        observations = []
    return [
        _split_component(
            assessment,
            observations,
            wanted_side="right",
        ),
        _split_component(
            assessment,
            observations,
            wanted_side="left",
        ),
        _grip_component(assessment, observations),
        _spinal_component(assessment, observations),
    ]


def _future_result(
    *,
    standard_id: str,
    attempted: bool,
    score: int | None,
    source_ids: list[str],
    reason: str | None,
    raw_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "standard_id": standard_id,
        "standard": FUTURE_PROOFING_STANDARD_NAMES[standard_id],
        "attempted": attempted,
        "sufficient": score is not None,
        "score": score,
        "level": LEVEL_NAMES.get(score) if score is not None else None,
        "source_observation_ids": sorted(
            source_id for source_id in set(source_ids) if source_id
        ),
        "reason": reason,
        "raw_result": raw_result or {},
    }


def _deadlift_future_standard(
    assessment: dict[str, Any],
    observations: list[dict[str, Any]],
) -> dict[str, Any]:
    matching = [
        row
        for row in observations
        if canonical_exercise(row.get("exerciseName")) == "deadlift"
    ]
    if not matching:
        return _future_result(
            standard_id="deadlift",
            attempted=False,
            score=None,
            source_ids=[],
            reason="not_tested",
        )
    verified = []
    for row in matching:
        load = _number(row.get("weightKg"))
        reps = _number(row.get("reps"))
        record_type = _key(row.get("recordType"))
        if load is not None and (
            reps == 1
            or record_type in {
                "1rm",
                "1 rep max",
                "one rep max",
                "one repetition maximum",
            }
        ):
            verified.append((load, row))
    if not verified:
        return _future_result(
            standard_id="deadlift",
            attempted=True,
            score=None,
            source_ids=[
                str(row.get("sourceObservationId") or "")
                for row in matching
            ],
            reason="deadlift_1rm_not_verified",
        )
    bodyweight, weight_quality = _body_weight(assessment)
    if bodyweight is None:
        return _future_result(
            standard_id="deadlift",
            attempted=True,
            score=None,
            source_ids=[
                str(row.get("sourceObservationId") or "")
                for _, row in verified
            ],
            reason=str(weight_quality["reason"]),
        )
    load, best = max(verified, key=lambda item: item[0])
    ratio = load / bodyweight
    score = (
        3
        if ratio >= 2.50
        else 2
        if ratio >= 1.25
        else 1
        if ratio >= 0.50
        else 0
    )
    return _future_result(
        standard_id="deadlift",
        attempted=True,
        score=score,
        source_ids=[str(best.get("sourceObservationId") or "")],
        reason=None,
        raw_result={
            "verified_1rm_kg": load,
            "bodyweight_kg": bodyweight,
            "load_to_bodyweight_ratio": round(ratio, 4),
            "bodyweight_evidence": weight_quality,
        },
    )


def _split_future_standard(
    assessment: dict[str, Any],
    observations: list[dict[str, Any]],
) -> dict[str, Any]:
    right = _split_component(
        assessment,
        observations,
        wanted_side="right",
    )
    left = _split_component(
        assessment,
        observations,
        wanted_side="left",
    )
    source_ids = [
        *right["source_observation_ids"],
        *left["source_observation_ids"],
    ]
    if not right["sufficient"] or not left["sufficient"]:
        return _future_result(
            standard_id="atg_split_squat",
            attempted=bool(right["attempted"] or left["attempted"]),
            score=None,
            source_ids=source_ids,
            reason="both_split_squat_sides_require_sufficient_evidence",
            raw_result={
                "right": right,
                "left": left,
            },
        )
    score = min(
        int(right["level_number"]),
        int(left["level_number"]),
    )
    return _future_result(
        standard_id="atg_split_squat",
        attempted=True,
        score=score,
        source_ids=source_ids,
        reason=None,
        raw_result={
            "right_level": right["level"],
            "right_score": right["level_number"],
            "left_level": left["level"],
            "left_score": left["level_number"],
            "asymmetry_levels": abs(
                int(right["level_number"])
                - int(left["level_number"])
            ),
            "paired_rule": (
                "highest level fully attained by both sufficient sides"
            ),
        },
    )


def _farmer_future_standard(
    assessment: dict[str, Any],
    observations: list[dict[str, Any]],
) -> dict[str, Any]:
    component = _grip_component(assessment, observations)
    return _future_result(
        standard_id="farmer_walk",
        attempted=component["attempted"],
        score=component["level_number"],
        source_ids=component["source_observation_ids"],
        reason=component["reason"],
        raw_result=component["raw_result"],
    )


def _core_future_standard(
    assessment: dict[str, Any],
    observations: list[dict[str, Any]],
) -> dict[str, Any]:
    matching = [
        (canonical_exercise(row.get("exerciseName")), row)
        for row in observations
        if canonical_exercise(row.get("exerciseName"))
        in {"high_plank", "side_plank", "toes_to_bar"}
    ]
    if not matching:
        return _future_result(
            standard_id="core_progression",
            attempted=False,
            score=None,
            source_ids=[],
            reason="not_tested",
        )
    high = [
        (_number(row.get("timeSeconds")), row)
        for exercise, row in matching
        if exercise == "high_plank"
        and _number(row.get("timeSeconds")) is not None
    ]
    toes = [
        (_number(row.get("reps")), row)
        for exercise, row in matching
        if exercise == "toes_to_bar"
        and _number(row.get("reps")) is not None
    ]
    side_by_side: dict[str, list[tuple[float, dict[str, Any]]]] = defaultdict(
        list
    )
    for exercise, row in matching:
        if exercise != "side_plank":
            continue
        duration = _number(row.get("timeSeconds"))
        side = _side(row.get("side"), row.get("exerciseName"))
        if duration is not None and side is not None:
            side_by_side[side].append((duration, row))
    best_high = max(high, default=(None, None), key=lambda item: item[0])
    best_toes = max(toes, default=(None, None), key=lambda item: item[0])
    right = max(
        side_by_side.get("right", []),
        default=(None, None),
        key=lambda item: item[0],
    )
    left = max(
        side_by_side.get("left", []),
        default=(None, None),
        key=lambda item: item[0],
    )
    if best_high[0] is None:
        return _future_result(
            standard_id="core_progression",
            attempted=True,
            score=None,
            source_ids=[
                str(row.get("sourceObservationId") or "")
                for _, row in matching
            ],
            reason="full_plank_duration_missing",
        )
    score = 0
    source_rows = [best_high[1]]
    if best_high[0] >= 120:
        score = 1
    if (
        score >= 1
        and right[0] is not None
        and left[0] is not None
        and right[0] >= 60
        and left[0] >= 60
    ):
        score = 2
        source_rows.extend([right[1], left[1]])
    if score >= 2 and best_toes[0] is not None and best_toes[0] >= 10:
        score = 3
        source_rows.append(best_toes[1])
    return _future_result(
        standard_id="core_progression",
        attempted=True,
        score=score,
        source_ids=[
            str(row.get("sourceObservationId") or "")
            for row in source_rows
            if row
        ],
        reason=None,
        raw_result={
            "full_plank_seconds": best_high[0],
            "side_plank_right_seconds": right[0],
            "side_plank_left_seconds": left[0],
            "strict_toes_to_bar_reps": best_toes[0],
        },
    )


def _work_capacity_future_standard(
    observations: list[dict[str, Any]],
) -> dict[str, Any]:
    aliases = {"run_5km", "run_10km", "run_21km", "row_1000m"}
    matching = [
        (canonical_exercise(row.get("exerciseName")), row)
        for row in observations
        if canonical_exercise(row.get("exerciseName")) in aliases
    ]
    if not matching:
        return _future_result(
            standard_id="work_capacity",
            attempted=False,
            score=None,
            source_ids=[],
            reason="not_tested",
        )
    candidates = []
    for exercise, row in matching:
        seconds = _number(row.get("timeSeconds"))
        if seconds is None or seconds <= 0:
            continue
        score = 0
        if exercise == "run_5km" and seconds < 30 * 60:
            score = 1
        elif exercise == "run_10km" and seconds < 50 * 60:
            score = 2
        elif exercise == "run_21km" and seconds < 90 * 60:
            score = 3
        elif exercise == "row_1000m":
            score = (
                3
                if seconds < 3 * 60 + 15
                else 2
                if seconds < 4 * 60 + 30
                else 1
                if seconds < 5 * 60 + 30
                else 0
            )
        candidates.append((score, -seconds, exercise, row))
    if not candidates:
        return _future_result(
            standard_id="work_capacity",
            attempted=True,
            score=None,
            source_ids=[
                str(row.get("sourceObservationId") or "")
                for _, row in matching
            ],
            reason="verified_work_capacity_duration_missing",
        )
    score, negative_seconds, exercise, best = max(candidates)
    return _future_result(
        standard_id="work_capacity",
        attempted=True,
        score=score,
        source_ids=[str(best.get("sourceObservationId") or "")],
        reason=None,
        raw_result={
            "test": exercise,
            "duration_seconds": -negative_seconds,
        },
    )


def _push_up_future_standard(
    observations: list[dict[str, Any]],
) -> dict[str, Any]:
    matching = [
        row
        for row in observations
        if canonical_exercise(row.get("exerciseName")) == "push_ups"
    ]
    if not matching:
        return _future_result(
            standard_id="push_ups",
            attempted=False,
            score=None,
            source_ids=[],
            reason="not_tested",
        )
    verified_targets = {
        "chest to ground",
        "full chest to ground",
        "full range chest to ground",
    }
    verified = [
        (_number(row.get("reps")), row)
        for row in matching
        if _number(row.get("reps")) is not None
        and _key(row.get("target")) in verified_targets
    ]
    if not verified:
        return _future_result(
            standard_id="push_ups",
            attempted=True,
            score=None,
            source_ids=[
                str(row.get("sourceObservationId") or "")
                for row in matching
            ],
            reason="push_up_reps_or_chest_to_ground_standard_missing",
        )
    reps, best = max(verified, key=lambda item: item[0])
    score = 3 if reps >= 30 else 2 if reps >= 15 else 1 if reps >= 5 else 0
    return _future_result(
        standard_id="push_ups",
        attempted=True,
        score=score,
        source_ids=[str(best.get("sourceObservationId") or "")],
        reason=None,
        raw_result={
            "full_chest_to_ground_reps": reps,
            "form_standard": "full chest-to-ground",
        },
    )


def classify_future_proofing_standards(
    assessment: dict[str, Any],
) -> list[dict[str, Any]]:
    observations = assessment.get("observations")
    if not isinstance(observations, list):
        observations = []
    return [
        _deadlift_future_standard(assessment, observations),
        _split_future_standard(assessment, observations),
        _farmer_future_standard(assessment, observations),
        _core_future_standard(assessment, observations),
        _work_capacity_future_standard(observations),
        _push_up_future_standard(observations),
    ]


def _future_proofing_band(score: int) -> str:
    if score <= 5:
        return "Significant capability gap"
    if score <= 9:
        return "Foundational capacity / Live in some areas"
    if score <= 13:
        return "Solid base / approaching Long across most"
    if score <= 17:
        return (
            "High physical capability / Long across most and approaching "
            "Perform in select areas"
        )
    return "Full Perform across all six"


def _future_proofing_score(
    assessment: dict[str, Any],
) -> dict[str, Any]:
    standards = classify_future_proofing_standards(assessment)
    insufficient = [
        row["standard_id"]
        for row in standards
        if not row["sufficient"]
    ]
    available = not insufficient
    score = (
        sum(int(row["score"]) for row in standards)
        if available
        else None
    )
    return {
        "status": "available" if available else "unavailable",
        "score": score,
        "maximum_score": FUTURE_PROOFING_MAX_SCORE,
        "band": _future_proofing_band(score) if score is not None else None,
        "assessment_date": assessment.get("assessmentDate"),
        "source_assessment_id": assessment.get("sourceAssessmentId"),
        "standards": standards,
        "insufficient_standard_ids": insufficient,
        "reason": (
            None
            if available
            else "all_six_primary_standards_require_sufficient_evidence"
        ),
    }


def _identity_index(
    membership_snapshot: dict[str, Any] | None,
) -> tuple[dict[str, dict[str, Any]], set[str]]:
    payload = _snapshot_payload(membership_snapshot)
    candidates: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in payload.get("rows") or []:
        if not isinstance(row, dict):
            continue
        source_ids = row.get("source_ids") or {}
        for trainerize_id in source_ids.get("trainerize") or []:
            candidates[str(trainerize_id)].append(row)
    resolved = {
        source_id: rows[0]
        for source_id, rows in candidates.items()
        if len(rows) == 1
    }
    ambiguous = {
        source_id
        for source_id, rows in candidates.items()
        if len(rows) != 1
    }
    return resolved, ambiguous


def _member_name(identity: dict[str, Any]) -> str:
    return " ".join(
        str(identity.get(field) or "").strip()
        for field in ("first_name", "last_name")
        if str(identity.get(field) or "").strip()
    )


def _effective_start(
    identity: dict[str, Any],
    acquisition_snapshot: dict[str, Any] | None,
) -> tuple[date | None, str | None]:
    source_ids = identity.get("source_ids") or {}
    ghl_ids = {
        str(value)
        for value in source_ids.get("ghl") or []
        if str(value).strip()
    }
    payload = _snapshot_payload(acquisition_snapshot)
    candidates = []
    for sale in payload.get("sales") or []:
        if str(sale.get("contact_id") or "") not in ghl_ids:
            continue
        sold_on = _date(sale.get("sold_at"))
        if sold_on is not None:
            candidates.append((sold_on, str(sale.get("sale_id") or "")))
    if not candidates:
        return None, None
    return max(candidates)


def _median_days(rows: list[dict[str, Any]], level: str) -> float | None:
    values = [
        int(row["days_from_effective_start"])
        for row in rows
        if row["level"] == level
        and row.get("days_from_effective_start") is not None
    ]
    return round(statistics.median(values), 1) if values else None


def build_evolved_standards_projection(
    *,
    trainerize_snapshot: dict[str, Any] | None,
    membership_snapshot: dict[str, Any] | None,
    acquisition_snapshot: dict[str, Any] | None,
    as_of_date: date | None = None,
    acceptance_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    as_of = as_of_date or date.today()
    summary = _summary(trainerize_snapshot)
    schema_version = summary.get("standardsEvidenceSchemaVersion")
    evidence = summary.get("standardsEvidence")
    coverage = summary.get("standardsEvidenceCoverage") or {}
    future_proofing_policy = {
        "status": "canonical_score_defined",
        "classification": None,
        "label": None,
        "score_name": "Future-Proofing Score",
        "maximum_score": FUTURE_PROOFING_MAX_SCORE,
        "required_standard_ids": list(FUTURE_PROOFING_STANDARD_IDS),
        "completeness_rule": (
            "all six primary standards must be sufficiently evidenced in "
            "the same assessment"
        ),
        "note": (
            "Live, Long and Perform remain per-standard results. The "
            "framework defines an overall score and interpretation band, "
            "not one overall Live, Long or Perform member label."
        ),
    }
    record = acceptance_record or {}
    acceptance = {
        "acceptance_record_id": record.get("acceptance_record_id"),
        "acceptance_fingerprint": record.get("acceptance_fingerprint"),
        "acceptance_state": (
            record.get("acceptance_state") or "collecting"
        ),
        "technical_gates_passed": bool(
            record.get("technical_gates_passed")
        ),
        "owner_approval_state": (
            record.get("owner_approval_state") or "pending"
        ),
        "promotion_authorised": bool(
            record.get("promotion_authorised")
        ),
    }
    contract_reason = None
    if schema_version != EVIDENCE_SCHEMA_VERSION or not isinstance(
        evidence, list
    ):
        contract_reason = "trainerize_standards_evidence_contract_unavailable"
    elif coverage.get("status") != "complete":
        contract_reason = "trainerize_standards_evidence_incomplete"
    if contract_reason is not None:
        unavailable_overall = {
            **future_proofing_policy,
            "status": "unavailable",
            "reason": contract_reason,
            "members_with_complete_score": 0,
            "members_with_incomplete_score": 0,
        }
        return {
            "status": "unavailable",
            "definition_version": DEFINITION_VERSION,
            "reason": contract_reason,
            "coverage": coverage,
            "component_results": [],
            "approaching": [],
            "newly_achieved": [],
            "transition_events": [],
            "time_to_standard": {
                "component_achievements": [],
                "summary": {},
                "overall": unavailable_overall,
            },
            "future_proofing_scores": [],
            "future_proofing_score_summary": {
                "members_with_complete_score": 0,
                "members_with_incomplete_score": 0,
                "bands": {},
            },
            "overall": unavailable_overall,
            "acceptance": acceptance,
            "exceptions": [],
        }

    identities, ambiguous_ids = _identity_index(membership_snapshot)
    histories: dict[
        tuple[str, str], list[dict[str, Any]]
    ] = defaultdict(list)
    score_histories: dict[str, list[dict[str, Any]]] = defaultdict(list)
    exceptions = []
    identity_members = set()
    for assessment in evidence:
        if not isinstance(assessment, dict):
            continue
        trainerize_id = str(assessment.get("trainerizeUserId") or "")
        if trainerize_id in ambiguous_ids:
            exceptions.append(
                {
                    "code": "trainerize_identity_ambiguous",
                    "trainerize_user_id": trainerize_id,
                }
            )
            continue
        identity = identities.get(trainerize_id)
        if identity is None:
            exceptions.append(
                {
                    "code": "trainerize_identity_unresolved",
                    "trainerize_user_id": trainerize_id,
                }
            )
            continue
        canonical_key = str(identity.get("canonical_key") or "")
        if not canonical_key:
            continue
        identity_members.add(canonical_key)
        for result in classify_assessment_components(assessment):
            result.update(
                {
                    "canonical_key": canonical_key,
                    "name": _member_name(identity),
                    "trainerize_user_id": trainerize_id,
                }
            )
            histories[(canonical_key, result["component_id"])].append(result)
        future_score = _future_proofing_score(assessment)
        future_score.update(
            {
                "canonical_key": canonical_key,
                "name": _member_name(identity),
                "trainerize_user_id": trainerize_id,
            }
        )
        score_histories[canonical_key].append(future_score)

    current_results = []
    approaching = []
    transitions = []
    component_achievements = []
    for (canonical_key, component), rows in histories.items():
        ordered = sorted(
            rows,
            key=lambda row: (
                row.get("assessment_date") or "",
                row.get("source_assessment_id") or "",
            ),
        )
        attempted = [row for row in ordered if row["attempted"]]
        if not attempted:
            continue
        current = attempted[-1]
        current_results.append(current)
        if current["sufficient"] and current["approaching"]:
            approaching.append(
                {
                    "canonical_key": canonical_key,
                    "name": current["name"],
                    "component_id": component,
                    "component": current["component"],
                    "current_level": current["level"],
                    "approaching_level": current["next_level"],
                    "progress_to_next": current["progress_to_next"],
                    "assessment_date": current["assessment_date"],
                    "confidence": current["confidence"],
                }
            )
        sufficient = [row for row in ordered if row["sufficient"]]
        if not sufficient:
            continue
        identity = identities.get(str(sufficient[-1]["trainerize_user_id"]))
        effective_start, sale_id = _effective_start(
            identity or {},
            acquisition_snapshot,
        )
        previous_level = None
        for row in sufficient:
            achieved_on = _date(row["assessment_date"])
            current_level = int(row["level_number"])
            if previous_level is not None and current_level > previous_level:
                for level_number in range(previous_level + 1, current_level + 1):
                    transitions.append(
                        {
                            "canonical_key": canonical_key,
                            "name": row["name"],
                            "component_id": component,
                            "component": row["component"],
                            "from_level": LEVEL_NAMES[previous_level],
                            "level": LEVEL_NAMES[level_number],
                            "achieved_on": row["assessment_date"],
                            "source_assessment_id": row[
                                "source_assessment_id"
                            ],
                            "confidence": row["confidence"],
                        }
                    )
            previous_level = max(previous_level or 0, current_level)
        for level_number in (1, 2, 3):
            first = next(
                (
                    row
                    for row in sufficient
                    if int(row["level_number"]) >= level_number
                    and (
                        effective_start is None
                        or (
                            _date(row["assessment_date"]) is not None
                            and _date(row["assessment_date"]) >= effective_start
                        )
                    )
                ),
                None,
            )
            if first is None:
                continue
            achieved_on = _date(first["assessment_date"])
            component_achievements.append(
                {
                    "canonical_key": canonical_key,
                    "name": first["name"],
                    "component_id": component,
                    "component": first["component"],
                    "level": LEVEL_NAMES[level_number],
                    "achieved_on": first["assessment_date"],
                    "effective_membership_start": (
                        effective_start.isoformat()
                        if effective_start
                        else None
                    ),
                    "effective_start_sale_id": sale_id,
                    "days_from_effective_start": (
                        (achieved_on - effective_start).days
                        if achieved_on and effective_start
                        else None
                    ),
                    "confidence": (
                        first["confidence"]
                        if effective_start
                        else "insufficient_start_evidence"
                    ),
                }
            )

    newly_cutoff = as_of - timedelta(days=NEWLY_ACHIEVED_DAYS)
    newly_achieved = [
        row
        for row in transitions
        if (
            _date(row.get("achieved_on")) is not None
            and newly_cutoff <= _date(row["achieved_on"]) <= as_of
        )
    ]
    current_results.sort(
        key=lambda row: (
            row.get("name") or "",
            row["component_id"],
        )
    )
    approaching.sort(
        key=lambda row: (
            row.get("approaching_level") or "",
            -(row.get("progress_to_next") or 0),
            row.get("name") or "",
        )
    )
    transitions.sort(
        key=lambda row: (
            row.get("achieved_on") or "",
            row.get("name") or "",
            row["component_id"],
        ),
        reverse=True,
    )
    component_achievements.sort(
        key=lambda row: (
            row.get("achieved_on") or "",
            row.get("name") or "",
            row["component_id"],
        )
    )
    sufficient_current = [
        row for row in current_results if row["sufficient"]
    ]
    future_proofing_scores = []
    for rows in score_histories.values():
        latest = max(
            rows,
            key=lambda row: (
                row.get("assessment_date") or "",
                row.get("source_assessment_id") or "",
            ),
        )
        future_proofing_scores.append(latest)
    future_proofing_scores.sort(
        key=lambda row: (
            row.get("name") or "",
            row.get("canonical_key") or "",
        )
    )
    complete_scores = [
        row
        for row in future_proofing_scores
        if row["status"] == "available"
    ]
    band_counts: dict[str, int] = defaultdict(int)
    for row in complete_scores:
        band_counts[str(row["band"])] += 1
    overall = {
        **future_proofing_policy,
        "status": "available" if complete_scores else "unavailable",
        "reason": (
            None
            if complete_scores
            else "no_member_has_all_six_sufficient_primary_standards"
        ),
        "members_with_complete_score": len(complete_scores),
        "members_with_incomplete_score": (
            len(future_proofing_scores) - len(complete_scores)
        ),
    }
    status = (
        "available"
        if sufficient_current
        else "unavailable"
    )
    return {
        "status": status,
        "definition_version": DEFINITION_VERSION,
        "reason": None if sufficient_current else "no_sufficient_component_results",
        "coverage": {
            **coverage,
            "identity_resolved_members": len(identity_members),
            "current_components_attempted": len(current_results),
            "current_components_sufficient": len(sufficient_current),
            "current_components_unavailable": (
                len(current_results) - len(sufficient_current)
            ),
        },
        "component_results": current_results,
        "approaching": approaching,
        "newly_achieved": newly_achieved,
        "transition_events": transitions,
        "time_to_standard": {
            "component_achievements": component_achievements,
            "summary": {
                level: {
                    "median_days": _median_days(
                        component_achievements, level
                    ),
                    "components": sum(
                        row["level"] == level
                        and row.get("days_from_effective_start")
                        is not None
                        for row in component_achievements
                    ),
                }
                for level in ("Live", "Long", "Perform")
            },
            "overall": overall,
        },
        "future_proofing_scores": future_proofing_scores,
        "future_proofing_score_summary": {
            "members_with_complete_score": len(complete_scores),
            "members_with_incomplete_score": (
                len(future_proofing_scores) - len(complete_scores)
            ),
            "bands": dict(sorted(band_counts.items())),
        },
        "overall": overall,
        "acceptance": acceptance,
        "exceptions": exceptions,
        "rules": {
            "approaching_ratio": APPROACHING_RATIO,
            "newly_achieved_days": NEWLY_ACHIEVED_DAYS,
            "split_squat": {
                "Live": "10 reps each side at full depth",
                "Long": "10 reps each side plus 50% bodyweight",
                "Perform": "10 reps each side plus 100% bodyweight",
            },
            "grip_endurance": {
                "Live": "60 seconds at 75% bodyweight",
                "Long": "60 seconds at 100% bodyweight",
                "Perform": "60 seconds at 150% bodyweight",
            },
            "spinal_control": {
                "Live": "120-second High Plank",
                "Long": (
                    "120-second Side Plank on independently recorded "
                    "right and left sides"
                ),
                "Perform": "10 Strict Toes to Bar",
            },
        },
    }
