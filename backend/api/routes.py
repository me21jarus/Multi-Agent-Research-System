"""
FastAPI routes.

Key endpoint: POST /api/research
  - Accepts a research query
  - Runs the LangGraph pipeline
  - Streams progress back to the client via SSE (Server-Sent Events)

What is SSE?
  SSE is a simple protocol where the server keeps an HTTP connection open
  and pushes text events to the client. The client receives them one by one
  as they arrive — no polling needed.

  Event format (each line):
    data: {"type": "progress", "node": "search", "message": "..."}

  vs WebSockets: SSE is one-directional (server → client) and much simpler.
  Perfect for streaming a pipeline's progress.
"""
import json
import uuid
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from backend.graph.research_graph import get_research_graph
from backend.graph.state import ResearchState

router = APIRouter(prefix="/api")

# ── Request / Response models ─────────────────────────────────────────────────

class ResearchRequest(BaseModel):
    query: str

# ── Node → human-readable status messages ────────────────────────────────────

NODE_MESSAGES = {
    "search":     "Searching the web for relevant sources...",
    "rag":        "Retrieving related past research...",
    "summarize":  "Summarizing key findings...",
    "fact_check": "Fact-checking the summary...",
    "write":      "Writing the final report...",
}

# ── SSE helper ────────────────────────────────────────────────────────────────

def sse_event(data: dict) -> str:
    """Format a dict as an SSE event string."""
    return f"data: {json.dumps(data)}\n\n"


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/health")
def health_check():
    return {"status": "ok"}


@router.post("/research")
async def research(request: ResearchRequest):
    """
    Run the multi-agent research pipeline and stream progress via SSE.

    The client receives a stream of JSON events:
      {"type": "progress", "node": "search",  "message": "Searching..."}
      {"type": "progress", "node": "rag",     "message": "Retrieving..."}
      {"type": "progress", "node": "summarize","message": "Summarizing..."}
      {"type": "progress", "node": "fact_check","message": "Fact-checking..."}
      {"type": "progress", "node": "write",   "message": "Writing..."}
      {"type": "result",   "data": { final_report, sources }}
      {"type": "error",    "message": "..."}  ← only if something fails
    """

    async def event_stream():
        initial_state: ResearchState = {
            "query":            request.query,
            "search_results":   [],
            "summary":          "",
            "fact_check_results": "",
            "final_report":     "",
            "rag_context":      "",
            "current_step":     "start",
            "error":            None,
        }

        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}

        try:
            graph = get_research_graph()
            # Stream node completions from LangGraph
            for step in graph.stream(initial_state, config=config):
                node_name = list(step.keys())[0]
                message = NODE_MESSAGES.get(node_name, f"{node_name} complete")

                # Send progress event to client
                yield sse_event({
                    "type":    "progress",
                    "node":    node_name,
                    "message": message,
                })

            # Pipeline done — get the full merged final state
            full_state = graph.get_state(config).values

            # Extract sources from search results
            sources = [
                {"title": r["title"], "url": r["url"]}
                for r in full_state.get("search_results", [])
            ]

            # Send the final result event
            yield sse_event({
                "type": "result",
                "data": {
                    "query":        request.query,
                    "final_report": full_state.get("final_report", ""),
                    "sources":      sources,
                    "thread_id":    thread_id,
                }
            })

        except Exception as e:
            yield sse_event({
                "type":    "error",
                "message": str(e),
            })

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",   # disable nginx buffering in production
        }
    )
