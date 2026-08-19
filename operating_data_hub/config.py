from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date
from zoneinfo import ZoneInfo


BRISBANE_TZ = ZoneInfo("Australia/Brisbane")


def _bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def _csv(name: str, default: str = "") -> tuple[str, ...]:
    return tuple(
        value.strip()
        for value in os.getenv(name, default).split(",")
        if value.strip()
    )


def _optional_date(name: str) -> date | None:
    value = os.getenv(name, "").strip()
    return date.fromisoformat(value) if value else None


@dataclass(frozen=True)
class Settings:
    database_url: str
    webhook_secret: str
    milestone_referral_secret: str
    dashboard_password: str
    flask_secret: str
    shadow_mode: bool
    scheduler_enabled: bool
    educational_intelligence_scheduler_enabled: bool
    educational_intelligence_discord_enabled: bool
    educational_intelligence_discord_webhook_url: str
    educational_intelligence_review_url: str
    google_spreadsheet_id: str
    google_service_account_json: str | None
    retention_health_url: str
    pt_health_url: str
    ghl_api_key: str
    ghl_location_id: str
    conversation_clearance_shadow_enabled: bool
    conversation_assignment_write_enabled: bool
    conversation_message_write_enabled: bool
    conversation_admin_user_id: str
    conversation_cover_user_id: str
    sa_calendar_ids: tuple[str, ...]
    sa_grace_minutes: int
    sa_feedback_matching_days: int
    sa_collection_lookback_days: int
    sa_collection_lookahead_days: int
    sa_legacy_attendance_cutoff: date
    sa_listed_history_enabled: bool
    sa_feedback_form_id: str
    sa_feedback_sales_outcome_field_id: str
    sa_ghl_write_enabled: bool
    sa_task_write_enabled: bool
    sa_task_followup_lookback_days: int
    sa_task_admin_user_id: str
    onboarding_task_write_enabled: bool
    onboarding_task_followup_lookback_days: int
    trainerize_attendance_enabled: bool
    trainerize_group_id: str
    trainerize_api_token: str
    trainerize_location_id: int | None
    sa_sheets_write_enabled: bool
    sa_sheet_tab_name: str
    sa_sheet_tab_id: int | None
    reporting_v2_manual_inputs_enabled: bool
    stripe_restricted_key: str
    reporting_v2_cash_lookback_days: int
    reporting_v2_cash_overlap_days: int
    xero_client_id: str
    xero_client_secret: str
    xero_redirect_uri: str
    xero_token_encryption_key: str
    xero_tenant_name: str
    ga4_property_id: str
    ga4_measurement_id: str
    website_analytics_started_on: date
    website_v2_cutover_reporting_start: date | None
    ghl_subscriber_form_id: str

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
            milestone_referral_secret=required(
                "MILESTONE_REFERRAL_SECRET",
                os.getenv("HUB_WEBHOOK_SECRET", "local-development-only"),
            ),
            dashboard_password=required(
                "HUB_DASHBOARD_PASSWORD", "local-dashboard"
            ),
            flask_secret=required(
                "HUB_FLASK_SECRET", "local-session-secret"
            ),
            shadow_mode=True,
            scheduler_enabled=_bool("HUB_SCHEDULER_ENABLED", True),
            educational_intelligence_scheduler_enabled=_bool(
                "EDUCATIONAL_INTELLIGENCE_SCHEDULER_ENABLED",
                False,
            ),
            educational_intelligence_discord_enabled=_bool(
                "EDUCATIONAL_INTELLIGENCE_DISCORD_ENABLED",
                False,
            ),
            educational_intelligence_discord_webhook_url=os.getenv(
                "EDUCATIONAL_INTELLIGENCE_DISCORD_WEBHOOK_URL",
                "",
            ).strip(),
            educational_intelligence_review_url=os.getenv(
                "EDUCATIONAL_INTELLIGENCE_REVIEW_URL",
                "",
            ).strip(),
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
            ghl_api_key=os.getenv("GHL_API_KEY", "").strip(),
            ghl_location_id=os.getenv("GHL_LOCATION_ID", "").strip(),
            conversation_clearance_shadow_enabled=_bool(
                "CONVERSATION_CLEARANCE_SHADOW_ENABLED",
                True,
            ),
            conversation_assignment_write_enabled=_bool(
                "CONVERSATION_ASSIGNMENT_WRITE_ENABLED",
                False,
            ),
            conversation_message_write_enabled=_bool(
                "CONVERSATION_MESSAGE_WRITE_ENABLED",
                False,
            ),
            conversation_admin_user_id=os.getenv(
                "GHL_ADMIN_EVE_USER_ID", ""
            ).strip(),
            conversation_cover_user_id=os.getenv(
                "GHL_CONVERSATION_COVER_USER_ID", ""
            ).strip(),
            sa_calendar_ids=_csv(
                "SA_ATTENDANCE_CALENDAR_IDS",
                "HSVEzfJH4nice96IxHem",
            ),
            sa_grace_minutes=max(
                0,
                int(os.getenv("SA_ATTENDANCE_GRACE_MINUTES", "60")),
            ),
            sa_feedback_matching_days=max(
                1,
                int(os.getenv("SA_ATTENDANCE_MATCHING_DAYS", "7")),
            ),
            sa_collection_lookback_days=max(
                7,
                int(os.getenv("SA_ATTENDANCE_LOOKBACK_DAYS", "120")),
            ),
            sa_collection_lookahead_days=max(
                14,
                int(os.getenv("SA_ATTENDANCE_LOOKAHEAD_DAYS", "730")),
            ),
            sa_legacy_attendance_cutoff=date.fromisoformat(
                os.getenv(
                    "SA_ATTENDANCE_LEGACY_SHOWED_BEFORE",
                    "2026-03-12",
                ).strip()
            ),
            sa_listed_history_enabled=_bool(
                "SA_LISTED_HISTORY_ENABLED",
                True,
            ),
            sa_feedback_form_id=os.getenv(
                "SA_FEEDBACK_FORM_ID",
                "Z83KtjAPMclhe8bsFJwS",
            ).strip(),
            sa_feedback_sales_outcome_field_id=os.getenv(
                "SA_FEEDBACK_SALES_OUTCOME_FIELD_ID",
                "ptOLpBIUbjaZLVHoAJAz",
            ).strip(),
            sa_ghl_write_enabled=_bool(
                "SA_ATTENDANCE_GHL_WRITE_ENABLED",
                False,
            ),
            sa_task_write_enabled=_bool(
                "SA_ATTENDANCE_TASK_WRITE_ENABLED",
                False,
            ),
            sa_task_followup_lookback_days=max(
                1,
                int(os.getenv("SA_ATTENDANCE_TASK_LOOKBACK_DAYS", "7")),
            ),
            sa_task_admin_user_id=os.getenv(
                "GHL_ADMIN_EVE_USER_ID",
                "",
            ).strip(),
            onboarding_task_write_enabled=_bool(
                "ONBOARDING_OUTCOME_TASK_WRITE_ENABLED",
                False,
            ),
            onboarding_task_followup_lookback_days=max(
                1,
                int(
                    os.getenv(
                        "ONBOARDING_OUTCOME_TASK_LOOKBACK_DAYS",
                        "14",
                    )
                ),
            ),
            trainerize_attendance_enabled=_bool(
                "TRAINERIZE_ATTENDANCE_PRECHECK_ENABLED",
                False,
            ),
            trainerize_group_id=os.getenv(
                "TRAINERIZE_GROUP_ID",
                "",
            ).strip(),
            trainerize_api_token=os.getenv(
                "TRAINERIZE_API_TOKEN",
                "",
            ).strip(),
            trainerize_location_id=(
                int(os.getenv("TRAINERIZE_LOCATION_ID", ""))
                if os.getenv("TRAINERIZE_LOCATION_ID", "").strip().isdigit()
                else None
            ),
            sa_sheets_write_enabled=_bool(
                "SA_ATTENDANCE_SHEETS_WRITE_ENABLED",
                False,
            ),
            sa_sheet_tab_name=os.getenv(
                "SA_ATTENDANCE_SHEET_TAB",
                "SA Attendance",
            ).strip(),
            sa_sheet_tab_id=(
                int(os.getenv("SA_ATTENDANCE_SHEET_TAB_ID", ""))
                if os.getenv("SA_ATTENDANCE_SHEET_TAB_ID", "").strip()
                else None
            ),
            reporting_v2_manual_inputs_enabled=_bool(
                "REPORTING_V2_MANUAL_INPUTS_ENABLED",
                False,
            ),
            stripe_restricted_key=os.getenv(
                "STRIPE_RESTRICTED_KEY",
                "",
            ).strip(),
            reporting_v2_cash_lookback_days=max(
                365,
                int(os.getenv("REPORTING_V2_CASH_LOOKBACK_DAYS", "400")),
            ),
            reporting_v2_cash_overlap_days=max(
                1,
                int(os.getenv("REPORTING_V2_CASH_OVERLAP_DAYS", "3")),
            ),
            xero_client_id=os.getenv("XERO_CLIENT_ID", "").strip(),
            xero_client_secret=os.getenv("XERO_CLIENT_SECRET", "").strip(),
            xero_redirect_uri=os.getenv(
                "XERO_REDIRECT_URI",
                "https://evolved-operating-data-hub-production.up.railway.app/api/v1/xero/callback",
            ).strip(),
            xero_token_encryption_key=os.getenv(
                "XERO_TOKEN_ENCRYPTION_KEY", ""
            ).strip(),
            xero_tenant_name=os.getenv(
                "XERO_TENANT_NAME", "Brown Casserly Pty Ltd"
            ).strip(),
            ga4_property_id=os.getenv(
                "GA4_PROPERTY_ID", "429372468"
            ).strip(),
            ga4_measurement_id=os.getenv(
                "GA4_MEASUREMENT_ID", "G-RXM7LVC0VJ"
            ).strip(),
            website_analytics_started_on=date.fromisoformat(
                os.getenv(
                    "WEBSITE_ANALYTICS_STARTED_ON",
                    "2024-10-23",
                ).strip()
            ),
            website_v2_cutover_reporting_start=_optional_date(
                "WEBSITE_V2_CUTOVER_REPORTING_START"
            ),
            ghl_subscriber_form_id=os.getenv(
                "GHL_SUBSCRIBER_FORM_ID",
                "qB8xGGwhLdSGtbc3Z0EJ",
            ).strip(),
        )
