# 🚀 Krümel AI Infra (Podman / Docker)

Modulare, produktionsbereite **KI-Infrastruktur-Plattform** mit **LiteLLM Gateway**, **Langfuse Observability** (Self-Hosted), **Dual-Memory** (Qdrant Vektor-Store & Memgraph Knowledge Graph), **Agent Tool Execution** (SearXNG Suche, Browserless Chromium & Code-Sandbox), **Krümel AI Chat** (Open WebUI), **n8n Workflow Automation**, automatisierter **Snapshot-Sicherung**, zentralem **Web-Hub** und deklarativer Trennung von **Modellen**, **MCP-Servern (Model Context Protocol)** und **A2A-Agenten**.

> 💡 **Zwei-Schichten-Architektur:**
> - **Infrastruktur & Plattform (dieses Repo):** [kruemel-ai-infra](https://github.com/wortkotze/kruemel-ai-infra) (Daemon-Container, Datenbanken, APIs, Tooling, Backups).
> - **Anwendungen & Agenten:** [kruemel-ai-agents](https://github.com/wortkotze/kruemel-ai-agents) (LangGraph, Python-Agenten, LangGraph Studio auf macOS).

---

## 🏗️ Verzeichnisstruktur

```text
kruemel-ai-infra/
├── compose.yaml             # Podman / Docker Compose Stack (15 Services: LiteLLM, Memgraph, Open WebUI, SearXNG, etc.)
├── .env.example             # Template für alle API-Keys & Secrets
├── Makefile                 # Make-Targets für Schnellzugriff (start, stop, hub, backup, test)
├── manage.sh                # Management- & Lifecycle-Script
├── hub/                     # ⚡ Krümel Hub Operations- & Monitoring-Portal (:1512)
│   ├── server.py            # Uptime-Engine, PostgreSQL-Health-Polling & JSON-API
│   ├── index.html           # Service-Übersicht & Matrix-HUD
│   ├── docs.html            # Interaktives Architektur-Handbuch & Dual-Memory Guide
│   ├── status.html          # StatusCake-Style Uptime-Monitore & Incident-Historie
│   ├── chat.html            # Eingebettetes Krümel AI Chat Portal
│   └── app.js               # Frontend-Controller (Zweisprachig DE/EN & Theme-Manager)
├── sandbox/                 # ⚡ Isolierte Code Execution Sandbox (:1517)
│   └── server.py            # Non-Root HTTP Runner für flüchtige Python- & Shell-Ausführung
├── searxng/                 # 🔍 Lokale Meta-Suchmaschine (:1514)
│   └── settings.yml         # SearXNG-Konfiguration (JSON-API aktiviert, werbefrei)
├── docs/
│   └── AGENT_GUIDE.md       # 🤖 Entwickler-Handbuch für n8n, LangGraph & Python-Agenten
├── workspace/               # Isoliertes Sandbox-Verzeichnis für Filesystem-MCP
├── backups/                 # Automatisierte Datenbank- & Config-Snapshots (in .gitignore)
├── config/
│   ├── config.yaml          # Aktive Runtime-Konfiguration (Callbacks, Admin UI, DB, Cache)
│   ├── models.yaml          # Lokale Ollama-Modelle + OpenRouter Cloud + Smart Failover
│   ├── mcp_servers.yaml     # Standard MCP-Server (SearXNG, Browserless, Sandbox, GitHub, FRITZ!Box, etc.)
│   ├── agents.yaml          # A2A-Agenten (vollständig auf lokale Ollama-Modelle gebunden)
│   └── skills.yaml          # Skill-Definitionen für LiteLLM
└── scripts/
    ├── mcp/                 # 🔌 12 FastMCP Server (Suche, Memory, Browser, Sandbox, Graph, Docker, etc.)
    │   └── vendor/          # Standalone Python-Treiber (z. B. neo4j Bolt client)
    ├── init/                # 🗄️ SQL-Init Skripte für PostgreSQL (Langfuse, Hub)
    └── ops/                 # ⚙️ Operations-, Build- & Synchronisations-Skripte
        ├── build_config.sh  # Baut aktive Runtime-Config aus modularen YAMLs
        ├── export_agent_env.sh # Synchronisiert infra_contract.json & ../kruemel-ai-agents/.env
        ├── setup_agent_keys.py # Richtet Virtual Keys mit Modell- & Tool-RBAC ein
        └── run.sh           # Validierungs- & Startskript
```

---

## 🏛️ Architektur & Services (16 Services)

Der Stack läuft in einem gemeinsamen Netzwerk (`litellm-net`) mit automatischer DNS-Auflösung und strengen RAM-Limits:

| Service | Container-Name | Port (Host) | RAM-Limit | Zweck |
|:---|:---|:---|:---|:---|
| **LiteLLM Gateway** | `litellm-proxy` | `4000:4000` | `1536M` | Zentrales KI-Gateway, Model-Router, RBAC & MCP-Host |
| **Krümel Hub** | `kruemel-hub` | `1512:1512` | `256M` | Operations-Dashboard, Agenten-Cockpit, Uptime & Doku |
| **Krümel AI Chat** | `litellm-open-webui` | `1513:8080` | `1024M` | Authentifizierter Human-to-AI Chat Workspace (Open WebUI) |
| **Agent Gateway & Registry** | `litellm-agent-gateway` | `1518:1518` | `256M` | Dynamische Agent-Registry & OpenAI Chat Dispatcher für Open WebUI |
| **SearXNG Meta-Search** | `litellm-searxng` | `1514:8080` | `512M` | Lokale, werbefreie Meta-Suche & JSON-API für Agenten |
| **Langfuse Web UI** | `langfuse-web` | `3000:3000` | `768M` | Tracing-Dashboard, Prompt Management & Evaluationen |
| **Langfuse Worker** | `langfuse-worker` | *intern* | `512M` | Asynchroner Event-Ingestion- & Queue-Worker |
| **Memgraph Graph DB** | `litellm-memgraph` | `7687:7687` | `512M` | In-Memory Graphdatenbank für Wissensgraphen & GraphRAG |
| **Memgraph Lab** | `litellm-memgraph-lab` | `1515:3000` | `256M` | Interaktives Visualisierungs-Studio für Cypher & Topologien |
| **Browserless Chromium** | `litellm-browserless` | `1516:3000` | `1024M` | Headless Web-Browsing, SPA-Rendering & Screenshots für Agenten |
| **Code Sandbox** | `litellm-sandbox` | `127.0.0.1:1517` | `512M` | Isolierte, flüchtige Python- & Shell-Ausführungsumgebung (Non-Root) |
| **Qdrant Vector DB** | `litellm-qdrant` | `6333:6333` | `512M` | Vektorspeicher & RAG für semantisches Agenten-Gedächtnis |
| **n8n Automation** | `litellm-n8n` | `5678:5678` | `768M` | Visuelle Workflow- und Node-Pipelines für Trigger & Alerts |
| **ClickHouse** | `langfuse-clickhouse` | `127.0.0.1:8123` | `1024M` | Hochperformante Spaltendatenbank für Traces & Analytics |
| **MinIO S3** | `langfuse-minio` | `9090` (Console: `9091`) | `384M` | S3-kompatibler Objektspeicher für große Payload-Daten |
| **PostgreSQL 16** | `litellm-db` | `127.0.0.1:5432` | `512M` | Relationale DB für LiteLLM, Langfuse, n8n und Hub-Uptime-Logs |
| **Redis 7** | `litellm-redis` | `127.0.0.1:6379` | `384M` | Cache für LiteLLM (`litellm.cache:*`) und Queue-Broker |

> [!NOTE]
> **Host-RAM-Optimierung:** Durch strikte Deckelung benötigt der gesamte Stack im Leerlauf **nur ~3,5–4 GB RAM**. Auf einem 32 GB Mac stehen damit über **24 GB RAM ungestört für lokale LLM-Inferenz** in Ollama bereit.

---

## ⚡ Zentrale Sprungseite (Krümel Hub & Portale)

Öffne das Dashboard mit einem Befehl:
```bash
make hub
# oder direkt im Browser: http://localhost:1512
```

### Die Web-Portale im Überblick:
* 📊 **Krümel Hub (Operations & Uptime)**: `http://localhost:1512`
* 💬 **Krümel AI Chat (Open WebUI)**: `http://localhost:1513`
* 🔍 **Krümel Search (SearXNG)**: `http://localhost:1514`
* 🛡️ **LiteLLM Admin UI**: `http://localhost:4000/ui`
* 📈 **Langfuse Observability**: `http://localhost:3000`
* 🕸️ **Memgraph Lab Studio**: `http://localhost:1515`
* 🌐 **Browserless Console**: `http://localhost:1516`
* 🗄️ **Qdrant Vector Console**: `http://localhost:6333/dashboard`
* ⚡ **n8n Workflow Automation**: `http://localhost:5678`
* 📦 **MinIO S3 Console**: `http://localhost:9091`

---

## 🧠 Dual-Memory: Qdrant Vektor-Store vs. Memgraph Knowledge Graph

Der Krümel AI Stack kombiniert zwei komplementäre Speicherformen für fortschrittliches **GraphRAG**:

1. **Qdrant (Vektor-Store, Port 6333):**
   * *Stärke:* Unstrukturierte semantische Ähnlichkeitssuche ("Finde relevante Textabschnitte").
   * *Use-Cases:* Dokument-Uploads im Chat, Code-Chunk-Suche, FAQ-Matching.
2. **Memgraph (Knowledge Graph, Port 7687 / 1515):**
   * *Stärke:* Strukturiertes Multi-Hop Reasoning ("Wie hängen Service A, Agent B und Tool C zusammen?").
   * *Use-Cases:* Infrastruktur-Topologie, Abhängigkeits-Mapping, Entitäts-Beziehungen.

---

## 🛠️ Agent Tool Execution: Suche, Browser & Sandbox

Autonome Agenten verfügen über eine vollständige, lokale Toolchain:

```
[Agent (Ollama / n8n / Python)]
       │
       ├─► 1. Web-Recherche ────────► [SearXNG :1514] (Meta-Search JSON)
       │                                   │ liefert Link- & Snippet-Liste
       ├─► 2. Deep-Content ─────────► [Browserless :1516] (DOM / Screenshot)
       │                                   │ extrahiert bereinigten Text
       ├─► 3. Wissens-Kontext ──────► [Qdrant / Memgraph]
       │
       └─► 4. Code ausführen ───────► [Code Sandbox :1517] (Non-Root UID 1000)
```

---

## 🔌 Standard MCP-Server (`config/mcp_servers.yaml`)

Die folgenden Server sind deklarativ mit granularen Guardrails und RBAC eingebunden:

1. **FRITZ!Box FastMCP (`fritzbox_mcp`)**: Multi-threaded TR-064 Integration (HTTPS/Port 49443) zur Abfrage aller aktiven Netzwerkgeräte, WAN-IP-Status, Bandbreiten, Gast-WLAN und Smart Home DECT-Geräten.
2. **Cloudflare MCP (`cloudflare_mcp`)**: DNS-Verwaltung, Zero Trust Policies & Tunnels. *(Destruktive Aktionen gesperrt)*.
3. **GitHub Read MCP (`github_read_mcp`) & DevOps MCP (`github_devops_mcp`)**: Repositories, PRs, Issues, Code-Suche und Commit-Historie.
4. **SearXNG Meta-Search MCP (`searxng_mcp`)**: Lokale, werbefreie Web-, News- und Wissenschafts-Suche via FastMCP (ohne API-Keys).
5. **Browserless Headless Chromium MCP (`browserless_mcp`)**: Web-Browsing, JavaScript/SPA-Rendering, Text-Scraping und PNG-Screenshots.
6. **Isolated Code Execution Sandbox MCP (`sandbox_mcp`)**: Sichere, flüchtige Python- und Shell-Ausführung im isolierten Non-Root Container.
7. **Brave Search MCP (`brave_search_mcp`) & Google Serper MCP (`google_search_mcp`)**: Kommerzielle Web-Recherche als Fallback.
8. **Google Workspace & Drive MCP (`google_workspace_mcp`)**: Lesen und Durchsuchen von Docs, Sheets und Drive-Dateien.
9. **Sandboxed Filesystem MCP (`filesystem_mcp`)**: Sichere Dateioperationen isoliert innerhalb des `./workspace`-Ordners.

---

## 🤖 A2A Agenten (`config/agents.yaml`)

Alle Agenten sind an lokale Modelle gebunden und werden über LiteLLM geroutet:

| Agent | Lokales Modell | MCP-Bindings | Fokus |
|---|---|---|---|
| `agent-devops` | `local-general` (`llama-3.3-70b` / `llama3.1:8b`) | `cloudflare_mcp`, `github_mcp`, `fritzbox_mcp` | DNS, Tunneling, FRITZ!Box Heimnetz, CI/CD & Zero Trust |
| `agent-researcher` | `local-general` (`llama-3.3-70b` / `llama3.1:8b`) | `searxng_mcp`, `browserless_mcp`, `brave_search_mcp`, `github_mcp` | Autonome Web-Recherche, Dokumentenanalyse, Synthese |
| `agent-coder` | `local-coder` (`qwen2.5-coder:32b` / `qwen2.5-coder:7b`) | `sandbox_mcp`, `filesystem_mcp`, `github_mcp` | Software-Architektur, Testausführung, Refactoring, Code-Audits |

---

## 🚀 Schnellstart

```bash
# 1. Repository klonen & vorbereiten
git clone <REPO_URL> && cd kruemel-ai-infra

# 2. Umgebungsvariablen anlegen
cp .env.example .env
# → Trage deine Secrets in .env ein

# 3. Konfigurationen validieren
make validate        # oder: ./manage.sh validate

# 4. Stack starten
make start           # oder: docker compose up -d

# 5. Health-Check & Test-Request ausführen
make test            # oder: ./manage.sh test

# 6. Kontrollzentrum öffnen
make hub             # öffnet http://localhost:1512
```

---

## 📦 Backup & Desaster Recovery

Mit einem Befehl werden konsistente Snapshots aller relationalen Datenbanken, Konfigurationen und Secrets erstellt:

```bash
make backup
# oder: ./manage.sh backup
```

* Erstellt ein komprimiertes Archiv unter `backups/backup_YYYYMMDD_HHMMSS.tar.gz`.
* Enthält SQL-Dumps von `litellm`, `langfuse` und `hub`, alle YAML-Configs, Skripte und die `.env`.
* **Automatischer Schutz:** Vor jedem automatischen oder manuellen Image-Update (`make update`) wird automatisch ein Snapshot gezogen.
* **Rotation:** Es werden stets die 7 neuesten Snapshots aufbewahrt, ältere werden automatisch bereinigt.

---

## 🤝 Multi-Repo Workflow: `kruemel-ai-infra` ⟷ `kruemel-ai-agents`

Um Inkonsistenzen zwischen Infrastruktur (Ports `:1512`–`:1517`, Virtual Keys, MCP-Server) und dem Agenten-Code (`kruemel-ai-agents`) zu vermeiden, existiert ein automatisierter Vertrag:

### 1. Synchronisation mit einem Befehl:
```bash
make sync-agents
# oder: ./scripts/ops/export_agent_env.sh
```
Dieser Befehl:
* Liest die aktiven Virtual Keys (`kruemel-agent-po`, `kruemel-agent-architect`, etc.) aus der LiteLLM-Datenbank aus.
* Generiert den maschinenlesbaren Systemvertrag [config/infra_contract.json](file:///Users/stephanstrecker/GitHub/kruemel-ai-infra/config/infra_contract.json).
* Exportiert alle relevanten API-Keys, Model-Namen und Service-URLs direkt in `../kruemel-ai-agents/.env`.

### 2. Central Agent Gateway (:1518) & Multi-Agent Cockpit (:1512/agents):
* **Live Cockpit:** Im Krümel Hub unter `http://localhost:1512/agents` werden alle 5 Rollen, deren Status (🟢 Online / 🟡 Standby), Inferenz-Modelle und erlaubte FastMCP-Tools live visualisiert.
* **Dynamische Registrierung:** Wenn ein Worker in `kruemel-ai-agents` gestartet wird, registriert er sich via `POST http://localhost:1518/api/registry/register` am Gateway. Das Gateway leitet Chat-Prompts aus Open WebUI (`:1513`) transparent an den aktiven Worker weiter.
* **Heartbeat:** Worker senden alle 20s `POST http://localhost:1518/api/registry/heartbeat`. Fehlt der Heartbeat länger als 45s, schaltet das Gateway den Agenten automatisch in den Standby-Modus zurück.

### 3. Best Practices für Agenten-Entwicklung:
* **Keine Ports im Agenten-Code hardcoden:** Agenten sprechen ausschließlich mit LiteLLM (`http://localhost:4000/v1`) über ihren jeweiligen API-Key. LiteLLM reicht MCP-Tools (`remember_knowledge`, `search_web`, `query_graph`, `execute_python`) automatisch durch.
* **IDE Multi-Root Workspace:** Öffne beide Repositories gleichzeitig in Antigravity IDE (**File -> Add Folder to Workspace... -> `kruemel-ai-agents`**), damit der KI-Assistent die Schnittstellen beider Repositories jederzeit synchron im Blick hat.

---

## 🛠️ Verfügbare Befehle

| Befehl | Beschreibung |
|:---|:---|
| `make start` | Startet den kompletten Stack (LiteLLM, Memgraph, Open WebUI, SearXNG, DBs, Caches) |
| `make stop` | Stoppt alle Container |
| `make restart` | Startet alle Container neu |
| `make hub` | Öffnet die zentrale Web UI & Agent Hub Sprungseite im Browser (`:1512`) |
| `make backup` | Erstellt einen vollständigen Snapshot aller Datenbanken, Konfigurationen und Secrets |
| `make update` | Sichert den Stack, zieht neueste Images, erzeugt Container neu & synchronisiert Skills |
| `make sync-agents` | Synchronisiert Infrastruktur-Vertrag & Virtual Keys direkt nach `../kruemel-ai-agents/.env` |
| `make install-autoupdate` | Richtet automatische tägliche Updates um 04:00 Uhr ein (macOS launchd) |
| `make uninstall-autoupdate` | Entfernt den automatischen Update-Zeitplan |
| `make logs` | Zeigt Live-Logs der Container an |
| `make status` | Zeigt den aktuellen Container-Status aller Stack-Dienste an |
| `make validate` | Prüft die YAML-Syntax aller Dateien in `config/` |
| `make sync-skills` | Synchronisiert `config/skills.yaml` in die LiteLLM-Datenbank |
| `make refresh-ollama` | Erkennt lokale Ollama-Modelle neu und aktualisiert `config/models.yaml` |
| `make test` | Führt Health-Checks und Test-Completions aus |
| `make help` | Zeigt die Hilfeübersicht an |
