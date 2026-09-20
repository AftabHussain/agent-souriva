import importlib

from fastapi.testclient import TestClient


def load_app(monkeypatch, tmp_path):
    monkeypatch.setenv("SOURIVA_DATA_DIR", str(tmp_path / "artifacts"))
    import souriva.config

    souriva.config.get_settings.cache_clear()
    application = importlib.import_module("app")
    application.runtime = application.create_runtime()
    return TestClient(application.app)


def test_documents_endpoint_ingests_local_file(monkeypatch, tmp_path):
    document = tmp_path / "manual.txt"
    document.write_text("The service supports token authentication.", encoding="utf-8")

    response = load_app(monkeypatch, tmp_path).post("/documents", json={"paths": [str(document)]})

    assert response.status_code == 200
    assert response.json() == {"chunks": 1, "sources": ["manual.txt"]}

    retrieved = load_app(monkeypatch, tmp_path).post(
        "/retrieve", json={"query": "token authentication", "top_k": 1}
    )
    assert retrieved.status_code == 200
    assert retrieved.json()["evidence"][0]["source"] == "manual.txt"


def test_documents_endpoint_reports_bad_path(monkeypatch, tmp_path):
    response = load_app(monkeypatch, tmp_path).post(
        "/documents", json={"paths": [str(tmp_path / "missing.txt")]}
    )
    assert response.status_code == 400


def test_retrieve_validates_top_k(monkeypatch, tmp_path):
    response = load_app(monkeypatch, tmp_path).post("/retrieve", json={"query": "x", "top_k": 0})
    assert response.status_code == 422

