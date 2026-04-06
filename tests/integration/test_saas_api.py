from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from showoff_saas.app import create_app
from showoff_saas.config import Settings
from showoff_saas.repository import SaaSRepository
from showoff_saas.service import SaaSService


def make_client(tmp_path) -> TestClient:
    settings = Settings(
        api_host="0.0.0.0",
        api_port=8000,
        db_path=str(tmp_path / "saas.db"),
    )
    app = create_app(settings=settings, service=SaaSService(SaaSRepository(settings)))
    return TestClient(app)


@pytest.mark.integration
def test_multi_tenant_admin_flow(tmp_path) -> None:
    with make_client(tmp_path) as client:
        create = client.post(
            "/organizations",
            headers={"X-User-Id": "alice"},
            json={"name": "Acme"},
        )
        assert create.status_code == 201
        organization = create.json()

        member = client.put(
            f"/organizations/{organization['id']}/members",
            headers={"X-User-Id": "alice"},
            json={"user_id": "bob", "role": "member"},
        )
        billing = client.post(
            f"/organizations/{organization['id']}/billing/mock-checkout",
            headers={"X-User-Id": "alice"},
            json={"plan": "growth"},
        )
        audit_logs = client.get(
            f"/organizations/{organization['id']}/audit-logs",
            headers={"X-User-Id": "alice"},
        )

    assert member.status_code == 200
    assert billing.status_code == 200
    assert billing.json()["plan"] == "growth"
    assert [entry["action"] for entry in audit_logs.json()] == [
        "organization.created",
        "membership.upserted",
        "billing.mock_checkout",
    ]


@pytest.mark.integration
def test_member_can_list_but_not_admin_endpoints(tmp_path) -> None:
    with make_client(tmp_path) as client:
        create = client.post(
            "/organizations",
            headers={"X-User-Id": "alice"},
            json={"name": "Acme"},
        )
        organization_id = create.json()["id"]
        client.put(
            f"/organizations/{organization_id}/members",
            headers={"X-User-Id": "alice"},
            json={"user_id": "bob", "role": "member"},
        )

        bob_list = client.get("/organizations", headers={"X-User-Id": "bob"})
        bob_read = client.get(
            f"/organizations/{organization_id}",
            headers={"X-User-Id": "bob"},
        )
        bob_billing = client.get(
            f"/organizations/{organization_id}/billing",
            headers={"X-User-Id": "bob"},
        )

    assert bob_list.status_code == 200
    assert bob_list.json()[0]["name"] == "Acme"
    assert bob_read.status_code == 200
    assert bob_read.json()["role"] == "member"
    assert bob_billing.status_code == 403
