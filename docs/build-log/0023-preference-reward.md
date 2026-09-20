# Preference optimization reward contract

## Change

Added a trainer-neutral reward function and preference-pair record for future RL or direct preference optimization.

## Architecture

The module converts measurable grounding outcomes into a scalar reward outside the runtime agent. A downstream TRL trainer can consume the normalized prompt, chosen response, and rejected response without changing evaluation logic.

## Design notes

Supported answers, valid citations, correct tools, and correct abstentions receive positive weight. Unsupported claims and invented citations receive the strongest penalties, with a smaller penalty for unnecessary tool calls. The explicit weights are a baseline to calibrate from observed preference data.

## Verification

Compiled the project, checked the diff, and added a test confirming supported behavior scores above an unsupported answer and produces the expected preference record. No optimization result is claimed or fabricated.

## Result

The project has a concrete data and reward boundary for later RL or preference optimization without adding it to the initial runtime.
