from langchain_chroma import Chroma
from typing import List
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

def create_or_update_vectorstore(documents: List[Document], embeddings: Embeddings, persist_directory: str) -> Chroma:
    """Creates or updates a Chroma vectorstore from documents."""
    return Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=persist_directory,
    )

def get_vectorstore(embeddings: Embeddings, persist_directory: str) -> Chroma:
    """Loads an existing Chroma vectorstore."""
    return Chroma(
        embedding_function=embeddings,
        persist_directory=persist_directory,
    )
