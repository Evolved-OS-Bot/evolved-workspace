import hashlib
import hmac
import json

import pytest

from reporting_control.website_public_proof import build_payload, publish_latest


class Response:
    def __init__(self, payload):
        self.payload = payload
        self.status_code = 200

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


class NonJsonResponse(Response):
    def __init__(self):
        super().__init__(None)
        self.content = b"<html>challenge</html>"
        self.headers = {"Content-Type": "text/html"}
        self.url = "https://site.example/final"
        self.history = []

    def json(self):
        raise ValueError("not json")


class Session:
    def __init__(self, snapshot):
        self.snapshot = snapshot
        self.posted = None

    def get(self, *args, **kwargs):
        return Response(self.snapshot)

    def post(self, url, data, headers, timeout):
        self.posted = (url, data, headers)
        return Response({"status": "accepted"})


def snapshot():
    return {
        "observed_at": "2026-08-08T00:00:00+00:00",
        "payload": {"summary": {"publicMarketingStatistics": {
            "schemaVersion": "website-public-proof-v1",
            "womenTrained": 484,
            "trackedWorkouts": 25188,
            "strengthProgress": {
                "fourWeeks": {"medianPercent": 10.5},
                "twelveWeeks": {"medianPercent": 20.0},
                "sixMonths": {"medianPercent": 28.6},
            },
            "strengthCohortWomen": 51,
        }}},
    }


def test_payload_is_deterministic():
    first = build_payload(snapshot())
    second = build_payload(snapshot())
    assert first["snapshotId"] == second["snapshotId"]
    assert len(first["snapshotId"]) == 64


def test_payload_rejects_an_incomplete_hub_proof():
    incomplete = snapshot()
    incomplete["payload"]["summary"]["publicMarketingStatistics"] = {
        "schemaVersion": "website-public-proof-v1",
        "status": "unavailable",
    }
    with pytest.raises(ValueError, match="womenTrained"):
        build_payload(incomplete)


def test_delivery_signs_exact_body():
    session = Session(snapshot())
    result = publish_latest(
        hub_url="https://hub.example",
        hub_secret="hub-secret",
        wordpress_url="https://site.example",
        wordpress_secret="wp-secret",
        session=session,
        timestamp=1234,
    )
    _, body, headers = session.posted
    expected = hmac.new(
        b"wp-secret", b"1234." + body, hashlib.sha256
    ).hexdigest()
    assert headers["X-Evolved-Signature"] == f"sha256={expected}"
    assert json.loads(body)["snapshotId"]
    assert result == {"status": "accepted"}


def test_delivery_rejects_non_json_acknowledgement_without_body_leak():
    session = Session(snapshot())
    session.post = lambda *args, **kwargs: NonJsonResponse()
    with pytest.raises(RuntimeError, match="returned non-JSON") as error:
        publish_latest(
            hub_url="https://hub.example",
            hub_secret="hub-secret",
            wordpress_url="https://site.example",
            wordpress_secret="wp-secret",
            session=session,
            timestamp=1234,
        )
    assert "challenge" not in str(error.value)
    assert "text/html" in str(error.value)
