"""
Writer Agent

Responsibility: Take everything gathered — the summary, the fact-check
report, and the original sources — and produce a clean, well-structured
final research report.

This is the "output" agent. It's the one whose work the user actually sees.
The quality here depends entirely on the quality of all previous agents.

Why a separate writer?
  - Summarizers are good at extracting, writers are good at presenting
  - Different temperature settings (higher = more natural prose)
  - Clear separation lets us tune each role independently
"""
import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from backend.graph.state import ResearchState
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(
    model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.6,   # moderate creativity for natural-sounding prose
)

WRITER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert research writer. You produce clear, well-structured,
and insightful research reports for a professional audience.

Your report must:
- Start with an executive summary (2-3 sentences)
- Be organized into logical sections with headers
- Incorporate the fact-check notes (don't include unsupported claims without caveats)
- End with a "Sources" section listing the URLs
- Be written in clear, professional prose — not bullet points

Format your output in Markdown."""),
    ("human", """Research Query: {query}

Key Findings (from Summarizer):
{summary}

Fact-Check Report:
{fact_check_results}

Source URLs:
{source_urls}

Please write a comprehensive research report based on the above.""")
])


def _extract_sources(search_results: list) -> str:
    sources = []
    for i, r in enumerate(search_results, 1):
        sources.append(f"{i}. [{r['title']}]({r['url']})")
    return "\n".join(sources)


def writer_agent(state: ResearchState) -> ResearchState:
    """LangGraph node: produce the final research report."""
    print(f"\n[Writer Agent] Writing final report...")

    source_urls = _extract_sources(state["search_results"])

    chain = WRITER_PROMPT | llm
    response = chain.invoke({
        "query": state["query"],
        "summary": state["summary"],
        "fact_check_results": state["fact_check_results"],
        "source_urls": source_urls,
    })

    final_report = response.content
    print(f"[Writer Agent] Report complete ({len(final_report)} chars)")

    return {
        "final_report": final_report,
        "current_step": "report_complete",
    }
