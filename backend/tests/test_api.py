from fastapi.testclient import TestClient
from app.main import app
 
client = TestClient(app)
 
 
def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
 
 
def test_predict_endpoint():
    response = client.post("/api/predict", json={"url": "https://example.com"})
    assert response.status_code == 200
 
    body = response.json()
    assert isinstance(body["is_phishing"], bool)
    assert 0.0 <= body["confidence"] <= 1.0
    assert body["url"] == "https://example.com"
    # Deliberately no assertion on WHICH verdict: the test checks the API contract, not model behavior (which is documented as invalid).
 