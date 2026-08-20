from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from typing import Any, Protocol
from zoneinfo import ZoneInfo

from .repository import FinalizationCase, Repository


BRISBANE = ZoneInfo("Australia/Brisbane")
STEPS = (
    "preflight",
    "billing",
    "trainerize",
    "roster",
    "ghl",
    "reporting",
    "task",
)


class RetryLater(RuntimeError):
    """A safe, expected delay such as waiting for the Hub refresh."""


class FinalizationError(RuntimeError):
    """A fail-closed cancellation finalization error."""


class Integrations(Protocol):
    def preflight(self, payload: dict[str, Any]) -> dict[str, Any]: ...
    def verify_billing(self, context: dict[str, Any]) -> dict[str, Any]: ...
    def reconcile_trainerize(self, context: dict[str, Any]) -> dict[str, Any]: ...
    def reconcile_roster(self, context: dict[str, Any]) -> dict[str, Any]: ...
    def reconcile_ghl(self, context: dict[str, Any]) -> dict[str, Any]: ...
    def verify_reporting(self, context: dict[str, Any]) -> dict[str, Any]: ...
    def complete_task(self, context: dict[str, Any]) -> dict[str, Any]: ...
    def create_exception(self, context: dict[str, Any], error: str) -> dict[str, Any]: ...


def normalize_email(value: Any) -> str:
    email = str(value or "").strip().lower()
    if not email or "@" not in email or any(ch.isspace() for ch in email):
        raise ValueError("a valid exact email is required")
    return email


def normalize_payload(raw: dict[str, Any]) -> dict[str, Any]:
    contact_id = str(raw.get("contact_id") or raw.get("contactId") or "").strip()
    if not contact_id:
        raise ValueError("contact_id is required")
    cancellation_type = str(
        raw.get("cancellation_type") or raw.get("cancellationType") or ""
    ).strip().lower()
    if cancellation_type not in {"membership", "pt"}:
        raise ValueError("cancellation_type must be Membership or PT")
    final_access = str(
        raw.get("final_access_date") or raw.get("finalAccessDate") or ""
    ).strip()[:10]
    try:
        date.fromisoformat(final_access)
    except ValueError as exc:
        raise ValueError("final_access_date must be YYYY-MM-DD") from exc
    task_id = str(raw.get("final_task_id") or raw.get("task_id") or "").strip()
    email = normalize_email(raw.get("email"))
    scope = str(raw.get("scope") or "service_only").strip().lower()
    if scope not in {"service_only", "all_services"}:
        raise ValueError("scope must be service_only or all_services")
    payload = {
        "contact_id": contact_id,
        "email": email,
        "cancellation_type": cancellation_type,
        "final_access_date": final_access,
        "final_task_id": task_id,
        "scope": scope,
        "requested_at": str(raw.get("requested_at") or datetime.now(UTC).isoformat()),
    }
    raw_key = "|".join((contact_id, cancellation_type, final_access, scope))
    payload["idempotency_key"] = "cancel-finalize-" + hashlib.sha256(
        raw_key.encode()
    ).hexdigest()[:24]
    return payload


@dataclass
class Finalizer:
    repository: Repository
    integrations: Integrations
    now: callable = lambda: datetime.now(UTC)

    def process(self, key: str) -> FinalizationCase:
        case = self.repository.get(key)
        if case is None:
            raise KeyError(key)
        if case.status == "completed":
            return case

        current = self.now()
        final_access = date.fromisoformat(case.final_access_date)
        if current.astimezone(BRISBANE).date() <= final_access:
            release = datetime.combine(
                final_access + timedelta(days=1), datetime.min.time(), tzinfo=BRISBANE
            ).astimezone(UTC)
            return self.repository.update(
                key,
                status="retry_scheduled",
                current_step="boundary_wait",
                next_attempt_at=release,
                last_error=None,
                attempts=case.attempts,
                updated_at=current,
            )

        receipts = dict(case.receipts or {})
        context: dict[str, Any] = {**case.payload, "receipts": receipts}
        self.repository.update(
            key,
            status="processing",
            attempts=case.attempts + 1,
            next_attempt_at=None,
            updated_at=current,
        )
        try:
            for step in STEPS:
                if step in receipts:
                    context[step] = receipts[step]
                    continue
                self.repository.update(key, current_step=step, updated_at=self.now())
                handler = {
                    "preflight": self.integrations.preflight,
                    "billing": self.integrations.verify_billing,
                    "trainerize": self.integrations.reconcile_trainerize,
                    "roster": self.integrations.reconcile_roster,
                    "ghl": self.integrations.reconcile_ghl,
                    "reporting": self.integrations.verify_reporting,
                    "task": self.integrations.complete_task,
                }[step]
                receipt = handler(context)
                if receipt.get("verified") is not True:
                    raise FinalizationError(f"{step} did not return verified read-back")
                receipts[step] = receipt
                context[step] = receipt
                self.repository.update(key, receipts=receipts, updated_at=self.now())
        except RetryLater as exc:
            return self.repository.update(
                key,
                status="retry_scheduled",
                last_error=str(exc),
                next_attempt_at=self.now() + timedelta(hours=1),
                receipts=receipts,
                updated_at=self.now(),
            )
        except Exception as exc:
            message = re.sub(r"\s+", " ", str(exc)).strip()[:2000]
            try:
                exception = self.integrations.create_exception(context, message)
                receipts.setdefault("exception", exception)
            except Exception:
                pass
            return self.repository.update(
                key,
                status="exception",
                last_error=message,
                next_attempt_at=None,
                receipts=receipts,
                updated_at=self.now(),
            )
        return self.repository.update(
            key,
            status="completed",
            current_step="completed",
            last_error=None,
            next_attempt_at=None,
            receipts=receipts,
            completed_at=self.now(),
            updated_at=self.now(),
        )

    def process_due(self, limit: int = 25) -> int:
        keys = self.repository.due(self.now(), limit=limit)
        for key in keys:
            self.process(key)
        return len(keys)
