import os
from langchain_pinecone import PineconeVectorStore
from sihbackend.rag.embeddings import get_embeddings_model
import json

emb = get_embeddings_model()
pa_store = PineconeVectorStore(index_name=os.environ.get("PINECONE_INDEX_NAME", "sihbackend"), embedding=emb, namespace="prior_art")
data = pa_store.get(limit=2)
print(json.dumps(data['metadatas'], indent=2))
print("---")
print(json.dumps(data['documents'][:1], indent=2))
