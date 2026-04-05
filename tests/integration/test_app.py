from __future__ import annotations

import asyncio

import httpx
import pytest
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from showoff_async.app import create_app
from showoff_async.config import AggregatorSettings


def create_mock_upstream() -> FastAPI:
    app = FastAPI()
    failures = {"profile": 0}

    @app.get("/profile/{user_id}", response_model=None)
    async def profile(user_id: str):
        if user_id == "retry" and failures["profile"] == 0:
            failures["profile"] += 1
            return JSONResponse(status_code=503, content={"detail": "unavailable"})
        if user_id == "timeout":
            await asyncio.sleep(0.05)
        return {"user_id": user_id, "name": user_id.capitalize(), "role": "engineer"}

    @app.get("/activity/{user_id}")
    async def activity(user_id: str) -> dict[str, int | str]:
        if user_id == "timeout":
            await asyncio.sleep(0.05)
        return {
            "user_id": user_id,
            "commits": len(user_id) * 3,
            "reviews": len(user_id),
        }

    @app.get("/status/{user_id}")
    async def status(user_id: str) -> dict[str, str]:
        if user_id == "timeout":
            await asyncio.sleep(0.05)
        return {"user_id": user_id, "availability": "focused"}

    return app


def create_test_client(
    transport: httpx.AsyncBaseTransport | None = None,
) -> TestClient:
    upstream = create_mock_upstream()
    settings = AggregatorSettings(
        profile_url="http://upstream.test/profile",
        activity_url="http://upstream.test/activity",
        status_url="http://upstream.test/status",
        timeout_seconds=0.01,
        retries=1,
        host="127.0.0.1",
        port=8000,
    )
    client = httpx.AsyncClient(
        transport=transport or httpx.ASGITransport(app=upstream),
        base_url="http://upstream.test",
    )
    return TestClient(create_app(settings, client))


@pytest.mark.integration
def test_aggregate_success() -> None:
    with create_test_client() as client:
        response = client.get("/aggregate/ada")

        assert response.status_code == 200
        assert response.json() == {
            "user_id": "ada",
            "profile": {"user_id": "ada", "name": "Ada", "role": "engineer"},
            "activity": {"user_id": "ada", "commits": 9, "reviews": 3},
            "status": {"user_id": "ada", "availability": "focused"},
        }


@pytest.mark.integration
def test_aggregate_retries_and_succeeds() -> None:
    with create_test_client() as client:
        response = client.get("/aggregate/retry")

        assert response.status_code == 200
        assert response.json()["profile"]["name"] == "Retry"


@pytest.mark.integration
def test_aggregate_times_out() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/profile/timeout":
            raise httpx.ReadTimeout("timeout", request=request)
        if request.url.path == "/activity/timeout":
            return httpx.Response(
                200,
                json={"user_id": "timeout", "commits": 21, "reviews": 7},
                request=request,
            )
        return httpx.Response(
            200,
            json={"user_id": "timeout", "availability": "focused"},
            request=request,
        )

    with create_test_client(httpx.MockTransport(handler)) as client:
        response = client.get("/aggregate/timeout")

        assert response.status_code == 504
        assert response.json() == {"detail": "profile timed out"}
