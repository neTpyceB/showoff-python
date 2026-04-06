from __future__ import annotations

from showoff_perf import __main__
from showoff_perf.config import Settings


def test_main_starts_uvicorn(monkeypatch) -> None:
    settings = Settings(
        api_host="0.0.0.0",
        api_port=8000,
        redis_url="redis://cache:6379/0",
        cache_ttl_seconds=60,
        default_workers=2,
        default_engine="auto",
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
    assert captured["app"].title == "High-performance Service"
