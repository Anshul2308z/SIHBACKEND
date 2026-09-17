from langchain_core.documents import Document
from sihbackend.rag.chunker import chunk_documents, DocumentClassifier, StructureAwareChunker

def test_classifier():
    assert DocumentClassifier.classify("INDIA — PATENT & TRADEMARK LAWS", "Indian Law.pdf") == "legal_section"
    assert DocumentClassifier.classify("WIPO GRATK TREATY", "wipo treaty law.pdf") == "legal_article"

def test_structural_context_retention():
    long_text = "\nSection 1\n" + ("word " * 1000)
    docs = [Document(page_content=long_text, metadata={"source": "fake/Indian Law.pdf", "page": 1})]
    chunks = chunk_documents(docs)
    
    assert len(chunks) > 1
    assert "[continuation]" in chunks[1].page_content
    assert "Section 1" in chunks[1].page_content

def test_metadata_extraction():
    docs = [
        Document(
            page_content="Intro\nSection 64\nThis is the section.",
            metadata={"source": "fake/Indian Law.pdf", "page": 1}
        )
    ]
    chunks = chunk_documents(docs)
    assert chunks[1].metadata["section"] == "64"
    assert chunks[1].metadata["filename"] == "Indian Law.pdf"

def test_title_extraction():
    chunker = StructureAwareChunker()
    title = chunker._get_document_title("corpus/fssai regulations.pdf")
    assert title == "fssai regulations"
    
def test_wipo_source_authority():
    docs = [
        Document(
            page_content="Intro\nArticle 10\nRule / content\nThe rule is X.",
            metadata={"source": "fake/wipo treaty law.pdf", "page": 1}
        )
    ]
    chunks = chunk_documents(docs)
    assert chunks[1].metadata["source_layer"] == "source_material"
