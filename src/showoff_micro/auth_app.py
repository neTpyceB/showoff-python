from __future__ import annotations

from fastapi import FastAPI, Header, HTTPException

from .config import Settings
from .models import (
    DiscoveryResponse,
    HealthResponse,
    TokenRequest,
    TokenResponse,
    ValidationResponse,
)


def create_auth_app(settings: Settings) -> FastAPI:
    app = FastAPI(title="Auth Service", version="0.9.0")

    @app.get("/health", response_model=HealthResponse)
    def read_health() -> HealthResponse:
        return HealthResponse(status="ok")

    @app.get("/discovery", response_model=DiscoveryResponse)
    def read_discovery() -> DiscoveryResponse:
        return DiscoveryResponse(
            service="auth",
            auth_url=settings.auth_service_url,
            data_url=settings.data_service_url,
            worker_service=settings.worker_service_name,
        )

    @app.post("/tokens", response_model=TokenResponse)
    def create_token(payload: TokenRequest) -> TokenResponse:
        return TokenResponse(access_token=payload.user_id)

    @app.get("/validate", response_model=ValidationResponse)
    def validate_token(
        authorization: str = Header(alias="Authorization"),
    ) -> ValidationResponse:
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Unauthorized")
        return ValidationResponse(user_id=authorization.removeprefix("Bearer "))

    return app
