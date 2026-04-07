from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel


class EventType(StrEnum):
    ACTIVITY_CREATED = "activity.created"


class HealthResponse(BaseModel):
    status: str


class PublishActivityRequest(BaseModel):
    user_id: str
    title: str
    detail: str


class EventEnvelope(BaseModel):
    event_id: str
    type: EventType
    user_id: str
    title: str
    detail: str
    created_at: str


class FeedEntry(BaseModel):
    event_id: str
    title: str
    detail: str
    created_at: str


class NotificationEntry(BaseModel):
    event_id: str
    message: str
    created_at: str


class AuditEntry(BaseModel):
    event_id: str
    type: EventType
    user_id: str
    title: str
    detail: str
    created_at: str
