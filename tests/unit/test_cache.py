from __future__ import annotations

from showoff_perf.cache import RedisCache


class FakeRedisClient:
    def __init__(self) -> None:
        self.storage: dict[str, str] = {}

    def get(self, key: str) -> str | None:
        return self.storage.get(key)

    def set(self, name: str, value: str, ex: int) -> None:
        self.storage[name] = value

    def ping(self) -> bool:
        return True


def test_redis_cache_delegates_to_client(monkeypatch) -> None:
    fake_client = FakeRedisClient()
    monkeypatch.setattr(
        "showoff_perf.cache.Redis.from_url",
        lambda *args, **kwargs: fake_client,
    )

    cache = RedisCache("redis://cache:6379/0")
    cache.set("key", "value", ex=10)

    assert cache.get("key") == "value"
    assert cache.ping() is True
