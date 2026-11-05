## Agent calculator routing

**Source commit:** [`29056ba`](https://github.com/AftabHussain/agent-souriva/commit/29056ba7aa41a969f4da6a2606495cb4ae691cec)

### Change

Added an explicit calculator route to the document agent and completed behavior for all four agent actions.

An explicit prefix selects the calculator path before document retrieval begins:

    def ask(self, question: str) -> AgentResult:
        if question.lower().startswith("calculate:"):
            expression = question.partition(":")[2].strip()
            return self._calculate(expression)
        evidence = self.retriever.search(
            question, self.top_k, self.min_relevance
        )

This deterministic branch prevents arithmetic requests from reaching retrieval or the language model and confines execution to the injected approved calculator.

### Architecture

Questions prefixed with `calculate:` take a bounded tool path. The calculator is injected as a callable, keeping the agent unaware of MCP transport and limiting tool access to an approved function.

### Design notes

Tool requests do not enter retrieval or the model. Expected parsing and arithmetic failures become a standardized abstention, while successful calculations are returned with a `USE_TOOL`, `ANSWER` trace and no document citations.

### Verification

Compiled source and tests, checked the diff, and added cases for successful and rejected calculator requests.

### Result

The agent now executes retrieval, approved tool use, answers, and abstentions through short deterministic paths.
