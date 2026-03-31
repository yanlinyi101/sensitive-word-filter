import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.database import Base, get_db
from app.db.models import WordlistEntry, Rule

@pytest.fixture
def db_engine():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)

@pytest.fixture
def db_session(db_engine):
    Session = sessionmaker(bind=db_engine)
    session = Session()
    yield session
    session.close()

@pytest.fixture
def client(db_session):
    from app.main import app
    def override():
        yield db_session
    app.dependency_overrides[get_db] = override
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture
def seeded_client(client, db_session):
    db_session.add(WordlistEntry(word="根治", category="医疗", risk_level=3, enabled=True, source="houbb"))
    db_session.add(WordlistEntry(word="特效", category="医疗", risk_level=2, enabled=True, source="houbb"))
    db_session.commit()
    return client
