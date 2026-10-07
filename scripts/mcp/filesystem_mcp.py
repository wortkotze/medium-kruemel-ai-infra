#!/usr/bin/env python3
"""
Sandboxed Local Filesystem MCP Server
Built with Python FastMCP (compatible with LiteLLM standard container)
"""
import os
import sys
from pathlib import Path
from mcp.server.fastmcp import FastMCP

# Workspace sandbox root
WORKSPACE_DIR = os.getenv("WORKSPACE_ROOT", "/workspace")
if len(sys.argv) > 1:
    WORKSPACE_DIR = sys.argv[1]

WORKSPACE_PATH = Path(WORKSPACE_DIR).resolve()
WORKSPACE_PATH.mkdir(parents=True, exist_ok=True)

mcp = FastMCP("Sandboxed Local Filesystem MCP")

def _resolve_safe_path(rel_path: str) -> Path:
    target = (WORKSPACE_PATH / rel_path).resolve()
    if not str(target).startswith(str(WORKSPACE_PATH)):
        raise ValueError(f"Access denied: path '{rel_path}' is outside sandbox '{WORKSPACE_PATH}'")
    return target

@mcp.tool()
def read_file(path: str) -> str:
    """Read full text content from a file inside the sandboxed workspace."""
    target = _resolve_safe_path(path)
    if not target.is_file():
        raise FileNotFoundError(f"File '{path}' does not exist.")
    return target.read_text(encoding="utf-8", errors="replace")

@mcp.tool()
def write_file(path: str, content: str) -> str:
    """Write or overwrite text content to a file inside the sandboxed workspace."""
    target = _resolve_safe_path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return f"Successfully wrote {len(content)} characters to {path}"

@mcp.tool()
def list_directory(path: str = "") -> list:
    """List directory contents within the workspace."""
    target = _resolve_safe_path(path)
    if not target.is_dir():
        raise NotADirectoryError(f"'{path}' is not a directory.")
    results = []
    for entry in target.iterdir():
        rel = entry.relative_to(WORKSPACE_PATH)
        results.append({
            "name": entry.name,
            "path": str(rel),
            "is_dir": entry.is_dir(),
            "size_bytes": entry.stat().st_size if entry.is_file() else 0
        })
    return results

@mcp.tool()
def get_file_info(path: str) -> dict:
    """Retrieve metadata (size, created, modified) for a path in the workspace."""
    target = _resolve_safe_path(path)
    if not target.exists():
        raise FileNotFoundError(f"Path '{path}' not found.")
    stat = target.stat()
    return {
        "path": str(target.relative_to(WORKSPACE_PATH)),
        "is_dir": target.is_dir(),
        "is_file": target.is_file(),
        "size_bytes": stat.st_size,
        "modified_timestamp": stat.st_mtime
    }

@mcp.tool()
def search_files(query: str, path: str = "") -> list:
    """Search filenames matching a query string inside the workspace."""
    target = _resolve_safe_path(path)
    matches = []
    for root, dirs, files in os.walk(target):
        for f in files:
            if query.lower() in f.lower():
                full = Path(root) / f
                matches.append(str(full.relative_to(WORKSPACE_PATH)))
    return matches

if __name__ == "__main__":
    mcp.run(transport="stdio")
