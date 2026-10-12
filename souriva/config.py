# This module defines *runtime* settings: values that may change between
# development, testing, and deployment without editing application code.
# Contrast with pyproject.toml, which configures packaging and dependencies.

# A decorator that saves a function's result and reuses it on later calls.
from functools import lru_cache

# Path represents filesystem paths and provides convenient path operations.
from pathlib import Path

# Literal restricts a setting to a fixed set of allowed string values.
from typing import Literal

# BaseSettings reads and validates settings from environment variables,
# a .env file, and class defaults. SettingsConfigDict configures that behavior.
from pydantic_settings import BaseSettings, SettingsConfigDict


# Inheritance syntax: Settings receives BaseSettings' loading, parsing,
# validation, and type-conversion behavior.
class Settings(BaseSettings):
    """Runtime configuration loaded from environment or a local .env file."""

    # SOURIVA_ is prepended to field names in environment variables:
    #   SOURIVA_RETRIEVAL_TOP_K=8  -> retrieval_top_k = 8
    # env_file permits local overrides in .env (often useful in development).
    # extra="ignore" tolerates unrecognized entries in that dotenv file.
    # Explicit constructor values and environment values generally take
    # precedence over .env entries, which take precedence over defaults.
    # Keep credentials in environment variables or an untracked .env file.
    model_config = SettingsConfigDict(env_prefix="SOURIVA_", env_file=".env", extra="ignore")

    # Field syntax: "name: type = default". Pydantic uses the annotation to
    # validate/convert an override, e.g., the string "8" can become an int.
    # Path("artifacts") creates a relative path (relative to the process's
    # working directory), not the directory containing this source file.
    data_dir: Path = Path("artifacts")
    index_name: str = "documents"

    # Retrieval/index settings. These values are *configuration*, not the
    # implementation of chunking, embedding, searching, or score calculation.
    # The embedding dimension must match the vectors used to build/search
    # the FAISS index. The units of chunk_size/overlap depend on the chunker.
    embedding_dimensions: int = 384
    chunk_size: int = 900
    chunk_overlap: int = 120
    # Ask the retrieval system for up to this many top-ranked chunks.
    retrieval_top_k: int = 4
    # A cutoff intended for filtering weak evidence; its scale/meaning
    # depends on the relevance-scoring implementation.
    min_relevance: float = 0.18

    # Literal[...] means only the listed strings are accepted at validation.
    # "mock" is the default, so specifying a real model name below does not
    # by itself start or select a live model server.
    model_backend: Literal["mock", "openai-compatible"] = "mock"
    # These are connection parameters for the OpenAI-compatible backend.
    # localhost means the server is expected on the same machine.
    model_base_url: str = "http://localhost:8001/v1"
    model_name: str = "openai/gpt-oss-20b"
    # "local" is a default string, not a production secret.
    model_api_key: str = "local"

    # MLflow experiment-tracking settings. sqlite:///mlflow.db is a SQLite
    # database URL for a local file; specifying it does not start tracking.
    mlflow_tracking_uri: str = "sqlite:///mlflow.db"
    mlflow_experiment: str = "baseline-rag"
    # bool fields may be overridden via values such as SOURIVA_MLFLOW_ENABLED=true.
    mlflow_enabled: bool = False

    # @property makes a zero-argument method behave like a read-only
    # attribute: settings.index_path (not settings.index_path()).
    # The resulting path is *derived*, so there is no second path setting to
    # update when data_dir or index_name changes.
    @property
    def index_path(self) -> Path:
        # "self" refers to this Settings instance.
        # The / operator on pathlib.Path JOINS path components; it does not
        # perform numeric division. The f-string inserts index_name into the
        # filename. Example: Path("artifacts") / "documents.faiss".
        # -> Path is a return-type annotation (not an explicit conversion).
        return self.data_dir / f"{self.index_name}.faiss"

    @property
    def metadata_path(self) -> Path:
        # Same directory and base filename, but with a .json extension.
        # This property computes a value; it does not create the JSON file.
        return self.data_dir / f"{self.index_name}.json"


# @lru_cache remembers the return value for this no-argument function.
# In a running process, repeated get_settings() calls normally reuse one
# Settings object instead of re-reading and validating configuration.
# If the environment/.env changes after the first call, existing cached
# settings do not refresh automatically (get_settings.cache_clear() resets it).
@lru_cache
def get_settings() -> Settings:
    # Construct Settings once on the first call using the active sources;
    # -> Settings documents the type returned by this function.
    return Settings()
