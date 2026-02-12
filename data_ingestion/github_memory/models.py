from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from datetime import datetime
from data_ingestion.github_memory.db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    github_username = Column(String, unique=True, index=True)
    access_token = Column(String)  # store encrypted later


class Memory(Base):
    __tablename__ = "memories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    source = Column(String)  # "github"
    title = Column(String)
    description = Column(Text)
    url = Column(String)
    tags = Column(String)  # comma-separated for now
    saved_at = Column(DateTime, default=datetime.utcnow)
