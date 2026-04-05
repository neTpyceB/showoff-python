from __future__ import annotations

import asyncio

import httpx
import pytest

from showoff_async.config import AggregatorSettings
from showoff_async.service import AggregatorService, UpstreamFailure


def make_settings() -> AggregatorSettings:
    return AggregatorSettings(
        profile_url="http://upstream.test/profile",
        activity_url="http://upstream.test/activity",
        status_url="http://upstream.test/status",
        timeout_seconds=0.01,
        retries=1,
        host="127.0.0.1",
        port=8000,
    )


@pytest.mark.unit
@pytest.mark.anyio
async def test_fetch_source_retries_http_status_error() -> None:
    calls = {"count": 0}

    async def handler(request: httpx.Request) -> httpx.Response:
        calls["count"] += 1
        if calls["count"] == 1:
            return httpx.Response(503, request=request)
        return httpx.Response(200, json={"ok": True}, request=request)

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    service = AggregatorService(make_settings(), client)

    assert await service.fetch_source(
        "profile",
        "http://upstream.test/profile",
        "ada",
    ) == {"ok": True}
    assert calls["count"] == 2
    await client.aclose()


@pytest.mark.unit
@pytest.mark.anyio
async def test_fetch_source_raises_timeout_after_retries() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timeout", request=request)

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    service = AggregatorService(make_settings(), client)

    with pytest.raises(UpstreamFailure) as error:
        await service.fetch_source("profile", "http://upstream.test/profile", "ada")

    assert error.value.status_code == 504
    assert error.value.message == "profile timed out"
    await client.aclose()


@pytest.mark.unit
@pytest.mark.anyio
async def test_aggregate_user_runs_sources_concurrently(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = AggregatorService(
        make_settings(),
        httpx.AsyncClient(
            transport=httpx.MockTransport(
                lambda request: httpx.Response(200),
            ),
        ),
    )
    state = {"running": 0, "max_running": 0}

    async def fake_fetch(source: str, base_url: str, user_id: str) -> dict:
        state["running"] += 1
        state["max_running"] = max(state["max_running"], state["running"])
        await asyncio.sleep(0)
        state["running"] -= 1
        if source == "profile":
            return {"user_id": user_id, "name": "Ada", "role": "engineer"}
        if source == "activity":
            return {"user_id": user_id, "commits": 9, "reviews": 3}
        return {"user_id": user_id, "availability": "focused"}

    monkeypatch.setattr(service, "fetch_source", fake_fetch)

    result = await service.aggregate_user("ada")

    assert result.user_id == "ada"
    assert state["max_running"] == 3
    await service.client.aclose()


@pytest.mark.unit
@pytest.mark.anyio
async def test_fetch_source_raises_on_final_status_error() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, request=request)

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    service = AggregatorService(make_settings(), client)

    with pytest.raises(UpstreamFailure) as error:
        await service.fetch_source("activity", "http://upstream.test/activity", "ada")

    assert error.value.status_code == 502
    assert error.value.message == "activity failed with status 500"
    await client.aclose()
