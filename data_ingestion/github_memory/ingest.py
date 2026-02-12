from sqlalchemy.orm import Session
from data_ingestion.github_memory.github_api import fetch_starred_repos
from data_ingestion.common.memory_writer import build_memory


def ingest_github_stars(db: Session, user_id: int, access_token: str):
    repos = fetch_starred_repos(access_token)
    memories = []

    for repo in repos:
        memories.append(
            build_memory(
                user_id=user_id,
                source="github",
                title=repo["full_name"],
                description=repo.get("description") or "",
                url=repo["html_url"],
                tags=",".join(repo.get("topics", [])) if repo.get("topics") else "",
            )
        )

    if memories:
        db.add_all(memories)
        db.commit()

    return len(memories)
