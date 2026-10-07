#!/usr/bin/env bash
# ──────────────────────────────────────────────
# scripts/run.sh – LiteLLM Startup & Reload Helper
# ──────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"
cd "$ROOT_DIR"

# Detect Podman or Docker
if command -v podman &>/dev/null; then
  COMPOSE_BIN="podman compose"
elif command -v docker &>/dev/null; then
  COMPOSE_BIN="docker compose"
else
  echo "❌ Neither Podman nor Docker was found in PATH."
  exit 1
fi

echo "🔧 Initializing LiteLLM Gateway environment..."

# Ensure workspace directory exists for Filesystem MCP
mkdir -p workspace

# Assemble modular configuration into runtime config
if [[ -f scripts/ops/build_config.sh ]]; then
  ./scripts/ops/build_config.sh
fi

# Ensure .env exists
if [[ ! -f .env ]]; then
  if [[ -f .env.example ]]; then
    echo "⚠️  .env not found. Creating from .env.example..."
    cp .env.example .env
    echo "❗ Please edit .env to set your passwords and API keys."
  fi
fi

# Validate YAML Configurations
echo "🔍 Validating configuration syntax..."
if python3 -c "import yaml" &>/dev/null; then
  python3 -c "
import yaml, glob, sys
for f in glob.glob('config/*.yaml'):
    try:
        yaml.safe_load(open(f))
        print(f'  ✓ {f} is valid')
    except Exception as e:
        print(f'  ✗ {f} syntax error: {e}')
        sys.exit(1)
"
elif command -v ruby &>/dev/null; then
  ruby -ryaml -e '
    Dir.glob("config/*.yaml").each do |f|
      begin
        YAML.load_file(f)
        puts "  ✓ #{f} is valid"
      rescue => e
        puts "  ✗ #{f} syntax error: #{e}"
        exit 1
      end
    end
  '
fi

# Parse CLI Action
ACTION="${1:-up}"

case "$ACTION" in
  up|start)
    echo "🚀 Starting LiteLLM Gateway ($COMPOSE_BIN)..."
    $COMPOSE_BIN up -d
    echo "✅ LiteLLM is running at http://localhost:${PORT:-4000}"
    echo "📊 Admin UI: http://localhost:${PORT:-4000}/ui"
    ;;
  down|stop)
    echo "🛑 Stopping LiteLLM Gateway..."
    $COMPOSE_BIN down
    ;;
  restart|reload)
    echo "🔄 Reloading LiteLLM Gateway..."
    $COMPOSE_BIN down
    $COMPOSE_BIN up -d
    echo "✅ LiteLLM reloaded."
    ;;
  logs)
    $COMPOSE_BIN logs -f
    ;;
  *)
    echo "Usage: $0 {up|start|down|stop|restart|reload|logs}"
    exit 1
    ;;
esac
