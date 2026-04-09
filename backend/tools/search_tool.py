"""
Tavily search wrapper.

Tavily is purpose-built for LLMs — unlike raw Google search, it returns
clean text snippets (not HTML) and is optimized for factual retrieval.
"""
import os
from typing import List
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()


def web_search(query: str, max_results: int = 5) -> List[dict]:
    """
    Search the web for a query and return structured results.

    Returns a list of dicts, each with:
      - title:   page title
      - url:     source URL
      - content: clean text snippet (Tavily strips HTML for us)
      - score:   relevance score (0-1)
    """
    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

    response = client.search(
        query=query,
        max_results=max_results,
        search_depth="advanced",   # deeper search than basic
        include_answer=True,       # Tavily's own quick answer (bonus context)
    )

    results = []
    for r in response.get("results", []):
        results.append({
            "title":   r.get("title", ""),
            "url":     r.get("url", ""),
            "content": r.get("content", ""),
            "score":   r.get("score", 0.0),
        })

    return results
