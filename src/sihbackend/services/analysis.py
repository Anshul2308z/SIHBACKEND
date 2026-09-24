import os
from sihbackend.schemas.analysis import AnalysisRequest, AnalysisResponse
from sihbackend.services.generation import generate_answer
from sihbackend.rag.embeddings import get_embeddings_model
from sihbackend.rag.vectorstore import get_vectorstore
from sihbackend.rag.metadata_aware_retriever import MetadataAwareRetriever

def perform_analysis(request: AnalysisRequest) -> AnalysisResponse:
    query = request.query
    
    # 1. Initialize Retrieval (Using the FROZEN safe fallback retriever)
    embeddings = get_embeddings_model()
    index_name = os.environ.get("PINECONE_INDEX_NAME", "sihbackend")
    vectorstore = get_vectorstore(embeddings, index_name, namespace="legal")
    
    # K=5 is standard for our tests
    retriever = MetadataAwareRetriever(vectorstore, use_fallback=True, k=5)
    
    # 2. Retrieve documents
    retrieved_documents, log_info = retriever.search(query)
    
    # 3. Generate answer grounded in retrieved documents
    response = generate_answer(query, retrieved_documents)
    
    return response
