from sqlalchemy.orm import Session
from data_ingestion.common.memory_writer import build_memory


def enrich_instagram_rows(db: Session, user_id: int, raw_rows: list[dict]):
    """
    raw_rows example:
    [
        {"name": "Framer", "description": "...", "url": "..."}
    ]
    """

    memories = []

    for row in raw_rows:
        memories.append(
            build_memory(
                user_id=user_id,
                source="instagram",
                title=row.get("name", "Unknown Tool"),
                description=row.get("description", ""),
                url=row.get("url", ""),
                tags="ai,tool",  # simple default for hackathon
            )
        )

    if memories:
        db.add_all(memories)
        db.commit()

    return len(memories)
