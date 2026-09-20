from pathlib import Path

from pydantic import BaseModel, Field


class DocumentsRequest(BaseModel):
    paths: list[Path] = Field(min_length=1, max_length=100)


class IngestResponse(BaseModel):
    chunks: int
    sources: list[str]

