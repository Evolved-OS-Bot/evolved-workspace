from pt_booking_shadow.ghl_client import GHLReadOnlyClient


def test_contact_pagination_restarts_after_an_expired_cursor(monkeypatch):
    client = GHLReadOnlyClient.__new__(GHLReadOnlyClient)
    client.location_id = "location-1"
    calls = []

    def fake_get(path, params):
        calls.append(dict(params))
        if len(calls) == 1:
            return {
                "contacts": [{"id": "discarded-after-restart"}],
                "meta": {"startAfter": 1, "startAfterId": "cursor-1"},
            }
        if len(calls) == 2:
            raise RuntimeError("expired cursor")
        return {"contacts": [{"id": "kept"}], "meta": {}}

    client._get = fake_get
    monkeypatch.setattr("pt_booking_shadow.ghl_client.time.sleep", lambda _seconds: None)

    assert client.list_contacts() == [{"id": "kept"}]
    assert calls[2] == {"locationId": "location-1", "limit": 100}
