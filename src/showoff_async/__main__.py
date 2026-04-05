from __future__ import annotations

import uvicorn

from showoff_async.app import create_app
from showoff_async.config import AggregatorSettings


def main() -> int:
    settings = AggregatorSettings.from_env()
    uvicorn.run(create_app(settings), host=settings.host, port=settings.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
