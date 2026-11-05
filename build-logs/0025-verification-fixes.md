## Dependency-backed verification fixes

**Source commit:** [`4055d6f`](https://github.com/AftabHussain/agent-souriva/commit/4055d6f615adc129bfdf4d1ad936dde1fef7520b)

### Change

Included the API, benchmark, and training entry points in package discovery, excluded successful tool-only responses from the unsupported document-answer metric, normalized imports with Ruff, and used native async ASGI request handling and tests.

The principal packaging and metric corrections are visible in these focused lines:

    [tool.setuptools]
    py-modules = ["app"]
    [tool.setuptools.packages.find]
    include = ["souriva*", "benchmarks*", "training*"]

    unsupported_answer = (
        not result.answer.abstained
        and Action.USE_TOOL not in result.actions
        and not cited_ids
    )

Package discovery now installs every executable module, while the metric excludes successful calculator results because tool-only answers intentionally have no document citations. Converting the API handlers and ASGI tests to `async` completed the Python 3.14 compatibility fix.

### Architecture

Installed command modules and `app:app` now resolve outside a source checkout. Evaluation distinguishes grounded document claims from approved tool results, which do not require document citations.

### Design notes

The initial benchmark exposed the metric distinction: a correct calculator response had no document citation by design. It remains covered by tool-use accuracy and is no longer treated as an unsupported factual document answer. Native async ASGI requests avoid a Python 3.14 incompatibility in the deprecated synchronous test-client bridge.

### Verification

Installed core, development, and MCP dependencies into `.venv`. After the initial failures exposed these issues, ran `pytest -q` (37 passed), `ruff check .`, `ruff format --check .`, the direct benchmark, and imports for the API, MCP, and training entry points. All completed successfully. The benchmark measured 1.0 retrieval hit, citation correctness, abstention accuracy, and tool-use accuracy; unsupported-answer rate was 0.0. Latency is environment-dependent and printed by the run.

### Result

Packaged entry points and direct metrics now reflect their intended runtime semantics.
