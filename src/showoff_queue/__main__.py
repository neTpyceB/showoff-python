from __future__ import annotations

import uvicorn

from showoff_queue.app import create_app
from showoff_queue.config import QueueSettings


def main() -> int:
    settings = QueueSettings.from_env()
    uvicorn.run(create_app(settings), host=settings.host, port=settings.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
