from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


SUPPORTED_SUFFIXES = {".pdf", ".md", ".markdown", ".txt"}


@dataclass(frozen=True)
class DocumentPart:
    text: str
    source: str
    location: str


@dataclass(frozen=True)
class Chunk:
    id: str
    text: str
    source: str
    location: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


def load_document(path: Path) -> list[DocumentPart]:
    """Extract source-aware parts from one supported document."""
    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_SUFFIXES:
        raise ValueError(f"Unsupported document type: {suffix or 'none'}")
    if not path.is_file():
        raise FileNotFoundError(path)

    if suffix == ".pdf":
        from pypdf import PdfReader

        return [
            DocumentPart(text=text, source=path.name, location=f"page {number}")
            for number, page in enumerate(PdfReader(path).pages, start=1)
            if (text := (page.extract_text() or "").strip())
        ]

    text = path.read_text(encoding="utf-8").strip()
    return [DocumentPart(text=text, source=path.name, location="document")] if text else []


def load_documents(paths: Iterable[Path]) -> list[DocumentPart]:
    parts: list[DocumentPart] = []
    for path in paths:
        parts.extend(load_document(path))
    return parts

