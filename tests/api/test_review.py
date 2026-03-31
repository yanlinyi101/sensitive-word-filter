def test_review_returns_structure(seeded_client):
    resp = seeded_client.post("/api/review", json={"text": "这是普通内容。", "doc_type": "live"})
    assert resp.status_code == 200
    data = resp.json()
    assert "session_id" in data
    assert "sentences" in data
    assert isinstance(data["sentences"], list)

def test_review_detects_risk_word(seeded_client):
    resp = seeded_client.post("/api/review", json={"text": "根治糖尿病。", "doc_type": "live"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["sentences"][0]["risk_level"] == 3
    assert any(m["word"] == "根治" for m in data["sentences"][0]["matched_words"])

def test_review_saves_to_history(seeded_client, db_session):
    from app.db.models import ReviewSession
    seeded_client.post("/api/review", json={"text": "测试文稿。", "doc_type": "live"})
    assert db_session.query(ReviewSession).count() == 1

def test_review_empty_text_returns_empty(seeded_client):
    resp = seeded_client.post("/api/review", json={"text": "", "doc_type": "live"})
    assert resp.status_code == 200
    assert resp.json()["sentences"] == []
