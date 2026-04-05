from __future__ import annotations

from fastapi import FastAPI


def create_mock_app() -> FastAPI:
    app = FastAPI(title="Async Data Aggregator Mock API", version="0.4.0")

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/profile/{user_id}")
    async def profile(user_id: str) -> dict[str, str]:
        return {
            "user_id": user_id,
            "name": user_id.capitalize(),
            "role": "engineer",
        }

    @app.get("/activity/{user_id}")
    async def activity(user_id: str) -> dict[str, int | str]:
        return {
            "user_id": user_id,
            "commits": len(user_id) * 3,
            "reviews": len(user_id),
        }

    @app.get("/status/{user_id}")
    async def status(user_id: str) -> dict[str, str]:
        return {
            "user_id": user_id,
            "availability": "focused",
        }

    return app
