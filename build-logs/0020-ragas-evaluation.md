## RAGAS evaluation runner

**Source commit:** [`5b0d127`](https://github.com/AftabHussain/agent-souriva/commit/5b0d127ba9f9e958782009c92fb4a8ea6c515500)

### Change

Added a four-case evaluation dataset, two source documents, a direct evaluation CLI, and optional RAGAS execution for faithfulness, answer relevance, context precision, and context recall.

The command always computes direct metrics and runs model-judged RAGAS metrics only when requested:

    direct, rows = evaluate_cases(runtime.agent, cases)
    output = {"direct": direct}
    if args.ragas:
        output["ragas"] = run_ragas(rows)
    print(json.dumps(output, indent=2))

This conditional keeps the default benchmark local and reproducible while preserving an explicit path to evaluator-model scoring.

### Architecture

The runner builds an isolated evaluation index, exercises the real runtime, then transforms observed answers and contexts into the RAGAS dataset schema. Model-judged metrics run only with `--ragas`.

### Design notes

RAGAS is pinned to the 0.2 API line used by the runner. The default command reports only locally measured direct metrics; RAGAS requires its evaluator model credentials and never substitutes invented scores.

### Verification

Compiled the runner and checked the diff. Full execution is deferred until the declared FAISS and NumPy dependencies are installed.

### Result

`python -m benchmarks.ragas_eval` runs the reproducible local suite, while `--ragas` adds the four requested evaluator-model metrics.
