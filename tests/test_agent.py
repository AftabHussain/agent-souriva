from souriva.agent import Action, DocumentAgent
from souriva.model import Evidence, ModelReply
from souriva.tools import calculator


class StubRetriever:
    def __init__(self, evidence):
        self.evidence = evidence

    def search(self, query, top_k, min_score):
        return self.evidence


class StubModel:
    def answer(self, question, evidence):
        return ModelReply("Supported. [chunk-a]", ("chunk-a",))


def test_agent_uses_short_grounded_path():
    evidence = [Evidence("chunk-a", "Supported.", "doc.md", "chunk 1", 0.9)]
    result = DocumentAgent(StubRetriever(evidence), StubModel()).ask("Question?")
    assert result.actions == (Action.RETRIEVE, Action.ANSWER)
    assert not result.answer.abstained


def test_agent_abstains_before_model_without_evidence():
    result = DocumentAgent(StubRetriever([]), StubModel()).ask("Unknown?")
    assert result.actions == (Action.RETRIEVE, Action.ABSTAIN)
    assert result.answer.reason == "no_relevant_evidence"


def test_agent_routes_explicit_calculation_to_approved_tool():
    result = DocumentAgent(StubRetriever([]), StubModel(), calculator=calculator).ask("calculate: 6 * 7")
    assert result.actions == (Action.USE_TOOL, Action.ANSWER)
    assert result.answer.text == "The result is 42."


def test_agent_abstains_when_calculation_is_invalid():
    result = DocumentAgent(StubRetriever([]), StubModel(), calculator=calculator).ask("calculate: open('x')")
    assert result.actions == (Action.USE_TOOL, Action.ABSTAIN)
    assert result.answer.reason == "tool_error"

