## Persistent FAISS index

**Source commit:** [`11737e5`](https://github.com/AftabHussain/agent-souriva/commit/11737e5383dfeecb3b0fdbc49ad2f7db491b7079)

### Change

Added exact inner-product indexing, metadata persistence, index restoration, and chunk lookup.

Replacing the corpus rebuilds the vector index and persists it with its metadata sidecar:

    def replace(self, chunks: Iterable[Chunk]) -> int:
        self.chunks = list(chunks)
        self.index = faiss.IndexFlatIP(self.embeddings.dimensions)
        if self.chunks:
            vectors = self.embeddings.embed(c.text for c in self.chunks)
            self.index.add(vectors)
        self.save()
        return self.count

Recreating `IndexFlatIP` makes replacement semantics explicit, while `save` writes both the FAISS data and the ordered chunk records needed to interpret its rows.

### Architecture

`FaissStore` owns the vector index and its ordered chunk sidecar. The sidecar retains citation fields that FAISS itself does not store.

### Design notes

Re-ingestion atomically replaces the logical corpus for predictable local behavior. Load validates both vector dimensions and row counts, preventing silent mismatches between the binary index and JSON metadata.

### Verification

Compiled source and tests and checked the diff. Added persistence, lookup, and missing-index test cases. Runtime execution requires the declared NumPy and FAISS dependencies.

### Result

Chunk vectors and citation metadata can now be saved locally and restored across process restarts.
