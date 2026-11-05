## Preference optimization reward contract

**Source commit:** [`63cd6be`](https://github.com/AftabHussain/agent-souriva/commit/63cd6bed2f3f4c2139374b8371e11ae48365b66d)

### Change

Added a trainer-neutral reward function and preference-pair record for future RL or direct preference optimization.

The reward makes the desired grounding behavior and its penalties explicit:

    reward = 0.0
    reward += 1.5 if signals.supported_answer else 0.0
    reward += 1.0 if signals.citations_correct else 0.0
    reward += 0.75 if signals.tool_use_correct else 0.0
    reward += 1.0 if signals.abstention_correct else 0.0
    reward -= 2.0 if signals.unsupported_claim else 0.0
    reward -= 1.5 if signals.invented_citation else 0.0

Keeping the weights in a plain function makes the initial preference contract inspectable and independent of any particular trainer.

### Architecture

The module converts measurable grounding outcomes into a scalar reward outside the runtime agent. A downstream TRL trainer can consume the normalized prompt, chosen response, and rejected response without changing evaluation logic.

### Design notes

Supported answers, valid citations, correct tools, and correct abstentions receive positive weight. Unsupported claims and invented citations receive the strongest penalties, with a smaller penalty for unnecessary tool calls. The explicit weights are a baseline to calibrate from observed preference data.

### Verification

Compiled the project, checked the diff, and added a test confirming supported behavior scores above an unsupported answer and produces the expected preference record. No optimization result is claimed or fabricated.

### Result

The project has a concrete data and reward boundary for later RL or preference optimization without adding it to the initial runtime.
