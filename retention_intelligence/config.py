from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


BRISBANE_TZ = ZoneInfo("Australia/Brisbane")


def _bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


def _json(name: str, default: Any) -> Any:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{name} is not valid JSON") from exc


def load_local_env(path: Path) -> None:
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


@dataclass(frozen=True)
class Settings:
    database_url: str
    reconciliation_database: str
    webhook_secret: str
    shadow_mode: bool
    scheduler_enabled: bool
    sheets_write_enabled: bool
    google_spreadsheet_id: str
    google_service_account_json: str | None
    google_credentials_file: str | None
    radar_sheet_name: str
    kpi_sheet_name: str
    account_classifications: dict[str, dict[str, Any]]
    identity_links: dict[str, str]
    identity_record_links: dict[tuple[str, str], str]
    authoritative_stripe_customers: dict[str, str]

    @classmethod
    def from_env(cls, require_runtime: bool = True) -> "Settings":
        if not _bool("SHADOW_MODE", True):
            raise RuntimeError("Retention service refuses to start unless SHADOW_MODE=true")

        def required(name: str, fallback: str = "") -> str:
            value = os.getenv(name, fallback).strip()
            if require_runtime and not value:
                raise RuntimeError(f"Missing required environment variable: {name}")
            return value

        record_links: dict[tuple[str, str], str] = {}
        for key, canonical in _json("IDENTITY_RECORD_LINKS_JSON", {}).items():
            source, separator, source_id = str(key).partition(":")
            if not separator:
                raise RuntimeError(
                    "IDENTITY_RECORD_LINKS_JSON keys must use source:source_id"
                )
            record_links[(source, source_id)] = str(canonical).strip().lower()

        return cls(
            database_url=os.getenv(
                "DATABASE_URL", "sqlite:////tmp/retention_intelligence.db"
            ),
            reconciliation_database=os.getenv(
                "RECONCILIATION_DATABASE",
                "/tmp/retention-intelligence/reconciliation.sqlite",
            ),
            webhook_secret=required("WEBHOOK_SHARED_SECRET", "local-development-only"),
            shadow_mode=True,
            scheduler_enabled=_bool("ENABLE_SCHEDULER", True),
            sheets_write_enabled=_bool("SHEETS_WRITE_ENABLED", False),
            google_spreadsheet_id=os.getenv(
                "GOOGLE_SPREADSHEET_ID",
                "1aeD8c2mY9rwltmVnTl86rx_rYXpSsAq3HTamk-hEs3c",
            ),
            google_service_account_json=os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
            or None,
            google_credentials_file=os.getenv("GOOGLE_SHEETS_CREDENTIALS_FILE")
            or None,
            radar_sheet_name=os.getenv("RETENTION_RADAR_SHEET", "Retention Radar"),
            kpi_sheet_name=os.getenv("RETENTION_KPI_SHEET", "Retention KPI"),
            account_classifications=_json("ACCOUNT_CLASSIFICATIONS_JSON", {}),
            identity_links={
                str(key).strip().lower(): str(value).strip().lower()
                for key, value in _json("IDENTITY_LINKS_JSON", {}).items()
            },
            identity_record_links=record_links,
            authoritative_stripe_customers={
                str(key).strip().lower(): str(value).strip()
                for key, value in _json(
                    "AUTHORITATIVE_STRIPE_CUSTOMERS_JSON", {}
                ).items()
            },
        )
