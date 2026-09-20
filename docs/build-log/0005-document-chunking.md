# Metadata-preserving document chunking

## Change

Added bounded, overlapping text chunking with stable content-derived identifiers.

## Architecture

Chunking converts loaded document parts into the retrieval unit used by embeddings, FAISS, citations, and chunk lookup.

## Design notes

Chunks prefer whitespace boundaries and retain controlled overlap to preserve context across edges. IDs are stable hashes of source, location, and text, making citations reproducible across equivalent ingestions without a global counter.

## Verification

Compiled the modules, checked the diff, and added cases for overlap, metadata, stable IDs, and invalid sizing.

## Result

Loaded documents can now be split into deterministic, citation-ready chunks.
