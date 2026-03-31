from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.database import Base
from app.db.models import WordlistEntry, Rule, ReviewSession, SentenceResult

def test_tables_created():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    assert db.query(WordlistEntry).count() == 0
    assert db.query(Rule).count() == 0
    assert db.query(ReviewSession).count() == 0
    assert db.query(SentenceResult).count() == 0
    db.close()

def test_wordlist_entry_insert():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    entry = WordlistEntry(word="根治", category="医疗", risk_level=3, source="houbb")
    db.add(entry)
    db.commit()
    assert db.query(WordlistEntry).filter_by(word="根治").first() is not None
    db.close()
