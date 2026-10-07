#!/usr/bin/env python3
"""
Product & Specification Management FastMCP Server.
Allows Product Owner (agent-po) and Architect (agent-architect) agents to persist,
list, and inspect structured specifications, PRDs, and user stories.
"""
import datetime
import os
import re
import sys
from pathlib import Path
from mcp.server.fastmcp import FastMCP

# Determine specs directory (Docker workspace or local fallback)
DEFAULT_WORKSPACE = "/workspace" if os.path.exists("/workspace") else str(Path(__file__).resolve().parent.parent.parent / "workspace")
SPECS_DIR = os.getenv("SPECS_DIR", str(Path(DEFAULT_WORKSPACE) / "docs" / "specs"))

SPECS_PATH = Path(SPECS_DIR).resolve()
SPECS_PATH.mkdir(parents=True, exist_ok=True)

mcp = FastMCP("Product Specification MCP")


def _sanitize_name(name: str) -> str:
    """Normalize specification file name."""
    clean = re.sub(r"[^\w\-\.]+", "_", name.strip())
    if not clean.endswith((".md", ".txt", ".json", ".yaml", ".yml")):
        clean += ".md"
    return clean


def _resolve_spec_file(name: str) -> Path:
    """Resolve file path and prevent directory traversal."""
    filename = _sanitize_name(name)
    target = (SPECS_PATH / filename).resolve()
    if not str(target).startswith(str(SPECS_PATH)):
        # Check subdirectories
        found = list(SPECS_PATH.rglob(filename))
        if found:
            return found[0]
        raise ValueError(f"Security error: '{name}' points outside specification directory.")
    return target


@mcp.tool()
def save_specification(name: str, content: str, category: str = "general") -> dict:
    """Save or update a specification document (PRD, epic, user story, API contract).

    Args:
        name: Name of the specification (e.g. 'auth-system-spec', 'rate-limiting.md').
        content: Full markdown or text content of the specification.
        category: Sub-category/folder (e.g. 'core', 'agents', 'integrations', 'api').
    """
    try:
        clean_cat = re.sub(r"[^\w\-]+", "_", category.strip().lower()) if category else "general"
        target_dir = SPECS_PATH / clean_cat
        target_dir.mkdir(parents=True, exist_ok=True)

        filename = _sanitize_name(name)
        target_file = target_dir / filename

        target_file.write_text(content, encoding="utf-8")
        stat = target_file.stat()

        return {
            "status": "success",
            "name": filename,
            "category": clean_cat,
            "path": str(target_file.relative_to(SPECS_PATH)),
            "full_path": str(target_file),
            "size_bytes": stat.st_size,
            "characters": len(content),
            "updated_at": datetime.datetime.fromtimestamp(stat.st_mtime).isoformat()
        }
    except Exception as e:
        return {"status": "error", "error": f"Failed to save specification: {str(e)}"}


@mcp.tool()
def list_specifications(category: str = "") -> list:
    """List all stored specifications, optionally filtered by category.

    Args:
        category: Optional category filter (e.g. 'core', 'agents', 'api').
    """
    try:
        results = []
        pattern = "*"
        search_path = SPECS_PATH
        if category:
            clean_cat = re.sub(r"[^\w\-]+", "_", category.strip().lower())
            search_path = SPECS_PATH / clean_cat
            if not search_path.exists():
                return []

        for p in search_path.rglob(pattern):
            if p.is_file() and p.suffix in (".md", ".txt", ".json", ".yaml", ".yml"):
                stat = p.stat()
                rel_parts = p.relative_to(SPECS_PATH).parts
                cat = rel_parts[0] if len(rel_parts) > 1 else "root"
                results.append({
                    "name": p.name,
                    "category": cat,
                    "relative_path": str(p.relative_to(SPECS_PATH)),
                    "size_bytes": stat.st_size,
                    "modified_at": datetime.datetime.fromtimestamp(stat.st_mtime).isoformat()
                })

        results.sort(key=lambda x: x["modified_at"], reverse=True)
        return results
    except Exception as e:
        return [{"error": f"Failed to list specifications: {str(e)}"}]


@mcp.tool()
def load_specification(name: str) -> dict:
    """Load and read the full text of a specification document.

    Args:
        name: Name or relative path of specification to load.
    """
    try:
        target = _resolve_spec_file(name)
        if not target.is_file():
            # Search by partial stem
            matches = [p for p in SPECS_PATH.rglob("*") if p.is_file() and name.lower() in p.name.lower()]
            if matches:
                target = matches[0]
            else:
                return {"status": "error", "error": f"Specification '{name}' not found."}

        content = target.read_text(encoding="utf-8", errors="replace")
        stat = target.stat()
        rel_parts = target.relative_to(SPECS_PATH).parts
        cat = rel_parts[0] if len(rel_parts) > 1 else "root"

        return {
            "status": "success",
            "name": target.name,
            "category": cat,
            "relative_path": str(target.relative_to(SPECS_PATH)),
            "size_bytes": stat.st_size,
            "modified_at": datetime.datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "content": content
        }
    except Exception as e:
        return {"status": "error", "error": f"Failed to load specification: {str(e)}"}


if __name__ == "__main__":
    mcp.run(transport="stdio")
