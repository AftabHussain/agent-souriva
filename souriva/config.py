from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment or a local .env file."""

    model_config = SettingsConfigDict(env_prefix="SOURIVA_", env_file=".env", extra="ignore")

    data_dir: Path = Path("artifacts")
    index_name: str = "documents"
    embedding_dimensions: int = 384
    chunk_size: int = 900
    chunk_overlap: int = 120
    retrieval_top_k: int = 4
    min_relevance: float = 0.18
    model_backend: Literal["mock", "openai-compatible"] = "mock"
    model_base_url: str = "http://localhost:8001/v1"
    model_name: str = "openai/gpt-oss-20b"
    model_api_key: str = "local"
    mlflow_tracking_uri: str = "file:./mlruns"
    mlflow_experiment: str = "baseline-rag"
    mlflow_enabled: bool = False

    @property
    def index_path(self) -> Path:
        return self.data_dir / f"{self.index_name}.faiss"

    @property
    def metadata_path(self) -> Path:
        return self.data_dir / f"{self.index_name}.json"


@lru_cache
def get_settings() -> Settings:
    return Settings()
