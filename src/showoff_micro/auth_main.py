from __future__ import annotations

import uvicorn

from .auth_app import create_auth_app
from .config import get_settings


def main() -> None:
    settings = get_settings()
    uvicorn.run(
        create_auth_app(settings),
        host=settings.auth_host,
        port=settings.auth_port,
    )


if __name__ == "__main__":  # pragma: no cover
    main()
