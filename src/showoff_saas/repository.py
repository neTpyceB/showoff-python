from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from .config import Settings
from .models import BillingPlan, BillingStatus, Role

CREATE_ORGANIZATIONS_TABLE = """
CREATE TABLE IF NOT EXISTS organizations (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TEXT NOT NULL
)
"""
CREATE_MEMBERSHIPS_TABLE = """
CREATE TABLE IF NOT EXISTS memberships (
    organization_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    role TEXT NOT NULL,
    created_at TEXT NOT NULL,
    PRIMARY KEY (organization_id, user_id)
)
"""
CREATE_BILLING_TABLE = """
CREATE TABLE IF NOT EXISTS billing_accounts (
    organization_id TEXT PRIMARY KEY,
    plan TEXT NOT NULL,
    status TEXT NOT NULL,
    updated_at TEXT NOT NULL
)
"""
CREATE_AUDIT_TABLE = """
CREATE TABLE IF NOT EXISTS audit_logs (
    id TEXT PRIMARY KEY,
    organization_id TEXT NOT NULL,
    actor_user_id TEXT NOT NULL,
    action TEXT NOT NULL,
    target_type TEXT NOT NULL,
    target_id TEXT NOT NULL,
    created_at TEXT NOT NULL
)
"""
SELECT_ORGANIZATIONS = """
SELECT
    organizations.id,
    organizations.name,
    memberships.role,
    billing_accounts.plan AS billing_plan,
    billing_accounts.status AS billing_status,
    organizations.created_at
FROM organizations
JOIN memberships
  ON memberships.organization_id = organizations.id
JOIN billing_accounts
  ON billing_accounts.organization_id = organizations.id
WHERE memberships.user_id = ?
ORDER BY organizations.created_at
"""
SELECT_ORGANIZATION = """
SELECT
    organizations.id,
    organizations.name,
    memberships.role,
    billing_accounts.plan AS billing_plan,
    billing_accounts.status AS billing_status,
    organizations.created_at
FROM organizations
JOIN memberships
  ON memberships.organization_id = organizations.id
JOIN billing_accounts
  ON billing_accounts.organization_id = organizations.id
WHERE organizations.id = ? AND memberships.user_id = ?
"""
SELECT_ROLE = """
SELECT role
FROM memberships
WHERE organization_id = ? AND user_id = ?
"""
SELECT_BILLING = """
SELECT
    organization_id,
    plan,
    status,
    updated_at
FROM billing_accounts
WHERE organization_id = ?
"""
SELECT_AUDIT_LOGS = """
SELECT
    id,
    organization_id,
    actor_user_id,
    action,
    target_type,
    target_id,
    created_at
FROM audit_logs
WHERE organization_id = ?
ORDER BY created_at
"""
CHECK_ORGANIZATION = "SELECT 1 FROM organizations WHERE id = ?"


@dataclass(frozen=True, slots=True)
class MembershipRecord:
    organization_id: str
    user_id: str
    role: str
    created_at: str


class SaaSRepository:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def ensure_schema(self) -> None:
        Path(self._settings.db_path).parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute(CREATE_ORGANIZATIONS_TABLE)
            connection.execute(CREATE_MEMBERSHIPS_TABLE)
            connection.execute(CREATE_BILLING_TABLE)
            connection.execute(CREATE_AUDIT_TABLE)

    def create_organization(self, name: str, actor_user_id: str) -> dict[str, str]:
        organization_id = str(uuid4())
        created_at = _now()
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO organizations (id, name, created_at) VALUES (?, ?, ?)",
                (organization_id, name, created_at),
            )
            connection.execute(
                """
                INSERT INTO memberships (organization_id, user_id, role, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (organization_id, actor_user_id, Role.ADMIN.value, created_at),
            )
            connection.execute(
                """
                INSERT INTO billing_accounts (organization_id, plan, status, updated_at)
                VALUES (?, ?, ?, ?)
                """,
                (
                    organization_id,
                    BillingPlan.STARTER.value,
                    BillingStatus.TRIAL.value,
                    created_at,
                ),
            )
            self._insert_audit_log(
                connection=connection,
                organization_id=organization_id,
                actor_user_id=actor_user_id,
                action="organization.created",
                target_type="organization",
                target_id=organization_id,
            )
        return self.get_organization(organization_id, actor_user_id)

    def list_organizations(self, actor_user_id: str) -> list[dict[str, str]]:
        with self._connect() as connection:
            rows = connection.execute(SELECT_ORGANIZATIONS, (actor_user_id,)).fetchall()
        return [dict(row) for row in rows]

    def get_organization(
        self,
        organization_id: str,
        actor_user_id: str,
    ) -> dict[str, str] | None:
        with self._connect() as connection:
            row = connection.execute(
                SELECT_ORGANIZATION,
                (organization_id, actor_user_id),
            ).fetchone()
        return None if row is None else dict(row)

    def get_role(self, organization_id: str, actor_user_id: str) -> Role | None:
        with self._connect() as connection:
            row = connection.execute(
                SELECT_ROLE,
                (organization_id, actor_user_id),
            ).fetchone()
        return None if row is None else Role(row["role"])

    def organization_exists(self, organization_id: str) -> bool:
        with self._connect() as connection:
            row = connection.execute(CHECK_ORGANIZATION, (organization_id,)).fetchone()
        return row is not None

    def upsert_membership(
        self,
        organization_id: str,
        actor_user_id: str,
        user_id: str,
        role: Role,
    ) -> MembershipRecord:
        created_at = _now()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO memberships (organization_id, user_id, role, created_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(organization_id, user_id)
                DO UPDATE SET role = excluded.role
                """,
                (organization_id, user_id, role.value, created_at),
            )
            self._insert_audit_log(
                connection=connection,
                organization_id=organization_id,
                actor_user_id=actor_user_id,
                action="membership.upserted",
                target_type="membership",
                target_id=user_id,
            )
            row = connection.execute(
                """
                SELECT organization_id, user_id, role, created_at
                FROM memberships
                WHERE organization_id = ? AND user_id = ?
                """,
                (organization_id, user_id),
            ).fetchone()
        return MembershipRecord(**dict(row))

    def get_billing(self, organization_id: str) -> dict[str, str]:
        with self._connect() as connection:
            row = connection.execute(SELECT_BILLING, (organization_id,)).fetchone()
        return dict(row)

    def mock_checkout(
        self,
        organization_id: str,
        actor_user_id: str,
        plan: BillingPlan,
    ) -> dict[str, str]:
        updated_at = _now()
        with self._connect() as connection:
            connection.execute(
                """
                UPDATE billing_accounts
                SET plan = ?, status = ?, updated_at = ?
                WHERE organization_id = ?
                """,
                (
                    plan.value,
                    BillingStatus.ACTIVE.value,
                    updated_at,
                    organization_id,
                ),
            )
            self._insert_audit_log(
                connection=connection,
                organization_id=organization_id,
                actor_user_id=actor_user_id,
                action="billing.mock_checkout",
                target_type="billing",
                target_id=organization_id,
            )
        return self.get_billing(organization_id)

    def list_audit_logs(self, organization_id: str) -> list[dict[str, str]]:
        with self._connect() as connection:
            rows = connection.execute(SELECT_AUDIT_LOGS, (organization_id,)).fetchall()
        return [dict(row) for row in rows]

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._settings.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _insert_audit_log(
        self,
        connection: sqlite3.Connection,
        organization_id: str,
        actor_user_id: str,
        action: str,
        target_type: str,
        target_id: str,
    ) -> None:
        connection.execute(
            """
            INSERT INTO audit_logs (
                id,
                organization_id,
                actor_user_id,
                action,
                target_type,
                target_id,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(uuid4()),
                organization_id,
                actor_user_id,
                action,
                target_type,
                target_id,
                _now(),
            ),
        )


def _now() -> str:
    return datetime.now(UTC).isoformat()
