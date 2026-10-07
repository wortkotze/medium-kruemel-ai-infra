#!/usr/bin/env python3
"""
LiteLLM Management MCP Server
Provides declarative tools to interact with and manage the LiteLLM Gateway.
"""
import os
import sys
import json
import urllib.request
import urllib.error
from mcp.server.fastmcp import FastMCP

LITELLM_URL = os.getenv("LITELLM_API_BASE", "http://localhost:4000")
MASTER_KEY = os.getenv("LITELLM_MASTER_KEY", "")

mcp = FastMCP("LiteLLM Management MCP")

def _request(endpoint: str, method: str = "GET", data: dict = None) -> dict:
    url = f"{LITELLM_URL.rstrip('/')}{endpoint}"
    headers = {
        "Authorization": f"Bearer {MASTER_KEY}",
        "Content-Type": "application/json"
    }
    body = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8", errors="replace")
        return {"error": f"HTTP {e.code}: {err_msg}"}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def list_gateway_models() -> dict:
    """Retrieve the full list of active models and routing aliases configured on the LiteLLM Gateway."""
    return _request("/models")

@mcp.tool()
def get_gateway_health() -> dict:
    """Check the health status of the LiteLLM Gateway, PostgreSQL database, and cache."""
    return _request("/health/readiness")

@mcp.tool()
def test_gateway_completion(model: str, prompt: str) -> dict:
    """Execute a quick test completion through LiteLLM on a specific local or cloud model."""
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 128
    }
    return _request("/v1/chat/completions", method="POST", data=payload)

@mcp.tool()
def generate_api_key(alias: str, max_budget: float = 10.0, models: list = None) -> dict:
    """Generate a new virtual API key with spend limits and model permissions."""
    payload = {
        "key_alias": alias,
        "max_budget": max_budget,
        "models": models or []
    }
    return _request("/key/generate", method="POST", data=payload)

if __name__ == "__main__":
    mcp.run(transport="stdio")
