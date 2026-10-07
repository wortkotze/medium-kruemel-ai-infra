#!/usr/bin/env python3
"""
Krümel AI – Central Agent Registry & Chat Gateway (Port 1518).

Provides:
1. Dynamic Agent Worker Registration & Heartbeats (Agent Registry Pattern).
2. OpenAI-compatible /v1/models and /v1/chat/completions for Open WebUI & Clients.
3. Smart Routing: Proxies chat to active Python workers in kruemel-ai-agents,
   or seamlessly falls back to LiteLLM Proxy (:4000) using agent virtual keys.
4. Rich Status API for Krümel Hub Cockpit (:1512).
"""
import asyncio
import json
import logging
import os
import time
from typing import Any, AsyncGenerator, Dict, List, Optional
import httpx
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("agent-gateway")

PORT = int(os.environ.get("GATEWAY_PORT", 1518))
LITELLM_URL = os.environ.get("LITELLM_URL", "http://litellm-proxy:4000").rstrip("/")
LITELLM_MASTER_KEY = os.environ.get("LITELLM_MASTER_KEY", "")
CONFIG_PATH = os.environ.get("CONFIG_PATH", "/config/infra_contract.json")
HEARTBEAT_TIMEOUT_SEC = 45

app = FastAPI(
    title="Krümel AI Agent Gateway & Registry",
    version="1.0.0",
    description="Central dynamic agent registry, dispatch, and OpenAI-compatible proxy."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Data Models ─────────────────────────────────────────────────────────────

class AgentRegistration(BaseModel):
    id: str = Field(..., description="Unique agent identifier (e.g. agent-researcher)")
    name: str = Field(..., description="Human readable name")
    role: str = Field(..., description="Agent role / domain")
    endpoint: str = Field(..., description="Worker HTTP endpoint (e.g. http://host.containers.internal:8004)")
    model: Optional[str] = "local-general"
    tools: List[str] = Field(default_factory=list)
    capabilities: List[str] = Field(default_factory=list)
    version: Optional[str] = "1.0.0"
    description: Optional[str] = ""

class HeartbeatRequest(BaseModel):
    id: str
    endpoint: Optional[str] = None

# In-memory Agent Store with Seeding
class AgentState:
    def __init__(self, agent_id: str, name: str, role: str, model: str, tools: List[str], description: str):
        self.id = agent_id
        self.name = name
        self.role = role
        self.model = model
        self.tools = tools
        self.description = description
        self.status = "standby"  # "online" | "standby" | "busy"
        self.endpoint: Optional[str] = None
        self.capabilities: List[str] = []
        self.version = "1.0.0"
        self.last_heartbeat: Optional[float] = None
        self.registered_at: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "model": self.model,
            "tools": self.tools,
            "description": self.description,
            "status": self.status,
            "endpoint": self.endpoint,
            "capabilities": self.capabilities,
            "version": self.version,
            "last_heartbeat": self.last_heartbeat,
            "registered_at": self.registered_at,
            "heartbeat_age_sec": round(time.time() - self.last_heartbeat, 1) if self.last_heartbeat else None
        }

# Pre-seeded canonical 5 roles
SEED_AGENTS: Dict[str, Dict[str, Any]] = {
    "agent-po": {
        "name": "Product Owner & Requirements Agent",
        "role": "Product Owner",
        "model": "local-general",
        "tools": ["spec_mcp", "qdrant_mcp", "memgraph_mcp"],
        "description": "Translates business visions into structured specifications, user stories, PRDs, and acceptance criteria in /workspace/docs/specs."
    },
    "agent-architect": {
        "name": "System & Software Architect Agent",
        "role": "Architect",
        "model": "local-general",
        "tools": ["architecture_mcp", "spec_mcp", "qdrant_mcp", "memgraph_mcp"],
        "description": "Designs system architecture, defines component boundaries, evaluates specifications, and writes Architecture Decision Records (ADRs)."
    },
    "agent-coder": {
        "name": "Software Architecture & Code Agent",
        "role": "Developer",
        "model": "local-coder",
        "tools": ["filesystem_mcp", "sandbox_mcp", "github_mcp", "qdrant_mcp"],
        "description": "Architects software systems, writes idiomatic code, refactors codebases, and performs repository audits."
    },
    "agent-researcher": {
        "name": "Deep Research & Intelligence Agent",
        "role": "Researcher",
        "model": "local-general",
        "tools": ["searxng_mcp", "browserless_mcp", "qdrant_mcp"],
        "description": "Performs web queries, extracts web documents, summarizes online sources, and navigates dynamic web pages using headless Chromium."
    },
    "agent-devops": {
        "name": "DevOps & Infrastructure Automation Agent",
        "role": "DevOps",
        "model": "local-general",
        "tools": ["docker_mcp", "litellm_mcp", "cloudflare_mcp", "fritzbox_mcp", "qdrant_mcp", "memgraph_mcp"],
        "description": "Monitors Docker containers, inspects LiteLLM proxies, manages Cloudflare networking, and handles home infrastructure."
    }
}

registry: Dict[str, AgentState] = {}

def init_registry():
    """Initializes the registry with the 5 canonical Krümel roles."""
    for aid, meta in SEED_AGENTS.items():
        if aid not in registry:
            registry[aid] = AgentState(
                agent_id=aid,
                name=meta["name"],
                role=meta["role"],
                model=meta["model"],
                tools=meta["tools"],
                description=meta["description"]
            )
    logger.info(f"Initialized Agent Registry with {len(registry)} canonical roles.")

init_registry()

# ─── Background TTL Checker ──────────────────────────────────────────────────

async def ttl_sweeper():
    """Periodically marks agents as standby if heartbeat expires."""
    while True:
        try:
            now = time.time()
            for agent in registry.values():
                if agent.status in ("online", "busy") and agent.last_heartbeat:
                    if (now - agent.last_heartbeat) > HEARTBEAT_TIMEOUT_SEC:
                        logger.warning(f"Agent {agent.id} heartbeat expired (> {HEARTBEAT_TIMEOUT_SEC}s). Switching to standby.")
                        agent.status = "standby"
                        agent.endpoint = None
        except Exception as e:
            logger.error(f"Error in TTL sweeper: {e}")
        await asyncio.sleep(10)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(ttl_sweeper())

# ─── Health & Registry Endpoints ─────────────────────────────────────────────

@app.get("/health")
@app.get("/api/health")
async def get_health():
    online_count = sum(1 for a in registry.values() if a.status == "online")
    return {
        "status": "healthy",
        "service": "kruemel-agent-gateway",
        "version": "1.0.0",
        "online_agents": online_count,
        "total_agents": len(registry),
        "timestamp": time.time()
    }

@app.get("/api/registry/agents")
async def list_agents():
    """Returns all agents, their status, tools, and endpoints for Krümel Hub."""
    return {
        "agents": [a.to_dict() for a in registry.values()],
        "online_count": sum(1 for a in registry.values() if a.status == "online"),
        "total_count": len(registry)
    }

@app.post("/api/registry/register")
async def register_agent(reg: AgentRegistration):
    """Called by Python workers in kruemel-ai-agents on startup."""
    now = time.time()
    if reg.id not in registry:
        registry[reg.id] = AgentState(
            agent_id=reg.id,
            name=reg.name,
            role=reg.role,
            model=reg.model or "local-general",
            tools=reg.tools,
            description=reg.description or ""
        )
    
    agent = registry[reg.id]
    agent.name = reg.name
    agent.role = reg.role
    agent.endpoint = reg.endpoint.rstrip("/")
    agent.tools = reg.tools or agent.tools
    agent.capabilities = reg.capabilities
    agent.version = reg.version or agent.version
    agent.status = "online"
    agent.last_heartbeat = now
    agent.registered_at = agent.registered_at or now

    logger.info(f"✅ Registered active agent worker '{reg.id}' at {agent.endpoint}")
    return {"status": "registered", "agent": agent.to_dict()}

@app.post("/api/registry/heartbeat")
async def agent_heartbeat(hb: HeartbeatRequest):
    """Keepalive ping from running agent workers."""
    if hb.id not in registry:
        raise HTTPException(status_code=404, detail=f"Agent '{hb.id}' not found in registry.")
    agent = registry[hb.id]
    agent.last_heartbeat = time.time()
    if hb.endpoint:
        agent.endpoint = hb.endpoint
    if agent.endpoint:
        agent.status = "online"
    return {"status": "ok", "id": hb.id, "last_heartbeat": agent.last_heartbeat, "status_now": agent.status}

@app.post("/api/registry/unregister")
async def unregister_agent(hb: HeartbeatRequest):
    """Graceful shutdown announcement from agent workers."""
    if hb.id in registry:
        registry[hb.id].status = "standby"
        registry[hb.id].endpoint = None
        logger.info(f"Agent '{hb.id}' graceful shutdown -> status standby.")
    return {"status": "unregistered", "id": hb.id}

# ─── OpenAI-Compatible API (/v1/models & /v1/chat/completions) ───────────────

@app.get("/v1/models")
async def get_models():
    """OpenAI-compatible models catalog for Open WebUI."""
    models_data = []
    
    # 1. Include all agents as first-class models
    for a in registry.values():
        models_data.append({
            "id": a.id,
            "object": "model",
            "created": int(a.registered_at or time.time()),
            "owned_by": "kruemel-ai-agents",
            "permission": [],
            "root": a.id,
            "parent": None,
            "status": a.status,
            "description": a.description or f"Krümel AI {a.name}"
        })
    
    # 2. Optionally merge models from LiteLLM Proxy so Open WebUI has everything
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(
                f"{LITELLM_URL}/v1/models",
                headers={"Authorization": f"Bearer {LITELLM_MASTER_KEY}"}
            )
            if resp.status_code == 200:
                litellm_data = resp.json().get("data", [])
                existing_ids = {m["id"] for m in models_data}
                for lm in litellm_data:
                    if lm["id"] not in existing_ids:
                        models_data.append(lm)
    except Exception as e:
        logger.warning(f"Could not fetch models from LiteLLM: {e}")

    return {"object": "list", "data": models_data}


async def stream_from_worker(worker_url: str, payload: dict) -> AsyncGenerator[bytes, None]:
    """Streams SSE chat completions from a live Python worker in kruemel-ai-agents."""
    async with httpx.AsyncClient(timeout=180.0) as client:
        # Check endpoint style (supports direct /chat/{id} or base URL /v1/chat/completions)
        target_url = worker_url if ("/chat" in worker_url or worker_url.endswith("/completions")) else f"{worker_url}/v1/chat/completions"
        try:
            async with client.stream("POST", target_url, json=payload) as response:
                if response.status_code != 200:
                    err_body = await response.aread()
                    yield f"data: {json.dumps({'choices': [{'delta': {'content': f'Error from worker: {err_body.decode()}'}}]})}\n\n".encode()
                    yield b"data: [DONE]\n\n"
                    return
                async for chunk in response.aiter_bytes():
                    yield chunk
        except Exception as e:
            logger.error(f"Failed to stream from worker {worker_url}: {e}")
            yield f"data: {json.dumps({'choices': [{'delta': {'content': f'Worker communication error: {str(e)}'}}]})}\n\n".encode()
            yield b"data: [DONE]\n\n"


async def stream_from_litellm_fallback(agent: AgentState, payload: dict) -> AsyncGenerator[bytes, None]:
    """Fallback proxy to LiteLLM Proxy when the standalone Python worker is in standby."""
    # Prefix a clear status indicator so the user sees the answer immediately
    standby_notice = {
        "id": f"notice-{int(time.time())}",
        "object": "chat.completion.chunk",
        "created": int(time.time()),
        "model": agent.id,
        "choices": [{
            "index": 0,
            "delta": {
                "content": f"⚡ *[Standby-Modus: Worker '{agent.id}' ist noch nicht gestartet. Antwort via LiteLLM '{agent.model}']*\n\n"
            },
            "finish_reason": None
        }]
    }
    yield f"data: {json.dumps(standby_notice)}\n\n".encode()

    # Route through LiteLLM using the agent's target model
    payload_copy = dict(payload)
    payload_copy["model"] = agent.model
    payload_copy["stream"] = True

    async with httpx.AsyncClient(timeout=180.0) as client:
        try:
            async with client.stream(
                "POST",
                f"{LITELLM_URL}/v1/chat/completions",
                headers={"Authorization": f"Bearer {LITELLM_MASTER_KEY}"},
                json=payload_copy
            ) as response:
                async for chunk in response.aiter_bytes():
                    yield chunk
        except Exception as e:
            logger.error(f"LiteLLM fallback error: {e}")
            err_chunk = {
                "id": f"err-{int(time.time())}",
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": agent.id,
                "choices": [{"index": 0, "delta": {"content": f"\n\nLiteLLM fallback error: {str(e)}"}, "finish_reason": "stop"}]
            }
            yield f"data: {json.dumps(err_chunk)}\n\n".encode()
            yield b"data: [DONE]\n\n"


@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    """
    OpenAI-compatible chat completion dispatcher.
    Directs the call to the active Python agent worker, or falls back to LiteLLM.
    """
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    model_name = body.get("model", "")
    is_stream = bool(body.get("stream", False))

    # 1. If requested model is a registered agent
    if model_name in registry:
        agent = registry[model_name]
        logger.info(f"Dispatching chat request for agent '{agent.id}' (Status: {agent.status}, Stream: {is_stream})")

        # A) Agent is ONLINE with live worker endpoint
        if agent.status == "online" and agent.endpoint:
            if is_stream:
                body_copy = dict(body)
                body_copy["stream"] = True
                return StreamingResponse(
                    stream_from_worker(agent.endpoint, body_copy),
                    media_type="text/event-stream"
                )
            else:
                body_copy = dict(body)
                body_copy["stream"] = False
                async with httpx.AsyncClient(timeout=180.0) as client:
                    target_url = agent.endpoint if ("/chat" in agent.endpoint or agent.endpoint.endswith("/completions")) else f"{agent.endpoint}/v1/chat/completions"
                    resp = await client.post(target_url, json=body_copy)
                    return JSONResponse(status_code=resp.status_code, content=resp.json())

        # B) Agent is in STANDBY -> Graceful LiteLLM Fallback
        else:
            logger.info(f"Agent '{agent.id}' is in standby. Using LiteLLM '{agent.model}' fallback.")
            if is_stream:
                return StreamingResponse(
                    stream_from_litellm_fallback(agent, body),
                    media_type="text/event-stream"
                )
            else:
                body_copy = dict(body)
                body_copy["model"] = agent.model
                body_copy["stream"] = False
                async with httpx.AsyncClient(timeout=180.0) as client:
                    resp = await client.post(
                        f"{LITELLM_URL}/v1/chat/completions",
                        headers={"Authorization": f"Bearer {LITELLM_MASTER_KEY}"},
                        json=body_copy
                    )
                    resp_data = resp.json()
                    notice = f"⚡ *[Standby-Modus: Worker '{agent.id}' ist noch nicht gestartet. Antwort via LiteLLM '{agent.model}']*\n\n"
                    if "choices" in resp_data and len(resp_data["choices"]) > 0:
                        msg = resp_data["choices"][0].get("message", {})
                        if "content" in msg and msg["content"]:
                            msg["content"] = notice + msg["content"]
                    return JSONResponse(status_code=resp.status_code, content=resp_data)

    # 2. If requested model is a standard LiteLLM model (e.g. local-general) -> Proxy to LiteLLM
    if is_stream:
        async def proxy_litellm():
            body_copy = dict(body)
            body_copy["stream"] = True
            async with httpx.AsyncClient(timeout=180.0) as client:
                async with client.stream(
                    "POST",
                    f"{LITELLM_URL}/v1/chat/completions",
                    headers={"Authorization": f"Bearer {LITELLM_MASTER_KEY}"},
                    json=body_copy
                ) as response:
                    async for chunk in response.aiter_bytes():
                        yield chunk

        return StreamingResponse(proxy_litellm(), media_type="text/event-stream")
    else:
        body_copy = dict(body)
        body_copy["stream"] = False
        async with httpx.AsyncClient(timeout=180.0) as client:
            resp = await client.post(
                f"{LITELLM_URL}/v1/chat/completions",
                headers={"Authorization": f"Bearer {LITELLM_MASTER_KEY}"},
                json=body_copy
            )
            return JSONResponse(status_code=resp.status_code, content=resp.json())


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="info")
