import pytest

from souriva.rag import DocumentPart, chunk_parts


def test_chunks_preserve_metadata_and_overlap():
    part = DocumentPart("alpha beta gamma delta epsilon", "notes.txt", "document")

    chunks = chunk_parts([part], chunk_size=17, overlap=5)

    assert len(chunks) == 3
    assert chunks[0].source == "notes.txt"
    assert chunks[0].location == "document, chunk 1"
    assert chunks[0].id.startswith("chunk-")
    assert set(chunks[0].text.split()) & set(chunks[1].text.split())


def test_chunk_ids_are_stable():
    part = DocumentPart("stable content", "notes.txt", "document")
    assert chunk_parts([part])[0].id == chunk_parts([part])[0].id


def test_rejects_invalid_chunk_configuration():
    with pytest.raises(ValueError, match="overlap smaller"):
        chunk_parts([], chunk_size=10, overlap=10)
