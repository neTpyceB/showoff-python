from __future__ import annotations

import json
from urllib import request


class DataClient:
    def __init__(self, data_service_url: str) -> None:
        self._data_service_url = data_service_url.rstrip("/")

    def claim_next_job(self) -> dict[str, str] | None:
        req = request.Request(
            f"{self._data_service_url}/internal/jobs/claim",
            data=b"{}",
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with request.urlopen(req, timeout=5) as response:
            payload = response.read().decode()
        return None if payload == "null" else json.loads(payload)

    def complete_job(self, job_id: str, result: str) -> dict[str, str]:
        req = request.Request(
            f"{self._data_service_url}/internal/jobs/{job_id}/complete",
            data=json.dumps({"result": result}).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with request.urlopen(req, timeout=5) as response:
            return json.loads(response.read().decode())
