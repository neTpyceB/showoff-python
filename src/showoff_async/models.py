from __future__ import annotations

from pydantic import BaseModel


class ProfileData(BaseModel):
    user_id: str
    name: str
    role: str


class ActivityData(BaseModel):
    user_id: str
    commits: int
    reviews: int


class StatusData(BaseModel):
    user_id: str
    availability: str


class AggregateResponse(BaseModel):
    user_id: str
    profile: ProfileData
    activity: ActivityData
    status: StatusData
