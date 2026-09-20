from time import perf_counter

from fastapi import FastAPI, HTTPException

from souriva.rag import ingest_paths
from souriva.runtime import create_runtime
from souriva.schemas import (
    AskRequest,
    AskResponse,
    DocumentsRequest,
    IngestResponse,
    RetrieveRequest,
    RetrieveResponse,
)
from souriva.tracking import log_agent_run

app = FastAPI(title="AgentSouriva", version="0.1.0")
runtime = create_runtime()


@app.get("/health")
async def health() -> dict:
    return {
        "status": "ok",
        "documents_ready": runtime.store.count > 0,
        "chunks": runtime.store.count,
        "model_backend": runtime.settings.model_backend,
    }


@app.post("/documents", response_model=IngestResponse)
async def ingest_documents(request: DocumentsRequest) -> IngestResponse:
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


@app.post("/retrieve", response_model=RetrieveResponse)
async def retrieve(request: RetrieveRequest) -> RetrieveResponse:
    evidence = runtime.store.search(
        request.query, top_k=request.top_k, min_score=runtime.settings.min_relevance
    )
    return RetrieveResponse(evidence=[item.__dict__ for item in evidence])


@app.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest) -> AskResponse:
    started = perf_counter()
    result = runtime.agent.ask(request.question)
    log_agent_run(request.question, result, (perf_counter() - started) * 1000, runtime.settings)
    return AskResponse(
        answer=result.answer.text,
        citations=[citation.__dict__ for citation in result.answer.citations],
        abstained=result.answer.abstained,
        reason=result.answer.reason,
        actions=[action.value for action in result.actions],
    )
