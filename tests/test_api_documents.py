import asyncio
import importlib

import httpx


def load_app(monkeypatch, tmp_path):
    monkeypatch.setenv("SOURIVA_DATA_DIR", str(tmp_path / "artifacts"))
    import souriva.config

    souriva.config.get_settings.cache_clear()
    application = importlib.import_module("app")
    application.runtime = application.create_runtime()
    return application.app


def request(app, method, path, json):
    async def send():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.request(method, path, json=json)

    return asyncio.run(send())


def test_documents_endpoint_ingests_local_file(monkeypatch, tmp_path):
    document = tmp_path / "manual.txt"
    document.write_text("The service supports token authentication.", encoding="utf-8")

    app = load_app(monkeypatch, tmp_path)
    response = request(app, "POST", "/documents", {"paths": [str(document)]})

    assert response.status_code == 200
    assert response.json() == {"chunks": 1, "sources": ["manual.txt"]}

    retrieved = request(app, "POST", "/retrieve", {"query": "token authentication", "top_k": 1})
    assert retrieved.status_code == 200
    assert retrieved.json()["evidence"][0]["source"] == "manual.txt"

    answer = request(app, "POST", "/ask", {"question": "How does token authentication work?"})
    assert answer.status_code == 200
    assert answer.json()["abstained"] is False
    assert answer.json()["citations"][0]["source"] == "manual.txt"


def test_documents_endpoint_reports_bad_path(monkeypatch, tmp_path):
    response = request(
        load_app(monkeypatch, tmp_path),
        "POST",
        "/documents",
        {"paths": [str(tmp_path / "missing.txt")]},
    )
    assert response.status_code == 400


def test_retrieve_validates_top_k(monkeypatch, tmp_path):
    response = request(
        load_app(monkeypatch, tmp_path), "POST", "/retrieve", {"query": "x", "top_k": 0}
    )
    assert response.status_code == 422


def test_ask_abstains_on_empty_corpus(monkeypatch, tmp_path):
    response = request(
        load_app(monkeypatch, tmp_path), "POST", "/ask", {"question": "Unknown fact?"}
    )
    assert response.status_code == 200
    assert response.json()["abstained"] is True
    assert response.json()["citations"] == []
