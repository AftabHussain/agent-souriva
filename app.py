from fastapi import FastAPI

from souriva.runtime import create_runtime


app = FastAPI(title="AgentSouriva", version="0.1.0")
runtime = create_runtime()


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "documents_ready": runtime.store.count > 0,
        "chunks": runtime.store.count,
        "model_backend": runtime.settings.model_backend,
    }

