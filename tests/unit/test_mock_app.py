from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from showoff_async.mock_app import create_mock_app


@pytest.mark.unit
def test_mock_app_routes_return_expected_payloads() -> None:
    client = TestClient(create_mock_app())

    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/profile/ada").json() == {
        "user_id": "ada",
        "name": "Ada",
        "role": "engineer",
    }
    assert client.get("/activity/ada").json() == {
        "user_id": "ada",
        "commits": 9,
        "reviews": 3,
    }
    assert client.get("/status/ada").json() == {
        "user_id": "ada",
        "availability": "focused",
    }
