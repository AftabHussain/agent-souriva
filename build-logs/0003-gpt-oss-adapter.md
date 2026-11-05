## GPT-OSS-compatible model adapter and citation validation

**Source commit:** [`d26e836`](https://github.com/AftabHussain/agent-souriva/commit/d26e8364efbe4d0a2cf02d8dc6e193e386948c34)

### Change

Added a small OpenAI-compatible HTTP adapter and backend selector.

The adapter serializes the grounded prompt into the standard chat-completions request shape:

    context = "\n\n".join(
        f"[{item.id}] {item.text}" for item in evidence
    )
    payload = {
        "model": self.model,
        "temperature": 0,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content":
             f"QUESTION:\n{question}\n\nEVIDENCE:\n{context}"},
        ],
    }

This small translation layer lets a locally served GPT-OSS model use the same `ModelAdapter` interface as the deterministic mock backend.

#### Citation Validation Using an Allow-List.

Here we validate model-generated citations by checking them against the evidence actually supplied to the model. Since a language model may generate nonexistent citation identifiers, the system uses an *allow-list*: only identifiers belonging to the supplied evidence are accepted. This check is implemented as follows:

**Listing 3: Filtering model-generated citations against supplied evidence**

```python
# Retain only evidence IDs that appear in the generated text.
valid = tuple(item.id for item in evidence if f"[{item.id}]" in text)
```

The expression iterates over each `Evidence` object in `evidence` and checks whether its identifier appears in the model-generated `text`, enclosed in square brackets. For example, if the supplied evidence contains identifiers `doc1`, `doc2`, and `doc3`, but the model generates citations `[doc1]`, `[doc2]`, and `[fake99]`, only `doc1` and `doc2` are retained. The `for` and `if` clauses form a generator expression that produces matching identifiers, while `tuple()` collects them into an immutable tuple. The resulting identifiers follow the order of the supplied evidence rather than their appearance in the generated text. Importantly, this mechanism verifies *citation identity*, not *semantic support*: it prevents unknown identifiers from entering the validated citation list, but does not establish whether the cited evidence actually supports the corresponding claim.

### Architecture

GPT-OSS-20B serving is isolated behind the same `ModelAdapter` boundary as the mock. The adapter sends retrieved context to a chat-completions endpoint and returns a normalized reply.

### Design notes

The prompt marks retrieved text as untrusted data and requires evidence-only answers. Returned citation identifiers are intersected with retrieved chunk IDs so fabricated citations cannot enter the application response. A standard-library HTTP client avoids another core dependency.

### Verification

Ran module compilation and checked the diff. Factory unit tests cover both configured backends and invalid configuration; full test execution awaits development dependency installation.

### Result

A local GPT-OSS-20B server can later replace the mock through configuration without changes to agent logic.
