import sys
from mcp.server import FastMCP

from data_ingestion.github_memory.db import SessionLocal
from data_ingestion.github_memory.models import Memory
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


@mcp.tool()
def list_saves(user_id: str, limit: int = 50):
    """
    List saved repositories for a user. Useful for downstream agent ranking/enrichment workflows.
    """
    db = SessionLocal()
    try:
        rows = (
            db.query(Memory)
            .filter(Memory.user_id == user_id)
            .order_by(Memory.saved_at.desc())
            .limit(limit)
            .all()
        )
        return {
            "user_id": user_id,
            "count": len(rows),
            "results": [
                {
                    "id": row.id,
                    "title": row.title,
                    "description": row.description,
                    "url": row.url,
                    "tags": row.tags,
                    "saved_at": row.saved_at.isoformat() if row.saved_at else None,
                }
                for row in rows
            ],
        }
    finally:
        db.close()


if __name__ == "__main__":
    print("Starting MCP server...")
    try:
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        print("Shutting down MCP server...")
        sys.exit(0) 
