from __future__ import annotations

import os
from dataclasses import dataclass


def _bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _positive_int(name: str, default: int) -> int:
    value = os.getenv(name, str(default)).strip()
    if not value.isdigit() or int(value) < 1:
        raise ValueError(f"{name} must be a positive integer")
    return int(value)


@dataclass(frozen=True)
class Settings:
    database_url: str
    webhook_signing_secret: str
    admin_secret: str
    relay_enabled: bool
    relay_membership_secret: str
    relay_pt_secret: str
    signature_tolerance_seconds: int
    webhook_rate_limit_per_minute: int
    relay_rate_limit_per_minute: int
    admin_rate_limit_per_minute: int
    write_enabled: bool
    ghl_api_key: str
    ghl_location_id: str
    ghl_admin_eve_user_id: str
    stripe_api_key: str
    google_spreadsheet_id: str
    google_service_account_json: str
    trainerize_group_id: str
    trainerize_api_token: str
    trainerize_api_base_url: str
    trainerize_location_id: int | None
    hub_base_url: str
    hub_current_people_read_key: str
    worker_enabled: bool

    def relay_configuration_issues(self) -> list[str]:
        if not self.relay_enabled:
            return []
        issues: list[str] = []
        if len(self.relay_membership_secret) < 32:
            issues.append("CANCELLATION_RELAY_MEMBERSHIP_SECRET")
        if len(self.relay_pt_secret) < 32:
            issues.append("CANCELLATION_RELAY_PT_SECRET")
        if (
            self.relay_membership_secret
            and self.relay_membership_secret == self.relay_pt_secret
        ):
            issues.append("CANCELLATION_RELAY_SERVICE_SECRETS_DISTINCT")
        protected = {self.webhook_signing_secret, self.admin_secret} - {""}
        if (
            self.relay_membership_secret in protected
            or self.relay_pt_secret in protected
        ):
            issues.append("CANCELLATION_RELAY_SECRETS_SEPARATE")
        return issues

    @classmethod
    def from_env(cls) -> "Settings":
        location = os.getenv("TRAINERIZE_LOCATION_ID", "").strip()
        return cls(
            database_url=os.getenv(
                "DATABASE_URL", "sqlite:///cancellation-finalizer.db"
            ),
            webhook_signing_secret=os.getenv(
                "CANCELLATION_WEBHOOK_SIGNING_SECRET", ""
            ).strip(),
            admin_secret=os.getenv("CANCELLATION_ADMIN_SECRET", "").strip(),
            relay_enabled=_bool("CANCELLATION_RELAY_ENABLED"),
            relay_membership_secret=os.getenv(
                "CANCELLATION_RELAY_MEMBERSHIP_SECRET", ""
            ).strip(),
            relay_pt_secret=os.getenv("CANCELLATION_RELAY_PT_SECRET", "").strip(),
            signature_tolerance_seconds=_positive_int(
                "CANCELLATION_SIGNATURE_TOLERANCE_SECONDS", 300
            ),
            webhook_rate_limit_per_minute=_positive_int(
                "CANCELLATION_WEBHOOK_RATE_LIMIT_PER_MINUTE", 30
            ),
            relay_rate_limit_per_minute=_positive_int(
                "CANCELLATION_RELAY_RATE_LIMIT_PER_MINUTE", 10
            ),
            admin_rate_limit_per_minute=_positive_int(
                "CANCELLATION_ADMIN_RATE_LIMIT_PER_MINUTE", 60
            ),
            write_enabled=_bool("CANCELLATION_FINALIZER_WRITE_ENABLED"),
            ghl_api_key=os.getenv("GHL_API_KEY", "").strip(),
            ghl_location_id=os.getenv("GHL_LOCATION_ID", "").strip(),
            ghl_admin_eve_user_id=os.getenv("GHL_ADMIN_EVE_USER_ID", "").strip(),
            stripe_api_key=(
                os.getenv("STRIPE_RESTRICTED_KEY", "").strip()
                or os.getenv("STRIPE_API_KEY", "").strip()
            ),
            google_spreadsheet_id=os.getenv("GOOGLE_SPREADSHEET_ID", "").strip(),
            google_service_account_json=os.getenv(
                "GOOGLE_SERVICE_ACCOUNT_JSON", ""
            ).strip(),
            trainerize_group_id=os.getenv("TRAINERIZE_GROUP_ID", "").strip(),
            trainerize_api_token=os.getenv("TRAINERIZE_API_TOKEN", "").strip(),
            trainerize_api_base_url=os.getenv(
                "TRAINERIZE_API_BASE_URL", "https://api.trainerize.com/v03"
            ).rstrip("/"),
            trainerize_location_id=int(location) if location.isdigit() else None,
            hub_base_url=os.getenv("OPERATING_DATA_HUB_URL", "").rstrip("/"),
            hub_current_people_read_key=os.getenv(
                "OPERATING_DATA_HUB_CURRENT_PEOPLE_READ_KEY", ""
            ).strip(),
            worker_enabled=_bool("CANCELLATION_FINALIZER_WORKER_ENABLED", True),
        )

    def missing_live_configuration(self) -> list[str]:
        required = {
            "CANCELLATION_WEBHOOK_SIGNING_SECRET": self.webhook_signing_secret,
            "CANCELLATION_ADMIN_SECRET": self.admin_secret,
            "GHL_API_KEY": self.ghl_api_key,
            "GHL_LOCATION_ID": self.ghl_location_id,
            "GHL_ADMIN_EVE_USER_ID": self.ghl_admin_eve_user_id,
            "STRIPE_RESTRICTED_KEY": self.stripe_api_key,
            "GOOGLE_SPREADSHEET_ID": self.google_spreadsheet_id,
            "GOOGLE_SERVICE_ACCOUNT_JSON": self.google_service_account_json,
            "TRAINERIZE_GROUP_ID": self.trainerize_group_id,
            "TRAINERIZE_API_TOKEN": self.trainerize_api_token,
            "TRAINERIZE_LOCATION_ID": self.trainerize_location_id,
            "OPERATING_DATA_HUB_URL": self.hub_base_url,
            "OPERATING_DATA_HUB_CURRENT_PEOPLE_READ_KEY": (
                self.hub_current_people_read_key
            ),
        }
        missing = [name for name, value in required.items() if not value]
        missing.extend(
            issue for issue in self.relay_configuration_issues() if issue not in missing
        )
        return missing
