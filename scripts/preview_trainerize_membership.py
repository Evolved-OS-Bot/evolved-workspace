"""Preview a post-sale Trainerize membership transition without making writes.

This script is deliberately offline. It validates the minimum sale evidence and
returns the Trainerize action that would be proposed for an existing assessment
client. It does not call GHL, Stripe or Trainerize.
"""

from __future__ import annotations

import argparse
from datetime import date
import json
from pathlib import Path
from typing import Any


OFFER_ALIASES = {
    "fit & flexible": "fit_flexible",
    "fit and flexible": "fit_flexible",
    "limited": "fit_flexible",
    "strong, fit & flexible": "strong_fit_flexible",
    "strong fit & flexible": "strong_fit_flexible",
    "strong, fit & flexible membership": "strong_fit_flexible",
    "sculpt & strength": "strong_fit_flexible",
    "bronze": "strong_fit_flexible",
    "fast track": "fast_track",
    "fast track package": "fast_track",
    "fast track membership": "fast_track",
    "silver": "fast_track",
}

TRAINERIZE_PRODUCTS = {
    "fit_flexible": "Membership: Fit & Flexible",
    "strong_fit_flexible": "Membership: Strong, Fit & Flexible",
    "fast_track": "Membership: Fast Track",
}

FULFILMENT_TARGETS = {
    "fit_flexible": {
        "client_type": "Full Access / 1-way messaging",
        "trainer": "Evolved All Female Gym",
        "location": "The Evolved Gym",
        "group": None,
        "add_on_program": None,
    },
    "strong_fit_flexible": {
        "client_type": "Full Access / 1-way messaging",
        "trainer": "Evolved All Female Gym",
        "location": "The Evolved Gym",
        "group": "The Evolved All Stars",
        "add_on_program": "Membership: Strong, Fit & Flexible",
    },
    "fast_track": {
        "client_type": "Full Access / 1-way messaging",
        "trainer": "Evolved All Female Gym",
        "location": "The Evolved Gym",
        "group": "The Evolved All Stars",
        "add_on_program": "Membership: Fast Track",
    },
}


def _normalise(value: Any) -> str:
    return " ".join(str(value or "").strip().lower().split())


def _valid_iso_date(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def build_preview(event: dict[str, Any]) -> dict[str, Any]:
    """Validate one provisioning candidate and return a no-write action plan."""
    errors: list[str] = []

    offer_key = OFFER_ALIASES.get(_normalise(event.get("offer")))
    if offer_key is None:
        errors.append("offer is missing or not mapped to a current membership")

    if event.get("agreement_signed") is not True:
        errors.append("agreement_signed must be true")

    if _normalise(event.get("upfront_payment_status")) not in {
        "paid",
        "succeeded",
        "successful",
    }:
        errors.append("upfront_payment_status must confirm a successful payment")

    if not _valid_iso_date(event.get("membership_start_date")):
        errors.append("membership_start_date must be a valid YYYY-MM-DD date")

    email = _normalise(event.get("email"))
    if not email or "@" not in email:
        errors.append("email is required for exact identity verification")

    trainerize_user_id = event.get("trainerize_user_id")
    if not isinstance(trainerize_user_id, int) or trainerize_user_id <= 0:
        errors.append("trainerize_user_id is required; preview will not rely on name matching")

    correlation_id = str(event.get("correlation_id") or "").strip()
    if not correlation_id:
        errors.append("correlation_id is required for idempotency and audit history")

    if errors:
        return {
            "mode": "preview",
            "external_write": False,
            "status": "exception",
            "correlation_id": correlation_id or None,
            "errors": errors,
        }

    return {
        "mode": "preview",
        "external_write": False,
        "status": "ready_for_review",
        "correlation_id": correlation_id,
        "identity": {
            "trainerize_user_id": trainerize_user_id,
            "normalised_email": email,
            "match_rule": "stored Trainerize user ID plus exact email verification",
        },
        "sale_evidence": {
            "agreement_signed": True,
            "upfront_payment_status": event["upfront_payment_status"],
            "membership_start_date": event["membership_start_date"],
        },
        "proposed_action": {
            "action": "assign_membership_product_to_existing_client",
            "canonical_offer": offer_key,
            "trainerize_product": TRAINERIZE_PRODUCTS[offer_key],
            "product_start_date": event["membership_start_date"],
            "create_client": False,
            "send_second_invitation": False,
            "expected_configuration": FULFILMENT_TARGETS[offer_key],
        },
        "verification_required": [
            "membership product is assigned exactly once",
            "product begins on the recorded GHL membership start date",
            "existing Trainerize identity is preserved",
            "expected access, trainer, location, program and group state are present",
            "no unexpected member-facing notification is sent",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Preview an existing-client Trainerize membership transition."
    )
    parser.add_argument("event", type=Path, help="Path to a JSON sale-event file")
    args = parser.parse_args()

    event = json.loads(args.event.read_text(encoding="utf-8"))
    if not isinstance(event, dict):
        raise SystemExit("Event JSON must contain one object")

    preview = build_preview(event)
    print(json.dumps(preview, indent=2, sort_keys=True))
    return 0 if preview["status"] == "ready_for_review" else 2


if __name__ == "__main__":
    raise SystemExit(main())
