## MLflow agent-run tracking

**Source commit:** [`ee865aa`](https://github.com/AftabHussain/agent-souriva/commit/ee865aa696610a102e8096e729138030317b63fa)

### Change

Added centralized, opt-in MLflow logging around question requests.

The request boundary measures the whole agent call and submits the completed trace to the optional tracker:

    started = perf_counter()
    result = runtime.agent.ask(request.question)
    latency_ms = (perf_counter() - started) * 1000
    log_agent_run(request.question, result, latency_ms,
                  runtime.settings)

Tracking after completion captures latency and final behavior in one place; `log_agent_run` returns immediately when MLflow is disabled.

### Architecture

Tracking receives the completed agent result rather than instrumenting retrieval, models, or alignment separately. This keeps experiment concerns out of core behavior while retaining the full trace.

### Design notes

Each run records configuration, latency, abstention, evidence and scores, response, citations, actions, and tool use. MLflow tracking is disabled by default, so it is not required for normal AgentSouriva operation. If tracking is enabled without installing the optional MLflow dependencies, the application reports that the tracking extra must be installed.

### Verification

Compiled the code, checked the diff, and added a test confirming disabled tracking has no side effects or MLflow import requirement.

### Result

Setting `SOURIVA_MLFLOW_ENABLED=true` records query traces in the configured `baseline-rag` experiment.
