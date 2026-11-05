# Features and Components

## Local document retrieval

Document chunks are indexed locally using FAISS.

The default `HashEmbeddings` backend uses deterministic feature hashing and requires no downloaded embedding weights. It favors lexical overlap and provides a lightweight replacement point for learned embedding backends.

## Grounded generation

Retrieved document chunks are supplied as evidence for the model rather than treated as trusted instructions.

Generated citation IDs are validated against the retrieved evidence before the answer is returned.

## Abstention

When the available evidence does not sufficiently support a document answer, the system can abstain rather than return an unsupported answer.

## Constrained tools

Agent actions are limited to explicitly approved tools. Retrieval and arithmetic remain separate from general model generation.

## Local-first model boundary

The default model and embedding backends can operate without a separately hosted model server.

For larger local models, AgentSouriva exposes an OpenAI-compatible model boundary. GPT-OSS-20B can be connected through any compatible serving setup without coupling the retrieval and grounding layers to a particular inference engine.

## Observable agent runs

Optional MLflow integration can record questions, retrieved evidence, scores, answers, citations, tool use, action traces, latency, and relevant configuration.

## Evaluation

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

## Approved Tool Surface

AgentSouriva keeps tool use explicit and restricted. The current tool set includes:

- Document search;

- Retrieval of a specific document chunk;

- Deterministic arithmetic.

Approved arithmetic is routed to the deterministic calculator instead of relying on model-generated arithmetic.

## Repository Structure

AgentSouriva distinguishes between the overall software project (`agent-souriva/`) and its importable Python package (`souriva/`). The project root contains the application package, tests, benchmarks, training utilities, documentation, datasets, and generated artifacts. The application package itself (`souriva/`) contains the core Python implementation, including application logic, runtime configuration, document processing, retrieval, model integration, and supporting components required for the agent’s operation. In other words, the project root organizes the complete software repository, whereas `souriva/` encapsulates the importable application implementation.

    app.py                    FastAPI interface

    souriva/
    |-- agent.py              action routing and orchestration
    |-- rag.py                loading, chunking, embeddings, FAISS, retrieval
    |-- model.py              model adapters
    |-- alignment.py          citation validation and abstention
    |-- tools.py              approved document tools and calculator
    |-- mcp_server.py         MCP interface
    |-- tracking.py           MLflow run and evaluation logging
    `-- evaluation.py         direct quality metrics

    benchmarks/
    `-- ragas_eval.py         evaluation CLI and RAGAS integration

    training/                 optional model adaptation

    docs-tex/build-logs/      per-change engineering reports (LaTeX)
