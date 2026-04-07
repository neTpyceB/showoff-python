from __future__ import annotations

import uvicorn

from .audit_app import create_audit_app
from .config import get_settings


def main() -> None:
    settings = get_settings()
    uvicorn.run(
        create_audit_app(settings),
        host=settings.audit_host,
        port=settings.audit_port,
    )


if __name__ == "__main__":  # pragma: no cover
    main()
