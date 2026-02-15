import logging
import os

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from embeddings.search import semantic_search
from data_ingestion.github_memory.db import SessionLocal, engine, Base
from data_ingestion.github_memory.ingest import ingest_github_stars


with engine.begin() as conn:
    vector_enabled = conn.execute(
        text("SELECT 1 FROM pg_extension WHERE extname = 'vector'")
    ).first()
    if not vector_enabled:
        try:
            conn.execute(text("CREATE EXTENSION vector"))
        except Exception as exc:
            raise RuntimeError(
                "pgvector extension is not enabled. Enable extension 'vector' in Supabase."
            ) from exc

# Create DB tables on startup
Base.metadata.create_all(bind=engine)

with engine.begin() as conn:
    conn.execute(text("CREATE INDEX IF NOT EXISTS idx_memories_user_id ON memories (user_id)"))
    conn.execute(
        text(
            "CREATE INDEX IF NOT EXISTS idx_memories_embedding_cosine "
            "ON memories USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)"
        )
    )

app = FastAPI(title="StashSave Ingestion API")
logger = logging.getLogger(__name__)

allowed_origins = os.getenv(
    "FRONTEND_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173",
).split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in allowed_origins if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------
# Dependency: DB session
# -------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -------------------------
# Health check
# -------------------------
@app.get("/")
def root():
    return {"status": "ok", "service": "stashsave-ingestion"}


# -------------------------
# GitHub Stars Ingestion
# -------------------------
@app.post("/ingest/github/{user_id}", status_code=201)
def ingest_github(user_id: str, access_token: str, db: Session = Depends(get_db)):
    """
    Ingest real GitHub starred repositories for a user.
    """
    try:
        count = ingest_github_stars(db, user_id, access_token)
        return {"source": "github", "ingested": count}
    except Exception as exc:
        logger.exception("GitHub ingestion failed for user_id=%s", user_id)
        raise HTTPException(status_code=500, detail=f"GitHub ingestion failed: {exc}")


# Search API
@app.get("/search")
def search(query: str, user_id: str, top_k: int = 5):
    results = semantic_search(query=query, user_id=user_id, top_k=top_k)
    return {"query": query, "user_id": user_id, "results": results}
