from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Header, HTTPException

from .auth_client import AuthClient
from .config import Settings
from .models import (
    DiscoveryResponse,
    HealthResponse,
    JobCompletionRequest,
    JobCreateRequest,
    JobResponse,
)
from .store import JobStore


def create_data_app(
    settings: Settings,
    store: JobStore | None = None,
    auth_client: AuthClient | None = None,
) -> FastAPI:
    resolved_store = store or JobStore(settings.data_db_path)
    resolved_auth_client = auth_client or AuthClient(settings.auth_service_url)

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        resolved_store.ensure_schema()
        yield

    app = FastAPI(title="Data Service", version="0.9.0", lifespan=lifespan)

    @app.get("/health", response_model=HealthResponse)
    def read_health() -> HealthResponse:
        return HealthResponse(status="ok")

    @app.get("/discovery", response_model=DiscoveryResponse)
    def read_discovery() -> DiscoveryResponse:
        return DiscoveryResponse(
            service="data",
            auth_url=settings.auth_service_url,
            data_url=settings.data_service_url,
            worker_service=settings.worker_service_name,
        )

    @app.post("/jobs", response_model=JobResponse, status_code=201)
    def create_job(
        payload: JobCreateRequest,
        authorization: str = Header(alias="Authorization"),
    ) -> JobResponse:
        try:
            user_id = resolved_auth_client.validate(authorization)
        except PermissionError as exc:
            raise HTTPException(status_code=401, detail="Unauthorized") from exc
        return JobResponse.model_validate(
            resolved_store.create_job(user_id, payload.payload)
        )

    @app.get("/jobs/{job_id}", response_model=JobResponse)
    def read_job(
        job_id: str,
        authorization: str = Header(alias="Authorization"),
    ) -> JobResponse:
        try:
            user_id = resolved_auth_client.validate(authorization)
        except PermissionError as exc:
            raise HTTPException(status_code=401, detail="Unauthorized") from exc
        job = resolved_store.get_job(job_id)
        if job is None or job["owner_user_id"] != user_id:
            raise HTTPException(status_code=404, detail="Job not found")
        return JobResponse.model_validate(job)

    @app.post("/internal/jobs/claim", response_model=JobResponse | None)
    def claim_job() -> JobResponse | None:
        job = resolved_store.claim_next_job()
        return None if job is None else JobResponse.model_validate(job)

    @app.post("/internal/jobs/{job_id}/complete", response_model=JobResponse)
    def complete_job(job_id: str, payload: JobCompletionRequest) -> JobResponse:
        return JobResponse.model_validate(
            resolved_store.complete_job(job_id, payload.result)
        )

    return app
