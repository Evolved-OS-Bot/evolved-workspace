from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from zoneinfo import ZoneInfo


BRISBANE_TZ = ZoneInfo("Australia/Brisbane")

PT_PIPELINE_ID = "fkEvrFkTihYkdb3bpprd"
PT_STAGE_FREQUENCY = {
    "58247f13-4a47-40f8-8289-35d62fc138b3": None,  # PT Only
    "9ce28fb1-f43b-472a-ac11-1b4c147b202b": 1,
    "01d615da-4bd4-4bf3-a5c6-54332588367d": 2,
    "edf7f617-e058-438a-978a-330fa262ef8e": 3,
}

FIELD_IDS = {
    "hold_status": "huVhp3xNLYJDtPA9JdFA",
    "hold_type": "J54g7CqeVbOHo6CoYzMA",
    "hold_start": "k40qV4w0HKj5KFbMnmq8",
    "hold_end": "WOnR5XTn45YnSx9KsBGF",
    "cancellation_status": "vqTZezcOELXVjVLRTiCR",
    "cancellation_type": "VhxR2hI4B1GfvcZJiD9j",
    "notice_end": "8Thl9yA4A7kwkbF8QL1Z",
    "final_access": "3mZzBYcUk7ZAvB9Fs7lH",
    "pt_block_service": "Upyxa5ORrkYuzKmB9ikp",
    "pt_block_start": "qoSPND4o6aOmyMesj6Xs",
    "pt_block_trainer": "gSYaeeCF2iiRSzJhKePT",
    "trainer": "YWkGI9PYbF8jP22NKpbQ",
}

CURRENT_TRAINERS = ("Megan", "Piper", "Nora", "Katrina", "Leisa")
CURRENT_TRAINER_FULL_NAMES = {
    "Megan": "Megan Brown",
    "Piper": "Piper Mae",
    "Nora": "Nora Silva",
    "Katrina": "Katrina Parsons",
    "Leisa": "Leisa Smith",
}


def _bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


def load_local_env(path: Path) -> None:
    if not path.exists():
        return
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


@dataclass(frozen=True)
class Settings:
    ghl_api_key: str
    ghl_location_id: str
    database_path: str
    webhook_secret: str
    resend_api_key: str | None
    admin_email_to: str
    email_from: str
    shadow_mode: bool
    scheduler_enabled: bool
    report_dry_run: bool
    pattern_confidence: float
    horizon_weeks: int
    history_weeks: int
    future_read_weeks: int
    kpi_write_enabled: bool
    google_spreadsheet_id: str
    google_kpi_sheet_name: str
    google_service_account_json: str | None
    google_credentials_file: str | None
    cross_system_reconciliation_enabled: bool
    stripe_restricted_key: str | None
    stripe_pt_pack_beneficiary_map_json: str | None
    stripe_pt_pack_lookback_days: int
    trainerize_group_id: str | None
    trainerize_api_token: str | None
    trainerize_api_base_url: str
    trainerize_location_id: int | None
    revenue_gap_data_dir: str

    @property
    def timezone(self):
        return BRISBANE_TZ

    @classmethod
    def from_env(cls, require_runtime: bool = True) -> "Settings":
        shadow = _bool("SHADOW_MODE", True)
        if not shadow:
            raise RuntimeError("PT booking shadow service refuses to start unless SHADOW_MODE=true")

        def required(name: str, fallback: str = "") -> str:
            value = os.getenv(name, fallback).strip()
            if require_runtime and not value:
                raise RuntimeError(f"Missing required environment variable: {name}")
            return value

        return cls(
            ghl_api_key=(
                os.getenv("GHL_CALENDAR_API_KEY", "").strip()
                or required("GHL_API_KEY")
            ),
            ghl_location_id=required("GHL_LOCATION_ID"),
            database_path=os.getenv("DATABASE_PATH", "/data/pt_booking_shadow.db"),
            webhook_secret=required("WEBHOOK_SHARED_SECRET", "local-development-only"),
            resend_api_key=os.getenv("RESEND_API_KEY") or None,
            admin_email_to=os.getenv("ADMIN_EMAIL_TO", "admin@theevolvedgym.com.au"),
            email_from=os.getenv("EMAIL_FROM", "The Evolved <info@theevolvedgym.com.au>"),
            shadow_mode=shadow,
            scheduler_enabled=_bool("ENABLE_SCHEDULER", True),
            report_dry_run=_bool("REPORT_DRY_RUN", False),
            pattern_confidence=float(os.getenv("PATTERN_CONFIDENCE", "0.80")),
            horizon_weeks=int(os.getenv("HORIZON_WEEKS", "13")),
            history_weeks=int(os.getenv("HISTORY_WEEKS", "8")),
            future_read_weeks=int(os.getenv("FUTURE_READ_WEEKS", "15")),
            kpi_write_enabled=_bool("KPI_WRITE_ENABLED", False),
            google_spreadsheet_id=os.getenv(
                "GOOGLE_SPREADSHEET_ID",
                "1aeD8c2mY9rwltmVnTl86rx_rYXpSsAq3HTamk-hEs3c",
            ),
            google_kpi_sheet_name=os.getenv(
                "GOOGLE_KPI_SHEET_NAME", "KPI's The Evolved"
            ),
            google_service_account_json=os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
            or None,
            google_credentials_file=os.getenv("GOOGLE_SHEETS_CREDENTIALS_FILE")
            or None,
            cross_system_reconciliation_enabled=_bool(
                "CROSS_SYSTEM_RECONCILIATION_ENABLED", False
            ),
            stripe_restricted_key=os.getenv("STRIPE_RESTRICTED_KEY") or None,
            stripe_pt_pack_beneficiary_map_json=(
                os.getenv("STRIPE_PT_PACK_BENEFICIARY_MAP_JSON") or None
            ),
            stripe_pt_pack_lookback_days=int(
                os.getenv("STRIPE_PT_PACK_LOOKBACK_DAYS", "365")
            ),
            trainerize_group_id=os.getenv("TRAINERIZE_GROUP_ID") or None,
            trainerize_api_token=os.getenv("TRAINERIZE_API_TOKEN") or None,
            trainerize_api_base_url=os.getenv(
                "TRAINERIZE_API_BASE_URL", "https://api.trainerize.com/v03"
            ).rstrip("/"),
            trainerize_location_id=(
                int(os.environ["TRAINERIZE_LOCATION_ID"])
                if os.getenv("TRAINERIZE_LOCATION_ID", "").isdigit()
                else None
            ),
            revenue_gap_data_dir=os.getenv(
                "REVENUE_GAP_DATA_DIR", "/data/revenue-gap-control"
            ),
        )
