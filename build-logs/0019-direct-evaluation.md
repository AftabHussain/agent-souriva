## Direct RAG evaluation metrics

**Source commit:** [`1dacf66`](https://github.com/AftabHussain/agent-souriva/commit/1dacf669a0993bee48905b1a64091c674cb987f0)

### Change

Added a compact evaluation runner for retrieval, citation, unsupported-answer, abstention, tool-use, and latency metrics.

Each observed run is reduced to directly measurable Boolean outcomes before aggregation:

    retrieval_hit = not case.expected_sources or bool(
        set(case.expected_sources) & retrieved_sources
    )
    rows.append({
        "retrieval_hit": retrieval_hit,
        "citation_correct": cited_ids <= retrieved_ids,
        "unsupported_answer":
            not result.answer.abstained and not cited_ids,
        "abstention_correct":
            result.answer.abstained is not case.answerable,
        "latency_ms": latency_ms,
    })

These fields compare the returned evidence, citations, and policy outcome with each case definition, producing transparent metrics without an evaluator model.

### Architecture

Evaluation operates on the public agent boundary and retains per-case answers, contexts, references, and measurements for optional RAGAS processing.

### Design notes

Metrics are calculated only from observed runs. Retrieval Recall@k is represented by expected-source hits for the initial dataset. Citation correctness verifies that every returned citation was among retrieved evidence, while unsupported-answer rate detects uncited non-abstentions.

### Verification

Compiled source and tests, checked the diff, and added deterministic cases covering an answerable question, a correct abstention, all aggregate direct metrics, and empty-dataset validation.

### Result

AgentSouriva can produce transparent baseline quality and latency measurements without requiring an evaluator model.
