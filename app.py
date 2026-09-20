from fastapi import FastAPI, HTTPException

from souriva.rag import ingest_paths
from souriva.runtime import create_runtime
from souriva.schemas import DocumentsRequest, IngestResponse


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


@app.post("/documents", response_model=IngestResponse)
def ingest_documents(request: DocumentsRequest) -> IngestResponse:
    try:
        count = ingest_paths(
            runtime.store,
            request.paths,
            chunk_size=runtime.settings.chunk_size,
            overlap=runtime.settings.chunk_overlap,
        )
    except (FileNotFoundError, OSError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return IngestResponse(chunks=count, sources=[path.name for path in request.paths])

