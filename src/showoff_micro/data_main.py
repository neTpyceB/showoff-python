from __future__ import annotations

import uvicorn

from .config import get_settings
from .data_app import create_data_app


def main() -> None:
    settings = get_settings()
    uvicorn.run(
        create_data_app(settings),
        host=settings.data_host,
        port=settings.data_port,
    )


if __name__ == "__main__":  # pragma: no cover
    main()
