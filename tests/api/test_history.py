def test_history_empty(client):
    resp = client.get("/api/history")
    assert resp.status_code == 200
    assert resp.json()["items"] == []

def test_history_after_review(seeded_client):
    seeded_client.post("/api/review", json={"text": "根治糖尿病。", "doc_type": "live"})
    resp = seeded_client.get("/api/history")
    assert resp.json()["total"] == 1

def test_history_detail(seeded_client):
    seeded_client.post("/api/review", json={"text": "根治糖尿病。", "doc_type": "live"})
    sid = seeded_client.get("/api/history").json()["items"][0]["id"]
    detail = seeded_client.get(f"/api/history/{sid}")
    assert detail.status_code == 200
    assert "sentences" in detail.json()

def test_history_detail_404(client):
    resp = client.get("/api/history/999")
    assert resp.status_code == 404
