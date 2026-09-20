# Document ingestion API

## Change

Added validated request and response schemas and `POST /documents` for local file ingestion.

## Architecture

The endpoint is a thin adapter over the RAG ingestion pipeline and shared runtime store. It accepts server-local paths for PDF, Markdown, and text files and replaces the active corpus.

## Design notes

Batch size is bounded at the schema. Expected file and format errors become HTTP 400 responses while unexpected failures remain visible. Responses report the resulting chunk count and submitted source names.

## Verification

Compiled the code, checked the diff, and added API cases for successful text ingestion and a missing path.

## Result

Clients can build the local FAISS corpus through a typed HTTP request.
