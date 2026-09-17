import pytest
from unittest.mock import patch, MagicMock
from langchain_core.documents import Document
from langchain_core.runnables import RunnableLambda
from sihbackend.schemas.analysis import AnalysisResponse
from sihbackend.services.generation import generate_answer, format_documents

def make_mock_llm(response_obj):
    class MockLLM:
        def with_structured_output(self, schema):
            return RunnableLambda(lambda x: response_obj)
    return MockLLM()

def test_context_supported_factual_answer():
    docs = [
        Document(
            page_content="Applicants must disclose the geographical origin of biological materials.",
            metadata={"filename": "biodiversity_act.pdf", "section": "10"}
        )
    ]
    mock_resp = AnalysisResponse(
        answer="You must disclose the geographical origin.",
        risk_level="medium",
        key_requirements=["Disclose geographical origin"],
        relevant_jurisdictions=[],
        sources=["Document: biodiversity_act.pdf, Section: 10"],
        caveats=[]
    )
    
    with patch("sihbackend.services.generation.get_llm", return_value=make_mock_llm(mock_resp)):
        res = generate_answer("What must applicants disclose?", docs)
        assert "geographical origin" in res.answer
        assert res.key_requirements == ["Disclose geographical origin"]
        assert "Section: 10" in res.sources[0]

def test_insufficient_context():
    docs = [
        Document(
            page_content="Patents cover inventions.",
            metadata={"filename": "patent_law.pdf"}
        )
    ]
    mock_resp = AnalysisResponse(
        answer="The available retrieved evidence is insufficient to answer this question.",
        risk_level="unknown",
        key_requirements=[],
        relevant_jurisdictions=[],
        sources=[],
        caveats=["Insufficient retrieved evidence"]
    )
    
    with patch("sihbackend.services.generation.get_llm", return_value=make_mock_llm(mock_resp)):
        res = generate_answer("What are the rules for genetic resources?", docs)
        assert "insufficient" in res.answer.lower()
        assert res.risk_level == "unknown"

def test_source_layer_distinction():
    docs = [
        Document(
            page_content="Rule 5: No genetic material.",
            metadata={"filename": "law.pdf", "source_layer": "source_material"}
        ),
        Document(
            page_content="Some say Rule 5 means absolutely no biological samples at all.",
            metadata={"filename": "blog.pdf", "source_layer": "interpretation"}
        )
    ]
    formatted = format_documents(docs)
    assert "Source Layer: source_material" in formatted
    assert "Source Layer: interpretation" in formatted

def test_sources_generated_only_from_metadata():
    docs = [
        Document(
            page_content="Test rule.",
            metadata={"filename": "doc1.pdf", "page": 5}
        )
    ]
    formatted = format_documents(docs)
    assert "Document: doc1.pdf" in formatted
    assert "Page: 5" in formatted
    assert "Source URL" not in formatted

def test_missing_source_url():
    docs = [
        Document(
            page_content="Test rule without URL.",
            metadata={"filename": "doc_no_url.pdf"}
        )
    ]
    formatted = format_documents(docs)
    assert "Source URL:" not in formatted
    
def test_insufficient_evidence_risk_unknown():
    # Test explicitly passing empty list
    res = generate_answer("Does the law allow this?", [])
    assert res.risk_level == "unknown"
    assert res.answer == "There is insufficient retrieved evidence to answer the query."
    assert res.sources == []
