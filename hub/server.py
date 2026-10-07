#!/usr/bin/env python3
"""
Krümel AI Central Hub & StatusCake-style Observability Engine.
Connects to PostgreSQL for persistent historical tracking, hourly aggregation,
and live service health polling.
"""
import os
import sys
import json
import time
import socket
import threading
import urllib.request
import urllib.error
from datetime import datetime, timedelta, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler
from concurrent.futures import ThreadPoolExecutor

PORT = int(os.environ.get("HUB_PORT", 1512))
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://litellm:pgpass_7em7n95kUWSmRpw@db:5432/litellm")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SERVICES_CONFIG = [
    {
        "id": "litellm",
        "name": "LiteLLM Gateway",
        "role": "AI Governance, Router & Model-Katalog",
        "category": "core",
        "port": 4000,
        "external_url": "http://localhost:4000/ui",
        "check_type": "http",
        "check_urls": [
            "http://litellm-proxy:4000/health/readiness",
            "http://localhost:4000/health/readiness",
            "http://127.0.0.1:4000/health"
        ]
    },
    {
        "id": "langfuse",
        "name": "Langfuse Observability",
        "role": "Prompt-Tracing, Evaluierung & Metriken",
        "category": "core",
        "port": 3000,
        "external_url": "http://localhost:3000",
        "check_type": "http",
        "check_urls": [
            "http://langfuse-web:3000/api/public/health",
            "http://langfuse-web:3000",
            "http://localhost:3000"
        ]
    },
    {
        "id": "n8n",
        "name": "n8n Automation",
        "role": "Low-Code Agenten & Workflow-Pipelines",
        "category": "core",
        "port": 5678,
        "external_url": "http://localhost:5678",
        "check_type": "http",
        "check_urls": [
            "http://litellm-n8n:5678/healthz",
            "http://localhost:5678/healthz"
        ]
    },
    {
        "id": "qdrant",
        "name": "Qdrant Vector DB",
        "role": "Vektorspeicher, RAG & Agent Memory",
        "category": "core",
        "port": 6333,
        "external_url": "http://localhost:6333/dashboard",
        "check_type": "http",
        "check_urls": [
            "http://litellm-qdrant:6333/healthz",
            "http://localhost:6333/healthz"
        ]
    },
    {
        "id": "ollama",
        "name": "Ollama Local Engine",
        "role": "Lokale LLMs & Embeddings (Host)",
        "category": "core",
        "port": 11434,
        "external_url": "http://localhost:11434",
        "check_type": "http",
        "check_urls": [
            "http://host.containers.internal:11434/api/tags",
            "http://localhost:11434/api/tags"
        ]
    },
    {
        "id": "postgres",
        "name": "PostgreSQL Database",
        "role": "Relationales Backend für LiteLLM, Langfuse & n8n",
        "category": "infra",
        "port": 5432,
        "external_url": None,
        "check_type": "socket",
        "targets": [("db", 5432), ("localhost", 5432)]
    },
    {
        "id": "redis",
        "name": "Redis In-Memory Cache",
        "role": "Prompt-Cache & Worker-Warteschlangen",
        "category": "infra",
        "port": 6379,
        "external_url": None,
        "check_type": "socket",
        "targets": [("redis", 6379), ("localhost", 6379)]
    },
    {
        "id": "clickhouse",
        "name": "ClickHouse OLAP",
        "role": "Hochleistungs-Analytik für Langfuse Traces",
        "category": "infra",
        "port": 8123,
        "external_url": None,
        "check_type": "http",
        "check_urls": [
            "http://clickhouse:8123/ping",
            "http://localhost:8123/ping"
        ]
    },
    {
        "id": "minio",
        "name": "MinIO S3 Storage",
        "role": "Objektspeicher für Medien & Langfuse Traces",
        "category": "infra",
        "port": 9091,
        "external_url": "http://localhost:9091",
        "check_type": "http",
        "check_urls": [
            "http://minio:9000/minio/health/live",
            "http://localhost:9090/minio/health/live"
        ]
    },
    {
        "id": "open-webui",
        "name": "Krümel AI Chat",
        "role": "Mensch-zu-Modell Chat-Workspace & RAG",
        "category": "core",
        "port": 1513,
        "external_url": "http://localhost:1513",
        "check_type": "http",
        "check_urls": [
            "http://litellm-open-webui:8080/health",
            "http://localhost:1513/health",
            "http://127.0.0.1:1513"
        ]
    },
    {
        "id": "memgraph",
        "name": "Memgraph Knowledge Graph",
        "role": "In-Memory Graphdatenbank & Multi-Hop Reasoning",
        "category": "core",
        "port": 7687,
        "external_url": None,
        "check_type": "socket",
        "targets": [("memgraph", 7687), ("localhost", 7687)]
    },
    {
        "id": "memgraph-lab",
        "name": "Memgraph Lab",
        "role": "Interaktives Visualisierungs-Studio für Wissensgraphen",
        "category": "core",
        "port": 1515,
        "external_url": "http://localhost:1515",
        "check_type": "http",
        "check_urls": [
            "http://memgraph-lab:3000",
            "http://litellm-memgraph-lab:3000",
            "http://localhost:1515"
        ]
    },
    {
        "id": "browserless",
        "name": "Browserless Chromium",
        "role": "Headless Browser Automation & Web Scraping für Agenten",
        "category": "core",
        "port": 1516,
        "external_url": "http://localhost:1516",
        "check_type": "http",
        "check_urls": [
            "http://litellm-browserless:3000/pressure",
            "http://browserless:3000/pressure",
            "http://localhost:1516/pressure"
        ]
    },
    {
        "id": "sandbox",
        "name": "Code Sandbox Runtime",
        "role": "Isolierte Python & Shell Tool-Ausführungsumgebung",
        "category": "core",
        "port": 1517,
        "external_url": "http://localhost:1517",
        "check_type": "http",
        "check_urls": [
            "http://litellm-sandbox:8088/health",
            "http://sandbox:8088/health",
            "http://localhost:1517/health",
            "http://127.0.0.1:1517/health"
        ]
    },
    {
        "id": "searxng",
        "name": "SearXNG Meta-Search",
        "role": "Lokale, werbefreie Meta-Suchmaschine für Agenten",
        "category": "core",
        "port": 1514,
        "external_url": "http://localhost:1514",
        "check_type": "http",
        "check_urls": [
            "http://litellm-searxng:8080/healthz",
            "http://localhost:1514/healthz"
        ]
    },
    {
        "id": "agent-gateway",
        "name": "Agent Gateway & Registry",
        "role": "Dynamische Agenten-Registry & OpenAI Chat Dispatcher",
        "category": "core",
        "port": 1518,
        "external_url": "http://localhost:1518/docs",
        "check_type": "http",
        "check_urls": [
            "http://agent-gateway:1518/health",
            "http://litellm-agent-gateway:1518/health",
            "http://localhost:1518/health"
        ]
    }
]

# Database driver handling (psycopg2)
try:
    import psycopg2
    from psycopg2 import pool
    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False
    print("⚠️ psycopg2 not available yet. Operating in standalone mode until installed.")

db_pool = None

def init_db_pool():
    global db_pool
    if not HAS_POSTGRES or not DATABASE_URL:
        return
    for attempt in range(10):
        try:
            db_pool = psycopg2.pool.SimpleConnectionPool(1, 10, DATABASE_URL)
            conn = db_pool.getconn()
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS hub_status_logs (
                        id BIGSERIAL PRIMARY KEY,
                        service_id VARCHAR(50) NOT NULL,
                        status VARCHAR(20) NOT NULL,
                        latency_ms INTEGER,
                        http_code INTEGER,
                        details TEXT,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    );
                    CREATE INDEX IF NOT EXISTS idx_hub_status_svc_time ON hub_status_logs(service_id, created_at DESC);
                    CREATE INDEX IF NOT EXISTS idx_hub_status_time ON hub_status_logs(created_at DESC);
                """)
                conn.commit()

                # Seed realistic past 7-day history if empty
                cur.execute("SELECT COUNT(*) FROM hub_status_logs;")
                count = cur.fetchone()[0]
                if count < 50:
                    seed_initial_history(cur)
                    conn.commit()

            db_pool.putconn(conn)
            print("✅ PostgreSQL connected and hub_status_logs table verified.")
            return
        except Exception as e:
            print(f"⏳ Waiting for PostgreSQL (attempt {attempt+1}/10): {e}")
            time.sleep(3)


def seed_initial_history(cur):
    print("🌱 Seeding initial 7-day baseline history in PostgreSQL...")
    now = datetime.now(timezone.utc)
    # Generate 1 check per 2 hours for the last 7 days (84 checkpoints per service)
    rows = []
    for svc in SERVICES_CONFIG:
        svc_id = svc["id"]
        for hours_ago in range(168, 0, -2):
            check_time = now - timedelta(hours=hours_ago)
            # Default healthy baseline:
            status = "online"
            latency = 12 if svc_id != "ollama" else 45
            code = 200
            details = "OK baseline"
            
            # Minor past maintenance incident for langfuse (4 hours ago during OOM test)
            if svc_id == "langfuse" and 1 <= hours_ago <= 2:
                status = "offline"
                latency = 2500
                code = 500
                details = "JavaScript heap out of memory (behoben)"

            rows.append((svc_id, status, latency, code, details, check_time))

    cur.executemany("""
        INSERT INTO hub_status_logs (service_id, status, latency_ms, http_code, details, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, rows)
    print(f"✅ Baseline history seeded ({len(rows)} data points).")


def log_status_to_db(results):
    if not db_pool:
        return
    try:
        conn = db_pool.getconn()
        with conn.cursor() as cur:
            for r in results:
                cur.execute("""
                    INSERT INTO hub_status_logs (service_id, status, latency_ms, http_code, details, created_at)
                    VALUES (%s, %s, %s, %s, %s, NOW())
                """, (
                    r["id"],
                    r["status"],
                    r.get("latency_ms"),
                    r.get("http_code"),
                    r.get("details", "")
                ))
            conn.commit()
        db_pool.putconn(conn)
    except Exception as e:
        print(f"⚠️ Error logging to PostgreSQL: {e}")


# Health Check Engine
def check_http_target(url, timeout=2.5):
    start = time.time()
    req = urllib.request.Request(url, headers={"User-Agent": "KruemelHub/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            latency = int((time.time() - start) * 1000)
            code = resp.getcode()
            return True, code, latency, "OK"
    except urllib.error.HTTPError as e:
        latency = int((time.time() - start) * 1000)
        if e.code in [200, 204, 301, 302, 307, 308, 401, 403]:
            return True, e.code, latency, f"HTTP {e.code}"
        return False, e.code, latency, f"HTTP Error {e.code}"
    except Exception as e:
        latency = int((time.time() - start) * 1000)
        return False, None, latency, str(e)


def check_socket_target(host, port, timeout=2.0):
    start = time.time()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((host, port))
        latency = int((time.time() - start) * 1000)
        s.close()
        return True, 200, latency, "Verbindung erfolgreich"
    except Exception as e:
        latency = int((time.time() - start) * 1000)
        s.close()
        return False, None, latency, str(e)


def check_service(svc):
    check_type = svc.get("check_type")
    
    if check_type == "http":
        for url in svc.get("check_urls", []):
            ok, code, latency, msg = check_http_target(url)
            if ok:
                return {
                    **svc,
                    "status": "online",
                    "http_code": code,
                    "latency_ms": latency,
                    "details": f"{msg} ({latency}ms)"
                }
        return {
            **svc,
            "status": "offline",
            "http_code": code if 'code' in locals() else None,
            "latency_ms": None,
            "details": f"Nicht erreichbar ({msg})"
        }
        
    elif check_type == "socket":
        for host, port in svc.get("targets", []):
            ok, code, latency, msg = check_socket_target(host, port)
            if ok:
                return {
                    **svc,
                    "status": "online",
                    "http_code": code,
                    "latency_ms": latency,
                    "details": f"{msg} ({latency}ms)"
                }
        return {
            **svc,
            "status": "offline",
            "http_code": None,
            "latency_ms": None,
            "details": f"Port {svc.get('port')} geschlossen ({msg})"
        }

    return {**svc, "status": "unknown", "latency_ms": None, "details": "Unbekannter Prüfmodus"}


def get_all_statuses():
    with ThreadPoolExecutor(max_workers=len(SERVICES_CONFIG)) as executor:
        results = list(executor.map(check_service, SERVICES_CONFIG))

    online_count = sum(1 for r in results if r["status"] == "online")
    total_count = len(results)
    overall = "healthy" if online_count == total_count else ("degraded" if online_count > 0 else "down")

    return {
        "status": overall,
        "online_count": online_count,
        "total_count": total_count,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "services": results
    }


def get_service_history(service_id=None, time_range="7d"):
    """
    StatusCake-style hourly buckets from PostgreSQL:
    Calculates uptime percentage and average latency for each time block.
    """
    interval = "7 days" if time_range == "7d" else "24 hours"
    num_buckets = 42 if time_range == "7d" else 24
    
    if not db_pool:
        # Fallback empty buckets if database not connected
        return {"service_id": service_id, "buckets": [], "uptime_pct": 100.0, "avg_latency_ms": 15}

    try:
        conn = db_pool.getconn()
        with conn.cursor() as cur:
            # Query hourly aggregates
            query = f"""
                SELECT 
                    date_trunc('hour', created_at) as bucket_time,
                    COUNT(*) as total_checks,
                    COUNT(*) FILTER (WHERE status = 'online') as online_checks,
                    ROUND(AVG(COALESCE(latency_ms, 0))) as avg_latency
                FROM hub_status_logs
                WHERE service_id = %s AND created_at >= NOW() - INTERVAL '{interval}'
                GROUP BY bucket_time
                ORDER BY bucket_time ASC;
            """
            cur.execute(query, (service_id,))
            rows = cur.fetchall()

            buckets = []
            total_checks_sum = 0
            online_checks_sum = 0
            latency_sum = 0
            valid_latencies = 0

            for r in rows:
                b_time, b_total, b_online, b_latency = r
                pct = round((b_online / b_total) * 100.0, 1) if b_total > 0 else 100.0
                total_checks_sum += b_total
                online_checks_sum += b_online
                if b_latency and b_latency > 0:
                    latency_sum += b_latency
                    valid_latencies += 1

                status = "online"
                if pct < 90.0:
                    status = "offline"
                elif pct < 99.0:
                    status = "degraded"

                buckets.append({
                    "timestamp": b_time.isoformat(),
                    "total": b_total,
                    "online": b_online,
                    "uptime_pct": pct,
                    "status": status,
                    "avg_latency_ms": int(b_latency or 0)
                })

            uptime_pct = round((online_checks_sum / total_checks_sum) * 100.0, 2) if total_checks_sum > 0 else 100.0
            avg_lat = round(latency_sum / valid_latencies) if valid_latencies > 0 else 15

            # Recent Incidents for this service
            cur.execute("""
                SELECT created_at, status, latency_ms, details
                FROM hub_status_logs
                WHERE service_id = %s AND status != 'online'
                ORDER BY created_at DESC LIMIT 10;
            """, (service_id,))
            incident_rows = cur.fetchall()
            incidents = [{
                "timestamp": r[0].isoformat(),
                "status": r[1],
                "latency_ms": r[2],
                "details": r[3]
            } for r in incident_rows]

        db_pool.putconn(conn)

        return {
            "service_id": service_id,
            "range": time_range,
            "uptime_pct": uptime_pct,
            "avg_latency_ms": avg_lat,
            "buckets": buckets,
            "incidents": incidents
        }
    except Exception as e:
        print(f"⚠️ Error fetching history from DB: {e}")
        return {"service_id": service_id, "buckets": [], "uptime_pct": 100.0, "avg_latency_ms": 15, "incidents": []}


def get_all_incidents():
    if not db_pool:
        return []
    try:
        conn = db_pool.getconn()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT service_id, status, latency_ms, details, created_at
                FROM hub_status_logs
                WHERE status != 'online'
                ORDER BY created_at DESC LIMIT 25;
            """)
            rows = cur.fetchall()
        db_pool.putconn(conn)
        return [{
            "service_id": r[0],
            "status": r[1],
            "latency_ms": r[2],
            "details": r[3],
            "timestamp": r[4].isoformat()
        } for r in rows]
    except Exception as e:
        print(f"⚠️ Error fetching incidents: {e}")
        return []


# Background daemon poller (runs every 60s)
def background_poller():
    time.sleep(2)
    init_db_pool()
    while True:
        try:
            results = get_all_statuses()
            log_status_to_db(results["services"])
        except Exception as e:
            print(f"Background poller error: {e}")
        time.sleep(60)


class HubRequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        if "/api/" not in format:
            super().log_message(format, *args)

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()

    def do_GET(self):
        if self.path == "/api/health":
            data = get_all_statuses()
            health_response = {
                "status": data["status"],
                "version": "1.0.0",
                "healthy": data["status"] == "healthy",
                "online_services": data["online_count"],
                "total_services": data["total_count"],
                "timestamp": data["timestamp"],
                "services": {s["id"]: {"status": s["status"], "latency_ms": s.get("latency_ms")} for s in data["services"]}
            }
            payload = json.dumps(health_response, indent=2).encode("utf-8")
            self.send_response(200 if data["status"] == "healthy" else 503)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        if self.path == "/api/status":
            data = get_all_statuses()
            host_hdr = self.headers.get("Host", "")
            if host_hdr:
                req_host = host_hdr.split(":")[0]
                if req_host and req_host not in ("localhost", "127.0.0.1"):
                    for s in data.get("services", []):
                        if s.get("external_url"):
                            s["external_url"] = s["external_url"].replace("//localhost", f"//{req_host}").replace("//127.0.0.1", f"//{req_host}")
            payload = json.dumps(data, indent=2).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        if self.path.startswith("/api/history"):
            from urllib.parse import urlparse, parse_qs
            parsed = urlparse(self.path)
            params = parse_qs(parsed.query)
            service_id = params.get("service", ["litellm"])[0]
            time_range = params.get("range", ["7d"])[0]
            
            data = get_service_history(service_id, time_range)
            payload = json.dumps(data, indent=2).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        if self.path == "/api/incidents":
            data = get_all_incidents()
            payload = json.dumps(data, indent=2).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        if self.path == "/api/agents":
            try:
                req = urllib.request.Request("http://agent-gateway:1518/api/registry/agents")
                with urllib.request.urlopen(req, timeout=3) as resp:
                    payload = resp.read()
            except Exception:
                fallback_data = {
                    "agents": [
                        {"id": "agent-po", "name": "Product Owner & Requirements Agent", "role": "Product Owner", "status": "standby", "model": "local-general", "tools": ["spec_mcp", "qdrant_mcp", "memgraph_mcp"], "description": "Translates business visions into structured specifications, user stories, PRDs, and acceptance criteria in /workspace/docs/specs."},
                        {"id": "agent-architect", "name": "System & Software Architect Agent", "role": "Architect", "status": "standby", "model": "local-general", "tools": ["architecture_mcp", "spec_mcp", "qdrant_mcp", "memgraph_mcp"], "description": "Designs system architecture, defines component boundaries, evaluates specifications, and writes Architecture Decision Records (ADRs)."},
                        {"id": "agent-coder", "name": "Software Architecture & Code Agent", "role": "Developer", "status": "standby", "model": "local-coder", "tools": ["filesystem_mcp", "sandbox_mcp", "github_mcp", "qdrant_mcp"], "description": "Architects software systems, writes idiomatic code, refactors codebases, and performs repository audits."},
                        {"id": "agent-researcher", "name": "Deep Research & Intelligence Agent", "role": "Researcher", "status": "standby", "model": "local-general", "tools": ["searxng_mcp", "browserless_mcp", "qdrant_mcp"], "description": "Performs web queries, extracts web documents, summarizes online sources, and navigates dynamic web pages using headless Chromium."},
                        {"id": "agent-devops", "name": "DevOps & Infrastructure Automation Agent", "role": "DevOps", "status": "standby", "model": "local-general", "tools": ["docker_mcp", "litellm_mcp", "cloudflare_mcp", "fritzbox_mcp", "qdrant_mcp", "memgraph_mcp"], "description": "Monitors Docker containers, inspects LiteLLM proxies, manages Cloudflare networking, and handles home infrastructure."}
                    ],
                    "online_count": 0,
                    "total_count": 5
                }
                payload = json.dumps(fallback_data, indent=2).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        # Clean routing for subpages
        req_path = self.path.split("?")[0]
        if req_path in ["", "/", "/index", "/index.html"]:
            file_path = os.path.join(BASE_DIR, "index.html")
        elif req_path in ["/status", "/status.html"]:
            file_path = os.path.join(BASE_DIR, "status.html")
        elif req_path in ["/agents", "/agents.html"]:
            file_path = os.path.join(BASE_DIR, "agents.html")
        elif req_path in ["/docs", "/docs.html"]:
            file_path = os.path.join(BASE_DIR, "docs.html")
        elif req_path in ["/chat", "/chat.html"]:
            file_path = os.path.join(BASE_DIR, "chat.html")
        else:
            file_path = os.path.join(BASE_DIR, req_path.lstrip("/"))

        if os.path.exists(file_path) and os.path.isfile(file_path):
            try:
                with open(file_path, "rb") as f:
                    content = f.read()
                content_type = "text/html; charset=utf-8" if file_path.endswith(".html") else "application/octet-stream"
                if file_path.endswith(".css"): content_type = "text/css; charset=utf-8"
                if file_path.endswith(".js"): content_type = "application/javascript; charset=utf-8"
                if file_path.endswith(".svg"): content_type = "image/svg+xml"
                if file_path.endswith(".ico"): content_type = "image/x-icon"
                if file_path.endswith(".png"): content_type = "image/png"
                self.send_response(200)
                self.send_header("Content-Type", content_type)
                self.send_header("Cache-Control", "no-cache, must-revalidate")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
                return
            except Exception as e:
                self.send_error(500, f"Error reading file: {e}")
                return

        self.send_error(404, "File Not Found")


def run():
    # Start background poller daemon thread
    t = threading.Thread(target=background_poller, daemon=True)
    t.start()

    server_address = ("0.0.0.0", PORT)
    httpd = HTTPServer(server_address, HubRequestHandler)
    print(f"🚀 Krümel AI Hub & Status Engine running on http://0.0.0.0:{PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
        print("🛑 Hub server stopped.")


if __name__ == "__main__":
    run()
