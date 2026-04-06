from __future__ import annotations

import pytest

import showoff_micro.worker_service as worker_service_module
from showoff_micro.worker_service import WorkerService, summarize_payload


class FakeDataClient:
    def __init__(self, job: dict[str, str] | None) -> None:
        self.job = job
        self.completed: tuple[str, str] | None = None

    def claim_next_job(self) -> dict[str, str] | None:
        current = self.job
        self.job = None
        return current

    def complete_job(self, job_id: str, result: str) -> dict[str, str]:
        self.completed = (job_id, result)
        return {"id": job_id, "result": result}


def test_summarize_payload_counts_words() -> None:
    assert summarize_payload("hello distributed world") == "word_count:3"


def test_run_once_processes_job() -> None:
    client = FakeDataClient({"id": "job-1", "payload": "hello world"})
    service = WorkerService(client, poll_seconds=1)

    worked = service.run_once()

    assert worked is True
    assert client.completed == ("job-1", "word_count:2")


def test_run_once_returns_false_without_job() -> None:
    service = WorkerService(FakeDataClient(None), poll_seconds=1)

    assert service.run_once() is False


def test_run_forever_sleeps_when_no_job(monkeypatch) -> None:
    service = WorkerService(FakeDataClient(None), poll_seconds=2)
    captured: dict[str, object] = {}

    def fake_sleep(seconds: int) -> None:
        captured["seconds"] = seconds
        raise RuntimeError("stop")

    monkeypatch.setattr(worker_service_module, "sleep", fake_sleep)

    with pytest.raises(RuntimeError, match="stop"):
        service.run_forever()

    assert captured["seconds"] == 2


def test_run_forever_loops_after_processing_job(monkeypatch) -> None:
    service = WorkerService(FakeDataClient(None), poll_seconds=3)
    outcomes = iter([True, False])
    captured: dict[str, object] = {}

    monkeypatch.setattr(service, "run_once", lambda: next(outcomes))

    def fake_sleep(seconds: int) -> None:
        captured["seconds"] = seconds
        raise RuntimeError("stop")

    monkeypatch.setattr(worker_service_module, "sleep", fake_sleep)

    with pytest.raises(RuntimeError, match="stop"):
        service.run_forever()

    assert captured["seconds"] == 3
