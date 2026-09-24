import os
import os
from sihbackend.rag.embeddings import get_embeddings_model
from langchain_pinecone import PineconeVectorStore

def test_retrieval():
    persist_dir = "vectorstore/prior_art"
    embeddings = get_embeddings_model()
    
    print("Loading Pinecone vectorstore...")
    index_name = os.environ.get("PINECONE_INDEX_NAME", "sihbackend")
    vectorstore = PineconeVectorStore(
        index_name=index_name,
        embedding=embeddings,
        namespace="prior_art"
    )
    
    query = "Neem extract for treating skin conditions like acne or psoriasis"
    print(f"\nQuerying: '{query}'")
    
    results = vectorstore.similarity_search_with_score(query, k=3)
    
    print("\n--- Results ---")
    if not results:
        print("No results found.")
    for doc, score in results:
        print(f"Score: {score:.4f} | Plant: {doc.metadata.get('plant_family')} | File: {doc.metadata.get('source')} (Page {doc.metadata.get('page')})")
        print(f"Content Snippet: {doc.page_content[:150].strip()}...\n")

if __name__ == "__main__":
    test_retrieval()
