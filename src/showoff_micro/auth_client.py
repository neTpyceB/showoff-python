from __future__ import annotations

import json
from urllib import request
from urllib.error import HTTPError


class AuthClient:
    def __init__(self, auth_service_url: str) -> None:
        self._auth_service_url = auth_service_url.rstrip("/")

    def validate(self, authorization: str) -> str:
        req = request.Request(
            f"{self._auth_service_url}/validate",
            headers={"Authorization": authorization},
        )
        try:
            with request.urlopen(req, timeout=5) as response:
                payload = json.loads(response.read().decode())
        except HTTPError as error:
            raise PermissionError("Unauthorized") from error
        return payload["user_id"]
