from souriva.agent import DocumentAgent
from souriva.evaluation import EvalCase, evaluate_cases
from souriva.model import Evidence, MockModel


class QueryRetriever:
    def search(self, query, top_k, min_score):
        if "known" not in query:
            return []
        return [Evidence("chunk-a", "A known fact.", "facts.md", "chunk 1", 0.8)]


def test_direct_evaluation_metrics_are_measured():
    agent = DocumentAgent(QueryRetriever(), MockModel())
    cases = [
        EvalCase("known question", True, ("facts.md",)),
        EvalCase("missing question", False),
    ]

    metrics, rows = evaluate_cases(agent, cases)

    assert metrics["retrieval_hit"] == 1
    assert metrics["citation_correct"] == 1
    assert metrics["unsupported_answer"] == 0
    assert metrics["abstention_correct"] == 1
    assert len(rows) == 2


def test_evaluation_rejects_empty_dataset():
    try:
        evaluate_cases(DocumentAgent(QueryRetriever(), MockModel()), [])
    except ValueError as exc:
        assert "At least one" in str(exc)
    else:
        raise AssertionError("empty evaluation dataset must fail")

