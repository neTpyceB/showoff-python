from __future__ import annotations

import pytest

from showoff_saas.config import Settings
from showoff_saas.models import BillingPlan, Role
from showoff_saas.repository import SaaSRepository
from showoff_saas.service import (
    Actor,
    OrganizationNotFoundError,
    PermissionDeniedError,
    SaaSService,
)


def make_service(tmp_path) -> SaaSService:
    settings = Settings(
        api_host="0.0.0.0",
        api_port=8000,
        db_path=str(tmp_path / "saas.db"),
    )
    service = SaaSService(SaaSRepository(settings))
    service.ensure_schema()
    return service


def test_create_organization_sets_admin_trial_and_audit(tmp_path) -> None:
    service = make_service(tmp_path)

    organization = service.create_organization("Acme", Actor("alice"))
    billing = service.get_billing(organization.id, Actor("alice"))
    audit_logs = service.list_audit_logs(organization.id, Actor("alice"))

    assert organization.name == "Acme"
    assert organization.role is Role.ADMIN
    assert billing.plan is BillingPlan.STARTER
    assert billing.status == "trial"
    assert [log.action for log in audit_logs] == ["organization.created"]


def test_list_organizations_is_scoped_by_membership(tmp_path) -> None:
    service = make_service(tmp_path)
    acme = service.create_organization("Acme", Actor("alice"))
    service.create_organization("Beta", Actor("bob"))
    service.upsert_membership(acme.id, Actor("alice"), "bob", Role.MEMBER)

    alice_orgs = service.list_organizations(Actor("alice"))
    bob_orgs = service.list_organizations(Actor("bob"))

    assert [org.name for org in alice_orgs] == ["Acme"]
    assert [org.name for org in bob_orgs] == ["Acme", "Beta"]


def test_member_cannot_manage_billing_or_audit(tmp_path) -> None:
    service = make_service(tmp_path)
    organization = service.create_organization("Acme", Actor("alice"))
    service.upsert_membership(organization.id, Actor("alice"), "bob", Role.MEMBER)

    with pytest.raises(PermissionDeniedError):
        service.get_billing(organization.id, Actor("bob"))

    with pytest.raises(PermissionDeniedError):
        service.list_audit_logs(organization.id, Actor("bob"))


def test_non_member_gets_forbidden_on_admin_endpoint(tmp_path) -> None:
    service = make_service(tmp_path)
    organization = service.create_organization("Acme", Actor("alice"))

    with pytest.raises(PermissionDeniedError):
        service.get_billing(organization.id, Actor("carol"))


def test_admin_can_update_membership_and_checkout(tmp_path) -> None:
    service = make_service(tmp_path)
    organization = service.create_organization("Acme", Actor("alice"))

    membership = service.upsert_membership(
        organization.id,
        Actor("alice"),
        "bob",
        Role.ADMIN,
    )
    billing = service.mock_checkout(
        organization.id,
        Actor("alice"),
        BillingPlan.GROWTH,
    )
    audit_logs = service.list_audit_logs(organization.id, Actor("alice"))

    assert membership.role is Role.ADMIN
    assert billing.plan is BillingPlan.GROWTH
    assert billing.status == "active"
    assert [log.action for log in audit_logs] == [
        "organization.created",
        "membership.upserted",
        "billing.mock_checkout",
    ]


def test_missing_organization_raises_not_found(tmp_path) -> None:
    service = make_service(tmp_path)

    with pytest.raises(OrganizationNotFoundError):
        service.get_organization("missing", Actor("alice"))

    with pytest.raises(OrganizationNotFoundError):
        service.get_billing("missing", Actor("alice"))
