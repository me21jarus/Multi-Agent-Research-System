"""
Research Graph — the LangGraph state machine that orchestrates all agents.

Key concepts:
  - StateGraph:  a directed graph where each node is an agent function
  - State:       the ResearchState TypedDict shared across all nodes
  - Nodes:       agent functions (state) -> partial_state
  - Edges:       define what runs after what
  - START / END: LangGraph built-ins marking entry and exit points
  - compile():   turns the graph definition into a runnable object

Why LangGraph instead of just calling agents in sequence?
  - Built-in streaming: stream() yields state after each node completes
  - Checkpointing: can pause/resume mid-pipeline (great for long research)
  - Conditional edges: easy to add "if fact-check fails, re-search" logic
  - Visualization: can render the graph as a diagram
  - Production-ready: handles retries, timeouts, concurrency
"""
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from backend.graph.state import ResearchState
from backend.agents.search_agent import search_agent
from backend.agents.rag_agent import rag_agent
from backend.agents.summarizer_agent import summarizer_agent
from backend.agents.fact_checker_agent import fact_checker_agent
from backend.agents.writer_agent import writer_agent


def build_research_graph(use_checkpointer: bool = False):
    """
    Build and compile the research graph.

    Args:
        use_checkpointer: if True, attaches an in-memory checkpointer.
                          Required for streaming by thread_id (Phase 5).

    Returns:
        A compiled LangGraph runnable.
    """
    # Create the graph with our shared state schema
    graph = StateGraph(ResearchState)

    # ─── Register nodes ──────────────────────────────────────────────────────
    # Each node name maps to an agent function.
    # LangGraph calls these with the current state and merges the returned dict.
    graph.add_node("search",     search_agent)
    graph.add_node("rag",        rag_agent)
    graph.add_node("summarize",  summarizer_agent)
    graph.add_node("fact_check", fact_checker_agent)
    graph.add_node("write",      writer_agent)

    # ─── Define edges (the flow) ─────────────────────────────────────────────
    # search → rag → summarize → fact_check → write
    # The RAG node sits between search and summarize:
    #   it stores results + retrieves related past research before summarization.
    graph.add_edge(START,        "search")
    graph.add_edge("search",     "rag")
    graph.add_edge("rag",        "summarize")
    graph.add_edge("summarize",  "fact_check")
    graph.add_edge("fact_check", "write")
    graph.add_edge("write",      END)

    # ─── Compile ─────────────────────────────────────────────────────────────
    # MemorySaver enables streaming and state inspection per thread_id.
    # Think of thread_id as a "session" — each research request gets its own.
    if use_checkpointer:
        memory = MemorySaver()
        return graph.compile(checkpointer=memory)

    return graph.compile()


# Lazy singleton — built on first request, not at import time.
# This prevents Railway healthcheck timeouts caused by heavy startup imports.
_graph = None

def get_research_graph():
    global _graph
    if _graph is None:
        _graph = build_research_graph(use_checkpointer=True)
    return _graph
