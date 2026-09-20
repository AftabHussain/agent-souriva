import pytest

from training.sft import format_trace


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

