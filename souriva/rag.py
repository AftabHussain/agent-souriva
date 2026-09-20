from dataclasses import asdict, dataclass
import hashlib
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


def chunk_parts(
    parts: Iterable[DocumentPart], chunk_size: int = 900, overlap: int = 120
) -> list[Chunk]:
    if chunk_size < 1 or overlap < 0 or overlap >= chunk_size:
        raise ValueError("chunk_size must be positive and overlap smaller than chunk_size")

    chunks: list[Chunk] = []
    for part in parts:
        start = 0
        number = 1
        while start < len(part.text):
            end = min(start + chunk_size, len(part.text))
            if end < len(part.text):
                # Avoid cutting a word; a short backward search keeps chunk sizes predictable.
                boundary = part.text.rfind(" ", start + chunk_size // 2, end)
                end = boundary if boundary > start else end
            text = " ".join(part.text[start:end].split())
            if text:
                location = f"{part.location}, chunk {number}"
                digest = hashlib.sha256(f"{part.source}:{location}:{text}".encode()).hexdigest()[:12]
                chunks.append(Chunk(id=f"chunk-{digest}", text=text, source=part.source, location=location))
            if end == len(part.text):
                break
            start = end - overlap
            number += 1
    return chunks

