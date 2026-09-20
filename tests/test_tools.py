from pathlib import Path

import pytest

from souriva.rag import Chunk, FaissStore, HashEmbeddings
from souriva.tools import DocumentTools, calculator


def test_calculator_supports_arithmetic():
    assert calculator("(40 * 3) / 2") == 60
    assert calculator("2 ** 3") == 8


def test_calculator_rejects_code_execution():
    with pytest.raises(ValueError, match="numeric arithmetic"):
        calculator("__import__('os').getcwd()")


def test_document_tools_expose_store_operations(tmp_path: Path):
    store = FaissStore(HashEmbeddings(16), tmp_path / "i.faiss", tmp_path / "i.json")
    store.replace([Chunk("chunk-a", "alpha throughput", "api.md", "chunk 1")])
    tools = DocumentTools(store)

    assert tools.search_documents("alpha")[0]["id"] == "chunk-a"
    assert tools.get_document_chunk("chunk-a")["source"] == "api.md"
    assert tools.get_document_chunk("missing") is None
