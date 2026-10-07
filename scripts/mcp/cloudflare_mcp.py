#!/usr/bin/env python3
"""
Cloudflare Infrastructure MCP Server
Built with Python FastMCP (talks directly to Cloudflare v4 REST API)
"""
import os
import sys
import json
import urllib.request
import urllib.error
from mcp.server.fastmcp import FastMCP

CF_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN", "")
CF_EMAIL = os.getenv("CLOUDFLARE_EMAIL", "")
CF_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID", "")
BASE_URL = "https://api.cloudflare.com/client/v4"

mcp = FastMCP("Cloudflare Infrastructure MCP")

def _cf_request(endpoint: str, method: str = "GET", data: dict = None) -> dict:
    if not CF_API_TOKEN:
        return {"error": "CLOUDFLARE_API_TOKEN is not configured in .env"}

    url = f"{BASE_URL.rstrip('/')}{endpoint}"
    headers = {
        "Authorization": f"Bearer {CF_API_TOKEN}",
        "Content-Type": "application/json"
    }
    if CF_EMAIL:
        headers["X-Auth-Email"] = CF_EMAIL

    body = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8", errors="replace")
        try:
            return json.loads(err_msg)
        except Exception:
            return {"error": f"HTTP {e.code}: {err_msg}"}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def verify_token() -> dict:
    """Verify if the current Cloudflare API token is active and valid."""
    return _cf_request("/user/tokens/verify")

@mcp.tool()
def list_zones() -> dict:
    """List all DNS zones / domains managed in your Cloudflare account."""
    return _cf_request("/zones")

@mcp.tool()
def list_dns_records(zone_id: str) -> dict:
    """List all DNS records for a given Cloudflare Zone ID."""
    return _cf_request(f"/zones/{zone_id}/dns_records")

@mcp.tool()
def get_dns_record(zone_id: str, record_id: str) -> dict:
    """Retrieve details for a specific DNS record."""
    return _cf_request(f"/zones/{zone_id}/dns_records/{record_id}")

@mcp.tool()
def create_dns_record(zone_id: str, type: str, name: str, content: str, ttl: int = 1, proxied: bool = True) -> dict:
    """Create a new DNS record (e.g. A, CNAME, TXT) in a Cloudflare Zone."""
    payload = {
        "type": type.upper(),
        "name": name,
        "content": content,
        "ttl": ttl,
        "proxied": proxied
    }
    return _cf_request(f"/zones/{zone_id}/dns_records", method="POST", data=payload)

@mcp.tool()
def update_dns_record(zone_id: str, record_id: str, type: str, name: str, content: str, ttl: int = 1, proxied: bool = True) -> dict:
    """Update an existing DNS record in a Cloudflare Zone."""
    payload = {
        "type": type.upper(),
        "name": name,
        "content": content,
        "ttl": ttl,
        "proxied": proxied
    }
    return _cf_request(f"/zones/{zone_id}/dns_records/{record_id}", method="PUT", data=payload)

@mcp.tool()
def list_tunnels(account_id: str = "") -> dict:
    """List all Cloudflare Tunnels for your account."""
    acc_id = account_id or CF_ACCOUNT_ID
    if not acc_id:
        return {"error": "CLOUDFLARE_ACCOUNT_ID is required to list tunnels."}
    return _cf_request(f"/accounts/{acc_id}/cfd_tunnel")

@mcp.tool()
def get_tunnel_status(tunnel_id: str, account_id: str = "") -> dict:
    """Get status and connector health for a specific Cloudflare Tunnel."""
    acc_id = account_id or CF_ACCOUNT_ID
    if not acc_id:
        return {"error": "CLOUDFLARE_ACCOUNT_ID is required."}
    return _cf_request(f"/accounts/{acc_id}/cfd_tunnel/{tunnel_id}")

@mcp.tool()
def list_workers(account_id: str = "") -> dict:
    """List Cloudflare Workers scripts in your account."""
    acc_id = account_id or CF_ACCOUNT_ID
    if not acc_id:
        return {"error": "CLOUDFLARE_ACCOUNT_ID is required."}
    return _cf_request(f"/accounts/{acc_id}/workers/scripts")

if __name__ == "__main__":
    mcp.run(transport="stdio")
