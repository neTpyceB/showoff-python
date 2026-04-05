from __future__ import annotations

from pathlib import Path

import pytest
from starlette.requests import Request
from starlette.types import Scope

from showoff_api.app import create_app, get_repository, get_settings
from showoff_api.config import Settings


def make_request(settings: Settings) -> Request:
    app = create_app(settings)
    scope: Scope = {"type": "http", "app": app}
    return Request(scope)


@pytest.mark.unit
def test_app_state_dependencies_return_settings_and_repository(tmp_path: Path) -> None:
    settings = Settings(tmp_path / "notes.db", "token")
    request = make_request(settings)

    assert get_settings(request) == settings
    assert get_repository(request).database_path == Path(tmp_path / "notes.db")
