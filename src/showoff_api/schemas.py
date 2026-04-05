from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, StringConstraints

Title = Annotated[str, StringConstraints(min_length=1, max_length=120)]
Content = Annotated[str, StringConstraints(min_length=1, max_length=5000)]


class NoteCreate(BaseModel):
    title: Title
    content: Content


class NoteUpdate(BaseModel):
    title: Title
    content: Content


class NoteRead(BaseModel):
    id: int
    title: Title
    content: Content
