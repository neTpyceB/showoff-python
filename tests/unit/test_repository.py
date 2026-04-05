from __future__ import annotations

from pathlib import Path

import pytest

from showoff_api.repository import NotesRepository


@pytest.mark.unit
def test_repository_crud(tmp_path: Path) -> None:
    repository = NotesRepository(tmp_path / "nested" / "notes.db")
    repository.initialize()

    created = repository.create_note("First note", "Minimal API.")
    assert created == {"id": 1, "title": "First note", "content": "Minimal API."}
    assert repository.list_notes() == [created]
    assert repository.get_note(1) == created

    updated = repository.update_note(1, "Updated note", "Still minimal.")
    assert updated == {"id": 1, "title": "Updated note", "content": "Still minimal."}
    assert repository.delete_note(1) is True
    assert repository.list_notes() == []


@pytest.mark.unit
def test_repository_missing_records_return_none_or_false(tmp_path: Path) -> None:
    repository = NotesRepository(tmp_path / "notes.db")
    repository.initialize()

    assert repository.get_note(1) is None
    assert repository.update_note(1, "title", "content") is None
    assert repository.delete_note(1) is False


@pytest.mark.unit
def test_repository_create_raises_if_inserted_note_cannot_be_loaded(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    repository = NotesRepository(tmp_path / "notes.db")
    repository.initialize()
    monkeypatch.setattr(repository, "get_note", lambda note_id: None)

    with pytest.raises(RuntimeError, match="Created note was not found"):
        repository.create_note("First note", "Minimal API.")
