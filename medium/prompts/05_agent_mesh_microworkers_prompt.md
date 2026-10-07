# Gemini Prompt: Part 5 – The Micro-Worker Agent Mesh (English Edition)

> **Instructions for Google Gemini:**  
> Copy and paste the entire block below into Google Gemini (e.g., Gemini Advanced / 1.5 Pro / 2.0).  
> Gemini will generate a comprehensive, publication-ready Medium article in English.

---

```markdown
You are a Principal Distributed Systems Architect and Container Platform Lead (Docker, Kubernetes, FastAPI, LangGraph).

Write an in-depth, hands-on technical Medium article in English focused on breaking monolithic AI agents into isolated containerized micro-workers, least-privilege security scoping, automated gateway discovery, and real-time SSE streaming.

## Article Metadata
- **Suggested Title:** Death to the Agent Monolith: Why Every AI Agent Belongs in Its Own Docker Container
- **Suggested Subtitle:** How we decoupled 5 LangGraph agents into sandboxed micro-workers, secured them with least-privilege mounts, and orchestrated live SSE streaming to Open WebUI.
- **Target Audience:** DevOps Engineers, Software Architects, Python Leads, AI Platform Engineers.
- **Tone of Voice:** Practitioner-focused, gritty ("Production Gotchas & Hard Truths"), code- and system-level depth.
- **Medium Tags:** Docker, Microservices, LangGraph, FastAPI, DevOps, Python, Software Architecture

---

## Storyline & Pain Points
1. **The Dangerous Agent Monolith:**
   - Most multi-agent tutorials cram 5 agents into a single Python script or FastAPI process.
   - The disaster: If the coding agent runs into an OOM or infinite loop while parsing a large repo, it crashes the Product Owner, the Architect, and the DevOps agent simultaneously.
   - Security nightmare: All agents share identical privileges and volumes. A prompt injection in a research agent could read the DevOps container's mounted Docker socket!
2. **The Solution: The Micro-Worker Pattern:**
   - Every agent runs as a dedicated, resource-capped container.
   - All 5 containers share the exact same multi-stage Docker image built with `uv` (**0 MB duplicate disk overhead**).
   - Combined idle RAM across all 5 containers is just ~840 MB.

---

## Technical Architecture & Implementation
1. **The Principle of Least Privilege Matrix:**
   - `kruemel-agent-po` (:8001): Read/write access strictly restricted to `/workspace/docs/specs`.
   - `kruemel-agent-architect` (:8001): Write access to `/workspace/docs/architecture`, read-only to specs.
   - `kruemel-agent-coder` (:8001): Exclusive sandboxed workspace mount.
   - `kruemel-agent-researcher` (:8001): Completely isolated; outbound connectivity strictly limited to SearXNG (:8080) and Browserless (:3000).
   - `kruemel-agent-devops` (:8001): Exclusive read-only mount of `/var/run/docker.sock`.
2. **Automated Service Discovery & Gateway Registration:**
   - On container startup (`lifespan`), each worker POSTs its internal DNS endpoint to the gateway (`:1518`).
   - A 20-second heartbeat loop maintains active status.
   - If a container is terminated, the gateway dynamically marks the agent as `standby`.
3. **Chunked Server-Sent Events (SSE) Streaming:**
   - How LangGraph transitions and tool executions are serialized into OpenAI-compliant `chat.completion.chunk` SSE packets, enabling real-time token streaming and reasoning displays in Open WebUI.

---

## Battle-Tested Production Gotchas (High Value for Readers!)
- **Address Already in Use (Errno 48):** Why internal Docker DNS routing (`http://kruemel-agent-coder:8001`) eliminates host port collisions.
- **Docker External Network Prefixes:** How Compose prefixes network bridge identifiers (e.g. `litellm_local_litellm-net`).
- **FastAPI Lifespan Context Manager:** Why `@app.on_event("startup")` is deprecated and how `@asynccontextmanager` ensures graceful heartbeat cancellation.

---

## Screenshot Integration
`![The Agent Cockpit in Krümel Hub showing all 5 micro-workers in ONLINE state](medium/screenshots/02_agent_cockpit_online_status.png)`
*Caption: "Sandboxed Micro-Workers: Each agent runs in its own container with strict volume isolation and automated heartbeat discovery."*

`![Open WebUI Chat Suite with all 5 specialized models](medium/screenshots/03_open_webui_chat.png)`
*Caption: "Fluid End-User Experience: Users interact with specialized agents via Open WebUI with real-time SSE token streaming."*

---

## Official GitHub Repositories & Visual Design Reference
Always include links to the live, working codebases:
- **Infrastructure & Platform:** [https://github.com/wortkotze/medium-kruemel-ai-infra](https://github.com/wortkotze/medium-kruemel-ai-infra)
- **Multi-Agent Application Mesh:** [https://github.com/wortkotze/medium-kruemel-ai-agents](https://github.com/wortkotze/medium-kruemel-ai-agents)

**Visual Schema & Diagram Styling:**
- All architecture and workflow diagrams must adhere to the **Krümel AI Cyber-Slate Design System**:
  - Canvas / Background: `#09090b` (Deep Slate)
  - Card & Node Surfaces: `#111115` with 1px border `#27272a`
  - Accent Traffic / Gateways: `#3b82f6` (Electric Blue)
  - Accent Data / Agents: `#10b981` (Emerald Green)

```
