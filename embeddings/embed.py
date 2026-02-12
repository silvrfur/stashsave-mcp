import argparse
from pathlib import Path

import numpy as np
from sqlalchemy.orm import Session

from data_ingestion.github_memory.db import SessionLocal
from data_ingestion.github_memory.models import Memory
from embeddings.model_loader import get_model

BASE_DIR = Path(__file__).resolve().parent


def build_embedding_text(memory: Memory) -> str:
    parts = [
        memory.title or "",
        memory.description or "",
        memory.tags or "",
    ]
    return " ".join(parts)


def generate_embeddings(user_id: int):
    db: Session = SessionLocal()
    memories = db.query(Memory).filter(Memory.user_id == user_id).all()

    if not memories:
        print(f"No memories found in DB for user_id={user_id}.")
        db.close()
        return

    texts = [build_embedding_text(m) for m in memories]

    print("Generating embeddings...")
    vectors = get_model().encode(texts, convert_to_numpy=True)

    np.save(BASE_DIR / f"vectors_user_{user_id}.npy", vectors)
    ids = np.array([m.id for m in memories])
    np.save(BASE_DIR / f"ids_user_{user_id}.npy", ids)

    print(f"Saved {len(vectors)} embeddings for user_id={user_id}.")
    db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--user-id", type=int, required=True)
    args = parser.parse_args()
    generate_embeddings(args.user_id)
