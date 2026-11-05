## Local embedding backend

**Source commit:** [`584e85c`](https://github.com/AftabHussain/agent-souriva/commit/584e85c3ddd8a389063acc9df814dbcff24b355c)

### Change

Added a deterministic, model-free embedding mechanism using *feature hashing*. The `HashEmbeddings` class converts text into fixed-dimensional numerical vectors without requiring a pretrained embedding model or external service. This makes it suitable for offline development, reproducible testing, and lightweight document retrieval. This allows the retrieval pipeline to be developed and tested without depending on external embedding models, making it easier to isolate implementation issues, establish a reproducible baseline, and evaluate individual system components before introducing more sophisticated semantic embeddings.

#### Embedding construction.

The `_embed_one()` method begins by initializing a zero-valued NumPy vector of the configured dimensionality (384 by default). It converts the input text to lowercase and extracts word-like tokens using the regular expression `TOKEN_PATTERN`. Each token is then mapped into the vector through the following procedure:

**Listing 4: Deterministic feature hashing and vector normalization**

```python
vector = np.zeros(self.dimensions, dtype="float32")
tokens = TOKEN_PATTERN.findall(text.lower())

for token in tokens:
    # Generate an 8-byte (64-bit) deterministic hash.
    digest = hashlib.blake2b(
        token.encode(), digest_size=8
    ).digest()

    # Convert the hash bytes into an integer.
    value = int.from_bytes(digest)

    # Map the token to a vector dimension using modulo.
    # Add +1 or -1 depending on the hash's lowest bit.
    vector[value % self.dimensions] += (
        1.0 if value & 1 else -1.0
    )

# Compute the Euclidean (L2) norm of the vector.
norm = np.linalg.norm(vector)

# Normalize nonzero vectors to unit length.
if norm:
    vector /= norm
```

The BLAKE2b hash function produces a reproducible 64-bit value for each token. Converting this hash into an integer allows two operations: `value % self.dimensions` selects the vector position using the modulo operator, while `value & 1` examines the lowest binary bit to determine whether to add $+1$ or $-1$. Repeated occurrences of a token accumulate at the same position. Different tokens may also map to the same dimension, a phenomenon known as a *hash collision*.

#### Vector normalization and similarity.

After processing all tokens, the resulting vector is normalized by its Euclidean norm:

$$\hat{\mathbf{v}} =
    \frac{\mathbf{v}}{\|\mathbf{v}\|_2}.$$

This produces a unit-length vector whenever the original vector is nonzero. Consequently, the inner product of two normalized vectors equals their cosine similarity:

$$\hat{\mathbf{u}}^\top\hat{\mathbf{v}}
    = \cos(\theta).$$

This is particularly relevant because AgentSouriva uses FAISS with an inner-product index (`faiss.IndexFlatIP`) for retrieval. Zero vectors are left unchanged to avoid division by zero.

#### Design rationale and limitations.

Unlike learned semantic embeddings, feature hashing does not capture contextual meaning or word order. It represents text through deterministic token-derived features, so similarity primarily reflects shared lexical features rather than semantic equivalence. Nevertheless, the approach is computationally inexpensive, requires no model download or training, and produces reproducible vectors for the same input and configuration. It therefore provides a useful baseline for testing AgentSouriva’s indexing, retrieval, and grounding pipeline independently of an external embedding model.

### Architecture

This backend supplies vectors to the FAISS index while keeping initial operation independent of network access and model downloads.

### Design notes

Token hashes select dimensions and signs, then vectors are L2-normalized for inner-product similarity. This baseline favors lexical overlap; the narrow `embed` interface can later be implemented by a learned embedding model without changing index behavior.

### Verification

Compiled source and tests and checked the diff. Unit cases cover determinism, shape, normalization, relative similarity, and empty batches.

### Result

AgentSouriva can produce repeatable local vectors suitable for FAISS cosine-style search.
