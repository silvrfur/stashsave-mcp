from sqlalchemy.orm import Session

from data_ingestion.github_memory.github_api import fetch_starred_repos
from data_ingestion.github_memory.models import Memory, User
from embeddings.model_loader import get_model
from embeddings.text_builder import build_embedding_text


def ingest_github_stars(db: Session, user_id: str, access_token: str):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        db.add(User(id=user_id))
        db.flush()

    repos = fetch_starred_repos(access_token)
    if not repos:
        db.commit()
        return 0

    texts = []
    payloads = []
    for repo in repos:
        title = repo["full_name"]
        description = repo.get("description") or ""
        url = repo["html_url"]
        tags = ",".join(repo.get("topics", [])) if repo.get("topics") else ""
        texts.append(build_embedding_text(title=title, description=description, tags=tags))
        payloads.append(
            {
                "source": "github",
                "title": title,
                "description": description,
                "url": url,
                "tags": tags,
            }
        )

    vectors = get_model().encode(texts, convert_to_numpy=True)
    upserted = 0

    for payload, vector in zip(payloads, vectors):
        memory = (
            db.query(Memory)
            .filter(Memory.user_id == user_id, Memory.url == payload["url"])
            .first()
        )
        if memory is None:
            memory = Memory(user_id=user_id, **payload)
            db.add(memory)
        else:
            memory.source = payload["source"]
            memory.title = payload["title"]
            memory.description = payload["description"]
            memory.tags = payload["tags"]

        memory.embedding = vector.tolist()
        upserted += 1

    db.commit()

    return upserted
