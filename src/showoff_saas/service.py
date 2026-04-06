from __future__ import annotations

from dataclasses import asdict, dataclass

from .models import (
    AuditLogResponse,
    BillingPlan,
    BillingResponse,
    MembershipResponse,
    OrganizationResponse,
    Role,
)
from .repository import SaaSRepository


class OrganizationNotFoundError(KeyError):
    """Organization was not found for the actor."""


class PermissionDeniedError(PermissionError):
    """Actor does not have permission for the operation."""


@dataclass(frozen=True, slots=True)
class Actor:
    user_id: str


class SaaSService:
    def __init__(self, repository: SaaSRepository) -> None:
        self._repository = repository

    def ensure_schema(self) -> None:
        self._repository.ensure_schema()

    def create_organization(self, name: str, actor: Actor) -> OrganizationResponse:
        return OrganizationResponse.model_validate(
            self._repository.create_organization(name=name, actor_user_id=actor.user_id)
        )

    def list_organizations(self, actor: Actor) -> list[OrganizationResponse]:
        return [
            OrganizationResponse.model_validate(row)
            for row in self._repository.list_organizations(actor.user_id)
        ]

    def get_organization(
        self,
        organization_id: str,
        actor: Actor,
    ) -> OrganizationResponse:
        organization = self._repository.get_organization(organization_id, actor.user_id)
        if organization is None:
            raise OrganizationNotFoundError(organization_id)
        return OrganizationResponse.model_validate(organization)

    def upsert_membership(
        self,
        organization_id: str,
        actor: Actor,
        user_id: str,
        role: Role,
    ) -> MembershipResponse:
        self._require_admin(organization_id, actor)
        membership = self._repository.upsert_membership(
            organization_id=organization_id,
            actor_user_id=actor.user_id,
            user_id=user_id,
            role=role,
        )
        return MembershipResponse.model_validate(asdict(membership))

    def get_billing(self, organization_id: str, actor: Actor) -> BillingResponse:
        self._require_admin(organization_id, actor)
        return BillingResponse.model_validate(
            self._repository.get_billing(organization_id)
        )

    def mock_checkout(
        self,
        organization_id: str,
        actor: Actor,
        plan: BillingPlan,
    ) -> BillingResponse:
        self._require_admin(organization_id, actor)
        return BillingResponse.model_validate(
            self._repository.mock_checkout(
                organization_id=organization_id,
                actor_user_id=actor.user_id,
                plan=plan,
            )
        )

    def list_audit_logs(
        self,
        organization_id: str,
        actor: Actor,
    ) -> list[AuditLogResponse]:
        self._require_admin(organization_id, actor)
        return [
            AuditLogResponse.model_validate(row)
            for row in self._repository.list_audit_logs(organization_id)
        ]

    def _require_admin(self, organization_id: str, actor: Actor) -> None:
        role = self._repository.get_role(organization_id, actor.user_id)
        if role is None:
            if self._repository.organization_exists(organization_id):
                raise PermissionDeniedError(organization_id)
            raise OrganizationNotFoundError(organization_id)
        if role is not Role.ADMIN:
            raise PermissionDeniedError(organization_id)
