## FAISS retrieval

**Source commit:** [`a6703bc`](https://github.com/AftabHussain/agent-souriva/commit/a6703bcecde6da3c19bdc9110fd3792eaa10ccc0)

### Change

Added ranked vector search, score thresholding, and an ingestion pipeline function that joins loading, chunking, embedding, and index replacement.

The search path converts FAISS positions back into source-aware evidence and applies the relevance floor:

    scores, positions = self.index.search(query_vector, limit)
    for score, position in zip(scores[0], positions[0]):
        if position < 0 or float(score) < min_score:
            continue
        chunk = self.chunks[int(position)]
        results.append(Evidence(id=chunk.id, text=chunk.text,
                                source=chunk.source,
                                location=chunk.location,
                                score=round(float(score), 6)))

FAISS supplies scores and row positions; the sidecar supplies the text and citation metadata returned to callers.

### Architecture

The retriever converts FAISS positions back into evidence objects carrying source, location, score, text, and stable citation ID.

### Design notes

Search uses normalized embeddings with inner product, equivalent to cosine similarity. Empty queries and empty indexes return no evidence. A configurable minimum score provides the first explicit control for evidence adequacy.

### Verification

Compiled all modules, checked the diff, and added retrieval cases for ranking, metadata, thresholding, and end-to-end text ingestion.

### Result

AgentSouriva now has a complete local path from supported files to ranked, citation-ready evidence.
