from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, HTTPException, Query, UploadFile

from .config import Settings, get_settings
from .models import (
    HealthResponse,
    MonitoringResponse,
    PipelineRunResponse,
    ProcessingMode,
)
from .pipeline import PipelineInputError, PipelineService


def create_app(
    settings: Settings | None = None,
    service: PipelineService | None = None,
) -> FastAPI:
    resolved_settings = settings or get_settings()
    resolved_service = service or PipelineService(resolved_settings)

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
        resolved_service.ensure_schema()
        yield

    app = FastAPI(title="ETL Pipeline System", version="0.6.0", lifespan=lifespan)

    @app.get("/health", response_model=HealthResponse)
    def read_health() -> HealthResponse:
        return HealthResponse(status="ok")

    @app.post("/pipeline/runs", response_model=PipelineRunResponse, status_code=201)
    def create_pipeline_run(
        file: UploadFile = File(...),
        mode: ProcessingMode = Query(default=ProcessingMode.STREAM),
    ) -> PipelineRunResponse:
        try:
            return resolved_service.run(
                file_object=file.file,
                source_name=file.filename or "upload.csv",
                mode=mode,
            )
        except PipelineInputError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

    @app.get("/pipeline/runs/{run_id}", response_model=PipelineRunResponse)
    def read_pipeline_run(run_id: str) -> PipelineRunResponse:
        try:
            return resolved_service.get_run(run_id)
        except KeyError as error:
            raise HTTPException(status_code=404, detail="Run not found") from error

    @app.get("/monitoring", response_model=MonitoringResponse)
    def read_monitoring() -> MonitoringResponse:
        return resolved_service.get_monitoring()

    return app


app = create_app()
