from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class Role(StrEnum):
    ADMIN = "admin"
    MEMBER = "member"


class BillingPlan(StrEnum):
    STARTER = "starter"
    GROWTH = "growth"
    ENTERPRISE = "enterprise"


class BillingStatus(StrEnum):
    TRIAL = "trial"
    ACTIVE = "active"


class HealthResponse(BaseModel):
    status: str


class CreateOrganizationRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)


class OrganizationResponse(BaseModel):
    id: str
    name: str
    role: Role
    billing_plan: BillingPlan
    billing_status: BillingStatus
    created_at: str


class MembershipRequest(BaseModel):
    user_id: str = Field(min_length=1, max_length=64)
    role: Role


class MembershipResponse(BaseModel):
    organization_id: str
    user_id: str
    role: Role
    created_at: str


class BillingResponse(BaseModel):
    organization_id: str
    plan: BillingPlan
    status: BillingStatus
    updated_at: str


class MockCheckoutRequest(BaseModel):
    plan: BillingPlan


class AuditLogResponse(BaseModel):
    id: str
    organization_id: str
    actor_user_id: str
    action: str
    target_type: str
    target_id: str
    created_at: str
