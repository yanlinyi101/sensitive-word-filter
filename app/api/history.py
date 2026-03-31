import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import ReviewSession, SentenceResult as SentenceResultDB

router = APIRouter()

@router.get("/history")
def list_history(page: int = 1, page_size: int = 20, db: Session = Depends(get_db)):
    q = db.query(ReviewSession).order_by(ReviewSession.id.desc())
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    return {
        "total": total,
        "items": [{"id": s.id, "doc_type": s.doc_type, "created_at": s.created_at,
                   "text_preview": (s.raw_text or "")[:80]} for s in items]
    }

@router.get("/history/{sid}")
def get_history(sid: int, db: Session = Depends(get_db)):
    session = db.get(ReviewSession, sid)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    return {
        "id": session.id,
        "doc_type": session.doc_type,
        "created_at": session.created_at,
        "raw_text": session.raw_text,
        "sentences": [
            {
                "index": r.sentence_index,
                "text": r.text,
                "risk_level": r.risk_level,
                "matched_words": json.loads(r.matched_words or "[]"),
                "triggered_rules": json.loads(r.triggered_rules or "[]"),
                "llm_confirmed_risk": r.llm_confirmed_risk,
                "llm_suggestion": r.llm_suggestion,
            }
            for r in sorted(session.results, key=lambda x: x.sentence_index)
        ],
    }
