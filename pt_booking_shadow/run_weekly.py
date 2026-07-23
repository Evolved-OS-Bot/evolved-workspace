from __future__ import annotations

import argparse
from pathlib import Path

from .config import Settings, load_local_env
from .service import ShadowAuditService


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the PT booking continuity shadow audit.")
    parser.add_argument("--send-email", action="store_true")
    args = parser.parse_args()

    load_local_env(Path(__file__).parent / ".env")
    settings = Settings.from_env()
    run_id, findings = ShadowAuditService(settings).run_full(send_email=args.send_email)
    counts: dict[str, int] = {}
    for finding in findings:
        counts[finding.category] = counts.get(finding.category, 0) + 1
    print({"run_id": run_id, "contacts": len(findings), "categories": counts})


if __name__ == "__main__":
    main()
