import os

import requests

HF_EMBEDDING_MODEL = os.getenv(
    "HF_EMBEDDING_MODEL",
    "sentence-transformers/all-MiniLM-L6-v2",
)
HF_API_BASE = os.getenv(
    "HF_API_BASE",
    "https://api-inference.huggingface.co/models",
).rstrip("/")


def embed_query(query: str) -> list[float]:
    """
    Embed query text for semantic search.
    Uses Hugging Face Inference API when HF_API_TOKEN is set.
    Falls back to local sentence-transformers model.
    """
    token = os.getenv("HF_API_TOKEN", "").strip()
    if token:
        return _embed_query_hf(query=query, token=token)

    # Lazy import keeps MCP runtime working without sentence-transformers.
    from embeddings.model_loader import get_model

    return get_model().encode(query).tolist()


def _embed_query_hf(query: str, token: str) -> list[float]:
    url = f"{HF_API_BASE}/{HF_EMBEDDING_MODEL}"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"inputs": query}

    response = requests.post(url, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    body = response.json()

    # HF can return either a single vector or a list with one vector.
    if isinstance(body, list) and body and isinstance(body[0], (int, float)):
        return [float(v) for v in body]
    if (
        isinstance(body, list)
        and body
        and isinstance(body[0], list)
        and body[0]
        and isinstance(body[0][0], (int, float))
    ):
        return [float(v) for v in body[0]]

    raise ValueError(f"Unexpected HF embedding response format: {type(body).__name__}")
