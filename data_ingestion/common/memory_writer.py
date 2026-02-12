from data_ingestion.github_memory.models import Memory


def build_memory(
    user_id: int,
    source: str,
    title: str,
    description: str,
    url: str,
    tags: str = "",
):
    memory = Memory(
        user_id=user_id,
        source=source,
        title=title,
        description=description,
        url=url,
        tags=tags,
    )
    return memory
