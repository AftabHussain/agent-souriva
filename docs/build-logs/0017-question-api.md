## Grounded question API

**Source commit:** [`de904b3`](https://github.com/AftabHussain/agent-souriva/commit/de904b3984171b8148748f000a6a07fd457a0642)

### Change

Added `POST /ask` with typed answers, citations, abstention details, and action traces.

The endpoint exposes the agent result without reimplementing its retrieval or grounding logic:

    @app.post("/ask", response_model=AskResponse)
    def ask(request: AskRequest) -> AskResponse:
        result = runtime.agent.ask(request.question)
        return AskResponse(
            answer=result.answer.text,
            citations=[c.__dict__ for c in result.answer.citations],
            abstained=result.answer.abstained,
            reason=result.answer.reason,
            actions=[action.value for action in result.actions],
        )

Mapping the normalized agent result into a typed response preserves citations, policy decisions, and the action trace for HTTP clients.

### Architecture

The endpoint delegates to the shared `DocumentAgent`, exposing alignment results without duplicating retrieval or grounding decisions in HTTP code.

### Design notes

Responses keep citations structured for clients while the answer text also retains inline chunk references. Abstentions use HTTP 200 (HTTP status code for OK) because they are successful, policy-compliant outcomes rather than transport failures.

### Verification

Compiled the project, checked the diff, and extended API integration coverage for a cited document answer and an empty-corpus abstention.

### Result

The complete ingest, retrieve, and grounded-answer flow is available through FastAPI.
