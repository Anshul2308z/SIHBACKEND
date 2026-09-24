import os
import pytest
from fastapi.testclient import TestClient
from sihbackend.main import app
from langchain_pinecone import PineconeVectorStore
from sihbackend.rag.embeddings import get_embeddings_model

client = TestClient(app)

def test_raw_chroma_semantic_search():
    """Safety Net 1: Verify exact database output instead of logic.
    Ensures that a query for 'Turmeric' actually returns vectors and we can read their raw L2 distances.
    """
    emb = get_embeddings_model()
    pa_store = PineconeVectorStore(index_name=os.environ.get("PINECONE_INDEX_NAME", "sihbackend"), embedding=emb, namespace="prior_art")
    
    query = "turmeric and neem skin inflammation"
    results = pa_store.similarity_search_with_score(query, k=3)
    
    assert len(results) > 0, "ChromaDB returned no results for a basic query!"
    
    # Verify the exact data structure from DB
    doc, score = results[0]
    assert isinstance(score, float)
    assert "plant_family" in doc.metadata
    assert "source" in doc.metadata

def test_patents_search_schema():
    """Safety Net 2: Verify the endpoint strictly matches the frontend's PatentRecord interface."""
    payload = {
        "query": "herbal formulation using turmeric and neem",
        "scope": "Both",
        "type": "Semantic",
        "activeSources": ["TKDL", "IP India"],
        "plant": "All",
        "status": "All"
    }
    
    response = client.post("/api/v1/patents/search", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    
    if len(data) > 0:
        first = data[0]
        # Check against frontend PatentRecord structure
        required_fields = ["id", "number", "title", "applicant", "jurisdiction", 
                           "similarity", "status", "risk", "whyRelevant", "plants"]
        for field in required_fields:
            assert field in first, f"Missing {field} in response"
            
        assert isinstance(first["similarity"], int) # UI expects an integer percentage (e.g. 91)

def test_patents_search_filters():
    """Safety Net 3: Verify the endpoint accurately filters based on scope/jurisdiction."""
    payload = {
        "query": "Ashwagandha stress relief",
        "scope": "International", # Should only return International records
        "type": "Semantic",
        "activeSources": ["WIPO", "EPO"],
        "plant": "All",
        "status": "All"
    }
    
    response = client.post("/api/v1/patents/search", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    for record in data:
        # If the DB has international records, it should only return those
        assert record["jurisdictionGroup"] == "International", f"Filter failed for record {record['id']}"
