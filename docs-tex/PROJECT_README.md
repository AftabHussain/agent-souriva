# AgentSouriva Overleaf migration map

This project is a plain, academic-style LaTeX reference, compiled from the
Markdown archive dated 9 October 2026. Compile `main.tex` with **pdfLaTeX**.

- `technical-documentation/01-...` through `06-...` contain all conceptual and
  technical README material: purpose, workflows, features, API request/response
  formats, metadata, supported formats, interfaces, MCP, model integration,
  settings and source example values, evaluation, tracking, optional adaptation,
  and repository organization. Some usage-oriented passages were rewritten as
  neutral interface specifications without removing their technical meaning.
- `build-logs/0001-...` through `0027-...` correspond one-for-one to the
  original Markdown files, in original order and with every original Change,
  Architecture, Design notes, Verification, and Result paragraph retained.
- `preamble.tex` defines `\aftabnote{...}`. Example:
  `\aftabnote{Review the retrieval threshold choice.}`
  Only `Aftab:` is bold; the entire note receives a pale yellow highlight.
- A commented note placeholder is at the end of every `.tex` source file.

## Excluded from the compiled PDF

Installation / environment setup and commands to start, configure, and operate
AgentSouriva, `curl` how-to tutorials, developer lint/test how-to instructions,
and interactive documentation URLs presented only as user directions. These
remain in the repository's Markdown README. Technical request-body schemas and
API behavior are retained in the LaTeX reference.

The separate `data/sample_docs/architecture.md` is sample ingestion data and
was not converted. After one-to-one content verification, the superseded
Markdown build logs were removed from the repository.

## Maintenance

Add a new build-log `.tex` under `build-logs/`, then add its
`\input{build-logs/<filename>}` line to `main.tex`. The `\aftabnote`
command is available in any `.tex` file without additional imports.
