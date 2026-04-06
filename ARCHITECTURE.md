# Architecture

## Services

- `api`: public FastAPI service for organization, billing, and audit operations.
- `sqlite`: local file-backed storage mounted into the API container.

## Domain

- Tenant boundary: organization.
- Roles: `admin`, `member`.
- Billing mock: plan + status per organization.
- Audit log: append-only records for organization creation, membership updates, and billing checkout.

## Structure

- `src/showoff_saas/config.py`: environment-driven runtime settings.
- `src/showoff_saas/repository.py`: SQLite schema and data access.
- `src/showoff_saas/service.py`: tenant scoping and RBAC rules.
- `src/showoff_saas/app.py`: FastAPI routes and HTTP mapping.
- `src/showoff_saas/models.py`: request and response models.
- `src/showoff_saas/__main__.py`: API process entrypoint.

## Access Model

- `X-User-Id` identifies the current actor.
- Organization reads require membership.
- Membership writes, billing reads, billing checkout, and audit log reads require `admin`.
- Non-members receive `404` on organization reads and `403` on admin-only operations for existing organizations.
