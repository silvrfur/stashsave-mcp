from sqlalchemy import Column, String, Text, DateTime, ForeignKey, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector
from data_ingestion.github_memory.db import Base

EMBEDDING_DIM = 384

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=False), primary_key=True, index=True, server_default=text("gen_random_uuid()"))
    github_username = Column(String, unique=True, index=True)
    access_token = Column(String)  # store encrypted later


class Memory(Base):
    __tablename__ = "memories"
    __table_args__ = (
        UniqueConstraint("user_id", "url", name="uq_memories_user_url"),
    )

    id = Column(UUID(as_uuid=False), primary_key=True, index=True, server_default=text("gen_random_uuid()"))
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"))
    source = Column(String)  # "github"
    title = Column(String)
    description = Column(Text)
    url = Column(String)
    tags = Column(String)  # comma-separated for now
    embedding = Column(Vector(EMBEDDING_DIM))
    saved_at = Column(DateTime, server_default=text("now()"))
