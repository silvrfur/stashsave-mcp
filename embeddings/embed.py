import argparse
from sqlalchemy.orm import Session

from data_ingestion.github_memory.db import SessionLocal
from data_ingestion.github_memory.models import Memory
from embeddings.model_loader import get_model
from embeddings.text_builder import build_embedding_text


def backfill_embeddings(user_id: str, refresh: bool = False):
    db: Session = SessionLocal()

    try:
        query = db.query(Memory).filter(Memory.user_id == user_id)
        if not refresh:
            query = query.filter(Memory.embedding.is_(None))

        memories = query.all()

        if not memories:
            print(f"No memories to embed for user_id={user_id}.")
            return

        texts = [
            build_embedding_text(
                title=memory.title,
                description=memory.description,
                tags=memory.tags,
            )
            for memory in memories
        ]

        print("Generating embeddings...")
        vectors = get_model().encode(texts, convert_to_numpy=True)

        for memory, vector in zip(memories, vectors):
            memory.embedding = vector.tolist()

        db.commit()
        print(f"Upserted embeddings for {len(memories)} memories (user_id={user_id}).")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--user-id", type=str, required=True)
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    backfill_embeddings(args.user_id, refresh=args.refresh)
