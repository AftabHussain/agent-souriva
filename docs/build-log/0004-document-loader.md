# Document loader

## Change

Added source-aware loading for PDF, Markdown, and UTF-8 text documents.

## Architecture

The loader is the first RAG pipeline stage. It normalizes files into `DocumentPart` values while preserving filenames and page locations for downstream citations.

## Design notes

PDF extraction uses one part per non-empty page. Text formats remain one part at this stage so chunking stays independent of file I/O. Unsupported extensions fail explicitly instead of being guessed.

## Verification

Compiled the package and tests, checked the diff, and added unit coverage for text, Markdown, and unsupported types. PDF extraction is exercised when the optional fixture is available in later integration testing.

## Result

AgentSouriva can normalize all three required document formats into a common metadata-preserving representation.
