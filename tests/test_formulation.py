import pytest
import os
from fastapi.testclient import TestClient
from sihbackend.main import app
from langchain_pinecone import PineconeVectorStore
from sihbackend.rag.embeddings import get_embeddings_model

client = TestClient(app)

def test_raw_pinecone_legal_formulation():
    """Safety Net 1: Verify exact database output for formulation logic.
    Ensures that queries related to 'Phytopharmaceutical', 'Nutraceutical', or 'Ayurveda-Aahar'
    actually exist in our legal knowledge base to fuel the LLM.
    """
    emb = get_embeddings_model()
    index_name = os.environ.get("PINECONE_INDEX_NAME", "sihbackend")
    leg_store = PineconeVectorStore(index_name=index_name, embedding=emb, namespace="legal")
    
    query = "Phytopharmaceutical CDSCO regulations"
    results = leg_store.similarity_search_with_score(query, k=2)
    
    # We expect to find legal documents in the vectorstore
    assert len(results) > 0, "Pinecone returned no legal results for phytopharmaceutical!"
    
    doc, score = results[0]
    assert isinstance(score, float)
    assert "source" in doc.metadata

def test_formulation_endpoint_schema():
    """Safety Net 2: Verify the formulation endpoint strictly matches the frontend's output interface."""
    payload = {
        "product": "Ashwagandha stress relief syrup",
        "classical": "Partly — classical base with modifications",
        "novelty": "No — whole herb or classical extract",
        "claim": "Therapeutic indication",
        "route": "Oral medicine form"
    }
    
    response = client.post("/api/v1/analyze/formulation", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    
    required_fields = ["label", "confidence", "reasoning", "route", "authorities", "ip"]
    for field in required_fields:
        assert field in data, f"Missing {field} in response"
        
    assert isinstance(data["confidence"], int)
    assert isinstance(data["authorities"], list)
    assert isinstance(data["ip"], list)

def test_formulation_endpoint_classification():
    """Safety Net 3: Verify the formulation engine accurately identifies Cosmetics."""
    payload = {
        "product": "Neem skin glowing cream",
        "classical": "No — the composition is newly developed",
        "novelty": "No — whole herb or classical extract",
        "claim": "Cosmetic or external appearance benefit",
        "route": "Topical application"
    }
    
    response = client.post("/api/v1/analyze/formulation", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    
    # The classification label should mention "Cosmetic"
    assert "Cosmetic" in data["label"], f"Failed to classify a cosmetic product! Got {data['label']}"
