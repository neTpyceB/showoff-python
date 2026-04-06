from __future__ import annotations

from showoff_micro.store import JobStore


def make_store(tmp_path) -> JobStore:
    store = JobStore(str(tmp_path / "micro.db"))
    store.ensure_schema()
    return store


def test_create_and_get_job(tmp_path) -> None:
    store = make_store(tmp_path)

    created = store.create_job("alice", "hello world")
    loaded = store.get_job(created["id"])

    assert created["owner_user_id"] == "alice"
    assert created["status"] == "queued"
    assert loaded == created


def test_claim_and_complete_job(tmp_path) -> None:
    store = make_store(tmp_path)
    created = store.create_job("alice", "hello world")

    claimed = store.claim_next_job()
    completed = store.complete_job(created["id"], "word_count:2")

    assert claimed["status"] == "processing"
    assert completed["status"] == "done"
    assert completed["result"] == "word_count:2"


def test_claim_next_job_returns_none_when_empty(tmp_path) -> None:
    store = make_store(tmp_path)

    assert store.claim_next_job() is None
