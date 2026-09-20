# MLflow agent-run tracking

## Change

Added centralized, opt-in MLflow logging around question requests.

## Architecture

Tracking receives the completed agent result rather than instrumenting retrieval, models, or alignment separately. This keeps experiment concerns out of core behavior while retaining the full trace.

## Design notes

Each run records configuration, latency, abstention, evidence and scores, response, citations, actions, and tool use. Tracking defaults off so the core install remains light; enabling it without the dependency produces a direct installation message.

## Verification

Compiled the code, checked the diff, and added a test confirming disabled tracking has no side effects or MLflow import requirement.

## Result

Setting `SOURIVA_MLFLOW_ENABLED=true` records query traces in the configured `baseline-rag` experiment.
