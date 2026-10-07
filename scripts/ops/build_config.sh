#!/usr/bin/env bash
# ──────────────────────────────────────────────
# scripts/build_config.sh
# Merges modular config files into active runtime config
# ──────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"
cd "$ROOT_DIR"

OUTPUT_FILE="config/config.yaml"

if python3 -c "import yaml" &>/dev/null; then
  python3 - <<'EOF'
import sys, os
import yaml

def load_yaml(path):
    if not os.path.exists(path):
        return {}
    with open(path, 'r') as f:
        return yaml.safe_load(f) or {}

base_config = load_yaml("config/config.yaml")
models_config = load_yaml("config/models.yaml")
mcp_config = load_yaml("config/mcp_servers.yaml")
agents_config = load_yaml("config/agents.yaml")
skills_config = load_yaml("config/skills.yaml")

merged = {}
if "model_list" in models_config:
    merged["model_list"] = models_config["model_list"]
if "router_settings" in models_config:
    merged["router_settings"] = models_config["router_settings"]
    merged["router_settings"]["redis_url"] = "redis://redis:6379"
if "mcp_servers" in mcp_config:
    merged["mcp_servers"] = mcp_config["mcp_servers"]
if "agents" in agents_config:
    merged["agents"] = agents_config["agents"]
if "skills" in skills_config:
    merged["skills"] = skills_config["skills"]

# Merge general & litellm settings
for key in ["sub_configs", "general_settings", "litellm_settings"]:
    if key in base_config:
        merged[key] = base_config[key]

with open("config/config.yaml", "w") as f:
    f.write("# ──────────────────────────────────────────────\n")
    f.write("# AUTO-GENERATED RUNTIME CONFIG (DO NOT EDIT DIRECTLY)\n")
    f.write("# Source files: config/models.yaml, config/mcp_servers.yaml, config/agents.yaml, config/skills.yaml\n")
    f.write("# ──────────────────────────────────────────────\n\n")
    yaml.dump(merged, f, sort_keys=False, default_flow_style=False)
EOF
elif command -v ruby &>/dev/null; then
  ruby -ryaml -e '
    merged = {}
    
    models = File.exist?("config/models.yaml") ? (YAML.load_file("config/models.yaml") || {}) : {}
    mcps   = File.exist?("config/mcp_servers.yaml") ? (YAML.load_file("config/mcp_servers.yaml") || {}) : {}
    agents = File.exist?("config/agents.yaml") ? (YAML.load_file("config/agents.yaml") || {}) : {}
    skills = File.exist?("config/skills.yaml") ? (YAML.load_file("config/skills.yaml") || {}) : {}
    
    merged["model_list"] = models["model_list"] if models["model_list"]
    merged["router_settings"] = models["router_settings"] if models["router_settings"]
    merged["mcp_servers"] = mcps["mcp_servers"] if mcps["mcp_servers"]
    merged["agents"] = agents["agents"] if agents["agents"]
    merged["skills"] = skills["skills"] if skills["skills"]
    
    merged["general_settings"] = {
      "master_key" => "os.environ/LITELLM_MASTER_KEY",
      "database_url" => "os.environ/DATABASE_URL",
      "redis_url" => "redis://redis:6379",
      "user_url_allowed_hosts" => [
        "localhost",
        "localhost:4000",
        "127.0.0.1",
        "127.0.0.1:4000",
        "host.containers.internal",
        "litellm-proxy",
        "llm.kruemel.cc"
      ],
      "proxy_admin_ui" => true,
      "store_audit_logs" => true,
      "alerting" => ["webhook"],
      "alerting_threshold" => 0.85,
      "webhook_url" => "os.environ/ALERT_WEBHOOK_URL"
    }
    
    merged["litellm_settings"] = {
      "drop_params" => true,
      "set_verbose" => false,
      "num_retries" => 2,
      "request_timeout" => 120,
      "json_logs" => true,
      "require_auth_for_metrics_endpoint" => false,
      "cache" => true,
      "cache_params" => {
        "type" => "redis",
        "host" => "redis",
        "port" => 6379,
        "namespace" => "litellm.cache",
        "supported_call_types" => ["completion", "acompletion", "embedding", "aembedding"]
      },
      "success_callback" => ["cache", "postgres", "prometheus", "langfuse"],
      "failure_callback" => ["postgres", "prometheus", "langfuse"]
    }
    
    header = "# ──────────────────────────────────────────────\n# AUTO-GENERATED RUNTIME CONFIG\n# Source files: config/models.yaml, config/mcp_servers.yaml, config/agents.yaml, config/skills.yaml\n# ──────────────────────────────────────────────\n\n"
    File.write("config/config.yaml", header + YAML.dump(merged).sub(/^---\s*\n/, ""))
  '
fi
