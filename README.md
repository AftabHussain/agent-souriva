# AgentSouriva

AgentSouriva is a local, evidence-grounded agent for reasoning over PDF, Markdown, and text collections.

It is built around a simple question: **how can an AI agent answer from documents while keeping its evidence, tool use, and uncertainty visible?**

Given a collection of documents, AgentSouriva indexes their contents, retrieves relevant evidence for each question, and returns source-aware answers. It can validate citations against retrieved evidence, route approved tasks through dedicated tools, and abstain when the available documents do not sufficiently support an answer.

The project is designed as a compact environment for exploring **trustworthy document-grounded agents**, including retrieval, constrained tool use, citation validation, abstention, evaluation, and optional model adaptation.

## Why AgentSouriva?

Retrieval-augmented systems can make language models useful over private or specialized documents, but retrieval alone does not guarantee that an answer is supported by the retrieved evidence.

AgentSouriva makes the important parts of this process explicit:

- **Evidence retrieval**: answers are grounded in chunks retrieved from the indexed corpus.
- **Source-aware citations**: responses retain references to the evidence used.
- **Citation validation**: citation IDs are checked against the evidence actually retrieved.
- **Controlled tool use**: the agent operates through a small set of approved tools.
- **Abstention**: unsupported document questions can return an abstention rather than an unsupported answer.
- **Evaluation**: retrieval, citation behavior, abstention, tool use, unsupported answers, and latency can be measured directly.

This makes AgentSouriva useful both as a local document assistant and as an experimental platform for studying grounded agent behavior.

## Example Uses

AgentSouriva can be used to:

- compare methods, datasets, metrics, and reported results across papers;
- answer questions from technical manuals and architecture documentation;
- extract authentication, endpoint, and usage details from API documentation;
- compare specifications across documents with source references;
- retrieve documented quantities and perform approved calculations;
- identify when the indexed documents do not contain enough information to answer a question.

## How It Works

```text
PDF / Markdown / text
         |
         v
   Load and chunk
         |
         v
  Embed and index
         |
         v
 Retrieve evidence
         |
         v
 Agent reasoning / tool use
         |
         v
 Grounding and citation checks
         |
         v
 Answer with citations
       or abstain
```

### 1. Build the document index

Documents are loaded and divided into chunks. Each chunk retains source information so retrieved evidence can later be traced back to its document and location.

The chunks are embedded and stored in a FAISS index for retrieval.

### 2. Retrieve relevant evidence

When a question arrives, AgentSouriva searches the index for the document chunks most relevant to that question.

Retrieval can also be called independently when an application needs the evidence itself rather than a generated answer.

### 3. Route the request

The agent decides whether the request should use document retrieval or an approved tool.

Document questions use retrieved evidence. Approved arithmetic is routed through a deterministic calculator rather than delegated to the language model.

### 4. Generate a grounded answer

For document questions, the model receives the question together with the retrieved evidence.

Retrieved document text is treated as untrusted data in the prompt rather than as instructions for the agent.

### 5. Validate the result

Before returning the response, AgentSouriva checks that citation IDs in the generated answer correspond to evidence retrieved above the configured relevance threshold.

The result is either a supported answer with citations or an abstention when the indexed evidence is insufficient.

## Quick Start

AgentSouriva requires Python 3.11 or newer.

Create and activate a virtual environment so the project dependencies stay isolated from the rest of your Python installation:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install the runtime dependencies:

```bash
pip install -r requirements.txt
```

Then start AgentSouriva as a local FastAPI service:

```bash
uvicorn app:app --reload
```

The API is now available at:

```text
http://localhost:8000
```

FastAPI also provides interactive API documentation at:

```text
http://localhost:8000/docs
```

## Add Documents

Once AgentSouriva is running, send it the paths of the files you want it to index and search.

The command below sends a POST request to `http://localhost:8000/documents`, the FastAPI endpoint used for loading documents. The JSON data lists the file paths to load: `architecture.md` and `api.txt`. AgentSouriva then builds the retrieval index and citation metadata for those files.

Because the data is being sent as JSON, `content-type: application/json` tells FastAPI how to parse the request body.

```bash
curl -s http://localhost:8000/documents \
  -H 'content-type: application/json' \
  -d '{"paths":["data/sample_docs/architecture.md","data/sample_docs/api.txt"]}'
```

Loading another set of documents later replaces the previously indexed set.

Supported formats:

```text
.pdf
.md
.markdown
.txt
```

For PDFs, citation locations use page numbers. Markdown and text sources retain document and chunk locations.

## Ask Questions

Once documents have been indexed, send a question to `http://localhost:8000/ask`, the FastAPI endpoint that runs AgentSouriva's answer flow.

The command below sends a JSON object containing the question. As with document loading, the `application/json` header tells FastAPI how to parse that request data:

```bash
curl -s http://localhost:8000/ask \
  -H 'content-type: application/json' \
  -d '{"question":"What vector index does AgentSouriva use?"}'
```

A grounded response includes both the answer and structured citation information:

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

The structured response exposes both the answer and the evidence trail to applications built on top of AgentSouriva.

## Retrieve Evidence Directly

If you want to inspect what AgentSouriva retrieves before any answer is generated, send a query directly to `http://localhost:8000/retrieve`.

The example below sends the query as JSON and asks for the four highest-ranked chunks related to `citation policy`:

```bash
curl -s http://localhost:8000/retrieve \
  -H 'content-type: application/json' \
  -d '{"query":"citation policy","top_k":4}'
```

This returns ranked document chunks together with their metadata and relevance scores.

## Tool Use

AgentSouriva keeps tool use explicit and restricted.

The current tool set includes:

- document search;
- retrieval of a specific document chunk;
- deterministic arithmetic.

To see this routing in practice, send another JSON question through the same `/ask` endpoint, this time containing an arithmetic request:

```bash
curl -s http://localhost:8000/ask \
  -H 'content-type: application/json' \
  -d '{"question":"calculate: (40 * 3) / 2"}'
```

AgentSouriva recognizes the request as approved arithmetic and routes it to the deterministic calculator instead of asking the language model to compute the result.

## Features

### Local document retrieval

Document chunks are indexed locally using FAISS.

The default `HashEmbeddings` backend uses deterministic feature hashing and requires no downloaded embedding weights. It favors lexical overlap and provides a lightweight replacement point for learned embedding backends.

### Grounded generation

Retrieved document chunks are supplied as evidence for the model rather than treated as trusted instructions.

Generated citation IDs are validated against the retrieved evidence before the answer is returned.

### Abstention

When the available evidence does not sufficiently support a document answer, the system can abstain rather than return an unsupported answer.

### Constrained tools

Agent actions are limited to explicitly approved tools. Retrieval and arithmetic remain separate from general model generation.

### Local-first model boundary

The default model and embedding backends can operate without a separately hosted model server.

For larger local models, AgentSouriva exposes an OpenAI-compatible model boundary. GPT-OSS-20B can be connected through any compatible serving setup without coupling the retrieval and grounding layers to a particular inference engine.

### Observable agent runs

Optional MLflow integration can record questions, retrieved evidence, scores, answers, citations, tool use, action traces, latency, and relevant configuration.

### Evaluation

The repository includes direct evaluation for:

- retrieval Recall@k source hits;
- citation correctness;
- unsupported-answer rate;
- abstention accuracy;
- tool-use accuracy;
- mean latency.

Optional RAGAS evaluation adds:

- faithfulness;
- answer relevance;
- context precision;
- context recall.

## API Reference

AgentSouriva exposes a small FastAPI interface. `GET` is used to read status information, while the `POST` endpoints accept request data such as document paths, retrieval queries, or questions.

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Check application, index, and model-backend status |
| `POST` | `/documents` | Load a new set of documents for indexing |
| `POST` | `/retrieve` | Retrieve ranked document evidence for a query |
| `POST` | `/ask` | Ask a grounded question or invoke an approved action |

Interactive OpenAPI documentation is available at:

```text
http://localhost:8000/docs
```

## Configuration

Runtime settings use the `SOURIVA_` prefix.

Set these environment variables before starting AgentSouriva when you want to change where indexes are stored, how documents are chunked, how many results are retrieved, or the minimum relevance threshold:

```bash
export SOURIVA_DATA_DIR=./artifacts
export SOURIVA_CHUNK_SIZE=900
export SOURIVA_CHUNK_OVERLAP=120
export SOURIVA_RETRIEVAL_TOP_K=4
export SOURIVA_MIN_RELEVANCE=0.18
```

Any values you set are read by the application when it starts.

## MCP

AgentSouriva can expose its approved capabilities through the Model Context Protocol, allowing an MCP-compatible client to call its document and calculator tools.

Start the stdio MCP server with:

```bash
python -m souriva.mcp_server
```

This launches AgentSouriva's MCP interface using the same persisted index and configuration as the main application.

The MCP interface exposes:

```text
search_documents(query, top_k=4)
get_document_chunk(chunk_id)
calculate(expression)
```

The MCP server uses the same persisted retrieval index and configuration as the API. MCP is an interface to the existing capabilities rather than a separate retrieval implementation.

## GPT-OSS-20B

AgentSouriva can connect to GPT-OSS-20B through an OpenAI-compatible model server.

The following settings tell AgentSouriva to use that backend, where the model server is running, which model name to request, and which API key value to send. After setting them, start AgentSouriva so it picks up the configuration:

```bash
export SOURIVA_MODEL_BACKEND=openai-compatible
export SOURIVA_MODEL_BASE_URL=http://localhost:8001/v1
export SOURIVA_MODEL_NAME=openai/gpt-oss-20b
export SOURIVA_MODEL_API_KEY=local

uvicorn app:app
```

The configured model server must provide:

```text
POST /v1/chat/completions
```

The adapter sends the question and retrieved evidence to the model and requests inline chunk citations.

Application logic, retrieval, and grounding do not depend on a specific serving engine.

Without an external model server, the default mock backend provides deterministic extractive responses for local operation and testing.

## MLflow Tracking

Agent-run tracking is optional and disabled by default.

To record AgentSouriva runs with MLflow, enable tracking, choose the local tracking database, and name the experiment before starting the application:

```bash
export SOURIVA_MLFLOW_ENABLED=true
export SOURIVA_MLFLOW_TRACKING_URI=sqlite:///mlflow.db
export SOURIVA_MLFLOW_EXPERIMENT=baseline-rag

uvicorn app:app
```

To inspect the recorded runs in MLflow's local web interface, start the UI against the same database:

```bash
mlflow ui --backend-store-uri sqlite:///mlflow.db
```

Each `/ask` run can record the question, retrieved chunks and scores, generated answer, citations, action trace, tool usage, latency, and relevant configuration.

## Evaluation

The included evaluation suite covers document retrieval, citation behavior, abstention, and calculator routing.

Install the development and evaluation dependencies, then run the built-in evaluation suite:

```bash
pip install -r requirements-dev.txt
python -m benchmarks.ragas_eval
```

The default evaluation reports directly measured metrics and does not require an evaluator model.

To add RAGAS model-judged metrics, provide the evaluator credentials and run the same evaluation command with `--ragas`:

```bash
export OPENAI_API_KEY=...
python -m benchmarks.ragas_eval --ragas
```

Add `--mlflow` to either command to record evaluation metrics and case-level artifacts.

No benchmark score is hard-coded into the repository.

LM Evaluation Harness is not part of the runtime. It can be used independently in future model-evaluation workflows if general-capability regression testing is needed.

## Optional Model Adaptation

AgentSouriva includes experimental entry points for adapting a model to the desired agent behavior.

Install the optional training dependencies separately from the core runtime:

```bash
pip install -e '.[training]'
```

Successful supervised traces contain:

```text
question
retrieved_context
desired_action
grounded_answer
citations
```

An example is available in:

```text
data/sft_example.jsonl
```

To start supervised fine-tuning from the example trace file, run the training module and specify the base model:

```bash
python -m training.sft data/sft_example.jsonl \
  --model openai/gpt-oss-20b
```

On supported systems, `--qlora` can be used to load the base model in 4-bit mode.

The preference-training interface defines an explicit reward signal around supported answers, citation correctness, appropriate tool use, and abstention. Unsupported claims, invented citations, and unnecessary tool calls are penalized.

These training components are optional. The core AgentSouriva runtime does not depend on model fine-tuning or preference optimization.

## Repository Structure

```text
app.py                    FastAPI interface

souriva/
├── agent.py              action routing and orchestration
├── rag.py                loading, chunking, embeddings, FAISS, retrieval
├── model.py              model adapters
├── alignment.py          citation validation and abstention
├── tools.py              approved document tools and calculator
├── mcp_server.py         MCP interface
├── tracking.py           MLflow run and evaluation logging
└── evaluation.py         direct quality metrics

benchmarks/
└── ragas_eval.py         evaluation CLI and RAGAS integration

training/                 optional model adaptation

docs-tex/build-logs/      per-change engineering reports (LaTeX)
```

## Development

For repository development, install the additional test, linting, and evaluation dependencies:

```bash
pip install -r requirements-dev.txt
```

Run the automated tests with:

```bash
pytest -q
```

Check the codebase for linting issues with:

```bash
ruff check .
```

## License

AgentSouriva is available under the MIT License.
