from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from showoff_saas.app import create_app
from showoff_saas.config import Settings
from showoff_saas.repository import SaaSRepository
from showoff_saas.service import SaaSService


@pytest.mark.e2e
def test_cross_tenant_isolation_flow(tmp_path) -> None:
    settings = Settings(
        api_host="0.0.0.0",
        api_port=8000,
        db_path=str(tmp_path / "saas.db"),
    )
    app = create_app(settings=settings, service=SaaSService(SaaSRepository(settings)))

    with TestClient(app) as client:
        acme = client.post(
            "/organizations",
            headers={"X-User-Id": "alice"},
            json={"name": "Acme"},
        ).json()
        beta = client.post(
            "/organizations",
            headers={"X-User-Id": "carol"},
            json={"name": "Beta"},
        ).json()
        client.put(
            f"/organizations/{acme['id']}/members",
            headers={"X-User-Id": "alice"},
            json={"user_id": "bob", "role": "member"},
        )

        bob_orgs = client.get("/organizations", headers={"X-User-Id": "bob"})
        bob_beta = client.get(
            f"/organizations/{beta['id']}",
            headers={"X-User-Id": "bob"},
        )

    assert bob_orgs.status_code == 200
    assert [org["name"] for org in bob_orgs.json()] == ["Acme"]
    assert bob_beta.status_code == 404
