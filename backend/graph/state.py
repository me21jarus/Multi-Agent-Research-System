"""
ResearchState — the shared data object that flows through every node in the graph.

Think of it like a baton in a relay race: each agent picks it up, adds their
work to it, and passes it to the next agent. LangGraph reads and writes this
TypedDict automatically as it moves through the graph.
"""
from typing import TypedDict, List, Optional


class ResearchState(TypedDict):
    # The original question from the user
    query: str

    # Raw search results from Tavily (list of dicts with title, url, content)
    search_results: List[dict]

    # Condensed key findings produced by the Summarizer Agent
    summary: str

    # Fact-check notes produced by the Fact-Checker Agent
    fact_check_results: str

    # The final polished research report produced by the Writer Agent
    final_report: str

    # Related context retrieved from ChromaDB (past research on similar topics)
    rag_context: str

    # Which step we're currently on (used for streaming status updates)
    current_step: str

    # Any error message if something goes wrong
    error: Optional[str]
