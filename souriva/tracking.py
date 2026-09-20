from dataclasses import asdict

from souriva.agent import AgentResult
from souriva.config import Settings


def log_agent_run(
    question: str, result: AgentResult, latency_ms: float, settings: Settings
) -> None:
    """Record one complete agent trace when MLflow tracking is enabled."""
    if not settings.mlflow_enabled:
        return

    try:
        import mlflow
    except ImportError as exc:
        raise RuntimeError("Install AgentSouriva with the 'tracking' extra") from exc

    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
    mlflow.set_experiment(settings.mlflow_experiment)
    trace = {
        "question": question,
        "retrieved_chunks": [asdict(item) for item in result.evidence],
        "model_response": result.answer.text,
        "citations": [asdict(item) for item in result.answer.citations],
        "tool_calls": [action.value for action in result.actions if action.value == "USE_TOOL"],
        "actions": [action.value for action in result.actions],
    }
    with mlflow.start_run(run_name="agent-query"):
        mlflow.log_params(
            {
                "model_backend": settings.model_backend,
                "model_name": settings.model_name,
                "top_k": settings.retrieval_top_k,
                "min_relevance": settings.min_relevance,
            }
        )
        mlflow.log_metrics(
            {
                "latency_ms": latency_ms,
                "retrieved_chunks": len(result.evidence),
                "abstained": float(result.answer.abstained),
            }
        )
        mlflow.log_dict(trace, "trace.json")


def log_evaluation(metrics: dict[str, float], rows: list[dict], settings: Settings) -> None:
    """Record aggregate measurements and case-level outputs in one MLflow run."""
    if not settings.mlflow_enabled:
        return
    try:
        import mlflow
    except ImportError as exc:
        raise RuntimeError("Install AgentSouriva with the 'tracking' extra") from exc

    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
    mlflow.set_experiment(settings.mlflow_experiment)
    with mlflow.start_run(run_name="evaluation"):
        mlflow.log_params(
            {
                "model_backend": settings.model_backend,
                "top_k": settings.retrieval_top_k,
                "min_relevance": settings.min_relevance,
                "cases": len(rows),
            }
        )
        mlflow.log_metrics(metrics)
        mlflow.log_dict({"cases": rows}, "evaluation.json")
