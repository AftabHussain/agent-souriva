## Model adapter and local backend

**Source commit:** [`5474d04`](https://github.com/AftabHussain/agent-souriva/commit/5474d04794d8ed528bc4ef9eab94c11c053b44fb)

### Change

Added the model protocol, shared evidence and reply values, and a deterministic extractive mock backend.

The protocol captures the narrow contract implemented by every model backend:

    class ModelAdapter(Protocol):
        def answer(
            self, question: str, evidence: Sequence[Evidence]
        ) -> ModelReply: ...

Agent code therefore depends only on an `answer` operation that consumes evidence and returns normalized text plus citation identifiers, not on a particular inference library.

### Architecture

The adapter separates agent behavior from model serving. Evidence enters through a small typed contract and model replies identify the chunk IDs they cite.

### Design notes

The mock selects at most two chunks and extracts one sentence from each. It is deliberately deterministic so ingestion, retrieval, grounding, and API behavior can be exercised without a running language model.

### Verification

Ran `python -m compileall souriva tests`. The modules compiled successfully. The test runner is added as a development dependency and tests will run after dependencies are installed.

### Result

The project can generate a predictable evidence-linked reply through the same interface a GPT-OSS-20B adapter will implement.
