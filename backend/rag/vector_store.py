"""
ChromaDB vector store operations.

ChromaDB stores documents alongside their embeddings so we can do
semantic similarity search — "find me documents related to X".

Key concepts:
  - Collection: like a table in SQL, groups related documents
  - Document:   the raw text we store
  - Embedding:  the vector representation (ChromaDB stores this automatically)
  - Metadata:   extra info stored alongside (source URL, title, timestamp)
  - Query:      "find me the N most similar documents to this text"

We persist ChromaDB to disk so the knowledge base survives restarts.
"""
import os
from typing import List
from langchain_chroma import Chroma
from backend.rag.embeddings import get_embeddings
from dotenv import load_dotenv

load_dotenv()

# Directory where ChromaDB persists data between sessions
CHROMA_PERSIST_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "chroma_db"
)

COLLECTION_NAME = "research_knowledge"


def get_vector_store() -> Chroma:
    """
    Get or create the ChromaDB vector store.
    If chroma_db/ directory exists, loads existing data.
    If not, creates a fresh collection.
    """
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=get_embeddings(),
        persist_directory=CHROMA_PERSIST_DIR,
    )


def store_search_results(query: str, search_results: List[dict]) -> int:
    """
    Embed and store search results in ChromaDB.

    Each search result becomes one document in the vector store.
    We store the title and URL as metadata for attribution.

    Returns the number of documents stored.
    """
    vector_store = get_vector_store()

    documents = []
    metadatas = []
    ids = []

    for i, result in enumerate(search_results):
        # Combine title + content for richer embeddings
        doc_text = f"{result['title']}\n\n{result['content']}"
        documents.append(doc_text)
        metadatas.append({
            "query":  query,
            "title":  result["title"],
            "url":    result["url"],
            "score":  str(result.get("score", 0.0)),
        })
        # Unique ID: hash of URL to avoid storing duplicates
        ids.append(f"{hash(result['url'])}")

    # add_texts handles embedding + storage in one call
    vector_store.add_texts(
        texts=documents,
        metadatas=metadatas,
        ids=ids,
    )

    return len(documents)


def retrieve_related_context(query: str, n_results: int = 3) -> str:
    """
    Retrieve the most semantically similar past research for a query.

    Returns a formatted string of related context ready to inject
    into the summarizer's prompt.
    """
    vector_store = get_vector_store()

    # Check if collection has any documents before querying
    collection = vector_store._collection
    if collection.count() == 0:
        return ""

    results = vector_store.similarity_search_with_score(
        query=query,
        k=n_results,
    )

    if not results:
        return ""

    # Format results into readable context
    context_parts = []
    for doc, score in results:
        # score in ChromaDB is distance (lower = more similar)
        # Only include if reasonably similar (distance < 1.5)
        if score < 1.5:
            title = doc.metadata.get("title", "Unknown")
            url = doc.metadata.get("url", "")
            context_parts.append(
                f"**{title}**\n{doc.page_content[:400]}...\nSource: {url}"
            )

    if not context_parts:
        return ""

    return "### Related Past Research:\n\n" + "\n\n---\n\n".join(context_parts)
