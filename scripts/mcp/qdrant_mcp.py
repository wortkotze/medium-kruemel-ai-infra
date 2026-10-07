#!/usr/bin/env python3
"""
Qdrant Vector Memory & Semantic Recall FastMCP Server.
Allows all Krümel AI agents to persist and recall long-term knowledge, context, and facts
using vector embeddings via LiteLLM (nomic-embed-text) and Qdrant Vector DB.
"""
import datetime
import json
import os
import sys
import urllib.error
import urllib.request
import uuid
from mcp.server.fastmcp import FastMCP

def _get_qdrant_base() -> str:
    env_url = os.getenv("QDRANT_URL", "").rstrip("/")
    # Inside docker containers, localhost:6333 refers to the container itself, not the Qdrant service
    if env_url and "localhost" in env_url:
        return "http://qdrant:6333"
    return env_url if env_url else "http://qdrant:6333"

QDRANT_URL = _get_qdrant_base()
LITELLM_URL = os.getenv("LITELLM_API_BASE", "http://localhost:4000").rstrip("/")
LITELLM_KEY = os.getenv("LITELLM_MASTER_KEY", "")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION", "kruemel_knowledge")
VECTOR_SIZE = 768

mcp = FastMCP("Qdrant Vector Knowledge Memory MCP")


def _http_request(url: str, method: str = "GET", data: dict = None, headers: dict = None, timeout: int = 15) -> dict:
    """Helper for JSON HTTP requests."""
    req_headers = {"Content-Type": "application/json"}
    if headers:
        req_headers.update(headers)
    body = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(url, data=body, headers=req_headers, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as res:
        raw = res.read().decode("utf-8")
        return json.loads(raw) if raw else {}


def _get_embedding(text: str) -> list[float]:
    """Fetch vector embedding from LiteLLM proxy."""
    url = f"{LITELLM_URL}/v1/embeddings"
    headers = {"Authorization": f"Bearer {LITELLM_KEY}"} if LITELLM_KEY else {}
    payload = {
        "model": EMBEDDING_MODEL,
        "input": text
    }
    res = _http_request(url, method="POST", data=payload, headers=headers, timeout=20)
    data = res.get("data", [])
    if not data or "embedding" not in data[0]:
        raise RuntimeError(f"Failed to retrieve embedding from LiteLLM: {res}")
    return data[0]["embedding"]


def _ensure_collection():
    """Ensure the Qdrant knowledge collection exists with correct vector size."""
    try:
        url = f"{QDRANT_URL}/collections/{COLLECTION_NAME}"
        try:
            _http_request(url, method="GET", timeout=5)
            return  # Collection already exists
        except urllib.error.HTTPError as e:
            if e.code != 404:
                raise

        # Create collection
        payload = {
            "vectors": {
                "size": VECTOR_SIZE,
                "distance": "Cosine"
            }
        }
        _http_request(url, method="PUT", data=payload, timeout=10)
    except Exception as e:
        # Ignore if concurrently created
        pass


@mcp.tool()
def remember_knowledge(text: str, category: str, tags: list[str] = None) -> dict:
    """Store structured knowledge, facts, code snippets, or decisions in long-term vector memory.

    Args:
        text: The text content, factual knowledge, or document to remember.
        category: Broad category (e.g. 'architecture', 'infra', 'bugfix', 'user_preference', 'api_spec').
        tags: Optional list of keywords for filtering and search (e.g. ['postgres', 'docker', 'failover']).
    """
    try:
        _ensure_collection()
        tags_list = tags if tags else []
        vector = _get_embedding(text)
        point_id = str(uuid.uuid4())
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

        payload = {
            "points": [
                {
                    "id": point_id,
                    "vector": vector,
                    "payload": {
                        "text": text,
                        "category": category.strip().lower(),
                        "tags": tags_list,
                        "timestamp": timestamp,
                        "length": len(text)
                    }
                }
            ]
        }

        url = f"{QDRANT_URL}/collections/{COLLECTION_NAME}/points?wait=true"
        _http_request(url, method="PUT", data=payload, timeout=15)

        return {
            "status": "success",
            "id": point_id,
            "category": category,
            "tags": tags_list,
            "vector_dimensions": len(vector),
            "stored_at": timestamp,
            "preview": text[:120] + ("..." if len(text) > 120 else "")
        }

    except Exception as e:
        return {"status": "error", "error": f"Failed to remember knowledge: {str(e)}"}


@mcp.tool()
def recall_knowledge(query: str, category: str = "", limit: int = 5) -> dict:
    """Semantically search long-term memory for relevant knowledge, context, and previously learned facts.

    Args:
        query: Natural language search query (e.g. 'How is PostgreSQL failover configured?').
        category: Optional category filter to narrow down results (e.g. 'architecture', 'infra').
        limit: Maximum number of results to retrieve (default: 5, max: 20).
    """
    try:
        _ensure_collection()
        limit_count = min(max(limit, 1), 20)
        query_vector = _get_embedding(query)

        search_payload = {
            "vector": query_vector,
            "limit": limit_count,
            "with_payload": True,
            "with_vector": False
        }

        if category:
            search_payload["filter"] = {
                "must": [
                    {
                        "key": "category",
                        "match": {"value": category.strip().lower()}
                    }
                ]
            }

        url = f"{QDRANT_URL}/collections/{COLLECTION_NAME}/points/search"
        res = _http_request(url, method="POST", data=search_payload, timeout=15)
        raw_hits = res.get("result", [])

        hits = []
        for hit in raw_hits:
            p = hit.get("payload", {})
            hits.append({
                "id": hit.get("id"),
                "similarity_score": round(hit.get("score", 0.0), 4),
                "category": p.get("category"),
                "tags": p.get("tags", []),
                "stored_at": p.get("timestamp"),
                "text": p.get("text")
            })

        return {
            "query": query,
            "category_filter": category if category else "none",
            "results_count": len(hits),
            "results": hits
        }

    except Exception as e:
        return {"query": query, "status": "error", "error": f"Failed to recall knowledge: {str(e)}"}


if __name__ == "__main__":
    mcp.run(transport="stdio")
