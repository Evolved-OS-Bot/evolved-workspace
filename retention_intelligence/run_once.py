from __future__ import annotations

import json
from pathlib import Path

from .config import Settings, load_local_env
from .service import RetentionService


def main() -> int:
    load_local_env(Path(__file__).parent / ".env")
    settings = Settings.from_env()
    result = RetentionService(settings).run(
        write_sheets=settings.sheets_write_enabled
    )
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
