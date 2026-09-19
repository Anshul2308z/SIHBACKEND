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
        # chromadb ef expects and returns lists
        return self.ef(texts)
        
    def embed_query(self, text: str) -> List[float]:
        return self.ef([text])[0]

def get_embeddings_model() -> FastONNXEmbeddings:
    """Returns the lightweight ONNX embeddings model instance."""
    return FastONNXEmbeddings()
