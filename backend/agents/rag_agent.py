"""
RAG Agent

Responsibility:
  1. Store the current search results into ChromaDB (builds the knowledge base)
  2. Retrieve any related past research from ChromaDB
  3. Pass that context to the next agent (Summarizer) to enrich its output

Why RAG matters for this project:
  - First query about "AI agents": searches web, stores results
  - Second query about "AI agent frameworks": retrieves relevant past results
    automatically, giving the summarizer richer context without extra web searches

This is what separates a basic LLM app from a knowledge-accumulating system.
"""
from backend.graph.state import ResearchState
from backend.rag.vector_store import store_search_results, retrieve_related_context


def rag_agent(state: ResearchState) -> ResearchState:
    """LangGraph node: store search results + retrieve related context."""
    print(f"\n[RAG Agent] Processing {len(state['search_results'])} results...")

    # Step 1: Store current search results in ChromaDB
    stored = store_search_results(state["query"], state["search_results"])
    print(f"[RAG Agent] Stored {stored} documents in vector store")

    # Step 2: Retrieve related past research
    related_context = retrieve_related_context(state["query"], n_results=3)

    if related_context:
        print(f"[RAG Agent] Retrieved related context ({len(related_context)} chars)")
    else:
        print(f"[RAG Agent] No related past research found (fresh topic)")

    return {
        "rag_context": related_context,
        "current_step": "rag_complete",
    }
