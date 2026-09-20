import asyncio
import importlib

import httpx


def test_health_endpoint(monkeypatch, tmp_path):
    monkeypatch.setenv("SOURIVA_DATA_DIR", str(tmp_path))
    import souriva.config

    souriva.config.get_settings.cache_clear()
    application = importlib.import_module("app")
    application.runtime = application.create_runtime()

    async def get_health():
        transport = httpx.ASGITransport(app=application.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.get("/health")

    response = asyncio.run(get_health())

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "documents_ready": False,
        "chunks": 0,
        "model_backend": "mock",
    }
