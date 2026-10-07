#!/usr/bin/env python3
"""
SearXNG Meta-Search FastMCP Server.
Provides privacy-focused web search, news aggregation, and academic search to AI agents.
"""
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from mcp.server.fastmcp import FastMCP

SEARXNG_URL = os.getenv("SEARXNG_URL", "http://searxng:8080")

mcp = FastMCP("SearXNG Meta-Search MCP")


def _search(query: str, categories: str = "general", num_results: int = 5, language: str = "de") -> list:
    params = {
        "q": query,
        "format": "json",
        "categories": categories,
        "language": language,
    }
    url = f"{SEARXNG_URL.rstrip('/')}/search?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Krümel-AI-Agent/1.0",
            "Accept": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as res:
            data = json.loads(res.read().decode("utf-8"))
            results = data.get("results", [])
            output = []
            for r in results[:num_results]:
                output.append({
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "content": r.get("content", ""),
                    "engine": r.get("engine", ""),
                    "score": r.get("score", 0),
                })
            return output
    except urllib.error.HTTPError as e:
        return [{"error": f"HTTP {e.code}: {e.reason}"}]
    except Exception as e:
        return [{"error": f"Search failed: {str(e)}"}]


@mcp.tool()
def search_web(query: str, categories: str = "general", num_results: int = 5, language: str = "de") -> list:
    """Search the web using SearXNG meta-search aggregator (Google, Bing, DuckDuckGo).

    Returns a list of deduplicated search results with title, URL, and snippet.
    """
    return _search(query=query, categories=categories, num_results=min(max(num_results, 1), 20), language=language)


@mcp.tool()
def search_news(query: str, num_results: int = 5, language: str = "de") -> list:
    """Search current news articles using SearXNG news aggregator."""
    return _search(query=query, categories="news", num_results=min(max(num_results, 1), 20), language=language)


@mcp.tool()
def search_scholar(query: str, num_results: int = 5) -> list:
    """Search academic papers, preprints (ArXiv), and science sources using SearXNG."""
    return _search(query=query, categories="science", num_results=min(max(num_results, 1), 20), language="en")


if __name__ == "__main__":
    mcp.run(transport="stdio")
