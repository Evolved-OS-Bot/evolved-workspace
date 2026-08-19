"""Railway-only weekly Website V2 public-proof delivery job."""

from __future__ import annotations

import json
import os
from collections.abc import Mapping

from reporting_control.website_public_proof import publish_latest


REQUIRED_ENVIRONMENT = (
    "PUBLIC_PROOF_HUB_URL",
    "PUBLIC_PROOF_HUB_SECRET",
    "PUBLIC_PROOF_WORDPRESS_URL",
    "PUBLIC_PROOF_WORDPRESS_SECRET",
)


def run_from_environment(
    environment: Mapping[str, str] | None = None,
) -> dict[str, object]:
    values = environment or os.environ
    missing = [key for key in REQUIRED_ENVIRONMENT if not values.get(key)]
    if missing:
        raise RuntimeError(
            "Missing required Website public-proof configuration: "
            + ", ".join(missing)
        )
    return publish_latest(
        hub_url=values["PUBLIC_PROOF_HUB_URL"],
        hub_secret=values["PUBLIC_PROOF_HUB_SECRET"],
        wordpress_url=values["PUBLIC_PROOF_WORDPRESS_URL"],
        wordpress_secret=values["PUBLIC_PROOF_WORDPRESS_SECRET"],
    )


def main() -> int:
    result = run_from_environment()
    print(json.dumps({
        "status": result.get("status"),
        "snapshotId": result.get("snapshotId"),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
