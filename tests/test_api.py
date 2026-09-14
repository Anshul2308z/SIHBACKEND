import pytest
from fastapi.testclient import TestClient
from sihbackend.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_analyze_success():
    payload = {"query": "What are the rules for Brazil?"}
    response = client.post("/api/v1/analyze", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    # Assert schema matches the placeholder implementation
    assert "Full analysis is currently unavailable" in data["answer"]
    assert data["risk_level"] is None
    assert data["key_requirements"] == []
    assert data["relevant_jurisdictions"] == []
    assert data["sources"] == []
    assert "The system is in prototype phase" in data["caveats"][0]

def test_analyze_empty_query():
    # Empty query string violates min_length=1
    payload = {"query": ""}
    response = client.post("/api/v1/analyze", json=payload)
    
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    # Verify it points to the query field
    assert data["detail"][0]["loc"] == ["body", "query"]

def test_analyze_missing_query():
    # Missing 'query' key entirely
    payload = {}
    response = client.post("/api/v1/analyze", json=payload)
    
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    assert data["detail"][0]["loc"] == ["body", "query"]
