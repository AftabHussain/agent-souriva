## Optional stack compatibility bounds

**Source commit:** [`56a702e`](https://github.com/AftabHussain/agent-souriva/commit/56a702ea4cf6dbe3db96499353cf4cdeb4658f5c)

### Change

Bound the RAGAS 0.2 LangChain dependencies below 0.4 and changed local MLflow 3 storage from the deprecated file store to SQLite.

The compatibility fix combines explicit evaluator bounds with a supported local tracking URI:

    evaluation = [
      "ragas>=0.2,<0.3",
      "langchain>=0.2,<0.4",
      "langchain-community>=0.2,<0.4",
      "langchain-openai>=0.1,<0.4",
    ]
    mlflow_tracking_uri: str = "sqlite:///mlflow.db"

The upper bounds retain the module layout expected by RAGAS 0.2, and SQLite replaces the file-store backend rejected by MLflow 3.

### Architecture

These changes affect only optional tracking and evaluator-model dependencies. Core API, retrieval, MCP, and mock-model behavior remain unchanged.

### Design notes

MLflow 3 places filesystem tracking in maintenance mode and rejects it by default, while its SQLite backend remains supported. RAGAS 0.2 allows newer LangChain packages in its metadata even though its imports require the pre-1.0 module layout. Explicit LangChain bounds make the evaluator extra reproducible.

### Verification

The first optional-stack smoke run reproduced both failures: MLflow rejected `file:./mlruns`, and RAGAS failed importing a module removed from LangChain 1.x. A trial MLflow 2 pin was rejected because its PyArrow constraint has no Python 3.14 wheel. Reinstalled MLflow 3 with the bounded evaluator dependencies. RAGAS imports succeeded, direct evaluation created the SQLite experiment and logged its run, all 38 tests passed, and Ruff checks passed. Evaluator-model RAGAS scoring was not run because no evaluator credential was configured.

### Result

Tracking uses `sqlite:///mlflow.db` by default, and the RAGAS adapter imports against a compatible dependency set.
