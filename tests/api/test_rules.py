import json

VALID_CONDITIONS = json.dumps({
    "conditions": [{"type": "word_match", "words": ["根治"], "op": "any"}],
    "logic": "AND"
})

def test_list_rules_empty(client):
    resp = client.get("/api/rules")
    assert resp.status_code == 200
    assert resp.json() == []

def test_create_rule(client):
    resp = client.post("/api/rules", json={
        "name": "医疗夸大", "description": "检测夸大功效",
        "conditions": VALID_CONDITIONS, "risk_level": 3
    })
    assert resp.status_code == 201
    assert resp.json()["name"] == "医疗夸大"

def test_update_rule_enabled(client):
    create = client.post("/api/rules", json={
        "name": "测试规则", "conditions": VALID_CONDITIONS, "risk_level": 2
    })
    rid = create.json()["id"]
    resp = client.put(f"/api/rules/{rid}", json={"enabled": False})
    assert resp.status_code == 200
    assert resp.json()["enabled"] == False

def test_delete_rule(client):
    create = client.post("/api/rules", json={
        "name": "删除规则", "conditions": VALID_CONDITIONS, "risk_level": 1
    })
    rid = create.json()["id"]
    client.delete(f"/api/rules/{rid}")
    assert client.get("/api/rules").json() == []
