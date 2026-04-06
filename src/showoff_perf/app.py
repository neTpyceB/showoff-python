from __future__ import annotations

from fastapi import FastAPI, HTTPException

from .cache import RedisCache
from .compute import CythonUnavailableError, PrimeService
from .config import Settings, get_settings
from .models import HealthResponse, PrimeSumRequest, PrimeSumResponse


def create_app(
    settings: Settings | None = None,
    service: PrimeService | None = None,
) -> FastAPI:
    resolved_settings = settings or get_settings()
    resolved_service = service or PrimeService(
        settings=resolved_settings,
        cache=RedisCache(resolved_settings.redis_url),
    )
    app = FastAPI(title="High-performance Service", version="0.8.0")

    @app.get("/health", response_model=HealthResponse)
    def read_health() -> HealthResponse:
        return HealthResponse.model_validate(resolved_service.health())

    @app.post("/prime-sums", response_model=PrimeSumResponse)
    def create_prime_sum(payload: PrimeSumRequest) -> PrimeSumResponse:
        try:
            return resolved_service.analyze(payload)
        except CythonUnavailableError as error:
            raise HTTPException(status_code=503, detail=str(error)) from error

    return app


app = create_app()
