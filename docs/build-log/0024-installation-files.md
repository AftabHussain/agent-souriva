# Installation entry points

## Change

Added pip requirements entry points for runtime and development/evaluation environments and allowed newer Python versions when dependency wheels are available.

## Architecture

Core package metadata remains the dependency source of truth. Requirements files select the relevant optional groups rather than duplicating version constraints.

## Design notes

The standard requirements include MCP and MLflow functionality. Development requirements additionally include tests and RAGAS evaluation; accelerator-heavy training dependencies remain an explicit separate extra.

## Verification

Checked the configuration diff and created a local virtual environment. Dependency installation and the complete suite are the next verification step.

## Result

Users have direct installation commands for the working service and for repository development.
