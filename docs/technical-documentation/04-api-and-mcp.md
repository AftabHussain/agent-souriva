# API and MCP Interfaces

AgentSouriva exposes a small FastAPI interface. `GET` is used to read status information, while the `POST` endpoints accept request data such as document paths, retrieval queries, or questions.

| Method | Endpoint     | Purpose                                              |
|:-------|:-------------|:-----------------------------------------------------|
| `GET`  | `/health`    | Check application, index, and model-backend status   |
| `POST` | `/documents` | Load a new set of documents for indexing             |
| `POST` | `/retrieve`  | Retrieve ranked document evidence for a query        |
| `POST` | `/ask`       | Ask a grounded question or invoke an approved action |

## Document Ingestion Interface

All endpoints belong to the AgentSouriva FastAPI server. A separate HTTP client—for example, an administration script, command-line client, web front end, test harness, or another service—sends requests to that server. The client does not call the retrieval store or model directly. An operator or administration process calls `/documents` when establishing or refreshing the searchable document collection. After that collection is ready, a user-facing application calls `/ask` when it needs a complete grounded answer, or `/retrieve` when it needs ranked evidence without answer generation. A deployment monitor can call `/health` at any time to check readiness.

For example, an administrator can first use a command-line HTTP client to send document paths using `POST /documents`. Later, when a user submits a question in a web interface, that web interface acts as the HTTP client and sends the question using `POST /ask`.

**Aftab:** RESOLVED– here give code listings of actually how are teh calls made in the code, I think you already have them implemented in the source

The repository’s API tests exercise this client-to-server path with `httpx`. A deployed web or command-line client sends the same methods, paths, and JSON bodies over the network rather than through `ASGITransport`.

Listing 1 illustrates an in-process HTTP testing pattern for AgentSouriva. The helper function `request()` provides a synchronous interface for sending HTTP requests to the application. Inside it, the nested asynchronous function `send()` performs the actual request using `httpx.AsyncClient`. The `httpx.ASGITransport` class routes requests directly to the FastAPI application through the ASGI interface, eliminating the need to start an external web server. Within `send()`, the `await` keyword suspends the coroutine while the asynchronous request is being processed, allowing the event loop to execute other ready tasks. The `async with` construct automatically manages the HTTP client’s lifecycle, including closing it when the block exits. The outer `request()` function uses `asyncio.run(send())` to execute the coroutine through an event loop and return the resulting HTTP response to synchronous test code. This helper is then reused to test the document ingestion endpoint (`/documents`) and question-answering endpoint (`/ask`), allowing HTTP-level application behavior to be tested without starting a separate server process.

**Listing 1: Testing AgentSouriva’s HTTP API in-process**

```python
import asyncio
import httpx

# Helper function for sending HTTP requests to an ASGI app.
# Parameters:
#   app    : FastAPI/ASGI application being tested
#   method : HTTP method, e.g., "GET" or "POST"
#   path   : API endpoint, e.g., "/documents"
#   json   : Python object sent as the JSON request body

def request(app, method, path, json):

    # 'async def' declares an asynchronous function.
    # It can use 'await' for asynchronous operations.
    # This nested function captures the arguments of
    # the enclosing request() function.

    async def send():

        # ASGITransport connects HTTPX directly to the app.
        # Requests are handled inside the Python process,
        # without starting a web server or opening a port.
        transport = httpx.ASGITransport(app=app)

        # AsyncClient supports asynchronous HTTP requests.
        # 'async with' automatically closes the client
        # when the block finishes.
        #
        # base_url supplies a base for relative paths.
        # "http://test" is not contacted over the network.

        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://test"
        ) as client:

            # 'await' suspends execution until the
            # asynchronous HTTP request completes.
            #
            # method and path select the API operation.
            # json=json serializes the supplied Python
            # object into the HTTP JSON request body.
            #
            # The result is an httpx.Response object.

            return await client.request(
                method, path, json=json
            )

    # asyncio.run() starts an event loop, executes the
    # coroutine returned by send(), and returns its result.
    #
    # This makes the asynchronous operation callable
    # from synchronous test code.
    # It requires that no event loop is already running.

    return asyncio.run(send())


# -------------------------------------------------------
# Example 1: Document ingestion
# -------------------------------------------------------

# Assume 'app' is the FastAPI application and
# 'document' is a Path pointing to a test document.
#
# POST /documents submits the document path for
# processing by the application's ingestion endpoint.
#
# str(document) converts a Path object into a string.

response = request(
    app,
    "POST",
    "/documents",
    {"paths": [str(document)]},
)


# -------------------------------------------------------
# Example 2: Question answering
# -------------------------------------------------------

# POST /ask sends a question to the agent.
# The endpoint can retrieve relevant document
# evidence and produce a grounded response.

answer = request(
    app,
    "POST",
    "/ask",
    {"question": "How does token authentication work?"},
)

# Both 'response' and 'answer' are HTTP response objects.
# Their status codes and JSON bodies can be inspected:
#
# answer.status_code
# answer.json()
```

On the server side, the corresponding FastAPI route declarations in `app.py` deserialize those JSON bodies into typed request objects and invoke the ingestion or agent flow. The excerpt below omits error handling and response-field assembly while retaining the implemented call path.

Listing 2 illustrates the server-side handling of document ingestion and question-answering requests in AgentSouriva. FastAPI uses route decorators, such as `@app.post("/documents")`, to associate an HTTP method and URL path with a Python function. The corresponding handler functions, `ingest_documents()` and `ask()`, are invoked when clients submit POST requests to `/documents` and `/ask`, respectively.

Each handler declares a typed request parameter: `DocumentsRequest` or `AskRequest`. These are request schemas that FastAPI uses to deserialize and validate incoming JSON data, assuming they are defined as Pydantic models, which are Python classes that define the expected structure and data types of information, and automatically validate incoming data. For example, a JSON body containing a `question` field is converted into an `AskRequest` object, allowing the handler to access the submitted text through `request.question`. The `response_model` argument similarly declares the expected response schema, which FastAPI uses for response validation and serialization.

The `runtime` object provides access to application components, including the document store (`runtime.store`) and agent (`runtime.agent`). The `ingest_documents()` handler delegates document processing to `ingest_paths()`, whereas the `ask()` handler delegates question answering to `runtime.agent.ask()`. This separates HTTP request handling from the underlying application logic.

Both handlers use `async def`, which declares coroutine functions that can support asynchronous execution. However, the illustrated calls to `ingest_paths()` and `runtime.agent.ask()` are synchronous: neither call uses `await`. Consequently, if these operations perform blocking work, they also block the event-loop thread during execution. The `async` declaration alone does not make synchronous operations non-blocking.

Finally, each handler constructs a typed response object, either `IngestResponse` or `AskResponse`, which FastAPI serializes into the HTTP response body. The ellipses in the listing indicate implementation details omitted for clarity, rather than complete argument values.

**Listing 2: FastAPI route handlers for document ingestion and question answering**

```python
# The @app.post decorator registers an HTTP endpoint.
# When POST /documents is received, FastAPI calls
# ingest_documents().
#
# response_model=IngestResponse specifies the response
# schema used for validation and JSON serialization.

@app.post("/documents", response_model=IngestResponse)

# 'async def' declares a coroutine function, allowing
# asynchronous operations within the route.
#
# 'request: DocumentsRequest' is a type annotation.
# FastAPI uses it to parse and validate the incoming
# JSON body into a DocumentsRequest object.

async def ingest_documents(request: DocumentsRequest):

    # runtime.store: the application's document store.
    # request.paths: document paths extracted from the
    # validated request object.
    #
    # ingest_paths() performs document ingestion.
    # Its return value is assigned to 'count'.
    # '...' represents arguments omitted in this excerpt.

    count = ingest_paths(runtime.store, request.paths, ...)

    # Construct an IngestResponse object.
    # 'chunks' receives the returned chunk count.
    # 'sources' represents source-related response data.
    # FastAPI serializes the response object into JSON.

    return IngestResponse(chunks=count, sources=...)


# Register the POST /ask endpoint.
# AskResponse specifies the expected response schema.

@app.post("/ask", response_model=AskResponse)

# FastAPI parses the incoming JSON body into AskRequest.
# The request object provides access to the question.

async def ask(request: AskRequest):

    # runtime.agent: the agent instance used by the app.
    # request.question: question supplied by the client.
    #
    # .ask() invokes the agent's question-answering flow.
    # The result is stored in the variable 'result'.

    result = runtime.agent.ask(request.question)

    # result.answer.text accesses the generated answer.
    # AskResponse packages it into the response schema.
    # FastAPI converts the returned object into JSON.

    return AskResponse(answer=result.answer.text, ...)
```

AgentSouriva retrieves evidence, invokes the configured model boundary when needed, validates the result, and returns JSON to the web interface for presentation to the user.

The `/documents` endpoint accepts a JSON object containing file paths and builds the index and source-aware citation metadata for those files. Ingestion is replacement-based rather than append-based: each successful call makes the submitted files the complete active corpus and replaces the previously indexed chunks. For example, if one request indexes `architecture.md` and `api.txt`, and a later request submits only `handbook.pdf`, subsequent `/retrieve` and `/ask` requests search `handbook.pdf` rather than the earlier two files. This later ingestion is useful when an operator publishes a revised or entirely different collection. Request bodies are transmitted as `application/json`.

A representative request-body structure from the project documentation is:

    {"paths": ["data/sample_docs/architecture.md", "data/sample_docs/api.txt"]}

## Grounded Question Interface

The `/ask` endpoint accepts a JSON question, initiates the answer flow, and returns the answer together with structured citation information, an abstention indicator, a reason, and an action trace.

The request-body structure is:

    {"question": "What vector index does AgentSouriva use?"}

A grounded response includes both the answer and structured citation information:

    {
      "answer": "AgentSouriva loads local documents ... FAISS index. [chunk-...]",
      "citations": [
        {
          "id": "chunk-...",
          "source": "architecture.md",
          "location": "document, chunk 1",
          "score": 0.4
        }
      ],
      "abstained": false,
      "reason": null,
      "actions": ["RETRIEVE", "ANSWER"]
    }

The structured response exposes both the answer and the evidence trail to applications built on top of AgentSouriva.

## Direct Retrieval Interface

The `/retrieve` endpoint returns ranked document chunks along with source metadata and relevance scores, without first generating an answer. Its JSON request includes a query and an optional retrieval limit, as illustrated by the source request-body structure:

    {"query": "citation policy", "top_k": 4}

## Approved Tool Routing

The `/ask` endpoint can route approved arithmetic requests to the deterministic calculator rather than delegate calculation to the language model. The approved tool surface consists of document search, chunk retrieval, and deterministic arithmetic.

## Model Context Protocol (MCP)

AgentSouriva can expose its approved capabilities through the Model Context Protocol, allowing an MCP-compatible client to call its document and calculator tools.

The stdio MCP interface exposes the following tool signatures:

    search_documents(query, top_k=4)
    get_document_chunk(chunk_id)
    calculate(expression)

The MCP interface uses the same persisted retrieval index and runtime configuration as the main API. It is an interface to the existing capabilities, not a separate retrieval implementation.

#### MCP-based interaction.

An MCP-compatible host, such as an IDE assistant or another agent runtime, acts as the MCP client. It starts or connects to the AgentSouriva MCP server over standard input and output, discovers the `search_documents` tool, and invokes it with a query. The AgentSouriva MCP server receives that tool call and delegates it to `DocumentTools`.

`DocumentTools` is the transport-independent approved-tool wrapper defined in .

DocumentTools, defined in souriva/tools.py, is a wrapper groups the small set of operations that are explicitly allowed to be invoked – Its methods contain no HTTP- or MCP-specific code, so different interfaces can reuse the same implementation. It holds the shared `FaissStore` and exposes three bounded operations: searching indexed documents, retrieving one chunk by its stable identifier, and evaluating restricted arithmetic. The MCP functions in are thin protocol adapters that call these methods; `DocumentTools` performs the reusable application operation without depending on MCP itself. For a search call, it queries the shared FAISS index and converts the resulting evidence objects into dictionaries before the MCP server sends them back to the client. The communicating entities are therefore the external MCP host and the AgentSouriva MCP server; the user interacts with the host rather than issuing the tool call directly.

#### Non-MCP HTTP interaction.

A web front end or command-line client can instead send `POST /retrieve` with a JSON query directly to the AgentSouriva FastAPI server. FastAPI calls the same underlying retrieval store and returns ranked evidence as an HTTP JSON response. The communicating entities are the HTTP client and the AgentSouriva FastAPI server, and no MCP host, tool discovery, or MCP transport participates. This form is appropriate when an application already integrates with AgentSouriva as an HTTP service; MCP is appropriate when an agent host needs AgentSouriva capabilities exposed as discoverable tools.

For example, a document-search web portal with a fixed backend contract can call `/documents`, `/retrieve`, and `/ask` directly: its developers already know which endpoint to call, and its user interface controls the request sequence. Because the portal already knows which HTTP endpoints to call, adding MCP would increase complexity without providing any useful new functionality. By contrast, an IDE assistant that already supports MCP can be configured to launch the AgentSouriva MCP server. The assistant discovers `search_documents`, `get_document_chunk`, and `calculate` at runtime and chooses among them while handling a user’s request, without requiring custom HTTP integration code for each operation. In that situation, tool discovery and standardized invocation are the reason to use MCP.
