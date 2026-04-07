from __future__ import annotations

import uvicorn

from .config import get_settings
from .platform_app import create_platform_app


def main() -> None:
    settings = get_settings()
    uvicorn.run(
        create_platform_app(settings),
        host=settings.platform_host,
        port=settings.platform_port,
    )


if __name__ == "__main__":  # pragma: no cover
    main()
