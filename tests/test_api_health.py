import importlib

from fastapi.testclient import TestClient


def test_health_endpoint(monkeypatch, tmp_path):
    monkeypatch.setenv("SOURIVA_DATA_DIR", str(tmp_path))
    import souriva.config

    souriva.config.get_settings.cache_clear()
    application = importlib.import_module("app")
    response = TestClient(application.app).get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "documents_ready": False,
        "chunks": 0,
        "model_backend": "mock",
    }

