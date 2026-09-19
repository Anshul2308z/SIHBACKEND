from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from sihbackend.api import health, analyze, chat, prior_art, translate, expert

@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Lifespan startup: Pre-loading heavy RAG models and vectorstores...")
    try:
        from sihbackend.services.chat_service import _get_vectorstores
        from sihbackend.services.reranker import get_reranker
        # This will download the MiniLM and BGE-reranker models on boot before accepting traffic
        _get_vectorstores()
        get_reranker()
        logging.info("Lifespan startup complete. Models loaded successfully.")
    except Exception as e:
        logging.error(f"Failed to initialize models during startup: {e}")
    yield
    logging.info("Lifespan shutdown: Cleaning up resources...")

app = FastAPI(
    title="SIH Backend - IP Risk Analysis",
    description="Backend service for IP Risk Analysis using RAG",
    version="0.1.0",
    lifespan=lifespan,
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(health.router)
app.include_router(analyze.router)
app.include_router(chat.router)
app.include_router(prior_art.router)
app.include_router(translate.router)
app.include_router(expert.router)
