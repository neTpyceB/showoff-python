from __future__ import annotations

import asyncio

import pytest

import showoff_event.bus as bus_module
from showoff_event.bus import RedisPublisher, consume_events
from showoff_event.models import EventEnvelope, EventType


class FakePubSub:
    def __init__(self) -> None:
        self.calls = 0
        self.channel = None
        self.closed = False
        self.unsubscribed = None

    async def subscribe(self, channel: str) -> None:
        self.channel = channel

    async def get_message(self, ignore_subscribe_messages: bool, timeout: float):
        self.calls += 1
        if self.calls == 1:
            return None
        if self.calls == 2:
            return {
                "data": EventEnvelope(
                    event_id="event-1",
                    type=EventType.ACTIVITY_CREATED,
                    user_id="alice",
                    title="Ride completed",
                    detail="Airport to city center",
                    created_at="2026-04-06T16:00:00+00:00",
                ).model_dump_json()
            }
        await asyncio.sleep(10)

    async def unsubscribe(self, channel: str) -> None:
        self.unsubscribed = channel

    async def aclose(self) -> None:
        self.closed = True


class FakeRedisClient:
    def __init__(self, pubsub: FakePubSub | None = None) -> None:
        self._pubsub = pubsub or FakePubSub()
        self.published = []
        self.closed = False

    async def publish(self, channel: str, data: str) -> None:
        self.published.append((channel, data))

    def pubsub(self) -> FakePubSub:
        return self._pubsub

    async def aclose(self) -> None:
        self.closed = True


def make_event() -> EventEnvelope:
    return EventEnvelope(
        event_id="event-1",
        type=EventType.ACTIVITY_CREATED,
        user_id="alice",
        title="Ride completed",
        detail="Airport to city center",
        created_at="2026-04-06T16:00:00+00:00",
    )


@pytest.mark.anyio
async def test_redis_publisher_publishes_event(monkeypatch) -> None:
    client = FakeRedisClient()

    class FakeRedis:
        @staticmethod
        def from_url(redis_url: str, decode_responses: bool):
            return client

    monkeypatch.setattr(bus_module, "Redis", FakeRedis)

    publisher = RedisPublisher("redis://redis:6379/0", "platform.events")
    await publisher.publish(make_event())

    assert client.published[0][0] == "platform.events"
    assert "Ride completed" in client.published[0][1]
    assert client.closed is True


@pytest.mark.anyio
async def test_consume_events_reads_messages_and_closes(monkeypatch) -> None:
    pubsub = FakePubSub()
    client = FakeRedisClient(pubsub)
    received = []

    class FakeRedis:
        @staticmethod
        def from_url(redis_url: str, decode_responses: bool):
            return client

    async def on_event(event: EventEnvelope) -> None:
        received.append(event)

    monkeypatch.setattr(bus_module, "Redis", FakeRedis)

    task = asyncio.create_task(
        consume_events("redis://redis:6379/0", "platform.events", on_event)
    )
    while not received:
        await asyncio.sleep(0.01)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task

    assert received[0].event_id == "event-1"
    assert pubsub.channel == "platform.events"
    assert pubsub.unsubscribed == "platform.events"
    assert pubsub.closed is True
    assert client.closed is True
