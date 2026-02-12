from pathlib import Path

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def _paths_for_user(user_id: int):
    base_dir = Path(__file__).resolve().parent
    vectors_path = base_dir / f"vectors_user_{user_id}.npy"
    ids_path = base_dir / f"ids_user_{user_id}.npy"
    return vectors_path, ids_path


def load_vectors(user_id: int):
    vectors_path, ids_path = _paths_for_user(user_id)
    vectors = np.load(vectors_path)
    ids = np.load(ids_path)
    return vectors, ids


def search_vectors(query_vector, user_id: int, top_k=5):
    vectors, ids = load_vectors(user_id)

    sims = cosine_similarity([query_vector], vectors)[0]

    top_indices = sims.argsort()[-top_k:][::-1]

    results = [(int(ids[i]), float(sims[i])) for i in top_indices]
    return results
