"""
FastAPI entry point for the Stock Movement Reason Finder API.

Run with:
    uvicorn app.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router

app = FastAPI(
    title="Stock Movement Reason Finder API",
    description=(
        "REST API that detects NIFTY100 stock price spikes, fetches related news, "
        "and generates AI-powered reasoning for price movements using Gemini."
    ),
    version="1.0.0",
)

# CORS — allow all origins for local development; restrict in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Register routes
app.include_router(router)


@app.get("/", tags=["Health"])
def health_check():
    """Root endpoint — confirms the API is running."""
    return {"status": "running"}
