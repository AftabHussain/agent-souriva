## Document ingestion API

**Source commit:** [`fd96f13`](https://github.com/AftabHussain/agent-souriva/commit/fd96f134e5e2cec4a33b7806393664c257605d70)

### Change

Added validated request and response schemas and `POST /documents` for local file ingestion.

The endpoint passes validated paths and configured chunking limits into the shared ingestion pipeline:

    @app.post("/documents", response_model=IngestResponse)
    def ingest_documents(request: DocumentsRequest) -> IngestResponse:
        count = ingest_paths(runtime.store, request.paths,
                             chunk_size=runtime.settings.chunk_size,
                             overlap=runtime.settings.chunk_overlap)
        return IngestResponse(chunks=count,
                              sources=[p.name for p in request.paths])

FastAPI validates the request schema, and the thin route replaces the runtime corpus before returning the resulting count and source names.

### Architecture

The endpoint is a thin adapter over the RAG ingestion pipeline and shared runtime store. It accepts server-local paths for PDF, Markdown, and text files and replaces the active corpus.

### Design notes

Batch size is bounded at the schema. Expected file and format errors become HTTP 400 responses while unexpected failures remain visible. Responses report the resulting chunk count and submitted source names.

### Verification

Compiled the code, checked the diff, and added API cases for successful text ingestion and a missing path.

### Result

Clients can build the local FAISS corpus through a typed HTTP request.
