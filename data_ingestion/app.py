from pathlib import Path
import json

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from embeddings.search import semantic_search  

from data_ingestion.github_memory.db import SessionLocal, engine, Base
from data_ingestion.github_memory.ingest import ingest_github_stars
from data_ingestion.instagram_memory.enrich_instagram import enrich_instagram_rows
from data_ingestion.whatsapp_memory.enrich_whatsapp import enrich_whatsapp_rows


# Create DB tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="StashSave Ingestion API")
BASE_DIR = Path(__file__).resolve().parent
INSTAGRAM_PATH = BASE_DIR / "instagram_memory" / "mock_instagram.json"
WHATSAPP_PATH = BASE_DIR / "whatsapp_memory" / "mock_whatsapp.json"


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
def ingest_github(user_id: int, access_token: str, db: Session = Depends(get_db)):
    """
    Ingest real GitHub starred repositories for a user.
    """
    try:
        count = ingest_github_stars(db, user_id, access_token)
        return {"source": "github", "ingested": count}
    except Exception:
        raise HTTPException(status_code=500, detail="GitHub ingestion failed")


# -------------------------
# Instagram Mock Ingestion
# -------------------------
@app.post("/ingest/instagram/{user_id}", status_code=201)
def ingest_instagram(user_id: int, db: Session = Depends(get_db)):
    """
    Ingest mocked Instagram saved tools → enrich → Memory table.
    """
    if not INSTAGRAM_PATH.exists():
        raise HTTPException(status_code=404, detail="Mock Instagram data not found")

    try:
        with INSTAGRAM_PATH.open("r", encoding="utf-8") as f:
            rows = json.load(f)

        count = enrich_instagram_rows(db, user_id, rows)
        return {"source": "instagram", "ingested": count}

    except Exception:
        raise HTTPException(status_code=500, detail="Instagram ingestion failed")


# -------------------------
# WhatsApp Mock Ingestion
# -------------------------
@app.post("/ingest/whatsapp/{user_id}", status_code=201)
def ingest_whatsapp(user_id: int, db: Session = Depends(get_db)):
    """
    Ingest mocked WhatsApp tool mentions → enrich → Memory table.
    """
    if not WHATSAPP_PATH.exists():
        raise HTTPException(status_code=404, detail="Mock WhatsApp data not found")

    try:
        with WHATSAPP_PATH.open("r", encoding="utf-8") as f:
            rows = json.load(f)

        count = enrich_whatsapp_rows(db, user_id, rows)
        return {"source": "whatsapp", "ingested": count}

    except Exception:
        raise HTTPException(status_code=500, detail="WhatsApp ingestion failed")


#Search API
@app.get("/search")
def search(query: str, user_id: int, top_k: int = 5):
    results = semantic_search(query=query, user_id=user_id, top_k=top_k)
    return {"query": query, "user_id": user_id, "results": results}
