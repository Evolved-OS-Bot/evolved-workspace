from __future__ import annotations

from .app import create_app, start_scheduler
from .config import Settings


settings = Settings.from_env()
app = create_app(settings)
start_scheduler(app, settings)
