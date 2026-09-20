from pathlib import Path

from souriva.rag import Chunk, FaissStore, HashEmbeddings


def test_faiss_store_persists_chunks(tmp_path: Path):
    chunks = [Chunk("chunk-a", "alpha content", "a.md", "document, chunk 1")]
    store = FaissStore(HashEmbeddings(16), tmp_path / "index.faiss", tmp_path / "index.json")

    assert store.replace(chunks) == 1
    restored = FaissStore(HashEmbeddings(16), store.index_path, store.metadata_path)

    assert restored.load()
    assert restored.get("chunk-a") == chunks[0]


def test_missing_store_load_is_clean(tmp_path: Path):
    store = FaissStore(HashEmbeddings(16), tmp_path / "missing.faiss", tmp_path / "missing.json")
    assert not store.load()
    assert store.count == 0
