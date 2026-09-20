# FastAPI runtime and health endpoint

## Change

Added centralized runtime construction and a FastAPI application with a health endpoint.

## Architecture

The runtime wires configuration, embeddings, persisted FAISS state, tools, model adapter, and agent in one place. The API imports that composition root rather than constructing components per request.

## Design notes

Startup restores an existing local index when present. Health reports readiness-relevant state without making model calls or exposing paths and credentials.

## Verification

Compiled all modules, checked the diff, and added an isolated API test for an empty temporary data directory.

## Result

`uvicorn app:app` can expose process health and confirm the selected backend and indexed chunk count.
