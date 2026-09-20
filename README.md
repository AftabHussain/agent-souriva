# AgentSouriva

AgentSouriva is a local document-grounded agent for PDF, Markdown, and text corpora. It indexes document chunks in FAISS, retrieves evidence for each question, and returns source-aware citations. When retrieval or citation checks fail, it abstains instead of returning an unsupported document answer.

The default model and embedding backends run without a model server. An OpenAI-compatible adapter provides the boundary for GPT-OSS-20B.

## Use cases

- Compare methods, datasets, metrics, and reported results across papers.
- Answer questions from technical manuals and architecture documentation.
- Extract authentication, endpoint, and usage details from API documentation.
- Compare specifications across documents with source references.
- Retrieve documented quantities and perform an approved calculation.
- Detect when the indexed documents do not contain the requested information.

## Architecture

```text
PDF / Markdown / text
          |
   loader and chunker
          |
  local embeddings + FAISS
          |
       retriever
          |
  agent: RETRIEVE or USE_TOOL
          |
 model adapter + grounding checks
          |
 ANSWER with citations or ABSTAIN
```

The agent uses one pass through retrieval and generation. Retrieved document text is marked as untrusted data in the model prompt. After generation, citation IDs are checked against retrieved evidence above the configured relevance threshold.

## Setup

Python 3.11 or newer is required.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload
```

`requirements.txt` installs the API, FAISS, PDF, MCP, and MLflow dependencies. For tests and evaluation tooling:

```bash
pip install -r requirements-dev.txt
pytest -q
ruff check .
```

Runtime settings use the `SOURIVA_` prefix. Common overrides include:

```bash
export SOURIVA_DATA_DIR=./artifacts
export SOURIVA_CHUNK_SIZE=900
export SOURIVA_CHUNK_OVERLAP=120
export SOURIVA_RETRIEVAL_TOP_K=4
export SOURIVA_MIN_RELEVANCE=0.18
```

The default feature-hashing embeddings are deterministic and favor lexical overlap. They require no downloaded weights. `HashEmbeddings` in `souriva/rag.py` is the replacement point for a learned embedding backend.

## Ingest documents

`POST /documents` accepts paths visible to the local API process. Each call replaces the active corpus and persists both the FAISS index and citation metadata under `SOURIVA_DATA_DIR`.

```bash
curl -s http://localhost:8000/documents \
  -H 'content-type: application/json' \
  -d '{"paths":["data/sample_docs/architecture.md","data/sample_docs/api.txt"]}'
```

Supported suffixes are `.pdf`, `.md`, `.markdown`, and `.txt`. PDF locations use page numbers; other formats retain document and chunk locations.

## Ask and retrieve

```bash
curl -s http://localhost:8000/ask \
  -H 'content-type: application/json' \
  -d '{"question":"What vector index does AgentSouriva use?"}'
```

A grounded response contains inline chunk references and structured citations:

```json
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
```

Direct retrieval is available separately:

```bash
curl -s http://localhost:8000/retrieve \
  -H 'content-type: application/json' \
  -d '{"query":"citation policy","top_k":4}'
```

Approved arithmetic takes an explicit route and does not call the model:

```bash
curl -s http://localhost:8000/ask \
  -H 'content-type: application/json' \
  -d '{"question":"calculate: (40 * 3) / 2"}'
```

## FastAPI endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Report process, index, and model-backend status. |
| `POST` | `/documents` | Replace the corpus from local document paths. |
| `POST` | `/retrieve` | Return ranked chunks with metadata and scores. |
| `POST` | `/ask` | Return a grounded answer, citations, or abstention. |

Interactive OpenAPI documentation is available at `http://localhost:8000/docs` while the service runs.

## MCP tools

Run the stdio MCP server with:

```bash
python -m souriva.mcp_server
```

It exposes only these approved tools:

- `search_documents(query, top_k=4)` returns ranked evidence.
- `get_document_chunk(chunk_id)` resolves a stable citation ID.
- `calculate(expression)` evaluates numeric arithmetic through a restricted syntax tree.

The MCP server reads the same persisted index and environment configuration as the API. Protocol handling is isolated in `souriva/mcp_server.py`; retrieval and calculator behavior remain usable without MCP.

## GPT-OSS-20B

Point the model adapter at an OpenAI-compatible GPT-OSS-20B endpoint:

```bash
export SOURIVA_MODEL_BACKEND=openai-compatible
export SOURIVA_MODEL_BASE_URL=http://localhost:8001/v1
export SOURIVA_MODEL_NAME=openai/gpt-oss-20b
export SOURIVA_MODEL_API_KEY=local
uvicorn app:app
```

The server must implement `POST /v1/chat/completions`. The adapter sends the question and retrieved chunks, requests inline chunk IDs, and rejects responses containing citation IDs outside the retrieved allow-list. Application, retrieval, and grounding code do not depend on a specific serving engine.

Without that server, leave `SOURIVA_MODEL_BACKEND=mock`. The mock returns deterministic extractive answers for local operation and tests.

## MLflow

Agent-run tracking is centralized and disabled by default. Enable it with:

```bash
export SOURIVA_MLFLOW_ENABLED=true
export SOURIVA_MLFLOW_TRACKING_URI=file:./mlruns
export SOURIVA_MLFLOW_EXPERIMENT=baseline-rag
uvicorn app:app
```

Each `/ask` run records the question, retrieved chunks and scores, answer, citations, action trace, tool use, latency, and relevant configuration. View local runs with:

```bash
mlflow ui --backend-store-uri ./mlruns
```

## Evaluation

The included four-case suite covers document retrieval, citations, abstention, and calculator routing:

```bash
python -m benchmarks.ragas_eval
```

This command reports measured retrieval Recall@k source hits, citation correctness, unsupported-answer rate, abstention accuracy, tool-use accuracy, and mean latency. It does not call an evaluator model.

Install the evaluation dependencies and provide credentials for the evaluator used by RAGAS before requesting model-judged metrics:

```bash
pip install -r requirements-dev.txt
export OPENAI_API_KEY=...
python -m benchmarks.ragas_eval --ragas
```

The RAGAS run adds faithfulness, answer relevance, context precision, and context recall. Add `--mlflow` to either command to record its observed metrics and case-level artifact. No benchmark score is hard-coded into the repository.

LM Evaluation Harness is not part of the runtime. It can be run independently against a future fine-tuned model when general-capability regression testing is needed.

## Optional model adaptation

Install the training dependencies separately:

```bash
pip install -e '.[training]'
```

Successful traces for supervised fine-tuning contain `question`, `retrieved_context`, `desired_action`, `grounded_answer`, and `citations`. An example is provided in `data/sft_example.jsonl`.

```bash
python -m training.sft data/sft_example.jsonl --model openai/gpt-oss-20b
# Add --qlora to load the base model in 4-bit mode on supported systems.
```

`training/rl.py` defines a trainer-neutral preference record and an explicit reward signal. It favors supported answers, correct citations, correct tool use, and appropriate abstention, while penalizing unsupported claims, invented citations, and unnecessary tool calls. The weights are starting values to calibrate against collected preferences; the runtime does not depend on preference optimization.

## Repository map

```text
app.py                    FastAPI transport
souriva/agent.py          action routing and orchestration
souriva/rag.py            loading, chunking, embeddings, FAISS, retrieval
souriva/model.py          mock and GPT-OSS-compatible adapters
souriva/alignment.py      citation validation and abstention
souriva/tools.py          approved document tools and calculator
souriva/mcp_server.py     MCP transport
souriva/tracking.py       MLflow run and evaluation logging
souriva/evaluation.py     direct quality metrics
benchmarks/ragas_eval.py  evaluation CLI and RAGAS adapter
training/                 optional LoRA and preference entry points
docs/build-log/           per-change engineering reports
```

## License

AgentSouriva is available under the MIT License.
