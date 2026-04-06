from __future__ import annotations

from time import sleep

from .data_client import DataClient


def summarize_payload(payload: str) -> str:
    return f"word_count:{len(payload.split())}"


class WorkerService:
    def __init__(self, data_client: DataClient, poll_seconds: int) -> None:
        self._data_client = data_client
        self._poll_seconds = poll_seconds

    def run_once(self) -> bool:
        job = self._data_client.claim_next_job()
        if job is None:
            return False
        self._data_client.complete_job(job["id"], summarize_payload(job["payload"]))
        return True

    def run_forever(self) -> None:
        while True:
            worked = self.run_once()
            if not worked:
                sleep(self._poll_seconds)
