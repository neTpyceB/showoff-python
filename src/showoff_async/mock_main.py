from __future__ import annotations

import uvicorn

from showoff_async.config import MockSettings
from showoff_async.mock_app import create_mock_app


def main() -> int:
    settings = MockSettings.from_env()
    uvicorn.run(create_mock_app(), host=settings.host, port=settings.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
