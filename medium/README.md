# 📚 Krümel AI – Medium Publikations-Kit & Gemini Prompts

Dieses Verzeichnis enthält alle vorbereiteten Prompts, Strukturpläne und Live-Screenshots, um die gesamte Entstehungsgeschichte, Architektur und Innovation von **Krümel AI** als reichweitenstarke 7-teilige Publikationsserie auf Medium (oder Substack / Dev.to) zu veröffentlichen.

---

## 📁 Struktur dieses Verzeichnisses

```
medium/
├── README.md                          # Dieses Strategie- und Benutzerhandbuch
├── screenshots/                       # Echte, hochauflösende Screenshots unserer Lösung
│   ├── 01_kruemel_hub_overview.png    # Krümel Hub Landing Page & Navigation
│   ├── 02_agent_cockpit_online_status.png # Multi-Agent Cockpit (alle 5 Micro-Worker ONLINE)
│   └── 03_open_webui_chat.png         # Open WebUI Chat Suite mit Modellauswahl
└── prompts/                           # Ausformulierte Mega-Prompts für Google Gemini
    ├── 00_master_blueprint_prompt.md  # Prolog / Der große Architektur-Überblick
    ├── 01_litellm_routing_finops_prompt.md # Teil 1: LiteLLM, Virtual Keys & 90% Kosten sparen
    ├── 02_zero_trust_pii_prompt.md    # Teil 2: PII-Redaction, DLP & Zero-Trust Prompting
    ├── 03_observability_langfuse_evals_prompt.md # Teil 3: Langfuse Traces, Evals & ClickHouse
    ├── 04_hybrid_memory_qdrant_memgraph_prompt.md # Teil 4: Duales Gedächtnis (Qdrant & Memgraph)
    ├── 05_agent_mesh_microworkers_prompt.md # Teil 5: Docker Micro-Worker & Least-Privilege
    └── 06_self_evolving_agents_prompt.md # Teil 6: Kontinuierliche Selbstoptimierung & Evolution
```

---

## 🚀 Workflow: So generierst du die Artikel mit Google Gemini

1. Öffne **Google Gemini** (empfohlen: Gemini Advanced mit Gemini 1.5 Pro oder Gemini 2.0).
2. Öffne den gewünschten Prompt aus `medium/prompts/` (z. B. `00_master_blueprint_prompt.md`).
3. Kopiere den gesamten Markdown-Inhalt des Prompts und füge ihn in Gemini ein.
4. Gemini erstellt daraufhin einen vollständigen, professionellen Artikel (2.000–2.500 Wörter) mit Zwischenüberschriften, Beispielen und Diagrammen.
5. Füge beim Veröffentlichen auf Medium die passenden Screenshots aus `medium/screenshots/` an den im Artikel markierten Stellen ein.

---

## 💡 Strategische Frage: Macht ein öffentliches Boilerplate-Repository Sinn?

### Klares Fazit: **JA, absolut!**

Ein begleitendes Open-Source-Boilerplate-Repository auf GitHub ist der **größte Hebel für Klicks, Follower und GitHub-Stars**. Artikel, die mit einem funktionierenden `git clone ... && docker compose up -d` verknüpft sind, erzielen ein Vielfaches der Reichweite reiner Textbeiträge.

### 🛡️ Wie stellen wir 100% sicher, dass keine Credentials oder Secrets leaken?

Wenn du ein öffentliches Boilerplate-Repo bereitstellst, müssen folgende **4 Sicherheitsregeln** strikt eingehalten werden:

1. **Neues, sauberes Repository anlegen (Kein bestehendes Repo auf Public schalten!):**
   * Alte Git-Histories können vergessene Test-Keys enthalten. Erstelle ein frisches Repository (z. B. `kruemel-ai-starter` oder `enterprise-agent-mesh-starter`).
2. **Das Zero-Secret Principle in Git:**
   * Niemals eine `.env`-Datei committen.
   * Ausschließlich eine `.env.example` mit generischen Platzhaltern (`your-master-key-here`, `password123`) bereitstellen.
   * Strikte `.gitignore` für alle Dateitypen wie `.env`, `*.key`, `*.pem`, `*.db`, `*.sqlite`.
3. **Automatisierter Key-Generator (`scripts/init.sh`):**
   * Statt dass der User Passwörter manuell tippt oder Default-Passwörter im Code stehen, generiert ein Skript beim ersten Ausführen sichere Random-Secrets:
     ```bash
     POSTGRES_PASSWORD=$(openssl rand -hex 16)
     LITELLM_MASTER_KEY="sk-kruemel-"$(openssl rand -hex 24)
     ```
   * Das Skript schreibt die Werte automatisch in die lokale `.env`. Null Secrets im Repository!
4. **Automatisierter Pre-Commit Secret-Scanner:**
   * Vor jedem Push lassen wir **Gitleaks** oder **TruffleHog** laufen:
     ```bash
     docker run --rm -v "$PWD:/repo" zricethezav/gitleaks:latest detect --source="/repo" -v
     ```
   * Zusätzlich aktivieren wir die kostenlose GitHub-Funktion **Secret Scanning & Push Protection** in den Repo-Settings.

---

## 📈 Veröffentlichungs-Fahrplan (Content Schedule)

| Woche | Artikel | Fokus | LinkedIn-Aufhänger |
| :---: | :--- | :--- | :--- |
| **Woche 1** | **Master Blueprint** | Das Gesamtsystem & Warum Spielzeug-Bots scheitern | *"Warum 90% aller Enterprise-Agenten im PoC steckenbleiben – und wie die echte Architektur aussieht."* |
| **Woche 2** | **Teil 1: LiteLLM FinOps** | Model-Routing, Local-First (0 €) & Virtual Keys | *"Wie wir 90% der OpenAI-Kosten eingespart haben, ohne den Code unserer Agenten anzufassen."* |
| **Woche 3** | **Teil 2: Zero-Trust & PII** | Datenschutz, DSGVO & automatische Maskierung | *"Lokale LLMs schützen dich nicht vor Datenlecks. Warum du PII vor dem API-Call schwärzen musst."* |
| **Woche 4** | **Teil 3: Observability** | Langfuse Traces, ClickHouse & Evals | *"Warum print()-Debugging bei autonomen Agenten in die Hölle führt."* |
| **Woche 5** | **Teil 4: Hybrid Memory** | Vektoren (Qdrant) + Wissensgraph (Memgraph) | *"Warum Vektordatenbanken für komplexe Unternehmensstrukturen blind sind."* |
| **Woche 6** | **Teil 5: Docker Micro-Workers** | Isolation, Least Privilege & Self-Registration | *"Schluss mit dem Agenten-Monolithen: Jeder Agent gehört in seine eigene Sandbox."* |
| **Woche 7** | **Teil 6: Continuous Evolution** | Reflexion, Sleep Cycles & dynamische Prompts | *"Wenn Agenten schlafen gehen: Wie autonome Systeme aus Fehlern lernen."* |
