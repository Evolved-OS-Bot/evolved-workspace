from __future__ import annotations

import os
from dataclasses import dataclass


def _bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    database_url: str
    api_secret: str
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
    hub_api_key: str
    worker_enabled: bool

    @classmethod
    def from_env(cls) -> "Settings":
        location = os.getenv("TRAINERIZE_LOCATION_ID", "").strip()
        return cls(
            database_url=os.getenv("DATABASE_URL", "sqlite:///cancellation-finalizer.db"),
            api_secret=os.getenv("CANCELLATION_FINALIZER_SECRET", "").strip(),
            write_enabled=_bool("CANCELLATION_FINALIZER_WRITE_ENABLED"),
            ghl_api_key=os.getenv("GHL_API_KEY", "").strip(),
            ghl_location_id=os.getenv("GHL_LOCATION_ID", "").strip(),
            ghl_admin_eve_user_id=os.getenv("GHL_ADMIN_EVE_USER_ID", "").strip(),
            stripe_api_key=(
                os.getenv("STRIPE_RESTRICTED_KEY", "").strip()
                or os.getenv("STRIPE_API_KEY", "").strip()
            ),
            google_spreadsheet_id=os.getenv("GOOGLE_SPREADSHEET_ID", "").strip(),
            google_service_account_json=os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "").strip(),
            trainerize_group_id=os.getenv("TRAINERIZE_GROUP_ID", "").strip(),
            trainerize_api_token=os.getenv("TRAINERIZE_API_TOKEN", "").strip(),
            trainerize_api_base_url=os.getenv(
                "TRAINERIZE_API_BASE_URL", "https://api.trainerize.com/v03"
            ).rstrip("/"),
            trainerize_location_id=int(location) if location.isdigit() else None,
            hub_base_url=os.getenv("OPERATING_DATA_HUB_URL", "").rstrip("/"),
            hub_api_key=os.getenv("OPERATING_DATA_HUB_API_KEY", "").strip(),
            worker_enabled=_bool("CANCELLATION_FINALIZER_WORKER_ENABLED", True),
        )

    def missing_live_configuration(self) -> list[str]:
        required = {
            "CANCELLATION_FINALIZER_SECRET": self.api_secret,
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
            "OPERATING_DATA_HUB_API_KEY": self.hub_api_key,
        }
        return [name for name, value in required.items() if not value]
