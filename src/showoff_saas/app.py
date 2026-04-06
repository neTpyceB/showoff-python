from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, Header, HTTPException

from .config import Settings, get_settings
from .models import (
    AuditLogResponse,
    BillingResponse,
    CreateOrganizationRequest,
    HealthResponse,
    MembershipRequest,
    MembershipResponse,
    MockCheckoutRequest,
    OrganizationResponse,
)
from .repository import SaaSRepository
from .service import (
    Actor,
    OrganizationNotFoundError,
    PermissionDeniedError,
    SaaSService,
)


def create_app(
    settings: Settings | None = None,
    service: SaaSService | None = None,
) -> FastAPI:
    resolved_settings = settings or get_settings()
    resolved_service = service or SaaSService(SaaSRepository(resolved_settings))

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        resolved_service.ensure_schema()
        yield

    app = FastAPI(
        title="Multi-tenant SaaS Backend",
        version="0.7.0",
        lifespan=lifespan,
    )

    @app.get("/health", response_model=HealthResponse)
    def read_health() -> HealthResponse:
        return HealthResponse(status="ok")

    @app.post("/organizations", response_model=OrganizationResponse, status_code=201)
    def create_organization(
        payload: CreateOrganizationRequest,
        actor: Annotated[str, Header(alias="X-User-Id")],
    ) -> OrganizationResponse:
        return resolved_service.create_organization(payload.name, Actor(actor))

    @app.get("/organizations", response_model=list[OrganizationResponse])
    def list_organizations(
        actor: Annotated[str, Header(alias="X-User-Id")],
    ) -> list[OrganizationResponse]:
        return resolved_service.list_organizations(Actor(actor))

    @app.get("/organizations/{organization_id}", response_model=OrganizationResponse)
    def get_organization(
        organization_id: str,
        actor: Annotated[str, Header(alias="X-User-Id")],
    ) -> OrganizationResponse:
        try:
            return resolved_service.get_organization(organization_id, Actor(actor))
        except OrganizationNotFoundError as error:
            raise HTTPException(
                status_code=404,
                detail="Organization not found",
            ) from error

    @app.put(
        "/organizations/{organization_id}/members",
        response_model=MembershipResponse,
    )
    def put_membership(
        organization_id: str,
        payload: MembershipRequest,
        actor: Annotated[str, Header(alias="X-User-Id")],
    ) -> MembershipResponse:
        try:
            return resolved_service.upsert_membership(
                organization_id=organization_id,
                actor=Actor(actor),
                user_id=payload.user_id,
                role=payload.role,
            )
        except OrganizationNotFoundError as error:
            raise HTTPException(
                status_code=404,
                detail="Organization not found",
            ) from error
        except PermissionDeniedError as error:
            raise HTTPException(
                status_code=403,
                detail="Admin role required",
            ) from error

    @app.get(
        "/organizations/{organization_id}/billing",
        response_model=BillingResponse,
    )
    def get_billing(
        organization_id: str,
        actor: Annotated[str, Header(alias="X-User-Id")],
    ) -> BillingResponse:
        try:
            return resolved_service.get_billing(organization_id, Actor(actor))
        except OrganizationNotFoundError as error:
            raise HTTPException(
                status_code=404,
                detail="Organization not found",
            ) from error
        except PermissionDeniedError as error:
            raise HTTPException(
                status_code=403,
                detail="Admin role required",
            ) from error

    @app.post(
        "/organizations/{organization_id}/billing/mock-checkout",
        response_model=BillingResponse,
    )
    def post_mock_checkout(
        organization_id: str,
        payload: MockCheckoutRequest,
        actor: Annotated[str, Header(alias="X-User-Id")],
    ) -> BillingResponse:
        try:
            return resolved_service.mock_checkout(
                organization_id=organization_id,
                actor=Actor(actor),
                plan=payload.plan,
            )
        except OrganizationNotFoundError as error:
            raise HTTPException(
                status_code=404,
                detail="Organization not found",
            ) from error
        except PermissionDeniedError as error:
            raise HTTPException(
                status_code=403,
                detail="Admin role required",
            ) from error

    @app.get(
        "/organizations/{organization_id}/audit-logs",
        response_model=list[AuditLogResponse],
    )
    def get_audit_logs(
        organization_id: str,
        actor: Annotated[str, Header(alias="X-User-Id")],
    ) -> list[AuditLogResponse]:
        try:
            return resolved_service.list_audit_logs(organization_id, Actor(actor))
        except OrganizationNotFoundError as error:
            raise HTTPException(
                status_code=404,
                detail="Organization not found",
            ) from error
        except PermissionDeniedError as error:
            raise HTTPException(
                status_code=403,
                detail="Admin role required",
            ) from error

    return app


app = create_app()
