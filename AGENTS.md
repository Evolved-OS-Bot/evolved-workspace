# Codex workspace instructions

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
