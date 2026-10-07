#!/usr/bin/env python3
"""
Build the interactive 1-Click Medium Publisher & Copy-Paste Tool.
Converts all 7 articles from medium/articles/*.md into pre-rendered, Medium-optimized HTML.
"""
import os
import json
import re
import markdown

ARTICLES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "medium", "articles"))
OUTPUT_STANDALONE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "medium", "publisher.html"))
OUTPUT_HUB = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "hub", "medium.html"))

ARTICLE_FILES = [
    ("00", "00_beyond_toy_bots_enterprise_ai_blueprint.md", "00. The Master Blueprint (5 Pillars & Architecture)"),
    ("01", "01_slashing_90_percent_llm_costs_litellm_finops.md", "01. Slashing 90% Costs (LiteLLM & FinOps)"),
    ("02", "02_zero_trust_prompting_pii_redaction.md", "02. Zero-Trust Prompting (PII Shield)"),
    ("03", "03_full_stack_observability_langfuse_evals.md", "03. Full-Stack Observability (Langfuse Evals)"),
    ("04", "04_vectors_are_not_enough_qdrant_memgraph_hybrid_memory.md", "04. Dual Memory (Qdrant + Memgraph)"),
    ("05", "05_death_to_the_agent_monolith_docker_microworkers.md", "05. Container Mesh (Docker Micro-Workers)"),
    ("06", "06_when_agents_sleep_continuous_self_evolution.md", "06. Self-Evolution (Nightly Reflection Cycles)")
]

def md_to_clean_html(md_text):
    # Ensure raw markdown is converted with fenced code blocks & clean tables
    html = markdown.markdown(md_text, extensions=['extra', 'sane_lists', 'nl2br'])
    return html

def main():
    articles_data = []
    
    for idx, fname, title in ARTICLE_FILES:
        fpath = os.path.join(ARTICLES_DIR, fname)
        if not os.path.exists(fpath):
            print(f"Warning: {fpath} not found")
            continue
        with open(fpath, "r", encoding="utf-8") as f:
            raw_md = f.read()
        
        # Convert to clean HTML
        rendered_html = md_to_clean_html(raw_md)
        articles_data.append({
            "id": idx,
            "filename": fname,
            "title": title,
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
            background: rgba(9, 9, 11, 0.85);
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

        .btn-copy:active {
            transform: translateY(1px);
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
            justify-content: center;
            padding: 2.5rem 1.5rem 5rem 1.5rem;
        }

        .article-container {
            width: 100%;
            max-width: 780px;
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
        <span>💡 <strong>How it works:</strong> Click <em>"1-Click Copy for Medium"</em>, switch to Medium's story editor, and press <strong>Cmd+V</strong>. Headings, code blocks, bullet points, and images will render natively!</span>
        <span>Images hosted on: <a href="https://github.com/wortkotze/medium-kruemel-ai-infra" target="_blank">github.com/wortkotze/medium-kruemel-ai-infra</a></span>
    </div>

    <main>
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
        const toastEl = document.getElementById('toast');
        const toastMsgEl = document.getElementById('toastMsg');

        // Populate dropdown
        articles.forEach((art, idx) => {
            const opt = document.createElement('option');
            opt.value = idx;
            opt.textContent = art.title;
            selectEl.appendChild(opt);
        });

        // Load initial article
        function switchArticle(idx) {
            const current = articles[idx];
            if (!current) return;
            containerEl.innerHTML = current.html;
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

        async function copyForMedium() {
            try {
                // Get clean HTML content
                const htmlContent = containerEl.innerHTML;
                const textContent = containerEl.innerText;

                // Modern Clipboard API supporting text/html (Rich Text)
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
                // Fallback: Select node contents and copy as Rich Text
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

    # Write standalone file
    with open(OUTPUT_STANDALONE, "w", encoding="utf-8") as f:
        f.write(final_html)
    print(f"Generated standalone publisher: {OUTPUT_STANDALONE}")

    # Write hub file
    with open(OUTPUT_HUB, "w", encoding="utf-8") as f:
        f.write(final_html)
    print(f"Generated hub page: {OUTPUT_HUB}")

if __name__ == "__main__":
    main()
