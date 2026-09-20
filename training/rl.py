from dataclasses import dataclass


@dataclass(frozen=True)
class RewardSignals:
    supported_answer: bool
    citations_correct: bool
    tool_use_correct: bool
    abstention_correct: bool
    invented_citation: bool = False
    unnecessary_tool_call: bool = False
    unsupported_claim: bool = False


def grounded_reward(signals: RewardSignals) -> float:
    """Transparent starting reward for future preference optimization."""
    reward = 0.0
    reward += 1.5 if signals.supported_answer else 0.0
    reward += 1.0 if signals.citations_correct else 0.0
    reward += 0.75 if signals.tool_use_correct else 0.0
    reward += 1.0 if signals.abstention_correct else 0.0
    reward -= 2.0 if signals.unsupported_claim else 0.0
    reward -= 1.5 if signals.invented_citation else 0.0
    reward -= 0.5 if signals.unnecessary_tool_call else 0.0
    return reward


def preference_record(chosen: dict, rejected: dict, signals: RewardSignals) -> dict:
    """Create a trainer-neutral pair while retaining its measurable reward."""
    return {
        "prompt": chosen["prompt"],
        "chosen": chosen["response"],
        "rejected": rejected["response"],
        "reward": grounded_reward(signals),
    }

