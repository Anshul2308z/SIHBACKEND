from langchain_huggingface import HuggingFaceEmbeddings

def get_embeddings_model(model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> HuggingFaceEmbeddings:
    """Returns the embeddings model instance."""
    return HuggingFaceEmbeddings(model_name=model_name)
