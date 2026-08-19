"""Aggregate-only Discord delivery for Educational Intelligence surveillance.

The notifier is deliberately unable to receive candidate rows, abstracts or
study-level claims. Detailed appraisal remains inside the protected Hub.
"""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse

import requests


ALLOWED_WEBHOOK_HOSTS = {
    "discord.com",
    "www.discord.com",
    "discordapp.com",
    "www.discordapp.com",
}


class DiscordNotificationError(RuntimeError):
    """Raised when an authorised Discord notification cannot be delivered."""


def _validate_webhook_url(value: str) -> str:
    url = value.strip()
    parsed = urlparse(url)
    if (
        parsed.scheme != "https"
        or parsed.hostname not in ALLOWED_WEBHOOK_HOSTS
        or not parsed.path.startswith("/api/webhooks/")
    ):
        raise DiscordNotificationError(
            "Discord webhook must use an official HTTPS Discord webhook URL"
        )
    return url


@dataclass(frozen=True)
class DiscordDelivery:
    status: str
    destination: str = "discord_primary"

    def as_dict(self) -> dict[str, str]:
        return {"status": self.status, "destination": self.destination}


class EducationalIntelligenceDiscordNotifier:
    """Send share-safe quarterly completion or failure messages."""

    def __init__(
        self,
        *,
        enabled: bool,
        webhook_url: str,
        review_url: str = "",
        timeout_seconds: int = 10,
    ):
        self.enabled = enabled
        self.webhook_url = (
            _validate_webhook_url(webhook_url) if enabled else ""
        )
        self.review_url = review_url.strip()
        self.timeout_seconds = timeout_seconds

    def send_complete(
        self,
        *,
        source_snapshot_id: str,
        counts: dict[str, int],
    ) -> DiscordDelivery:
        if not self.enabled:
            return DiscordDelivery("disabled")
        safety_flags = int(counts.get("safety_flags", 0))
        urgency = (
            f"\n⚠️ {safety_flags} correction/safety signals require human review."
            if safety_flags
            else "\nNo correction or safety signals detected."
        )
        review_line = (
            f"\n[Open protected review]({self.review_url})"
            if self.review_url
            else "\nOpen the protected Hub to review the held queue."
        )
        content = (
            "**Quarterly Educational Intelligence — COMPLETE**\n"
            f"Candidates: {int(counts.get('candidates', 0))} "
            f"({int(counts.get('new', 0))} new; "
            f"{int(counts.get('existing', 0))} already known)\n"
            f"Horizon status refreshes: "
            f"{int(counts.get('horizon_refresh', 0))}"
            f"{urgency}\n"
            "No evidence, doctrine or public content was changed. "
            "All candidates remain held for human appraisal."
            f"{review_line}\n"
            f"Snapshot: `{source_snapshot_id}`"
        )
        self._post(content)
        return DiscordDelivery("sent")

    def send_failed(self) -> DiscordDelivery:
        if not self.enabled:
            return DiscordDelivery("disabled")
        review_line = (
            f"\n[Open protected job ledger]({self.review_url})"
            if self.review_url
            else "\nInspect the protected Hub job ledger."
        )
        content = (
            "**Quarterly Educational Intelligence — FAILED**\n"
            "The discovery run did not complete. The previous accepted position "
            "remains in force; nothing was promoted or changed."
            f"{review_line}"
        )
        self._post(content)
        return DiscordDelivery("sent")

    def send_activation_test(self) -> DiscordDelivery:
        if not self.enabled:
            return DiscordDelivery("disabled")
        review_line = (
            f"\n[Open protected Hub]({self.review_url})"
            if self.review_url
            else "\nOpen the protected Hub for substantive review."
        )
        content = (
            "**Quarterly Educational Intelligence — DISCORD ACTIVATED**\n"
            "Primary aggregate-only delivery is verified. Future quarterly runs "
            "will report completion or failure, counts and safety urgency here.\n"
            "No evidence, doctrine or public content was changed. Study-level "
            "material remains inside the protected Hub."
            f"{review_line}"
        )
        self._post(content)
        return DiscordDelivery("sent")

    def _post(self, content: str) -> None:
        try:
            response = requests.post(
                self.webhook_url,
                json={
                    "content": content,
                    "allowed_mentions": {"parse": []},
                },
                timeout=self.timeout_seconds,
            )
        except requests.RequestException as exc:
            raise DiscordNotificationError(
                "Discord notification request failed"
            ) from exc
        if response.status_code not in {200, 204}:
            raise DiscordNotificationError(
                f"Discord notification returned HTTP {response.status_code}"
            )
