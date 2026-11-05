## MLflow evaluation tracking

**Source commit:** [`5458832`](https://github.com/AftabHussain/agent-souriva/commit/5458832e70cd1092a5f234cd7c72719a6e1a7635)

### Change

Added MLflow recording for aggregate evaluation metrics and case-level outputs, with a CLI flag on the evaluation runner.

One MLflow run stores summary measurements alongside the full case records:

    with mlflow.start_run(run_name="evaluation"):
        mlflow.log_params({
            "model_backend": settings.model_backend,
            "top_k": settings.retrieval_top_k,
            "cases": len(rows),
        })
        mlflow.log_metrics(metrics)
        mlflow.log_dict({"cases": rows}, "evaluation.json")

The aggregate values support run comparison, while the JSON artifact retains the evidence needed to audit each score.

### Architecture

Evaluation tracking remains centralized beside agent-run tracking. The benchmark runner passes only measured metrics and observed case records after execution.

### Design notes

Direct and RAGAS metric names are kept distinct, configuration is recorded as parameters, and detailed cases are stored as one JSON artifact. Tracking remains opt-in through `--mlflow`.

### Verification

Compiled the project, checked the diff, and extended disabled-tracking coverage to ensure evaluation does not require MLflow unless requested.

### Result

Evaluation runs can be compared in the configured MLflow experiment without adding instrumentation to core RAG code.
