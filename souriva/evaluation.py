from collections.abc import Iterable
from dataclasses import dataclass
from statistics import mean
from time import perf_counter

from souriva.agent import Action, DocumentAgent


@dataclass(frozen=True)
class EvalCase:
    question: str
    answerable: bool
    expected_sources: tuple[str, ...] = ()
    expected_action: Action | None = None
    reference: str = ""


def evaluate_cases(agent: DocumentAgent, cases: Iterable[EvalCase]) -> tuple[dict, list[dict]]:
    """Measure direct system properties without an evaluator model."""
    rows: list[dict] = []
    for case in cases:
        started = perf_counter()
        result = agent.ask(case.question)
        latency_ms = (perf_counter() - started) * 1000
        retrieved_ids = {item.id for item in result.evidence}
        cited_ids = {item.id for item in result.answer.citations}
        retrieved_sources = {item.source for item in result.evidence}
        retrieval_hit = not case.expected_sources or bool(
            set(case.expected_sources) & retrieved_sources
        )
        rows.append(
            {
                "question": case.question,
                "answer": result.answer.text,
                "contexts": [item.text for item in result.evidence],
                "reference": case.reference,
                "retrieval_hit": retrieval_hit,
                "citation_correct": cited_ids <= retrieved_ids,
                "unsupported_answer": not result.answer.abstained
                and Action.USE_TOOL not in result.actions
                and not cited_ids,
                "abstention_correct": result.answer.abstained is not case.answerable,
                "tool_use_correct": case.expected_action is None
                or case.expected_action in result.actions,
                "latency_ms": latency_ms,
            }
        )
    if not rows:
        raise ValueError("At least one evaluation case is required")

    boolean_metrics = (
        "retrieval_hit",
        "citation_correct",
        "unsupported_answer",
        "abstention_correct",
        "tool_use_correct",
    )
    metrics = {name: mean(float(row[name]) for row in rows) for name in boolean_metrics}
    metrics["latency_ms"] = mean(row["latency_ms"] for row in rows)
    return metrics, rows
