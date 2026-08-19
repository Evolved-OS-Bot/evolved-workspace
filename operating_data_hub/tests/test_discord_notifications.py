import pytest

from operating_data_hub.discord_notifications import (
    DiscordNotificationError,
    EducationalIntelligenceDiscordNotifier,
)


class Response:
    status_code = 204


def test_completion_notification_is_aggregate_only(monkeypatch):
    sent = {}

    def fake_post(url, *, json, timeout):
        sent.update(url=url, json=json, timeout=timeout)
        return Response()

    monkeypatch.setattr(
        "operating_data_hub.discord_notifications.requests.post",
        fake_post,
    )
    notifier = EducationalIntelligenceDiscordNotifier(
        enabled=True,
        webhook_url="https://discord.com/api/webhooks/123/secret",
        review_url="https://hub.example/dashboard",
    )

    delivery = notifier.send_complete(
        source_snapshot_id="snapshot-1",
        counts={
            "candidates": 30,
            "new": 24,
            "existing": 6,
            "safety_flags": 2,
            "horizon_refresh": 10,
        },
    )

    content = sent["json"]["content"]
    assert delivery.status == "sent"
    assert "Candidates: 30 (24 new; 6 already known)" in content
    assert "2 correction/safety signals" in content
    assert "No evidence, doctrine or public content was changed" in content
    assert sent["json"]["allowed_mentions"] == {"parse": []}
    assert "abstract" not in content.lower()
    assert "candidate_rows" not in content


def test_disabled_notifier_does_not_post(monkeypatch):
    monkeypatch.setattr(
        "operating_data_hub.discord_notifications.requests.post",
        lambda *_args, **_kwargs: pytest.fail("unexpected outbound request"),
    )
    notifier = EducationalIntelligenceDiscordNotifier(
        enabled=False,
        webhook_url="",
    )
    assert notifier.send_failed().status == "disabled"


def test_activation_message_preserves_protected_boundary(monkeypatch):
    sent = {}

    def fake_post(_url, *, json, timeout):
        sent.update(json=json, timeout=timeout)
        return Response()

    monkeypatch.setattr(
        "operating_data_hub.discord_notifications.requests.post",
        fake_post,
    )
    notifier = EducationalIntelligenceDiscordNotifier(
        enabled=True,
        webhook_url="https://discord.com/api/webhooks/123/secret",
        review_url="https://hub.example/dashboard",
    )
    assert notifier.send_activation_test().status == "sent"
    assert "DISCORD ACTIVATED" in sent["json"]["content"]
    assert "Study-level material remains inside the protected Hub" in (
        sent["json"]["content"]
    )


def test_enabled_notifier_rejects_non_discord_destination():
    with pytest.raises(DiscordNotificationError):
        EducationalIntelligenceDiscordNotifier(
            enabled=True,
            webhook_url="https://example.com/api/webhooks/123/secret",
        )
