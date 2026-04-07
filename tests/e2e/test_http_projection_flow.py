from __future__ import annotations

import asyncio
import socket
from threading import Thread
from time import monotonic, sleep
from urllib import request

import httpx
import pytest
import uvicorn

from showoff_event.audit_app import create_audit_app
from showoff_event.config import Settings
from showoff_event.feed_app import create_feed_app
from showoff_event.notification_app import create_notification_app
from showoff_event.platform_app import create_platform_app
from showoff_event.store import AuditStore, FeedStore, NotificationStore


def get_open_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def wait_for_server(url: str) -> None:
    deadline = monotonic() + 5
    while monotonic() < deadline:
        try:
            with request.urlopen(f"{url}/health", timeout=1):
                return
        except OSError:
            sleep(0.05)
    raise AssertionError("Server did not start")


async def idle_consumer() -> None:
    await asyncio.Future()


class ProjectingPublisher:
    def __init__(
        self,
        feed_store: FeedStore,
        notification_store: NotificationStore,
        audit_store: AuditStore,
    ) -> None:
        self._feed_store = feed_store
        self._notification_store = notification_store
        self._audit_store = audit_store

    async def publish(self, event) -> None:
        self._feed_store.add_event(event)
        self._notification_store.add_event(event)
        self._audit_store.add_event(event)


def make_settings(tmp_path, ports: tuple[int, int, int, int]) -> Settings:
    return Settings(
        platform_host="127.0.0.1",
        platform_port=ports[0],
        feed_host="127.0.0.1",
        feed_port=ports[1],
        feed_db_path=str(tmp_path / "feed.db"),
        notification_host="127.0.0.1",
        notification_port=ports[2],
        notification_db_path=str(tmp_path / "notifications.db"),
        audit_host="127.0.0.1",
        audit_port=ports[3],
        audit_db_path=str(tmp_path / "audit.db"),
        redis_url="redis://redis:6379/0",
        event_channel="platform.events",
    )


@pytest.mark.e2e
def test_http_services_expose_projected_reads(tmp_path) -> None:
    ports = tuple(get_open_port() for _ in range(4))
    settings = make_settings(tmp_path, ports)
    feed_store = FeedStore(settings.feed_db_path)
    notification_store = NotificationStore(settings.notification_db_path)
    audit_store = AuditStore(settings.audit_db_path)

    platform_app = create_platform_app(
        settings,
        publisher=ProjectingPublisher(feed_store, notification_store, audit_store),
    )
    feed_app = create_feed_app(settings, store=feed_store, consumer=idle_consumer)
    notification_app = create_notification_app(
        settings,
        store=notification_store,
        consumer=idle_consumer,
    )
    audit_app = create_audit_app(settings, store=audit_store, consumer=idle_consumer)

    servers = [
        uvicorn.Server(
            uvicorn.Config(
                platform_app,
                host=settings.platform_host,
                port=settings.platform_port,
                log_level="error",
            )
        ),
        uvicorn.Server(
            uvicorn.Config(
                feed_app,
                host=settings.feed_host,
                port=settings.feed_port,
                log_level="error",
            )
        ),
        uvicorn.Server(
            uvicorn.Config(
                notification_app,
                host=settings.notification_host,
                port=settings.notification_port,
                log_level="error",
            )
        ),
        uvicorn.Server(
            uvicorn.Config(
                audit_app,
                host=settings.audit_host,
                port=settings.audit_port,
                log_level="error",
            )
        ),
    ]
    threads = [Thread(target=server.run, daemon=True) for server in servers]
    for thread in threads:
        thread.start()
    wait_for_server(f"http://127.0.0.1:{settings.platform_port}")
    wait_for_server(f"http://127.0.0.1:{settings.feed_port}")
    wait_for_server(f"http://127.0.0.1:{settings.notification_port}")
    wait_for_server(f"http://127.0.0.1:{settings.audit_port}")
    try:
        with httpx.Client(timeout=5) as client:
            event = client.post(
                f"http://127.0.0.1:{settings.platform_port}/events/activities",
                json={
                    "user_id": "alice",
                    "title": "Movie watched",
                    "detail": "Finished a full season",
                },
            ).json()
            feed = client.get(
                f"http://127.0.0.1:{settings.feed_port}/users/alice/feed"
            ).json()
            notifications = client.get(
                f"http://127.0.0.1:{settings.notification_port}/users/alice/notifications"
            ).json()
            audit = client.get(f"http://127.0.0.1:{settings.audit_port}/events").json()
    finally:
        for server in servers:
            server.should_exit = True
        for thread in threads:
            thread.join(timeout=5)

    assert event["title"] == "Movie watched"
    assert feed[0]["detail"] == "Finished a full season"
    assert notifications[0]["message"] == "Activity recorded: Movie watched"
    assert audit[0]["event_id"] == event["event_id"]
