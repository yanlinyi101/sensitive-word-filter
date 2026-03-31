# tests/test_seed.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.database import Base
from app.db.models import WordlistEntry
from app.db.seed import seed_from_file
import tempfile, os

def test_seed_imports_words():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    content = "根治,医疗,3\n特效,医疗,2\n最低价,广告法,2\n"
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write(content)
        path = f.name

    seed_from_file(db, path)
    assert db.query(WordlistEntry).count() == 3
    entry = db.query(WordlistEntry).filter_by(word="根治").first()
    assert entry.category == "医疗"
    assert entry.risk_level == 3
    assert entry.source == "houbb"
    os.unlink(path)
    db.close()

def test_seed_skips_duplicates():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    content = "根治,医疗,3\n根治,医疗,3\n"
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write(content)
        path = f.name
    seed_from_file(db, path)
    assert db.query(WordlistEntry).count() == 1
    os.unlink(path)
    db.close()
