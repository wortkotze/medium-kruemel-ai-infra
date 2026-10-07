# Death to the Agent Monolith: Why Every AI Agent Belongs in Its Own Docker Container

**How we decoupled 5 LangGraph agents into sandboxed micro-workers, secured them with least-privilege mounts, and orchestrated live SSE streaming to Open WebUI.**

---

![Isolated Container Mesh](https://raw.githubusercontent.com/wortkotze/medium-kruemel-ai-infra/main/medium/images/05_microworker_docker_mesh.jpg)
*Figure 1: Isolated Container Mesh — 5 autonomous LangGraph micro-workers running in sandboxed Docker containers with least-privilege volume scoping around a central dispatch event router.*

---

## 1. The Dangerous Agent Monolith

Look at almost every multi-agent tutorial or framework demo published today. They all follow the exact same architectural pattern:
* A single Python script or monolithic FastAPI server.
* All five or ten agents imported into the same application process.
* All agents sharing the same file system, memory space, network permissions, and environment variables.

In a tutorial, this looks clean and convenient. In production, this design is an **operational and security catastrophe**:

### Failure Mode 1: Shared Crash Cascades
If your software engineering agent (`agent-coder`) encounters a memory leak or an unhandled exception while parsing an enormous git repository, **the entire Python process crashes**. Your Product Owner agent, your Architect agent, and your DevOps triage agent all go offline simultaneously.

### Failure Mode 2: Privilege Escalation & Security Leaks
If all agents share the same container, they share the same access tokens and volume mounts. 
A research agent browsing the public web could fall victim to an indirect prompt injection that commands it to read the local filesystem. In a monolith, it has access to the `/var/run/docker.sock` socket intended exclusively for the DevOps agent!

### Failure Mode 3: Resource Starvation
One CPU-intensive agent compiling a binary or running unit tests can starve your interactive customer-facing chat agent of CPU cycles and memory.

**Conclusion:** The monolithic agent architecture is dead. Production agents require **the Micro-Worker Pattern**.

---

## 2. The Micro-Worker Pattern & The Least-Privilege Matrix

In Krümel AI, every agent role is decoupled into an **isolated, resource-capped Docker container**. 

Crucially, we do not build five separate, bloated Docker images. We use **one single multi-stage Dockerfile** built with `uv`:

```dockerfile
# Multi-Stage Build with Astral uv
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim AS builder
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

FROM python:3.11-slim-bookworm
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates && rm -rf /var/lib/apt/lists/*
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"
COPY src /app/src
EXPOSE 8001
CMD ["python", "-m", "src.server"]
```

**The Efficiency Miracle:** All five micro-worker containers share the **exact same underlying image layers** (`kruemel-ai-agent:latest`, ~393 MB). The additional disk space consumed by running five containers instead of one is **0 MB**. In idle mode, all five containers combined consume less than **840 MB of RAM**.

### The Principle of Least Privilege Matrix (`compose.agents.yaml`)

Every agent container receives strictly the filesystem mounts and secrets required for its job:

* **`kruemel-agent-po` (`:8001`, Memory: 384 MB):**  
  *Volume Mounts:* `./workspace/docs/specs:/app/docs/specs:rw`  
  *Secrets:* `LITELLM_MASTER_KEY` (no shell or docker access).
* **`kruemel-agent-architect` (`:8001`, Memory: 384 MB):**  
  *Volume Mounts:* `./workspace/docs/architecture:rw`, `./workspace/docs/specs:ro`  
  *Secrets:* `LITELLM_MASTER_KEY` & Memgraph bolt port.
* **`kruemel-agent-coder` (`:8001`, Memory: 768 MB):**  
  *Volume Mounts:* `./workspace:rw`, `./sandbox:rw`  
  *Secrets:* `GITHUB_TOKEN` (isolated from system docker socket).
* **`kruemel-agent-researcher` (`:8001`, Memory: 512 MB):**  
  *Volume Mounts:* `./workspace/docs/research:rw`  
  *Secrets:* `LITELLM_MASTER_KEY` (accesses local SearXNG).
* **`kruemel-agent-devops` (`:8001`, Memory: 384 MB):**  
  *Volume Mounts:* `/var/run/docker.sock:ro` (read-only monitoring)  
  *Secrets:* `CLOUDFLARE_API_TOKEN`.

Even if an attacker manages to compromise `agent-researcher`, the container has zero access to the Docker socket, zero write access to production code, and cannot modify architectural specs.

---

## 3. Dynamic Micro-Worker Mode vs. Local Host Development

How do we support isolated micro-worker containers in production while preserving a rapid local development workflow for engineers on macOS?

Inside [`src/server.py`](https://github.com/wortkotze/medium-kruemel-ai-agents/blob/main/src/server.py), we implement dynamic role filtering based on the `AGENT_ID` environment variable:

```python
SELECTED_AGENT_ID = os.environ.get("AGENT_ID", "all").strip().lower()

if SELECTED_AGENT_ID and SELECTED_AGENT_ID != "all":
    # 🎯 Dedicated Micro-Worker Mode (Docker Container)
    # Only compile and load the single targeted LangGraph agent
    AGENTS_CONFIG = {SELECTED_AGENT_ID: ALL_AGENTS_CONFIG[SELECTED_AGENT_ID]}
    logger.info(f"🎯 Running in Micro-Worker Mode for: {SELECTED_AGENT_ID}")
else:
    # 🌐 Multi-Agent Worker Mode (Local Host Dev)
    # Boot all 5 agents in a single process for rapid testing via `make serve`
    AGENTS_CONFIG = ALL_AGENTS_CONFIG
```

* In **Docker Compose**: each service passes `AGENT_ID=agent-coder`, `CONTAINER_HOST=http://kruemel-agent-coder`.
* On the **Host**: running `make serve` boots all five agents on port 8001 with hot reload.

---

## 4. Automated Service Discovery & Gateway Registration

How does the central platform know where each container is running?

When an agent container boots up, its modern FastAPI **Lifespan Handler** automatically registers the worker with the **Central Agent Gateway (`:1518`)**:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Startup: Self-Registration with Central Gateway
    async with httpx.AsyncClient(timeout=10.0) as client:
        for aid, meta in AGENTS_CONFIG.items():
            payload = {
                "id": aid,
                "name": meta["name"],
                "role": meta["role"],
                "endpoint": f"{CONTAINER_HOST}:{PORT}/chat/{aid}",
                "model": meta["model"]
            }
            await client.post(f"{GATEWAY_URL}/api/registry/register", json=payload)

    # 2. Spawn 20-second keepalive heartbeat task
    hb_task = asyncio.create_task(heartbeat_loop())
    yield
    
    # 3. Shutdown: Graceful deregistration
    hb_task.cancel()
    async with httpx.AsyncClient(timeout=5.0) as client:
        for aid in AGENTS_CONFIG.keys():
            await client.post(f"{GATEWAY_URL}/api/registry/unregister", json={"id": aid})
```

If a container crashes or is taken down for maintenance:
1. Heartbeats cease.
2. The Gateway's watchdog detects the missing ping within 45 seconds and flips the agent's status from `online` to `standby`.
3. Open WebUI immediately knows that the agent is unavailable, preventing hanging user prompts.

---

## 5. Streaming Live Thinking via Server-Sent Events (SSE)

Enterprise users expect modern conversational interfaces. If an agent takes 30 seconds to formulate an answer, displaying a blank screen or a loading spinner causes users to refresh or abandon the page.

Krümel AI converts LangGraph state transitions into standard **OpenAI-compliant Server-Sent Events (`chat.completion.chunk`)**:

```python
async def run_langgraph_stream(agent_id: str, graph, user_text: str):
    # 1. Emit instant initial thinking chunk
    yield format_sse_chunk("🧠 *[Agent analyzing inquiry...]*\n\n")

    # 2. Run LangGraph StateGraph execution
    final_state = await run_in_executor(graph.invoke, {"messages": [HumanMessage(content=user_text)]})

    # 3. Emit formatted tool call reports
    for tool_call in extract_tool_calls(final_state):
        yield format_sse_chunk(f"🔧 *Tool executed:* `{tool_call.name}`\n")
    yield format_sse_chunk("\n---\n\n")

    # 4. Stream final synthesized response token-by-token
    for token in tokenize(final_state.content):
        yield format_sse_chunk(token)
        await asyncio.sleep(0.015) # Smooth natural typing cadence

    # 5. Emit termination signal
    yield b"data: [DONE]\n\n"
```

Inside **Open WebUI (`:1513`)**, users see the agent's real-time reasoning steps, tool invocations, and responses stream smoothly onto the screen token-by-token.

---

## Production Gotchas & Lessons Learned

During the engineering of this containerized architecture, we solved three subtle bugs that every team moving agents to containers will face:

1. **Address Already in Use (`Errno 48`):**  
   * *Problem:* Attempting to expose port 8001 to the host for all 5 containers causes port collision errors.  
   * *Solution:* Never map micro-worker ports to the host! Keep port 8001 internal to the Docker bridge network. The Central Gateway (`:1518`) routes traffic using Docker's internal DNS (`http://kruemel-agent-coder:8001`).
2. **Docker Compose Network Bridge Prefixes:**  
   * *Problem:* Declaring an external network as `networks: litellm-net` fails if Compose prefixed the network name with the project name.  
   * *Solution:* Always explicitly declare the exact external name:  
     `networks: litellm-net: { name: litellm_local_litellm-net, external: true }`.
3. **FastAPI Lifespan Migration:**  
   * *Problem:* `@app.on_event("startup")` and `@app.on_event("shutdown")` are deprecated in modern FastAPI/Starlette versions and can leave background tasks dangling.  
   * *Solution:* Migrate to `@asynccontextmanager async def lifespan(app: FastAPI)` with structured cancellation of background heartbeat tasks.

---

## Key Takeaways

1. **Ditch the Monolith:** Decomposing agents into micro-worker containers isolates failures and prevents cascading outages.
2. **Apply Least Privilege:** Restrict volume mounts and secrets so that a compromised agent cannot pivot across your infrastructure.
3. **Use Shared Layers:** A single multi-stage `uv` Dockerfile allows five containers to run with 0 MB duplicate disk overhead.
4. **Automate Service Discovery:** Have containers register dynamically with a central gateway on boot, backed by health-checking heartbeats.
5. **Stream SSE Chunks:** Emit real-time reasoning and tool reports using standard SSE chunks to deliver a fluid end-user experience.

---

*Deploy your own multi-agent container mesh in minutes:*  
👉 **[GitHub: wortkotze/medium-kruemel-ai-infra](https://github.com/wortkotze/medium-kruemel-ai-infra)**  
👉 **[GitHub: wortkotze/medium-kruemel-ai-agents](https://github.com/wortkotze/medium-kruemel-ai-agents)**

---

```text
> Initiating ArticleProtocol...
> Loading Human Ideas... [100% Complete]
> Loading AI Grammar... [100% Complete]
> Merging... Success.
> Disclaimer: Content architected by a human, compiled by an agent
> Disclaimer: Graphics generated by an agent
```

