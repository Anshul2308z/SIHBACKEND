import json
from langchain_chroma import Chroma
from sihbackend.rag.embeddings import get_embeddings_model
from sihbackend.services.reranker import rerank_documents

def run_reranker_eval():
    print("=== Phase 4 Cross-Encoder Evaluation ===\n")
    
    embeddings = get_embeddings_model()
    vectorstore = Chroma(
        persist_directory="vectorstore/prior_art",
        embedding_function=embeddings
    )
    
    query = "Neem extract for treating skin conditions like acne or psoriasis"
    print(f"Query: '{query}'\n")
    
    print("1. Executing Chroma Dense Retrieval (k=15)...")
    dense_results = vectorstore.similarity_search_with_score(query, k=15)
    
    print("\n--- Top 3 Before Reranking (Chroma L2 Distance - Lower is better) ---")
    for i, (doc, distance) in enumerate(dense_results[:3]):
        content_snippet = doc.page_content.replace('\n', ' ')[:120]
        print(f"{i+1}. L2: {distance:.4f} | Source: {doc.metadata.get('source')} | Preview: {content_snippet}...")
        
    print("\n2. Executing Cross-Encoder Reranking...")
    reranked_results = rerank_documents(query, dense_results, top_k=5)
    
    print("\n--- Top 5 After Reranking (Cross-Encoder Score - Higher is better) ---")
    for i, (doc, original_dist, rerank_score) in enumerate(reranked_results):
        content_snippet = doc.page_content.replace('\n', ' ')[:120]
        print(f"{i+1}. Rerank Score: {rerank_score:.4f} | Original L2: {original_dist:.4f} | Source: {doc.metadata.get('source')}")
        print(f"   Preview: {content_snippet}...\n")

if __name__ == "__main__":
    run_reranker_eval()
