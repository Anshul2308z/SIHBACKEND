# OpenCode Agent Instructions

## Tech Stack & Toolchain
- **Python Manager:** Uses `uv` with Python >=3.13. Always use `uv add`, `uv remove`, and `uv run`. Do not use `pip` or `venv` directly.
- **Framework:** FastAPI for the web server (`src/sihbackend/main.py`).
- **Testing:** `pytest` and `httpx`.
- **AI/RAG:** Langchain, ChromaDB, and HuggingFace sentence-transformers.

## App Architecture
- **Web App (`src/sihbackend/`):**
  - `main.py`: FastAPI application entrypoint. Maps routers.
  - `api/`: API route handlers (e.g., `/health`, `/api/v1/analyze`).
  - `schemas/`: Pydantic request and response models.
  - `services/`: Business logic and orchestration.
  - `rag/`: RAG pipeline modules (document loader, chunker, embeddings, vectorstore, retriever).
- **Scripts (`scripts/`):** Data ingestion and query utility scripts (e.g., `ingest_legal.py`, `query_legal.py`).
- **Tests (`tests/`):** Pytest test cases validating the API layer.
- **Data Directories:**
  - `corpus/`: Contains the raw source documents (like PDFs). 
  - `vectorstore/`: Persistent local ChromaDB vector databases (e.g., `vectorstore/legal/`). Do not track the contents of this folder in git unless specifically required, it is generated data.

## Running the Project
- **Start server:** `uv run uvicorn sihbackend.main:app --reload`
- **Run tests:** `uv run pytest`
- **Ingest data:** `uv run scripts/ingest_legal.py` to rebuild or test the Chroma vectorstore with documents from `corpus/`.
- **Query data:** `uv run scripts/query_legal.py` to test the RAG similarity search output.
