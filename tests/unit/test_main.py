from __future__ import annotations

from showoff_saas import __main__
from showoff_saas.config import Settings


def test_main_starts_uvicorn(monkeypatch) -> None:
    settings = Settings(
        api_host="0.0.0.0",
        api_port=8000,
        db_path="/tmp/saas.db",
    )
    captured: dict[str, object] = {}

    monkeypatch.setattr(__main__, "get_settings", lambda: settings)

    def fake_run(app, host: str, port: int) -> None:
        captured["app"] = app
        captured["host"] = host
        captured["port"] = port

    monkeypatch.setattr(__main__.uvicorn, "run", fake_run)

    __main__.main()

    assert captured["host"] == "0.0.0.0"
    assert captured["port"] == 8000
    assert captured["app"].title == "Multi-tenant SaaS Backend"
