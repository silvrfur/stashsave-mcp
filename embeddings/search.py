from sqlalchemy.orm import Session

from data_ingestion.github_memory.db import SessionLocal
from data_ingestion.github_memory.models import Memory
from embeddings.query_embedder import embed_query


def _search_with_vector(db: Session, query_vector: list[float], user_id: str, top_k: int):
    distance = Memory.embedding.cosine_distance(query_vector)
    rows = (
        db.query(Memory, distance.label("distance"))
        .filter(
            Memory.user_id == user_id,
            Memory.embedding.isnot(None),
        )
        .order_by(distance.asc())
        .limit(top_k)
        .all()
    )

    results = []
    for memory, raw_distance in rows:
        score = max(0.0, 1.0 - float(raw_distance))
        results.append(
            {
                "id": memory.id,
                "user_id": memory.user_id,
                "title": memory.title,
                "description": memory.description,
                "url": memory.url,
                "tags": memory.tags,
                "score": round(score, 4),
            }
        )

    return results


def semantic_search_by_vector(query_embedding: list[float], user_id: str, top_k: int = 5):
    db: Session = SessionLocal()

    try:
        return _search_with_vector(
            db=db,
            query_vector=query_embedding,
            user_id=user_id,
            top_k=top_k,
        )
    finally:
        db.close()


def semantic_search(query: str, user_id: str, top_k: int = 5):
    query_vector = embed_query(query)
    return semantic_search_by_vector(query_embedding=query_vector, user_id=user_id, top_k=top_k)
