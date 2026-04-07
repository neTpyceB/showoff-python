from __future__ import annotations

import asyncio
from typing import Protocol

from redis.asyncio import Redis

from .models import EventEnvelope


class EventPublisher(Protocol):
    async def publish(self, event: EventEnvelope) -> None: ...


class RedisPublisher:
    def __init__(self, redis_url: str, channel: str) -> None:
        self._redis_url = redis_url
        self._channel = channel

    async def publish(self, event: EventEnvelope) -> None:
        client = Redis.from_url(self._redis_url, decode_responses=True)
        try:
            await client.publish(self._channel, event.model_dump_json())
        finally:
            await client.aclose()


async def consume_events(
    redis_url: str,
    channel: str,
    on_event,
) -> None:
    client = Redis.from_url(redis_url, decode_responses=True)
    pubsub = client.pubsub()
    await pubsub.subscribe(channel)
    try:
        while True:
            message = await pubsub.get_message(
                ignore_subscribe_messages=True,
                timeout=1.0,
            )
            if message is not None:
                await on_event(EventEnvelope.model_validate_json(message["data"]))
            await asyncio.sleep(0.05)
    finally:
        await pubsub.unsubscribe(channel)
        await pubsub.aclose()
        await client.aclose()
