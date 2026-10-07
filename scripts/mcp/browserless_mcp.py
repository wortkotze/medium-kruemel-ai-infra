#!/usr/bin/env python3
"""
Browserless Headless Chromium FastMCP Server.
Enables AI agents to navigate web pages, render dynamic SPAs, scrape content, and capture screenshots.
"""
import base64
import json
import os
import re
import urllib.error
import urllib.request
from mcp.server.fastmcp import FastMCP

BROWSERLESS_URL = os.getenv("BROWSERLESS_URL", "http://browserless:3000")

mcp = FastMCP("Browserless Headless Chromium MCP")


def _post_json(endpoint: str, payload: dict, timeout: int = 30) -> bytes:
    url = f"{BROWSERLESS_URL.rstrip('/')}{endpoint}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "Krümel-AI-Agent/1.0",
        },
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=timeout) as res:
        return res.read()


@mcp.tool()
def get_web_content(url: str) -> dict:
    """Fetch and render full DOM content from a web page using Headless Chromium.

    Executes JavaScript and single-page apps (React/Vue), returning rendered HTML.
    """
    try:
        raw_html = _post_json("/content", {"url": url}, timeout=30).decode("utf-8", errors="replace")
        return {
            "url": url,
            "status": "success",
            "html": raw_html[:50000],
            "truncated": len(raw_html) > 50000
        }
    except Exception as e:
        return {"url": url, "status": "error", "error": str(e)}


@mcp.tool()
def scrape_text(url: str) -> dict:
    """Scrape human-readable text and headings from a web page, stripping markup and styles.

    Ideal for reading articles, blogs, and documentation without HTML boilerplate.
    """
    try:
        raw_html = _post_json("/content", {"url": url}, timeout=30).decode("utf-8", errors="replace")
        clean = re.sub(r"<(script|style|svg|noscript)[^>]*>.*?</\1>", "", raw_html, flags=re.DOTALL | re.IGNORECASE)
        clean = re.sub(r"<[^>]+>", " ", clean)
        lines = [line.strip() for line in clean.splitlines() if line.strip()]
        text = "\n".join(lines)
        return {
            "url": url,
            "status": "success",
            "text": text[:30000],
            "truncated": len(text) > 30000
        }
    except Exception as e:
        return {"url": url, "status": "error", "error": str(e)}


@mcp.tool()
def take_screenshot(url: str) -> dict:
    """Capture a PNG screenshot of a web page using headless Chromium.

    Returns base64-encoded image data for vision models.
    """
    try:
        payload = {
            "url": url,
            "options": {
                "type": "png",
                "fullPage": False
            }
        }
        image_bytes = _post_json("/screenshot", payload, timeout=30)
        b64_img = base64.b64encode(image_bytes).decode("ascii")
        return {
            "url": url,
            "status": "success",
            "format": "image/png",
            "base64_data": b64_img[:5000] + "... [truncated for MCP response]" if len(b64_img) > 5000 else b64_img,
            "byte_size": len(image_bytes)
        }
    except Exception as e:
        return {"url": url, "status": "error", "error": str(e)}


if __name__ == "__main__":
    mcp.run(transport="stdio")
