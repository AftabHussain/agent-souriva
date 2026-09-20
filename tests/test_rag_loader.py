from pathlib import Path

import pytest

from souriva.rag import load_document, load_documents


def test_loads_text_and_markdown(tmp_path: Path):
    text = tmp_path / "notes.txt"
    markdown = tmp_path / "guide.md"
    text.write_text("plain text", encoding="utf-8")
    markdown.write_text("# Guide\n\nDetails", encoding="utf-8")

    parts = load_documents([text, markdown])

    assert [part.source for part in parts] == ["notes.txt", "guide.md"]
    assert parts[1].text.startswith("# Guide")


def test_rejects_unsupported_documents(tmp_path: Path):
    path = tmp_path / "data.csv"
    path.write_text("a,b", encoding="utf-8")
    with pytest.raises(ValueError, match="Unsupported document type"):
        load_document(path)

