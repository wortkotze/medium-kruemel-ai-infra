/**
 * Krümel AI Hub – Core Frontend Controller
 * Multilingual (DE/EN), Dark/Light Theme Manager & Matrix ASCII Animation
 */

const I18N = {
  de: {
    // Navigation & Common
    nav_overview: "Übersicht",
    nav_chat: "💬 Chat",
    nav_status: "Status & Uptime",
    nav_docs: "Architektur & Doku",
    btn_theme_dark: "🌙 Dunkel",
    btn_theme_light: "☀️ Hell",
    btn_check_now: "Jetzt prüfen",
    btn_fullscreen_chat: "↗ Vollbild",
    chat_connecting: "Verbinde mit Krümel AI Chat (:1513)...",
    chat_connecting_sub: "LiteLLM Proxy & Ollama Backend bereit",
    pill_checking: "Prüfe Infrastruktur...",
    pill_all_healthy: "Alle Systeme aktiv",
    pill_degraded: "Eingeschränkt",
    pill_down: "Ausfall erkannt",
    last_updated: "Zuletzt geprüft",
    view_details: "Details & Ausfälle 📊",
    open_portal: "Öffnen ↗",
    open_chat: "Chat öffnen ↗",
    open_admin_ui: "Admin-UI öffnen ↗",
    open_dashboard: "Dashboard öffnen ↗",
    open_canvas: "Canvas öffnen ↗",
    open_console: "Konsole öffnen ↗",
    open_endpoint: "API Endpunkt ansehen ↗",
    open_docs_guide: "Architektur ansehen ↗",
    backend_service: "Hintergrunddienst (Port aktiv)",
    before_7d: "vor 7 Tagen",
    today: "Heute",
    uptime_7d: "7-Tage Uptime",
    avg_latency: "Latenz",
    footer_health_api: "Health Endpoint (JSON ↗)",
    footer_platform: "Krümel AI Platform &bull; Port 1512",

    // Homepage Matrix Hero
    hud_tag: "KRÜMEL_INFRA // RUNTIME_V2.6",
    matrix_title: "SYSTEM-INFRASTRUKTUR & ORCHESTRIERUNG",
    matrix_subtitle: "Zentrales Steuerungsportal für lokale KI-Infrastruktur, Observability, verteilte Agenten & High-Speed Inferenz.",
    spec_daemons: "DAEMONS",
    spec_daemons_val: "14 SERVICES IM STACK",
    spec_inference: "INFERENZ",
    spec_inference_val: "APPLE SILICON GPU",
    spec_storage: "PERSISTENZ",
    spec_storage_val: "POSTGRESQL 16",
    spec_gateway: "GATEWAY",
    spec_gateway_val: "LITELLM :4000",
    hero_btn_explore: "Systeme erkunden ↓",
    hero_btn_status: "Live Status Monitor →",
    hero_btn_docs: "Architektur & Handbuch →",
    scroll_explore: "SYSTEME ENTDECKEN",

    // Overview Cards
    section_apps: "Kernkomponenten & Portale",
    section_quickstart: "Entwickler-Schnellstart",
    card_litellm_title: "LiteLLM Gateway",
    card_litellm_sub: "AI Governance & Router",
    card_litellm_desc: "Zentrales KI-Gateway für alle Modelle. Übernimmt RBAC-Zugriffskontrolle, virtuelle API-Keys, PII-Datenmaskierung, Spend-Tracking und A2A-Agentenprofile.",
    meta_proto_lbl: "Protokoll:",
    meta_proto_val: "OpenAI-kompatibel /v1",
    meta_routing_lbl: "Routing:",
    meta_routing_val: "Lokal (Ollama) & Cloud-Fallback",

    card_langfuse_title: "Langfuse Observability",
    card_langfuse_sub: "Tracing & Evaluierung",
    card_langfuse_desc: "LLM-Application Tracing in Echtzeit. Visualisiert komplexe Agent-Ketten, Einzelschritte, Latenzen, Token-Kosten und Prompt-Versionen.",
    meta_analytics_lbl: "Analytik:",
    meta_analytics_val: "ClickHouse OLAP Backend",
    meta_storage_lbl: "Storage:",
    meta_storage_val: "MinIO S3 Event Store",

    card_n8n_title: "n8n Automation Engine",
    card_n8n_sub: "Low-Code Workflow AI",
    card_n8n_desc: "Leistungsstarke visuelle Workflow-Automation. Erstellt autonome Multi-Step-Agenten, Event-Trigger, Webhooks und Tool-Orchestrierungen.",
    meta_workflows_lbl: "Engine:",
    meta_workflows_val: "Node-based Canvas",
    meta_triggers_lbl: "Trigger:",
    meta_triggers_val: "Webhooks, Cron & APIs",

    card_qdrant_title: "Qdrant Vector DB",
    card_qdrant_sub: "Semantisches Gedächtnis",
    card_qdrant_desc: "In Rust geschriebene Hochleistungs-Vektordatenbank mit HNSW-Indexierung für semantische Ähnlichkeitssuche und Langzeit-RAG-Memory.",
    meta_engine_lbl: "Core:",
    meta_engine_val: "Rust HNSW Engine",
    meta_index_lbl: "Schnittstelle:",
    meta_index_val: "REST & gRPC Ports",

    card_memgraph_title: "Memgraph Knowledge Graph",
    card_memgraph_sub: "Strukturiertes Wissen & Relationen",
    card_memgraph_desc: "Ultra-schnelle C++ In-Memory Graphdatenbank mit Cypher/Bolt & Memgraph Lab Studio. Ermöglicht Multi-Hop Reasoning, GraphRAG und Beziehungsanalysen.",
    meta_protocol_lbl: "Protokoll:",
    meta_protocol_val: "Bolt (:7687) & Cypher",
    meta_studio_lbl: "Studio:",
    meta_studio_val: "Memgraph Lab Visualizer",
    open_graph_lab: "Graph Studio öffnen ↗",

    card_browserless_title: "Browserless Chromium",
    card_browserless_sub: "Headless Web Browsing & Scraping",
    card_browserless_desc: "Vollwertiger Headless-Chromium-Browser für Agenten via REST & Playwright CDP. Ermöglicht Web-Navigation, Scraping dynamischer SPAs und Screenshots.",
    meta_browser_proto_lbl: "Protokoll:",
    meta_browser_proto_val: "REST & Playwright CDP",
    meta_browser_caps_lbl: "Features:",
    meta_browser_caps_val: "DOM, Screenshots & PDF",
    open_browser_lab: "Browser Konsole öffnen ↗",

    card_sandbox_title: "Code Execution Sandbox",
    card_sandbox_sub: "Isolierte Tool-Ausführung",
    card_sandbox_desc: "Sichere, kurzlebige Python- und Bash-Sandbox für LLM-Agenten. Führt Code unter unprivilegiertem User (UID 1000) mit Memory- und Timeout-Limits aus.",
    meta_sandbox_runtime_lbl: "Laufzeit:",
    meta_sandbox_runtime_val: "Python 3.11 & Alpine Shell",
    meta_sandbox_isolation_lbl: "Isolation:",
    meta_sandbox_isolation_val: "Non-Root (Limits: 512MB)",
    open_sandbox_health: "Health API ansehen ↗",

    card_searxng_title: "SearXNG Meta-Search",
    card_searxng_sub: "Lokale Web-Suche & Research API",
    card_searxng_desc: "Datenschutzfreundliche Meta-Suchmaschine. Aggregiert Google, Bing, DuckDuckGo & ArXiv ohne Tracking. Stellt Agenten eine unlimitierte JSON-Such-API bereit.",
    meta_searxng_mode_lbl: "Quellen:",
    meta_searxng_mode_val: "Google, Bing, DDG, ArXiv",
    meta_searxng_api_lbl: "Output:",
    meta_searxng_api_val: "JSON API & Web UI",
    open_searxng_ui: "Suche öffnen ↗",

    card_ollama_title: "Ollama Local Engine",
    card_ollama_sub: "Lokale Hardware-Inferenz",
    card_ollama_desc: "Führt Open-Source Sprachmodelle wie Qwen 2.5 Coder oder Llama 3.1 direkt auf der Apple Silicon GPU aus – vollkommen offline ohne Datenabfluss.",
    meta_hardware_lbl: "Hardware:",
    meta_hardware_val: "Metal Neural Engine",
    meta_models_lbl: "Modelle:",
    meta_models_val: "Qwen 2.5, Llama 3.1, Nomic",

    card_agents_title: "Krümel Agents (Python)",
    card_agents_sub: "Autonome StateGraphs",
    card_agents_desc: "Eigene Python-Agenten unter 'kruemel-ai-agents', verwaltet mit modernem 'uv'-Paketmanager. StateGraph-Pipelines mit Tool Calling.",
    meta_env_lbl: "Umgebung:",
    meta_env_val: "uv Venv & Python 3.11",
    meta_state_lbl: "Framework:",
    meta_state_val: "LangGraph Multi-Agent",

    card_webui_title: "Krümel AI Chat",
    card_webui_sub: "Human-to-AI Workspace",
    card_webui_desc: "Vollwertiges Chat-Interface im ChatGPT/Gemini-Stil (Open WebUI). Unterstützt fliegenden Modellwechsel, RAG-Dateiuploads, Prompt-Vorlagen und Live-Streaming via LiteLLM.",
    meta_ui_lbl: "Oberfläche:",
    meta_ui_val: "Open WebUI (:1513)",
    meta_rag_lbl: "Features:",
    meta_rag_val: "RAG, Dateiupload & Presets",

    // Quickstart
    quickstart_desc: "Befehle zur Steuerung, Überprüfung und Nutzung der lokalen Infrastruktur:",
    tab_python: "Python (OpenAI SDK)",
    tab_langchain: "LangChain / LangGraph",
    tab_curl: "cURL Request",

    // Dynamic Service Roles & Status Page
    svc_litellm_role: "AI Governance, Router & Model-Katalog",
    svc_langfuse_role: "Prompt-Tracing, Evaluierung & Metriken",
    svc_n8n_role: "Low-Code Agenten & Workflow-Pipelines",
    svc_qdrant_role: "Vektorspeicher, RAG & Agent Memory",
    svc_memgraph_role: "In-Memory Graph & Multi-Hop Reasoning",
    "svc_memgraph-lab_role": "Interaktives Graph-Studio & Visualizer",
    svc_browserless_role: "Headless Browser Automation & Web Scraping für Agenten",
    svc_sandbox_role: "Isolierte Python & Shell Tool-Ausführungsumgebung",
    svc_searxng_role: "Lokale, werbefreie Meta-Suchmaschine für Agenten",
    svc_ollama_role: "Lokale LLMs & Embeddings (Host)",
    svc_postgres_role: "Relationales Backend für LiteLLM, Langfuse & n8n",
    svc_redis_role: "Prompt-Cache & Job-Queue",
    svc_clickhouse_role: "OLAP Spaltendatenbank für Telemetrie",
    svc_minio_role: "S3-kompatibler Objektspeicher",
    "svc_open-webui_role": "Mensch-zu-Modell Chat-Workspace & RAG",
    badge_loading: "Lade...",
    uptime_word: "Uptime",
    status_online: "ONLINE",
    status_offline: "OFFLINE",
    status_degraded: "EINGESCHRÄNKT",

    // Status Page
    status_page_title: "Infrastruktur Status & Uptime",
    status_page_subtitle: "Echtzeit-Health-Checks und 7-Tage Verfügbarkeitshistorie aller Container, gestützt durch PostgreSQL.",
    section_monitors_title: "Service-Monitore (PostgreSQL Historie)",
    btn_raw_json: "📄 Raw JSON",
    loading_status: "Lade...",
    loading_history: "Lade Monitore und PostgreSQL-Historie...",
    modal_title: "Service Details",
    modal_kpi_uptime: "Uptime (7 Tage)",
    modal_kpi_latency: "Durchschnitts-Latenz",
    modal_kpi_status: "Aktueller Status",
    modal_incidents_title: "Incident- & Störungshistorie",
    modal_no_incidents: "Keine Ausfälle in den letzten 7 Tagen verzeichnet.",
    modal_th_time: "Zeitpunkt",
    modal_th_status: "Status",
    modal_th_latency: "Latenz",
    modal_th_details: "Details",
    modal_conn_error: "Verbindungsfehler",

    // Docs Page
    docs_page_title: "Systemarchitektur & Komponenten-Handbuch",
    docs_page_subtitle: "Detaillierte technische Dokumentation der Rollen, Aufgaben und Interaktionen aller Dienste im Krümel AI Stack.",
    docs_architecture_title: "Gesamtarchitektur & Datenflüsse",
    docs_architecture_desc: "Der Krümel AI Stack trennt strikt zwischen <strong>Infrastruktur & Governance (kruemel-ai-infra)</strong> und <strong>Agenten-Orchestrierung (kruemel-ai-agents / n8n)</strong>. Alle Aufrufe laufen über ein zentrales Sicherheits-Gateway (LiteLLM) und werden transparent durch Langfuse auditiert.",
    tier1_title: "01 Orchestrierung & Agenten-Schicht",
    tier1_meta: "Client & Execution Layer",
    tier1_node1_role: "LangGraph StateGraph Maschinen",
    tier1_node1_desc: "Autonome Multi-Agenten mit strukturiertem State, Tool Calling, Human-in-the-Loop & Langfuse Instrumentierung.",
    tier1_node2_role: "Visuelle Low-Code Automation",
    tier1_node2_desc: "Visuelle Event-Pipelines, Webhook Trigger, automatisierte Datenflüsse und nahtlose Anbindung an Qdrant & LiteLLM.",
    tier1_node3_role: "Human-to-AI Chat Workspace",
    tier1_node3_desc: "Direkte menschliche Interaktion mit lokalen & Cloud-Modellen. Dateiupload, RAG, Prompt-Vorlagen & fliegender Modellwechsel.",

    tier1b_title: "01b Agent Tool-Execution & Sandbox-Schicht",
    tier1b_meta: "Tool Calling & Runtime Environment",
    tier1b_node0_role: "Lokale Web-Suchmaschine",
    tier1b_node0_desc: "Aggregiert Google, Bing, DuckDuckGo & ArXiv ohne Tracking. Stellt Agenten eine unlimitierte JSON-Such-API bereit.",
    tier1b_node1_role: "Headless Browser Automation",
    tier1b_node1_desc: "Vollwertiges Chromium für autonome Web-Recherchen, Screenshot-Erfassung und dynamisches Scraping komplexer Web-Apps.",
    tier1b_node2_role: "Isolierte Code-Ausführung",
    tier1b_node2_desc: "Sichere Sandbox-Ausführung von Python- und Shell-Code für Agenten ohne Zugriff auf das Host-Dateisystem.",

    connector1_text: "⬇ OpenAI REST Protokoll (/v1/chat/completions) &bull; Port :4000",
    tier2_title: "02 Governance, Security & Model Routing",
    tier2_meta: "Zentraler Kontrollpunkt",
    tier2_gw_role: "Zentrale Kontrollinstanz für alle ein- und ausgehenden LLM-Anfragen",
    tier2_col1_title: "🔑 RBAC & Virtuelle Keys",
    tier2_col1_desc: "Keine echten API-Keys im Code; dedizierte virtuelle Tokens für jeden Agenten (z. B. <code>key-agent-devops</code>).",
    tier2_col2_title: "🔒 PII-Maskierung & Safety",
    tier2_col2_desc: "Automatisches Redigieren von Passwörtern, E-Mails und sensiblen Kundendaten vor der Modell-Inferenz.",
    tier2_col3_title: "💰 Token- & Spend-Budgets",
    tier2_col3_desc: "Echtzeit-Tracking und Budget-Limits pro Agent, Modell und Team zur strikten Kostenkontrolle.",
    tier2_col4_title: "🔀 Intelligentes Routing",
    tier2_col4_desc: "Local-First (Ollama auf Apple Silicon) mit automatischem Fallback auf Cloud-Modelle (OpenRouter).",
    connector2_text: "⬇ Audited Inference &bull; Distributed Traces &bull; Vector Memory Pipelines",
    tier3_title: "03 Inferenz, Observability & Semantisches Gedächtnis",
    tier3_meta: "Core Execution & Telemetry",
    tier3_node1_role: "Prompt-Tracing & Metriken",
    tier3_node1_desc: "End-to-End Tracing aller Agentenschritte, Prompt-Versionierung, Latenzmessung und Kostenanalyse.",
    tier3_node2_role: "Apple Silicon GPU Inferenz",
    tier3_node2_desc: "On-Premise Inferenz auf dem Mac Host (Metal GPU). Qwen 2.5 Coder, Llama 3.1 & Nomic Embeddings mit 0% Datenabfluss.",
    tier3_node3_role: "Vektorspeicher & RAG",
    tier3_node3_desc: "In Rust geschriebene Hochleistungs-Vektordatenbank mit HNSW-Index für semantische Suche und Agent-Gedächtnis.",
    tier3_node4_role: "In-Memory Graph & Relationen",
    tier3_node4_desc: "C++ In-Memory Graphdatenbank mit Cypher/Bolt. Speichert Entitäten, Relationen und Topologien für Multi-Hop GraphRAG.",
    connector3_text: "⬇ Interne Docker-Netzwerke (litellm-net) &bull; Persistente Volumes",
    tier4_title: "04 Infrastruktur & Enterprise-Persistenz",
    tier4_meta: "State, Queues & Analytics",
    tier4_node1_role: "Relationale Datenbank",
    tier4_node1_desc: "Zentraler Speicher für LiteLLM Keys, Langfuse Metadaten, n8n Workflows und Hub-Uptime-Logs.",
    tier4_node2_role: "In-Memory Cache & Broker",
    tier4_node2_desc: "Zero-Latency Exact Match Prompt-Caching für LiteLLM und Task-Queues für Hintergrund-Worker.",
    tier4_node3_role: "Columnar Telemetry DB",
    tier4_node3_desc: "High-Speed Aggregationen über Millionen von Observation- und Telemetrie-Events in Langfuse.",
    tier4_node4_role: "S3 Objektspeicher",
    tier4_node4_desc: "Sichert Trace-Payloads, Ausführungs-Screenshots, PDFs und Mediendateien lokal im Container-Netzwerk.",

    // Component Catalog Cards
    docs_components_title: "Detaillierte Komponenten-Übersicht",
    docs_components_subtitle: "Jede Komponente erfüllt eine dedizierte Aufgabe im Gesamtstack und ist über isolierte Docker-Netzwerke abgesichert:",
    comp_webui_role: "Human-to-AI Chat Interface & RAG Workspace",
    comp_webui_desc: "Stellt eine moderne Benutzeroberfläche nach Art von ChatGPT und Gemini bereit. Ermöglicht interaktive Chats, Prompt-Verwaltung, RAG-Dateiuploads und fliegenden Modellwechsel – 100 % auditiert via LiteLLM & Langfuse.",
    comp_litellm_role: "Governance, Security & Model-Router",
    comp_litellm_desc: "Bietet eine einheitliche Schnittstelle nach OpenAI-Standard. Verhindert direkte API-Key-Herausgabe an Agenten durch virtuelle Tokens, schützt vor Datenlecks (PII Redaction) und routet Anfragen automatisch auf lokale oder Cloud-Modelle.",
    comp_langfuse_role: "Application Tracing & Metriken",
    comp_langfuse_desc: "Open-Source LLM-Engineering Plattform. Zeichnet jeden Prompt, jeden Tool-Call und jede Latenz auf. Ermöglicht systematische Evaluierungen, Kostenanalysen und Fehlerdiagnosen über komplexe Multi-Agenten-Graphen.",
    comp_n8n_role: "Low-Code Workflow & Agent Canvas",
    comp_n8n_desc: "Ermöglicht das visuelle Verknüpfen von Hunderten von Diensten mit KI-Modellen. Nutzt den n8n AI Agent Node zur Anbindung an LiteLLM und Qdrant. Automatisierte Trigger, Webhooks und periodische Aufgaben.",
    comp_qdrant_role: "Semantisches Gedächtnis & RAG",
    comp_qdrant_desc: "In Rust geschriebene Hochleistungs-Vektordatenbank. Speichert Dokument-Embeddings und Agent-Erinnerungen. Bietet extrem schnelle Ähnlichkeitssuche mittels HNSW-Algorithmus mit Payload-Filtering.",
    comp_memgraph_role: "In-Memory Graph & Multi-Hop Reasoning",
    comp_memgraph_desc: "Ultra-schnelle C++ Graphdatenbank mit nativer Cypher/Bolt-Unterstützung und Memgraph Lab Visualizer. Ermöglicht GraphRAG, Beziehungsanalysen und Entitäts-Gedächtnis für autonome Agenten.",
    comp_browserless_role: "Headless Browser Automation & Web Scraping",
    comp_browserless_desc: "Headless Chromium-Browser mit WebSocket CDP- und REST-API. Ermöglicht Agenten das eigenständige Surfen im Web, Interaktion mit dynamischen Webseiten, PDF-Generierung und Screenshot-Analysen.",
    comp_sandbox_role: "Isolierte Code Execution Sandbox",
    comp_sandbox_desc: "Kurzlebige und abgesicherte Python 3.11 / Shell-Laufzeitumgebung. Agenten können dynamischen Code generieren und ausführen lassen, geschützt durch strikte Timeouts, Memory-Limits und Non-Root Isolation.",
    comp_searxng_role: "Lokale, privacy-fokussierte Meta-Suchmaschine",
    comp_searxng_desc: "Aggregiert Suchergebnisse aus Google, Bing, DuckDuckGo, Wikipedia und ArXiv ohne Tracking oder Werbeanzeigen. Stellt eine hochperformante JSON-API für autonome Research-Agenten bereit.",
    comp_ollama_role: "Native Apple Silicon Inferenz",
    comp_ollama_desc: "Läuft direkt auf dem Mac-Host und nutzt die Unified Memory Architektur (GPU/Neural Engine). Stellt Open-Source Modelle wie Qwen 2.5 Coder und Llama 3.1 mit maximaler Lese-/Schreibgeschwindigkeit bereit.",
    comp_postgres_role: "Zentrale relationale Persistenz",
    comp_postgres_desc: "Das Rückgrat für Konfigurationen, User-Accounts, n8n-Workflows und Hub-Statusdaten. Wird konsistent über automatisierte Backups (<code>make backup</code>) als komprimierter SQL-Dump gesichert.",
    comp_redis_role: "In-Memory Cache & Message Broker",
    comp_redis_desc: "Reduziert LLM-Kosten und Latenzen durch Caching identischer Anfragen auf Proxy-Ebene. Dient gleichzeitig als Job-Queue für Hintergrund-Worker und asynchrone Berechnungen.",
    comp_clickhouse_role: "Spaltenorientierte Telemetrie-Analytik",
    comp_clickhouse_desc: "Spezialisiert auf schnelle SQL-Abfragen über Millionen von Telemetrie- und Observation-Events in Langfuse. Bietet unvergleichliche Aggregations-Performance bei minimalem Speicherbedarf.",
    comp_minio_role: "S3-kompatibler Objektspeicher",
    comp_minio_desc: "Sichert große Payloads, Medien-Dateien, Ausführungs-Screenshots und Event-Batches aus Langfuse vollkommen lokal und isoliert im Container-Netzwerk.",

    // Agent Tooling & Execution Docs Section
    docs_agent_tools_title: "🛠️ Agent Tooling & Execution: Web Browsing & Sichere Code-Sandbox",
    docs_agent_tools_intro: "Moderne autonome Agenten benötigen die Fähigkeit, über reine Textgenerierung hinauszugehen: Sie müssen im Web recherchieren und generierten Programmcode sicher testen können.",

    // Dual Memory Section
    docs_dual_memory_title: "🧠 Dual-Memory Architektur: Vektor-Store (Qdrant) vs. Knowledge Graph (Memgraph)",
    docs_dual_memory_intro: "Autonome Agenten und RAG-Pipelines benötigen zwei fundamentale, komplementäre Speicherformen. Bei Krümel AI kombinieren wir semantische Vektorsuche mit strukturiertem Beziehungs-Reasoning zu einem hybriden GraphRAG-System.",
    th_dimension: "Dimension",
    th_qdrant: "🗄️ Qdrant (Vektor-Store)",
    th_memgraph: "🕸️ Memgraph (Knowledge Graph)",
    td_paradigm: "Paradigma",
    td_qdrant_paradigm: "Dichte Vektor-Einbettungen (Embeddings)",
    td_memgraph_paradigm: "Labeled Property Graph (Knoten, Kanten, Properties)",
    td_strength: "Kernstärke",
    td_qdrant_strength: "Unstrukturierte Ähnlichkeitssuche (\"Finde relevante Textabschnitte\")",
    td_memgraph_strength: "Multi-Hop Reasoning (\"Wie hängen A, B und C zusammen?\")",
    td_query: "Abfragesprache",
    td_qdrant_query: "Kosinus-Ähnlichkeit, Dot-Product, HNSW REST/gRPC",
    td_memgraph_query: "Cypher Query Language (OpenCypher via Bolt :7687)",
    td_usecases: "Typische Use-Cases",
    td_qdrant_usecases: "Semantischer Dokument-Upload im Chat, Code-Chunk-Suche, FAQ-Matching",
    td_memgraph_usecases: "Infrastruktur-Topologie, Abhängigkeiten, Agenten-Ontologien, Fakten-Tripel",
    td_hybrid: "Hybrid GraphRAG",
    td_hybrid_desc: "Der Goldstandard: Qdrant findet die relevanten Einstiegsknoten via semantischer Ähnlichkeit. Memgraph folgt den Kanten 1–2 Hops tief, um den vollständigen strukturierten Beziehungskontext ohne Halluzinationen ans LLM zu übergeben.",
    docs_cypher_example_title: "Cypher Abfragebeispiel in Python (LangGraph & kruemel-ai-agents):",

    docs_backup_title: "🛡️ Backup, Wiederherstellung & Desaster Recovery",
    docs_backup_desc: "Alle Systeme sind auf 100 % Reproduzierbarkeit ausgelegt. Docker-Volumes, Konfigurationen und Datenbanken lassen sich jederzeit mit einem Befehl sichern:",
    backup_code_snippet: `# Vollständiges Snapshot-Backup aller PostgreSQL-Datenbanken & Konfigurationen:
make backup

# Snapshot-Archive werden unter backups/backup_YYYYMMDD_HHMMSS.tar.gz abgelegt.
# Es werden stets die 7 neuesten Snapshots aufbewahrt (automatische Rotation).`
  },
  en: {
    // Navigation & Common
    nav_overview: "Overview",
    nav_chat: "💬 Chat",
    nav_status: "Status & Uptime",
    nav_docs: "Architecture & Docs",
    btn_theme_dark: "🌙 Dark",
    btn_theme_light: "☀️ Light",
    btn_check_now: "Check Now",
    btn_fullscreen_chat: "↗ Fullscreen",
    chat_connecting: "Connecting to Krümel AI Chat (:1513)...",
    chat_connecting_sub: "LiteLLM Proxy & Ollama Backend ready",
    pill_checking: "Checking health...",
    pill_all_healthy: "All Systems Operational",
    pill_degraded: "Degraded Performance",
    pill_down: "Outage Detected",
    last_updated: "Last checked",
    view_details: "Details & Incidents 📊",
    open_portal: "Launch UI ↗",
    open_chat: "Launch Chat ↗",
    open_admin_ui: "Open Admin UI ↗",
    open_dashboard: "Open Dashboard ↗",
    open_canvas: "Open Canvas ↗",
    open_console: "Open Console ↗",
    open_endpoint: "View API Endpoint ↗",
    open_docs_guide: "View Architecture ↗",
    backend_service: "Backend Service (Port active)",
    before_7d: "7 days ago",
    today: "Today",
    uptime_7d: "7d Uptime",
    avg_latency: "Latency",
    footer_health_api: "Health Endpoint (JSON ↗)",
    footer_platform: "Krümel AI Platform &bull; Port 1512",

    // Homepage Matrix Hero
    hud_tag: "KRÜMEL_INFRA // RUNTIME_V2.6",
    matrix_title: "SYSTEM INFRASTRUCTURE & ORCHESTRATION",
    matrix_subtitle: "Central operations hub for local AI infrastructure, observability, distributed agent orchestration & high-speed inference.",
    spec_daemons: "DAEMONS",
    spec_daemons_val: "14 STACK SERVICES",
    spec_inference: "INFERENCE",
    spec_inference_val: "APPLE SILICON GPU",
    spec_storage: "PERSISTENCE",
    spec_storage_val: "POSTGRESQL 16",
    spec_gateway: "GATEWAY",
    spec_gateway_val: "LITELLM :4000",
    hero_btn_explore: "Explore Systems ↓",
    hero_btn_status: "Live Status Monitor →",
    hero_btn_docs: "Architecture & Docs →",
    scroll_explore: "EXPLORE SYSTEMS",

    // Overview Cards
    section_apps: "Core Components & Portals",
    section_quickstart: "Developer Quickstart",
    card_litellm_title: "LiteLLM Gateway",
    card_litellm_sub: "AI Governance & Router",
    card_litellm_desc: "Central AI Gateway for all language models. Handles RBAC access control, virtual API keys, PII redaction, spend budgets, and A2A agent profiles.",
    meta_proto_lbl: "Protocol:",
    meta_proto_val: "OpenAI-compatible /v1",
    meta_routing_lbl: "Routing:",
    meta_routing_val: "Local (Ollama) & Cloud Fallback",

    card_langfuse_title: "Langfuse Observability",
    card_langfuse_sub: "Tracing & Evaluation",
    card_langfuse_desc: "Realtime LLM application tracing. Visualizes complex multi-agent graphs, step-by-step executions, latencies, token costs, and prompt versions.",
    meta_analytics_lbl: "Analytics:",
    meta_analytics_val: "ClickHouse OLAP Backend",
    meta_storage_lbl: "Storage:",
    meta_storage_val: "MinIO S3 Event Store",

    card_n8n_title: "n8n Automation Engine",
    card_n8n_sub: "Low-Code Workflow AI",
    card_n8n_desc: "Visual workflow automation engine. Builds autonomous multi-step agents, scheduled triggers, webhooks, and tool orchestrations.",
    meta_workflows_lbl: "Engine:",
    meta_workflows_val: "Node-based Canvas",
    meta_triggers_lbl: "Triggers:",
    meta_triggers_val: "Webhooks, Cron & APIs",

    card_qdrant_title: "Qdrant Vector DB",
    card_qdrant_sub: "Semantic Memory & RAG",
    card_qdrant_desc: "High-performance vector database written in Rust. Features HNSW indexing for ultrafast semantic similarity search and long-term agent memory.",
    meta_engine_lbl: "Core:",
    meta_engine_val: "Rust HNSW Engine",
    meta_index_lbl: "Interface:",
    meta_index_val: "REST & gRPC Ports",

    card_memgraph_title: "Memgraph Knowledge Graph",
    card_memgraph_sub: "Structured Knowledge & Relations",
    card_memgraph_desc: "Ultrafast in-memory C++ graph database featuring native Cypher/Bolt support & Memgraph Lab Studio. Powers Multi-Hop Reasoning, GraphRAG, and relation discovery.",
    meta_protocol_lbl: "Protocol:",
    meta_protocol_val: "Bolt (:7687) & Cypher",
    meta_studio_lbl: "Studio:",
    meta_studio_val: "Memgraph Lab Visualizer",
    open_graph_lab: "Open Graph Studio ↗",

    card_browserless_title: "Browserless Chromium",
    card_browserless_sub: "Headless Web Browsing & Scraping",
    card_browserless_desc: "Full headless Chromium browser for agents via REST & Playwright CDP. Enables autonomous web browsing, dynamic SPA scraping, and screenshots.",
    meta_browser_proto_lbl: "Protocol:",
    meta_browser_proto_val: "REST & Playwright CDP",
    meta_browser_caps_lbl: "Features:",
    meta_browser_caps_val: "DOM, Screenshots & PDF",
    open_browser_lab: "Open Browser Console ↗",

    card_sandbox_title: "Code Execution Sandbox",
    card_sandbox_sub: "Isolated Tool Execution",
    card_sandbox_desc: "Secure, ephemeral Python and Bash sandbox for LLM agents. Runs code under an unprivileged user (UID 1000) with memory and timeout limits.",
    meta_sandbox_runtime_lbl: "Runtime:",
    meta_sandbox_runtime_val: "Python 3.11 & Alpine Shell",
    meta_sandbox_isolation_lbl: "Isolation:",
    meta_sandbox_isolation_val: "Non-Root (Limits: 512MB)",
    open_sandbox_health: "View Health API ↗",

    card_searxng_title: "SearXNG Meta-Search",
    card_searxng_sub: "Local Web Search & Research API",
    card_searxng_desc: "Privacy-focused meta-search engine. Aggregates Google, Bing, DuckDuckGo & ArXiv without tracking. Supplies agents with an unlimited JSON search API.",
    meta_searxng_mode_lbl: "Engines:",
    meta_searxng_mode_val: "Google, Bing, DDG, ArXiv",
    meta_searxng_api_lbl: "Output:",
    meta_searxng_api_val: "JSON API & Web UI",
    open_searxng_ui: "Open Search ↗",

    card_ollama_title: "Ollama Local Engine",
    card_ollama_sub: "Local Hardware Inference",
    card_ollama_desc: "Runs open-source models like Qwen 2.5 Coder or Llama 3.1 directly on Apple Silicon unified memory – 100% offline without cloud data exposure.",
    meta_hardware_lbl: "Hardware:",
    meta_hardware_val: "Metal Neural Engine",
    meta_models_lbl: "Models:",
    meta_models_val: "Qwen 2.5, Llama 3.1, Nomic",

    card_agents_title: "Krümel Agents (Python)",
    card_agents_sub: "Autonomous StateGraphs",
    card_agents_desc: "Custom Python agents in 'kruemel-ai-agents', managed via modern 'uv' package tooling. StateGraph architectures with tool calling.",
    meta_env_lbl: "Environment:",
    meta_env_val: "uv Venv & Python 3.11",
    meta_state_lbl: "Framework:",
    meta_state_val: "LangGraph Multi-Agent",

    card_webui_title: "Krümel AI Chat",
    card_webui_sub: "Human-to-AI Workspace",
    card_webui_desc: "Full-featured ChatGPT/Gemini-style chat workspace (Open WebUI). Supports live model switching, document RAG uploads, prompt templates, and streaming via LiteLLM.",
    meta_ui_lbl: "Interface:",
    meta_ui_val: "Open WebUI (:1513)",
    meta_rag_lbl: "Features:",
    meta_rag_val: "RAG, File Uploads & Presets",

    // Quickstart
    quickstart_desc: "Core CLI commands for controlling, verifying, and developing against local infrastructure:",
    tab_python: "Python (OpenAI SDK)",
    tab_langchain: "LangChain / LangGraph",
    tab_curl: "cURL Request",

    // Dynamic Service Roles & Status Page
    svc_litellm_role: "AI Governance, Router & Model Catalog",
    svc_langfuse_role: "Prompt Tracing, Evaluation & Metrics",
    svc_n8n_role: "Low-Code Agents & Workflow Pipelines",
    svc_qdrant_role: "Vector Memory, RAG & Agent Memory",
    svc_memgraph_role: "In-Memory Graph & Multi-Hop Reasoning",
    "svc_memgraph-lab_role": "Interactive Graph Studio & Visualizer",
    svc_browserless_role: "Headless Browser Automation & Web Scraping for Agents",
    svc_sandbox_role: "Isolated Python & Shell Tool Execution Environment",
    svc_searxng_role: "Local, Ad-Free Meta-Search Engine for Agents",
    svc_ollama_role: "Local LLMs & Embeddings (Host)",
    svc_postgres_role: "Relational Backend for LiteLLM, Langfuse & n8n",
    svc_redis_role: "Prompt Cache & Job Queue",
    svc_clickhouse_role: "OLAP Columnar Database for Telemetry",
    svc_minio_role: "S3-Compatible Object Storage",
    "svc_open-webui_role": "Human-to-Model Chat Workspace & RAG",
    badge_loading: "Loading...",
    uptime_word: "Uptime",
    status_online: "ONLINE",
    status_offline: "OFFLINE",
    status_degraded: "DEGRADED",

    // Status Page
    status_page_title: "Infrastructure Status & Uptime",
    status_page_subtitle: "Realtime health checks and 7-day availability history across all containers, backed by PostgreSQL.",
    section_monitors_title: "Service Monitors (PostgreSQL History)",
    btn_raw_json: "📄 Raw JSON",
    loading_status: "Loading...",
    loading_history: "Loading monitors and PostgreSQL history...",
    modal_title: "Service Details",
    modal_kpi_uptime: "Uptime (7 Days)",
    modal_kpi_latency: "Average Latency",
    modal_kpi_status: "Current Status",
    modal_incidents_title: "Incident & Outage History",
    modal_no_incidents: "No outages recorded in the past 7 days.",
    modal_th_time: "Timestamp",
    modal_th_status: "Status",
    modal_th_latency: "Latency",
    modal_th_details: "Details",
    modal_conn_error: "Connection Error",

    // Docs Page
    docs_page_title: "System Architecture & Component Guide",
    docs_page_subtitle: "Comprehensive technical documentation detailing the roles, responsibilities, and interactions across the Krümel AI stack.",
    docs_architecture_title: "System Architecture & Data Flows",
    docs_architecture_desc: "The Krümel AI stack strictly separates <strong>Infrastructure & Governance (kruemel-ai-infra)</strong> from <strong>Agent Orchestration (kruemel-ai-agents / n8n)</strong>. All model calls route through LiteLLM and are audited via Langfuse.",
    tier1_title: "01 Orchestration & Agent Layer",
    tier1_meta: "Client & Execution Layer",
    tier1_node1_role: "LangGraph StateGraph Machines",
    tier1_node1_desc: "Autonomous multi-agents featuring structured state, tool calling, human-in-the-loop, and Langfuse tracing.",
    tier1_node2_role: "Visual Low-Code Automation",
    tier1_node2_desc: "Visual event pipelines, webhook triggers, automated data flows, and direct integration with Qdrant and LiteLLM.",
    tier1_node3_role: "Human-to-AI Chat Workspace",
    tier1_node3_desc: "Direct human interaction with local & cloud models. File uploads, RAG, prompt templates & model switcher.",

    tier1b_title: "01b Agent Tool Execution & Sandbox Layer",
    tier1b_meta: "Tool Calling & Runtime Environment",
    tier1b_node0_role: "Local Web Search Engine",
    tier1b_node0_desc: "Aggregates Google, Bing, DuckDuckGo & ArXiv without tracking. Provides an unlimited JSON search API for autonomous agents.",
    tier1b_node1_role: "Headless Browser Automation",
    tier1b_node1_desc: "Full headless Chromium for autonomous web research, screenshot capture, and dynamic scraping of complex web apps.",
    tier1b_node2_role: "Isolated Code Execution",
    tier1b_node2_desc: "Safe sandboxed execution of Python and shell snippets for agents with zero exposure to host files or root access.",

    connector1_text: "⬇ OpenAI REST Protocol (/v1/chat/completions) &bull; Port :4000",
    tier2_title: "02 Governance, Security & Model Routing",
    tier2_meta: "Central Control Point",
    tier2_gw_role: "Central control point for all incoming and outgoing LLM inference requests",
    tier2_col1_title: "🔑 RBAC & Virtual Keys",
    tier2_col1_desc: "No raw API keys in code; dedicated virtual tokens per agent (e.g. <code>key-agent-devops</code>).",
    tier2_col2_title: "🔒 PII Redaction & Safety",
    tier2_col2_desc: "Automatic redaction of passwords, emails, and sensitive user data before model inference.",
    tier2_col3_title: "💰 Token & Spend Budgets",
    tier2_col3_desc: "Realtime tracking and enforced spending limits per agent, model, and department.",
    tier2_col4_title: "🔀 Intelligent Routing",
    tier2_col4_desc: "Local-First (Ollama on Apple Silicon) with automated fallback to cloud models (OpenRouter).",
    connector2_text: "⬇ Audited Inference &bull; Distributed Traces &bull; Vector Memory Pipelines",
    tier3_title: "03 Inference, Observability & Semantic Memory",
    tier3_meta: "Core Execution & Telemetry",
    tier3_node1_role: "Prompt Tracing & Metrics",
    tier3_node1_desc: "End-to-end tracing of all agent steps, prompt versioning, latency benchmarks, and cost tracking.",
    tier3_node2_role: "Apple Silicon GPU Inference",
    tier3_node2_desc: "On-premise inference directly on Mac host (Metal GPU). Qwen 2.5 Coder, Llama 3.1 & Nomic Embeddings with zero data leak.",
    tier3_node3_role: "Vector Memory & RAG",
    tier3_node3_desc: "High-performance vector database written in Rust with HNSW indexing for semantic search and agent memory.",
    tier3_node4_role: "In-Memory Graph & Relations",
    tier3_node4_desc: "C++ in-memory graph database with Cypher/Bolt. Models entities, relationships, and topologies for multi-hop GraphRAG.",
    connector3_text: "⬇ Internal Docker Networks (litellm-net) &bull; Persistent Volumes",
    tier4_title: "04 Infrastructure & Enterprise Persistence",
    tier4_meta: "State, Queues & Analytics",
    tier4_node1_role: "Relational Database",
    tier4_node1_desc: "Central storage for LiteLLM keys, Langfuse metadata, n8n workflows, and Hub uptime logs.",
    tier4_node2_role: "In-Memory Cache & Broker",
    tier4_node2_desc: "Zero-latency exact match prompt caching for LiteLLM and task queues for background workers.",
    tier4_node3_role: "Columnar Telemetry DB",
    tier4_node3_desc: "High-speed aggregations across millions of observation and telemetry events in Langfuse.",
    tier4_node4_role: "S3 Object Storage",
    tier4_node4_desc: "Stores trace payloads, screenshots, execution PDFs, and media assets locally within container network.",

    // Component Catalog Cards
    docs_components_title: "Detailed Component Catalog",
    docs_components_subtitle: "Each component serves a dedicated function in the stack and is secured via isolated Docker networking:",
    comp_webui_role: "Human-to-AI Chat Interface & RAG Workspace",
    comp_webui_desc: "Provides a modern user interface akin to ChatGPT and Gemini. Empowers interactive chatting, prompt management, RAG document uploads, and dynamic model switching – 100% audited via LiteLLM & Langfuse.",
    comp_litellm_role: "Governance, Security & Model-Router",
    comp_litellm_desc: "Provides a unified OpenAI-standard interface. Prevents direct API key exposure to agents via virtual tokens, protects against data leaks (PII redaction), and automatically routes requests to local or cloud models.",
    comp_langfuse_role: "Application Tracing & Metrics",
    comp_langfuse_desc: "Open-source LLM engineering platform. Records every prompt, tool call, and latency. Enables systematic evaluations, cost analysis, and root-cause debugging across complex multi-agent graphs.",
    comp_n8n_role: "Low-Code Workflow & Agent Canvas",
    comp_n8n_desc: "Visually connects hundreds of services with AI models. Leverages the n8n AI Agent Node for integration with LiteLLM and Qdrant. Automated triggers, webhooks, and scheduled jobs.",
    comp_qdrant_role: "Semantic Memory & RAG",
    comp_qdrant_desc: "High-performance vector database written in Rust. Stores document embeddings and agent memories. Delivers ultrafast similarity search via HNSW indexing with payload filtering.",
    comp_memgraph_role: "In-Memory Graph & Multi-Hop Reasoning",
    comp_memgraph_desc: "Ultrafast in-memory C++ graph database with native Cypher/Bolt protocol and Memgraph Lab visualizer. Empowers GraphRAG, topological reasoning, and entity memory for autonomous agents.",
    comp_browserless_role: "Headless Browser Automation & Web Scraping",
    comp_browserless_desc: "Headless Chromium browser with WebSocket CDP and REST API. Enables agents to autonomously browse the web, interact with JavaScript-heavy SPAs, generate PDFs, and capture screenshots.",
    comp_sandbox_role: "Isolated Code Execution Sandbox",
    comp_sandbox_desc: "Ephemeral and hardened Python 3.11 / shell runtime. Agents can generate and execute dynamic code safely, governed by strict timeouts, memory constraints, and non-root execution.",
    comp_searxng_role: "Local, Privacy-Focused Meta-Search Engine",
    comp_searxng_desc: "Aggregates search results across Google, Bing, DuckDuckGo, Wikipedia, and ArXiv without ad trackers. Delivers a high-throughput JSON API for autonomous research agents.",
    comp_ollama_role: "Native Apple Silicon Inference",
    comp_ollama_desc: "Runs directly on the Mac host, leveraging the unified memory architecture (GPU/Neural Engine). Serves open-source models like Qwen 2.5 Coder and Llama 3.1 with maximum bandwidth.",
    comp_postgres_role: "Central Relational Persistence",
    comp_postgres_desc: "The backbone for configurations, user accounts, n8n workflows, and hub status logs. Reliably protected via automated snapshots (<code>make backup</code>) as compressed SQL dumps.",
    comp_redis_role: "In-Memory Cache & Message Broker",
    comp_redis_desc: "Reduces LLM latency and costs by caching identical queries at the proxy level. Doubles as a job queue for background workers and asynchronous processing.",
    comp_clickhouse_role: "Columnar Telemetry Analytics",
    comp_clickhouse_desc: "Specialized for ultrafast SQL queries across millions of telemetry and observation events in Langfuse. Delivers unmatched aggregation performance with minimal disk footprint.",
    comp_minio_role: "S3-Compatible Object Storage",
    comp_minio_desc: "Stores large payloads, media files, execution screenshots, and event batches from Langfuse completely locally and isolated within the container network.",

    // Agent Tooling & Execution Docs Section
    docs_agent_tools_title: "🛠️ Agent Tooling & Execution: Web Browsing & Secure Code Sandbox",
    docs_agent_tools_intro: "Modern autonomous agents must go beyond static text generation: they require live web exploration and safe execution of self-generated code in a sandboxed runtime.",

    // Dual Memory Section
    docs_dual_memory_title: "🧠 Dual-Memory Architecture: Vector Store (Qdrant) vs. Knowledge Graph (Memgraph)",
    docs_dual_memory_intro: "Autonomous agents and enterprise RAG pipelines require two fundamental, complementary memory forms. Krümel AI unifies unstructured semantic vector search with structured relational reasoning into a hybrid GraphRAG architecture.",
    th_dimension: "Dimension",
    th_qdrant: "🗄️ Qdrant (Vector Store)",
    th_memgraph: "🕸️ Memgraph (Knowledge Graph)",
    td_paradigm: "Paradigm",
    td_qdrant_paradigm: "Dense Vector Embeddings (High-Dimensional Space)",
    td_memgraph_paradigm: "Labeled Property Graph (Nodes, Edges, Properties)",
    td_strength: "Core Strength",
    td_qdrant_strength: "Unstructured semantic similarity (\"Find relevant text passages\")",
    td_memgraph_strength: "Multi-hop relational reasoning (\"How are A, B, and C connected?\")",
    td_query: "Query Language",
    td_qdrant_query: "Cosine Similarity, Dot-Product, HNSW REST/gRPC",
    td_memgraph_query: "Cypher Query Language (OpenCypher via Bolt :7687)",
    td_usecases: "Typical Use Cases",
    td_qdrant_usecases: "Semantic document uploads in chat, code snippet retrieval, FAQ matching",
    td_memgraph_usecases: "Infrastructure topology, dependency mapping, agent ontologies, entity triples",
    td_hybrid: "Hybrid GraphRAG",
    td_hybrid_desc: "The Gold Standard: Qdrant discovers the semantic entry points via vector similarity. Memgraph traverses relationship paths 1–2 hops deep to feed full relational context to the LLM without hallucinations.",
    docs_cypher_example_title: "Cypher Query Example in Python (LangGraph & kruemel-ai-agents):",

    docs_backup_title: "🛡️ Backup, Recovery & Disaster Management",
    docs_backup_desc: "All systems are built for 100% reproducibility. All Docker volumes, configs, and databases can be backed up at any time with a single command:",
    backup_code_snippet: `# Full snapshot backup of all PostgreSQL databases & configurations:
make backup

# Snapshot archives are saved under backups/backup_YYYYMMDD_HHMMSS.tar.gz.
# The 7 most recent snapshots are automatically retained (rotation).`
  }
};

function getSavedLanguage() {
  return localStorage.getItem("kruemel_lang") || "de";
}

function getSavedTheme() {
  return localStorage.getItem("kruemel_theme") || "dark";
}

let currentLang = getSavedLanguage();
let currentTheme = getSavedTheme();

function applyTheme(theme) {
  currentTheme = theme;
  document.documentElement.setAttribute("data-theme", theme);
  localStorage.setItem("kruemel_theme", theme);
  const btn = document.getElementById("btn-theme");
  if (btn) {
    btn.innerText = theme === "dark" ? I18N[currentLang].btn_theme_light : I18N[currentLang].btn_theme_dark;
  }
}

function toggleTheme() {
  applyTheme(currentTheme === "dark" ? "light" : "dark");
}

function applyLanguage(lang) {
  currentLang = lang;
  localStorage.setItem("kruemel_lang", lang);
  document.documentElement.setAttribute("lang", lang);
  
  // Update elements with data-i18n attribute
  document.querySelectorAll("[data-i18n]").forEach(el => {
    const key = el.getAttribute("data-i18n");
    if (I18N[lang] && I18N[lang][key] !== undefined) {
      el.innerHTML = I18N[lang][key];
    }
  });

  const langBtn = document.getElementById("btn-lang");
  if (langBtn) {
    langBtn.innerText = lang === "de" ? "🇬🇧 EN" : "🇩🇪 DE";
  }

  // Update theme button text for the new language
  applyTheme(currentTheme);

  // Trigger optional page-specific re-renders (e.g. status monitors)
  if (typeof window.onLanguageChange === "function") {
    try {
      window.onLanguageChange(lang);
    } catch (err) {
      console.warn("onLanguageChange error:", err);
    }
  }
}

function toggleLanguage() {
  const nextLang = currentLang === "de" ? "en" : "de";
  applyLanguage(nextLang);
}

// Global Tooltip Management
const globalTooltip = document.getElementById("global-tooltip");
function showTooltip(event, text) {
  if (!globalTooltip) return;
  globalTooltip.innerText = text;
  globalTooltip.style.display = "block";
  globalTooltip.style.left = (event.pageX + 10) + "px";
  globalTooltip.style.top = (event.pageY - 28) + "px";
}
function hideTooltip() {
  if (globalTooltip) globalTooltip.style.display = "none";
}

// Global Status & Health Poller
async function updateGlobalHealth() {
  try {
    const res = await fetch("/api/health");
    const data = await res.json();
    const pill = document.getElementById("header-health-pill");
    const text = document.getElementById("header-health-text");
    if (!pill || !text) return;

    if (data.status === "healthy") {
      pill.className = "health-indicator-btn";
      text.innerText = `${I18N[currentLang].pill_all_healthy} (${data.online_services}/${data.total_services})`;
    } else if (data.status === "degraded") {
      pill.className = "health-indicator-btn degraded";
      text.innerText = `${I18N[currentLang].pill_degraded} (${data.online_services}/${data.total_services})`;
    } else {
      pill.className = "health-indicator-btn down";
      text.innerText = `${I18N[currentLang].pill_down} (${data.online_services}/${data.total_services})`;
    }
  } catch (err) {
    console.warn("Health check error:", err);
  }
}

// ─── Matrix ASCII Canvas Animation ──────────────
function initMatrixAnimation() {
  const canvas = document.getElementById("matrix-canvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");

  let width = (canvas.width = canvas.offsetWidth);
  let height = (canvas.height = canvas.offsetHeight);

  window.addEventListener("resize", () => {
    if (!canvas) return;
    width = canvas.width = canvas.offsetWidth;
    height = canvas.height = canvas.offsetHeight;
    initColumns();
  });

  const techTokens = [
    "0x7F", "POSTGRES", "LITELLM", "LANGFUSE", "N8N", "QDRANT", "OLLAMA",
    "METAL", "GPU", "REST", "ACK", "INIT", "PORT", "200_OK", "NET", "HNSW",
    "CACHE", "REDIS", "OLAP", "BLOB", "AUTH", "0101", "1010", "RUN", "SYS",
    "AGENT", "TOKEN", "PROXY", "TRACE", "MODEL", "RAG", "SYNC"
  ];
  const charTokens = "0123456789ABCDEF$#@%&*+=~^:<>{}[]|/\\";

  const fontSize = 13;
  let columns = Math.floor(width / (fontSize * 1.8));
  let drops = [];
  let speeds = [];

  function initColumns() {
    columns = Math.floor(width / (fontSize * 1.8));
    drops = [];
    speeds = [];
    for (let i = 0; i < columns; i++) {
      drops[i] = Math.floor(Math.random() * -60);
      speeds[i] = 1 + Math.random() * 1.2;
    }
  }
  initColumns();

  let lastTime = 0;
  const fps = 28;
  const interval = 1000 / fps;

  function draw(time) {
    requestAnimationFrame(draw);
    const delta = time - lastTime;
    if (delta < interval) return;
    lastTime = time - (delta % interval);

    const isLight = document.documentElement.getAttribute("data-theme") === "light";

    // Subtle fading trail
    ctx.fillStyle = isLight ? "rgba(248, 250, 252, 0.22)" : "rgba(9, 9, 11, 0.16)";
    ctx.fillRect(0, 0, width, height);

    ctx.font = `${fontSize}px 'JetBrains Mono', monospace`;

    for (let i = 0; i < drops.length; i++) {
      const x = i * (fontSize * 1.8);
      const y = drops[i] * fontSize;

      if (y > 0 && y < height + 40) {
        const useToken = Math.random() < 0.22;
        const text = useToken
          ? techTokens[Math.floor(Math.random() * techTokens.length)]
          : charTokens[Math.floor(Math.random() * charTokens.length)];

        // Glowing leader
        if (Math.random() < 0.25) {
          ctx.fillStyle = isLight ? "#1d4ed8" : "#a7f3d0";
        } else {
          ctx.fillStyle = isLight ? "rgba(37, 99, 235, 0.7)" : "rgba(16, 185, 129, 0.8)";
        }

        ctx.fillText(text, x, y);
      }

      if (y > height && Math.random() > 0.975) {
        drops[i] = 0;
      }
      drops[i] += speeds[i];
    }
  }

  requestAnimationFrame(draw);
}

// Automatically rewrite any hardcoded localhost links to active hostname (supports LAN, Tailscale, VPN)
function resolveDynamicHostnames() {
  const host = window.location.hostname;
  if (!host || host === "localhost" || host === "127.0.0.1") return;

  document.querySelectorAll('a[href*="localhost"]').forEach((link) => {
    link.href = link.href.replace("//localhost", "//" + host);
  });

  document.querySelectorAll("pre code").forEach((code) => {
    if (code.textContent.includes("localhost")) {
      code.textContent = code.textContent.replaceAll("localhost", host);
    }
  });
}

// Robust hydration & navigation lifecycle management
function initKruemelHub() {
  currentLang = getSavedLanguage();
  currentTheme = getSavedTheme();
  applyTheme(currentTheme);
  applyLanguage(currentLang);
  resolveDynamicHostnames();
  updateGlobalHealth();
  if (!window._kruemelHealthInterval) {
    window._kruemelHealthInterval = setInterval(updateGlobalHealth, 10000);
  }
  initMatrixAnimation();
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initKruemelHub);
} else {
  initKruemelHub();
}

window.addEventListener("pageshow", () => {
  currentLang = getSavedLanguage();
  currentTheme = getSavedTheme();
  applyTheme(currentTheme);
  applyLanguage(currentLang);
  resolveDynamicHostnames();
});
