import hashlib
import json
import re
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from pathlib import Path

import faiss
import numpy as np

from souriva.model import Evidence

SUPPORTED_SUFFIXES = {".pdf", ".md", ".markdown", ".txt"}
TOKEN_PATTERN = re.compile(r"[a-z0-9][a-z0-9_-]+")


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
    # Function inputs and output:
    # - parts: Iterable[DocumentPart] means any collection/iterator of DocumentPart
    #   objects that can be traversed with `for` (e.g., a list or generator).
    # - chunk_size: target MAXIMUM number of source-text characters per chunk.
    # - overlap: number of source-text characters reused between neighboring chunks.
    # - `-> list[Chunk]` in the signature is a return-type annotation: this function
    #   returns a list of Chunk objects, but Python does not enforce the hint itself.
    #
    # Validate arguments before processing. nonpositive chunk size, negative overlap, or 
    # overlap >= chunk size.
    if chunk_size < 1 or overlap < 0 or overlap >= chunk_size:
        # `raise` stops execution and reports invalid caller input.
        raise ValueError("chunk_size must be positive and overlap smaller than chunk_size")

    # Start an empty output list. `: list[Chunk]` is a variable type annotation.
    chunks: list[Chunk] = []
    # Each DocumentPart contains text plus its source and location (e.g., PDF page).
    for part in parts:
        # `start` is the zero-based character index where the next chunk begins.
        start = 0
        # Number chunks separately within EACH document part, starting at 1.
        number = 1
        while start < len(part.text):
            # Propose an end position at most `chunk_size` characters after `start`.
            # `min(...)` prevents the slice from extending past the end of the text if the text 
            # is less than the chunk size
            end = min(start + chunk_size, len(part.text))
            # If this is NOT the final chunk, try to end at a space so a word
            # isn't cut between adjacent chunks.
            if end < len(part.text):
                # Avoid cutting a word; a short backward search keeps chunk sizes predictable.
                # `//` is integer (floor) division: chunk_size // 2 is half the
                # target chunk size rounded down. The search begins halfway in,
                # encouraging reasonably sized chunks rather than very short ones.
                # str.rfind(" ", lo, hi) finds the LAST space in [lo, hi), returning
                # its character index, or -1 if no space exists in that interval.
                boundary = part.text.rfind(" ", start + chunk_size // 2, end)
                # Conditional expression: X if condition else Y.
                # Use the space as the chunk boundary only if it is after `start`;
                # otherwise keep the original end (which may split a long word).
                end = boundary if boundary > start else end
            # Slice out the characters from start (inclusive) to end (exclusive).
            # `.split()` splits on whitespace and discards repeated whitespace.
            # `" ".join(...)` joins the pieces with single spaces, normalizing
            # spaces, tabs, and newlines in the stored chunk text.
            text = " ".join(part.text[start:end].split())
            # Empty strings are false in Python; skip chunks with no visible text.
            if text:
                # An f-string inserts the current source location and chunk number
                # into a readable label (e.g., "page 2, chunk 3").
                location = f"{part.location}, chunk {number}"
                # Create a reproducible, content-dependent identifier:
                # 1. Combine source filename, location label, and normalized text.
                # 2. `.encode()` converts the string to UTF-8 bytes for SHA-256.
                # 3. `.hexdigest()` turns the hash into hexadecimal characters.
                # 4. `[:12]` keeps only its first 12 hex characters, making the ID
                #    short. Truncation makes collisions more likely than with full SHA-256.
                digest = hashlib.sha256(f"{part.source}:{location}:{text}".encode()).hexdigest()[
                    :12
                ]
                # Create one Chunk dataclass instance and add it to the result list.
                # Its metadata allows retrieved text to be traced to its source.
                chunks.append(
                    Chunk(id=f"chunk-{digest}", text=text, source=part.source, location=location)
                )
            # If this chunk reached the end of the part, there is nothing left
            # to process. Exit the `while` loop using `break`.
            if end == len(part.text):
                break
            # Move the next window forward, but back up by `overlap` characters.
            # E.g., with end=900 and overlap=120, the next chunk starts at 780,
            # repeating source characters 780..899 to preserve nearby context.
            # Note: very large overlaps plus early word boundaries can cause
            # insufficient forward progress; typical settings keep overlap small.
            start = end - overlap
            # `+= 1` means `number = number + 1` for the next chunk label.
            number += 1
    # Return the accumulated list of Chunk objects for all input parts.
    return chunks


class HashEmbeddings:
    """Small deterministic embedding backend requiring no model download."""

    def __init__(self, dimensions: int = 384) -> None:
        if dimensions < 8:
            raise ValueError("embedding dimensions must be at least 8")
        self.dimensions = dimensions

    def embed(self, texts: Iterable[str]) -> np.ndarray:
        vectors = [self._embed_one(text) for text in texts]
        if not vectors:
            return np.empty((0, self.dimensions), dtype="float32")
        return np.stack(vectors)

    def _embed_one(self, text: str) -> np.ndarray:
        vector = np.zeros(self.dimensions, dtype="float32")
        tokens = TOKEN_PATTERN.findall(text.lower())
        for token in tokens:
            digest = hashlib.blake2b(token.encode(), digest_size=8).digest()
            value = int.from_bytes(digest)
            vector[value % self.dimensions] += 1.0 if value & 1 else -1.0
        norm = np.linalg.norm(vector)
        if norm:
            vector /= norm
        return vector


class FaissStore:
    """Persistent exact inner-product index with sidecar chunk metadata."""

    def __init__(self, embeddings: HashEmbeddings, index_path: Path, metadata_path: Path) -> None:
        self.embeddings = embeddings
        self.index_path = index_path
        self.metadata_path = metadata_path
        self.index = faiss.IndexFlatIP(embeddings.dimensions)
        self.chunks: list[Chunk] = []

    @property
    def count(self) -> int:
        return len(self.chunks)

    def replace(self, chunks: Iterable[Chunk]) -> int:
        self.chunks = list(chunks)
        self.index = faiss.IndexFlatIP(self.embeddings.dimensions)
        if self.chunks:
            self.index.add(self.embeddings.embed(chunk.text for chunk in self.chunks))
        self.save()
        return self.count

    def save(self) -> None:
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(self.index_path))
        payload = [chunk.to_dict() for chunk in self.chunks]
        self.metadata_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def load(self) -> bool:
        if not self.index_path.exists() or not self.metadata_path.exists():
            return False
        index = faiss.read_index(str(self.index_path))
        if index.d != self.embeddings.dimensions:
            raise ValueError("Stored index dimensions do not match embedding configuration")
        chunks = [
            Chunk(**item) for item in json.loads(self.metadata_path.read_text(encoding="utf-8"))
        ]
        if index.ntotal != len(chunks):
            raise ValueError("FAISS index and metadata count do not match")
        self.index, self.chunks = index, chunks
        return True

    def get(self, chunk_id: str) -> Chunk | None:
        return next((chunk for chunk in self.chunks if chunk.id == chunk_id), None)

    def search(self, query: str, top_k: int = 4, min_score: float = 0.0) -> list[Evidence]:
        if not query.strip() or top_k < 1 or not self.chunks:
            return []
        query_vector = self.embeddings.embed([query])
        limit = min(top_k, self.count)
        scores, positions = self.index.search(query_vector, limit)
        results: list[Evidence] = []
        for score, position in zip(scores[0], positions[0]):
            if position < 0 or float(score) < min_score:
                continue
            chunk = self.chunks[int(position)]
            results.append(
                Evidence(
                    id=chunk.id,
                    text=chunk.text,
                    source=chunk.source,
                    location=chunk.location,
                    score=round(float(score), 6),
                )
            )
        return results


def ingest_paths(store: FaissStore, paths: Iterable[Path], chunk_size: int, overlap: int) -> int:
    parts = load_documents(paths)
    return store.replace(chunk_parts(parts, chunk_size=chunk_size, overlap=overlap))
