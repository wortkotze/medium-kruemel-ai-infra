#!/usr/bin/env python3
"""
Ensures all 5 Multi-Agent Roles have active Virtual Keys with strictly isolated
models, tools, and permissions in LiteLLM:
1. kruemel-agent-po        -> ['agent-po', 'local-general']                              | ['spec_mcp']
2. kruemel-agent-architect -> ['agent-architect', 'local-general']                       | ['architecture_mcp', 'spec_mcp']
3. kruemel-agent-coder     -> ['agent-coder', 'local-coder', 'qwen2.5-coder:7b']         | ['filesystem_mcp', 'sandbox_mcp', 'github_mcp']
4. kruemel-agent-researcher-> ['agent-researcher', 'local-general', 'llama3.1:8b']       | ['searxng_mcp', 'browserless_mcp']
5. kruemel-agent-devops    -> ['agent-devops', 'local-general', 'local-coder', 'llama3.1:8b'] | ['docker_mcp', 'litellm_mcp', 'cloudflare_mcp', 'fritzbox_mcp']
"""
import asyncio
import json
import os
import sys
import urllib.error
import urllib.request

try:
    from prisma import Prisma, Json
except ImportError:
    Prisma = None
    Json = None

AGENT_ROLES = {
    "kruemel-agent-po": {
        "agent_name": "agent-po",
        "models": ["agent-po", "local-general"],
        "tools": ["spec_mcp", "qdrant_mcp", "memgraph_mcp"],
        "role": "Product Owner",
        "description": "Product Owner Virtual Key (Spec Management, Memory & Graph)"
    },
    "kruemel-agent-architect": {
        "agent_name": "agent-architect",
        "models": ["agent-architect", "local-general"],
        "tools": ["architecture_mcp", "spec_mcp", "qdrant_mcp", "memgraph_mcp"],
        "role": "System Architect",
        "description": "System Architect Virtual Key (Architecture, Memory & Graph)"
    },
    "kruemel-agent-coder": {
        "agent_name": "agent-coder",
        "models": ["agent-coder", "local-coder", "qwen2.5-coder:7b"],
        "tools": ["filesystem_mcp", "sandbox_mcp", "github_mcp", "qdrant_mcp"],
        "role": "Software Engineer",
        "description": "Code & Implementation Virtual Key (Sandbox, Filesystem, GitHub, Memory)"
    },
    "kruemel-agent-researcher": {
        "agent_name": "agent-researcher",
        "models": ["agent-researcher", "local-general", "llama3.1:8b"],
        "tools": ["searxng_mcp", "browserless_mcp", "qdrant_mcp"],
        "role": "Researcher",
        "description": "Research & Web Virtual Key (SearXNG, Browserless, Memory)"
    },
    "kruemel-agent-devops": {
        "agent_name": "agent-devops",
        "models": ["agent-devops", "local-general", "local-coder", "llama3.1:8b"],
        "tools": ["docker_mcp", "litellm_mcp", "cloudflare_mcp", "fritzbox_mcp", "qdrant_mcp", "memgraph_mcp"],
        "role": "DevOps Engineer",
        "description": "DevOps & Infrastructure Virtual Key (Docker, LiteLLM, Cloudflare, FRITZ!Box, Memory & Graph)"
    }
}


def _get_agents_from_api(base_url: str, master_key: str) -> dict:
    """Query active agents and map agent_name -> agent_id."""
    req = urllib.request.Request(
        f"{base_url}/v1/agents",
        headers={"Authorization": f"Bearer {master_key}"}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return {a.get("agent_name"): a.get("agent_id") for a in data if a.get("agent_name")}
    except Exception as e:
        print(f"  ⚠ Notice: Could not query /v1/agents via API: {e}")
        return {}


async def _sync_with_prisma(agent_id_map: dict):
    """Direct database sync via Prisma for atomic model and permission assignment."""
    db = Prisma()
    await db.connect()

    print("\n🔍 Synchronizing 5 Agent Virtual Keys in PostgreSQL Database:")

    for key_alias, role_spec in AGENT_ROLES.items():
        agent_name = role_spec["agent_name"]
        models = role_spec["models"]
        tools = role_spec["tools"]
        agent_id = agent_id_map.get(agent_name)

        metadata = {
            "agent_name": agent_name,
            "role": role_spec["role"],
            "description": role_spec["description"],
            "managed_by": "kruemel-ai-infra",
            "tools": tools
        }
        permissions = {
            "tools": tools,
            "mcp_servers": tools
        }

        # Check existing token by key_alias
        existing = await db.litellm_verificationtoken.find_first(
            where={"key_alias": key_alias}
        )

        if existing:
            # Update models, metadata, permissions and link agent_id
            update_data = {
                "models": models,
                "metadata": Json(metadata),
                "permissions": Json(permissions)
            }
            if agent_id:
                update_data["agent_id"] = agent_id

            await db.litellm_verificationtoken.update(
                where={"token": existing.token},
                data=update_data
            )
            print(f"  ✓ Updated '{key_alias}' -> Models: {models} | Tools: {tools}")
        else:
            # Generate via REST API fallback or create in DB
            print(f"  ✨ Generating new key '{key_alias}'...")
            await _generate_via_api(
                key_alias=key_alias,
                agent_name=agent_name,
                models=models,
                tools=tools,
                agent_id=agent_id
            )

    await db.disconnect()


async def _generate_via_api(key_alias: str, agent_name: str, models: list, tools: list, agent_id: str = None):
    """Fallback generator via LiteLLM /key/generate HTTP endpoint."""
    base_url = os.getenv("LITELLM_API_BASE", "http://localhost:4000")
    master_key = os.getenv("LITELLM_MASTER_KEY", "sk-litellm-master-key")

    payload = {
        "key_alias": key_alias,
        "models": models,
        "metadata": {
            "agent_name": agent_name,
            "tools": tools,
            "managed_by": "kruemel-ai-infra"
        },
        "permissions": {
            "tools": tools
        }
    }
    if agent_id:
        payload["agent_id"] = agent_id

    req = urllib.request.Request(
        f"{base_url}/key/generate",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {master_key}",
            "Content-Type": "application/json"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            print(f"    Key '{key_alias}' generated successfully -> token prefix: {data.get('key', '')[:8]}...")
    except Exception as e:
        print(f"    ✗ Failed to generate key '{key_alias}': {e}")


async def main():
    base_url = os.getenv("LITELLM_API_BASE", "http://localhost:4000")
    master_key = os.getenv("LITELLM_MASTER_KEY", "sk-litellm-master-key")

    print("═══════════════════════════════════════════════════════════════")
    print(" 🍪 Krümel AI – 5-Role Multi-Agent Virtual Key & Tool Setup")
    print("═══════════════════════════════════════════════════════════════")

    agent_id_map = _get_agents_from_api(base_url, master_key)
    print(f"Found {len(agent_id_map)} agent definitions registered at LiteLLM: {list(agent_id_map.keys())}")

    if Prisma:
        await _sync_with_prisma(agent_id_map)
    else:
        print("\nPrisma not available locally, applying via LiteLLM HTTP REST API:")
        for alias, spec in AGENT_ROLES.items():
            await _generate_via_api(
                key_alias=alias,
                agent_name=spec["agent_name"],
                models=spec["models"],
                tools=spec["tools"],
                agent_id=agent_id_map.get(spec["agent_name"])
            )

    print("\n✅ Virtual key setup complete. All 5 agent roles are configured with strict model and tool isolation.")


if __name__ == "__main__":
    asyncio.run(main())
