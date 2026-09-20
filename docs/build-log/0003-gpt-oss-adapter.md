# GPT-OSS-compatible model adapter

## Change

Added a small OpenAI-compatible HTTP adapter and backend selector.

## Architecture

GPT-OSS-20B serving is isolated behind the same `ModelAdapter` boundary as the mock. The adapter sends retrieved context to a chat-completions endpoint and returns a normalized reply.

## Design notes

The prompt marks retrieved text as untrusted data and requires evidence-only answers. Returned citation identifiers are intersected with retrieved chunk IDs so fabricated citations cannot enter the application response. A standard-library HTTP client avoids another core dependency.

## Verification

Ran module compilation and checked the diff. Factory unit tests cover both configured backends and invalid configuration; full test execution awaits development dependency installation.

## Result

A local GPT-OSS-20B server can later replace the mock through configuration without changes to agent logic.
