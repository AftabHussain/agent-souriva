import numpy as np

from souriva.rag import HashEmbeddings


def test_hash_embeddings_are_normalized_and_deterministic():
    backend = HashEmbeddings(32)
    vectors = backend.embed(["alpha beta", "alpha beta", "unrelated terms"])

    assert vectors.shape == (3, 32)
    assert np.allclose(vectors[0], vectors[1])
    assert np.isclose(np.linalg.norm(vectors[0]), 1.0)
    assert np.dot(vectors[0], vectors[1]) > np.dot(vectors[0], vectors[2])


def test_hash_embeddings_handle_empty_batches():
    assert HashEmbeddings(16).embed([]).shape == (0, 16)

