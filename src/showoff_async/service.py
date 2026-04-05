from __future__ import annotations

import asyncio
from dataclasses import dataclass

import httpx

from showoff_async.config import AggregatorSettings
from showoff_async.models import AggregateResponse


@dataclass(frozen=True)
class UpstreamFailure(Exception):
    status_code: int
    message: str


class AggregatorService:
    def __init__(self, settings: AggregatorSettings, client: httpx.AsyncClient) -> None:
        self.settings = settings
        self.client = client

    async def aggregate_user(self, user_id: str) -> AggregateResponse:
        results: dict[str, dict] = {}
        try:
            async with asyncio.TaskGroup() as task_group:
                tasks = {
                    "profile": task_group.create_task(
                        self.fetch_source(
                            "profile",
                            self.settings.profile_url,
                            user_id,
                        ),
                    ),
                    "activity": task_group.create_task(
                        self.fetch_source(
                            "activity",
                            self.settings.activity_url,
                            user_id,
                        ),
                    ),
                    "status": task_group.create_task(
                        self.fetch_source("status", self.settings.status_url, user_id),
                    ),
                }
        except* UpstreamFailure as errors:
            raise errors.exceptions[0] from errors.exceptions[0]
        for name, task in tasks.items():
            results[name] = task.result()
        return AggregateResponse(user_id=user_id, **results)

    async def fetch_source(self, source: str, base_url: str, user_id: str) -> dict:
        attempts = self.settings.retries + 1
        attempt = 0
        while True:
            attempt += 1
            try:
                response = await self.client.get(
                    f"{base_url}/{user_id}",
                    timeout=self.settings.timeout_seconds,
                )
                response.raise_for_status()
                return response.json()
            except httpx.TimeoutException as error:
                if attempt == attempts:
                    raise UpstreamFailure(504, f"{source} timed out") from error
            except httpx.HTTPStatusError as error:
                if attempt == attempts:
                    raise UpstreamFailure(
                        502,
                        f"{source} failed with status {error.response.status_code}",
                    ) from error
