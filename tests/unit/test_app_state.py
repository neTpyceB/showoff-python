from __future__ import annotations

import httpx
import pytest
from fastapi.testclient import TestClient
from starlette.requests import Request
from starlette.types import Scope

from showoff_async.app import create_app, get_service, get_settings
from showoff_async.config import AggregatorSettings
from showoff_async.mock_app import create_mock_app
from showoff_async.service import AggregatorService


def make_request(settings: AggregatorSettings) -> Request:
    client = httpx.AsyncClient(
        transport=httpx.ASGITransport(app=create_mock_app()),
        base_url="http://upstream.test",
    )
    app = create_app(settings, client)
    app.state.settings = settings
    app.state.service = AggregatorService(settings, client)
    scope: Scope = {"type": "http", "app": app}
    return Request(scope)


@pytest.mark.unit
def test_app_state_dependencies_return_settings_and_service() -> None:
    settings = AggregatorSettings(
        profile_url="http://upstream.test/profile",
        activity_url="http://upstream.test/activity",
        status_url="http://upstream.test/status",
        timeout_seconds=0.1,
        retries=1,
        host="127.0.0.1",
        port=8000,
    )
    request = make_request(settings)

    assert get_settings(request) == settings
    assert get_service(request).settings == settings


@pytest.mark.unit
def test_app_closes_owned_client_on_shutdown() -> None:
    settings = AggregatorSettings(
        profile_url="http://upstream.test/profile",
        activity_url="http://upstream.test/activity",
        status_url="http://upstream.test/status",
        timeout_seconds=0.1,
        retries=1,
        host="127.0.0.1",
        port=8000,
    )

    with TestClient(create_app(settings)) as client:
        assert client.get("/health").json() == {"status": "ok"}
