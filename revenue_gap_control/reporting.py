from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

from .models import AuditInputs, AuditResult


def money(value) -> str:
    return f"${value:,.2f}"


def aggregate_markdown(inputs: AuditInputs, result: AuditResult) -> str:
    bridge = result.bridge
    lines = [
        "# KPI Revenue Gap and Active Client Audit",
        "",
        f"**Run:** `{result.run_id}`  ",
        f"**Window:** {result.window_start.isoformat()} to {result.window_end.isoformat()}  ",
        f"**Cash source:** {inputs.cash_label or 'Manually confirmed cleared cash'}  ",
        "",
        "## Control Totals",
        "",
        "| Measure | Value |",
        "|---|---:|",
        f"| SGPT numeric allocation | {money(bridge.sgpt_numeric_allocation)} |",
        f"| PT numeric allocation | {money(bridge.pt_numeric_allocation)} |",
        f"| Combined numeric allocation | {money(bridge.combined_numeric_allocation)} |",
        f"| PIF or PIA rows | {bridge.pif_rows} |",
        f"| Approved pauses | {money(bridge.approved_pauses)} |",
        f"| Arrears | {money(bridge.arrears)} |",
        f"| Future starts | {money(bridge.future_starts)} |",
        f"| Confirmed current income | {money(bridge.confirmed_current_income)} |",
        f"| Scheduled run-rate | {money(bridge.scheduled_run_rate)} |",
        f"| Cleared cash | {money(bridge.cleared_cash)} |",
        f"| Named timing items | {money(bridge.timing_items)} |",
        f"| Unexplained variance | {money(bridge.unexplained_variance)} |",
        "",
        "## Classification Counts",
        "",
        "| Classification | Clients |",
        "|---|---:|",
    ]
    for classification, count in sorted(result.status_counts.items()):
        lines.append(f"| {classification} | {count} |")

    exception_counts = Counter(item.classification for item in result.exceptions)
    lines.extend(
        [
            "",
            "## Exception Counts",
            "",
            "| Exception | Count |",
            "|---|---:|",
        ]
    )
    if exception_counts:
        for classification, count in sorted(exception_counts.items()):
            lines.append(f"| {classification} | {count} |")
    else:
        lines.append("| None | 0 |")

    lines.extend(["", "## Duplicate Controls", ""])
    if result.duplicate_emails:
        lines.extend(f"- `{item}`" for item in result.duplicate_emails)
    else:
        lines.append("No duplicate email exists within either active service sheet.")

    lines.extend(["", "## Source Limitations", ""])
    if result.limitations:
        lines.extend(f"- {item}" for item in result.limitations)
    else:
        lines.append("No source limitation was recorded.")

    lines.extend(
        [
            "",
            "## Close Status",
            "",
            (
                "The cash bridge is closed."
                if bridge.unexplained_variance == 0
                else "The cash bridge remains open and requires named owned evidence."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def write_reports(
    inputs: AuditInputs,
    result: AuditResult,
    public_dir: Path,
    private_dir: Path,
) -> dict[str, Path]:
    public_dir.mkdir(parents=True, exist_ok=True)
    run_private = private_dir / "runs" / result.run_id
    run_private.mkdir(parents=True, exist_ok=True)

    public_summary = public_dir / "latest-summary.md"
    public_summary.write_text(aggregate_markdown(inputs, result), encoding="utf-8")

    exceptions_path = run_private / "exceptions.csv"
    with exceptions_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "email",
                "client_name",
                "service",
                "classification",
                "summary",
                "financial_value",
                "evidence_checked",
                "owner",
                "next_action",
                "due_date",
                "source_row",
            ]
        )
        for item in result.exceptions:
            writer.writerow(
                [
                    item.email,
                    item.client_name,
                    item.service,
                    item.classification,
                    item.summary,
                    str(item.financial_value),
                    "; ".join(item.evidence_checked),
                    item.owner,
                    item.next_action,
                    item.due_date,
                    item.source_row or "",
                ]
            )

    audit_path = run_private / "client-audit.csv"
    with audit_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "service",
                "source_row",
                "email",
                "client_name",
                "status",
                "product",
                "weekly_allocation",
                "payment_marker",
                "classification",
                "included_confirmed",
                "included_scheduled",
                "booking_category",
                "booked_through",
                "reasons",
            ]
        )
        for item in result.assessments:
            record = item.roster
            writer.writerow(
                [
                    record.service,
                    record.row_number,
                    record.email,
                    record.name,
                    record.status,
                    record.product,
                    str(record.weekly_allocation or ""),
                    record.payment_marker,
                    item.classification,
                    item.included_in_confirmed_income,
                    item.included_in_scheduled_run_rate,
                    item.evidence.booking_category,
                    item.evidence.booked_through,
                    "; ".join(item.reasons),
                ]
            )

    bridge_path = run_private / "cash-bridge.csv"
    with bridge_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["measure", "amount"])
        for name, value in result.bridge.__dict__.items():
            writer.writerow([name, value])

    return {
        "public_summary": public_summary,
        "exceptions": exceptions_path,
        "client_audit": audit_path,
        "cash_bridge": bridge_path,
    }
