from __future__ import annotations

import argparse
import sys
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path

from .database import AuditStore
from .engine import AuditEngine
from .models import AuditInputs
from .reporting import write_reports
from .sources import (
    SourceError,
    apply_verified_phone_fallback,
    load_booking_evidence,
    load_approved_account_classifications,
    load_legacy_payment_csv,
    load_live_roster,
    load_membership_evidence,
    read_kpi_cash,
    load_roster_csv,
    load_timing_items_csv,
)


ROOT = Path(__file__).resolve().parents[1]


def _date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Use YYYY-MM-DD") from exc


def _decimal(value: str) -> Decimal:
    try:
        return Decimal(value.replace("$", "").replace(",", "")).quantize(
            Decimal("0.01")
        )
    except InvalidOperation as exc:
        raise argparse.ArgumentTypeError("Use a numeric cash amount") from exc


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        description="Read-only KPI revenue-gap and active-client audit controller"
    )
    result.add_argument("--window-start", required=True, type=_date)
    result.add_argument("--window-end", required=True, type=_date)
    result.add_argument("--cleared-cash", type=_decimal)
    result.add_argument(
        "--cash-label", default="Manually confirmed cleared bank cash"
    )
    result.add_argument(
        "--membership-db",
        type=Path,
        default=ROOT / "data/private/integration-reporting/reconciliation.sqlite",
    )
    result.add_argument(
        "--booking-db",
        type=Path,
        default=Path("/data/pt_booking_shadow.db"),
    )
    result.add_argument(
        "--audit-db",
        type=Path,
        default=ROOT / "data/private/revenue-gap-control/revenue_gap.sqlite",
    )
    result.add_argument(
        "--private-output-dir",
        type=Path,
        default=ROOT / "data/private/revenue-gap-control",
    )
    result.add_argument(
        "--public-output-dir",
        type=Path,
        default=ROOT / "outputs/revenue-gap-control",
    )
    result.add_argument("--legacy-evidence-csv", type=Path)
    result.add_argument(
        "--identity-links-csv",
        type=Path,
        default=ROOT / "data/private/integration-reporting/identity_links.csv",
    )
    result.add_argument(
        "--account-classifications-csv",
        type=Path,
        default=ROOT / "data/private/integration-reporting/account_classifications.csv",
    )
    result.add_argument("--timing-items-csv", type=Path)
    result.add_argument("--sgpt-csv", type=Path)
    result.add_argument("--pt-csv", type=Path)
    result.add_argument("--membership-max-age-hours", type=int, default=48)
    result.add_argument("--booking-max-age-hours", type=int, default=192)
    result.add_argument(
        "--allow-missing-invoices",
        action="store_true",
        help="Permit a source snapshot without Stripe invoices and record the limitation.",
    )
    return result


def _live_reader():
    scripts_dir = ROOT / "scripts"
    sys.path.insert(0, str(scripts_dir))
    try:
        from sheets_client import read_sheet
    finally:
        sys.path.pop(0)
    return read_sheet


def _roster(args, read_sheet=None) -> list:
    if bool(args.sgpt_csv) != bool(args.pt_csv):
        raise SourceError("Provide both --sgpt-csv and --pt-csv, or neither")
    if args.sgpt_csv and args.pt_csv:
        return load_roster_csv(args.sgpt_csv, "SGPT") + load_roster_csv(
            args.pt_csv, "PT"
        )
    read_sheet = read_sheet or _live_reader()
    return load_live_roster(read_sheet)


def run(args) -> tuple:
    live_reader = None
    if not (args.sgpt_csv and args.pt_csv) or args.cleared_cash is None:
        live_reader = _live_reader()
    roster = _roster(args, live_reader)
    cleared_cash = args.cleared_cash
    cash_label = args.cash_label
    if cleared_cash is None:
        cleared_cash, detected_label = read_kpi_cash(
            live_reader, args.window_end + timedelta(days=1)
        )
        if cash_label == "Manually confirmed cleared bank cash":
            cash_label = f"{detected_label}; manually confirmed bank input"
    evidence, contact_to_email, limitations, membership_run = (
        load_membership_evidence(
            args.membership_db,
            max_age_hours=args.membership_max_age_hours,
            require_invoices=not args.allow_missing_invoices,
            identity_links_path=args.identity_links_csv,
        )
    )
    apply_verified_phone_fallback(roster, evidence)
    booking_limitations, booking_run = load_booking_evidence(
        args.booking_db,
        evidence,
        contact_to_email,
        max_age_hours=args.booking_max_age_hours,
    )
    limitations.extend(booking_limitations)
    if args.allow_missing_invoices:
        limitations.append(
            "Stripe invoice completeness was not required for this run; payment classifications need manual verification."
        )
    legacy_evidence = load_approved_account_classifications(
        args.account_classifications_csv
    )
    legacy_evidence.update(load_legacy_payment_csv(args.legacy_evidence_csv))
    inputs = AuditInputs(
        window_start=args.window_start,
        window_end=args.window_end,
        cleared_cash=cleared_cash,
        roster=roster,
        evidence_by_email=evidence,
        legacy_evidence_by_email=legacy_evidence,
        timing_items=load_timing_items_csv(args.timing_items_csv),
        limitations=limitations,
        cash_label=cash_label,
    )
    result = AuditEngine().run(inputs)
    AuditStore(args.audit_db).save(inputs, result)
    paths = write_reports(
        inputs,
        result,
        args.public_output_dir,
        args.private_output_dir,
    )
    metadata = {
        "run_id": result.run_id,
        "membership_source_run": membership_run,
        "booking_source_run": booking_run,
        "roster_rows": len(roster),
        "exceptions": len(result.exceptions),
        "unexplained_variance": str(result.bridge.unexplained_variance),
        "reports": {key: str(value) for key, value in paths.items()},
    }
    return result, metadata


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        _result, metadata = run(args)
    except Exception as exc:
        print(
            {
                "status": "failed",
                "error": type(exc).__name__,
                "message": str(exc),
            }
        )
        return 1
    print({"status": "complete", **metadata})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
