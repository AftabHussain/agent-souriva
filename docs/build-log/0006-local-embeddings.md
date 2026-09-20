# Local embedding backend

## Change

Added deterministic normalized feature-hashing embeddings.

## Architecture

This backend supplies vectors to the FAISS index while keeping initial operation independent of network access and model downloads.

## Design notes

Token hashes select dimensions and signs, then vectors are L2-normalized for inner-product similarity. This baseline favors lexical overlap; the narrow `embed` interface can later be implemented by a learned embedding model without changing index behavior.

## Verification

Compiled source and tests and checked the diff. Unit cases cover determinism, shape, normalization, relative similarity, and empty batches.

## Result

AgentSouriva can produce repeatable local vectors suitable for FAISS cosine-style search.
