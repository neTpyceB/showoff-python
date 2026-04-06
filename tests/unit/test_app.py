from __future__ import annotations

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


def test_health_endpoint(tmp_path) -> None:
    with make_client(tmp_path) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_member_write_returns_forbidden(tmp_path) -> None:
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
        response = client.get(
            f"/organizations/{organization_id}/billing",
            headers={"X-User-Id": "bob"},
        )

    assert response.status_code == 403
    assert response.json() == {"detail": "Admin role required"}


def test_membership_write_requires_admin_or_existing_org(tmp_path) -> None:
    with make_client(tmp_path) as client:
        create = client.post(
            "/organizations",
            headers={"X-User-Id": "alice"},
            json={"name": "Acme"},
        )
        organization_id = create.json()["id"]

        forbidden = client.put(
            f"/organizations/{organization_id}/members",
            headers={"X-User-Id": "carol"},
            json={"user_id": "bob", "role": "member"},
        )
        missing = client.put(
            "/organizations/missing/members",
            headers={"X-User-Id": "alice"},
            json={"user_id": "bob", "role": "member"},
        )

    assert forbidden.status_code == 403
    assert missing.status_code == 404


def test_checkout_and_audit_errors_are_mapped(tmp_path) -> None:
    with make_client(tmp_path) as client:
        create = client.post(
            "/organizations",
            headers={"X-User-Id": "alice"},
            json={"name": "Acme"},
        )
        organization_id = create.json()["id"]

        forbidden_checkout = client.post(
            f"/organizations/{organization_id}/billing/mock-checkout",
            headers={"X-User-Id": "carol"},
            json={"plan": "growth"},
        )
        missing_checkout = client.post(
            "/organizations/missing/billing/mock-checkout",
            headers={"X-User-Id": "alice"},
            json={"plan": "growth"},
        )
        forbidden_audit = client.get(
            f"/organizations/{organization_id}/audit-logs",
            headers={"X-User-Id": "carol"},
        )
        missing_audit = client.get(
            "/organizations/missing/audit-logs",
            headers={"X-User-Id": "alice"},
        )
        missing_billing = client.get(
            "/organizations/missing/billing",
            headers={"X-User-Id": "alice"},
        )

    assert forbidden_checkout.status_code == 403
    assert missing_checkout.status_code == 404
    assert forbidden_audit.status_code == 403
    assert missing_audit.status_code == 404
    assert missing_billing.status_code == 404


def test_missing_organization_returns_not_found(tmp_path) -> None:
    with make_client(tmp_path) as client:
        response = client.get(
            "/organizations/missing",
            headers={"X-User-Id": "alice"},
        )

    assert response.status_code == 404
    assert response.json() == {"detail": "Organization not found"}
