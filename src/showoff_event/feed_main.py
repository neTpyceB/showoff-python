from __future__ import annotations

import uvicorn

from .config import get_settings
from .feed_app import create_feed_app


def main() -> None:
    settings = get_settings()
    uvicorn.run(
        create_feed_app(settings),
        host=settings.feed_host,
        port=settings.feed_port,
    )


if __name__ == "__main__":  # pragma: no cover
    main()
