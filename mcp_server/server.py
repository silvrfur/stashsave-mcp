import sys
from mcp.server import FastMCP

from embeddings.search import semantic_search

mcp = FastMCP("stashsave-memory")


@mcp.tool()
def search_saves(query: str, user_id: str, limit: int = 5):
    """
    Semantic search over user's saved developer resources.
    """
    results = semantic_search(query=query, user_id=user_id, top_k=limit)
    return {
        "query": query,
        "user_id": user_id,
        "count": len(results),
        "results": results,
    }


if __name__ == "__main__":
    print("Starting MCP server...")
    try:
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        print("Shutting down MCP server...")
        sys.exit(0) 
