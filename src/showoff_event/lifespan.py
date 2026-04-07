from __future__ import annotations

from asyncio import CancelledError, Task, create_task
from contextlib import asynccontextmanager, suppress
from typing import Awaitable, Callable

from fastapi import FastAPI


def create_consumer_lifespan(
    ensure_schema: Callable[[], None],
    consumer: Callable[[], Awaitable[None]],
):
    @asynccontextmanager
    async def lifespan(_: FastAPI):
        ensure_schema()
        task: Task[None] = create_task(consumer())
        try:
            yield
        finally:
            task.cancel()
            with suppress(CancelledError):
                await task

    return lifespan
