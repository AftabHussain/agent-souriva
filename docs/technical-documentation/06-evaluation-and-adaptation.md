# Evaluation, Tracking, and Model Adaptation

## Direct Evaluation

The included evaluation suite covers document retrieval, citation behavior, abstention, and calculator routing. The default evaluation reports directly observed metrics without requiring an evaluator model.

The direct evaluation metrics are:

- Retrieval Recall@k source hits;

- Citation correctness;

- Unsupported-answer rate;

- Abstention accuracy;

- Tool-use accuracy;

- Mean latency.

No benchmark score is hard-coded into the repository.

## Optional RAGAS Evaluation

Optional RAGAS model-judged evaluation adds:

- Faithfulness;

- Answer relevance;

- Context precision;

- Context recall.

RAGAS scoring requires evaluator model credentials and remains distinct from the directly observed metrics. LM Evaluation Harness is not part of the runtime but can be used independently for future general-capability regression testing.

## MLflow Tracking

Agent-run tracking is optional and disabled by default. Each `/ask` run can record the question, retrieved chunks and scores, generated answer, citations, action trace, tool usage, latency, and relevant configuration.

Evaluation metrics and case-level artifacts can also be recorded for comparison across runs.

The tracking configuration variables and example values provided in the source README are:

| Setting                       | Source README example | Role                                |
|:------------------------------|:----------------------|:------------------------------------|
| `SOURIVA_MLFLOW_ENABLED`      | `true`                | Enables optional agent-run tracking |
| `SOURIVA_MLFLOW_TRACKING_URI` | `sqlite:///mlflow.db` | SQLite tracking database URI        |
| `SOURIVA_MLFLOW_EXPERIMENT`   | `baseline-rag`        | Experiment identifier               |

## Optional Model Adaptation

AgentSouriva includes experimental entry points for adapting a model to the desired agent behavior. These training components are separate from the core runtime and are not required for document retrieval and grounded answering.

Successful supervised traces contain the following fields:

    question
    retrieved_context
    desired_action
    grounded_answer
    citations

A validated example trace is located at `data/sft_example.jsonl`. Supervised fine-tuning is based on these successful traces. The LoRA approach can be extended to QLoRA, in which supported systems load the base model in 4-bit mode.

The preference-training interface defines an explicit reward signal around supported answers, citation correctness, appropriate tool use, and abstention. Unsupported claims, invented citations, and unnecessary tool calls are penalized.

Training and preference optimization remain optional, distinct from the core runtime.
