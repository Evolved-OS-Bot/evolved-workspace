#!/usr/bin/env python3
"""Fail when a canonical Evolved standard is missing or stale downstream."""

from __future__ import annotations

import hashlib
import html
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTER_PATH = ROOT / "outputs" / "systems" / "evolved-standards-cascade-register.json"


def clean(value: str) -> str:
    value = html.unescape(value)
    value = re.sub(r"<[^>]+>", " ", value)
    value = re.sub(r"[*_`]", "", value)
    value = value.replace("—", " ").replace("–", " ").replace("-", " ")
    value = value.replace("×", " x ")
    value = re.sub(r"[^a-zA-Z0-9%+<:.]+", " ", value)
    return re.sub(r"\s+", " ", value).strip().lower()


def markdown_rows(text: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 4:
            continue
        if clean(cells[0]) in {"exercise", "standard", "canonical standard"}:
            continue
        if all(re.fullmatch(r":?---+:?", cell) for cell in cells):
            continue
        rows.append(cells)
    return rows


def canonical_rows(path: Path) -> list[list[str]]:
    text = path.read_text(encoding="utf-8")
    start = text.index("## The Standards Tables")
    end = text.index("## Movement Breakdown Framework")
    rows = markdown_rows(text[start:end])
    return [row[:4] for row in rows]


def target_rows(path: Path) -> list[list[str]]:
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".html":
        rows: list[list[str]] = []
        for block in re.findall(r"<tr[^>]*>(.*?)</tr>", text, re.I | re.S):
            cells = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", block, re.I | re.S)
            if cells:
                rows.append(cells)
        return rows
    return markdown_rows(text)


def fingerprint(rows: list[list[str]]) -> str:
    payload = json.dumps([[clean(cell) for cell in row] for row in rows], separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def row_is_represented(canonical: list[str], candidates: list[list[str]]) -> bool:
    exercise = clean(canonical[0])
    thresholds = [clean(cell) for cell in canonical[1:4]]
    for candidate in candidates:
        if not candidate or clean(candidate[0]) != exercise:
            continue
        candidate_text = " ".join(clean(cell) for cell in candidate[1:])
        if all(threshold in candidate_text for threshold in thresholds):
            return True
    return False


def main() -> int:
    register = json.loads(REGISTER_PATH.read_text(encoding="utf-8"))
    source = ROOT / register["canonical_source"]
    standards = canonical_rows(source)
    actual_fingerprint = fingerprint(standards)
    errors: list[str] = []

    if len(standards) != register["canonical_table_rows"]:
        errors.append(
            f"Canonical row count changed: expected {register['canonical_table_rows']}, "
            f"found {len(standards)}"
        )

    if actual_fingerprint != register["canonical_standards_fingerprint"]:
        errors.append(
            "Canonical standards fingerprint changed. Review every governed cascade item "
            f"and update the register only after verification. Current: {actual_fingerprint}"
        )

    for relative_path in register["required_local_surfaces"]:
        path = ROOT / relative_path
        if not path.exists():
            errors.append(f"Missing required surface: {relative_path}")
            continue
        candidates = target_rows(path)
        missing = [
            row[0]
            for row in standards
            if not row_is_represented(row, candidates)
        ]
        if missing:
            errors.append(f"{relative_path}: missing or stale rows: {', '.join(missing)}")

    for relative_path in register["quiz_audit_surfaces"]:
        if not (ROOT / relative_path).exists():
            errors.append(f"Missing quiz audit surface: {relative_path}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print(
        f"Evolved standards cascade passed: {len(standards)} canonical rows, "
        f"{len(register['required_local_surfaces'])} local surfaces, "
        f"fingerprint {actual_fingerprint}."
    )
    print(
        "Manual verification remains required for registered Trainerize and GHL live surfaces."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
