from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from typing import Any


def normalise_email(value: Any) -> str:
    return str(value or "").strip().lower()


def normalise_phone(value: Any) -> str:
    digits = re.sub(r"\D", "", str(value or ""))
    if digits.startswith("61") and len(digits) >= 11:
        digits = "0" + digits[2:]
    return digits


def decimal_value(value: Any) -> Decimal | None:
    if value is None or value == "":
        return None
    if isinstance(value, Decimal):
        return value
    if isinstance(value, (int, float)):
        return Decimal(str(value)).quantize(Decimal("0.01"))
    text = str(value).strip()
    if not text or text.upper() in {"PIF", "PIA", "N/A", "-", "NONE"}:
        return None
    text = text.replace("$", "").replace(",", "")
    try:
        return Decimal(text).quantize(Decimal("0.01"))
    except InvalidOperation:
        return None
