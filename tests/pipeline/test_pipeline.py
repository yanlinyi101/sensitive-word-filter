from unittest.mock import patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.database import Base
from app.db.models import WordlistEntry, Rule
from app.pipeline.pipeline import run_pipeline

def _make_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    db.add(WordlistEntry(word="根治", category="医疗", risk_level=3, enabled=True, source="houbb"))
    db.add(WordlistEntry(word="特效", category="医疗", risk_level=2, enabled=True, source="houbb"))
    db.commit()
    return db

def test_clean_text_has_zero_risk():
    db = _make_db()
    results = run_pipeline("这是一款普通产品。效果不错。", "live", db)
    assert all(r.risk_level == 0 for r in results)
    db.close()

def test_risk_word_detected():
    db = _make_db()
    results = run_pipeline("这款产品能根治糖尿病。", "live", db)
    assert results[0].risk_level == 3
    assert any(m.word == "根治" for m in results[0].matched_words)
    db.close()

def test_pipeline_returns_one_result_per_sentence():
    db = _make_db()
    results = run_pipeline("第一句。第二句。第三句。", "live", db)
    assert len(results) == 3
    db.close()

def test_llm_not_called_for_low_risk():
    db = _make_db()
    with patch("app.pipeline.pipeline.LLMReviewer") as MockLLM:
        run_pipeline("这是普通内容。安全文本。", "live", db)
        MockLLM.assert_not_called()
    db.close()
