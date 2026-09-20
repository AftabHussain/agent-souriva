# Retrieval API

## Change

Added typed evidence schemas and `POST /retrieve` for direct corpus search.

## Architecture

The endpoint exposes the same configured FAISS retriever used by the agent and MCP tools. Results preserve the stable chunk ID, text, source, location, and measured similarity score.

## Design notes

Query length and result count are bounded by request validation. The global relevance threshold is applied consistently so direct retrieval and agent decisions observe the same evidence floor.

## Verification

Compiled source and tests, checked the diff, and extended the ingestion integration test to restore and query the persisted corpus. Added request validation coverage for invalid `top_k`.

## Result

Clients can inspect ranked evidence independently of answer generation.
