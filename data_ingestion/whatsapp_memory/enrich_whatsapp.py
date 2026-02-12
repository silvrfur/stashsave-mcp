from sqlalchemy.orm import Session
from data_ingestion.common.memory_writer import build_memory


def enrich_whatsapp_rows(db: Session, user_id: int, raw_rows: list[dict]):
    """
    raw_rows example:
    [
        {"tool": "Supabase", "text": "Great backend", "url": "https://supabase.com"}
    ]
    """

    memories = []

    for row in raw_rows:
        memories.append(
            build_memory(
                user_id=user_id,
                source="whatsapp",
                title=row.get("tool", "Unknown Tool"),
                description=row.get("text", ""),
                url=row.get("url", ""),
                tags="recommendation,chat",
            )
        )

    if memories:
        db.add_all(memories)
        db.commit()

    return len(memories)
