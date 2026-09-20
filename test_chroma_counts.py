from langchain_chroma import Chroma
from sihbackend.rag.embeddings import get_embeddings_model
import os

print("BASE DIR:", os.getcwd())
emb = get_embeddings_model()
try:
    pa_store = Chroma(persist_directory="vectorstore/prior_art", embedding_function=emb)
    print("Prior Art count:", len(pa_store.get()['ids']))
except Exception as e:
    print("Error PA:", e)

try:
    leg_store = Chroma(persist_directory="vectorstore/legal", embedding_function=emb)
    print("Legal count:", len(leg_store.get()['ids']))
except Exception as e:
    print("Error Legal:", e)
