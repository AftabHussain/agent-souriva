## Document loader: The First RAG Pipeline Stage

**Source commit:** [`b7bd2a2`](https://github.com/AftabHussain/agent-souriva/commit/b7bd2a2e5e9fe1c1cf6833998e1f1b39b144b292)

### Change

Added source-aware loading for PDF, Markdown, and UTF-8 text documents.

The format branch preserves page information for PDFs and a document location for text files:

    if suffix == ".pdf":
        return [
            DocumentPart(text=text, source=path.name,
                         location=f"page {number}")
            for number, page in enumerate(PdfReader(path).pages, start=1)
            if (text := (page.extract_text() or "").strip())
        ]

Each extracted part carries its filename and location immediately, so later chunking and citation stages do not need to reconstruct provenance.

### Architecture

The loader is the first RAG pipeline stage. It normalizes files into `DocumentPart` values while preserving filenames and page locations for downstream citations.

### Design notes

PDF extraction uses one part per non-empty page. Text formats remain one part at this stage so chunking stays independent of file I/O. Unsupported extensions fail explicitly instead of being guessed.

### Verification

Compiled the package and tests, checked the diff, and added unit coverage for text, Markdown, and unsupported types. PDF extraction is exercised when the optional fixture is available in later integration testing.

### Result

AgentSouriva can normalize all three required document formats into a common metadata-preserving representation.
