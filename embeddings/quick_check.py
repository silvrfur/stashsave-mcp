#!!!Temp file, to be removed
from data_ingestion.github_memory.models import Memory
from data_ingestion.github_memory.db import SessionLocal

db = SessionLocal()
print(db.query(Memory).count())