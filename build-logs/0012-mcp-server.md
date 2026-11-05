## MCP document and calculator tools

**Source commit:** [`7c1be2f`](https://github.com/AftabHussain/agent-souriva/commit/7c1be2f9c20ca31436da38eb1ef2856269ea772b)

### Change

Added the approved document tool surface and exposed document search, chunk lookup, and arithmetic through a FastMCP server.

The MCP layer registers narrow functions and delegates their work to `DocumentTools`:

    @mcp.tool()
    def search_documents(query: str, top_k: int = 4) -> list[dict]:
        return tools.search_documents(query, top_k=max(1, min(top_k, 20)))

    @mcp.tool()
    def get_document_chunk(chunk_id: str) -> dict | None:
        return tools.get_document_chunk(chunk_id)

The decorators expose only these approved operations, while delegation keeps retrieval behavior independent of the MCP transport.

### Architecture

`DocumentTools` contains transport-independent behavior. `mcp_server` only constructs the configured store and maps approved methods to MCP, keeping protocol concerns out of retrieval and agent modules.

### Design notes

The server restores the same persisted index used by the API. Search result counts are bounded to protect local resources, and no generic function dispatcher is exposed, so clients can invoke only the three registered tools.

### Verification

Compiled all modules and checked the diff. Core tests cover search serialization, chunk lookup, missing IDs, arithmetic, and rejection of executable syntax.

### Result

MCP clients can search the local corpus, inspect cited chunks, and perform controlled calculations over stdio.
