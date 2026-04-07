from __future__ import annotations

from showoff_event.models import EventEnvelope, EventType
from showoff_event.store import AuditStore, FeedStore, NotificationStore


def make_event(event_id: str, created_at: str) -> EventEnvelope:
    return EventEnvelope(
        event_id=event_id,
        type=EventType.ACTIVITY_CREATED,
        user_id="alice",
        title=f"Activity {event_id}",
        detail=f"detail-{event_id}",
        created_at=created_at,
    )


def test_feed_store_orders_entries_desc(tmp_path) -> None:
    store = FeedStore(str(tmp_path / "feed.db"))
    store.ensure_schema()
    store.add_event(make_event("event-1", "2026-04-06T16:00:00+00:00"))
    store.add_event(make_event("event-2", "2026-04-06T17:00:00+00:00"))

    entries = store.list_entries("alice")

    assert [entry.event_id for entry in entries] == ["event-2", "event-1"]


def test_notification_store_formats_message(tmp_path) -> None:
    store = NotificationStore(str(tmp_path / "notifications.db"))
    store.ensure_schema()
    store.add_event(make_event("event-1", "2026-04-06T16:00:00+00:00"))

    entries = store.list_entries("alice")

    assert entries[0].message == "Activity recorded: Activity event-1"


def test_audit_store_persists_event_log(tmp_path) -> None:
    store = AuditStore(str(tmp_path / "audit.db"))
    store.ensure_schema()
    store.add_event(make_event("event-1", "2026-04-06T16:00:00+00:00"))

    entries = store.list_entries()

    assert entries[0].event_id == "event-1"
    assert entries[0].detail == "detail-event-1"
