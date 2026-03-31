from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import WordlistEntry

router = APIRouter()

class WordCreate(BaseModel):
    word: str
    category: str = "自定义"
    risk_level: int
    enabled: bool = True

class WordUpdate(BaseModel):
    category: Optional[str] = None
    risk_level: Optional[int] = None
    enabled: Optional[bool] = None

def _serialize(e: WordlistEntry):
    return {"id": e.id, "word": e.word, "category": e.category,
            "risk_level": e.risk_level, "enabled": e.enabled, "source": e.source}

@router.get("/wordlist")
def list_words(search: str = "", page: int = 1, page_size: int = 50, db: Session = Depends(get_db)):
    q = db.query(WordlistEntry)
    if search:
        q = q.filter(WordlistEntry.word.contains(search))
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    return {"total": total, "items": [_serialize(e) for e in items]}

@router.post("/wordlist")
def create_word(body: WordCreate, db: Session = Depends(get_db)):
    if db.query(WordlistEntry).filter_by(word=body.word).first():
        raise HTTPException(status_code=409, detail="词条已存在")
    entry = WordlistEntry(word=body.word, category=body.category,
                          risk_level=body.risk_level, enabled=body.enabled, source="custom")
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return _serialize(entry)

@router.put("/wordlist/{wid}")
def update_word(wid: int, body: WordUpdate, db: Session = Depends(get_db)):
    entry = db.get(WordlistEntry, wid)
    if not entry:
        raise HTTPException(status_code=404, detail="词条不存在")
    if body.category is not None:
        entry.category = body.category
    if body.risk_level is not None:
        entry.risk_level = body.risk_level
    if body.enabled is not None:
        entry.enabled = body.enabled
    db.commit()
    db.refresh(entry)
    return _serialize(entry)

@router.delete("/wordlist/{wid}")
def delete_word(wid: int, db: Session = Depends(get_db)):
    entry = db.get(WordlistEntry, wid)
    if not entry:
        raise HTTPException(status_code=404, detail="词条不存在")
    db.delete(entry)
    db.commit()
    return {"ok": True}
