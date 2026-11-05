## Metadata-preserving document chunking

**Source commit:** [`98e802b`](https://github.com/AftabHussain/agent-souriva/commit/98e802b70d1c6312619060c4188592c818d4d1ef)

### Change

Added bounded, overlapping text chunking with stable content-derived identifiers.

Each emitted chunk receives location metadata and a deterministic digest:

    location = f"{part.location}, chunk {number}"
    digest = hashlib.sha256(
        f"{part.source}:{location}:{text}".encode()
    ).hexdigest()[:12]
    chunks.append(Chunk(id=f"chunk-{digest}", text=text,
                        source=part.source, location=location))

Hashing the source, location, and normalized text makes the identifier repeatable for equivalent content while the overlap loop preserves context between neighboring chunks.

### Architecture

Chunking converts loaded document parts into the retrieval unit used by embeddings, FAISS, citations, and chunk lookup.

### Design notes

Chunks prefer whitespace boundaries and retain controlled overlap to preserve context across edges. IDs are stable hashes of source, location, and text, making citations reproducible across equivalent ingestions without a global counter.

### Verification

Compiled the modules, checked the diff, and added cases for overlap, metadata, stable IDs, and invalid sizing.

### Result

Loaded documents can now be split into deterministic, citation-ready chunks.
