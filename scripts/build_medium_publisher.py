#!/usr/bin/env python3
"""
Build the interactive 1-Click Medium Publisher & Copy-Paste Tool.
Converts all 7 articles from medium/articles/*.md into pre-rendered, Medium-optimized HTML
and includes Medium Publishing Tags, Subtitles, and SEO descriptions.
"""
import os
import json
import re
import markdown

ARTICLES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "medium", "articles"))
OUTPUT_STANDALONE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "medium", "publisher.html"))
OUTPUT_HUB = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "hub", "medium.html"))

ARTICLE_METADATA = [
    {
        "id": "00",
        "filename": "00_beyond_toy_bots_enterprise_ai_blueprint.md",
        "title": "00. The Master Blueprint (5 Pillars & Architecture)",
        "subtitle": "How we engineered an audited, zero-lock-in enterprise AI platform with LiteLLM, Langfuse, Memgraph, Qdrant, and LangGraph micro-workers.",
        "seo_description": "A production-ready blueprint for building self-hosted, audited enterprise multi-agent AI infrastructure with LiteLLM, Langfuse, and Docker.",
        "tags": ["Artificial Intelligence", "Software Engineering", "Devops", "Open Source", "System Architecture"]
    },
    {
        "id": "01",
        "filename": "01_slashing_90_percent_llm_costs_litellm_finops.md",
        "title": "01. Slashing 90% Costs (LiteLLM & FinOps)",
        "subtitle": "Decouple agent code from commercial AI providers, route to local GPUs ($0.00) with automatic cloud fallbacks, and enforce monthly budget caps.",
        "seo_description": "Learn how to slash 90% of enterprise LLM expenses using LiteLLM model routing, semantic caching, and virtual key spend caps.",
        "tags": ["Artificial Intelligence", "Finops", "Software Engineering", "Devops", "Open Source"]
    },
    {
        "id": "02",
        "filename": "02_zero_trust_prompting_pii_redaction.md",
        "title": "02. Zero-Trust Prompting (PII Shield)",
        "subtitle": "Why local LLMs alone are not a silver bullet for data privacy, and how to build automatic PII redaction and audit trails into your gateway.",
        "seo_description": "Implement real-time PII redaction, secret scanning, and GDPR compliance for enterprise AI prompts before data leaves your network.",
        "tags": ["Cybersecurity", "Artificial Intelligence", "Data Privacy", "Software Engineering", "Information Security"]
    },
    {
        "id": "03",
        "filename": "03_full_stack_observability_langfuse_evals.md",
        "title": "03. Full-Stack Observability (Langfuse Evals)",
        "subtitle": "Why traditional logs fail for multi-agent loops, and how to audit every tool call, latency bottleneck, and token spend in ClickHouse and Langfuse.",
        "seo_description": "Achieve full-stack observability and automated evaluation for LangGraph multi-agent systems using Langfuse and ClickHouse.",
        "tags": ["Observability", "Artificial Intelligence", "Devops", "Software Development", "Monitoring"]
    },
    {
        "id": "04",
        "filename": "04_vectors_are_not_enough_qdrant_memgraph_hybrid_memory.md",
        "title": "04. Dual Memory (Qdrant + Memgraph)",
        "subtitle": "Merging semantic fuzzy search with relational graph traversals (Memgraph) to eliminate hallucinations and context window explosions.",
        "seo_description": "Why vector embeddings fail on multi-hop questions, and how dual memory with Qdrant and Memgraph powers accurate GraphRAG agents.",
        "tags": ["Knowledge Graph", "Artificial Intelligence", "Databases", "Software Architecture", "Data Science"]
    },
    {
        "id": "05",
        "filename": "05_death_to_the_agent_monolith_docker_microworkers.md",
        "title": "05. Container Mesh (Docker Micro-Workers)",
        "subtitle": "How we decoupled 5 LangGraph agents into sandboxed micro-workers, secured them with least-privilege mounts, and orchestrated live SSE streaming.",
        "seo_description": "Stop running monolithic Python agent scripts. Learn how to containerize LangGraph agents with Docker and least-privilege security.",
        "tags": ["Docker", "Devops", "Software Architecture", "Artificial Intelligence", "Microservices"]
    },
    {
        "id": "06",
        "filename": "06_when_agents_sleep_continuous_self_evolution.md",
        "title": "06. Self-Evolution (Nightly Reflection Cycles)",
        "subtitle": "Why hardcoded system prompts are a dead end, and how we built a closed-loop self-evolution architecture with Langfuse traces and episodic memory.",
        "seo_description": "Build autonomous agents that learn from operational failures, reflect during sleep loops, and continuously evolve their prompts and tools.",
        "tags": ["Artificial Intelligence", "Machine Learning", "Software Engineering", "Autonomous Agents", "Tech Trends"]
    }
]

def md_to_clean_html(md_text):
    html = markdown.markdown(md_text, extensions=['extra', 'sane_lists', 'nl2br'])
    return html

def main():
    articles_data = []
    
    for item in ARTICLE_METADATA:
        fpath = os.path.join(ARTICLES_DIR, item["filename"])
        if not os.path.exists(fpath):
            print(f"Warning: {fpath} not found")
            continue
        with open(fpath, "r", encoding="utf-8") as f:
            raw_md = f.read()
        
        rendered_html = md_to_clean_html(raw_md)
        articles_data.append({
            "id": item["id"],
            "filename": item["filename"],
            "title": item["title"],
            "subtitle": item["subtitle"],
            "seo_description": item["seo_description"],
            "tags": item["tags"],
            "raw_md": raw_md,
            "html": rendered_html
        })

    articles_json = json.dumps(articles_data)

    template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Krümel AI - Medium 1-Click Copy-Paste Publisher</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600&family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-canvas: #09090b;
            --bg-surface: #111115;
            --bg-card: #18181b;
            --border: #27272a;
            --border-hover: #3f3f46;
            --text-main: #fafafa;
            --text-muted: #a1a1aa;
            --accent-blue: #3b82f6;
            --accent-emerald: #10b981;
            --accent-purple: #8b5cf6;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: var(--bg-canvas);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }

        /* Top Bar */
        header {
            position: sticky;
            top: 0;
            z-index: 50;
            background: rgba(9, 9, 11, 0.88);
            backdrop-filter: blur(16px);
            border-bottom: 1px solid var(--border);
            padding: 0.85rem 2rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1.5rem;
        }

        .brand {
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }

        .brand-badge {
            background: linear-gradient(135deg, #3b82f6 0%, #10b981 100%);
            color: #000;
            font-weight: 800;
            font-size: 0.75rem;
            padding: 0.25rem 0.6rem;
            border-radius: 6px;
            letter-spacing: 0.05em;
            text-transform: uppercase;
        }

        .brand h1 {
            font-size: 1.05rem;
            font-weight: 700;
            letter-spacing: -0.02em;
            color: #fff;
        }

        .controls {
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        select.article-select {
            background: var(--bg-card);
            border: 1px solid var(--border);
            color: #fff;
            padding: 0.55rem 1rem;
            border-radius: 8px;
            font-size: 0.88rem;
            font-weight: 500;
            outline: none;
            cursor: pointer;
            transition: border-color 0.15s ease;
            min-width: 380px;
        }

        select.article-select:hover, select.article-select:focus {
            border-color: var(--accent-blue);
        }

        .btn-copy {
            background: linear-gradient(135deg, #2563eb 0%, #059669 100%);
            color: #fff;
            border: none;
            padding: 0.6rem 1.4rem;
            border-radius: 8px;
            font-size: 0.9rem;
            font-weight: 700;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            transition: all 0.2s ease;
            box-shadow: 0 4px 14px rgba(37, 99, 235, 0.35);
        }

        .btn-copy:hover {
            transform: translateY(-1px);
            box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
        }

        .btn-outline {
            background: var(--bg-card);
            border: 1px solid var(--border);
            color: var(--text-muted);
            padding: 0.55rem 1rem;
            border-radius: 8px;
            font-size: 0.85rem;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            transition: all 0.15s ease;
        }

        .btn-outline:hover {
            color: #fff;
            border-color: var(--border-hover);
        }

        /* Banner info */
        .info-strip {
            background: rgba(59, 130, 246, 0.08);
            border-bottom: 1px solid rgba(59, 130, 246, 0.2);
            padding: 0.65rem 2rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 0.85rem;
            color: #93c5fd;
        }

        .info-strip a {
            color: #60a5fa;
            text-decoration: underline;
        }

        /* Main Workspace */
        main {
            flex: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 2rem 1.5rem 5rem 1.5rem;
            gap: 1.5rem;
        }

        /* Publication Metadata Box (Tags, Subtitle, SEO) */
        .meta-card {
            width: 100%;
            max-width: 820px;
            background: #111116;
            border: 1px solid #27272f;
            border-radius: 12px;
            padding: 1.4rem 1.75rem;
            display: flex;
            flex-direction: column;
            gap: 1rem;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
        }

        .meta-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .meta-title {
            font-size: 0.85rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: #a1a1aa;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .tags-container {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 0.5rem;
        }

        .tag-chip {
            background: rgba(59, 130, 246, 0.12);
            color: #93c5fd;
            border: 1px solid rgba(59, 130, 246, 0.3);
            font-size: 0.82rem;
            font-weight: 600;
            padding: 0.35rem 0.75rem;
            border-radius: 20px;
            display: flex;
            align-items: center;
            gap: 0.3rem;
            user-select: all;
        }

        .btn-copy-sm {
            background: var(--bg-card);
            border: 1px solid var(--border);
            color: #e4e4e7;
            font-size: 0.78rem;
            font-weight: 600;
            padding: 0.3rem 0.75rem;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.15s ease;
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
        }

        .btn-copy-sm:hover {
            border-color: var(--accent-blue);
            color: #60a5fa;
        }

        .meta-row {
            font-size: 0.86rem;
            line-height: 1.5;
            color: #d4d4d8;
            background: #18181f;
            padding: 0.65rem 1rem;
            border-radius: 8px;
            border: 1px solid #272733;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 1rem;
        }

        .meta-row span strong {
            color: #fff;
            margin-right: 0.4rem;
        }

        .article-container {
            width: 100%;
            max-width: 820px;
            background: var(--bg-surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 3rem 3.5rem;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.45);
        }

        /* Article Typography - Native Medium emulation */
        .rendered-content {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            color: #e4e4e7;
            font-size: 1.12rem;
            line-height: 1.75;
        }

        .rendered-content h1 {
            font-size: 2.35rem;
            font-weight: 800;
            letter-spacing: -0.03em;
            line-height: 1.25;
            color: #ffffff;
            margin-bottom: 1.25rem;
        }

        .rendered-content h2 {
            font-size: 1.65rem;
            font-weight: 700;
            letter-spacing: -0.02em;
            line-height: 1.35;
            color: #f4f4f5;
            margin-top: 2.75rem;
            margin-bottom: 1rem;
            padding-bottom: 0.35rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        }

        .rendered-content h3 {
            font-size: 1.3rem;
            font-weight: 600;
            letter-spacing: -0.015em;
            line-height: 1.4;
            color: #e4e4e7;
            margin-top: 2rem;
            margin-bottom: 0.75rem;
        }

        .rendered-content p {
            margin-bottom: 1.35rem;
        }

        .rendered-content strong {
            color: #ffffff;
            font-weight: 700;
        }

        .rendered-content em {
            color: #d4d4d8;
        }

        .rendered-content a {
            color: #60a5fa;
            text-decoration: underline;
            text-underline-offset: 3px;
        }

        .rendered-content hr {
            border: none;
            text-align: center;
            margin: 2.5rem 0;
            height: 24px;
        }

        .rendered-content hr::before {
            content: '...';
            letter-spacing: 0.6em;
            color: #71717a;
            font-size: 1.5rem;
            font-weight: bold;
        }

        .rendered-content img {
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            margin: 1.75rem 0 0.5rem 0;
            border: 1px solid var(--border);
            display: block;
        }

        .rendered-content blockquote {
            border-left: 3px solid var(--accent-blue);
            padding: 0.6rem 1.25rem;
            margin: 1.75rem 0;
            background: rgba(59, 130, 246, 0.05);
            color: #cbd5e1;
            font-style: italic;
            border-radius: 0 6px 6px 0;
        }

        .rendered-content ul, .rendered-content ol {
            margin: 1.25rem 0 1.5rem 1.5rem;
        }

        .rendered-content li {
            margin-bottom: 0.65rem;
            padding-left: 0.25rem;
        }

        .rendered-content pre {
            background: #0d0d10;
            border: 1px solid #27272a;
            border-radius: 8px;
            padding: 1.25rem 1.5rem;
            overflow-x: auto;
            margin: 1.75rem 0;
        }

        .rendered-content code {
            font-family: 'Fira Code', monospace;
            font-size: 0.95rem;
            color: #38bdf8;
            background: rgba(255, 255, 255, 0.06);
            padding: 0.15rem 0.35rem;
            border-radius: 4px;
        }

        .rendered-content pre code {
            background: transparent;
            padding: 0;
            color: #f1f5f9;
            font-size: 0.9rem;
            line-height: 1.6;
        }

        /* Toast notification */
        .toast {
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            background: #10b981;
            color: #000;
            font-weight: 700;
            padding: 0.85rem 1.5rem;
            border-radius: 8px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
            display: flex;
            align-items: center;
            gap: 0.6rem;
            opacity: 0;
            transform: translateY(20px);
            transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
            pointer-events: none;
            z-index: 100;
        }

        .toast.visible {
            opacity: 1;
            transform: translateY(0);
        }
    </style>
</head>
<body>
    <header>
        <div class="brand">
            <span class="brand-badge">Medium Publisher</span>
            <h1>Krümel AI Series</h1>
        </div>

        <div class="controls">
            <select id="articleSelect" class="article-select" onchange="switchArticle(this.value)">
                <!-- populated dynamically -->
            </select>
            <button class="btn-copy" onclick="copyForMedium()">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><rect width="14" height="14" x="8" y="8" rx="2" ry="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/></svg>
                1-Click Copy for Medium
            </button>
            <a href="https://medium.com/new-story" target="_blank" class="btn-outline">
                Open Medium Draft ↗
            </a>
        </div>
    </header>

    <div class="info-strip">
        <span>💡 <strong>Publishing flow:</strong> Click <em>"1-Click Copy for Medium"</em>, switch to Medium editor, press <strong>Cmd+V</strong>, and use the recommended 5 tags below when publishing!</span>
        <span>Images hosted on: <a href="https://github.com/wortkotze/medium-kruemel-ai-infra" target="_blank">github.com/wortkotze/medium-kruemel-ai-infra</a></span>
    </div>

    <main>
        <!-- Metadata & Recommended Tags Box -->
        <div class="meta-card">
            <div class="meta-header">
                <span class="meta-title">🏷️ Recommended Medium Tags (Max 5 allowed):</span>
                <button class="btn-copy-sm" onclick="copyCurrentTags()">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><rect width="14" height="14" x="8" y="8" rx="2" ry="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/></svg>
                    Copy All 5 Tags
                </button>
            </div>
            <div id="tagsContainer" class="tags-container">
                <!-- Tag chips inserted dynamically -->
            </div>
            <div class="meta-row">
                <span id="subtitleText"><strong>Subtitle:</strong> ...</span>
                <button class="btn-copy-sm" onclick="copySubtitle()">Copy Subtitle</button>
            </div>
        </div>

        <div class="article-container">
            <div id="renderedArticle" class="rendered-content">
                <!-- active article HTML injected here -->
            </div>
        </div>
    </main>

    <div id="toast" class="toast">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>
        <span id="toastMsg">Copied! Switch to Medium and press Cmd+V</span>
    </div>

    <script>
        const articles = __ARTICLES_DATA_PLACEHOLDER__;

        const selectEl = document.getElementById('articleSelect');
        const containerEl = document.getElementById('renderedArticle');
        const tagsContainerEl = document.getElementById('tagsContainer');
        const subtitleTextEl = document.getElementById('subtitleText');
        const toastEl = document.getElementById('toast');
        const toastMsgEl = document.getElementById('toastMsg');

        let currentArticleIdx = 0;

        // Populate dropdown
        articles.forEach((art, idx) => {
            const opt = document.createElement('option');
            opt.value = idx;
            opt.textContent = art.title;
            selectEl.appendChild(opt);
        });

        // Load article
        function switchArticle(idx) {
            currentArticleIdx = idx;
            const current = articles[idx];
            if (!current) return;
            
            containerEl.innerHTML = current.html;
            subtitleTextEl.innerHTML = `<strong>Subtitle:</strong> ${current.subtitle}`;

            // Render tags
            tagsContainerEl.innerHTML = '';
            current.tags.forEach(tag => {
                const chip = document.createElement('span');
                chip.className = 'tag-chip';
                chip.textContent = tag;
                tagsContainerEl.appendChild(chip);
            });

            window.scrollTo({ top: 0, behavior: 'smooth' });
        }

        switchArticle(0);

        function showToast(msg) {
            toastMsgEl.textContent = msg;
            toastEl.classList.add('visible');
            setTimeout(() => {
                toastEl.classList.remove('visible');
            }, 3500);
        }

        async function copyCurrentTags() {
            const current = articles[currentArticleIdx];
            if (!current) return;
            const tagsStr = current.tags.join(', ');
            await navigator.clipboard.writeText(tagsStr);
            showToast(`🏷️ Copied 5 tags: ${tagsStr}`);
        }

        async function copySubtitle() {
            const current = articles[currentArticleIdx];
            if (!current) return;
            await navigator.clipboard.writeText(current.subtitle);
            showToast("📝 Subtitle copied to clipboard!");
        }

        async function copyForMedium() {
            try {
                const htmlContent = containerEl.innerHTML;
                const textContent = containerEl.innerText;

                const blobHtml = new Blob([htmlContent], { type: 'text/html' });
                const blobText = new Blob([textContent], { type: 'text/plain' });
                const item = new ClipboardItem({
                    'text/html': blobHtml,
                    'text/plain': blobText
                });

                await navigator.clipboard.write([item]);
                showToast("✨ Rich Text copied! Switch to Medium and press Cmd+V.");
            } catch (err) {
                console.warn("ClipboardItem API failed, falling back to selection copy:", err);
                const range = document.createRange();
                range.selectNodeContents(containerEl);
                const sel = window.getSelection();
                sel.removeAllRanges();
                sel.addRange(range);
                document.execCommand('copy');
                sel.removeAllRanges();
                showToast("✨ Rich Text copied! Switch to Medium and press Cmd+V.");
            }
        }
    </script>
</body>
</html>
"""

    final_html = template.replace("__ARTICLES_DATA_PLACEHOLDER__", articles_json)

    with open(OUTPUT_STANDALONE, "w", encoding="utf-8") as f:
        f.write(final_html)
    print(f"Generated standalone publisher: {OUTPUT_STANDALONE}")

    with open(OUTPUT_HUB, "w", encoding="utf-8") as f:
        f.write(final_html)
    print(f"Generated hub page: {OUTPUT_HUB}")

if __name__ == "__main__":
    main()
