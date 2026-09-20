from pathlib import Path

from pydantic import BaseModel, Field


class DocumentsRequest(BaseModel):
    paths: list[Path] = Field(min_length=1, max_length=100)


class IngestResponse(BaseModel):
    chunks: int
    sources: list[str]


class RetrieveRequest(BaseModel):
    query: str = Field(min_length=1, max_length=4000)
    top_k: int = Field(default=4, ge=1, le=20)


class EvidenceResponse(BaseModel):
    id: str
    text: str
    source: str
    location: str
    score: float


class RetrieveResponse(BaseModel):
    evidence: list[EvidenceResponse]

