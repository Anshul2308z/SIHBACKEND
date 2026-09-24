from typing import List
from chromadb.utils import embedding_functions

# We wrap Chroma's extremely fast and lightweight ONNX embedding function 
# so it matches LangChain's Embeddings interface. This allows us to completely 
# remove PyTorch from the project and boot instantly on Render's 512MB RAM tier.
class FastONNXEmbeddings:
    def __init__(self):
        # This downloads a tiny ~80MB ONNX version of all-MiniLM-L6-v2.
        # It requires NO PyTorch, NO sentence-transformers, and boots instantly.
        self.ef = embedding_functions.DefaultEmbeddingFunction()
        
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        # chromadb ef expects and returns lists, but might return ndarray inside
        embeddings = self.ef(texts)
        if hasattr(embeddings, "tolist"):
            return embeddings.tolist()
        if isinstance(embeddings, list) and len(embeddings) > 0 and hasattr(embeddings[0], "tolist"):
            return [e.tolist() for e in embeddings]
        return embeddings
        
    def embed_query(self, text: str) -> List[float]:
        embedding = self.ef([text])[0]
        if hasattr(embedding, "tolist"):
            return embedding.tolist()
        return embedding

def get_embeddings_model() -> FastONNXEmbeddings:
    """Returns the lightweight ONNX embeddings model instance."""
    return FastONNXEmbeddings()
