import time
import asyncio
from sihbackend.services.chat_service import _get_vectorstores
from sihbackend.services.reranker import get_reranker

print("1. Starting initialization test...")
start = time.time()

print("2. Initializing vectorstores (and downloading MiniLM)...")
_get_vectorstores()
print(f"   -> Vectorstores initialized in {time.time() - start:.2f}s")

start = time.time()
print("3. Initializing reranker (and downloading BGE-reranker)...")
get_reranker()
print(f"   -> Reranker initialized in {time.time() - start:.2f}s")

print("Initialization test completed successfully.")
