from mcp.server.fastmcp import FastMCP

from souriva.config import get_settings
from souriva.rag import FaissStore, HashEmbeddings
from souriva.tools import DocumentTools

settings = get_settings()
store = FaissStore(
    HashEmbeddings(settings.embedding_dimensions), settings.index_path, settings.metadata_path
)
store.load()
tools = DocumentTools(store)
mcp = FastMCP("AgentSouriva")


@mcp.tool()
def search_documents(query: str, top_k: int = 4) -> list[dict]:
    """Search indexed documents for evidence relevant to a query."""
    return tools.search_documents(query, top_k=max(1, min(top_k, 20)))


@mcp.tool()
def get_document_chunk(chunk_id: str) -> dict | None:
    """Fetch one indexed document chunk by its stable identifier."""
    return tools.get_document_chunk(chunk_id)


@mcp.tool()
def calculate(expression: str) -> float:
    """Evaluate a numeric arithmetic expression."""
    return tools.calculator(expression)


if __name__ == "__main__":
    mcp.run()
