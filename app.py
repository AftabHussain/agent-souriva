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


# ---------------------------------------------------------------------
# Document Retrieval FastAPI Endpoint
# ---------------------------------------------------------------------
# This endpoint allows a client to search AgentSouriva's indexed
# documents and retrieve relevant evidence without invoking an LLM.
#
# 1. @app.post("/retrieve", response_model=RetrieveResponse)
#    - Registers retrieve() as the handler for POST /retrieve.
#    - response_model specifies the expected response structure,
#      which FastAPI uses for validation and JSON serialization.
#
# 2. def retrieve(request: RetrieveRequest) -> RetrieveResponse:
#    - Defines a synchronous request handler. FastAPI executes
#      synchronous handlers in a thread pool.
#    - RetrieveRequest is a Pydantic model used to parse and validate
#      the incoming JSON body (e.g., {"query": "authentication",
#      "top_k": 3}).
#    - The -> syntax specifies the expected return type.
#
# 3. runtime.store.search(...)
#    - runtime.store is the application's document search store.
#    - request.query contains the client's search question.
#    - request.top_k limits the number of retrieved chunks.
#    - runtime.settings.min_relevance supplies the minimum acceptable
#      similarity score.
#    - In FaissStore, search() embeds the query, performs FAISS
#      inner-product similarity search, filters low-scoring results,
#      and returns a list of Evidence objects.
#
# 4. RetrieveResponse(evidence=[item.__dict__ for item in evidence])
#    - This is a list comprehension that iterates over the retrieved
#      Evidence objects.
#    - __dict__ is a Python attribute containing an object's instance
#      attributes as a dictionary (for these Evidence dataclasses).
#    - For example, an Evidence object becomes:
#      {"id": "chunk-123", "text": "...", "source": "doc.pdf",
#       "location": "page 2", "score": 0.75}
#    - RetrieveResponse wraps the dictionaries in the response schema.
#    - FastAPI serializes the validated response into HTTP JSON.
#
# Overall flow:
# Client JSON -> FastAPI validation -> retrieve() -> FaissStore.search()
#             -> Evidence objects -> dictionaries -> JSON response.
#
# Design distinction: /retrieve only returns matching document
# evidence. It does not generate answers; that is handled by /ask.
# ---------------------------------------------------------------------
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
