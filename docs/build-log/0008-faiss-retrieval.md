# FAISS retrieval

## Change

Added ranked vector search, score thresholding, and an ingestion pipeline function that joins loading, chunking, embedding, and index replacement.

## Architecture

The retriever converts FAISS positions back into evidence objects carrying source, location, score, text, and stable citation ID.

## Design notes

Search uses normalized embeddings with inner product, equivalent to cosine similarity. Empty queries and empty indexes return no evidence. A configurable minimum score provides the first explicit control for evidence adequacy.

## Verification

Compiled all modules, checked the diff, and added retrieval cases for ranking, metadata, thresholding, and end-to-end text ingestion.

## Result

AgentSouriva now has a complete local path from supported files to ranked, citation-ready evidence.
