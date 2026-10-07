# No More Black Boxes: Full-Stack Observability & Evals for Autonomous Agents with Langfuse

**Why traditional application logs fail miserably for multi-agent loops, and how we audit every tool call, latency bottleneck, and token spend in ClickHouse and Langfuse.**

---

![Langfuse Observability Traces](https://raw.githubusercontent.com/wortkotze/medium-kruemel-ai-infra/main/medium/images/03_langfuse_observability_traces.jpg)
*Figure 1: Full-Stack Observability Console — Hierarchical trace trees tracking latency, token usage, tool spans, and ClickHouse analytical data streams.*

---

## 1. The Nightmare of `print()` Debugging in Autonomous Agents

In standard microservice architectures, debugging is straightforward. A request hits an endpoint, calls a database, returns a response, and writes a structured JSON log. If something breaks, you grep for `error: true` in Datadog or Grafana.

In an autonomous multi-agent mesh, traditional logging collapses completely.

Consider what happens when a user asks:
> *"Audit the repository, identify missing acceptance criteria, update our architecture diagram, and submit a PR."*

Over the next 60 seconds, a LangGraph state machine:
1. Spawns an intent classifier.
2. Invokes `agent-architect` to query a Memgraph knowledge graph.
3. Calls `agent-researcher` to query SearXNG.
4. Triggers `agent-coder` to read files, run a linter in an isolated sandbox, hit a syntax error, and retry twice.
5. Emits a completion.

If this workflow fails at step 4 or takes 52 seconds to respond, a terminal log or text file is utterly useless:
* Which tool call consumed 80% of the latency?
* Which sub-agent hallucinated the incorrect argument?
* How many tokens were spent on retrying failed linter runs?
* Did the system prompt trigger an unintended prompt injection?

Autonomous agents are **non-deterministic state graphs**. They require **hierarchical, distributed tracing**.

---

## 2. The Solution: Hierarchical Trace Trees

Instead of flat text lines, observability platforms like **Langfuse** organize agent runs into **Trace Trees**:

```
[Trace: User Audit Request] (Latency: 28.4s, Total Tokens: 18,420, Cost: $0.024)
  ├── [Span: Product Owner Decomposition] (Latency: 1.2s)
  │     └── [Generation: local-general] (Prompt: 412 tokens, Completion: 85 tokens)
  ├── [Span: Graph Topology Inspection] (Latency: 0.8s)
  │     └── [Tool: query_knowledge_graph] (Cypher: MATCH (s:Service)...)
  └── [Span: Code Refactor Cycle] (Latency: 26.4s)
        ├── [Generation: local-coder] (Prompt: 4,120 tokens, Completion: 620 tokens)
        ├── [Tool: run_sandbox_linter] (Exit Code: 1, Output: "SyntaxError at line 42")
        └── [Generation: local-coder (Retry 1)] (Prompt: 4,800 tokens, Completion: 590 tokens)
```

Within two seconds, an engineer can click directly into the failed span, inspect the exact prompt state that caused the linter failure, review token consumption, and identify latency bottlenecks.

---

## 3. The Production Docker Architecture

Rather than paying steep per-seat SaaS subscription fees, Krümel AI hosts the complete **Langfuse Observability Stack** locally within our Docker Compose network:

```yaml
# In compose.yaml:
services:
  langfuse-clickhouse:
    image: clickhouse/clickhouse-server:24.3-alpine
    container_name: langfuse-clickhouse
    networks: [litellm-net]
    volumes: [clickhouse_data:/var/lib/clickhouse]

  langfuse-minio:
    image: minio/minio:RELEASE.2024-05-10T01-41-38Z
    container_name: langfuse-minio
    networks: [litellm-net]
    command: server /data --console-address ":9001"

  langfuse-web:
    image: ghcr.io/langfuse/langfuse:2
    container_name: langfuse-web
    depends_on: [db, langfuse-clickhouse, langfuse-minio]
    networks: [litellm-net]
    ports: ["3000:3000"]
    environment:
      - DATABASE_URL=postgresql://litellm:${POSTGRES_PASSWORD}@litellm-db:5432/langfuse
      - CLICKHOUSE_URL=http://langfuse-clickhouse:8123
```

### Why ClickHouse is Non-Negotiable
Language model traces generate massive amounts of high-entropy textual data. Storing millions of execution spans in traditional relational databases like PostgreSQL causes index bloat and slow dashboard queries.

By decoupling transactional user metadata (PostgreSQL) from the high-throughput span ingestion engine (**ClickHouse**), the platform can ingest thousands of agent tool spans per minute with zero UI degradation.

---

## 4. Hooking Observability into LiteLLM & LangGraph

Connecting your agents to Langfuse requires zero boilerplate inside individual tool functions.

### Step 1: Proxy-Level Callbacks
Inside LiteLLM ([`config/config.yaml`](https://github.com/wortkotze/medium-kruemel-ai-infra/blob/main/config/config.yaml)):
```yaml
litellm_settings:
  callbacks: ["langfuse"]
```
Every model request routed through LiteLLM automatically ships generation tokens, model parameters, and latency metrics to Langfuse.

### Step 2: Agent Graph State Tracing
Inside `kruemel-ai-agents` ([`src/core/llm.py`](https://github.com/wortkotze/medium-kruemel-ai-agents/blob/main/src/core/llm.py)):
```python
from langfuse.callback import CallbackHandler
from src.core.config import settings

def get_langfuse_callback() -> CallbackHandler:
    return CallbackHandler(
        public_key=settings.LANGFUSE_PUBLIC_KEY,
        secret_key=settings.LANGFUSE_SECRET_KEY,
        host=settings.LANGFUSE_HOST # http://langfuse-web:3000
    )
```
When compiling the LangGraph workflow:
```python
callbacks = [get_langfuse_callback()]
final_state = graph.invoke(inputs, config={"callbacks": callbacks})
```

---

## 5. Automated Evals & LLM-as-a-Judge

Observability is incomplete without **quality evaluation**. Knowing that an agent ran in 1.4 seconds is useless if the generated code contains security vulnerabilities.

Krümel AI implements a two-tier evaluation strategy:

### 1. Human Feedback Signals (Open WebUI)
When engineers interact with agents in Open WebUI (`:1513`), clicking 👍 or 👎 transmits an immediate feedback score directly to the associated Langfuse trace ID.

### 2. Automated LLM-as-a-Judge
For background autonomous agents (e.g., `agent-po`), an asynchronous evaluation job invokes a small, fast evaluator model (`llama3.1:8b`) to score the output:
* *„Did the PRD include Gherkin acceptance criteria?“* (Score: 1.0 / 0.0)
* *„Did the refactored code introduce unhandled exceptions?“* (Score: 0.0 - 1.0)

These scores appear directly inside the Langfuse dashboard, allowing platform teams to detect prompt regressions before code is merged into production.

---

## Key Takeaways

1. **Abandon `print()` and Flat Logs:** Multi-agent state graphs require hierarchical trace trees to isolate tool bottlenecks and hallucination triggers.
2. **Leverage Columnar Storage:** High-volume agent trace ingestion demands ClickHouse to keep dashboards fast and responsive.
3. **Capture Cost and Latency at the Gateway:** Use proxy-level callbacks to maintain 100% financial and operational auditability across all providers.
4. **Implement Continuous Evals:** Combine human feedback with automated LLM-as-a-Judge scoring to catch performance drift early.

---

*Launch your self-hosted Langfuse observability platform today:*  
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

