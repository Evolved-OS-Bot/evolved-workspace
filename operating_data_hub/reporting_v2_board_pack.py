from __future__ import annotations

from typing import Any, Iterable


BOARD_PACK_TABS = {
    "Board Pack": (
        "Metric",
        "Period",
        "Value",
        "Unit",
        "Numerator",
        "Denominator",
        "Confidence",
        "Freshness",
        "Definition Version",
        "Publication State",
        "Unavailable Reason",
    ),
    "Trends": (
        "Metric ID",
        "Period Start",
        "Period End",
        "Value",
        "Unit",
        "Confidence",
        "Definition Version",
    ),
    "Manual Inputs": (
        "Input ID",
        "Input Type",
        "Effective Date",
        "Value",
        "Unit",
        "Source Reference",
        "Reason",
        "Submitted By",
        "Submitted At",
        "Approval State",
        "Approved By",
        "Approved At",
        "Supersedes Input ID",
        "Validation State",
        "Rejection Reason",
    ),
    "Exceptions & Decisions": (
        "Exception ID",
        "Domain",
        "Plain English Issue",
        "Owner",
        "Due Date",
        "Status",
        "Decision",
        "Decision Reason",
        "Updated At",
    ),
    "Metric Dictionary": (
        "Metric ID",
        "Plain English Name",
        "Decision Question",
        "Event Grain",
        "Numerator",
        "Denominator",
        "Period Semantics",
        "Definition Version",
        "Owner",
        "Approval State",
    ),
    "Source Health": (
        "Source",
        "Required By",
        "Last Accepted At",
        "Maximum Age",
        "Freshness",
        "Record Count",
        "Run ID",
    ),
    "Migration Reconciliation": (
        "Metric ID",
        "Period Start",
        "Period End",
        "Legacy Value",
        "V2 Value",
        "Variance",
        "Classification",
        "Unexplained Events",
        "Unexplained Cents",
        "Acceptance State",
    ),
}


def board_pack_contract() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "mode": "shadow",
        "calculation_authority": "Operating Data Hub",
        "sheet_calculation_allowed": False,
        "publication_enabled": False,
        "tabs": [
            {
                "name": name,
                "headers": list(headers),
                "direction": (
                    "sheet_to_hub"
                    if name == "Manual Inputs"
                    else "controlled_bidirectional"
                    if name == "Exceptions & Decisions"
                    else "hub_to_sheet"
                ),
            }
            for name, headers in BOARD_PACK_TABS.items()
        ],
    }


def build_metric_dictionary_rows(
    definitions: Iterable[dict[str, Any]],
) -> list[list[Any]]:
    rows = [list(BOARD_PACK_TABS["Metric Dictionary"])]
    for definition in sorted(
        definitions,
        key=lambda item: (
            str(item.get("metric_id") or ""),
            str(item.get("definition_version") or ""),
        ),
    ):
        rows.append(
            [
                definition.get("metric_id"),
                definition.get("plain_english_name"),
                definition.get("decision_question"),
                definition.get("event_grain"),
                definition.get("numerator_definition"),
                definition.get("denominator_definition"),
                definition.get("period_semantics"),
                definition.get("definition_version"),
                definition.get("owner"),
                definition.get("approval_state"),
            ]
        )
    return rows


def build_board_pack_rows(
    observations: Iterable[dict[str, Any]],
    definitions: Iterable[dict[str, Any]],
) -> list[list[Any]]:
    definitions_by_key = {
        (
            str(item.get("metric_id") or ""),
            str(item.get("definition_version") or ""),
        ): item
        for item in definitions
    }
    rows = [list(BOARD_PACK_TABS["Board Pack"])]
    for observation in observations:
        definition = definitions_by_key.get(
            (
                str(observation.get("metric_id") or ""),
                str(observation.get("definition_version") or ""),
            ),
            {},
        )
        period = (
            f"{observation.get('period_start')} to "
            f"{observation.get('period_end')}"
        )
        rows.append(
            [
                definition.get("plain_english_name")
                or observation.get("metric_id"),
                period,
                observation.get("value"),
                observation.get("unit"),
                observation.get("numerator"),
                observation.get("denominator"),
                observation.get("confidence"),
                observation.get("freshness") or "Not published",
                observation.get("definition_version"),
                observation.get("publication_state"),
                observation.get("unavailable_reason"),
            ]
        )
    return rows


def validate_manual_input_sheet_row(
    row: dict[str, Any],
) -> dict[str, Any]:
    mapping = {
        "input_id": "Input ID",
        "input_type": "Input Type",
        "effective_date": "Effective Date",
        "value": "Value",
        "unit": "Unit",
        "source_reference": "Source Reference",
        "reason": "Reason",
        "submitted_by": "Submitted By",
        "submitted_at": "Submitted At",
        "supersedes_input_id": "Supersedes Input ID",
    }
    payload = {
        key: row.get(header)
        for key, header in mapping.items()
        if row.get(header) not in (None, "")
    }
    required = (
        "input_type",
        "effective_date",
        "value",
        "unit",
        "source_reference",
        "reason",
        "submitted_by",
    )
    missing = [
        field for field in required if not str(payload.get(field) or "").strip()
    ]
    if missing:
        raise ValueError(
            "manual input row missing: " + ", ".join(missing)
        )
    forbidden = {
        "Approval State",
        "Approved By",
        "Approved At",
        "Validation State",
        "Rejection Reason",
    }
    if any(row.get(field) not in (None, "") for field in forbidden):
        raise ValueError(
            "hub-controlled approval and validation fields must be blank"
        )
    return payload
