# MLflow evaluation tracking

## Change

Added MLflow recording for aggregate evaluation metrics and case-level outputs, with a CLI flag on the evaluation runner.

## Architecture

Evaluation tracking remains centralized beside agent-run tracking. The benchmark runner passes only measured metrics and observed case records after execution.

## Design notes

Direct and RAGAS metric names are kept distinct, configuration is recorded as parameters, and detailed cases are stored as one JSON artifact. Tracking remains opt-in through `--mlflow`.

## Verification

Compiled the project, checked the diff, and extended disabled-tracking coverage to ensure evaluation does not require MLflow unless requested.

## Result

Evaluation runs can be compared in the configured MLflow experiment without adding instrumentation to core RAG code.
