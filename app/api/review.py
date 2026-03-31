import json
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import ReviewSession, SentenceResult as SentenceResultDB
from app.pipeline.pipeline import run_pipeline

router = APIRouter()

class ReviewRequest(BaseModel):
    text: str
    doc_type: str = "live"

@router.post("/review")
def review(req: ReviewRequest, db: Session = Depends(get_db)):
    results = run_pipeline(req.text, req.doc_type, db)

    session = ReviewSession(raw_text=req.text, doc_type=req.doc_type)
    db.add(session)
    db.flush()

    for r in results:
        db.add(SentenceResultDB(
            session_id=session.id,
            sentence_index=r.index,
            text=r.text,
            risk_level=r.risk_level,
            matched_words=json.dumps(
                [{"word": m.word, "category": m.category, "risk_level": m.risk_level}
                 for m in r.matched_words],
                ensure_ascii=False
            ),
            triggered_rules=json.dumps(r.triggered_rules, ensure_ascii=False),
            llm_confirmed_risk=r.llm_confirmed_risk or "skipped",
            llm_suggestion=r.llm_suggestion or "",
        ))
    db.commit()

    return {
        "session_id": session.id,
        "sentences": [
            {
                "index": r.index,
                "text": r.text,
                "risk_level": r.risk_level,
                "matched_words": [
                    {"word": m.word, "category": m.category, "risk_level": m.risk_level}
                    for m in r.matched_words
                ],
                "triggered_rules": r.triggered_rules,
                "llm_confirmed_risk": r.llm_confirmed_risk or "skipped",
                "llm_suggestion": r.llm_suggestion or "",
            }
            for r in results
        ],
    }
