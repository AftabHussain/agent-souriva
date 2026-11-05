# Models and Runtime Configuration

## Local and External Model Boundaries

The default model and embedding backends can operate without a separately hosted model server. For larger local models, AgentSouriva exposes an OpenAI-compatible model boundary. GPT-OSS-20B can be connected through any compatible serving setup without coupling the retrieval and grounding layers to a particular inference engine.

## GPT-OSS-20B

AgentSouriva can connect to GPT-OSS-20B through an OpenAI-compatible model server. The configured model server must implement `POST /v1/chat/completions`.

In AgentSouriva, the adapter implements the `ModelAdapter` Python protocol, which provides a common interface between the agent’s internal question-and-evidence representation and different answer-generation backends. The `OpenAICompatibleModel` adapter translates questions and retrieved evidence into OpenAI-compatible chat-completions API requests, sends them to the configured model server, and converts the responses, including generated text and referenced chunk identifiers, into AgentSouriva’s `ModelReply` structure. The local `MockModel` follows the same protocol but operates without a model server. By relying on this shared interface, the agent keeps its application logic, retrieval, and grounding mechanisms independent of the underlying model-serving implementation.

Without an external model server, the default mock backend provides deterministic extractive responses for local operation and testing.

## Runtime Settings and Configuration Interface

Runtime settings use the `SOURIVA_` prefix. The application reads configuration during startup. The following values are shown as configuration examples in the source README, not asserted as deployment defaults.

| Setting                   | Source README example        | Role                                   |
|:--------------------------|:-----------------------------|:---------------------------------------|
| `SOURIVA_DATA_DIR`        | `./artifacts`                | Persisted index and runtime artifacts  |
| `SOURIVA_CHUNK_SIZE`      | `900`                        | Chunk-size setting                     |
| `SOURIVA_CHUNK_OVERLAP`   | `120`                        | Overlap between text chunks            |
| `SOURIVA_RETRIEVAL_TOP_K` | `4`                          | Number of retrieved chunks             |
| `SOURIVA_MIN_RELEVANCE`   | `0.18`                       | Minimum evidence-relevance threshold   |
| `SOURIVA_MODEL_BACKEND`   | `openai-compatible`          | Model-backend selector                 |
| `SOURIVA_MODEL_BASE_URL`  | `http://localhost:``8001/v1` | Model server API base URL              |
| `SOURIVA_MODEL_NAME`      | `openai/gpt-oss-20b`         | Model identifier                       |
| `SOURIVA_MODEL_API_KEY`   | `local`                      | API key supplied to the model endpoint |

## Runtime Environment

The source README specifies Python 3.11 or newer. Runtime, evaluation, tracking, MCP, and training capabilities have distinct dependency requirements, as detailed in the chronological build logs.
