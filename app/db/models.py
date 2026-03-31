import datetime
from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

def _now():
    return datetime.datetime.utcnow().isoformat()

class WordlistEntry(Base):
    __tablename__ = "wordlist_entries"
    id = Column(Integer, primary_key=True, index=True)
    word = Column(String, nullable=False, unique=True)
    category = Column(String, default="自定义")
    risk_level = Column(Integer, nullable=False)  # 1/2/3
    enabled = Column(Boolean, default=True)
    source = Column(String, default="custom")  # houbb | custom
    created_at = Column(String, default=_now)
    updated_at = Column(String, default=_now, onupdate=_now)

class Rule(Base):
    __tablename__ = "rules"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, default="")
    conditions = Column(Text, nullable=False)  # JSON string
    risk_level = Column(Integer, nullable=False)  # 1/2/3
    enabled = Column(Boolean, default=True)
    priority = Column(Integer, default=0)
    created_at = Column(String, default=_now)
    updated_at = Column(String, default=_now, onupdate=_now)

class ReviewSession(Base):
    __tablename__ = "review_sessions"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, default="")
    raw_text = Column(Text)
    doc_type = Column(String, default="live")  # live | documentary
    created_at = Column(String, default=_now)
    results = relationship("SentenceResult", back_populates="session", cascade="all, delete-orphan")

class SentenceResult(Base):
    __tablename__ = "sentence_results"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("review_sessions.id"))
    sentence_index = Column(Integer)
    text = Column(Text)
    risk_level = Column(Integer, default=0)  # 0=无 1=低 2=中 3=高
    matched_words = Column(Text, default="[]")   # JSON
    triggered_rules = Column(Text, default="[]") # JSON
    llm_confirmed_risk = Column(String, default="skipped")
    llm_suggestion = Column(Text, default="")
    created_at = Column(String, default=_now)
    session = relationship("ReviewSession", back_populates="results")
