import pytest

from training.sft import format_trace
from training.rl import RewardSignals, grounded_reward, preference_record


def test_sft_trace_contains_action_answer_and_citations():
    text = format_trace(
        {
            "question": "What is documented?",
            "retrieved_context": ["Supported fact."],
            "desired_action": "ANSWER",
            "grounded_answer": "A supported fact.",
            "citations": ["chunk-a"],
        }
    )
    assert "Action: ANSWER" in text
    assert "[chunk-a]" in text


def test_sft_trace_validates_required_fields():
    with pytest.raises(ValueError, match="missing fields"):
        format_trace({"question": "Incomplete"})


def test_grounded_reward_prefers_supported_behavior():
    good = RewardSignals(True, True, True, True)
    bad = RewardSignals(False, False, False, False, invented_citation=True, unsupported_claim=True)
    assert grounded_reward(good) > grounded_reward(bad)
    pair = preference_record(
        {"prompt": "Question", "response": "Supported"},
        {"prompt": "Question", "response": "Invented"},
        good,
    )
    assert pair["chosen"] == "Supported"

