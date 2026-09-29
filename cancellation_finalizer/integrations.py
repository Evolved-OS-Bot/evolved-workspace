from __future__ import annotations

import hashlib
import json
import re
import time
from datetime import UTC, datetime
from typing import Any

import requests
import stripe
from google.oauth2 import service_account
from googleapiclient.discovery import build

from .config import Settings
from .engine import FinalizationError, RetryLater, normalize_email


GHL_BASE = "https://services.leadconnectorhq.com"
CANCELLATION_PIPELINE_ID = "Tl3wKQfNYnAlcgWpORMD"
CANCELLED_MEMBER_STAGE_ID = "03e01d68-a44c-429f-8770-ce4f72fa33ca"
FIELD_NAMES = {
    "submitted_date": "CS: Date Submitted",
    "cancellation_status": "CS: Cancellation Status",
    "cancellation_type": "CS: Cancellation Type",
    "final_access_date": "CS: Final Access Date",
    "billing_status": "Billing OS: Cancellation Action Status",
    "billing_result": "Billing OS: Last Result",
}
ACTIVE_TABS = ("Active SGPT", "Active PT", "Active Online")


class ProductionIntegrations:
    def __init__(self, settings: Settings, *, session: requests.Session | None = None):
        self.settings = settings
        self.session = session or requests.Session()
        self._field_ids: dict[str, str] = {}
        stripe.api_key = settings.stripe_api_key

    def _require_writes(self) -> None:
        if not self.settings.write_enabled:
            raise FinalizationError("cancellation finalizer writes are disabled")
        missing = self.settings.missing_live_configuration()
        if missing:
            raise FinalizationError("missing live configuration: " + ", ".join(missing))

    def _ghl_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.settings.ghl_api_key}",
            "Version": "2021-07-28",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def _ghl(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        response = self.session.request(
            method,
            f"{GHL_BASE}{path}",
            headers=self._ghl_headers(),
            timeout=30,
            **kwargs,
        )
        if not response.ok:
            raise FinalizationError(
                f"GHL {method} {path} failed with HTTP {response.status_code}"
            )
        return response.json() if response.content else {}

    def _fields(self) -> dict[str, str]:
        if self._field_ids:
            return self._field_ids
        payload = self._ghl(
            "GET",
            f"/locations/{self.settings.ghl_location_id}/customFields",
            params={"model": "contact"},
        )
        by_name = {
            str(item.get("name") or ""): str(item.get("id") or "")
            for item in payload.get("customFields") or []
        }
        missing = [name for name in FIELD_NAMES.values() if not by_name.get(name)]
        if missing:
            raise FinalizationError("missing GHL cancellation fields: " + ", ".join(missing))
        self._field_ids = {key: by_name[name] for key, name in FIELD_NAMES.items()}
        return self._field_ids

    @staticmethod
    def _contact_field_values(contact: dict[str, Any]) -> dict[str, Any]:
        return {
            str(item.get("id")): item.get("fieldValue", item.get("value"))
            for item in contact.get("customFields") or []
        }

    def _contact(self, contact_id: str) -> dict[str, Any]:
        payload = self._ghl("GET", f"/contacts/{contact_id}")
        contact = payload.get("contact") or payload
        if not contact:
            raise FinalizationError("GHL contact was not found")
        return contact

    def _sheets(self):
        info = json.loads(self.settings.google_service_account_json)
        credentials = service_account.Credentials.from_service_account_info(
            info, scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        return build("sheets", "v4", credentials=credentials, cache_discovery=False)

    def _sheet_matches(self, service, tab: str, email: str) -> list[int]:
        values = (
            service.spreadsheets()
            .values()
            .get(
                spreadsheetId=self.settings.google_spreadsheet_id,
                range=f"'{tab}'!E1:E2000",
                valueRenderOption="FORMATTED_VALUE",
            )
            .execute()
            .get("values", [])
        )
        return [
            index
            for index, row in enumerate(values, start=1)
            if row and str(row[0]).strip().lower() == email
        ]

    def _roster_state(self, email: str) -> dict[str, list[int]]:
        service = self._sheets()
        return {tab: self._sheet_matches(service, tab, email) for tab in ACTIVE_TABS}

    def _trainerize_rows(self, view: str) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        start = 0
        while True:
            response = self.session.post(
                f"{self.settings.trainerize_api_base_url}/user/getClientList",
                auth=(self.settings.trainerize_group_id, self.settings.trainerize_api_token),
                headers={"Accept": "application/json", "Content-Type": "application/json"},
                json={
                    "view": view,
                    "sort": "name",
                    "start": start,
                    "count": 100,
                    "verbose": True,
                    "locationID": self.settings.trainerize_location_id,
                },
                timeout=30,
            )
            if not response.ok:
                raise FinalizationError(
                    f"Trainerize {view} read failed with HTTP {response.status_code}"
                )
            data = response.json()
            batch = data.get("users") or []
            rows.extend(batch)
            start += len(batch)
            if not batch or start >= int(data.get("total") or 0):
                return rows

    @staticmethod
    def _email_matches(rows: list[dict[str, Any]], email: str) -> list[dict[str, Any]]:
        return [
            row for row in rows if str(row.get("email") or "").strip().lower() == email
        ]

    def preflight(self, payload: dict[str, Any]) -> dict[str, Any]:
        contact = self._contact(payload["contact_id"])
        if normalize_email(contact.get("email")) != payload["email"]:
            raise FinalizationError("GHL contact email does not match the request")
        ids = self._fields()
        current = self._contact_field_values(contact)
        previous = payload.get("receipts", {}).get("preflight", {})
        submitted = str(current.get(ids["submitted_date"]) or "")
        if previous and previous.get("submitted_date") != submitted:
            raise FinalizationError("cancellation episode changed since the first attempt")
        expected = {
            "cancellation_status": "Cancelled" if previous and current.get(ids["cancellation_status"]) == "Cancelled" else "Notice Active",
            "cancellation_type": payload["cancellation_type"].upper()
            if payload["cancellation_type"] == "pt"
            else "Membership",
            "final_access_date": payload["final_access_date"],
            "billing_status": "Succeeded",
        }
        for key, value in expected.items():
            actual = str(current.get(ids[key]) or "").strip()
            if actual.lower() != str(value).lower():
                raise FinalizationError(f"GHL {FIELD_NAMES[key]} expected {value}; found {actual or 'blank'}")

        appointments = self._ghl("GET", f"/contacts/{payload['contact_id']}/appointments")
        if any(
            str(row.get("startTime") or "")[:10] > payload["final_access_date"]
            and str(row.get("appointmentStatus") or "").lower() not in {"cancelled", "canceled", "invalid"}
            for row in appointments.get("events") or []
        ):
            raise FinalizationError("future appointments require service-specific entitlement reconciliation before final closure")

        roster = self._roster_state(payload["email"])
        duplicates = {tab: rows for tab, rows in roster.items() if len(rows) > 1}
        if duplicates:
            raise FinalizationError(f"duplicate exact-email active roster rows: {duplicates}")

        ending_tabs: list[str]
        continuing_tabs: list[str]
        if payload["cancellation_type"] == "pt":
            ending_tabs = ["Active PT"]
            continuing_tabs = [tab for tab in ("Active SGPT", "Active Online") if roster[tab]]
        elif payload["scope"] == "all_services":
            ending_tabs = [tab for tab in ACTIVE_TABS if roster[tab]]
            continuing_tabs = []
        else:
            ending_tabs = ["Active SGPT"]
            continuing_tabs = [tab for tab in ("Active PT", "Active Online") if roster[tab]]
            if continuing_tabs:
                raise FinalizationError(
                    "Membership service-only cancellation has continuing service; explicit all_services or governed service change is required"
                )
        if previous and set(previous.get("continuing_tabs", [])) != set(continuing_tabs):
            raise FinalizationError("continuing service changed between finalizer attempts")
        # Accepted PT cancellations leave the commercial roster immediately;
        # a missing ending row is also a normal retry after a partial closure.
        # The exact lifecycle and billing evidence above still remain mandatory.

        return {
            "verified": True,
            "field_ids": ids,
            "submitted_date": submitted,
            "billing_result": str(current.get(ids["billing_result"]) or ""),
            "roster_before": roster,
            "ending_tabs": ending_tabs,
            "continuing_tabs": continuing_tabs,
            "deactivate_trainerize": not continuing_tabs,
            "contact_type_before": contact.get("type"),
            "tags_before": sorted(contact.get("tags") or []),
        }

    def verify_billing(self, context: dict[str, Any]) -> dict[str, Any]:
        result = context["preflight"]["billing_result"]
        match = re.search(r"\b(sub_[A-Za-z0-9]+)\b", result)
        if not match:
            raise FinalizationError("Billing OS result does not contain the exact Stripe subscription ID")
        subscription_id = match.group(1)
        subscription = stripe.Subscription.retrieve(subscription_id)
        if str(subscription.status).lower() not in {"canceled", "cancelled"}:
            raise FinalizationError(
                f"Stripe subscription {subscription_id} is {subscription.status}, not cancelled"
            )
        customer_id = str(subscription.customer)
        customer = stripe.Customer.retrieve(customer_id)
        if normalize_email(customer.get("email")) != context["email"]:
            raise FinalizationError("Stripe subscription owner does not match the exact cancellation identity")
        active = [s for s in stripe.Subscription.list(
            customer=customer_id, status="all", limit=100
        ).auto_paging_iter() if s.status not in {"canceled", "incomplete_expired"}]
        if active and not context["preflight"]["continuing_tabs"]:
            raise FinalizationError("Stripe still has an active subscription and no continuing service is recorded")
        return {
            "verified": True,
            "subscription_id": subscription_id,
            "subscription_status": str(subscription.status),
            "continuing_active_subscription_count": len(active),
        }

    def reconcile_trainerize(self, context: dict[str, Any]) -> dict[str, Any]:
        email = context["email"]
        active = self._email_matches(self._trainerize_rows("activeClient"), email)
        deactivated = self._email_matches(self._trainerize_rows("deactivatedClient"), email)
        if len(active) > 1 or (active and deactivated):
            raise FinalizationError("Trainerize exact identity is duplicated or ambiguous")
        should_deactivate = bool(context["preflight"]["deactivate_trainerize"])
        if not should_deactivate:
            if len(active) != 1:
                raise FinalizationError("continuing service requires one exact active Trainerize account")
            return {
                "verified": True,
                "action": "preserved_for_continuing_service",
                "trainerize_user_id": int(active[0]["id"]),
            }
        if not active and len(deactivated) == 1:
            return {
                "verified": True,
                "action": "already_deactivated",
                "trainerize_user_id": int(deactivated[0]["id"]),
            }
        if len(active) != 1:
            raise FinalizationError("full closure requires one exact active Trainerize account")
        self._require_writes()
        user_id = int(active[0]["id"])
        try:
            self.session.post(
                f"{self.settings.trainerize_api_base_url}/user/setStatus",
                auth=(self.settings.trainerize_group_id, self.settings.trainerize_api_token),
                headers={"Accept": "application/json", "Content-Type": "application/json"},
                json={
                    "userID": user_id,
                    "accountStatus": "deactivated",
                    "enableSignin": False,
                    "enableMessage": False,
                },
                timeout=30,
            )
        except requests.RequestException:
            # The exact active/deactivated roster read-back below is authoritative.
            pass
        for _ in range(5):
            time.sleep(2)
            active_after = self._email_matches(self._trainerize_rows("activeClient"), email)
            inactive_after = self._email_matches(self._trainerize_rows("deactivatedClient"), email)
            if not active_after and len(inactive_after) == 1 and int(inactive_after[0]["id"]) == user_id:
                return {"verified": True, "action": "deactivated", "trainerize_user_id": user_id}
        raise FinalizationError("Trainerize deactivation failed exact read-back")

    def reconcile_roster(self, context: dict[str, Any]) -> dict[str, Any]:
        self._require_writes()
        service = self._sheets()
        before = context["preflight"]["roster_before"]
        # Never clear saved row offsets: another edit can move a different
        # member into that row between attempts.
        fresh = {tab: self._sheet_matches(service, tab, context["email"]) for tab in ACTIVE_TABS}
        if any(len(rows) > 1 for rows in fresh.values()):
            raise FinalizationError("duplicate exact-email roster rows before removal")
        for tab in ACTIVE_TABS:
            if tab not in context["preflight"]["ending_tabs"] and bool(fresh[tab]) != bool(before[tab]):
                raise FinalizationError("continuing service changed since preflight")
        ranges = [
            f"'{tab}'!A{row}:K{row}"
            for tab in context["preflight"]["ending_tabs"]
            for row in fresh[tab]
        ]
        if ranges:
            (
                service.spreadsheets()
                .values()
                .batchClear(
                    spreadsheetId=self.settings.google_spreadsheet_id,
                    body={"ranges": ranges},
                )
                .execute()
            )
        after = {tab: self._sheet_matches(service, tab, context["email"]) for tab in ACTIVE_TABS}
        if any(after[tab] for tab in context["preflight"]["ending_tabs"]):
            raise FinalizationError("active roster removal failed read-back")
        for tab in context["preflight"]["continuing_tabs"]:
            if len(after[tab]) != len(before[tab]):
                raise FinalizationError("continuing active roster relationship changed")
        return {"verified": True, "cleared_ranges": ranges, "roster_after": after}

    def _set_tags(self, contact_id: str, *, add: list[str], remove: list[str]) -> None:
        if remove:
            self._ghl("DELETE", f"/contacts/{contact_id}/tags", json={"tags": remove})
        if add:
            self._ghl("POST", f"/contacts/{contact_id}/tags", json={"tags": add})

    def _cancellation_opportunity(self, contact_id: str) -> dict[str, Any]:
        payload = self._ghl(
            "GET",
            "/opportunities/search",
            params={
                "location_id": self.settings.ghl_location_id,
                "contact_id": contact_id,
                "pipeline_id": CANCELLATION_PIPELINE_ID,
                "limit": 100,
            },
        )
        rows = [
            row
            for row in payload.get("opportunities") or []
            if str(row.get("contactId")) == contact_id
            and str(row.get("pipelineId")) == CANCELLATION_PIPELINE_ID
        ]
        current = [row for row in rows if str(row.get("status") or "").lower() == "open"]
        if not current and len(rows) == 1 and rows[0].get("status") == "lost" and rows[0].get("pipelineStageId") == CANCELLED_MEMBER_STAGE_ID:
            return rows[0]
        if len(current) != 1:
            raise FinalizationError("current Cancellation OS opportunity is missing or ambiguous")
        return current[0]

    def reconcile_ghl(self, context: dict[str, Any]) -> dict[str, Any]:
        self._require_writes()
        contact_id = context["contact_id"]
        ids = context["preflight"]["field_ids"]
        continuing = bool(context["preflight"]["continuing_tabs"])
        # Resolve before any contact mutation, including retries after an
        # opportunity write succeeded but its response was lost.
        opportunity = self._cancellation_opportunity(contact_id)
        custom_fields = [{"id": ids["cancellation_status"], "fieldValue": "Cancelled"}]
        payload: dict[str, Any] = {"customFields": custom_fields}
        if not continuing:
            payload["type"] = "lead"
        self._ghl("PUT", f"/contacts/{contact_id}", json=payload)

        cancellation_type = context["cancellation_type"]
        add = ["old pt client"] if cancellation_type == "pt" else ["old member"]
        remove = ["personal training", "pt only"] if cancellation_type == "pt" else ["member"]
        if context["scope"] == "all_services":
            add = sorted(set(add + ["old member", "old pt client"]))
            remove = sorted(set(remove + ["member", "personal training", "pt only"]))
        self._set_tags(contact_id, add=add, remove=remove)

        opportunity_id = str(opportunity["id"])
        self._ghl(
            "PUT",
            f"/opportunities/{opportunity_id}",
            json={"pipelineStageId": CANCELLED_MEMBER_STAGE_ID, "status": "lost"},
        )

        contact = self._contact(contact_id)
        values = self._contact_field_values(contact)
        tags = {str(tag).lower() for tag in contact.get("tags") or []}
        if str(values.get(ids["cancellation_status"]) or "").lower() != "cancelled":
            raise FinalizationError("GHL cancellation status failed read-back")
        if any(tag in tags for tag in remove):
            raise FinalizationError("GHL active-service tags failed removal read-back")
        if not set(add).issubset(tags):
            raise FinalizationError("GHL former-service tags failed read-back")
        updated = self._ghl("GET", f"/opportunities/{opportunity_id}")
        row = updated.get("opportunity") or updated
        if str(row.get("pipelineStageId")) != CANCELLED_MEMBER_STAGE_ID or str(row.get("status")).lower() != "lost":
            raise FinalizationError("Cancellation OS opportunity failed terminal read-back")
        return {
            "verified": True,
            "opportunity_id": opportunity_id,
            "continuing_service_preserved": continuing,
            "tags_added": add,
            "tags_removed": remove,
        }

    def verify_reporting(self, context: dict[str, Any]) -> dict[str, Any]:
        if (
            not self.settings.hub_base_url
            or not self.settings.hub_current_people_read_key
        ):
            raise FinalizationError("Hub verification is not configured")
        response = self.session.get(
            f"{self.settings.hub_base_url}/api/v2/reporting/current-people",
            headers={
                "X-Current-People-Read-Secret": (
                    self.settings.hub_current_people_read_key
                )
            },
            params={"period": "week"},
            timeout=60,
        )
        if not response.ok:
            raise RetryLater(f"Hub current-people read returned HTTP {response.status_code}")
        payload = response.json()
        if payload.get("complete") is False or payload.get("blocked_reasons"):
            raise RetryLater("Hub current-people projection is incomplete")
        if any(item.get("freshness") not in {"fresh", None} for item in payload.get("source_freshness") or []):
            raise RetryLater("Hub source evidence is not fresh")
        rows = [
            row
            for row in payload.get("rows") or []
            if any(
                identity.get("source") == "ghl"
                and str(identity.get("source_record_id")) == context["contact_id"]
                for identity in row.get("source_identities") or []
            )
        ]
        if len(rows) != 1:
            raise RetryLater("Hub has not resolved one exact GHL identity yet")
        row = rows[0]
        lifecycle = row.get("lifecycle") or {}
        continuing = bool(context.get("preflight", {}).get("continuing_tabs"))
        if not continuing and str(lifecycle.get("status") or "").lower() not in {"cancelled", "inactive"}:
            raise RetryLater("Hub has not projected the terminal lifecycle yet")
        ended_types = {"personal_training"} if context["cancellation_type"] == "pt" else {"sgpt", "fast_track"}
        if context["scope"] == "all_services":
            ended_types = {"personal_training", "sgpt", "fast_track", "online"}
        remaining = {
            str(item.get("service_type") or "")
            for item in row.get("service_relationships") or []
            if str(item.get("status") or "").lower() in {"active", "paused", "cancelling"}
        }
        if remaining & ended_types:
            raise RetryLater("Hub still contains the ended service relationship")
        return {
            "verified": True,
            "person_id": row.get("person_id"),
            "lifecycle_status": lifecycle.get("status"),
            "remaining_service_types": sorted(remaining),
            "source_freshness": payload.get("source_freshness") or [],
        }

    def complete_task(self, context: dict[str, Any]) -> dict[str, Any]:
        self._require_writes()
        contact_id = context["contact_id"]
        task_id = context["final_task_id"]
        if not task_id:
            return {
                "verified": True,
                "task_id": None,
                "completed": False,
                "reason": "no_exact_final_task_supplied",
            }
        self._ghl(
            "PUT",
            f"/contacts/{contact_id}/tasks/{task_id}",
            json={"completed": True},
        )
        tasks = self._ghl("GET", f"/contacts/{contact_id}/tasks").get("tasks") or []
        matches = [row for row in tasks if str(row.get("id")) == task_id]
        if len(matches) != 1 or not matches[0].get("completed"):
            raise FinalizationError("exact final task failed completion read-back")
        return {"verified": True, "task_id": task_id, "completed": True}

    def create_exception(self, context: dict[str, Any], error: str) -> dict[str, Any]:
        # The durable case owns the exception. Owner policy requires explicit
        # case-specific approval before assigning any new Admin Eve task.
        return {"verified": True, "held": True, "reason": "recorded_in_finalizer_exception_queue"}
