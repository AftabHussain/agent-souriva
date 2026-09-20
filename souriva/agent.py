from dataclasses import dataclass
from enum import StrEnum
from typing import Callable, Protocol

from souriva.alignment import ABSTENTION, GroundedAnswer, ground_reply
from souriva.model import Evidence, ModelAdapter


class Action(StrEnum):
    RETRIEVE = "RETRIEVE"
    USE_TOOL = "USE_TOOL"
    ANSWER = "ANSWER"
    ABSTAIN = "ABSTAIN"


class Retriever(Protocol):
    def search(self, query: str, top_k: int, min_score: float) -> list[Evidence]: ...


@dataclass(frozen=True)
class AgentResult:
    answer: GroundedAnswer
    evidence: tuple[Evidence, ...]
    actions: tuple[Action, ...]


class DocumentAgent:
    """Single-pass retrieve, answer, and verify flow."""

    def __init__(
        self,
        retriever: Retriever,
        model: ModelAdapter,
        top_k: int = 4,
        min_relevance: float = 0.18,
        calculator: Callable[[str], float] | None = None,
    ) -> None:
        self.retriever = retriever
        self.model = model
        self.top_k = top_k
        self.min_relevance = min_relevance
        self.calculator = calculator

    def ask(self, question: str) -> AgentResult:
        if question.lower().startswith("calculate:"):
            return self._calculate(question.partition(":")[2].strip())

        evidence = self.retriever.search(question, self.top_k, self.min_relevance)
        if not evidence:
            answer = GroundedAnswer(ABSTENTION, (), True, "no_relevant_evidence")
            return AgentResult(answer, (), (Action.RETRIEVE, Action.ABSTAIN))

        reply = self.model.answer(question, evidence)
        answer = ground_reply(reply, evidence, self.min_relevance)
        final_action = Action.ABSTAIN if answer.abstained else Action.ANSWER
        return AgentResult(answer, tuple(evidence), (Action.RETRIEVE, final_action))

    def _calculate(self, expression: str) -> AgentResult:
        if self.calculator is None:
            answer = GroundedAnswer(ABSTENTION, (), True, "tool_unavailable")
            return AgentResult(answer, (), (Action.USE_TOOL, Action.ABSTAIN))
        try:
            value = self.calculator(expression)
        except (SyntaxError, ValueError, ZeroDivisionError, OverflowError):
            answer = GroundedAnswer(ABSTENTION, (), True, "tool_error")
            return AgentResult(answer, (), (Action.USE_TOOL, Action.ABSTAIN))
        answer = GroundedAnswer(f"The result is {value:g}.", (), False)
        return AgentResult(answer, (), (Action.USE_TOOL, Action.ANSWER))
