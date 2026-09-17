from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sihbackend.api import health, analyze, chat, prior_art

app = FastAPI(
    title="SIH Backend - IP Risk Analysis",
    description="Backend service for IP Risk Analysis using RAG",
    version="0.1.0",
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
