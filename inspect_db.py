from langchain_chroma import Chroma
from sihbackend.rag.embeddings import get_embeddings_model
import json

emb = get_embeddings_model()
pa_store = Chroma(persist_directory="vectorstore/prior_art", embedding_function=emb)
data = pa_store.get(limit=2)
print(json.dumps(data['metadatas'], indent=2))
print("---")
print(json.dumps(data['documents'][:1], indent=2))
