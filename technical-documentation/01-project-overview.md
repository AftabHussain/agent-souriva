# Project Overview

AgentSouriva is a local, evidence-grounded agent for reasoning over PDF, Markdown, and text collections.

It is built around a simple question: **how can an AI agent answer from documents while keeping its evidence, tool use, and uncertainty visible?**

Given a collection of documents, AgentSouriva indexes their contents, retrieves relevant evidence for each question, and returns source-aware answers. It can validate citations against retrieved evidence, route approved tasks through dedicated tools, and abstain when the available documents do not sufficiently support an answer.

The project is designed as a compact environment for exploring **trustworthy document-grounded agents**, including retrieval, constrained tool use, citation validation, abstention, evaluation, and optional model adaptation.

## Why AgentSouriva?

Retrieval-augmented systems can make language models useful over private or specialized documents, but retrieval alone does not guarantee that an answer is supported by the retrieved evidence.

AgentSouriva makes the important parts of this process explicit:

- **Evidence retrieval**: answers are grounded in chunks retrieved from the indexed corpus.

- **Source-aware citations**: responses retain references to the evidence used.

- **Citation validation**: citation IDs are checked against the evidence actually retrieved.

- **Controlled tool use**: the agent operates through a small set of approved tools.

- **Abstention**: unsupported document questions can return an abstention rather than an unsupported answer.

- **Evaluation**: retrieval, citation behavior, abstention, tool use, unsupported answers, and latency can be measured directly.

This makes AgentSouriva useful both as a local document assistant and as an experimental platform for studying grounded agent behavior.

## Example Uses

AgentSouriva can be used to:

- compare methods, datasets, metrics, and reported results across papers;

- answer questions from technical manuals and architecture documentation;

- extract authentication, endpoint, and usage details from API documentation;

- compare specifications across documents with source references;

- retrieve documented quantities and perform approved calculations;

- identify when the indexed documents do not contain enough information to answer a question.

## License

AgentSouriva is available under the MIT License.
