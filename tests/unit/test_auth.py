from __future__ import annotations

from pathlib import Path

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from starlette.requests import Request
from starlette.types import Scope

from showoff_api.auth import get_settings, require_bearer_token
from showoff_api.config import Settings


def make_request(settings: Settings) -> Request:
    state = type("State", (), {"settings": settings})()
    app = type("App", (), {"state": state})()
    scope: Scope = {"type": "http", "app": app}
    return Request(scope)


@pytest.mark.unit
def test_get_settings_reads_from_request_state(tmp_path: Path) -> None:
    settings = Settings(tmp_path / "notes.db", "token")
    request = make_request(settings)

    assert get_settings(request) == settings


@pytest.mark.unit
def test_require_bearer_token_accepts_matching_token(tmp_path: Path) -> None:
    settings = Settings(tmp_path / "notes.db", "token")
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="token")

    assert require_bearer_token(credentials, settings) is None


@pytest.mark.unit
def test_require_bearer_token_rejects_missing_or_wrong_token(tmp_path: Path) -> None:
    settings = Settings(tmp_path / "notes.db", "token")

    with pytest.raises(HTTPException) as missing:
        require_bearer_token(None, settings)
    assert missing.value.status_code == 401

    with pytest.raises(HTTPException) as wrong:
        require_bearer_token(
            HTTPAuthorizationCredentials(scheme="Bearer", credentials="wrong"),
            settings,
        )
    assert wrong.value.status_code == 401
