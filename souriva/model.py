from dataclasses import dataclass
from typing import Protocol, Sequence


@dataclass(frozen=True)
class Evidence:
    id: str
    text: str
    source: str
    location: str
    score: float


@dataclass(frozen=True)
class ModelReply:
    text: str
    citation_ids: tuple[str, ...] = ()


class ModelAdapter(Protocol):
    """Boundary implemented by local mocks and production model servers."""

    def answer(self, question: str, evidence: Sequence[Evidence]) -> ModelReply: ...


class MockModel:
    """Deterministic extractive backend for offline development and tests."""

    def answer(self, question: str, evidence: Sequence[Evidence]) -> ModelReply:
        del question
        if not evidence:
            return ModelReply("I do not have enough evidence to answer.")

        selected = evidence[:2]
        statements = [self._first_sentence(item.text) for item in selected]
        citations = tuple(item.id for item in selected)
        rendered = " ".join(
            f"{statement} [{citation}]" for statement, citation in zip(statements, citations)
        )
        return ModelReply(rendered, citations)

    @staticmethod
    def _first_sentence(text: str) -> str:
        line = " ".join(text.split())
        stop = line.find(". ")
        return line if stop < 0 else line[: stop + 1]

