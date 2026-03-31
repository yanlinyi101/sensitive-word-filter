def test_list_wordlist_empty(client):
    resp = client.get("/api/wordlist")
    assert resp.status_code == 200
    assert resp.json()["items"] == []

def test_create_word(client):
    resp = client.post("/api/wordlist", json={"word": "根治", "category": "医疗", "risk_level": 3})
    assert resp.status_code == 200
    data = resp.json()
    assert data["word"] == "根治"
    assert data["id"] is not None

def test_create_duplicate_returns_409(client):
    client.post("/api/wordlist", json={"word": "根治", "category": "医疗", "risk_level": 3})
    resp = client.post("/api/wordlist", json={"word": "根治", "category": "医疗", "risk_level": 3})
    assert resp.status_code == 409

def test_update_word(client):
    create = client.post("/api/wordlist", json={"word": "根治", "category": "医疗", "risk_level": 3})
    wid = create.json()["id"]
    resp = client.put(f"/api/wordlist/{wid}", json={"risk_level": 2})
    assert resp.status_code == 200
    assert resp.json()["risk_level"] == 2

def test_delete_word(client):
    create = client.post("/api/wordlist", json={"word": "根治", "category": "医疗", "risk_level": 3})
    wid = create.json()["id"]
    resp = client.delete(f"/api/wordlist/{wid}")
    assert resp.status_code == 200
    assert client.get("/api/wordlist").json()["items"] == []
