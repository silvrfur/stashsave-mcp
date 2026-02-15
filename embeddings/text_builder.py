def build_embedding_text(title: str, description: str, tags: str) -> str:
    parts = [title or "", description or "", tags or ""]
    return " ".join(parts).strip()
