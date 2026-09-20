# MCP document and calculator tools

## Change

Added the approved document tool surface and exposed document search, chunk lookup, and arithmetic through a FastMCP server.

## Architecture

`DocumentTools` contains transport-independent behavior. `mcp_server` only constructs the configured store and maps approved methods to MCP, keeping protocol concerns out of retrieval and agent modules.

## Design notes

The server restores the same persisted index used by the API. Search result counts are bounded to protect local resources, and no generic function dispatcher is exposed, so clients can invoke only the three registered tools.

## Verification

Compiled all modules and checked the diff. Core tests cover search serialization, chunk lookup, missing IDs, arithmetic, and rejection of executable syntax.

## Result

MCP clients can search the local corpus, inspect cited chunks, and perform controlled calculations over stdio.
