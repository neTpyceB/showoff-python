from __future__ import annotations

from typing import Protocol

from redis import Redis


class Cache(Protocol):
    def get(self, key: str) -> str | None: ...
    def set(self, key: str, value: str, ex: int) -> None: ...
    def ping(self) -> bool: ...


class RedisCache:
    def __init__(self, redis_url: str) -> None:
        self._client = Redis.from_url(redis_url, decode_responses=True)

    def get(self, key: str) -> str | None:
        return self._client.get(key)

    def set(self, key: str, value: str, ex: int) -> None:
        self._client.set(name=key, value=value, ex=ex)

    def ping(self) -> bool:
        return bool(self._client.ping())
