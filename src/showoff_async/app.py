from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Annotated

import httpx
from fastapi import Depends, FastAPI, HTTPException, Request

from showoff_async import __version__
from showoff_async.config import AggregatorSettings
from showoff_async.models import AggregateResponse
from showoff_async.service import AggregatorService, UpstreamFailure


def get_settings(request: Request) -> AggregatorSettings:
    return request.app.state.settings


def get_service(request: Request) -> AggregatorService:
    return request.app.state.service


def create_app(
    settings: AggregatorSettings,
    client: httpx.AsyncClient | None = None,
) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        owned_client = client is None
        async_client = client or httpx.AsyncClient()
        app.state.settings = settings
        app.state.client = async_client
        app.state.service = AggregatorService(settings, async_client)
        try:
            yield
        finally:
            if owned_client:
                await async_client.aclose()

    app = FastAPI(
        title="Async Data Aggregator",
        version=__version__,
        summary="Concurrent aggregation of multiple upstream APIs.",
        lifespan=lifespan,
    )

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/aggregate/{user_id}", response_model=AggregateResponse)
    async def aggregate(
        user_id: str,
        service: Annotated[AggregatorService, Depends(get_service)],
    ) -> AggregateResponse:
        try:
            return await service.aggregate_user(user_id)
        except UpstreamFailure as error:
            raise HTTPException(
                status_code=error.status_code,
                detail=error.message,
            ) from error

    return app
