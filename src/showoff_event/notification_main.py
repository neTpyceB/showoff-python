from __future__ import annotations

import uvicorn

from .config import get_settings
from .notification_app import create_notification_app


def main() -> None:
    settings = get_settings()
    uvicorn.run(
        create_notification_app(settings),
        host=settings.notification_host,
        port=settings.notification_port,
    )


if __name__ == "__main__":  # pragma: no cover
    main()
