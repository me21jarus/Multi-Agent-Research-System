"""
Search Agent

Responsibility: Take the user's query, run a web search, and store
the raw results in state. This is always the first node in the graph.

Why a dedicated agent for search?
  - Separation of concerns: searching ≠ reasoning
  - We can swap Tavily for another tool without touching other agents
  - Easy to add query rewriting / query expansion here later
"""
from backend.graph.state import ResearchState
from backend.tools.search_tool import web_search


def search_agent(state: ResearchState) -> ResearchState:
    """
    LangGraph node function.

    LangGraph passes the current state in, we return the updated state.
    Only the keys we return get updated — others stay unchanged.
    """
    print(f"\n[Search Agent] Searching for: {state['query']}")

    results = web_search(state["query"], max_results=5)

    print(f"[Search Agent] Found {len(results)} results")
    for r in results:
        print(f"  - {r['title'][:60]} ({r['url'][:50]})")

    return {
        "search_results": results,
        "current_step": "search_complete",
    }
