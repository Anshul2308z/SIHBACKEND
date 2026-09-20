from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os
import asyncio

from sihbackend.api import health, analyze, chat, prior_art, translate, expert, patents, formulation

@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Lifespan startup: Port binding immediately. Models will load in background.")
    
    def preload_models():
        try:
            # Aggressively limit PyTorch memory/thread footprint
            import torch
            torch.set_num_threads(1)
            os.environ["OMP_NUM_THREADS"] = "1"
            os.environ["MKL_NUM_THREADS"] = "1"
            
            logging.info("Background thread: Beginning to load ML models...")
            from sihbackend.services.chat_service import _get_vectorstores
            _get_vectorstores()
            logging.info("Background thread: ML Models loaded successfully!")
        except Exception as e:
            logging.error(f"Background thread failed: {e}")

    # Run the heavy loading in a background thread so the server binds the port instantly
    loop = asyncio.get_running_loop()
    loop.run_in_executor(None, preload_models)
    
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
app.include_router(patents.router)
app.include_router(formulation.router)
