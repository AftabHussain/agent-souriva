## Installation entry points

**Source commit:** [`9cd644b`](https://github.com/AftabHussain/agent-souriva/commit/9cd644bc35834cc64cd953d42cbd43249239a240)

### Change

Added pip requirements entry points for runtime and development/evaluation environments and allowed newer Python versions when dependency wheels are available.

The two requirements files select optional groups from the shared package metadata:

    # requirements.txt
    -e .[mcp,tracking]

    # requirements-dev.txt
    -e .[dev,evaluation,mcp,tracking]

Both environments therefore inherit one set of version constraints from `pyproject.toml`; the development entry point simply enables additional testing and evaluation tools.

### Architecture

Core package metadata remains the dependency source of truth. Requirements files select the relevant optional groups rather than duplicating version constraints.

### Design notes

The standard requirements include MCP and MLflow functionality. Development requirements additionally include tests and RAGAS evaluation; accelerator-heavy training dependencies remain an explicit separate extra.

### Verification

Checked the configuration diff and created a local virtual environment. Dependency installation and the complete suite are the next verification step.

### Result

Users have direct installation commands for the working service and for repository development.
