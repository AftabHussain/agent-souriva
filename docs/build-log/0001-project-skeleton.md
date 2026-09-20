# Project skeleton and configuration

## Change

Added the installable `souriva` package, project metadata, dependency groups, ignore rules, and environment-driven runtime settings.

## Architecture

This establishes the configuration boundary shared by the API, retrieval, model, tracking, and evaluation components. Runtime artifacts are kept outside source control.

## Design notes

The default backend is a local mock and the default index lives under `artifacts/`. Optional dependency groups keep MLflow, MCP, evaluation, and training stacks out of the core installation. Python is capped below 3.14 because several binary ML dependencies do not yet publish compatible wheels.

## Verification

Ran `python -m compileall souriva` and inspected the staged diff. Compilation succeeded.

## Result

AgentSouriva now has a package boundary and one centralized, environment-overridable configuration object.
