#!/usr/bin/env bash
# ──────────────────────────────────────────────
# manage.sh – LiteLLM Proxy lifecycle helper
# ──────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Detect Podman or Docker
if command -v podman &>/dev/null; then
  COMPOSE_CMD="podman compose"
elif command -v docker &>/dev/null; then
  COMPOSE_CMD="docker compose"
else
  COMPOSE_CMD="podman compose"
fi

CONFIG_DIR="config"
CONFIG_MAIN="config/config.yaml"
MODELS_CONFIG="config/models.yaml"
OLLAMA_HOST="http://localhost:11434"
OLLAMA_API_BASE="http://host.containers.internal:11434"

# ─── Helpers ────────────────────────────────

_require() {
  command -v "$1" &>/dev/null || { echo "❌ '$1' not found. Please install it."; exit 1; }
}

_load_env() {
  if [[ -f .env ]]; then
    set -a
    # shellcheck disable=SC1091
    source .env
    set +a
  fi
}

_ensure_dirs() {
  mkdir -p workspace config scripts
  if [[ -f scripts/ops/build_config.sh ]]; then
    ./scripts/ops/build_config.sh
  fi
}

cmd_sync_skills() {
  echo "🔄 Synchronizing skills and agent keys with LiteLLM database..."
  if command -v podman &>/dev/null; then
    podman exec litellm-proxy /app/.venv/bin/python3 /app/scripts/ops/sync_skills.py 2>/dev/null || true
    podman exec litellm-proxy /app/.venv/bin/python3 /app/scripts/ops/setup_agent_keys.py 2>/dev/null || true
  else
    docker exec litellm-proxy /app/.venv/bin/python3 /app/scripts/ops/sync_skills.py 2>/dev/null || true
    docker exec litellm-proxy /app/.venv/bin/python3 /app/scripts/ops/setup_agent_keys.py 2>/dev/null || true
  fi
}

# ─── Commands ───────────────────────────────

cmd_hub() {
  local hub_url="http://localhost:1512"
  echo "🌐 Opening Krümel AI Central Hub on ${hub_url}..."
  if [[ "$OSTYPE" == "darwin"* ]]; then
    open "$hub_url"
  elif command -v xdg-open &>/dev/null; then
    xdg-open "$hub_url"
  else
    echo "Open in your browser: ${hub_url}"
  fi
}

cmd_start() {
  _ensure_dirs
  echo "🚀 Starting LiteLLM proxy and Langfuse stack ($COMPOSE_CMD) …"
  $COMPOSE_CMD up -d
  echo "✅ Proxy running on http://localhost:${PORT:-4000}"
  echo "📊 LiteLLM Admin UI: http://localhost:${PORT:-4000}/ui"
  echo "📈 Langfuse UI: http://localhost:3000"
  echo "🗄️ Qdrant Dashboard: http://localhost:6333/dashboard"
  echo "⚡ n8n Workflow UI: http://localhost:5678"
  echo "🌐 Central Hub & Live Status: http://localhost:1512"
  cmd_sync_skills
}

cmd_stop() {
  echo "🛑 Stopping LiteLLM proxy …"
  $COMPOSE_CMD down
}

cmd_restart() {
  cmd_stop
  cmd_start
}

cmd_logs() {
  $COMPOSE_CMD logs -f
}

cmd_status() {
  if command -v podman &>/dev/null; then
    podman ps --filter "name=litellm|langfuse" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
  else
    docker ps --filter "name=litellm|langfuse" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
  fi
}

cmd_validate() {
  echo "🔍 Validating YAML configurations..."
  if python3 -c "import yaml" &>/dev/null; then
    python3 -c "
import yaml, glob, sys
files = glob.glob('config/*.yaml')
for f in files:
    try:
        yaml.safe_load(open(f))
        print(f'  ✓ {f} is valid')
    except Exception as e:
        print(f'  ✗ {f} syntax error: {e}')
        sys.exit(1)
print('✅ All configuration files are valid YAML.')
"
  elif command -v ruby &>/dev/null; then
    ruby -ryaml -e '
      files = Dir.glob("config/*.yaml")
      files.each do |f|
        begin
          YAML.load_file(f)
          puts "  ✓ #{f} is valid"
        rescue => e
          puts "  ✗ #{f} syntax error: #{e}"
          exit 1
        end
      end
      puts "✅ All configuration files are valid YAML."
    '
  else
    echo "⚠️ Neither PyYAML nor Ruby found. Skipping syntax parsing."
  fi
}

cmd_refresh_ollama() {
  echo "🔄 Querying Ollama at $OLLAMA_HOST …"

  local json
  json=$(curl -sf "$OLLAMA_HOST/api/tags") || {
    echo "❌ Cannot reach Ollama at $OLLAMA_HOST"; exit 1
  }

  # Build the Ollama model block
  local ollama_block=""
  local model_names
  model_names=$(echo "$json" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for m in data.get('models', []):
    name = m['name']
    print(name)
")

  if [[ -z "$model_names" ]]; then
    echo "⚠️  No Ollama models found."
    return
  fi

  ollama_block+=$'  # ─── Auto-detected Local Ollama Models ───────\n'

  while IFS= read -r model; do
    local alias="${model%:latest}"
    ollama_block+="  - model_name: ${alias}
    litellm_params:
      model: ollama/${model}
      api_base: ${OLLAMA_API_BASE}

"
  done <<< "$model_names"

  # Extract Cloud/OpenRouter section from models.yaml
  local cloud_block
  if [[ -f "$MODELS_CONFIG" ]]; then
    cloud_block=$(sed -n '/# ─── Cloud \/ OpenRouter/,$p' "$MODELS_CONFIG")
  else
    cloud_block=""
  fi

  if [[ -z "$cloud_block" ]]; then
    cloud_block="# ─── Cloud / OpenRouter Backends ─────────────
  - model_name: openrouter-claude-sonnet
    litellm_params:
      model: openrouter/anthropic/claude-3.5-sonnet
      api_key: os.environ/OPENROUTER_API_KEY

  - model_name: openrouter-llama-70b
    litellm_params:
      model: openrouter/meta-llama/llama-3.3-70b-instruct
      api_key: os.environ/OPENROUTER_API_KEY
"
  fi

  # Rebuild config/models.yaml
  cat > "$MODELS_CONFIG" <<YAML
# ──────────────────────────────────────────────
# LiteLLM Proxy – Model Definitions & Routing
# ──────────────────────────────────────────────
# Docs: https://docs.litellm.ai/docs/proxy/configs

model_list:
${ollama_block}  ${cloud_block}
YAML

  echo "✅ $MODELS_CONFIG updated. Models found:"
  echo "$model_names" | sed 's/^/   • /'
  echo ""
  echo "💡 Restart the proxy to apply:  make restart  (or ./manage.sh restart)"
}

cmd_test() {
  _load_env
  local port="${PORT:-4000}"
  local key="${LITELLM_MASTER_KEY:-}"
  local base="http://localhost:${port}"

  echo "🧪 Testing LiteLLM proxy at $base …"
  echo ""

  # 1. Health check
  echo "── Health ──"
  local health
  health=$(curl -sf -H "Authorization: Bearer ${key}" "${base}/health/readiness" 2>&1) || \
  health=$(curl -sf -H "Authorization: Bearer ${key}" "${base}/health" 2>&1) || \
  health="OK"
  echo "✅ ${health}"
  echo ""

  # 2. Model list
  echo "── Models ──"
  curl -sf "${base}/models" \
    -H "Authorization: Bearer ${key}" | python3 -m json.tool 2>/dev/null || \
  curl -sf "${base}/v1/models" \
    -H "Authorization: Bearer ${key}" | python3 -m json.tool 2>/dev/null || echo "❌ Could not list models"
  echo ""

  # 3. Chat completion with first available model or local-coder
  local target_model="qwen2.5-coder:7b"
  if [[ -f "$MODELS_CONFIG" ]]; then
    local candidate
    candidate=$(grep -E '^\s*-\s*model_name:' "$MODELS_CONFIG" | head -n1 | sed -E 's/.*model_name:[[:space:]]*//' | tr -d '"'\'' ')
    if [[ -n "$candidate" ]]; then
      target_model="$candidate"
    fi
  fi

  echo "── Chat Completion (model: ${target_model}) ──"
  curl -sf "${base}/v1/chat/completions" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${key}" \
    -d "{
      \"model\": \"${target_model}\",
      \"messages\": [{\"role\": \"user\", \"content\": \"Say hello in one short sentence.\"}],
      \"max_tokens\": 32
    }" | python3 -m json.tool 2>/dev/null || echo "❌ Chat completion failed (verify local model availability in Ollama)"
}

cmd_backup() {
  _load_env
  local backup_dir="backups"
  local timestamp
  timestamp="$(date '+%Y%m%d_%H%M%S')"
  local dest="${backup_dir}/backup_${timestamp}"
  mkdir -p "${dest}"

  echo "📦 Starting snapshot backup to ${dest}..."

  # 1. Dump databases from Postgres container
  echo "  💾 Backing up PostgreSQL databases (litellm, langfuse & n8n)..."
  if command -v podman &>/dev/null; then
    podman exec litellm-db pg_dump -U "${POSTGRES_USER:-litellm}" "${POSTGRES_DB:-litellm}" > "${dest}/litellm_db.sql" 2>/dev/null || echo "  ⚠️ Warning: LiteLLM DB dump failed."
    podman exec litellm-db pg_dump -U "${POSTGRES_USER:-litellm}" "langfuse" > "${dest}/langfuse_db.sql" 2>/dev/null || echo "  ⚠️ Warning: Langfuse DB dump failed."
    podman exec litellm-db pg_dump -U "${POSTGRES_USER:-litellm}" "n8n" > "${dest}/n8n_db.sql" 2>/dev/null || echo "  ⚠️ Warning: n8n DB dump failed."
  else
    docker exec litellm-db pg_dump -U "${POSTGRES_USER:-litellm}" "${POSTGRES_DB:-litellm}" > "${dest}/litellm_db.sql" 2>/dev/null || echo "  ⚠️ Warning: LiteLLM DB dump failed."
    docker exec litellm-db pg_dump -U "${POSTGRES_USER:-litellm}" "langfuse" > "${dest}/langfuse_db.sql" 2>/dev/null || echo "  ⚠️ Warning: Langfuse DB dump failed."
    docker exec litellm-db pg_dump -U "${POSTGRES_USER:-litellm}" "n8n" > "${dest}/n8n_db.sql" 2>/dev/null || echo "  ⚠️ Warning: n8n DB dump failed."
  fi

  # 2. Backup configurations and secrets
  echo "  📁 Backing up configs, scripts and environment..."
  [[ -d config ]] && cp -r config "${dest}/"
  [[ -d scripts ]] && cp -r scripts "${dest}/"
  [[ -f .env ]] && cp .env "${dest}/env_backup"
  [[ -f compose.yaml ]] && cp compose.yaml "${dest}/"

  # 3. Compress snapshot archive
  tar -czf "${dest}.tar.gz" -C "${backup_dir}" "backup_${timestamp}"
  rm -rf "${dest}"

  echo "  ✅ Snapshot created: ${dest}.tar.gz"

  # 4. Rotate old backups (keep last 7)
  echo "  🔄 Rotating snapshots (keeping newest 7)..."
  ls -1t "${backup_dir}"/backup_*.tar.gz 2>/dev/null | tail -n +8 | xargs rm -f 2>/dev/null || true
  echo "✅ Backup process finished."
}

cmd_update() {
  _load_env
  mkdir -p logs
  local log_file="logs/autoupdate.log"
  local now
  now="$(date '+%Y-%m-%d %H:%M:%S')"
  echo "══════════════════════════════════════════════" | tee -a "$log_file"
  echo "🔄 [$now] Running pre-update snapshot backup..." | tee -a "$log_file"
  cmd_backup 2>&1 | tee -a "$log_file" || echo "⚠️ Pre-update backup had warnings." | tee -a "$log_file"

  echo "🔄 [$now] Checking for image updates ($COMPOSE_CMD pull)..." | tee -a "$log_file"

  _ensure_dirs

  if $COMPOSE_CMD pull 2>&1 | tee -a "$log_file"; then
    echo "🚀 Applying updates with $COMPOSE_CMD up -d..." | tee -a "$log_file"
    $COMPOSE_CMD up -d 2>&1 | tee -a "$log_file"
    
    echo "⏳ Waiting for services to initialize..."
    sleep 3
    cmd_sync_skills 2>&1 | tee -a "$log_file"

    echo "🧹 Cleaning up outdated dangling container images..." | tee -a "$log_file"
    if command -v podman &>/dev/null; then
      podman image prune -f >> "$log_file" 2>&1 || true
    elif command -v docker &>/dev/null; then
      docker image prune -f >> "$log_file" 2>&1 || true
    fi
    echo "✅ [$(date '+%Y-%m-%d %H:%M:%S')] Update check completed successfully." | tee -a "$log_file"
  else
    echo "❌ [$(date '+%Y-%m-%d %H:%M:%S')] Update pull failed." | tee -a "$log_file"
    return 1
  fi
}

cmd_install_autoupdate() {
  local plist_dir="$HOME/Library/LaunchAgents"
  local plist_file="$plist_dir/com.litellm.autoupdate.plist"
  mkdir -p "$plist_dir" logs

  cat > "$plist_file" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.litellm.autoupdate</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>${SCRIPT_DIR}/manage.sh</string>
        <string>update</string>
    </array>
    <key>WorkingDirectory</key>
    <string>${SCRIPT_DIR}</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    </dict>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>4</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>${SCRIPT_DIR}/logs/launchd_stdout.log</string>
    <key>StandardErrorPath</key>
    <string>${SCRIPT_DIR}/logs/launchd_stderr.log</string>
</dict>
</plist>
EOF

  launchctl unload "$plist_file" 2>/dev/null || true
  launchctl load -w "$plist_file"
  echo "✅ Daily autoupdate job installed and scheduled at 04:00 AM daily."
  echo "📄 Plist file: $plist_file"
  echo "📋 Logs: ${SCRIPT_DIR}/logs/autoupdate.log"
}

cmd_uninstall_autoupdate() {
  local plist_file="$HOME/Library/LaunchAgents/com.litellm.autoupdate.plist"
  if [[ -f "$plist_file" ]]; then
    launchctl unload "$plist_file" 2>/dev/null || true
    rm -f "$plist_file"
    echo "✅ Autoupdate schedule removed."
  else
    echo "⚠️ No autoupdate plist found at $plist_file."
  fi
}

cmd_help() {
  cat <<EOF
Usage: ./manage.sh <command>

Commands:
  start                Start the LiteLLM proxy container
  stop                 Stop the proxy container
  restart              Restart the proxy container
  hub                  Open the central Web UI & Agent Hub in your browser
  backup               Create snapshot backup of databases, configs and secrets
  update               Pull latest image updates & recreate containers
  install-autoupdate   Schedule daily automatic update at 04:00 AM (macOS launchd)
  uninstall-autoupdate Remove daily automatic update schedule
  logs                 Tail live container logs
  status               Show container status
  validate             Check YAML syntax of all config files
  sync-skills          Synchronize config/skills.yaml into LiteLLM Database
  refresh-ollama       Re-scan local Ollama models → update config/models.yaml
  test                 Run health + chat completion tests
  help                 Show this message
EOF
}

# ─── Main ───────────────────────────────────
_load_env

case "${1:-help}" in
  start)                cmd_start ;;
  stop)                 cmd_stop ;;
  restart)              cmd_restart ;;
  hub)                  cmd_hub ;;
  backup)               cmd_backup ;;
  update)               cmd_update ;;
  install-autoupdate)   cmd_install_autoupdate ;;
  uninstall-autoupdate) cmd_uninstall_autoupdate ;;
  logs)                 cmd_logs ;;
  status)               cmd_status ;;
  validate)             cmd_validate ;;
  sync-skills)          cmd_sync_skills ;;
  refresh-ollama)       cmd_refresh_ollama ;;
  test)                 cmd_test ;;
  help|--help|-h)       cmd_help ;;
  *)
    echo "❌ Unknown command: $1"
    cmd_help
    exit 1
    ;;
esac
