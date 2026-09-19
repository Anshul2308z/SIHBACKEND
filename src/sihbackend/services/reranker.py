from typing import List, Tuple
from langchain_core.documents import Document

def get_reranker():
    # Reranker completely disabled to prevent 512MB RAM OOM crash on Render
    return None

def rerank_documents(query: str, docs_with_scores: List[Tuple[Document, float]], top_k: int = 5) -> List[Tuple[Document, float, float]]:
    """
    Bypasses the heavy ML CrossEncoder to save 200MB+ of RAM on Render.
    Relies purely on the extremely fast ChromaDB dense vector search.
    """
    if not docs_with_scores:
        return []
        
    reranked_results = []
    # Chroma already sorts by L2 distance (lower is better). We just take the top_k.
    for doc, original_distance in docs_with_scores[:top_k]:
        doc.metadata["chroma_l2_distance"] = float(original_distance)
        
        # We mock a cross_encoder score (negative distance) so downstream code (like the graph) 
        # doesn't filter it out for being < -2.0. We use a safe baseline like 5.0.
        mock_score = 5.0 
        doc.metadata["cross_encoder_score"] = mock_score
        reranked_results.append((doc, float(original_distance), mock_score))
        
    return reranked_results
