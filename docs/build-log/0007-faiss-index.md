# Persistent FAISS index

## Change

Added exact inner-product indexing, metadata persistence, index restoration, and chunk lookup.

## Architecture

`FaissStore` owns the vector index and its ordered chunk sidecar. The sidecar retains citation fields that FAISS itself does not store.

## Design notes

Re-ingestion atomically replaces the logical corpus for predictable local behavior. Load validates both vector dimensions and row counts, preventing silent mismatches between the binary index and JSON metadata.

## Verification

Compiled source and tests and checked the diff. Added persistence, lookup, and missing-index test cases. Runtime execution requires the declared NumPy and FAISS dependencies.

## Result

Chunk vectors and citation metadata can now be saved locally and restored across process restarts.
