# 🚀 Enterprise AI Infrastructure Blueprint

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](compose.yaml)
[![LiteLLM](https://img.shields.io/badge/Gateway-LiteLLM-4A90E2)](https://github.com/BerriAI/litellm)
[![Langfuse](https://img.shields.io/badge/Observability-Langfuse-black)](https://langfuse.com)
[![Qdrant](https://img.shields.io/badge/Vector%20DB-Qdrant-red)](https://qdrant.tech)
[![Memgraph](https://img.shields.io/badge/Graph%20DB-Memgraph-00A98F)](https://memgraph.com)

A modular, production-ready **Enterprise AI Infrastructure Platform** featuring:
- **Central Model Gateway & Routing** ([LiteLLM Proxy](https://github.com/BerriAI/litellm) with virtual keys & spend quotas)
- **Full-Stack Observability** (Self-hosted [Langfuse](https://langfuse.com) with PostgreSQL, ClickHouse & MinIO)
- **Dual-Layer Memory** ([Qdrant](https://qdrant.tech) Vector Store & [Memgraph](https://memgraph.com) Knowledge Graph)
- **Air-Gapped Tool Execution** (SearXNG private search, Browserless headless Chromium & Code Sandbox)
- **User Interface Suite** ([Open WebUI](https://github.com/open-webui/open-webui) & Krümel Hub Dashboard)
- **Agent Micro-Worker Mesh** (Isolated, resource-capped Docker containers running [LangGraph](https://github.com/langchain-ai/langgraph) agents)

---

## 🏛️ System Architecture

```mermaid
graph TD
    subgraph UI & Ingestion
        OWUI["Open WebUI (:1513)"]
        HUB["Krümel Hub Portal (:1512)"]
    end

    subgraph Platform Gateway Layer
        GW["Agent Gateway (:1518)<br/>Dynamic Service Registry"]
        LLM["LiteLLM Proxy (:4000)<br/>Model Router & Virtual Keys"]
    end

    subgraph Agent Micro-Workers [Docker Bridge]
        PO["agent-po (:8001)<br/>Product Owner"]
        ARCH["agent-architect (:8001)<br/>System Architect"]
        DEV["agent-coder (:8001)<br/>Software Engineer"]
        RES["agent-researcher (:8001)<br/>Deep Researcher"]
        OPS["agent-devops (:8001)<br/>DevOps & Infra"]
    end

    subgraph Memory & Observability
        QDRANT["Qdrant Vector DB (:6333)"]
        MEM["Memgraph Knowledge Graph (:7687)"]
        LANGFUSE["Langfuse Tracing (:3000)<br/>Postgres + ClickHouse"]
    end

    subgraph Air-Gapped Tooling
        SEARX["SearXNG Search (:1514)"]
        BROWSER["Browserless Headless (:1516)"]
        SANDBOX["Code Sandbox (:1517)"]
    end

    OWUI -->|OpenAI SSE Chat| GW
    HUB -->|Registry API| GW
    GW -->|Dispatches /chat/{id}| PO & ARCH & DEV & RES & OPS

    PO & ARCH & DEV & RES & OPS -->|LLM Inference & FinOps Caps| LLM
    LLM -->|Hierarchical Tracing| LANGFUSE

    PO & ARCH & OPS -.->|Graph Queries| MEM
    PO & DEV & RES -.->|Semantic Memory| QDRANT
    RES -.-> SEARX & BROWSER
    DEV -.-> SANDBOX
```

---

## ⚡ Quickstart

### Prerequisites
- Docker Engine or Podman with Compose support (`docker compose` or `podman-compose`)
- `make` and `curl`

### 1. Clone & Configure
```bash
git clone https://github.com/wortkotze/medium-kruemel-ai-infra.git
git clone https://github.com/wortkotze/medium-kruemel-ai-agents.git
cd medium-kruemel-ai-infra

# Copy configuration template
cp .env.example .env
```

### 2. Launch the Core Infrastructure
```bash
make start
```
This starts the databases (PostgreSQL, Redis, Qdrant, Memgraph, ClickHouse), LiteLLM Gateway, Langfuse, SearXNG, Browserless, and Open WebUI.

### 3. Launch the 5 Agent Micro-Workers
```bash
make agents-build
make agents-up
```
All 5 agents will boot in isolated containers, register dynamically with the Agent Gateway (`:1518`), and become available in Open WebUI immediately.

---

## 🌐 Endpoints & Ports

| Service | Internal / Host Port | Purpose |
| :--- | :---: | :--- |
| **Krümel Hub** | `http://localhost:1512` | Central Operations HUD & Agent Status Matrix |
| **Open WebUI** | `http://localhost:1513` | Chat suite with real-time SSE token streaming |
| **Agent Gateway** | `http://localhost:1518` | Dynamic agent registration & dispatch router |
| **LiteLLM Proxy** | `http://localhost:4000` | Unified model gateway, rate limiter & virtual key manager |
| **Langfuse UI** | `http://localhost:3000` | Tracing, latency tracking & prompt evaluation |
| **Qdrant Vector DB** | `http://localhost:6333` | Dense vector memory & semantic similarity search |
| **Memgraph Bolt / Lab** | `:7687` / `:1515` | In-memory graph engine & Cypher query web interface |
| **SearXNG Search** | `http://localhost:1514` | Privacy-preserving meta-search API |
| **Browserless** | `http://localhost:1516` | Headless Chromium automation |
| **Code Sandbox** | `http://localhost:1517` | Transient non-root script execution engine |

---

## 🔒 Security & Zero-Secret Architecture

1. **Zero Real Keys in Git:** This repository contains **no hardcoded credentials**. All secrets are configured via `.env` and loaded at runtime.
2. **Virtual Keys:** Every agent is isolated to its own LiteLLM virtual key with spend limits.
3. **Least-Privilege Mounts:** Each agent micro-worker container only receives read/write access to the specific volumes required for its role (e.g. only DevOps receives read-only Docker socket access).

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
