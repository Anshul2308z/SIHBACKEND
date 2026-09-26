# SIH Backend - IP Risk Analysis

A FastAPI-based backend application for IP-risk analysis leveraging Retrieval-Augmented Generation (RAG).

## Prerequisites
- Python >=3.13
- [`uv`](https://docs.astral.sh/uv/) (Python package manager)

## Project Structure
- `src/sihbackend/`: The main application package.
  - `api/`: FastAPI route handlers (endpoints).
  - `schemas/`: Pydantic models for request and response validation.
  - `services/`: Core business logic and service layers.
  - `rag/`: RAG pipeline modules (document loading, chunking, embeddings, vector store).
- `scripts/`: Standalone scripts for testing and populating the RAG vector store.
- `tests/`: Pytest suite for testing the API.
- `corpus/`: Raw source documents for the RAG pipeline (e.g., PDFs).
- `vectorstore/`: Local ChromaDB persistent storage.

## Setup & Running

This project uses `uv` to manage dependencies seamlessly without needing to manually activate virtual environments.

### 1. Start the API Server
To start the FastAPI development server with hot-reloading:

```bash
uv run uvicorn sihbackend.main:app --reload
```
The API will be available at `http://localhost:8000`. 
- Interactive API documentation (Swagger UI) is available at `http://localhost:8000/docs`.
- Health check: `curl http://localhost:8000/health`

### 2. RAG Pipeline Scripts
To run the RAG document ingestion pipeline:
```bash
uv run scripts/ingest_legal.py
```

To run a test query against the populated vector database:
```bash
uv run scripts/query_legal.py
```

### 3. Run Tests
The project uses `pytest` for testing. To execute the test suite:
```bash
uv run pytest
```

## Supported LLM Models
The application relies on specific Large Language Models depending on your configuration. You can switch models by setting `ACTIVE_LLM` in your `.env` file:

- **Google (Gemini)**: `gemini-3.6-flash` (Set `ACTIVE_LLM="google"`)
- **OpenAI**: `gpt-4o-mini` (Set `ACTIVE_LLM="openai"`)
- **Groq**: `groq/compound` (Set `ACTIVE_LLM="groq"`)
- **Mistral**: `mistral-large-latest` (Set `ACTIVE_LLM="mistral"`)
