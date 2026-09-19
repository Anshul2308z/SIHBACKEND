from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os

from sihbackend.api import health, analyze, chat, prior_art, translate, expert

@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Lifespan startup: Pre-loading heavy RAG models and vectorstores...")
    try:
        # Aggressively limit PyTorch memory/thread footprint for Render's 512MB RAM limit
        import torch
        torch.set_num_threads(1)
        os.environ["OMP_NUM_THREADS"] = "1"
        os.environ["MKL_NUM_THREADS"] = "1"
        
        from sihbackend.services.chat_service import _get_vectorstores
        # This will download the MiniLM models on boot before accepting traffic
        _get_vectorstores()
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
