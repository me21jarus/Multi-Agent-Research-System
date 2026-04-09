"""
Gemini Embeddings wrapper.

Embeddings convert text into a vector (list of numbers) that captures
semantic meaning. Similar texts get similar vectors — this is what lets
ChromaDB find "related" content without exact keyword matching.

Example:
  "AI in healthcare" and "machine learning for doctors"
  → both get vectors that are close in 3072-dimensional space
  → ChromaDB returns both when you search for either

We use Gemini's gemini-embedding-001 model (free tier, 3072 dimensions).
"""
import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

# Single instance reused across the app
embeddings = GoogleGenerativeAIEmbeddings(
    model=os.getenv("EMBEDDING_MODEL", "models/gemini-embedding-001"),
    google_api_key=os.getenv("GOOGLE_API_KEY"),
)


def get_embeddings():
    """Return the shared embeddings instance."""
    return embeddings
