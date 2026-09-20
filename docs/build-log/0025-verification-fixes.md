# Dependency-backed verification fixes

## Change

Included the API, benchmark, and training entry points in package discovery, excluded successful tool-only responses from the unsupported document-answer metric, normalized imports with Ruff, and used native async ASGI request handling and tests.

## Architecture

Installed command modules and `app:app` now resolve outside a source checkout. Evaluation distinguishes grounded document claims from approved tool results, which do not require document citations.

## Design notes

The initial benchmark exposed the metric distinction: a correct calculator response had no document citation by design. It remains covered by tool-use accuracy and is no longer treated as an unsupported factual document answer. Native async ASGI requests avoid a Python 3.14 incompatibility in the deprecated synchronous test-client bridge.

## Verification

Installed core, development, and MCP dependencies into `.venv`. After the initial failures exposed these issues, ran `pytest -q` (37 passed), `ruff check .`, `ruff format --check .`, the direct benchmark, and imports for the API, MCP, and training entry points. All completed successfully. The benchmark measured 1.0 retrieval hit, citation correctness, abstention accuracy, and tool-use accuracy; unsupported-answer rate was 0.0. Latency is environment-dependent and printed by the run.

## Result

Packaged entry points and direct metrics now reflect their intended runtime semantics.
