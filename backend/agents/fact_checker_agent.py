"""
Fact-Checker Agent

Responsibility: Take the summary produced by the Summarizer Agent and
cross-check each key claim against the original search results.

This is what makes the system a proper multi-agent pipeline — not just
one LLM call, but a dedicated verification step that catches hallucinations
and unsupported claims before they end up in the final report.

What it outputs:
  - A confidence assessment for each major claim
  - Notes on what is well-supported vs. what needs a caveat
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
    temperature=0.1,   # very low — fact-checking needs to be precise
)

FACT_CHECKER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a rigorous fact-checker. Your job is to verify the claims
in a research summary against the original source material.

For each major claim in the summary:
1. Check if it is directly supported by the search results
2. Flag anything that seems exaggerated, missing context, or unsupported
3. Note if multiple sources agree (increases confidence)

Be critical but fair. Your goal is to ensure accuracy, not to be contrarian.

Output format:
## Fact-Check Report

**Verified Claims** ✓
- [Claim] — Supported by: [source title(s)]

**Claims Needing Caveats** ⚠️
- [Claim] — [explanation of why it needs qualification]

**Unverified / Unsupported** ✗
- [Claim] — Not found in sources

**Overall Confidence:** [High / Medium / Low]
**Notes:** [Any general observations about source quality or gaps]"""),
    ("human", """Original Query: {query}

Summary to Fact-Check:
{summary}

Original Search Results (ground truth):
{search_results}

Please fact-check the summary against the search results.""")
])


def _format_search_results(results: list) -> str:
    formatted = []
    for i, r in enumerate(results, 1):
        formatted.append(
            f"[Source {i}]: {r['title']}\n{r['content'][:500]}..."
        )
    return "\n\n".join(formatted)


def fact_checker_agent(state: ResearchState) -> ResearchState:
    """LangGraph node: verify summary claims against source material."""
    print(f"\n[Fact-Checker Agent] Verifying claims in summary...")

    formatted_results = _format_search_results(state["search_results"])

    chain = FACT_CHECKER_PROMPT | llm
    response = chain.invoke({
        "query": state["query"],
        "summary": state["summary"],
        "search_results": formatted_results,
    })

    fact_check_results = response.content
    print(f"[Fact-Checker Agent] Fact-check complete ({len(fact_check_results)} chars)")

    return {
        "fact_check_results": fact_check_results,
        "current_step": "fact_check_complete",
    }
