# Grounded question API

## Change

Added `POST /ask` with typed answers, citations, abstention details, and action traces.

## Architecture

The endpoint delegates to the shared `DocumentAgent`, exposing alignment results without duplicating retrieval or grounding decisions in HTTP code.

## Design notes

Responses keep citations structured for clients while the answer text also retains inline chunk references. Abstentions use HTTP 200 because they are successful, policy-compliant outcomes rather than transport failures.

## Verification

Compiled the project, checked the diff, and extended API integration coverage for a cited document answer and an empty-corpus abstention.

## Result

The complete ingest, retrieve, and grounded-answer flow is available through FastAPI.
