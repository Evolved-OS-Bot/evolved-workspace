from __future__ import annotations

import os
from dataclasses import dataclass
from zoneinfo import ZoneInfo


BRISBANE_TZ = ZoneInfo("Australia/Brisbane")


def _bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


@dataclass(frozen=True)
class Settings:
    database_url: str
    webhook_secret: str
    dashboard_password: str
    flask_secret: str
    shadow_mode: bool
    scheduler_enabled: bool
    google_spreadsheet_id: str
    google_service_account_json: str | None
    retention_health_url: str
    pt_health_url: str

    @classmethod
    def from_env(cls, *, require_runtime: bool = True) -> "Settings":
        def required(name: str, fallback: str = "") -> str:
            value = os.getenv(name, fallback).strip()
            if require_runtime and not value:
                raise RuntimeError(f"Missing required environment variable: {name}")
            return value

        if not _bool("HUB_SHADOW_MODE", True):
            raise RuntimeError(
                "Operating-data hub refuses to start unless HUB_SHADOW_MODE=true"
            )
        return cls(
            database_url=os.getenv(
                "DATABASE_URL",
                "sqlite:////tmp/evolved-operating-data-hub.db",
            ),
            webhook_secret=required(
                "HUB_WEBHOOK_SECRET", "local-development-only"
            ),
            dashboard_password=required(
                "HUB_DASHBOARD_PASSWORD", "local-dashboard"
            ),
            flask_secret=required(
                "HUB_FLASK_SECRET", "local-session-secret"
            ),
            shadow_mode=True,
            scheduler_enabled=_bool("HUB_SCHEDULER_ENABLED", True),
            google_spreadsheet_id=os.getenv(
                "GOOGLE_SPREADSHEET_ID",
                "1aeD8c2mY9rwltmVnTl86rx_rYXpSsAq3HTamk-hEs3c",
            ),
            google_service_account_json=(
                os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON") or None
            ),
            retention_health_url=os.getenv(
                "RETENTION_HEALTH_URL",
                "https://retention-intelligence-production-dd86.up.railway.app/health",
            ),
            pt_health_url=os.getenv(
                "PT_HEALTH_URL",
                "https://pt-booking-shadow-production.up.railway.app/health",
            ),
        )

