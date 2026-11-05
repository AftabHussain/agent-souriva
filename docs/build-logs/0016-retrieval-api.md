## Retrieval API

**Source commit:** [`3bf0fef`](https://github.com/AftabHussain/agent-souriva/commit/3bf0fefbf7db3f692740a7512b8f1762862624c2)

### Change

Added typed evidence schemas and `POST /retrieve` for direct corpus search.

The route applies request bounds and the runtime relevance threshold to the same store used by the agent:

    @app.post("/retrieve", response_model=RetrieveResponse)
    def retrieve(request: RetrieveRequest) -> RetrieveResponse:
        evidence = runtime.store.search(
            request.query,
            top_k=request.top_k,
            min_score=runtime.settings.min_relevance,
        )
        return RetrieveResponse(evidence=[item.__dict__ for item in evidence])

The response model serializes complete evidence records, letting clients inspect ranking and citations without triggering answer generation.

### Architecture

The endpoint exposes the same configured FAISS retriever used by the agent and MCP tools. Results preserve the stable chunk ID, text, source, location, and measured similarity score.

### Design notes

Query length and result count are bounded by request validation. The global relevance threshold is applied consistently so direct retrieval and agent decisions observe the same evidence floor.

### Verification

Compiled source and tests, checked the diff, and extended the ingestion integration test to restore and query the persisted corpus. Added request validation coverage for invalid `top_k`.

### Result

Clients can inspect ranked evidence independently of answer generation.
