## Project skeleton and configuration

**Source commit:** [`9ba1ed1`](https://github.com/AftabHussain/agent-souriva/commit/9ba1ed146cca9114c179878e637e1ad90a4472b0)

### Change

Added the installable `souriva` package, project metadata, dependency groups, ignore rules, and environment-driven runtime settings.

#### Overall Souriva Package Structure.

The Souriva uses three complementary files to organize its Python project. The `pyproject.toml` file defines project metadata, build and installation requirements, dependencies, and development tool configurations. The `config.py` file manages runtime settings, including storage, retrieval parameters, model selection, and experiment tracking. Finally, `__init__.py` identifies the `souriva` directory as a Python package, executes package initialization code when imported, and exposes package-level information such as `__version__`. In summary, `pyproject.toml` configures the software project, `config.py` configures the running application, and `__init__.py` defines the package’s initialization and public interface.

#### Python Project Configuration (`pyproject.toml`).

The `pyproject.toml` file is the standard configuration file for a Python project. It defines how the project is built and installed, specifies package metadata (e.g., name, version, and supported Python versions), and declares required and optional dependencies. For AgentSouriva, core dependencies support API serving, document processing, and retrieval, while optional dependency groups provide additional capabilities such as MCP integration, evaluation, training, and experiment tracking. The file also configures development tools, including `pytest` for testing and `ruff` for linting and formatting. By centralizing these settings, `pyproject.toml` simplifies installation, dependency management, and development.

#### Runtime Configuration (`config.py`).

AgentSouriva centralizes its runtime configuration in a `Settings` class that inherits from Pydantic’s `BaseSettings`. This separates configurable parameters from application logic, allowing behavior to be changed without modifying source code. Settings are loaded from environment variables prefixed with `SOURIVA_` or a local `.env` file, falling back to predefined defaults. Pydantic also validates and converts values according to their declared types, while `Literal` restricts the model backend to supported options.

The configuration covers storage locations, embedding dimensions, document chunking and overlap, retrieval limits and relevance thresholds, model backend and connection details, and MLflow experiment tracking. The `@property` decorator defines computed paths for the FAISS index and its associated metadata, ensuring that both remain consistent with the configured storage directory and index name.

Finally, the `get_settings()` function uses Python’s `@lru_cache` decorator to instantiate the configuration only once and reuse it across subsequent calls. This avoids repeated environment parsing and provides a consistent configuration throughout the running process. Together, these mechanisms provide centralized, validated, environment-specific, and reusable runtime configuration.

The central settings object is the key configuration boundary:

    class Settings(BaseSettings):
        model_config = SettingsConfigDict(env_prefix="SOURIVA_")
        data_dir: Path = Path("artifacts")
        model_backend: Literal["mock", "openai-compatible"] = "mock"

These declarations give every runtime component typed defaults while allowing each value to be overridden through a consistently prefixed environment variable.

### Architecture

This establishes the configuration boundary shared by the API, retrieval, model, tracking, and evaluation components. Runtime artifacts are kept outside the Git repository (i.e., the Git source control).

### Design notes

The default backend is a local mock and the default index lives under `artifacts/`. Optional dependency groups keep MLflow, MCP, evaluation, and training stacks out of the core installation. Python is capped below 3.14 because several binary ML dependencies do not yet publish compatible wheels.

### Verification

Ran `python -m compileall souriva` and inspected the staged diff. Compilation succeeded.

### Result

AgentSouriva now has a package boundary and one centralized, environment-overridable configuration object.
