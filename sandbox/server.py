#!/usr/bin/env python3
"""
Krümel AI Isolated Code Execution Sandbox Microservice.
Provides a controlled, ephemeral runtime for AI agents to run Python and shell snippets.
"""

import json
import os
import subprocess
import sys
import tempfile
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOST = "0.0.0.0"
PORT = int(os.environ.get("SANDBOX_PORT", 8088))
DEFAULT_TIMEOUT_SEC = 15
MAX_TIMEOUT_SEC = 60
MAX_OUTPUT_BYTES = 500 * 1024  # 500 KB limit to prevent OOM via print loops


class SandboxHandler(BaseHTTPRequestHandler):
    def _send_json(self, status_code: int, data: dict):
        response_bytes = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()
        self.wfile.write(response_bytes)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self):
        if self.path in ("/", "/health", "/status"):
            try:
                uid = os.getuid()
            except AttributeError:
                uid = None
            self._send_json(200, {
                "status": "ok",
                "service": "kruemel-sandbox",
                "description": "Krümel AI Isolated Code Execution Sandbox",
                "python_version": sys.version.split()[0],
                "uid": uid,
                "supported_languages": ["python", "bash", "sh"],
                "default_timeout_sec": DEFAULT_TIMEOUT_SEC,
                "max_timeout_sec": MAX_TIMEOUT_SEC
            })
        else:
            self._send_json(404, {"error": "Not Found", "path": self.path})

    def do_POST(self):
        if self.path != "/run":
            self._send_json(404, {"error": "Endpoint not found. Use POST /run"})
            return

        content_length = int(self.headers.get("Content-Length", 0))
        if content_length <= 0:
            self._send_json(400, {"error": "Missing request body"})
            return

        try:
            body = self.rfile.read(content_length).decode("utf-8")
            payload = json.loads(body)
        except Exception as e:
            self._send_json(400, {"error": f"Invalid JSON payload: {str(e)}"})
            return

        code = payload.get("code")
        if not code or not isinstance(code, str):
            self._send_json(400, {"error": "'code' string field is required"})
            return

        language = str(payload.get("language", "python")).lower().strip()
        timeout = payload.get("timeout", DEFAULT_TIMEOUT_SEC)
        try:
            timeout = min(max(int(timeout), 1), MAX_TIMEOUT_SEC)
        except (ValueError, TypeError):
            timeout = DEFAULT_TIMEOUT_SEC

        result = self._execute_code(code, language, timeout)
        self._send_json(200, result)

    def _execute_code(self, code: str, language: str, timeout: int) -> dict:
        t_start = time.perf_counter()
        suffix = ".py" if language == "python" else ".sh"

        with tempfile.TemporaryDirectory(prefix="kruemel_exec_") as tmpdir:
            script_path = os.path.join(tmpdir, f"script{suffix}")
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(code)

            if language == "python":
                cmd = [sys.executable, "-u", script_path]
            elif language in ("bash", "sh"):
                cmd = ["/bin/sh", script_path]
            else:
                return {
                    "stdout": "",
                    "stderr": f"Unsupported language: '{language}'. Supported: python, bash, sh",
                    "exit_code": 1,
                    "duration_ms": 0,
                    "timed_out": False
                }

            env = {
                "PATH": "/usr/local/bin:/usr/bin:/bin",
                "PYTHONUNBUFFERED": "1",
                "PYTHONDONTWRITEBYTECODE": "1",
                "HOME": tmpdir,
                "TMPDIR": tmpdir,
            }

            try:
                proc = subprocess.run(
                    cmd,
                    cwd=tmpdir,
                    env=env,
                    capture_output=True,
                    timeout=timeout,
                    text=True,
                    errors="replace"
                )
                duration_ms = round((time.perf_counter() - t_start) * 1000, 2)
                stdout = proc.stdout[:MAX_OUTPUT_BYTES]
                stderr = proc.stderr[:MAX_OUTPUT_BYTES]

                return {
                    "stdout": stdout,
                    "stderr": stderr,
                    "exit_code": proc.returncode,
                    "duration_ms": duration_ms,
                    "timed_out": False
                }
            except subprocess.TimeoutExpired as e:
                duration_ms = round((time.perf_counter() - t_start) * 1000, 2)
                stdout = (e.stdout or "")[:MAX_OUTPUT_BYTES] if isinstance(e.stdout, str) else ""
                stderr = (e.stderr or "")[:MAX_OUTPUT_BYTES] if isinstance(e.stderr, str) else ""
                return {
                    "stdout": stdout,
                    "stderr": stderr + f"\n[Execution timed out after {timeout} seconds]",
                    "exit_code": 124,
                    "duration_ms": duration_ms,
                    "timed_out": True
                }
            except Exception as e:
                duration_ms = round((time.perf_counter() - t_start) * 1000, 2)
                return {
                    "stdout": "",
                    "stderr": f"Execution error: {str(e)}",
                    "exit_code": 1,
                    "duration_ms": duration_ms,
                    "timed_out": False
                }

    def log_message(self, format, *args):
        # Concise logging to stdout
        sys.stdout.write(f"[sandbox] {self.address_string()} - {format % args}\n")
        sys.stdout.flush()


def run():
    server_address = (HOST, PORT)
    httpd = ThreadingHTTPServer(server_address, SandboxHandler)
    print(f"[kruemel-sandbox] Server listening on {HOST}:{PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()


if __name__ == "__main__":
    run()
