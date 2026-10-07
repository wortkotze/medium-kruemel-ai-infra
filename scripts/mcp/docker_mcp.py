#!/usr/bin/env python3
"""
Docker Monitoring & Container Management FastMCP Server.
Allows DevOps agents to monitor container states, inspect logs, and safely trigger restarts.
"""
import http.client
import json
import os
import re
import socket
import sys
import urllib.parse
from mcp.server.fastmcp import FastMCP

DOCKER_SOCKET = os.getenv("DOCKER_SOCKET", "/var/run/docker.sock")
DOCKER_HOST = os.getenv("DOCKER_HOST", "")

mcp = FastMCP("Docker Monitoring MCP")


class UnixSocketConnection(http.client.HTTPConnection):
    """HTTPConnection over a local UNIX domain socket."""
    def __init__(self, socket_path: str, timeout: int = 30):
        super().__init__("localhost", timeout=timeout)
        self.socket_path = socket_path

    def connect(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.settimeout(self.timeout)
        self.sock.connect(self.socket_path)


def _docker_request(path: str, method: str = "GET", body: bytes = None, timeout: int = 30) -> tuple[int, bytes]:
    """Execute raw HTTP request against Docker Engine API via socket or TCP host."""
    if DOCKER_HOST.startswith("tcp://") or DOCKER_HOST.startswith("http://"):
        parsed = urllib.parse.urlparse(DOCKER_HOST.replace("tcp://", "http://"))
        conn = http.client.HTTPConnection(parsed.hostname, parsed.port or 2375, timeout=timeout)
    else:
        socket_path = DOCKER_SOCKET
        if not os.path.exists(socket_path):
            raise FileNotFoundError(f"Docker socket not found at '{socket_path}'. Make sure it is mounted into the container.")
        conn = UnixSocketConnection(socket_path, timeout=timeout)

    try:
        headers = {"Host": "localhost"}
        if body:
            headers["Content-Type"] = "application/json"
            headers["Content-Length"] = str(len(body))
        conn.request(method, path, body=body, headers=headers)
        res = conn.getresponse()
        data = res.read()
        return res.status, data
    finally:
        conn.close()


def _clean_docker_logs(raw_bytes: bytes) -> str:
    """Strip 8-byte Docker multiplex stream headers (stdout=1, stderr=2) if present."""
    if len(raw_bytes) < 8:
        return raw_bytes.decode("utf-8", errors="replace")

    # Docker multiplex stream frames begin with [STREAM_TYPE, 0, 0, 0, SIZE1, SIZE2, SIZE3, SIZE4]
    cleaned = []
    idx = 0
    total = len(raw_bytes)
    has_multiplex = False

    while idx + 8 <= total:
        stream_type = raw_bytes[idx]
        if stream_type in (1, 2) and raw_bytes[idx + 1:idx + 4] == b"\x00\x00\x00":
            has_multiplex = True
            frame_len = int.from_bytes(raw_bytes[idx + 4:idx + 8], byteorder="big")
            payload = raw_bytes[idx + 8:idx + 8 + frame_len]
            cleaned.append(payload.decode("utf-8", errors="replace"))
            idx += 8 + frame_len
        else:
            break

    if has_multiplex and idx == total:
        return "".join(cleaned)
    return raw_bytes.decode("utf-8", errors="replace")


@mcp.tool()
def get_container_status(container_name: str = "") -> list | dict:
    """Retrieve status, state, uptime, and ports of all containers or a specific container.

    Args:
        container_name: Optional name or ID of container to filter (e.g. 'litellm-proxy', 'litellm-db').
    """
    try:
        status_code, data = _docker_request("/containers/json?all=true")
        if status_code != 200:
            return {"error": f"Docker API returned status {status_code}: {data.decode('utf-8', errors='replace')}"}

        containers = json.loads(data.decode("utf-8"))
        results = []

        for c in containers:
            raw_names = c.get("Names", [])
            clean_names = [n.lstrip("/") for n in raw_names]
            c_id = c.get("Id", "")[:12]
            image = c.get("Image", "")
            state = c.get("State", "")
            status = c.get("Status", "")

            # Formatted ports
            ports = []
            for p in c.get("Ports", []):
                pub = p.get("PublicPort")
                priv = p.get("PrivatePort")
                proto = p.get("Type", "tcp")
                if pub:
                    ports.append(f"{pub}->{priv}/{proto}")
                elif priv:
                    ports.append(f"{priv}/{proto}")

            info = {
                "id": c_id,
                "names": clean_names,
                "image": image,
                "state": state,
                "status": status,
                "ports": ports,
            }

            if container_name:
                target = container_name.lower().strip().lstrip("/")
                if target == c_id or any(target in n.lower() for n in clean_names):
                    return info

            results.append(info)

        if container_name:
            return {"error": f"Container '{container_name}' not found."}

        return results

    except Exception as e:
        return {"error": f"Failed to get container status: {str(e)}"}


@mcp.tool()
def get_container_logs(container_name: str, tail: int = 100) -> dict:
    """Inspect stdout and stderr logs of a specific Docker container.

    Args:
        container_name: Container name or ID (e.g. 'litellm-proxy', 'langfuse-web').
        tail: Number of recent log lines to retrieve (default: 100, max: 1000).
    """
    try:
        tail_count = min(max(tail, 1), 1000)
        target = urllib.parse.quote(container_name.strip().lstrip("/"))
        path = f"/containers/{target}/logs?stdout=true&stderr=true&tail={tail_count}&timestamps=true"

        status_code, data = _docker_request(path, timeout=30)
        if status_code == 404:
            return {"error": f"Container '{container_name}' not found."}
        if status_code != 200:
            return {"error": f"Docker API returned status {status_code}: {data.decode('utf-8', errors='replace')}"}

        logs = _clean_docker_logs(data)
        lines = logs.splitlines()

        return {
            "container": container_name,
            "line_count": len(lines),
            "tail_requested": tail_count,
            "logs": logs
        }

    except Exception as e:
        return {"container": container_name, "error": f"Failed to get logs: {str(e)}"}


@mcp.tool()
def restart_container(container_name: str) -> dict:
    """Safely restart a Docker container with standard grace period.

    Args:
        container_name: Name or ID of container to restart (e.g. 'litellm-redis', 'litellm-memgraph').
    """
    try:
        target = urllib.parse.quote(container_name.strip().lstrip("/"))
        path = f"/containers/{target}/restart?t=10"

        status_code, data = _docker_request(path, method="POST", timeout=45)
        if status_code == 204:
            return {
                "container": container_name,
                "status": "success",
                "message": f"Container '{container_name}' successfully restarted."
            }
        elif status_code == 404:
            return {"container": container_name, "status": "error", "error": f"Container '{container_name}' not found."}
        else:
            return {
                "container": container_name,
                "status": "error",
                "error": f"Restart failed with status {status_code}: {data.decode('utf-8', errors='replace')}"
            }

    except Exception as e:
        return {"container": container_name, "status": "error", "error": f"Failed to restart container: {str(e)}"}


if __name__ == "__main__":
    mcp.run(transport="stdio")
