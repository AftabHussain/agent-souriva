# Optional stack compatibility bounds

## Change

Bound the RAGAS 0.2 LangChain dependencies below 0.4 and changed local MLflow 3 storage from the deprecated file store to SQLite.

## Architecture

These changes affect only optional tracking and evaluator-model dependencies. Core API, retrieval, MCP, and mock-model behavior remain unchanged.

## Design notes

MLflow 3 places filesystem tracking in maintenance mode and rejects it by default, while its SQLite backend remains supported. RAGAS 0.2 allows newer LangChain packages in its metadata even though its imports require the pre-1.0 module layout. Explicit LangChain bounds make the evaluator extra reproducible.

## Verification

The first optional-stack smoke run reproduced both failures: MLflow rejected `file:./mlruns`, and RAGAS failed importing a module removed from LangChain 1.x. A trial MLflow 2 pin was rejected because its PyArrow constraint has no Python 3.14 wheel. Reinstalled MLflow 3 with the bounded evaluator dependencies. RAGAS imports succeeded, direct evaluation created the SQLite experiment and logged its run, all 38 tests passed, and Ruff checks passed. Evaluator-model RAGAS scoring was not run because no evaluator credential was configured.

## Result

Tracking uses `sqlite:///mlflow.db` by default, and the RAGAS adapter imports against a compatible dependency set.
