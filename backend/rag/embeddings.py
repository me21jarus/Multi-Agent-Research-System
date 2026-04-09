"""
Gemini Embeddings wrapper — lazy singleton.
Initialized on first use, not at import time, to avoid startup crashes
when environment variables haven't been loaded yet.
"""
import os
from dotenv import load_dotenv

load_dotenv()

_embeddings = None


def get_embeddings():
    global _embeddings
    if _embeddings is None:
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        _embeddings = GoogleGenerativeAIEmbeddings(
            model=os.getenv("EMBEDDING_MODEL", "models/gemini-embedding-001"),
            google_api_key=os.getenv("GOOGLE_API_KEY"),
        )
    return _embeddings
