# Agent calculator routing

## Change

Added an explicit calculator route to the document agent and completed behavior for all four agent actions.

## Architecture

Questions prefixed with `calculate:` take a bounded tool path. The calculator is injected as a callable, keeping the agent unaware of MCP transport and limiting tool access to an approved function.

## Design notes

Tool requests do not enter retrieval or the model. Expected parsing and arithmetic failures become a standardized abstention, while successful calculations are returned with a `USE_TOOL`, `ANSWER` trace and no document citations.

## Verification

Compiled source and tests, checked the diff, and added cases for successful and rejected calculator requests.

## Result

The agent now executes retrieval, approved tool use, answers, and abstentions through short deterministic paths.
