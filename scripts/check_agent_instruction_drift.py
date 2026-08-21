#!/usr/bin/env python3
"""Fail when AGENTS.md stops being the small pointer to canonical CLAUDE.md."""

from __future__ import annotations

import difflib
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
AGENTS_PATH = ROOT / "AGENTS.md"
CLAUDE_PATH = ROOT / "CLAUDE.md"

EXPECTED_AGENTS = """# Codex workspace instructions

<!-- canonical-workspace-instructions: CLAUDE.md -->

`CLAUDE.md` is the canonical source of truth for this workspace. This file exists only as the Codex-compatible entry point.

## Required startup

1. Read `CLAUDE.md` completely before planning or taking action.
2. Follow every applicable instruction in `CLAUDE.md` as repository guidance.
3. When permanent workspace guidance changes, update `CLAUDE.md`; do not copy those rules into this file.

## Drift protection

Keep this file as a small pointer only. Do not add business rules, operating procedures, workspace indexes, or duplicated sections from `CLAUDE.md`.

After changing either instruction file, run:

```bash
python3 scripts/check_agent_instruction_drift.py
```
"""

CANONICAL_DECLARATION = (
    "**This file (CLAUDE.md) is the foundation.** It is automatically loaded "
    "at the start of every session. Keep it current"
)


def fail(message: str) -> None:
    print(f"Instruction drift check failed: {message}", file=sys.stderr)


def main() -> int:
    errors: list[str] = []

    if not CLAUDE_PATH.is_file():
        errors.append("canonical CLAUDE.md is missing")
    else:
        claude_text = CLAUDE_PATH.read_text(encoding="utf-8")
        if CANONICAL_DECLARATION not in claude_text:
            errors.append(
                "CLAUDE.md no longer contains its canonical-source declaration"
            )

    if not AGENTS_PATH.is_file():
        errors.append("Codex entry point AGENTS.md is missing")
    else:
        agents_text = AGENTS_PATH.read_text(encoding="utf-8")
        if agents_text != EXPECTED_AGENTS:
            errors.append(
                "AGENTS.md contains drift or duplicated guidance; restore the "
                "pointer-only content shown below"
            )
            diff = difflib.unified_diff(
                agents_text.splitlines(),
                EXPECTED_AGENTS.splitlines(),
                fromfile="current/AGENTS.md",
                tofile="expected/AGENTS.md",
                lineterm="",
            )
            print("\n".join(diff), file=sys.stderr)

    if errors:
        for error in errors:
            fail(error)
        return 1

    print("Agent instruction drift check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
