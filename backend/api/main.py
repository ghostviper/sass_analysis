"""
FastAPI Application Entry Point
"""

# NOTE: On Windows with Python 3.8+, ProactorEventLoop (default) is required for subprocess support.
# Do NOT set WindowsSelectorEventLoopPolicy as it breaks subprocess on newer Python versions.
import sys
import asyncio

# Ensure ProactorEventLoopPolicy on Windows so subprocess (Claude CLI) works
if sys.platform == "win32":
    try:
        policy = asyncio.get_event_loop_policy()
        if not isinstance(policy, asyncio.WindowsProactorEventLoopPolicy):
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    except Exception:
        # Fallback silently; uvicorn will still attempt default policy
        pass

import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

from database.db import init_db, close_db
from api.routes import startups, chat, analytics, search
from api.routes import category_analysis, product_analysis, landing_analysis
from api.routes import leaderboard, sessions, auth, user


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    await init_db()
    print("Database initialized")
    yield
    # Shutdown
    await close_db()
    print("Application shutting down")


app = FastAPI(
    title="BuildWhat API",
    description="API for TrustMRR data analysis and AI-powered insights",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(startups.router, prefix="/api", tags=["Startups"])
app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(analytics.router, prefix="/api", tags=["Analytics"])
app.include_router(search.router, prefix="/api", tags=["Search"])

# Analysis routers
app.include_router(category_analysis.router, prefix="/api", tags=["Category Analysis"])
app.include_router(product_analysis.router, prefix="/api", tags=["Product Analysis"])
app.include_router(landing_analysis.router, prefix="/api", tags=["Landing Page Analysis"])
app.include_router(leaderboard.router, prefix="/api", tags=["Leaderboard"])
app.include_router(sessions.router, prefix="/api", tags=["Sessions"])
app.include_router(auth.router, prefix="/api", tags=["Auth"])
app.include_router(user.router, prefix="/api", tags=["User"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "SaaS Analysis API",
        "docs": "/docs",
        "version": "1.0.0",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
