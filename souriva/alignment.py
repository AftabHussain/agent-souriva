from dataclasses import dataclass
from typing import Sequence

from souriva.model import Evidence, ModelReply


ABSTENTION = "I do not have enough evidence to answer."


@dataclass(frozen=True)
class Citation:
    id: str
    source: str
    location: str
    score: float


@dataclass(frozen=True)
class GroundedAnswer:
    text: str
    citations: tuple[Citation, ...]
    abstained: bool
    reason: str | None = None


def ground_reply(
    reply: ModelReply, evidence: Sequence[Evidence], min_relevance: float
) -> GroundedAnswer:
    """Enforce evidence and citation invariants after model generation."""
    eligible = {item.id: item for item in evidence if item.score >= min_relevance}
    if not eligible:
        return GroundedAnswer(ABSTENTION, (), True, "insufficient_retrieval_score")

    if reply.text.strip() == ABSTENTION:
        return GroundedAnswer(ABSTENTION, (), True, "model_abstained")

    cited_ids = tuple(dict.fromkeys(reply.citation_ids))
    if not cited_ids or any(item_id not in eligible for item_id in cited_ids):
        return GroundedAnswer(ABSTENTION, (), True, "missing_or_invalid_citations")

    citations = tuple(
        Citation(item.id, item.source, item.location, item.score)
        for item_id in cited_ids
        if (item := eligible.get(item_id)) is not None
    )
    return GroundedAnswer(reply.text, citations, False)

