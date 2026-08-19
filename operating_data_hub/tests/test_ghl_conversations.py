import requests

import pytest

from operating_data_hub.ghl_conversations import (
    GHLConversationClient,
    GHLConversationError,
)


class Response:
    def __init__(self, payload=None, status_code=200, malformed=False):
        self.payload = payload
        self.status_code = status_code
        self.ok = 200 <= status_code < 300
        self.malformed = malformed

    def json(self):
        if self.malformed:
            raise ValueError("bad json")
        return self.payload


class Session:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response

    def put(self, url, **kwargs):
        self.calls.append((url, kwargs))
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


def client(responses):
    return GHLConversationClient(
        api_key="test",
        location_id="location",
        base_url="https://example.test",
        session=Session(responses),
    )


def test_search_paginates_and_deduplicates_exact_ids():
    first = {
        "conversations": [{"id": "c1"}, {"id": "c2"}],
        "meta": {
            "total": 3,
            "startAfterDate": "2",
            "startAfterId": "c2",
        },
    }
    second = {
        "conversations": [{"id": "c2"}, {"id": "c3"}],
        "meta": {"total": 3},
    }
    source = client([Response(first), Response(second)])
    result = source.search_unread(page_size=2)
    assert result.complete is True
    assert [row["id"] for row in result.records] == ["c1", "c2", "c3"]
    assert source.session.calls[1][1]["params"]["startAfterId"] == "c2"


def test_full_page_without_cursor_is_incomplete():
    result = client(
        [Response({"conversations": [{"id": "c1"}], "meta": {}})]
    ).search_unread(page_size=1)
    assert result.complete is False
    assert result.error_code == "missing_cursor"


@pytest.mark.parametrize("status", [401, 429, 500])
def test_http_failures_raise_typed_source_error(status):
    with pytest.raises(GHLConversationError) as caught:
        client([Response({}, status_code=status)]).search_unread()
    assert caught.value.code == f"http_{status}"


def test_transport_and_malformed_json_fail_closed():
    with pytest.raises(GHLConversationError, match="request failed"):
        client([requests.Timeout("timeout")]).search_unread()
    with pytest.raises(GHLConversationError, match="valid JSON"):
        client([Response(malformed=True)]).search_unread()


def test_capability_probe_is_read_only_and_reports_gates():
    source = client(
        [
            Response(
                {
                    "conversation": {
                        "id": "c1",
                        "assignedTo": "admin",
                        "lastMessageDate": 1,
                    }
                }
            ),
            Response({"messages": {"messages": [{"id": "m1"}]}}),
        ]
    )
    summary = source.capability_summary("c1")
    assert summary["assignment_field_present"] is True
    assert summary["write_gates"] == {
        "assignment": False,
        "message": False,
    }
    assert summary["secondary_task_creation"] == "prohibited"
    assert all(call[0].startswith("https://example.test") for call in source.session.calls)


def test_assignment_is_gated_and_never_overwrites_existing_owner():
    source = client(
        [Response({"conversation": {"id": "c1", "assignedTo": "coach"}})]
    )
    preview = source.assignment_preview("c1", target_user_id="admin")
    assert preview["action"] == "preserve_existing_owner"
    assert preview["contact_assignment_unchanged"] is True
    assert preview["secondary_task_created"] is False
    with pytest.raises(GHLConversationError) as caught:
        source.assign_unassigned_conversation(
            "c1", target_user_id="admin"
        )
    assert caught.value.code == "assignment_write_disabled"


def test_assignment_requires_empty_precondition_and_verifies_readback():
    source = GHLConversationClient(
        api_key="test",
        location_id="location",
        base_url="https://example.test",
        session=Session(
            [
                Response({"conversation": {"id": "c1"}}),
                Response({"conversation": {"id": "c1"}}),
                Response({"conversation": {"id": "c1", "assignedTo": "admin"}}),
            ]
        ),
        assignment_write_enabled=True,
    )
    result = source.assign_unassigned_conversation(
        "c1",
        target_user_id="admin",
        expected_current_assignment=None,
    )
    assert result["status"] == "assigned"
    update_call = source.session.calls[1]
    assert update_call[0].endswith("/conversations/c1")
    assert update_call[1]["json"] == {"assignedTo": "admin"}


def test_contact_search_proves_complete_and_uses_contact_filter():
    source = client(
        [
            Response(
                {
                    "conversations": [{"id": "c1"}],
                    "meta": {"total": 1},
                }
            )
        ]
    )
    result = source.search_by_contact("contact-1")
    assert result.complete is True
    assert result.records[0]["id"] == "c1"
    assert source.session.calls[0][1]["params"]["contactId"] == "contact-1"


def test_full_message_history_paginates_with_nested_cursor():
    source = client(
        [
            Response(
                {
                    "messages": {
                        "messages": [{"id": "m2"}, {"id": "m1"}],
                        "nextPage": True,
                        "lastMessageId": "m1",
                    }
                }
            ),
            Response(
                {
                    "messages": {
                        "messages": [{"id": "m1"}, {"id": "m0"}],
                        "nextPage": False,
                    }
                }
            ),
        ]
    )
    result = source.get_all_messages("c1", page_size=2)
    assert result.complete is True
    assert [row["id"] for row in result.records] == ["m2", "m1", "m0"]
    assert source.session.calls[1][1]["params"]["lastMessageId"] == "m1"


def test_full_message_history_fails_closed_without_cursor():
    source = client(
        [
            Response(
                {
                    "messages": {
                        "messages": [{"id": "m2"}, {"id": "m1"}],
                        "nextPage": True,
                    }
                }
            )
        ]
    )
    result = source.get_all_messages("c1", page_size=2)
    assert result.complete is False
    assert result.error_code == "missing_cursor"
