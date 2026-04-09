# Multi-Agent Research System

An AI-powered research assistant where multiple specialized agents collaborate to search the web, summarize findings, fact-check information, and produce a structured research report — all from a single query.

---

## What It Does

You give it a topic (e.g., *"Impact of AI on healthcare in 2025"*) and it:

1. **Searches** the web for relevant, up-to-date information
2. **Summarizes** the findings into key points
3. **Fact-checks** the summary against the source material
4. **Writes** a clean, structured research report
5. **Streams** the output live to a web UI

---

## Architecture

```
User Query
    │
    ▼
[Orchestrator / LangGraph State Machine]
    │
    ├──► [Search Agent]       → Tavily web search → raw results
    │
    ├──► [Summarizer Agent]   → condenses results → key findings
    │
    ├──► [Fact-Check Agent]   → verifies claims   → confidence notes
    │
    └──► [Writer Agent]       → produces final report (streamed)
```

### Agent Communication via Shared State

All agents read from and write to a shared `ResearchState` object that flows through the graph:

```python
ResearchState = {
    "query":               str,   # original user question
    "search_results":      list,  # raw Tavily results
    "summary":             str,   # condensed findings
    "fact_check_results":  str,   # verification notes
    "final_report":        str,   # the output
}
```

---

## Tech Stack

| Layer | Technology | Purpose | Cost |
|---|---|---|---|
| **LLM** | Groq (Llama 3.3 70b) | Powers all agents | Free tier |
| **Embeddings** | Gemini `gemini-embedding-001` | RAG vector search | Free tier |
| **Agent Framework** | LangGraph 1.x | Orchestrates agent graph | Open source |
| **LLM Abstraction** | LangChain 1.x | Unified LLM interface | Open source |
| **Web Search** | Tavily API | Real-time web search | Free (1000/mo) |
| **Vector DB** | ChromaDB | Local RAG storage | Open source |
| **Backend** | FastAPI + uvicorn | REST API + streaming | Open source |
| **Streaming** | Server-Sent Events (SSE) | Live output to UI | — |
| **Frontend** | Next.js + Tailwind CSS | Web interface | Open source |
| **Deployment** | Railway (backend) + Vercel (frontend) | Hosting | Free tier |

---

## Project Structure

```
Multi Agent Research System/
├── backend/
│   ├── agents/              # Individual agent logic
│   │   ├── __init__.py
│   │   ├── search_agent.py      # Searches the web via Tavily
│   │   ├── summarizer_agent.py  # Summarizes search results
│   │   ├── fact_checker_agent.py# Verifies key claims
│   │   └── writer_agent.py      # Writes the final report
│   │
│   ├── graph/               # LangGraph orchestration
│   │   ├── __init__.py
│   │   ├── state.py             # Shared ResearchState definition
│   │   └── research_graph.py    # Graph wiring (nodes + edges)
│   │
│   ├── rag/                 # RAG pipeline
│   │   ├── __init__.py
│   │   ├── embeddings.py        # Gemini embedding wrapper
│   │   └── vector_store.py      # ChromaDB operations
│   │
│   ├── tools/               # Reusable tools
│   │   ├── __init__.py
│   │   └── search_tool.py       # Tavily search wrapper
│   │
│   ├── api/                 # FastAPI routes
│   │   ├── __init__.py
│   │   └── routes.py            # /research endpoint (streaming)
│   │
│   ├── main.py              # FastAPI app entry point
│   ├── requirements.txt
│   └── test_connections.py  # Phase 1 verification script
│
├── frontend/                # Next.js app (Phase 6)
│   └── ...
│
├── .env                     # API keys (never commit this)
├── .gitignore
└── README.md
```

---

## Build Phases

### Phase 1 — Foundation & Setup ✅
- Project structure
- Virtual environment
- Dependencies installed
- All API connections verified (Groq, Gemini embeddings, Tavily, ChromaDB)

### Phase 2 — Individual Agents 🔄
- `search_agent.py` — takes a query, returns web search results
- `summarizer_agent.py` — condenses results into key findings
- `fact_checker_agent.py` — cross-checks claims against sources
- `writer_agent.py` — produces final structured report

### Phase 3 — LangGraph Orchestration
- Define `ResearchState` shared state
- Wire agents as graph nodes
- Add conditional edges (e.g., re-search if fact-check fails)
- End-to-end pipeline test

### Phase 4 — RAG Pipeline
- Gemini embeddings wrapper
- ChromaDB vector store
- Store past research for context
- Query vector store to enrich agent context

### Phase 5 — FastAPI Backend + Streaming
- `/api/research` POST endpoint
- Real-time SSE streaming of agent progress
- Request/response models with Pydantic

### Phase 6 — Next.js Frontend
- Clean research UI
- Live streaming output display
- Research history sidebar

### Phase 7 — Production Deployment
- Railway for backend (FastAPI)
- Vercel for frontend (Next.js)
- Environment variable configuration

### Phase 8 — Polish
- LangSmith observability (free tier)
- Error handling + retries
- README + demo GIF for resume

---

## Setup

### Prerequisites
- Python 3.10+
- Node.js 18+

### Backend

```powershell
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# Add your API keys to .env
# GROQ_API_KEY, GOOGLE_API_KEY, TAVILY_API_KEY

# Verify connections
python backend/test_connections.py

# Run the server
uvicorn backend.main:app --reload
```

### Frontend (Phase 6)

```powershell
cd frontend
npm install
npm run dev
```

---

## API Keys Required

| Key | Get From | Used For |
|---|---|---|
| `GROQ_API_KEY` | console.groq.com | LLM (all agents) |
| `GOOGLE_API_KEY` | aistudio.google.com/app/apikey | Embeddings only |
| `TAVILY_API_KEY` | tavily.com | Web search |

All free tier. No credit card required for Groq or Tavily.
