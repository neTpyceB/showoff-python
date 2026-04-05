from __future__ import annotations

from io import BytesIO

import pytest

from showoff_pipeline.config import Settings
from showoff_pipeline.models import ProcessingMode
from showoff_pipeline.pipeline import PipelineInputError, PipelineService


def make_service(tmp_path, batch_size: int = 2) -> PipelineService:
    settings = Settings(
        api_host="0.0.0.0",
        api_port=8000,
        db_path=str(tmp_path / "pipeline.db"),
        insert_batch_size=batch_size,
    )
    service = PipelineService(settings)
    service.ensure_schema()
    return service


def test_stream_run_stores_transformed_rows(tmp_path) -> None:
    service = make_service(tmp_path)
    payload = BytesIO(
        b"timestamp,account,amount\n"
        b"2026-01-01T10:00:00+00:00, ACME ,10.50\n"
        b"2026-01-01T11:00:00+00:00,Globex,2.00\n"
    )

    result = service.run(payload, "sales.csv", ProcessingMode.STREAM)

    assert result.source_name == "sales.csv"
    assert result.mode is ProcessingMode.STREAM
    assert result.status == "success"
    assert result.processed_rows == 2
    assert result.stored_rows == 2
    assert result.total_amount_cents == 1250
    loaded = service.get_run(result.run_id)
    assert loaded == result


def test_batch_run_reads_all_rows_before_store(tmp_path) -> None:
    service = make_service(tmp_path, batch_size=1)
    payload = BytesIO(
        b"timestamp,account,amount\n"
        b"2026-01-02T10:00:00+00:00,Acme,1.25\n"
        b"2026-01-02T12:00:00+00:00,Acme,2.75\n"
    )

    result = service.run(payload, "batch.csv", ProcessingMode.BATCH)
    monitoring = service.get_monitoring()

    assert result.mode is ProcessingMode.BATCH
    assert result.total_amount_cents == 400
    assert monitoring.runs_total == 1
    assert monitoring.successful_runs == 1
    assert monitoring.failed_runs == 0
    assert monitoring.stored_rows_total == 2
    assert monitoring.total_amount_cents == 400


def test_invalid_input_marks_run_failed(tmp_path) -> None:
    service = make_service(tmp_path)
    payload = BytesIO(b"timestamp,account,amount\nnot-a-date,Acme,1.00\n")

    with pytest.raises(PipelineInputError):
        service.run(payload, "broken.csv", ProcessingMode.STREAM)

    monitoring = service.get_monitoring()
    assert monitoring.runs_total == 1
    assert monitoring.successful_runs == 0
    assert monitoring.failed_runs == 1
    assert monitoring.stored_rows_total == 0
    assert monitoring.total_amount_cents == 0


def test_empty_file_marks_run_failed(tmp_path) -> None:
    service = make_service(tmp_path)

    with pytest.raises(PipelineInputError, match="CSV header is required"):
        service.run(BytesIO(b""), "empty.csv", ProcessingMode.STREAM)


def test_get_run_raises_for_missing_id(tmp_path) -> None:
    service = make_service(tmp_path)

    with pytest.raises(KeyError):
        service.get_run("missing")
