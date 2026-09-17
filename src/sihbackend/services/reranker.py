from typing import List, Tuple
from langchain_core.documents import Document

_reranker_model = None

def get_reranker():
    global _reranker_model
    if _reranker_model is None:
        # Import inside to avoid slow startup if reranking isn't used immediately
        from sentence_transformers import CrossEncoder
        # We select BAAI/bge-reranker-base because it offers a great balance between
        # speed (base size) and state-of-the-art semantic ranking performance, especially
        # useful for distinguishing dense/nuanced patent texts from general matching.
        _reranker_model = CrossEncoder('BAAI/bge-reranker-base')
    return _reranker_model

def rerank_documents(query: str, docs_with_scores: List[Tuple[Document, float]], top_k: int = 5) -> List[Tuple[Document, float, float]]:
    """
    Reranks documents using a CrossEncoder.
    
    Args:
        query: The search query.
        docs_with_scores: A list of tuples containing (Document, original_chroma_l2_distance).
        top_k: Number of top documents to return after reranking.
        
    Returns:
        A list of tuples containing (Document, original_chroma_distance, cross_encoder_score),
        sorted by cross_encoder_score (descending - higher is better).
    """
    if not docs_with_scores:
        return []
        
    reranker = get_reranker()
    
    # Prepare input pairs for the cross-encoder: (query, text)
    pairs = [[query, doc.page_content] for doc, _ in docs_with_scores]
    
    # Get scores
    scores = reranker.predict(pairs)
    
    # Combine docs, original distances, and new scores
    reranked_results = []
    for (doc, original_distance), score in zip(docs_with_scores, scores):
        # We explicitly preserve the original chroma distance and inject the new score
        doc.metadata["chroma_l2_distance"] = float(original_distance)
        doc.metadata["cross_encoder_score"] = float(score)
        reranked_results.append((doc, float(original_distance), float(score)))
        
    # Sort by cross-encoder score descending (higher = better relevance)
    reranked_results.sort(key=lambda x: x[2], reverse=True)
    
    return reranked_results[:top_k]
