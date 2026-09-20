# Grounded agent flow

## Change

Added the single-pass document agent and explicit action trace.

## Architecture

The agent coordinates retrieval, model generation, and alignment without owning their implementation. Its trace uses the four conceptual actions `RETRIEVE`, `USE_TOOL`, `ANSWER`, and `ABSTAIN`.

## Design notes

Document questions take the shortest path: one retrieval, at most one model call, then a grounding decision. No evidence causes an immediate abstention, avoiding unnecessary model work and reducing the chance of unsupported answers.

## Verification

Compiled modules, checked the diff, and added isolated tests for the successful grounded path and pre-generation abstention path.

## Result

The core can now coordinate retrieval and generation into a validated, traceable answer.
