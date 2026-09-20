import pytest
from fastapi.testclient import TestClient
from sihbackend.main import app
from langchain_chroma import Chroma
from sihbackend.rag.embeddings import get_embeddings_model

client = TestClient(app)

def test_raw_chroma_legal_abs():
    """Safety Net 1: Verify exact database output for ABS legal context.
    Ensures that queries related to 'Biological Diversity Act' or 'ABS'
    actually exist in our legal knowledge base.
    """
    emb = get_embeddings_model()
    leg_store = Chroma(persist_directory="vectorstore/legal", embedding_function=emb)
    
    query = "Biological Diversity Act Access and Benefit Sharing NBA approval"
    results = leg_store.similarity_search_with_score(query, k=2)
    
    assert len(results) > 0, "ChromaDB returned no legal results for ABS!"
    
    doc, score = results[0]
    assert isinstance(score, float)
    assert "source" in doc.metadata

def test_abs_endpoint_schema():
    """Safety Net 2: Verify the ABS endpoint strictly matches the frontend's output interface."""
    payload = {
        "resource": "Withania somnifera",
        "origin": "India",
        "collection": "Wild-collected",
        "tk": True,
        "commercial": True,
        "patent": True,
        "exportMarket": True
    }
    
    response = client.post("/api/v1/compliance/abs", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    
    assert "status" in data
    assert "level" in data["status"]
    assert "label" in data["status"]
    assert "framework" in data
    assert "reasoning" in data
    
    assert isinstance(data["framework"], list)
    assert data["status"]["level"] in ["risk", "review", "verified"]

def test_abs_endpoint_risk_level():
    """Safety Net 3: Verify the ABS engine accurately identifies a high-risk commercial scenario."""
    payload = {
        "resource": "Curcuma longa",
        "origin": "India",
        "collection": "Wild-collected",
        "tk": True,
        "commercial": True,
        "patent": True,
        "exportMarket": True
    }
    
    response = client.post("/api/v1/compliance/abs", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    # An Indian wild-collected plant with TK used commercially MUST require review or risk
    assert data["status"]["level"] in ["risk", "review"], "Failed to flag high-risk ABS scenario!"
