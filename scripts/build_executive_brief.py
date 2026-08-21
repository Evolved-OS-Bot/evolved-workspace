#!/usr/bin/env python3
"""Build the aggregate, share-safe Evolved reporting brief."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from reporting_control.executive_brief import (  # noqa: E402
    build_executive_brief,
    render_markdown,
)


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(path)


def main() -> int:
    brief = build_executive_brief(
        root=ROOT,
        registry_path=ROOT / "reporting_control" / "report_registry.json",
    )
    output = ROOT / "outputs" / "reporting-control-plane"
    atomic_write(
        output / "latest-executive-brief.json",
        json.dumps(brief, indent=2, sort_keys=True) + "\n",
    )
    atomic_write(
        output / "latest-executive-brief.md",
        render_markdown(brief),
    )
    print(
        json.dumps(
            {
                "status": "complete",
                "reports": len(brief["reports"]),
                "status_counts": brief["report_status_counts"],
                "output": str(output / "latest-executive-brief.md"),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
