from langchain_pinecone import PineconeVectorStore
from typing import List
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

def create_or_update_vectorstore(documents: List[Document], embeddings: Embeddings, index_name: str, namespace: str = "") -> PineconeVectorStore:
    """Creates or updates a Pinecone vectorstore from documents."""
    return PineconeVectorStore.from_documents(
        documents=documents,
        embedding=embeddings,
        index_name=index_name,
        namespace=namespace
    )

def get_vectorstore(embeddings: Embeddings, index_name: str, namespace: str = "") -> PineconeVectorStore:
    """Loads an existing Pinecone vectorstore."""
    return PineconeVectorStore(
        embedding=embeddings,
        index_name=index_name,
        namespace=namespace
    )
