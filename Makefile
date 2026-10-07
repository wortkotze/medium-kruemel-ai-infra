# ──────────────────────────────────────────────
# LiteLLM Proxy – Makefile
# ──────────────────────────────────────────────

.PHONY: start stop restart hub backup update install-autoupdate uninstall-autoupdate logs status validate sync-skills refresh-ollama test help

start:                 ## Start the LiteLLM proxy
	@./manage.sh start

stop:                  ## Stop the proxy
	@./manage.sh stop

restart:               ## Restart the proxy
	@./manage.sh restart

hub:                   ## Open Web UI & Agent Hub landing page in browser
	@./manage.sh hub

backup:                ## Create snapshot backup of databases, configs and secrets
	@./manage.sh backup

update:                ## Pull newest container images and recreate containers
	@./manage.sh update

install-autoupdate:    ## Schedule automatic daily update at 04:00 AM (macOS launchd)
	@./manage.sh install-autoupdate

uninstall-autoupdate:  ## Remove automatic daily update schedule
	@./manage.sh uninstall-autoupdate

logs:                  ## Tail live logs
	@./manage.sh logs

status:                ## Show container status
	@./manage.sh status

validate:              ## Validate YAML syntax for all config files
	@./manage.sh validate

sync-skills:           ## Synchronize config/skills.yaml into LiteLLM Database
	@./manage.sh sync-skills

refresh-ollama:        ## Re-scan Ollama models and update config/models.yaml
	@./manage.sh refresh-ollama

test:                  ## Run health + completion tests against the proxy
	@./manage.sh test

sync-agents:           ## Export and synchronize infra contract and virtual keys to ../kruemel-ai-agents
	@./scripts/ops/export_agent_env.sh

agents-build:          ## Build Docker image for the 5 isolated agent micro-workers
	docker compose -f compose.agents.yaml build

agents-up:             ## Start all 5 agent micro-worker containers
	docker compose -f compose.agents.yaml up -d

agents-down:           ## Stop all 5 agent micro-worker containers
	docker compose -f compose.agents.yaml down

agents-logs:           ## Follow live logs across all agent micro-workers
	docker compose -f compose.agents.yaml logs -f

agents-status:         ## Show agent registry and container status
	@curl -s http://localhost:1518/api/registry/agents | jq '{online_count, total_count, agents: [.agents[] | {id, status, endpoint}]}'

help:                  ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*##' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "}; {printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2}'

