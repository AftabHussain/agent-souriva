from pathlib import Path

from souriva.rag import Chunk, FaissStore, HashEmbeddings, ingest_paths


def make_store(tmp_path: Path) -> FaissStore:
    return FaissStore(HashEmbeddings(64), tmp_path / "index.faiss", tmp_path / "index.json")


def test_search_returns_ranked_metadata(tmp_path: Path):
    store = make_store(tmp_path)
    store.replace(
        [
            Chunk("chunk-alpha", "alpha protocol authentication", "api.md", "chunk 1"),
            Chunk("chunk-beta", "beta hardware dimensions", "spec.txt", "chunk 1"),
        ]
    )

    results = store.search("alpha authentication", top_k=1)

    assert [result.id for result in results] == ["chunk-alpha"]
    assert results[0].source == "api.md"
    assert results[0].score > 0


def test_ingest_paths_replaces_corpus(tmp_path: Path):
    document = tmp_path / "guide.txt"
    document.write_text("Documented throughput is 40 requests per second.", encoding="utf-8")
    store = make_store(tmp_path)

    assert ingest_paths(store, [document], chunk_size=100, overlap=10) == 1
    assert store.search("throughput requests", min_score=0.1)[0].source == "guide.txt"


def test_search_applies_threshold(tmp_path: Path):
    store = make_store(tmp_path)
    store.replace([Chunk("chunk-a", "alpha", "a.txt", "chunk 1")])
    assert store.search("unrelated", min_score=0.1) == []

