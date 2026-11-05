## Grounded agent flow

**Source commit:** [`f71e9a1`](https://github.com/AftabHussain/agent-souriva/commit/f71e9a17cd6092157f40168de0aa599fe84d71f4)

### Change

Added the single-pass document agent and explicit action trace.

The coordinating method takes one retrieval-to-grounding path and records its outcome:

    evidence = self.retriever.search(
        question, self.top_k, self.min_relevance
    )
    if not evidence:
        answer = GroundedAnswer(ABSTENTION, (), True,
                                "no_relevant_evidence")
        return AgentResult(answer, (),
                           (Action.RETRIEVE, Action.ABSTAIN))
    reply = self.model.answer(question, evidence)
    answer = ground_reply(reply, evidence, self.min_relevance)

The early return avoids generation when retrieval fails; otherwise the model reply must pass the grounding policy before becoming an agent result.

### Architecture

The agent coordinates retrieval, model generation, and alignment without owning their implementation. Its trace uses the four conceptual actions `RETRIEVE`, `USE_TOOL`, `ANSWER`, and `ABSTAIN`.

### Design notes

Document questions take the shortest path: one retrieval, at most one model call, then a grounding decision. No evidence causes an immediate abstention, avoiding unnecessary model work and reducing the chance of unsupported answers.

### Verification

Compiled modules, checked the diff, and added isolated tests for the successful grounded path and pre-generation abstention path.

### Result

The core can now coordinate retrieval and generation into a validated, traceable answer.
