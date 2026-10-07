#!/usr/bin/env python3
"""
Isolated Code Execution Sandbox FastMCP Server.
Allows AI agents to execute ephemeral Python and Shell code in a secure, non-root, resource-limited container.
"""
import json
import os
import urllib.error
import urllib.request
from mcp.server.fastmcp import FastMCP

SANDBOX_URL = os.getenv("SANDBOX_URL", "http://sandbox:8088")

mcp = FastMCP("Isolated Code Execution Sandbox MCP")


def _run_in_sandbox(code: str, language: str = "python", timeout: int = 15) -> dict:
    url = f"{SANDBOX_URL.rstrip('/')}/run"
    payload = {
        "code": code,
        "language": language,
        "timeout": min(max(timeout, 1), 60)
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout + 5) as res:
            return json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8", errors="replace")
        return {
            "stdout": "",
            "stderr": f"HTTP {e.code}: {err_msg}",
            "exit_code": 1,
            "timed_out": False
        }
    except Exception as e:
        return {
            "stdout": "",
            "stderr": f"Sandbox request error: {str(e)}",
            "exit_code": 1,
            "timed_out": False
        }


@mcp.tool()
def execute_python(code: str, timeout: int = 15) -> dict:
    """Execute Python 3.11 code inside the isolated container sandbox.

    Returns stdout, stderr, exit_code, and execution duration in milliseconds.
    Safe for testing calculations, algorithms, data formatting, and scripts.
    """
    return _run_in_sandbox(code=code, language="python", timeout=timeout)


@mcp.tool()
def execute_shell(command: str, timeout: int = 15) -> dict:
    """Execute Alpine shell (/bin/sh) command inside the isolated sandbox container.

    Returns stdout, stderr, exit_code, and execution duration in milliseconds.
    Runs under unprivileged user (UID 1000) with no access to host or production data.
    """
    return _run_in_sandbox(code=command, language="sh", timeout=timeout)


if __name__ == "__main__":
    mcp.run(transport="stdio")
