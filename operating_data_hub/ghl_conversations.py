from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import parse_qs, urlparse

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class GHLConversationError(RuntimeError):
    def __init__(
        self,
        code: str,
        message: str,
        *,
        status_code: int | None = None,
        retryable: bool = False,
    ):
        super().__init__(message)
        self.code = code
        self.status_code = status_code
        self.retryable = retryable


@dataclass(frozen=True)
class ConversationSearchResult:
    records: tuple[dict[str, Any], ...]
    complete: bool
    pages: int
    expected_total: int | None
    status: str
    error_code: str | None = None


@dataclass(frozen=True)
class ConversationMessagesResult:
    records: tuple[dict[str, Any], ...]
    complete: bool
    pages: int
    status: str
    error_code: str | None = None


def _cursor_from_meta(meta: dict[str, Any]) -> dict[str, Any] | None:
    direct = {
        key: meta.get(key)
        for key in ("startAfterDate", "startAfterId")
        if meta.get(key) not in (None, "")
    }
    if direct:
        return direct
    next_url = str(
        meta.get("nextPageUrl") or meta.get("nextPage") or ""
    ).strip()
    if not next_url:
        return None
    query = parse_qs(urlparse(next_url).query)
    cursor = {}
    for key in ("startAfterDate", "startAfterId"):
        values = query.get(key) or []
        if values:
            cursor[key] = values[-1]
    return cursor or None


class GHLConversationClient:
    def __init__(
        self,
        *,
        api_key: str,
        location_id: str,
        base_url: str = "https://services.leadconnectorhq.com",
        version: str = "2021-07-28",
        timeout: int = 25,
        session: requests.Session | None = None,
        assignment_write_enabled: bool = False,
        message_write_enabled: bool = False,
    ):
        self.location_id = location_id
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = session or requests.Session()
        if session is None:
            retries = Retry(
                total=2,
                connect=2,
                read=2,
                status=2,
                backoff_factor=0.5,
                status_forcelist=(429, 500, 502, 503, 504),
                allowed_methods=frozenset({"GET"}),
                respect_retry_after_header=True,
            )
            self.session.mount("https://", HTTPAdapter(max_retries=retries))
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Version": version,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        self.assignment_write_enabled = assignment_write_enabled
        self.message_write_enabled = message_write_enabled

    def _get(self, path: str, *, params: dict[str, Any] | None = None):
        try:
            response = self.session.get(
                f"{self.base_url}{path}",
                headers=self.headers,
                params=params,
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            raise GHLConversationError(
                "transport_error",
                "GHL conversation request failed",
                retryable=True,
            ) from exc
        if not response.ok:
            raise GHLConversationError(
                f"http_{response.status_code}",
                "GHL conversation request was rejected",
                status_code=response.status_code,
                retryable=response.status_code in {429, 500, 502, 503, 504},
            )
        try:
            payload = response.json()
        except ValueError as exc:
            raise GHLConversationError(
                "malformed_json",
                "GHL conversation response was not valid JSON",
            ) from exc
        if not isinstance(payload, dict):
            raise GHLConversationError(
                "invalid_payload",
                "GHL conversation response must be an object",
            )
        return payload

    def _put(self, path: str, *, payload: dict[str, Any]):
        try:
            response = self.session.put(
                f"{self.base_url}{path}",
                headers=self.headers,
                json=payload,
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            raise GHLConversationError(
                "transport_error",
                "GHL conversation update failed",
                retryable=False,
            ) from exc
        if not response.ok:
            raise GHLConversationError(
                f"http_{response.status_code}",
                "GHL conversation update was rejected",
                status_code=response.status_code,
                retryable=False,
            )
        try:
            result = response.json()
        except ValueError as exc:
            raise GHLConversationError(
                "malformed_json",
                "GHL conversation update response was not valid JSON",
            ) from exc
        if not isinstance(result, dict):
            raise GHLConversationError(
                "invalid_payload",
                "GHL conversation update response must be an object",
            )
        return result

    def _post(self, path: str, *, payload: dict[str, Any]):
        try:
            response = self.session.post(
                f"{self.base_url}{path}",
                headers=self.headers,
                json=payload,
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            raise GHLConversationError(
                "transport_error", "GHL conversation message failed", retryable=False
            ) from exc
        if not response.ok:
            raise GHLConversationError(
                f"http_{response.status_code}",
                "GHL conversation message was rejected",
                status_code=response.status_code,
                retryable=False,
            )
        try:
            result = response.json()
        except ValueError as exc:
            raise GHLConversationError(
                "malformed_json", "GHL message response was not valid JSON"
            ) from exc
        if not isinstance(result, dict):
            raise GHLConversationError(
                "invalid_payload", "GHL message response must be an object"
            )
        return result

    def search_unread(
        self,
        *,
        page_size: int = 100,
        max_pages: int = 50,
    ) -> ConversationSearchResult:
        params: dict[str, Any] = {
            "locationId": self.location_id,
            "status": "unread",
            "limit": max(1, min(page_size, 100)),
            "sort": "desc",
            "sortBy": "last_message_date",
        }
        records: list[dict[str, Any]] = []
        seen_ids: set[str] = set()
        seen_cursors: set[tuple[tuple[str, str], ...]] = set()
        expected_total: int | None = None
        pages = 0
        for _ in range(max_pages):
            payload = self._get("/conversations/search", params=params)
            pages += 1
            page = payload.get("conversations")
            if not isinstance(page, list):
                raise GHLConversationError(
                    "invalid_records",
                    "GHL conversation list is missing",
                )
            meta = payload.get("meta") or {}
            if not isinstance(meta, dict):
                meta = {}
            total_value = meta.get("total") or payload.get("total")
            if total_value not in (None, ""):
                try:
                    expected_total = int(total_value)
                except (TypeError, ValueError):
                    raise GHLConversationError(
                        "invalid_total",
                        "GHL conversation total is invalid",
                    )
            for row in page:
                if not isinstance(row, dict):
                    raise GHLConversationError(
                        "invalid_record",
                        "GHL conversation record is invalid",
                    )
                record_id = str(row.get("id") or "").strip()
                if not record_id:
                    raise GHLConversationError(
                        "missing_conversation_id",
                        "GHL conversation record has no id",
                    )
                if record_id in seen_ids:
                    continue
                seen_ids.add(record_id)
                records.append(row)
            if expected_total is not None and len(records) >= expected_total:
                return ConversationSearchResult(
                    records=tuple(records),
                    complete=True,
                    pages=pages,
                    expected_total=expected_total,
                    status="complete",
                )
            cursor = _cursor_from_meta(meta)
            if not cursor:
                if len(page) < params["limit"]:
                    complete = (
                        expected_total is None
                        or len(records) == expected_total
                    )
                    return ConversationSearchResult(
                        records=tuple(records),
                        complete=complete,
                        pages=pages,
                        expected_total=expected_total,
                        status="complete" if complete else "partial",
                        error_code=None if complete else "missing_cursor",
                    )
                return ConversationSearchResult(
                    records=tuple(records),
                    complete=False,
                    pages=pages,
                    expected_total=expected_total,
                    status="partial",
                    error_code="missing_cursor",
                )
            cursor_key = tuple(
                sorted((key, str(value)) for key, value in cursor.items())
            )
            if cursor_key in seen_cursors:
                return ConversationSearchResult(
                    records=tuple(records),
                    complete=False,
                    pages=pages,
                    expected_total=expected_total,
                    status="partial",
                    error_code="repeated_cursor",
                )
            seen_cursors.add(cursor_key)
            params.update(cursor)
        return ConversationSearchResult(
            records=tuple(records),
            complete=False,
            pages=pages,
            expected_total=expected_total,
            status="partial",
            error_code="page_limit_reached",
        )

    def search_by_contact(
        self,
        contact_id: str,
        *,
        page_size: int = 100,
        max_pages: int = 50,
    ) -> ConversationSearchResult:
        """Return every conversation for one contact with completeness proof."""
        contact = str(contact_id or "").strip()
        if not contact:
            raise ValueError("contact_id is required")
        params: dict[str, Any] = {
            "locationId": self.location_id,
            "contactId": contact,
            "limit": max(1, min(page_size, 100)),
            "sort": "desc",
            "sortBy": "last_message_date",
        }
        records: list[dict[str, Any]] = []
        seen_ids: set[str] = set()
        seen_cursors: set[tuple[tuple[str, str], ...]] = set()
        expected_total: int | None = None
        pages = 0
        for _ in range(max_pages):
            payload = self._get("/conversations/search", params=params)
            pages += 1
            page = payload.get("conversations")
            if not isinstance(page, list):
                raise GHLConversationError(
                    "invalid_records", "GHL conversation list is missing"
                )
            meta = payload.get("meta") or {}
            if not isinstance(meta, dict):
                meta = {}
            total_value = meta.get("total") or payload.get("total")
            if total_value not in (None, ""):
                try:
                    expected_total = int(total_value)
                except (TypeError, ValueError) as exc:
                    raise GHLConversationError(
                        "invalid_total", "GHL conversation total is invalid"
                    ) from exc
            for row in page:
                if not isinstance(row, dict):
                    raise GHLConversationError(
                        "invalid_record", "GHL conversation record is invalid"
                    )
                record_id = str(row.get("id") or "").strip()
                if not record_id:
                    raise GHLConversationError(
                        "missing_conversation_id",
                        "GHL conversation record has no id",
                    )
                if record_id not in seen_ids:
                    seen_ids.add(record_id)
                    records.append(dict(row))
            if expected_total is not None and len(records) >= expected_total:
                return ConversationSearchResult(
                    tuple(records), True, pages, expected_total, "complete"
                )
            cursor = _cursor_from_meta(meta)
            if not cursor:
                complete = len(page) < params["limit"] and (
                    expected_total is None or len(records) == expected_total
                )
                return ConversationSearchResult(
                    tuple(records),
                    complete,
                    pages,
                    expected_total,
                    "complete" if complete else "partial",
                    None if complete else "missing_cursor",
                )
            cursor_key = tuple(
                sorted((key, str(value)) for key, value in cursor.items())
            )
            if cursor_key in seen_cursors:
                return ConversationSearchResult(
                    tuple(records), False, pages, expected_total, "partial",
                    "repeated_cursor",
                )
            seen_cursors.add(cursor_key)
            params.update(cursor)
        return ConversationSearchResult(
            tuple(records), False, pages, expected_total, "partial",
            "page_limit_reached",
        )

    def get_messages(
        self,
        conversation_id: str,
        *,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        payload = self._get(
            f"/conversations/{conversation_id}/messages",
            params={"limit": max(1, min(limit, 100))},
        )
        messages = payload.get("messages") or {}
        if isinstance(messages, dict):
            messages = messages.get("messages") or []
        if not isinstance(messages, list):
            raise GHLConversationError(
                "invalid_messages", "GHL message list is invalid"
            )
        return [dict(row) for row in messages if isinstance(row, dict)]

    def get_all_messages(
        self,
        conversation_id: str,
        *,
        page_size: int = 100,
        max_pages: int = 100,
    ) -> ConversationMessagesResult:
        """Read a complete conversation or return an explicit partial result.

        HighLevel's message response carries its pagination cursor inside the
        nested ``messages`` object. A missing cursor is accepted only when the
        source explicitly says there is no next page or returns a short page.
        """
        conversation = str(conversation_id or "").strip()
        if not conversation:
            raise ValueError("conversation_id is required")
        params: dict[str, Any] = {
            "limit": max(1, min(page_size, 100)),
        }
        records: list[dict[str, Any]] = []
        seen_ids: set[str] = set()
        seen_cursors: set[str] = set()
        pages = 0
        for _ in range(max_pages):
            payload = self._get(
                f"/conversations/{conversation}/messages",
                params=params,
            )
            pages += 1
            container = payload.get("messages") or {}
            if isinstance(container, dict):
                page = container.get("messages") or []
                next_page = container.get("nextPage")
                cursor = (
                    container.get("lastMessageId")
                    or container.get("nextPageToken")
                    or container.get("cursor")
                )
            elif isinstance(container, list):
                page = container
                next_page = None
                cursor = None
            else:
                raise GHLConversationError(
                    "invalid_messages", "GHL message list is invalid"
                )
            if not isinstance(page, list):
                raise GHLConversationError(
                    "invalid_messages", "GHL message list is invalid"
                )
            for row in page:
                if not isinstance(row, dict):
                    continue
                message_id = str(row.get("id") or "").strip()
                dedupe_key = message_id or repr(sorted(row.items()))
                if dedupe_key in seen_ids:
                    continue
                seen_ids.add(dedupe_key)
                records.append(dict(row))
            has_next = bool(next_page)
            if next_page is False or (next_page is None and len(page) < params["limit"]):
                return ConversationMessagesResult(
                    tuple(records), True, pages, "complete"
                )
            cursor_text = str(cursor or "").strip()
            if not cursor_text:
                return ConversationMessagesResult(
                    tuple(records), False, pages, "partial", "missing_cursor"
                )
            if cursor_text in seen_cursors:
                return ConversationMessagesResult(
                    tuple(records), False, pages, "partial", "repeated_cursor"
                )
            seen_cursors.add(cursor_text)
            params["lastMessageId"] = cursor_text
            if not has_next and len(page) < params["limit"]:
                return ConversationMessagesResult(
                    tuple(records), True, pages, "complete"
                )
        return ConversationMessagesResult(
            tuple(records), False, pages, "partial", "page_limit_reached"
        )

    def get_conversation(self, conversation_id: str) -> dict[str, Any]:
        payload = self._get(f"/conversations/{conversation_id}")
        conversation = payload.get("conversation") or payload
        if not isinstance(conversation, dict):
            raise GHLConversationError(
                "invalid_conversation", "GHL conversation is invalid"
            )
        return dict(conversation)

    def get_contact(self, contact_id: str) -> dict[str, Any]:
        contact = str(contact_id or "").strip()
        if not contact:
            raise ValueError("contact_id is required")
        payload = self._get(f"/contacts/{contact}")
        record = payload.get("contact") or payload
        if not isinstance(record, dict):
            raise GHLConversationError(
                "invalid_contact", "GHL contact response is invalid"
            )
        return dict(record)

    def send_sms(self, *, contact_id: str, message: str) -> dict[str, Any]:
        if not self.message_write_enabled:
            raise GHLConversationError(
                "message_write_disabled", "Prospect message write is disabled"
            )
        contact = str(contact_id or "").strip()
        wording = str(message or "").strip()
        if not contact or not wording:
            raise ValueError("contact_id and message are required")
        result = self._post(
            "/conversations/messages",
            payload={"type": "SMS", "contactId": contact, "message": wording},
        )
        message_id = str(
            result.get("messageId")
            or (result.get("message") or {}).get("id")
            or result.get("id")
            or ""
        ).strip()
        if not message_id:
            raise GHLConversationError(
                "message_id_missing", "GHL did not return a message ID"
            )
        return {"message_id": message_id, "channel": "SMS", "response": result}

    @staticmethod
    def conversation_assignment(conversation: dict[str, Any]) -> str | None:
        value = (
            conversation.get("assignedTo")
            or conversation.get("assignedUserId")
        )
        if value in (None, ""):
            return None
        return str(value).strip() or None

    def assignment_preview(
        self,
        conversation_id: str,
        *,
        target_user_id: str,
    ) -> dict[str, Any]:
        target = str(target_user_id or "").strip()
        if not target:
            raise ValueError("target_user_id is required")
        conversation = self.get_conversation(conversation_id)
        current = self.conversation_assignment(conversation)
        return {
            "conversation_id": str(conversation_id),
            "current_assignment": current,
            "target_user_id": target,
            "eligible": current in {None, target},
            "action": (
                "assign" if current is None else "already_assigned"
                if current == target
                else "preserve_existing_owner"
            ),
            "write_enabled": self.assignment_write_enabled,
            "contact_assignment_unchanged": True,
            "secondary_task_created": False,
        }

    def assign_unassigned_conversation(
        self,
        conversation_id: str,
        *,
        target_user_id: str,
        expected_current_assignment: str | None = None,
    ) -> dict[str, Any]:
        if not self.assignment_write_enabled:
            raise GHLConversationError(
                "assignment_write_disabled",
                "Conversation assignment write is disabled",
            )
        preview = self.assignment_preview(
            conversation_id,
            target_user_id=target_user_id,
        )
        current = preview["current_assignment"]
        expected = str(expected_current_assignment or "").strip() or None
        if current != expected:
            raise GHLConversationError(
                "assignment_precondition_failed",
                "Conversation assignment changed after preview",
            )
        if preview["action"] == "preserve_existing_owner":
            return {**preview, "status": "preserved"}
        if preview["action"] == "already_assigned":
            return {**preview, "status": "unchanged"}
        self._put(
            f"/conversations/{conversation_id}",
            payload={"assignedTo": preview["target_user_id"]},
        )
        readback = self.get_conversation(conversation_id)
        resulting = self.conversation_assignment(readback)
        if resulting != preview["target_user_id"]:
            raise GHLConversationError(
                "assignment_readback_failed",
                "Conversation assignment did not persist",
            )
        return {
            **preview,
            "status": "assigned",
            "resulting_assignment": resulting,
        }

    def capability_summary(self, conversation_id: str) -> dict[str, Any]:
        conversation = self.get_conversation(conversation_id)
        messages = self.get_messages(conversation_id, limit=1)
        return {
            "conversation_fields": sorted(conversation.keys()),
            "message_fields": sorted(messages[0].keys()) if messages else [],
            "assignment_field_present": any(
                key in conversation
                for key in ("assignedTo", "assignedUserId", "userId")
            ),
            "write_gates": {
                "assignment": self.assignment_write_enabled,
                "message": self.message_write_enabled,
            },
            "secondary_task_creation": "prohibited",
        }


__all__ = [
    "ConversationMessagesResult",
    "ConversationSearchResult",
    "GHLConversationClient",
    "GHLConversationError",
]
