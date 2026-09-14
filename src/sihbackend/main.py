from fastapi import FastAPI
from sihbackend.api import health, analyze

app = FastAPI(
    title="SIH Backend - IP Risk Analysis",
    description="Backend service for IP Risk Analysis using RAG",
    version="0.1.0",
)

# Include Routers
app.include_router(health.router)
app.include_router(analyze.router)
