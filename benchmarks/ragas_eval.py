import argparse
import json
from pathlib import Path

from souriva.agent import Action
from souriva.config import Settings
from souriva.evaluation import EvalCase, evaluate_cases
from souriva.rag import ingest_paths
from souriva.runtime import create_runtime
from souriva.tracking import log_evaluation


ROOT = Path(__file__).parents[1]


def load_cases(path: Path) -> list[EvalCase]:
    records = json.loads(path.read_text(encoding="utf-8"))
    return [
        EvalCase(
            question=item["question"],
            answerable=item["answerable"],
            expected_sources=tuple(item.get("expected_sources", [])),
            expected_action=Action(item["expected_action"])
            if item.get("expected_action")
            else None,
            reference=item.get("reference", ""),
        )
        for item in records
    ]


def run_ragas(rows: list[dict]) -> dict:
    """Run model-judged metrics only when explicitly requested."""
    from datasets import Dataset
    from ragas import evaluate
    from ragas.metrics import answer_relevancy, context_precision, context_recall, faithfulness

    dataset = Dataset.from_dict(
        {
            "question": [row["question"] for row in rows],
            "answer": [row["answer"] for row in rows],
            "contexts": [row["contexts"] for row in rows],
            "ground_truth": [row["reference"] for row in rows],
        }
    )
    result = evaluate(
        dataset,
        metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
    )
    return {name: float(value) for name, value in result.items()}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run AgentSouriva RAG evaluation")
    parser.add_argument("--ragas", action="store_true", help="run evaluator-model RAGAS metrics")
    parser.add_argument("--mlflow", action="store_true", help="record results with MLflow")
    args = parser.parse_args()
    settings = Settings(
        data_dir=ROOT / "artifacts" / "evaluation",
        model_backend="mock",
        mlflow_enabled=args.mlflow,
    )
    runtime = create_runtime(settings)
    documents = sorted((ROOT / "data" / "sample_docs").glob("*"))
    ingest_paths(runtime.store, documents, settings.chunk_size, settings.chunk_overlap)
    cases = load_cases(ROOT / "data" / "eval.json")
    direct, rows = evaluate_cases(runtime.agent, cases)
    output = {"direct": direct}
    if args.ragas:
        output["ragas"] = run_ragas(rows)
    logged_metrics = dict(direct)
    logged_metrics.update({f"ragas_{key}": value for key, value in output.get("ragas", {}).items()})
    log_evaluation(logged_metrics, rows, settings)
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
