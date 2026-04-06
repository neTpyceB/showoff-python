from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

import pytest
from fastapi.testclient import TestClient

from showoff_micro.auth_client import AuthClient
from showoff_micro.config import Settings
from showoff_micro.data_app import create_data_app
from showoff_micro.store import JobStore


class AuthHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        if self.path != "/validate":
            self.send_response(404)
            self.end_headers()
            return
        if self.headers.get("Authorization") != "Bearer alice":
            self.send_response(401)
            self.end_headers()
            return
        payload = json.dumps({"user_id": "alice"}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format, *args) -> None:  # noqa: A003
        return None


@pytest.mark.integration
def test_data_service_calls_auth_service(tmp_path) -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 0), AuthHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        settings = Settings(
            auth_host="0.0.0.0",
            auth_port=8000,
            data_host="0.0.0.0",
            data_port=8000,
            data_db_path=str(tmp_path / "micro.db"),
            auth_service_url=f"http://127.0.0.1:{server.server_address[1]}",
            data_service_url="http://data:8000",
            worker_service_name="worker",
            worker_poll_seconds=1,
        )
        app = create_data_app(
            settings=settings,
            store=JobStore(settings.data_db_path),
            auth_client=AuthClient(settings.auth_service_url),
        )
        with TestClient(app) as client:
            response = client.post(
                "/jobs",
                headers={"Authorization": "Bearer alice"},
                json={"payload": "hello world"},
            )
    finally:
        server.shutdown()
        server.server_close()

    assert response.status_code == 201
    assert response.json()["owner_user_id"] == "alice"


@pytest.mark.integration
def test_auth_client_rejects_bad_token(tmp_path) -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 0), AuthHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        client = AuthClient(f"http://127.0.0.1:{server.server_address[1]}")
        with pytest.raises(PermissionError):
            client.validate("Bearer bob")
    finally:
        server.shutdown()
        server.server_close()
