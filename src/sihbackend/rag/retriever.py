from langchain_chroma import Chroma
from typing import List
from langchain_core.documents import Document

def search_similar_documents(vectorstore: Chroma, query: str, k: int = 3) -> List[Document]:
    """Searches the vectorstore for documents similar to the query."""
    return vectorstore.similarity_search(query, k=k)
