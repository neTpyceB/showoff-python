from __future__ import annotations

from .config import get_settings
from .data_client import DataClient
from .worker_service import WorkerService


def main() -> None:
    settings = get_settings()
    WorkerService(
        data_client=DataClient(settings.data_service_url),
        poll_seconds=settings.worker_poll_seconds,
    ).run_forever()


if __name__ == "__main__":  # pragma: no cover
    main()
