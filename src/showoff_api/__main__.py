from __future__ import annotations

import uvicorn

from showoff_api.app import create_app
from showoff_api.config import Settings


def main() -> int:
    settings = Settings.from_env()
    uvicorn.run(create_app(settings), host=settings.host, port=settings.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
