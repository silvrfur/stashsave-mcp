from sqlalchemy.orm import Session

from data_ingestion.github_memory.db import SessionLocal
from data_ingestion.github_memory.models import Memory
from embeddings.model_loader import get_model
from .vector_store import search_vectors

def semantic_search(query: str, user_id: int, top_k: int = 5):
    db: Session = SessionLocal()

    query_vector = get_model().encode(query)

    matches = search_vectors(query_vector, user_id=user_id, top_k=top_k)

    results = []

    for memory_id, score in matches:
        memory = (
            db.query(Memory)
            .filter(Memory.id == memory_id, Memory.user_id == user_id)
            .first()
        )
        if memory:
            results.append({
                "id": memory.id,
                "user_id": memory.user_id,
                "title": memory.title,
                "description": memory.description,
                "url": memory.url,
                "tags": memory.tags,
                "score": round(score, 4),
            })

    db.close()
    return results
