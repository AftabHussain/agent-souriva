# System Architecture and Document Flow

    PDF / Markdown / text
             |
             v
       Load and chunk
             |
             v
      Embed and index
             |
             v
     Retrieve evidence
             |
             v
     Agent reasoning / tool use
             |
             v
     Grounding and citation checks
             |
             v
     Answer with citations
           or abstain

## Build the document index

Documents are loaded and divided into chunks. Each chunk retains source information so retrieved evidence can later be traced back to its document and location.

The chunks are embedded and stored in a FAISS index for retrieval.

## Retrieve relevant evidence

When a question arrives, AgentSouriva searches the index for the document chunks most relevant to that question.

Retrieval can also be called independently when an application needs the evidence itself rather than a generated answer.

## Route the request

The agent decides whether the request should use document retrieval or an approved tool.

Document questions use retrieved evidence. Approved arithmetic is routed through a deterministic calculator rather than delegated to the language model.

## Generate a grounded answer

For document questions, the model receives the question together with the retrieved evidence.

Retrieved document text is treated as untrusted data in the prompt rather than as instructions for the agent.

## Validate the result

Before returning the response, AgentSouriva checks that citation IDs in the generated answer correspond to evidence retrieved above the configured relevance threshold.

The result is either a supported answer with citations or an abstention when the indexed evidence is insufficient.

## Document Ingestion Semantics

The `/documents` interface accepts paths to source files and builds the retrieval index and citation metadata for the selected files. Loading another set of documents replaces the previously indexed set.

Supported source extensions are `.pdf`, `.md`, `.markdown`, and `.txt`. For PDFs, citation locations use page numbers. Markdown and text sources retain document and chunk locations.

Documents are normalized into source-aware chunks before embedding and indexing. The document corpus can be replaced by a subsequent ingestion request, rather than cumulatively appended.
