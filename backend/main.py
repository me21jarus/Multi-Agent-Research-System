"""
FastAPI application entry point.

Run with:
  uvicorn backend.main:app --reload --port 8000
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from backend.api.routes import router

load_dotenv()

app = FastAPI(
    title="Multi-Agent Research System",
    description="AI-powered research assistant using LangGraph + Groq + Gemini",
    version="1.0.0",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
# Allows the Next.js frontend (localhost:3000) to call this API.
# In production, replace "*" with your actual frontend domain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://multi-agent-research-system-omega.vercel.app", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ────────────────────────────────────────────────────────────────────
app.include_router(router)


@app.get("/")
def root():
    return {
        "name": "Multi-Agent Research System",
        "status": "running",
        "docs": "/docs",      # FastAPI auto-generates Swagger UI here
    }
