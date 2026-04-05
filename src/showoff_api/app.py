from __future__ import annotations

from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    FastAPI,
    HTTPException,
    Path,
    Request,
    Response,
    status,
)

from showoff_api import __version__
from showoff_api.auth import require_bearer_token
from showoff_api.config import Settings
from showoff_api.repository import NotesRepository
from showoff_api.schemas import NoteCreate, NoteRead, NoteUpdate

NoteId = Annotated[int, Path(ge=1)]


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


def get_repository(request: Request) -> NotesRepository:
    return request.app.state.repository


def create_app(settings: Settings) -> FastAPI:
    repository = NotesRepository(settings.database_path)
    repository.initialize()

    app = FastAPI(
        title="Notes REST API Service",
        version=__version__,
        summary="Bearer-protected CRUD API for notes.",
    )
    app.state.settings = settings
    app.state.repository = repository

    router = APIRouter(
        prefix="/notes",
        tags=["notes"],
        dependencies=[Depends(require_bearer_token)],
    )

    @router.get("", response_model=list[NoteRead])
    def list_notes(
        repo: Annotated[NotesRepository, Depends(get_repository)],
    ) -> list[dict]:
        return repo.list_notes()

    @router.post("", response_model=NoteRead, status_code=status.HTTP_201_CREATED)
    def create_note(
        payload: NoteCreate,
        repo: Annotated[NotesRepository, Depends(get_repository)],
    ) -> dict:
        return repo.create_note(payload.title, payload.content)

    @router.get("/{note_id}", response_model=NoteRead)
    def read_note(
        note_id: NoteId,
        repo: Annotated[NotesRepository, Depends(get_repository)],
    ) -> dict:
        note = repo.get_note(note_id)
        if note is None:
            raise HTTPException(status_code=404, detail="Note not found")
        return note

    @router.put("/{note_id}", response_model=NoteRead)
    def update_note(
        note_id: NoteId,
        payload: NoteUpdate,
        repo: Annotated[NotesRepository, Depends(get_repository)],
    ) -> dict:
        note = repo.update_note(note_id, payload.title, payload.content)
        if note is None:
            raise HTTPException(status_code=404, detail="Note not found")
        return note

    @router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
    def delete_note(
        note_id: NoteId,
        repo: Annotated[NotesRepository, Depends(get_repository)],
    ) -> Response:
        deleted = repo.delete_note(note_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Note not found")
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    app.include_router(router)
    return app
