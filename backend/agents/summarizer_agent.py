"""
Summarizer Agent

Responsibility: Read the raw search results and condense them into
structured key findings. Removes noise, repetition, and irrelevant content.

Why summarize before fact-checking?
  - Fact-checking raw search results is messy and expensive (too many tokens)
  - A good summary gives the fact-checker clean claims to verify
  - It also makes the writer's job much easier
"""
import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from backend.graph.state import ResearchState
from dotenv import load_dotenv

load_dotenv()

# Initialize the LLM once (module-level) so it's not recreated on every call
llm = ChatGroq(
    model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.3,   # low temperature = more factual, less creative
)

SUMMARIZER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a research summarizer. Your job is to extract and organize
the most important information from web search results.

Instructions:
- Extract the key facts, statistics, and insights
- Group related information together
- Ignore ads, navigation text, or irrelevant content
- Be concise but thorough
- Always cite which source each point came from (use the title)

Output format:
## Key Findings

**[Topic Area]**
- Finding 1 (Source: [title])
- Finding 2 (Source: [title])

**[Topic Area]**
- Finding 3 (Source: [title])
..."""),
    ("human", """Research Query: {query}

Search Results:
{search_results}

{rag_context}

Please summarize the key findings from these results.""")
])


def _format_search_results(results: list) -> str:
    """Format search results into a readable string for the prompt."""
    formatted = []
    for i, r in enumerate(results, 1):
        formatted.append(
            f"[Result {i}]\n"
            f"Title: {r['title']}\n"
            f"URL: {r['url']}\n"
            f"Content: {r['content']}\n"
        )
    return "\n---\n".join(formatted)


def summarizer_agent(state: ResearchState) -> ResearchState:
    """LangGraph node: summarize search results into key findings."""
    print(f"\n[Summarizer Agent] Summarizing {len(state['search_results'])} results...")

    formatted_results = _format_search_results(state["search_results"])

    chain = SUMMARIZER_PROMPT | llm
    response = chain.invoke({
        "query": state["query"],
        "search_results": formatted_results,
        "rag_context": state.get("rag_context", ""),
    })

    summary = response.content
    print(f"[Summarizer Agent] Summary complete ({len(summary)} chars)")

    return {
        "summary": summary,
        "current_step": "summarization_complete",
    }
