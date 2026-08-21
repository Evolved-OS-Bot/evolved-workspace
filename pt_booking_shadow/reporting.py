from __future__ import annotations

import base64
import csv
import html
import io
from collections import Counter
from datetime import datetime

import requests

from .config import BRISBANE_TZ, Settings
from .models import Finding


PRIORITY = {
    "CANCELLATION_DATE_MISSING": 0,
    "WOULD_REMOVE_AFTER_CANCELLATION": 1,
    "NO_FUTURE_BOOKINGS": 2,
    "DUPLICATE_APPOINTMENT": 3,
    "GAP_INSIDE_SERIES": 4,
    "GHL_ONLY_PT_RECORD_REVIEW": 3,
    "PATTERN_CONFIRMATION_REQUIRED": 5,
    "FREQUENCY_MISMATCH": 6,
    "FORMER_PT_WITH_FUTURE_BOOKINGS": 7,
    "WOULD_TOP_UP": 8,
    "PT_HOLD_ACTIVE": 9,
    "PT_NOTICE_ACTIVE": 10,
    "CROSS_SYSTEM_SOURCE_UNAVAILABLE": 11,
    "CROSS_SYSTEM_IDENTITY_REVIEW": 12,
    "COMMERCIAL_EVIDENCE_REVIEW_REQUIRED": 13,
    "TRAINERIZE_ACCESS_REVIEW_REQUIRED": 14,
    "WORKBOOK_PT_RECORD_MISSING": 15,
    "HEALTHY": 99,
}

HIGH_RISK = {
    "CANCELLATION_DATE_MISSING",
    "WOULD_REMOVE_AFTER_CANCELLATION",
    "NO_FUTURE_BOOKINGS",
    "DUPLICATE_APPOINTMENT",
}

SUPPRESSED_REPORT_CATEGORIES = {"FORMER_PT"}


def _reportable(findings: list[Finding]) -> list[Finding]:
    """Hide routine former-client evidence while retaining actionable exceptions."""
    return [
        item
        for item in findings
        if item.category not in SUPPRESSED_REPORT_CATEGORIES
    ]


def _contact_url(location_id: str, contact_id: str) -> str:
    return f"https://app.gohighlevel.com/v2/location/{location_id}/contacts/detail/{contact_id}"


def build_csv(findings: list[Finding], location_id: str, run_id: str) -> bytes:
    output = io.StringIO()
    columns = [
        "run_id",
        "contact_id",
        "contact_name",
        "ghl_contact_url",
        "effective_status",
        "category",
        "expected_frequency",
        "inferred_frequency",
        "patterns",
        "confidence",
        "last_completed",
        "last_future",
        "booked_through",
        "coverage_weeks",
        "proposed_dates",
        "reason",
    ]
    writer = csv.DictWriter(output, fieldnames=columns)
    writer.writeheader()
    for item in _reportable(findings):
        writer.writerow(
            {
                "run_id": run_id,
                "contact_id": item.contact_id,
                "contact_name": item.contact_name,
                "ghl_contact_url": _contact_url(location_id, item.contact_id),
                "effective_status": item.effective_status,
                "category": item.category,
                "expected_frequency": item.expected_frequency,
                "inferred_frequency": item.inferred_frequency,
                "patterns": " | ".join(item.patterns),
                "confidence": item.confidence,
                "last_completed": item.last_completed,
                "last_future": item.last_future,
                "booked_through": item.booked_through,
                "coverage_weeks": item.coverage_weeks,
                "proposed_dates": " | ".join(item.proposed_dates),
                "reason": item.reason,
            }
        )
    return output.getvalue().encode("utf-8")


def build_html(findings: list[Finding], location_id: str, run_id: str) -> str:
    now = datetime.now(BRISBANE_TZ)
    reportable = _reportable(findings)
    counts = Counter(item.category for item in reportable)
    sorted_items = sorted(
        reportable,
        key=lambda item: (PRIORITY.get(item.category, 50), item.contact_name.lower()),
    )
    action_items = [item for item in sorted_items if item.category != "HEALTHY"]
    healthy = counts.get("HEALTHY", 0)

    count_rows = "".join(
        f"<tr><td>{html.escape(category)}</td><td style='text-align:right'>{count}</td></tr>"
        for category, count in sorted(counts.items(), key=lambda pair: PRIORITY.get(pair[0], 50))
    )
    cards = []
    for item in action_items:
        proposed = (
            f"<p><strong>Would affect:</strong> {len(item.proposed_dates)} occurrence(s), "
            f"{html.escape(item.proposed_dates[0])} to {html.escape(item.proposed_dates[-1])}</p>"
            if item.proposed_dates
            else ""
        )
        pattern = (
            f"<p><strong>Pattern:</strong> {html.escape(' | '.join(item.patterns))}</p>"
            if item.patterns
            else ""
        )
        cards.append(
            f"""
            <div style="border:1px solid #ddd;border-left:5px solid #0b6655;
                        border-radius:6px;padding:14px;margin:12px 0;">
              <p style="margin:0 0 6px;"><strong>{html.escape(item.contact_name)}</strong>
              · {html.escape(item.category)}</p>
              <p>{html.escape(item.reason)}</p>
              {pattern}{proposed}
              <p><strong>Coverage:</strong> {item.coverage_weeks} complete week(s)
              · <strong>Confidence:</strong> {item.confidence:.0%}</p>
              <a href="{_contact_url(location_id, item.contact_id)}">Open GHL contact</a>
            </div>
            """
        )

    return f"""
    <html><body style="font-family:Arial,sans-serif;max-width:760px;margin:0 auto;color:#222;">
      <div style="background:#fff3cd;border:1px solid #e4c55b;padding:12px;border-radius:6px;">
        <strong>SHADOW MODE: NO GHL APPOINTMENTS WERE CHANGED</strong>
      </div>
      <h2>PT Booking Continuity · {now.strftime('%A, %-d %B %Y')}</h2>
      <p>Run {html.escape(run_id)} ·
         {len({item.contact_id for item in reportable if item.contact_id != 'system'})}
         reportable contact result(s) ·
         {len(action_items)} exception(s) · {healthy} healthy.</p>
      <table style="border-collapse:collapse;min-width:360px;">
        {count_rows}
      </table>
      <h3>Admin Eve review</h3>
      {''.join(cards) if cards else '<p>No exceptions found.</p>'}
      <p style="color:#666;font-size:12px;">
        Healthy-client detail and exact proposed dates are included in the attached CSV.
      </p>
    </body></html>
    """


def send_report(
    settings: Settings,
    findings: list[Finding],
    run_id: str,
    subject_prefix: str = "PT Booking Shadow",
) -> dict:
    csv_bytes = build_csv(findings, settings.ghl_location_id, run_id)
    html_body = build_html(findings, settings.ghl_location_id, run_id)
    if settings.report_dry_run:
        return {"status": "dry_run", "html": html_body, "csv": csv_bytes}
    if not settings.resend_api_key:
        raise RuntimeError("RESEND_API_KEY is required when REPORT_DRY_RUN=false")

    response = requests.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {settings.resend_api_key}",
            "Content-Type": "application/json",
        },
        json={
            "from": settings.email_from,
            "to": [settings.admin_email_to],
            "subject": f"{subject_prefix} · {datetime.now(BRISBANE_TZ).strftime('%-d %b %Y')}",
            "html": html_body,
            "attachments": [
                {
                    "filename": f"pt-booking-shadow-{run_id}.csv",
                    "content": base64.b64encode(csv_bytes).decode("ascii"),
                }
            ],
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def high_risk(findings: list[Finding]) -> list[Finding]:
    return [item for item in findings if item.category in HIGH_RISK]
