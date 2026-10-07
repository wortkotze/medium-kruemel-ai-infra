#!/usr/bin/env python3
"""
Architecture Decision & Documentation FastMCP Server.
Allows Architect (agent-architect) agents to persist, list, and inspect
Architecture Decision Records (ADRs), system designs, component specs, and diagrams.
"""
import datetime
import os
import re
import sys
from pathlib import Path
from mcp.server.fastmcp import FastMCP

# Determine architecture directory (Docker workspace or local fallback)
DEFAULT_WORKSPACE = "/workspace" if os.path.exists("/workspace") else str(Path(__file__).resolve().parent.parent.parent / "workspace")
ARCH_DIR = os.getenv("ARCHITECTURE_DIR", str(Path(DEFAULT_WORKSPACE) / "docs" / "architecture"))

ARCH_PATH = Path(ARCH_DIR).resolve()
ARCH_PATH.mkdir(parents=True, exist_ok=True)

mcp = FastMCP("Architecture Documentation MCP")


def _sanitize_name(name: str) -> str:
    """Normalize architecture document file name."""
    clean = re.sub(r"[^\w\-\.]+", "_", name.strip())
    if not clean.endswith((".md", ".txt", ".json", ".yaml", ".yml")):
        clean += ".md"
    return clean


def _resolve_arch_file(name: str) -> Path:
    """Resolve file path and prevent directory traversal."""
    filename = _sanitize_name(name)
    target = (ARCH_PATH / filename).resolve()
    if not str(target).startswith(str(ARCH_PATH)):
        found = list(ARCH_PATH.rglob(filename))
        if found:
            return found[0]
        raise ValueError(f"Security error: '{name}' points outside architecture directory.")
    return target


@mcp.tool()
def save_architecture_doc(name: str, content: str, category: str = "general") -> dict:
    """Save or update an architecture document (ADR, system design, data flow, component schema).

    Args:
        name: Document identifier or file name (e.g. 'adr-001-hybrid-memory.md', 'c4-container-model').
        content: Full markdown, mermaid, or yaml content of the architecture specification.
        category: Sub-category/folder (e.g. 'adr', 'components', 'dataflow', 'security').
    """
    try:
        clean_cat = re.sub(r"[^\w\-]+", "_", category.strip().lower()) if category else "general"
        target_dir = ARCH_PATH / clean_cat
        target_dir.mkdir(parents=True, exist_ok=True)

        filename = _sanitize_name(name)
        target_file = target_dir / filename

        target_file.write_text(content, encoding="utf-8")
        stat = target_file.stat()

        return {
            "status": "success",
            "name": filename,
            "category": clean_cat,
            "path": str(target_file.relative_to(ARCH_PATH)),
            "full_path": str(target_file),
            "size_bytes": stat.st_size,
            "characters": len(content),
            "updated_at": datetime.datetime.fromtimestamp(stat.st_mtime).isoformat()
        }
    except Exception as e:
        return {"status": "error", "error": f"Failed to save architecture doc: {str(e)}"}


@mcp.tool()
def list_architecture_docs(category: str = "") -> list:
    """List all stored architecture documents, optionally filtered by category.

    Args:
        category: Optional category filter (e.g. 'adr', 'components', 'security').
    """
    try:
        results = []
        pattern = "*"
        search_path = ARCH_PATH
        if category:
            clean_cat = re.sub(r"[^\w\-]+", "_", category.strip().lower())
            search_path = ARCH_PATH / clean_cat
            if not search_path.exists():
                return []

        for p in search_path.rglob(pattern):
            if p.is_file() and p.suffix in (".md", ".txt", ".json", ".yaml", ".yml"):
                stat = p.stat()
                rel_parts = p.relative_to(ARCH_PATH).parts
                cat = rel_parts[0] if len(rel_parts) > 1 else "root"
                results.append({
                    "name": p.name,
                    "category": cat,
                    "relative_path": str(p.relative_to(ARCH_PATH)),
                    "size_bytes": stat.st_size,
                    "modified_at": datetime.datetime.fromtimestamp(stat.st_mtime).isoformat()
                })

        results.sort(key=lambda x: x["modified_at"], reverse=True)
        return results
    except Exception as e:
        return [{"error": f"Failed to list architecture docs: {str(e)}"}]


@mcp.tool()
def load_architecture_doc(name: str) -> dict:
    """Load and read the full text of an architecture document.

    Args:
        name: Name or relative path of architecture doc to load.
    """
    try:
        target = _resolve_arch_file(name)
        if not target.is_file():
            matches = [p for p in ARCH_PATH.rglob("*") if p.is_file() and name.lower() in p.name.lower()]
            if matches:
                target = matches[0]
            else:
                return {"status": "error", "error": f"Architecture document '{name}' not found."}

        content = target.read_text(encoding="utf-8", errors="replace")
        stat = target.stat()
        rel_parts = target.relative_to(ARCH_PATH).parts
        cat = rel_parts[0] if len(rel_parts) > 1 else "root"

        return {
            "status": "success",
            "name": target.name,
            "category": cat,
            "relative_path": str(target.relative_to(ARCH_PATH)),
            "size_bytes": stat.st_size,
            "modified_at": datetime.datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "content": content
        }
    except Exception as e:
        return {"status": "error", "error": f"Failed to load architecture doc: {str(e)}"}


if __name__ == "__main__":
    mcp.run(transport="stdio")
